"""
Monitoring service for Empire - provides insights into system health and performance
"""
import os
import time
import json
import logging
import threading
import psutil
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional
import socket
from pathlib import Path
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("empire-monitor")

# Define data models
class SystemMetrics(BaseModel):
    """System-level metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    boot_time: str
    process_count: int
    uptime_seconds: int

class AgentMetrics(BaseModel):
    """Agent-specific metrics"""
    agent_id: str
    name: str
    status: str
    tasks_completed: int
    tasks_failed: int
    avg_response_time: float
    last_activity: str

class MonitoringData(BaseModel):
    """Complete monitoring data"""
    timestamp: str
    system: SystemMetrics
    agents: List[AgentMetrics]
    api_requests: Dict[str, int]

# Global storage for monitoring data
monitoring_data = {
    "timestamp": datetime.now().isoformat(),
    "system": {
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "disk_percent": 0.0,
        "boot_time": "",
        "process_count": 0,
        "uptime_seconds": 0
    },
    "agents": [],
    "api_requests": {}
}

# Track API requests
request_counts: Dict[str, int] = {}
active_websockets: List[WebSocket] = []

def increment_endpoint_counter(endpoint: str) -> None:
    """Increment the counter for a specific API endpoint"""
    global request_counts
    if endpoint in request_counts:
        request_counts[endpoint] += 1
    else:
        request_counts[endpoint] = 1

def collect_system_metrics() -> Dict[str, Any]:
    """Collect system-level metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
        process_count = len(psutil.pids())
        uptime_seconds = int(time.time() - psutil.boot_time())
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "boot_time": boot_time,
            "process_count": process_count,
            "uptime_seconds": uptime_seconds
        }
    except Exception as e:
        logger.error(f"Error collecting system metrics: {str(e)}")
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "boot_time": datetime.now().isoformat(),
            "process_count": 0,
            "uptime_seconds": 0
        }

def collect_agent_metrics(empire) -> List[Dict[str, Any]]:
    """Collect metrics from all registered agents"""
    try:
        agent_metrics = []
        if not empire or not hasattr(empire, '_agents'):
            return agent_metrics
            
        for agent_id, agent in empire._agents.items():
            metrics = {
                "agent_id": agent_id,
                "name": agent.name,
                "status": "active",  # Default status
                "tasks_completed": 0,
                "tasks_failed": 0,
                "avg_response_time": 0.0,
                "last_activity": datetime.now().isoformat()
            }
            
            # Try to get accountability metrics if available
            if hasattr(agent, '_accountability_metrics'):
                accountability = agent._accountability_metrics
                metrics.update({
                    "tasks_completed": accountability.get("tasks_completed", 0),
                    "tasks_failed": accountability.get("tasks_failed", 0),
                    "avg_response_time": accountability.get("avg_response_time", 0.0),
                })
                
            agent_metrics.append(metrics)
            
        return agent_metrics
    except Exception as e:
        logger.error(f"Error collecting agent metrics: {str(e)}")
        return []

def update_monitoring_data(empire=None) -> None:
    """Update the global monitoring data"""
    global monitoring_data
    
    monitoring_data = {
        "timestamp": datetime.now().isoformat(),
        "system": collect_system_metrics(),
        "agents": collect_agent_metrics(empire),
        "api_requests": dict(request_counts)
    }

async def broadcast_updates() -> None:
    """Broadcast monitoring updates to all connected WebSockets"""
    for websocket in active_websockets:
        try:
            await websocket.send_json(monitoring_data)
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {str(e)}")
            # Will be removed on next connection attempt

def monitoring_thread(empire=None, interval: int = 5) -> None:
    """Background thread that collects metrics at regular intervals"""
    try:
        while True:
            update_monitoring_data(empire)
            # Use asyncio to broadcast updates
            asyncio.run(broadcast_updates())
            time.sleep(interval)
    except Exception as e:
        logger.error(f"Error in monitoring thread: {str(e)}")

def start_monitoring(empire=None, interval: int = 5) -> threading.Thread:
    """Start the monitoring thread"""
    thread = threading.Thread(
        target=monitoring_thread,
        args=(empire, interval),
        daemon=True
    )
    thread.start()
    logger.info(f"Monitoring thread started with {interval}s interval")
    return thread

# FastAPI Router and endpoints
router = APIRouter()

@router.get("/metrics", response_model=MonitoringData)
async def get_metrics():
    """Get the current monitoring data"""
    increment_endpoint_counter("/monitoring/metrics")
    return monitoring_data

@router.get("/system")
async def get_system_metrics():
    """Get system-level metrics"""
    increment_endpoint_counter("/monitoring/system")
    return monitoring_data["system"]

@router.get("/agents")
async def get_agent_metrics():
    """Get agent metrics"""
    increment_endpoint_counter("/monitoring/agents")
    return monitoring_data["agents"]

@router.get("/requests")
async def get_request_metrics():
    """Get API request metrics"""
    increment_endpoint_counter("/monitoring/requests")
    return monitoring_data["api_requests"]

@router.websocket("/ws")
async def metrics_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        # Send initial data
        await websocket.send_json(monitoring_data)
        
        # Keep connection alive
        while True:
            # Wait for any message (will be used to detect disconnection)
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Clean up on disconnect
        if websocket in active_websockets:
            active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)

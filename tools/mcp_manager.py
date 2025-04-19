#!/usr/bin/env python
"""
Management script for the Empire MCP Server
"""
import os
import sys
import argparse
import subprocess
import signal
import time
import logging
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("mcp-manager")

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.pid")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "mcp_server.log")

def is_server_running():
    """Check if the MCP server is currently running"""
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process with this PID exists
        process = psutil.Process(pid)
        return process.is_running() and "python" in process.name().lower()
    except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def start_server():
    """Start the MCP server"""
    if is_server_running():
        logger.info("MCP Server is already running")
        return
    
    logger.info("Starting MCP Server...")
    
    # Make sure logs directory exists
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"), exist_ok=True)
    
    # Start the server
    try:
        process = subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "adk_mcp_server.py")],
            stdout=open(LOG_FILE, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Store the PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment to ensure the server is starting
        time.sleep(2)
        
        if process.poll() is None:
            logger.info(f"MCP Server started with PID {process.pid}")
            logger.info(f"Log file: {LOG_FILE}")
        else:
            logger.error("Failed to start MCP Server")
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    last_lines = f.readlines()[-10:]  # Get last 10 lines
                    logger.error("Last log entries:")
                    for line in last_lines:
                        logger.error(f"  {line.strip()}")
    except Exception as e:
        logger.error(f"Error starting MCP Server: {str(e)}")

def stop_server():
    """Stop the MCP server"""
    if not os.path.exists(PID_FILE):
        logger.info("No MCP Server PID file found")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        logger.info(f"Stopping MCP Server (PID {pid})...")
        
        try:
            # Try to terminate gracefully first
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for up to 5 seconds for termination
            gone, still_alive = psutil.wait_procs([process], timeout=5)
            
            # Kill if still running
            for p in still_alive:
                p.kill()
            
            logger.info("MCP Server stopped")
        except psutil.NoSuchProcess:
            logger.info("MCP Server was not running")
        
        # Remove the PID file
        os.remove(PID_FILE)
    except Exception as e:
        logger.error(f"Error stopping MCP Server: {str(e)}")

def status():
    """Check the status of the MCP server"""
    if is_server_running():
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        logger.info(f"MCP Server is running (PID {pid})")
        return True
    else:
        logger.info("MCP Server is not running")
        return False
        
def view_logs():
    """Display the last 20 lines of the log file"""
    if not os.path.exists(LOG_FILE):
        logger.info("No log file found")
        return
    
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            last_lines = lines[-20:] if lines else []
        
        if not last_lines:
            logger.info("Log file is empty")
            return
        
        logger.info("Last 20 log entries:")
        for line in last_lines:
            print(f"  {line.strip()}")
    except Exception as e:
        logger.error(f"Error reading log file: {str(e)}")

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Empire MCP Server Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'logs'],
                        help="Action to perform on the MCP server")
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_server()
    elif args.action == 'stop':
        stop_server()
    elif args.action == 'restart':
        stop_server()
        time.sleep(2)  # Wait for full shutdown
        start_server()
    elif args.action == 'status':
        status()
    elif args.action == 'logs':
        view_logs()
    
if __name__ == "__main__":
    main()

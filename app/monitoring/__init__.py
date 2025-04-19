"""
Initialization module for monitoring system
"""
from app.monitoring.monitor import router as monitor_router, start_monitoring

# Initialize monitoring
monitor_thread = None

def init_monitoring(app=None, empire=None, interval=5):
    """Initialize the monitoring system and attach routes to FastAPI app"""
    global monitor_thread

    # Start the monitoring thread
    monitor_thread = start_monitoring(empire, interval)
    
    # Register monitoring routes if app is provided
    if app:
        app.include_router(
            monitor_router,
            prefix="/monitoring",
            tags=["Monitoring"]
        )
        
    return monitor_thread

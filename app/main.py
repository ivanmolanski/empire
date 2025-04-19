import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
from app.config import settings
from app.utils.version_check import verify_compatibility
from app.core import empire
from app.monitoring import init_monitoring

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '../logs'), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/empire.log'), mode='a')
    ]
)

logger = logging.getLogger(__name__)

# Verify environment compatibility
try:
    is_compatible = verify_compatibility(exit_on_failure=False)
    if not is_compatible:
        logger.warning("Running with compatibility issues. Some features may not work correctly.")
except Exception as e:
    logger.error(f"Error during compatibility check: {str(e)}")
    logger.warning("Proceeding with startup, but system may be unstable.")

# Initialize FastAPI app
app = FastAPI(
    title="Bach AI Empire API", 
    version="1.0.0",
    description="Multi-agent orchestration framework for website creation and management"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Welcome endpoint returning basic API information"""
    return {
        "message": "Welcome to the Empire API",
        "version": "1.0.0",
        "documentation": "/docs",
        "monitoring": "/monitoring/dashboard"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Request counting middleware for monitoring
@app.middleware("http")
async def count_requests(request: Request, call_next):
    """Middleware to count API requests for monitoring"""
    from app.monitoring.monitor import increment_endpoint_counter
    path = request.url.path
    
    response = await call_next(request)
    
    # Only count API endpoints, not static files
    if not path.startswith("/static"):
        increment_endpoint_counter(path)
        
    return response

# Include API routes
app.include_router(api_router)

# Create static files directory for dashboard
dashboard_dir = os.path.join(os.path.dirname(__file__), "static/dashboard")
os.makedirs(dashboard_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Initialize monitoring system
init_monitoring(app, empire)

# Startup event to log successful initialization
@app.on_event("startup")
async def startup_event():
    logger.info("Empire API successfully started")
    logger.info(f"Documentation available at http://localhost:8000/docs")
    logger.info(f"Monitoring dashboard available at http://localhost:8000/monitoring/dashboard")

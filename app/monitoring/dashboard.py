P"""
Monitoring dashboard routes for FastAPI
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# Define router
router = APIRouter()

# Get the static files directory path
static_dir = Path(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"))
dashboard_dir = static_dir / "dashboard"

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the monitoring dashboard"""
    with open(dashboard_dir / "index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

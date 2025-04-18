from fastapi import APIRouter, Request, HTTPException
from app.routes.llm import router as llm_router
from app.routes.niche import router as niche_router
from app.routes.website import router as website_router
from app.routes.user import router as user_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router
from app.routes.webhook import router as webhook_router
from app.routes.analytics import router as analytics_router
from app.models import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse, ProjectCreateRequest, ProjectResponse, ProjectListResponse, TaskStatusResponse, WebhookRegisterRequest, WebhookResponse, WebsiteAnalyticsResponse, WebsiteMonetizationResponse
from typing import Dict
import yaml

router = APIRouter()
router.include_router(llm_router, prefix="/llm", tags=["LLM"])
router.include_router(niche_router, prefix="/niche", tags=["Niche Discovery"])
router.include_router(website_router, prefix="/website", tags=["Website Management"])
router.include_router(user_router, prefix="/user", tags=["User Management"])
router.include_router(project_router, prefix="/project", tags=["Project Management"])
router.include_router(task_router, prefix="/task", tags=["Async Tasks"])
router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics & Monetization"])

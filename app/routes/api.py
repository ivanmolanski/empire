from fastapi import APIRouter, Request, HTTPException
from app.routes.llm import router as llm_router
from app.routes.niche import router as niche_router
from app.routes.website import router as website_router
from app.routes.user import router as user_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router
from app.routes.webhook import router as webhook_router
from app.routes.analytics import router as analytics_router
from pydantic import BaseModel
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

class PydanticModel(BaseModel):
    name: str
    fields: Dict[str, str]

@router.post("/generate-pydantic", response_model=PydanticModel, tags=["Pydantic Generation"])
async def generate_pydantic(request: Request):
    try:
        yaml_data = await request.body()
        data = yaml.safe_load(yaml_data)
        models = []
        for model_name, fields in data.items():
            model_fields = {field_name: field_type for field_name, field_type in fields.items()}
            models.append(PydanticModel(name=model_name, fields=model_fields))
        return models
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

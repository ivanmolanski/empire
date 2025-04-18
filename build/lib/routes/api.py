from fastapi import APIRouter
from .llm import router as llm_router
from .niche import router as niche_router
from .website import router as website_router

router = APIRouter()
router.include_router(llm_router, prefix="/llm", tags=["LLM"])
router.include_router(niche_router, prefix="/niche", tags=["Niche Discovery"])
router.include_router(website_router, prefix="/website", tags=["Website Management"])

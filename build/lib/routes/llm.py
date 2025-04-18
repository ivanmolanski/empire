from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LLMProviderSwitchRequest(BaseModel):
    provider: str

@router.post("/switch")
def switch_llm(request: LLMProviderSwitchRequest):
    return {"message": f"Switched to {request.provider}"}

from fastapi import APIRouter, status
from app.models import LLMProviderSwitchRequest, MessageResponse, ErrorResponse

router = APIRouter()

@router.post(
    "/switch",
    response_model=MessageResponse,
    responses={400: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Switch the active Large Language Model provider"
)
def switch_llm(request: LLMProviderSwitchRequest):
    """
    Switch the active LLM provider (e.g., OpenRouter or Gemini).
    - **provider**: The LLM provider to switch to. Must be "openrouter" or "gemini".
    """
    # Example logic: In production, you would update a config or trigger an agent.
    if request.provider not in ("openrouter", "gemini"):
        return ErrorResponse(error="Invalid provider specified")
    return MessageResponse(message=f"Switched to {request.provider}")

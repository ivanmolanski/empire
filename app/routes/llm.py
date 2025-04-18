from fastapi import APIRouter, status
from app.models import LLMProviderSwitchRequest, MessageResponse, ErrorResponse

router = APIRouter()

@router.post(
    "/switch-provider",
    response_model=MessageResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Switch the active Large Language Model provider"
)
def switch_llm_provider(request: LLMProviderSwitchRequest):
    """
    Switch the active LLM provider (e.g., OpenRouter or Gemini).
    - **provider**: The LLM provider to switch to. Must be "openrouter" or "gemini".
    """
    # Example logic: In production, you would update a config or trigger an agent.
    if request.provider not in ("openrouter", "gemini"):
        return ErrorResponse(error="Invalid provider specified")
    
    try:
        # Placeholder for actual logic to switch the LLM provider
        # For example, updating a configuration file or environment variable
        # config.update_llm_provider(request.provider)
        pass
    except Exception as e:
        return ErrorResponse(error=f"Failed to switch provider: {str(e)}")
    
    return MessageResponse(message=f"Switched to {request.provider}")

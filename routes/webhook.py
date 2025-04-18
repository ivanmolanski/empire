from fastapi import APIRouter, status
from models import WebhookRegisterRequest, WebhookResponse, ErrorResponse

router = APIRouter()

@router.post(
    "/register",
    response_model=WebhookResponse,
    responses={400: {"model": ErrorResponse}},
    status_code=status.HTTP_201_CREATED,
    summary="Register a webhook for events"
)
def register_webhook(request: WebhookRegisterRequest):
    """
    Register a webhook to receive event notifications.
    - **url**: The webhook endpoint URL.
    - **event**: The event to subscribe to.
    """
    # TODO: Store webhook in database and validate URL.
    return WebhookResponse(webhook_id="webhook_123", url=request.url, event=request.event)

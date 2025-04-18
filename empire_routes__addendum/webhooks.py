from fastapi import APIRouter
from models import WebhookRegisterRequest, WebhookResponse

router = APIRouter()

@router.post("/register", response_model=WebhookResponse, status_code=201)
def register_webhook(request: WebhookRegisterRequest):
    return WebhookResponse(webhook_id="webhook_123", url=request.url, event=request.event)
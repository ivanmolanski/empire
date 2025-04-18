from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

class WebsiteIdentifierRequest(BaseModel):
    website_id: str

class WebsiteCreationRequest(BaseModel):
    niche: str

@router.post("/create")
def create_website(request: WebsiteCreationRequest):
    return {"website_id": "site_123"}

@router.get("/view")
def view_website(website_id: str = Query(...)):
    return {"url": f"https://example.com/{website_id}"}

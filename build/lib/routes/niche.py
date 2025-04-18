from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class NicheDiscoveryRequest(BaseModel):
    keywords: List[str]

@router.post("/discover")
def discover_niches(request: NicheDiscoveryRequest):
    return {"results": [{"niche": "Example Niche", "score": 85}]}

@router.get("/report/daily")
def daily_report():
    return {"report": [{"niche": "Example", "monetization": "Ads", "details": "High CTR niche"}]}

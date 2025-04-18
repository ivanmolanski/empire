from fastapi import APIRouter, Query
from models import WebsiteAnalyticsResponse, WebsiteMonetizationResponse

router = APIRouter()

@router.get("/analytics", response_model=WebsiteAnalyticsResponse)
def get_analytics(website_id: str = Query(...)):
    return WebsiteAnalyticsResponse(
        website_id=website_id, visits=1234, bounce_rate=0.45, avg_time_on_site=128.5
    )

@router.get("/monetization", response_model=WebsiteMonetizationResponse)
def get_monetization(website_id: str = Query(...)):
    return WebsiteMonetizationResponse(
        website_id=website_id, revenue=1050.75, currency="USD", sources=["Ads", "Affiliates"]
    )
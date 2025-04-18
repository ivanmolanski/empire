from fastapi import APIRouter, status, Query
from models import (
    WebsiteAnalyticsResponse,
    WebsiteMonetizationResponse,
    ErrorResponse
)

router = APIRouter()

@router.get(
    "/analytics",
    response_model=WebsiteAnalyticsResponse,
    responses={404: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Get analytics for a website"
)
def website_analytics(website_id: str = Query(..., description="Website identifier")):
    """
    Get analytics data for a specific website.
    - **website_id**: The unique identifier of the website.
    """
    # TODO: Query analytics data from database or analytics service.
    return WebsiteAnalyticsResponse(
        website_id=website_id,
        visits=1000,
        bounce_rate=0.45,
        avg_time_on_site=120.5
    )

@router.get(
    "/monetization",
    response_model=WebsiteMonetizationResponse,
    responses={404: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Get monetization data for a website"
)
def website_monetization(website_id: str = Query(..., description="Website identifier")):
    """
    Get monetization data for a specific website.
    - **website_id**: The unique identifier of the website.
    """
    # TODO: Query monetization data from database or payment provider.
    return WebsiteMonetizationResponse(
        website_id=website_id,
        revenue=1234.56,
        currency="USD",
        sources=["Ads", "Affiliate"]
    )

from fastapi import APIRouter, status
from models import (
    NicheDiscoveryRequest,
    NicheDiscoveryResponse,
    DailyNicheReportResponse,
    ErrorResponse
)

router = APIRouter()

@router.post(
    "/discover",
    response_model=NicheDiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Discover potential niches based on keywords"
)
def discover_niches(request: NicheDiscoveryRequest):
    """
    Discover profitable market niches based on a list of keywords.
    - **keywords**: List of keywords to analyze for niche opportunities.
    """
    # Example: In production, this would call your agent/AI logic.
    return NicheDiscoveryResponse(
        results=[
            {
                "niche": "Example Niche",
                "score": 85,
                "monetization_strategies": ["Affiliate Marketing", "Ads"],
                "report": "High potential for growth."
            }
        ]
    )

@router.get(
    "/report/daily",
    response_model=DailyNicheReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the daily report on profitable niche opportunities"
)
def daily_report():
    """
    Get a daily report of trending or profitable niche opportunities.
    """
    return DailyNicheReportResponse(
        report=[
            {
                "niche": "Example",
                "monetization": "Ads",
                "details": "High CTR niche"
            }
        ]
    )

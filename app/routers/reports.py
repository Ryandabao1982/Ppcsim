from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app import models, schemas, auth # models for current_user type hint
from app.database import get_db
from app.reports import get_search_term_report_data # Import the new function

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
    dependencies=[Depends(auth.get_current_user)] # All report routes require authentication
)

@router.get("/search-term", response_model=List[schemas.SearchTermReportItem])
def read_search_term_report(
    start_date: Optional[datetime.date] = Query(None, description="Start date for report (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End date for report (YYYY-MM-DD)"),
    campaign_id: Optional[int] = Query(None, description="Filter by specific campaign ID"),
    # ad_group_id: Optional[int] = Query(None, description="Filter by specific ad group ID"), # Can add later
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"), # Max 1000 for STR
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Use models.User for current_user
):
    """
    Retrieves the Search Term Report data for the authenticated user.
    Allows filtering by date range and campaign ID.
    """
    report_data = get_search_term_report_data(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        campaign_id=campaign_id,
        # ad_group_id=ad_group_id,
        skip=skip,
        limit=limit
    )
    return report_data

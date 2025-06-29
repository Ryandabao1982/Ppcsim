from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import datetime

from app import models, schemas, auth
from app.database import get_db
from app.reports import get_dashboard_metrics # Import the new function

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(auth.get_current_user)] # All dashboard routes require authentication
)

@router.get("/", response_model=schemas.DashboardMetrics)
def read_dashboard_metrics(
    start_date: Optional[datetime.date] = Query(None, description="Start date for metrics (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End date for metrics (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieves key performance metrics for the user's dashboard.
    Metrics can be filtered by an optional date range.
    """
    metrics = get_dashboard_metrics(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return metrics

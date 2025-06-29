from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app import models, schemas
from decimal import Decimal, ROUND_HALF_UP
import datetime
from typing import Optional

def get_dashboard_metrics(
    db: Session,
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> schemas.DashboardMetrics:
    """
    Calculates dashboard metrics for a given user and optional date range.
    Metrics include: Total Sales, Total Spend, ACoS, ROAS, Impressions, Clicks, Orders.
    """

    query = db.query(
        func.sum(models.AdPerformanceMetric.sales).label("total_sales"),
        func.sum(models.AdPerformanceMetric.spend).label("total_spend"),
        func.sum(models.AdPerformanceMetric.impressions).label("total_impressions"),
        func.sum(models.AdPerformanceMetric.clicks).label("total_clicks"),
        func.sum(models.AdPerformanceMetric.orders).label("total_orders")
    ).filter(models.AdPerformanceMetric.user_id == user_id)

    period_description = "Overall"
    if start_date:
        query = query.filter(models.AdPerformanceMetric.metric_date >= start_date)
        period_description = f"From {start_date.isoformat()}"
    if end_date:
        query = query.filter(models.AdPerformanceMetric.metric_date <= end_date)
        if period_description == "Overall": # Only end_date provided
            period_description = f"Until {end_date.isoformat()}"
        else: # Both start_date and end_date provided
             period_description += f" to {end_date.isoformat()}"


    result = query.one()

    total_sales = result.total_sales or Decimal(0)
    total_spend = result.total_spend or Decimal(0)
    total_impressions = result.total_impressions or 0
    total_clicks = result.total_clicks or 0
    total_orders = result.total_orders or 0

    # Calculate ACoS and ROAS, handling division by zero
    acos = (total_spend / total_sales * 100) if total_sales > 0 else float(0)
    roas = total_sales / total_spend if total_spend > 0 else float(0)

    return schemas.DashboardMetrics(
        total_sales=total_sales.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        total_spend=total_spend.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        acos=float(acos), # Ensure it's float for schema
        roas=float(roas), # Ensure it's float for schema
        impressions=total_impressions,
        clicks=total_clicks,
        orders=total_orders,
        period_description=period_description
    )

from typing import List # Ensure List is imported
from sqlalchemy.orm import aliased, joinedload # For using aliased tables in joins and eager loading

# Placeholder for other reporting functions, e.g., Search Term Report data
def get_search_term_report_data(
    db: Session,
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    campaign_id: Optional[int] = None,
    # ad_group_id: Optional[int] = None # Could add more filters
    skip: int = 0,
    limit: int = 1000 # Default to a higher limit for reports
) -> List[schemas.SearchTermReportItem]:

    query = db.query(
        models.SearchTermPerformance.report_date,
        models.SearchTermPerformance.search_term_text,
        models.Campaign.campaign_name,
        models.AdGroup.ad_group_name,
        models.Keyword.keyword_text.label("matched_keyword_text"), # Alias for clarity
        models.SearchTermPerformance.impressions,
        models.SearchTermPerformance.clicks,
        models.SearchTermPerformance.spend,
        models.SearchTermPerformance.orders,
        models.SearchTermPerformance.sales,
        models.SearchTermPerformance.acos,
        models.SearchTermPerformance.roas,
        models.SearchTermPerformance.cpc,
        models.SearchTermPerformance.ctr,
        models.SearchTermPerformance.cvr,
        models.SearchTermPerformance.campaign_id, # Already on SearchTermPerformance
        models.SearchTermPerformance.ad_group_id, # Already on SearchTermPerformance
        models.SearchTermPerformance.matched_keyword_id
    ).select_from(models.SearchTermPerformance).join(
        models.Campaign, models.SearchTermPerformance.campaign_id == models.Campaign.id
    ).join(
        models.AdGroup, models.SearchTermPerformance.ad_group_id == models.AdGroup.id
    ).outerjoin( # Use outerjoin for keyword in case it's an auto target or keyword is deleted
        models.Keyword, models.SearchTermPerformance.matched_keyword_id == models.Keyword.id
    ).filter(models.SearchTermPerformance.user_id == user_id)

    if start_date:
        query = query.filter(models.SearchTermPerformance.report_date >= start_date)
    if end_date:
        query = query.filter(models.SearchTermPerformance.report_date <= end_date)
    if campaign_id:
        query = query.filter(models.SearchTermPerformance.campaign_id == campaign_id)
    # if ad_group_id:
    #     query = query.filter(models.SearchTermPerformance.ad_group_id == ad_group_id)

    results = query.order_by(
        models.SearchTermPerformance.report_date.desc(),
        models.SearchTermPerformance.impressions.desc()
    ).offset(skip).limit(limit).all()

    # Convert SQLAlchemy result objects (Row-like) to Pydantic schemas
    report_items = []
    for row in results:
        item_data = {
            'report_date': row.report_date,
            'search_term_text': row.search_term_text,
            'campaign_name': row.campaign_name,
            'ad_group_name': row.ad_group_name,
            'matched_keyword_text': row.matched_keyword_text,
            'impressions': row.impressions,
            'clicks': row.clicks,
            'spend': row.spend,
            'orders': row.orders,
            'sales': row.sales,
            'acos': row.acos,
            'roas': row.roas,
            'cpc': row.cpc,
            'ctr': row.ctr,
            'cvr': row.cvr,
            'campaign_id': row.campaign_id,
            'ad_group_id': row.ad_group_id,
            'matched_keyword_id': row.matched_keyword_id,
        }
        report_items.append(schemas.SearchTermReportItem(**item_data))

    return report_items

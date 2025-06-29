from django.db.models import Sum, Avg, F, ExpressionWrapper, fields, Case, When, Value
from django.db.models.functions import Coalesce
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
import datetime
from typing import List, Dict, Optional

from campaigns.models import Campaign, AdGroup, Keyword, ProductTarget # For lookups
from .models import AdPerformanceMetric, SearchTermPerformance # Main data source
# User = settings.AUTH_USER_MODEL # Not directly used in aggregation funcs if user_id is passed

def _calculate_derived_metrics(data_dict: Dict) -> Dict:
    """Helper to calculate ACOS, ROAS, CPC, CTR, CVR from aggregated sums."""
    impressions = data_dict.get('impressions', 0)
    clicks = data_dict.get('clicks', 0)
    spend = data_dict.get('spend', Decimal('0.00'))
    orders = data_dict.get('orders', 0)
    sales = data_dict.get('sales', Decimal('0.00'))

    data_dict['cpc'] = (spend / Decimal(clicks)).quantize(Decimal('0.01')) if clicks > 0 else Decimal('0.00')
    data_dict['ctr'] = float(Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else 0.0
    data_dict['cvr'] = float(Decimal(orders) / Decimal(clicks) * 100) if clicks > 0 else 0.0
    data_dict['acos'] = float((spend / sales) * 100) if sales > 0 else 0.0
    data_dict['roas'] = float(sales / spend) if spend > 0 else 0.0
    return data_dict

def get_campaign_performance_summary(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> List[Dict]:

    queryset = AdPerformanceMetric.objects.filter(user_id=user_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    # Group by campaign and aggregate metrics
    # We also need to fetch campaign details (name, ad_type, etc.)
    # This can be done by annotating these fields from the related Campaign model.
    # However, values() + annotate() is often more efficient for pure aggregation reports
    # than trying to make Django ORM output instances of a non-model class.

    summary = queryset.values(
        'campaign_id',
        'campaign__name',
        'campaign__ad_type',
        'campaign__status',
        'campaign__daily_budget',
        'campaign__start_date',
        'campaign__end_date'
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('-spend', 'campaign__name') # Example ordering

    results = []
    for item in summary:
        # Rename fields to match serializer if necessary
        data = {
            'campaign_id': item['campaign_id'],
            'campaign_name': item['campaign__name'],
            'ad_type': item['campaign__ad_type'],
            'status': item['campaign__status'],
            'daily_budget': item['campaign__daily_budget'],
            'start_date': item['campaign__start_date'],
            'end_date': item['campaign__end_date'],
            'impressions': item['impressions'],
            'clicks': item['clicks'],
            'spend': item['spend'],
            'orders': item['orders'],
            'sales': item['sales'],
        }
        results.append(_calculate_derived_metrics(data))

    return results


def get_keyword_performance_report(
    user_id: int,
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> List[Dict]:
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id, keyword_id__isnull=False) # Only metrics for keywords

    if campaign_id:
        queryset = queryset.filter(campaign_id=campaign_id)
    if ad_group_id:
        queryset = queryset.filter(ad_group_id=ad_group_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    summary = queryset.values(
        'keyword_id',
        'keyword__text',
        'keyword__match_type',
        'keyword__bid',
        'keyword__status',
        'ad_group_id', # For context
        'ad_group__name',
        'campaign_id',
        'campaign__name'
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('campaign__name', 'ad_group__name', '-spend', 'keyword__text')

    results = []
    for item in summary:
        data = {
            'keyword_id': item['keyword_id'],
            'keyword_text': item['keyword__text'],
            'match_type': item['keyword__match_type'],
            'bid': item['keyword__bid'],
            'status': item['keyword__status'],
            'ad_group_id': item['ad_group_id'],
            'ad_group_name': item['ad_group__name'],
            'campaign_id': item['campaign_id'],
            'campaign_name': item['campaign__name'],
            'impressions': item['impressions'],
            'clicks': item['clicks'],
            'spend': item['spend'],
            'orders': item['orders'],
            'sales': item['sales'],
        }
        results.append(_calculate_derived_metrics(data))
    return results

# Similar functions can be created for AdGroupPerformance and ProductTargetPerformance:
# get_adgroup_performance_summary(...)
# get_product_target_performance_report(...)

# For now, these two cover the main requirements for Campaign Performance and Keywords Report.
# The Search Term Report will query SearchTermPerformance model directly.
# Dashboard might use get_campaign_performance_summary and then sum totals, or a dedicated overall summary function.
# The AdGroup performance can be derived by further filtering/grouping CampaignPerformance or via a specific query.
# Let's add AdGroup performance for completeness as it's in the plan.

def get_adgroup_performance_summary(
    user_id: int,
    campaign_id: int, # Ad groups are always within a campaign
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> List[Dict]:
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id, campaign_id=campaign_id, ad_group_id__isnull=False)

    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    summary = queryset.values(
        'ad_group_id',
        'ad_group__name',
        'ad_group__status', # Assuming AdGroup model has a status field similar to CampaignStatusChoices
        'ad_group__default_bid',
        'campaign_id',      # For context
        'campaign__name'    # For context
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('-spend', 'ad_group__name')

    results = []
    for item in summary:
        data = {
            'ad_group_id': item['ad_group_id'],
            'ad_group_name': item['ad_group__name'],
            'status': item['ad_group__status'], # Ensure AdGroup model has this status field matching choices
            'default_bid': item['ad_group__default_bid'],
            'campaign_id': item['campaign_id'],
            'campaign_name': item['campaign__name'],
            'impressions': item['impressions'],
            'clicks': item['clicks'],
            'spend': item['spend'],
            'orders': item['orders'],
            'sales': item['sales'],
        }
        results.append(_calculate_derived_metrics(data))
    return results

# TODO: Add get_product_target_performance_report in a similar fashion if needed.
# For the dashboard's top 5-7 metrics, a simpler overall aggregation might be needed:
def get_overall_dashboard_metrics(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> Dict:
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    aggregation = queryset.aggregate(
        total_impressions=Coalesce(Sum('impressions'), 0),
        total_clicks=Coalesce(Sum('clicks'), 0),
        total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
        total_orders=Coalesce(Sum('orders'), 0),
        total_sales=Coalesce(Sum('sales'), Decimal('0.00')),
    )

    # Rename keys to match DashboardMetrics schema (removing 'total_')
    data = {
        'impressions': aggregation['total_impressions'],
        'clicks': aggregation['total_clicks'],
        'spend': aggregation['total_spend'],
        'orders': aggregation['total_orders'],
        'sales': aggregation['total_sales'],
    }
    return _calculate_derived_metrics(data)

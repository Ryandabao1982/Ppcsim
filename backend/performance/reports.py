"""
Reporting functions for the Performance application.

This module contains functions to query and aggregate performance data from
the AdPerformanceMetric and SearchTermPerformance models to generate various
reports (e.g., campaign summary, keyword performance, search term reports).

These functions are typically called by API views to retrieve data for display.
They handle filtering by user, date range, and other relevant criteria,
and perform necessary calculations for derived metrics like ACOS, ROAS, CPC, CTR, CVR.
"""
from django.db.models import Sum, Avg, F, ExpressionWrapper, fields, Case, When, Value
from django.db.models.functions import Coalesce
# from django.conf import settings # Not strictly needed if User model isn't directly queried here
from decimal import Decimal, ROUND_HALF_UP
import datetime
from typing import List, Dict, Optional

# Import models from campaigns app for joining and accessing campaign/ad group/keyword details
# from campaigns.models import Campaign, AdGroup, Keyword, ProductTarget # Not strictly needed if using __ notation
from .models import AdPerformanceMetric, SearchTermPerformance # Main data sources

# User = settings.AUTH_USER_MODEL # Not directly used in aggregation funcs if user_id is passed as an argument

def _calculate_derived_metrics(data_dict: Dict) -> Dict:
    """
    Helper function to calculate derived performance metrics (ACOS, ROAS, CPC, CTR, CVR)
    from a dictionary containing aggregated sums of impressions, clicks, spend, orders, and sales.

    Args:
        data_dict (Dict): A dictionary with keys 'impressions', 'clicks', 'spend',
                          'orders', 'sales'.

    Returns:
        Dict: The input dictionary updated with calculated 'cpc', 'ctr', 'cvr',
              'acos', and 'roas'.
    """
    impressions = data_dict.get('impressions', 0)
    clicks = data_dict.get('clicks', 0)
    spend = data_dict.get('spend', Decimal('0.00'))
    orders = data_dict.get('orders', 0)
    sales = data_dict.get('sales', Decimal('0.00'))

    data_dict['cpc'] = (spend / Decimal(clicks)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if clicks > 0 else Decimal('0.00')
    data_dict['ctr'] = float(Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else 0.0
    data_dict['cvr'] = float(Decimal(orders) / Decimal(clicks) * 100) if clicks > 0 else 0.0
    data_dict['acos'] = float((spend / sales) * 100) if sales > 0 else 0.0 # ACOS is 0 if no sales, or infinite if spend > 0 and sales = 0. Conventionally 0.
    data_dict['roas'] = float(sales / spend) if spend > 0 else 0.0 # ROAS is 0 if no spend, or infinite if sales > 0 and spend = 0. Conventionally 0.

    # Ensure float metrics are rounded for consistent presentation if needed, though usually done at serializer/display level.
    # For now, direct float conversion is fine.
    return data_dict

def get_campaign_performance_summary(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> List[Dict]:
    """
    Retrieves a summary of performance metrics for all campaigns belonging to a user,
    aggregated over a specified date range.

    Args:
        user_id (int): The ID of the user whose campaigns are to be summarized.
        start_date (Optional[datetime.date]): The start date for filtering metrics.
        end_date (Optional[datetime.date]): The end date for filtering metrics.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a campaign's
                    performance summary, including calculated derived metrics.
    """
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    # Group by campaign and aggregate metrics.
    # Fetch campaign details (name, ad_type, etc.) by joining with the Campaign model
    # using the `__` notation in `values()`.
    summary = queryset.values(
        'campaign_id',
        'campaign__name',
        'campaign__ad_type',
        'campaign__status',
        'campaign__daily_budget',
        'campaign__start_date',
        'campaign__end_date' # This is the campaign's end date, not the metric period end date
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('-spend', 'campaign__name') # Example ordering: highest spend first

    results = []
    for item in summary:
        # Prepare data dictionary to match the CampaignPerformanceSerializer structure
        data = {
            'campaign_id': item['campaign_id'],
            'campaign_name': item['campaign__name'],
            'ad_type': item['campaign__ad_type'],
            'status': item['campaign__status'],
            'daily_budget': item['campaign__daily_budget'],
            'start_date': item['campaign__start_date'], # Campaign's overall start date
            'end_date': item['campaign__end_date'],     # Campaign's overall end date
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
    """
    Retrieves a performance report for keywords, filterable by campaign, ad group,
    and date range for a specific user.

    Args:
        user_id (int): The ID of the user.
        campaign_id (Optional[int]): Filter by a specific campaign ID.
        ad_group_id (Optional[int]): Filter by a specific ad group ID.
        start_date (Optional[datetime.date]): Start date for metrics.
        end_date (Optional[datetime.date]): End date for metrics.

    Returns:
        List[Dict]: A list of dictionaries, each representing a keyword's performance.
    """
    # Start with metrics related to keywords for the given user
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id, keyword_id__isnull=False)

    if campaign_id:
        queryset = queryset.filter(campaign_id=campaign_id)
    if ad_group_id: # This is the primary filter from the URL in the KeywordPerformanceListView
        queryset = queryset.filter(ad_group_id=ad_group_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    # Aggregate metrics per keyword, including details from related Keyword, AdGroup, and Campaign models.
    summary = queryset.values(
        'keyword_id',
        'keyword__text',
        'keyword__match_type',
        'keyword__bid',
        'keyword__status',
        'ad_group_id',
        'ad_group__name',
        'campaign_id', # Campaign ID from the metric record (should match ad_group__campaign_id)
        'campaign__name' # Campaign Name from the metric record's campaign link
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('campaign__name', 'ad_group__name', '-spend', 'keyword__text') # Example ordering

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

def get_adgroup_performance_summary(
    user_id: int,
    campaign_id: int, # Ad groups are always within a specific campaign
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> List[Dict]:
    """
    Retrieves a summary of performance metrics for all ad groups within a specific campaign
    for a user, aggregated over a specified date range.

    Args:
        user_id (int): The ID of the user.
        campaign_id (int): The ID of the campaign whose ad groups are to be summarized.
        start_date (Optional[datetime.date]): Start date for metrics.
        end_date (Optional[datetime.date]): End date for metrics.

    Returns:
        List[Dict]: A list of dictionaries, each representing an ad group's performance.
    """
    # Filter metrics for the given user, campaign, and ensure ad_group_id is not null
    queryset = AdPerformanceMetric.objects.filter(
        user_id=user_id,
        campaign_id=campaign_id,
        ad_group_id__isnull=False
    )

    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    # Aggregate metrics per ad group, including details from related AdGroup and Campaign models.
    summary = queryset.values(
        'ad_group_id',
        'ad_group__name',
        'ad_group__status', # Assumes AdGroup model has a 'status' field
        'ad_group__default_bid',
        'campaign_id',      # Context: Campaign ID from the metric (should be the one passed)
        'campaign__name'    # Context: Campaign Name from the metric's campaign link
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('-spend', 'ad_group__name') # Example ordering

    results = []
    for item in summary:
        data = {
            'ad_group_id': item['ad_group_id'],
            'ad_group_name': item['ad_group__name'],
            'status': item['ad_group__status'], # Ensure AdGroup model has this field and it matches choices if applicable
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

# TODO: Implement get_product_target_performance_report
# This would be similar to get_keyword_performance_report but for product_target_id,
# joining with ProductTarget model for details like targeting_type, target_value, bid, status.

def get_overall_dashboard_metrics(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None
) -> Dict:
    """
    Calculates overall account-level performance metrics for the dashboard display.
    Aggregates all performance data for the user within the given date range.

    Args:
        user_id (int): The ID of the user.
        start_date (Optional[datetime.date]): Start date for metrics.
        end_date (Optional[datetime.date]): End date for metrics.

    Returns:
        Dict: A dictionary containing total impressions, clicks, spend, orders, sales,
              and calculated ACOS, ROAS, CPC, CTR, CVR for the entire account.
    """
    queryset = AdPerformanceMetric.objects.filter(user_id=user_id)
    if start_date:
        queryset = queryset.filter(metric_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(metric_date__lte=end_date)

    # Aggregate totals across all relevant metrics for the user.
    aggregation = queryset.aggregate(
        total_impressions=Coalesce(Sum('impressions'), 0),
        total_clicks=Coalesce(Sum('clicks'), 0),
        total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
        total_orders=Coalesce(Sum('orders'), 0),
        total_sales=Coalesce(Sum('sales'), Decimal('0.00')),
    )

    # Prepare data for calculating derived metrics, matching the structure expected by _calculate_derived_metrics.
    # Keys are renamed to remove 'total_' prefix to match the DashboardMetrics schema/serializer.
    data = {
        'impressions': aggregation['total_impressions'],
        'clicks': aggregation['total_clicks'],
        'spend': aggregation['total_spend'],
        'orders': aggregation['total_orders'],
        'sales': aggregation['total_sales'],
    }
    return _calculate_derived_metrics(data)

def get_search_term_report_data(
    user_id: int,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 1000 # Default limit for pagination
) -> List[Dict]:
    """
    Retrieves Search Term Report (STR) data for a user, aggregated by search term text
    and other contextual campaign/ad group/keyword information over a specified period.
    Supports filtering by date range, campaign, ad group, and provides pagination.

    Args:
        user_id (int): The ID of the user.
        start_date (Optional[datetime.date]): Start date for STR data.
        end_date (Optional[datetime.date]): End date for STR data.
        campaign_id (Optional[int]): Filter by a specific campaign ID.
        ad_group_id (Optional[int]): Filter by a specific ad group ID.
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents an aggregated
                    search term's performance, including derived metrics.
    """
    # Start with SearchTermPerformance records for the user, prefetching related objects for efficiency.
    queryset = SearchTermPerformance.objects.filter(user_id=user_id).select_related(
        'campaign', 'ad_group', 'matched_keyword' # Pre-fetch for performance when accessing related fields
    )

    # Apply date and entity filters
    if start_date:
        queryset = queryset.filter(report_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(report_date__lte=end_date)
    if campaign_id:
        queryset = queryset.filter(campaign_id=campaign_id)
    if ad_group_id:
        queryset = queryset.filter(ad_group_id=ad_group_id)

    # The SearchTermPerformance model stores daily raw metrics. For a typical STR,
    # we aggregate these by search_term_text (and other relevant dimensions like campaign, ad group, matched keyword)
    # over the selected period.
    aggregated_terms = queryset.values(
        'search_term_text',
        'campaign_id', 'campaign__name', # Include campaign details
        'ad_group_id', 'ad_group__name', # Include ad group details
        'matched_keyword_id', 'matched_keyword__text', 'matched_keyword__match_type' # Include matched keyword details
    ).annotate(
        impressions=Coalesce(Sum('impressions'), 0),
        clicks=Coalesce(Sum('clicks'), 0),
        spend=Coalesce(Sum('spend'), Decimal('0.00')),
        orders=Coalesce(Sum('orders'), 0),
        sales=Coalesce(Sum('sales'), Decimal('0.00')),
    ).order_by('-clicks', '-impressions', 'search_term_text') # Common STR ordering: by clicks, then impressions

    # Apply pagination to the aggregated queryset
    paginated_terms = aggregated_terms[skip : skip + limit]

    results = []
    for item in paginated_terms:
        # Structure the data for each aggregated search term
        data = {
            # 'report_date': None, # Aggregated over a period, so individual report_date is not applicable here.
                                 # Could pass start/end of period if needed by frontend.
            'search_term_text': item['search_term_text'],
            'campaign_id': item['campaign_id'],
            'campaign_name': item['campaign__name'],
            'ad_group_id': item['ad_group_id'],
            'ad_group_name': item['ad_group__name'],
            'matched_keyword_id': item['matched_keyword_id'],
            'matched_keyword_text': item['matched_keyword__text'],
            'match_type': item['matched_keyword__match_type'], # This is the match type of the keyword that was triggered
            'impressions': item['impressions'],
            'clicks': item['clicks'],
            'spend': item['spend'],
            'orders': item['orders'],
            'sales': item['sales'],
        }
        # Calculate derived metrics (ACOS, ROAS, etc.) based on the *aggregated* sums for each search term.
        results.append(_calculate_derived_metrics(data))

    return results

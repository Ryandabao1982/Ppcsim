import datetime
from decimal import Decimal
from typing import List, Dict, Optional

from django.db.models import Sum, Case, When, Value, F, FloatField, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from insights_challenges.models import CoachInsightsLog, InsightTypeChoices
from performance.models import AdPerformanceMetric, SearchTermPerformance
from campaigns.models import Campaign, AdGroup, Keyword # For linking insights
from products.models import Product # For COGS
from products.keyword_data import get_all_product_keyword_data_for_asin # For negative keyword list

# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL


def _create_insight_if_not_exists_this_week(
    user_id: int,
    sim_week_start_date: datetime.date,
    insight_type: InsightTypeChoices,
    message: str,
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    keyword_id: Optional[int] = None,
    search_term_text: Optional[str] = None
):
    """
    Creates an insight log if a similar one for the same entity doesn't already exist for this week.
    """
    existing_insight_query = CoachInsightsLog.objects.filter(
        user_id=user_id,
        simulated_week_start_date=sim_week_start_date,
        insight_type=insight_type,
    )
    if campaign_id: existing_insight_query = existing_insight_query.filter(related_campaign_id=campaign_id)
    if ad_group_id: existing_insight_query = existing_insight_query.filter(related_ad_group_id=ad_group_id)
    if keyword_id: existing_insight_query = existing_insight_query.filter(related_keyword_id=keyword_id)
    if search_term_text: existing_insight_query = existing_insight_query.filter(related_search_term_text=search_term_text)

    if not existing_insight_query.exists():
        CoachInsightsLog.objects.create(
            user_id=user_id,
            simulated_week_start_date=sim_week_start_date,
            insight_type=insight_type,
            generated_message=message,
            related_campaign_id=campaign_id,
            related_ad_group_id=ad_group_id,
            related_keyword_id=keyword_id,
            related_search_term_text=search_term_text
        )
        print(f"Insight generated for user {user_id}: {insight_type.label} - {message}")
        return True
    return False


def check_budget_capping_insights(user_id: int, week_start_date: datetime.date, week_end_date: datetime.date):
    """
    Checks for campaigns hitting budget caps and generates insights.
    - Missed Scaling: Budget capped, good ACoS, growing sales.
    - Wasted Spend Risk: Budget capped, poor ACoS, stagnant/declining sales.
    """
    campaigns = Campaign.objects.filter(user_id=user_id, status='enabled')
    for campaign in campaigns:
        # 1. Check for consistent budget capping (e.g., 4+ days in the week)
        # This requires daily performance data with budget tracking, which our current AdPerformanceMetric doesn't directly store.
        # For V1, we can simplify: if total spend for the week is close to 7 * daily_budget.
        weekly_spend_limit = campaign.daily_budget * 7
        actual_weekly_spend = AdPerformanceMetric.objects.filter(
            campaign=campaign, metric_date__range=(week_start_date, week_end_date)
        ).aggregate(total_spend=Coalesce(Sum('spend'), Decimal('0.00')))['total_spend']

        budget_capped_consistently = actual_weekly_spend >= (weekly_spend_limit * Decimal('0.95')) # e.g. 95% of weekly potential

        if not budget_capped_consistently:
            continue

        # Aggregate performance for the campaign for the week
        campaign_perf = AdPerformanceMetric.objects.filter(
            campaign=campaign, metric_date__range=(week_start_date, week_end_date)
        ).aggregate(
            total_sales=Coalesce(Sum('sales'), Decimal('0.00')),
            total_spend=actual_weekly_spend # Use already calculated spend
        )

        campaign_acos = float((campaign_perf['total_spend'] / campaign_perf['total_sales']) * 100) if campaign_perf['total_sales'] > 0 else float('inf')

        # TODO: Sales Growth WoW - requires data from previous week. For V1, might omit or simplify.
        # For now, let's focus on ACoS.

        # Assuming we can get COGS ratio for the primary product of the campaign
        # This is a simplification. A campaign can have multiple products.
        primary_product = campaign.advertised_products.first()
        if not primary_product: continue

        cogs_ratio = float(primary_product.cost_of_goods_sold / primary_product.avg_selling_price) if primary_product.avg_selling_price > 0 else 1.0 # Default to 100% COGS if price is 0

        # Missed Scaling Opportunity
        profitable_acos_threshold = cogs_ratio * 100 - 10 # e.g., COGS 30% -> ACoS < 20%
        if campaign_acos <= profitable_acos_threshold:
            message = (f"Excellent progress! Your '{campaign.name}' campaign is consistently hitting its daily budget "
                       f"while delivering a strong ACoS of {campaign_acos:.2f}%. This indicates an opportunity to "
                       f"increase your daily budget to capture more market share. Don't leave profitable sales on the table!")
            _create_insight_if_not_exists_this_week(
                user_id, week_start_date, InsightTypeChoices.BUDGET_CAPPED_GOOD_PERF, message, campaign_id=campaign.id
            )

        # Wasted Spend Risk
        unprofitable_acos_threshold = cogs_ratio * 100 + 15 # e.g., COGS 30% -> ACoS > 45%
        if campaign_acos >= unprofitable_acos_threshold:
            message = (f"Your '{campaign.name}' campaign is hitting its daily budget, but its ACoS of {campaign_acos:.2f}% "
                       f"is quite high. Before increasing budget, optimize efficiency. Dive into the Search Term Report "
                       f"and Keywords Report to identify wasted spend and underperforming targets.")
            _create_insight_if_not_exists_this_week(
                user_id, week_start_date, InsightTypeChoices.BUDGET_CAPPED_POOR_PERF, message, campaign_id=campaign.id
            )


def check_wasted_spend_on_search_terms(user_id: int, week_start_date: datetime.date, week_end_date: datetime.date):
    """
    Identifies search terms with significant spend but no orders.
    """
    # This aggregates SearchTermPerformance data
    # The model already has calculated metrics, but for this rule, we need sums over the period.
    str_data = SearchTermPerformance.objects.filter(
        user_id=user_id, report_date__range=(week_start_date, week_end_date)
    ).values(
        'search_term_text', 'campaign_id', 'campaign__name', 'matched_keyword__text' # For message context
    ).annotate(
        term_spend=Sum('spend'),
        term_orders=Sum('orders')
    ).filter(term_spend__gt=Decimal('7.00'), term_orders=0) # Your threshold: Spend > $7, Orders = 0

    for item in str_data:
        # Check against product's predefined negative keywords (from keyword_data.py)
        # This requires knowing which product this search term is for.
        # SearchTermPerformance links to campaign. Campaign links to products.
        # For simplicity, we might check against negative keywords of *any* product in that campaign.
        campaign_products = Product.objects.filter(campaigns__id=item['campaign_id'])
        is_likely_irrelevant = False
        for product in campaign_products:
            product_kw_data = get_all_product_keyword_data_for_asin(product.asin)
            if product_kw_data:
                negative_keywords_for_product = [nk.strip("[]\"") for nk in product_kw_data.get("negative_keywords", [])]
                if any(neg_example in item['search_term_text'] for neg_example in negative_keywords_for_product):
                    is_likely_irrelevant = True
                    break

        if is_likely_irrelevant: # Only trigger if it matches predefined negatives for now
            message = (f"Alert! Your '{item['campaign__name']}' campaign is spending on the search term "
                       f"'{item['search_term_text']}' (spent ${item['term_spend']:.2f}) but it hasn't generated any sales. "
                       f"This term seems irrelevant. Add it as an exact negative keyword to prevent wasted spend.")
            _create_insight_if_not_exists_this_week(
                user_id, week_start_date, InsightTypeChoices.WASTED_SPEND_STR, message,
                campaign_id=item['campaign_id'], search_term_text=item['search_term_text']
            )


# --- Main Insight Generation Function ---
def generate_insights_for_user(user_id: int, current_sim_week_start_date: datetime.date):
    """
    Main function to generate all types of insights for a user for the completed week.
    This should be called AFTER run_weekly_simulation for the week ending on current_sim_week_start_date - 1 day,
    or rather, for the week *defined* by current_sim_week_start_date.
    So, if current_sim_week_start_date is Monday, this analyzes data from Monday to Sunday.
    """
    week_end_date = current_sim_week_start_date + datetime.timedelta(days=6)

    print(f"Generating insights for user {user_id} for week {current_sim_week_start_date} to {week_end_date}...")

    # Call specific check functions
    check_budget_capping_insights(user_id, current_sim_week_start_date, week_end_date)
    check_wasted_spend_on_search_terms(user_id, current_sim_week_start_date, week_end_date)
    # TODO: Implement other check functions based on defined scenarios:
    # - check_underbidding_relevant_keywords(...)
    # - check_exact_match_opportunities(...)
    # - check_high_acos_general(...)
    # - check_low_cvr_listing_issue(...)
    # - check_scaling_opportunities_general(...)

    print(f"Insight generation complete for user {user_id} for week of {current_sim_week_start_date}.")


# Example of how product COGS ratio could be used (needs Product model access)
# def get_product_cogs_ratio(product_id):
#     try:
#         product = Product.objects.get(id=product_id)
#         if product.avg_selling_price > 0:
#             return float(product.cost_of_goods_sold / product.avg_selling_price)
#     except Product.DoesNotExist:
#         return None # Or a default
#     return 1.0 # Default to 100% COGS if price is 0 or product not found, meaning any ACoS is unprofitable.

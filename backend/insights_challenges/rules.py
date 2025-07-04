import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Any

from django.db.models import Sum, Case, When, Value, F, FloatField, Q, Avg, Count
from django.db.models.functions import Coalesce
from django.utils import timezone

from insights_challenges.models import CoachInsightsLog, InsightTypeChoices
from performance.models import AdPerformanceMetric, SearchTermPerformance
from campaigns.models import Campaign, AdGroup, Keyword, MatchTypeChoices, KeywordStatusChoices
from products.models import Product
from products.keyword_data import get_all_product_keyword_data_for_asin

# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL

# --- Helper Functions ---

def _get_user_name(user_id: int) -> str:
    """Fetches user's first name or email."""
    try:
        user = User.objects.get(id=user_id)
        return user.first_name if user.first_name else user.email
    except User.DoesNotExist:
        return "Student"

def _calculate_metrics_from_agg(aggregation: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates derived metrics (ACOS, CVR, CPC, CTR) from aggregated sums."""
    data = aggregation.copy() # Avoid modifying the original dict
    impressions = data.get('total_impressions', 0)
    clicks = data.get('total_clicks', 0)
    spend = data.get('total_spend', Decimal('0.00'))
    orders = data.get('total_orders', 0)
    sales = data.get('total_sales', Decimal('0.00'))

    data['cpc'] = (spend / Decimal(clicks)) if clicks > 0 else Decimal('0.00')
    data['ctr'] = (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else Decimal('0.00')
    data['cvr'] = (Decimal(orders) / Decimal(clicks) * 100) if clicks > 0 else Decimal('0.00')
    data['acos'] = (spend / sales * 100) if sales > 0 else Decimal('inf') # Use Decimal for precision, handle inf display later

    # Convert to float for storage/comparison if needed, or keep as Decimal
    data['cpc'] = float(data['cpc'].quantize(Decimal('0.01')))
    data['ctr'] = float(data['ctr'].quantize(Decimal('0.01')))
    data['cvr'] = float(data['cvr'].quantize(Decimal('0.01')))
    data['acos'] = float(data['acos'].quantize(Decimal('0.01'))) if data['acos'] != Decimal('inf') else float('inf')

    return data

def _get_entity_performance(
    user_id: int,
    start_date: datetime.date,
    end_date: datetime.date,
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    keyword_id: Optional[int] = None,
    search_term_text: Optional[str] = None, # For SearchTermPerformance
) -> Optional[Dict[str, Any]]:
    """
    Fetches aggregated performance metrics for a specific entity over a date range.
    Returns a dictionary with summed metrics and calculated derived ones, or None if no data.
    """
    filters = Q(user_id=user_id) & Q(metric_date__range=(start_date, end_date))
    model_to_query = AdPerformanceMetric

    if campaign_id: filters &= Q(campaign_id=campaign_id)
    if ad_group_id: filters &= Q(ad_group_id=ad_group_id)
    if keyword_id: filters &= Q(keyword_id=keyword_id)

    if search_term_text: # This implies querying SearchTermPerformance
        model_to_query = SearchTermPerformance
        filters = Q(user_id=user_id) & Q(report_date__range=(start_date, end_date)) & Q(search_term_text=search_term_text)
        if campaign_id: filters &= Q(campaign_id=campaign_id) # STR can also be campaign specific
        # Add other STR specific filters if needed (ad_group_id, matched_keyword_id)

    aggregation = model_to_query.objects.filter(filters).aggregate(
        total_impressions=Coalesce(Sum('impressions'), 0),
        total_clicks=Coalesce(Sum('clicks'), 0),
        total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
        total_orders=Coalesce(Sum('orders'), 0),
        total_sales=Coalesce(Sum('sales'), Decimal('0.00')),
        # For budget capping check, count distinct days with metrics
        distinct_metric_days=Count('metric_date', distinct=True) if model_to_query == AdPerformanceMetric else Value(0)
    )

    if aggregation['total_impressions'] == 0 and aggregation['total_clicks'] == 0 and aggregation['total_spend'] == Decimal('0.00'):
        return None # No significant activity

    return _calculate_metrics_from_agg(aggregation)


def _get_wow_sales_change(
    user_id: int,
    current_week_start: datetime.date, current_week_end: datetime.date,
    prev_week_start: datetime.date, prev_week_end: datetime.date,
    campaign_id: int
) -> Optional[float]:
    """Calculates Week-over-Week sales percentage change for a campaign."""
    current_week_sales_agg = AdPerformanceMetric.objects.filter(
        user_id=user_id, campaign_id=campaign_id, metric_date__range=(current_week_start, current_week_end)
    ).aggregate(total_sales=Coalesce(Sum('sales'), Decimal('0.00')))
    current_week_sales = current_week_sales_agg['total_sales']

    prev_week_sales_agg = AdPerformanceMetric.objects.filter(
        user_id=user_id, campaign_id=campaign_id, metric_date__range=(prev_week_start, prev_week_end)
    ).aggregate(total_sales=Coalesce(Sum('sales'), Decimal('0.00')))
    prev_week_sales = prev_week_sales_agg['total_sales']

    if prev_week_sales == Decimal('0.00'):
        return float('inf') if current_week_sales > Decimal('0.00') else 0.0 # Infinite growth or no change from zero

    change_percent = ((current_week_sales - prev_week_sales) / prev_week_sales) * 100
    return float(change_percent.quantize(Decimal('0.1')))


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
    # Check for existing insight of the same type for the same entity and week
    existing_insight_query = CoachInsightsLog.objects.filter(
        user_id=user_id,
        simulated_week_start_date=sim_week_start_date,
        insight_type=insight_type,
    )
    # Narrow down by specific entity if provided
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
        # print(f"Insight generated for user {user_id} ({insight_type.label}): {message[:100]}...") # Log snippet
        return True
    # print(f"Insight already exists for user {user_id} ({insight_type.label}) this week for this entity.")
    return False

# --- Rule Implementations ---

def rule_budget_capping_scaling_opportunity(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date, prev_week_start: datetime.date, prev_week_end: datetime.date):
    """
    Insight: Consistent Budget Capping (Missed Scaling Opportunity)
    Trigger: Campaign's Daily Budget Reached TRUE for >=4/7 days, ACoS <= (Break-Even - 10%), Sales WoW >= 7%.
    """
    # Check for budget capping: total spend close to potential weekly spend (7 * daily_budget)
    # And distinct metric days >= 4 (meaning it ran for at least 4 days)
    perf_data = _get_entity_performance(user_id, week_start, week_end, campaign_id=campaign.id)
    if not perf_data or perf_data['distinct_metric_days'] < 4: return

    is_budget_capped = perf_data['total_spend'] >= (campaign.daily_budget * 7 * Decimal('0.90')) # 90% of max weekly spend as proxy

    if not is_budget_capped: return

    primary_product = campaign.advertised_products.first()
    if not primary_product: return

    break_even_acos = primary_product.break_even_acos
    target_acos = break_even_acos - 10.0

    wow_sales_change = _get_wow_sales_change(user_id, week_start, week_end, prev_week_start, prev_week_end, campaign.id)
    if wow_sales_change is None: wow_sales_change = 0.0 # Assume no change if no prior data

    if perf_data['acos'] <= target_acos and wow_sales_change >= 7.0:
        message = (
            f"Phenomenal work, {student_name}! Your '{campaign.name}' campaign for '{primary_product.product_name}' "
            f"is a powerhouse – hitting its daily budget consistently at an impressive {perf_data['acos']:.2f}% ACoS, "
            f"while sales are climbing {wow_sales_change:.1f}% week-over-week! This is the prime time to scale. "
            f"You're leaving profitable sales on the table. My clear advice: increase your daily budget by 15-25%. "
            f"Monitor closely next week, but this is how we grow accounts strategically."
        )
        _create_insight_if_not_exists_this_week(
            user_id, week_start, InsightTypeChoices.BUDGET_CAPPING_SCALING_OPPORTUNITY, message, campaign_id=campaign.id
        )

def rule_budget_capping_poor_performance(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date, prev_week_start: datetime.date, prev_week_end: datetime.date):
    """
    Insight: Budget Capping with Poor Performance (Wasted Spend Alert)
    Trigger: Campaign's Daily Budget Reached TRUE for >=4/7 days, ACoS > (Break-Even + 15%), Sales stagnant/declining.
    """
    perf_data = _get_entity_performance(user_id, week_start, week_end, campaign_id=campaign.id)
    if not perf_data or perf_data['distinct_metric_days'] < 4: return

    is_budget_capped = perf_data['total_spend'] >= (campaign.daily_budget * 7 * Decimal('0.90'))
    if not is_budget_capped: return

    primary_product = campaign.advertised_products.first()
    if not primary_product: return

    break_even_acos = primary_product.break_even_acos
    target_acos = break_even_acos + 15.0

    wow_sales_change = _get_wow_sales_change(user_id, week_start, week_end, prev_week_start, prev_week_end, campaign.id)
    if wow_sales_change is None: wow_sales_change = 0.0

    if perf_data['acos'] > target_acos and wow_sales_change <= 2.0: # Stagnant (0-2%) or declining (<0)
        message = (
            f"Urgent attention needed for your '{campaign.name}' campaign, {student_name}. "
            f"While you're hitting your daily budget, your ACoS of {perf_data['acos']:.2f}% is far too high. "
            f"This means we're maxing out our spend but not generating profitable returns. Do NOT increase your budget. "
            f"Instead, your immediate focus should be campaign optimization. Head straight to your Search Term Report "
            f"and Keywords Report to identify irrelevant spend and underperforming keywords. Let's plug those budget leaks first!"
        )
        _create_insight_if_not_exists_this_week(
            user_id, week_start, InsightTypeChoices.BUDGET_CAPPING_POOR_PERFORMANCE, message, campaign_id=campaign.id
        )

def rule_high_spend_irrelevant_search_terms(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date):
    """
    Insight: High Spend on Irrelevant Search Terms (Negative Keyword Imperative)
    Trigger: Search Term Spend > $7, Orders = 0, CVR < 0.05%, from Broad/Phrase, contains irrelevant_keywords.
    """
    # This rule needs SearchTermPerformance data.
    # Querying STR data aggregated by search_term_text for the week.
    str_items = SearchTermPerformance.objects.filter(
        user_id=user_id, campaign_id=campaign.id, report_date__range=(week_start, week_end),
        matched_keyword__match_type__in=[MatchTypeChoices.BROAD, MatchTypeChoices.PHRASE]
    ).values('search_term_text', 'matched_keyword__text').annotate(
        term_spend=Sum('spend'),
        term_orders=Sum('orders'),
        term_clicks=Sum('clicks') # Need clicks for CVR
    ).filter(term_spend__gt=Decimal('7.00'), term_orders=0)

    primary_product = campaign.advertised_products.first() # Assuming one main product for irrelevant_keywords check
    if not primary_product: return
    product_kw_data = get_all_product_keyword_data_for_asin(primary_product.asin)
    irrelevant_keywords_for_product = [
        kw.lower() for kw in product_kw_data.get("negative_keywords", []) # Using 'negative_keywords' as 'irrelevant_keywords'
    ] if product_kw_data else []


    for item in str_items:
        term_cvr = (Decimal(item['term_orders']) / Decimal(item['term_clicks']) * 100) if item['term_clicks'] > 0 else Decimal('0.00')

        is_irrelevant_by_list = any(neg_kw in item['search_term_text'].lower() for neg_kw in irrelevant_keywords_for_product)

        if float(term_cvr) < 0.05 and is_irrelevant_by_list:
            message = (
                f"Critical alert, {student_name}! I've detected wasted ad spend in your '{campaign.name}' campaign. "
                f"The search term '{item['search_term_text']}' has consumed ${item['term_spend']:.2f} without a single conversion. "
                f"This is a common pitfall for new managers! You absolutely must add '{item['search_term_text']}' "
                f"as an exact negative keyword to your campaign or ad group. This will prevent future irrelevant clicks "
                f"and drastically improve your campaign efficiency."
            )
            _create_insight_if_not_exists_this_week(
                user_id, week_start, InsightTypeChoices.HIGH_SPEND_IRRELEVANT_SEARCH_TERMS, message,
                campaign_id=campaign.id, search_term_text=item['search_term_text']
            )

def rule_underbidding_relevant_keywords(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date):
    """
    Insight: Underbidding for Relevant Keywords (Missed Visibility)
    Trigger: Enabled Keyword, Low Impressions/Clicks, Primary Keyword or good historical CVR, Bid < 20% below Est. Top of Search.
    """
    # This is complex due to "historical CVR" and "Est. Top of Search Bid".
    # V1: Simplify: Focus on primary keywords with low impressions.

    primary_product = campaign.advertised_products.first()
    if not primary_product: return
    product_kw_data = get_all_product_keyword_data_for_asin(primary_product.asin)
    primary_keywords_text = [pk.strip("[]") for pk in product_kw_data.get("primary_keywords", [])] if product_kw_data else []

    for ad_group in campaign.ad_groups.filter(status=KeywordStatusChoices.ENABLED):
        for keyword in ad_group.keywords.filter(status=KeywordStatusChoices.ENABLED, text__in=primary_keywords_text):
            perf_data = _get_entity_performance(user_id, week_start, week_end, keyword_id=keyword.id)

            impression_threshold = 150 if primary_product.competitive_intensity == 'high' else 250
            clicks_threshold = 15

            # Simplified: if impressions are low
            if perf_data and perf_data['total_impressions'] < impression_threshold and perf_data['total_clicks'] < clicks_threshold:
                # Simplified "Top of Search Bid" proxy: category_avg_bid * 1.2 (very rough)
                category_avg_bid = primary_product.category_avg_bid if hasattr(primary_product, 'category_avg_bid') else Decimal("1.00") # Assume Product model has this or a getter
                # Actual product model has `get_category_avg_bid(competitive_intensity)` - need to call that.
                # This implies `primary_product.get_category_avg_bid()` - but it's not on the model.
                # Let's use the helper from simulation_logic.py for now.
                # from performance.simulation_logic import get_category_avg_bid # Avoid circular import
                # For now, use a fixed multiplier on current bid as a proxy for being too low.
                # Ryan's logic: "Current Bid ... more than 20% below ... Top of Search Bid"
                # Simplified: If keyword bid is below category average significantly for a primary keyword.

                # This part needs a better proxy for "Top of Search Bid".
                # For now, if it's a primary keyword with low impressions, suggest a bid increase.
                message = (
                    f"Opportunity knocking, {student_name}! Your highly relevant keyword, '{keyword.text},' "
                    f"in '{campaign.name}' isn't reaching its full potential. It's only generating "
                    f"{perf_data['total_impressions']} impressions this week, suggesting it's getting lost in the noise. "
                    f"Your current bid of ${keyword.bid:.2f} might be too low. "
                    f"Consider gradually increasing your bid by 10-15% for this keyword. "
                    f"Let's get more eyes on your product for this high-intent search!"
                )
                _create_insight_if_not_exists_this_week(
                    user_id, week_start, InsightTypeChoices.UNDERBIDDING_RELEVANT_KEYWORDS, message,
                    campaign_id=campaign.id, ad_group_id=ad_group.id, keyword_id=keyword.id
                )


def rule_exact_match_opportunity_str(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date, prev_week_start: datetime.date, prev_week_end: datetime.date):
    """
    Insight: Exact Match Opportunity Identified (The "Goldmine" Discovery)
    Trigger: Search Term (Broad/Phrase) Orders > 7 AND ACoS < 20% (or ACoS 10% < campaign_avg_acos), sustained 2 weeks.
    """
    # Current week performance for search terms
    current_week_str_perf = SearchTermPerformance.objects.filter(
        user_id=user_id, campaign_id=campaign.id, report_date__range=(week_start, week_end),
        matched_keyword__match_type__in=[MatchTypeChoices.BROAD, MatchTypeChoices.PHRASE]
    ).values('search_term_text', 'matched_keyword__text', 'matched_keyword__match_type').annotate(
        current_orders=Sum('orders'), current_spend=Sum('spend'), current_sales=Sum('sales')
    ).filter(current_orders__gt=7)

    campaign_avg_perf_current_week = _get_entity_performance(user_id, week_start, week_end, campaign_id=campaign.id)
    campaign_avg_acos_current = campaign_avg_perf_current_week['acos'] if campaign_avg_perf_current_week else float('inf')

    for item_cur in current_week_str_perf:
        current_term_acos = (item_cur['current_spend'] / item_cur['current_sales'] * 100) if item_cur['current_sales'] > 0 else float('inf')

        acos_condition_met = (current_term_acos < 20.0) or \
                             (campaign_avg_acos_current != float('inf') and current_term_acos < (campaign_avg_acos_current - 10.0))

        if not acos_condition_met: continue

        # Check previous week's performance for the same search term
        prev_week_term_perf = SearchTermPerformance.objects.filter(
            user_id=user_id, campaign_id=campaign.id, search_term_text=item_cur['search_term_text'],
            report_date__range=(prev_week_start, prev_week_end),
            matched_keyword__match_type__in=[MatchTypeChoices.BROAD, MatchTypeChoices.PHRASE]
        ).aggregate(prev_orders=Sum('orders'), prev_spend=Sum('spend'), prev_sales=Sum('sales'))

        if prev_week_term_perf['prev_orders'] is None or prev_week_term_perf['prev_orders'] <= 7: continue # Not sustained

        prev_term_acos = (prev_week_term_perf['prev_spend'] / prev_week_term_perf['prev_sales'] * 100) if prev_week_term_perf['prev_sales'] and prev_week_term_perf['prev_sales'] > 0 else float('inf')

        campaign_avg_perf_prev_week = _get_entity_performance(user_id, prev_week_start, prev_week_end, campaign_id=campaign.id)
        campaign_avg_acos_prev = campaign_avg_perf_prev_week['acos'] if campaign_avg_perf_prev_week else float('inf')

        prev_acos_condition_met = (prev_term_acos < 20.0) or \
                                  (campaign_avg_acos_prev != float('inf') and prev_term_acos < (campaign_avg_acos_prev - 10.0))

        if prev_acos_condition_met: # Sustained good performance
            primary_product_name = campaign.advertised_products.first().product_name if campaign.advertised_products.exists() else "your product"
            message = (
                f"Absolutely brilliant analysis, {student_name}! You've struck gold with the search term "
                f"'{item_cur['search_term_text']}' for {primary_product_name}. It's delivering fantastic sales at an incredible "
                f"{current_term_acos:.2f}% ACoS under your current {item_cur['matched_keyword__match_type']} match keyword "
                f"('{item_cur['matched_keyword__text']}'). This is the perfect candidate for an exact match keyword. "
                f"Create a new exact match keyword for '{item_cur['search_term_text']}', ideally in its own ad group. "
                f"This gives you ultimate control over bidding and maximizes profitability for this winning term. Keep finding these!"
            )
            _create_insight_if_not_exists_this_week(
                user_id, week_start, InsightTypeChoices.EXACT_MATCH_OPPORTUNITY_STR, message,
                campaign_id=campaign.id, search_term_text=item_cur['search_term_text']
            )


def rule_high_acos_general_inefficiency(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date, prev_week_start: datetime.date, prev_week_end: datetime.date):
    """
    Insight: High ACoS (General Inefficiency)
    Trigger: Campaign/AdGroup/Keyword ACoS > (Break-Even + 15%) for 2 consecutive weeks, Spend > $25.
    """
    # Check Campaign Level
    primary_product = campaign.advertised_products.first()
    if not primary_product: return
    break_even_acos = primary_product.break_even_acos
    target_acos_threshold = break_even_acos + 15.0

    current_perf = _get_entity_performance(user_id, week_start, week_end, campaign_id=campaign.id)
    prev_perf = _get_entity_performance(user_id, prev_week_start, prev_week_end, campaign_id=campaign.id)

    if current_perf and current_perf['total_spend'] > Decimal('25.00') and current_perf['acos'] > target_acos_threshold and \
       prev_perf and prev_perf['total_spend'] > Decimal('25.00') and prev_perf['acos'] > target_acos_threshold:
        message = (
            f"{student_name}, we need to address the efficiency of your '{campaign.name}' campaign. "
            f"An ACoS of {current_perf['acos']:.2f}% is signaling significant unprofitability. This campaign "
            f"is spending ${current_perf['total_spend']:.2f} but not delivering enough in return. Your action plan: "
            f"pause any visibly underperforming keywords/targets immediately, and then conduct a thorough "
            f"Search Term Report audit to identify and negate any further irrelevant search terms. We need to tighten up spend here."
        )
        _create_insight_if_not_exists_this_week(
            user_id, week_start, InsightTypeChoices.HIGH_ACOS_GENERAL_INEFFICIENCY, message, campaign_id=campaign.id
        )

    # TODO: Extend to AdGroup and Keyword levels if desired, iterating through them.


def rule_low_cvr_relevant_traffic_listing_red_flag(user_id: int, student_name: str, campaign: Campaign, week_start: datetime.date, week_end: datetime.date):
    """
    Insight: Low CVR Despite Relevant Traffic (Listing/Product Red Flag)
    Trigger: Campaign/AdGroup/Keyword Clicks > 75, CVR < 0.7%, ACoS > 70%.
    Implicit: Majority of search terms are relevant (harder to check systematically in V1 without advanced NLP).
    """
    # Check Campaign Level
    perf_data = _get_entity_performance(user_id, week_start, week_end, campaign_id=campaign.id)
    if not perf_data: return

    if perf_data['total_clicks'] > 75 and perf_data['cvr'] < 0.7 and perf_data['acos'] > 70.0:
        primary_product_name = campaign.advertised_products.first().product_name if campaign.advertised_products.exists() else "your product"
        message = (
            f"Interesting case with your '{primary_product_name}' campaign, {student_name}. "
            f"Your ads are successfully driving {perf_data['total_clicks']} relevant clicks, which is excellent targeting! "
            f"However, the Conversion Rate (CVR) is only {perf_data['cvr']:.2f}%, leading to a very high ACoS of {perf_data['acos']:.2f}%. "
            f"This often indicates the bottleneck isn't the ad, but the product listing itself. "
            f"Critically review your '{primary_product_name}'s images, title, bullet points, A+ Content, and customer reviews. "
            f"Is it compelling enough to convert those valuable clicks into sales once customers land on the page?"
        )
        _create_insight_if_not_exists_this_week(
            user_id, week_start, InsightTypeChoices.LOW_CVR_RELEVANT_TRAFFIC_LISTING_RED_FLAG, message, campaign_id=campaign.id
        )
    # TODO: Extend to AdGroup and Keyword levels if desired.


# --- Main Insight Generation Function ---
def generate_insights_for_user(user_id: int, current_sim_week_start_date: datetime.date):
    """
    Main function to generate all types of insights for a user for the completed week.
    """
    week_end_date = current_sim_week_start_date + datetime.timedelta(days=6)
    prev_week_start_date = current_sim_week_start_date - datetime.timedelta(days=7)
    prev_week_end_date = current_sim_week_start_date - datetime.timedelta(days=1)

    student_name = _get_user_name(user_id)

    print(f"Generating insights for user {user_id} ({student_name}) for week {current_sim_week_start_date} to {week_end_date}...")

    campaigns = Campaign.objects.filter(user_id=user_id, status=CampaignStatusChoices.ENABLED).prefetch_related('advertised_products')

    for campaign in campaigns:
        # Call rule functions for each campaign
        rule_budget_capping_scaling_opportunity(user_id, student_name, campaign, current_sim_week_start_date, week_end_date, prev_week_start_date, prev_week_end_date)
        rule_budget_capping_poor_performance(user_id, student_name, campaign, current_sim_week_start_date, week_end_date, prev_week_start_date, prev_week_end_date)
        rule_high_spend_irrelevant_search_terms(user_id, student_name, campaign, current_sim_week_start_date, week_end_date)
        rule_underbidding_relevant_keywords(user_id, student_name, campaign, current_sim_week_start_date, week_end_date) # Consider if prev week data needed for historical CVR
        rule_exact_match_opportunity_str(user_id, student_name, campaign, current_sim_week_start_date, week_end_date, prev_week_start_date, prev_week_end_date)
        rule_high_acos_general_inefficiency(user_id, student_name, campaign, current_sim_week_start_date, week_end_date, prev_week_start_date, prev_week_end_date)
        rule_low_cvr_relevant_traffic_listing_red_flag(user_id, student_name, campaign, current_sim_week_start_date, week_end_date)

    print(f"Insight generation complete for user {user_id} for week of {current_sim_week_start_date}.")

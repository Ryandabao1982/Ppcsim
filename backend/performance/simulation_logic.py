"""
Core simulation logic for the Amazon Ads Simulator.

This module is responsible for simulating the performance of ad campaigns over a period (typically a week),
calculating metrics like impressions, clicks, spend, orders, and sales based on various factors
including bids, product relevance, market conditions (simplified), and campaign settings.

The main entry point is `run_weekly_simulation`, which iterates through each active campaign,
ad group, and target (keywords, product targets) for a given user, simulates their daily performance
for a week, and stores the resulting metrics in the AdPerformanceMetric model.

Helper functions are used to model:
- Bid impact on impression volume.
- Product relevance and quality influencing CTR and CVR.
- Match type and targeting type efficiency.
- Dynamic CTR and CVR calculations.
- Simulated Cost Per Click (CPC) based on bids and competition.
- Daily budget capping.
"""
import random
import datetime
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP # Added ROUND_HALF_UP
import math
from typing import Optional, Dict # Ensure Dict is imported for type hinting

from django.db import transaction
from django.conf import settings

from campaigns.models import (
    Campaign, Keyword, ProductTarget, CampaignStatusChoices,
    KeywordStatusChoices, ProductTargetStatusEnum, # Corrected Enum name
    MatchTypeChoices, ProductTargetingTypeChoices
)
from products.models import Product
from products.keyword_data import get_all_product_keyword_data_for_asin # For product-specific keyword/negative data
from .models import AdPerformanceMetric, SearchTermPerformance, PlacementChoices # Local models

User = settings.AUTH_USER_MODEL

# --- Helper Functions for Simulation ---

def get_category_avg_bid(competitive_intensity: Optional[str]) -> Decimal:
    """
    Determines a base average bid for a product category based on its competitive intensity.
    This serves as a benchmark for evaluating student bids.
    """
    if competitive_intensity == 'high': return Decimal("1.50")
    if competitive_intensity == 'low': return Decimal("0.50")
    return Decimal("1.00") # Default for 'medium' or undefined

def calculate_bid_impact_multiplier(bid: Decimal, category_avg_bid: Decimal) -> float:
    """
    Calculates a multiplier based on how the student's bid compares to the category average.
    A higher bid relative to the average generally results in a higher multiplier,
    influencing potential impressions. Uses a non-linear relationship (power function).
    """
    if category_avg_bid <= Decimal('0'): return 0.05 if bid <= Decimal('0') else 1.0 # Avoid division by zero
    bid_ratio = float(bid / category_avg_bid)
    if bid_ratio <= 0: return 0.05 # Minimal impact for zero or negative bids
    # Power function to model diminishing returns for very high bids and significant impact for competitive bids.
    return bid_ratio ** 0.7

def get_product_relevance_multiplier(product: Product) -> float:
    """
    Calculates a multiplier reflecting the overall attractiveness and relevance of a product.
    Factors considered: average star rating, review count, and baseline CVR (as a proxy for appeal).
    This multiplier affects both potential impressions and Click-Through Rate (CTR).
    Future: Could use `current_avg_star_rating`, `current_review_count` if these evolve in simulation.
    """
    multiplier = 1.0
    avg_star_rating = getattr(product, 'current_avg_star_rating', product.avg_star_rating)
    review_count = getattr(product, 'current_review_count', product.review_count)

    if avg_star_rating is not None:
        if avg_star_rating >= 4.5: multiplier += 0.15
        elif avg_star_rating >= 4.0: multiplier += 0.05
        elif avg_star_rating < 3.5: multiplier -= 0.10 # Slightly lower penalty
    if review_count is not None:
        if review_count > 1000: multiplier += 0.15
        elif review_count > 100: multiplier += 0.05
        elif review_count < 20: multiplier -= 0.10 # Slightly lower penalty

    # Baseline CVR as an indicator of product appeal
    if product.initial_cvr_baseline > 0.05: # High baseline CVR
        multiplier += 0.10
    elif product.initial_cvr_baseline < 0.01: # Very low baseline CVR
        multiplier -= 0.05

    return max(0.5, min(1.5, multiplier)) # Clamp multiplier between 0.5 and 1.5

def get_match_type_efficiency(match_type: str) -> float:
    """
    Returns an efficiency factor based on keyword match type.
    Exact match is most efficient, followed by Phrase, then Broad.
    This affects potential impressions and the specificity factor in CTR.
    """
    if match_type == MatchTypeChoices.EXACT: return 1.0
    if match_type == MatchTypeChoices.PHRASE: return 0.85
    if match_type == MatchTypeChoices.BROAD: return 0.65
    return 0.7 # Default for unspecified or new match types

def get_keyword_relevance_for_ctr(keyword_text: str, product: Product) -> float:
    """
    Estimates the relevance of a keyword to a specific product, influencing CTR.
    Checks against predefined primary keywords and general search terms for the product.
    """
    product_data = get_all_product_keyword_data_for_asin(product.asin)
    if not product_data: return 0.8 # Default relevance if no specific data

    primary_keywords = [pk.strip("[]") for pk in product_data.get("primary_keywords", [])]
    if keyword_text in primary_keywords: return 1.2 # Higher relevance for primary keywords
    if keyword_text in product_data.get("general_search_terms", []): return 1.0
    if keyword_text.lower() in product.product_name.lower(): return 0.9 # Moderate relevance if in product name
    return 0.7 # Lower relevance otherwise

def calculate_dynamic_ctr(base_ctr: float, product_relevance: float, target_specificity: float, ad_rank_factor: float) -> float:
    """
    Calculates a dynamic Click-Through Rate (CTR).

    Args:
        base_ctr (float): A baseline CTR for the ad type/placement.
        product_relevance (float): Multiplier from get_product_relevance_multiplier.
        target_specificity (float): Multiplier based on match type efficiency or keyword relevance.
        ad_rank_factor (float): Simplified factor representing ad rank (higher bid can improve this).

    Returns:
        float: The calculated dynamic CTR, clamped within a realistic range.
    """
    dynamic_ctr = base_ctr * product_relevance * target_specificity * ad_rank_factor
    return max(0.0001, min(dynamic_ctr, 0.15)) # Clamp CTR (e.g., 0.01% to 15%)

def calculate_simulated_cpc(student_bid: Decimal, category_avg_bid: Decimal, competitive_intensity: Optional[str]) -> Decimal:
    """
    Simulates Cost Per Click (CPC) using a simplified second-price auction model.
    The CPC is influenced by the student's bid and a simulated competitor bid (proxied by category average and intensity).
    Ensures CPC is at least a minimum value (e.g., $0.02).
    """
    comp_factor = Decimal('1.0')
    if competitive_intensity == 'high': comp_factor = Decimal('1.1')
    elif competitive_intensity == 'low': comp_factor = Decimal('0.8')

    # Simulate a competitor's bid based on category average, intensity, and some randomness
    sim_competitor_bid_proxy = category_avg_bid * comp_factor * Decimal(random.uniform(0.7, 1.1))

    # CPC is typically the competitor's bid + a small increment, capped by student's own bid
    cpc = min(student_bid, sim_competitor_bid_proxy + Decimal(random.uniform(0.01, 0.05)))
    return max(Decimal("0.02"), cpc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) # Ensure minimum CPC and 2 decimal places

# --- CVR (Conversion Rate) Helper Functions ---

def get_product_quality_cvr_multiplier(product: Product) -> float:
    """
    Calculates a multiplier for CVR based on product quality attributes (rating, reviews).
    Similar to `get_product_relevance_multiplier` but can have a more sensitive impact on CVR.
    """
    multiplier = 1.0
    avg_star_rating = getattr(product, 'current_avg_star_rating', product.avg_star_rating)
    review_count = getattr(product, 'current_review_count', product.review_count)

    if avg_star_rating is not None: # More sensitive impact for CVR
        if avg_star_rating >= 4.7: multiplier += 0.25
        elif avg_star_rating >= 4.2: multiplier += 0.12
        elif avg_star_rating < 3.8: multiplier -= 0.20
        elif avg_star_rating < 3.0: multiplier -= 0.40 # Significant penalty for very low ratings
    if review_count is not None:
        if review_count > 1500: multiplier += 0.25
        elif review_count > 200: multiplier += 0.12
        elif review_count < 50: multiplier -= 0.15
        elif review_count < 10: multiplier -= 0.30 # Significant penalty for very few reviews

    return max(0.2, min(1.8, multiplier)) # Clamp CVR quality multiplier

def get_search_term_relevance_cvr_multiplier(keyword_text_proxy: str, product: Product, is_negative_example_match: bool) -> float:
    """
    Estimates how relevant a search term (proxied by keyword text here) is for conversion for a given product.
    Penalizes heavily if the term resembles predefined negative keywords for the product.
    Boosts for primary keywords.

    Args:
        keyword_text_proxy (str): The keyword text, used as a proxy for the search term.
        product (Product): The advertised product.
        is_negative_example_match (bool): True if keyword_text_proxy matches a negative pattern for the product.

    Returns:
        float: A multiplier affecting CVR.
    """
    if is_negative_example_match:
        return 0.1 # Heavily penalize CVR if the keyword itself is like a negative term

    product_data = get_all_product_keyword_data_for_asin(product.asin)
    if not product_data: return 0.9 # Default if no specific mapping

    primary_keywords = [pk.strip("[]") for pk in product_data.get("primary_keywords", [])]

    if keyword_text_proxy in primary_keywords: return 1.25 # Boost for highly relevant (primary keyword match)
    if keyword_text_proxy in product_data.get("general_search_terms", []): return 1.0
    if keyword_text_proxy.lower() in product.product_name.lower(): return 0.95 # Slight boost if in product name
    return 0.8 # General fallback for less relevant terms

def calculate_dynamic_cvr(base_cvr: float, quality_mult: float, search_term_rel_mult: float, seasonality_mult: float = 1.0) -> float:
    """
    Calculates a dynamic Conversion Rate (CVR).

    Args:
        base_cvr (float): The product's baseline CVR.
        quality_mult (float): Multiplier from get_product_quality_cvr_multiplier.
        search_term_rel_mult (float): Multiplier from get_search_term_relevance_cvr_multiplier.
        seasonality_mult (float, optional): Multiplier for seasonality effects (default 1.0).

    Returns:
        float: The calculated dynamic CVR, clamped within a realistic range.
    """
    dynamic_cvr = base_cvr * quality_mult * search_term_rel_mult * seasonality_mult
    return max(0.00001, min(dynamic_cvr, 0.60)) # Clamp CVR (e.g., 0.001% to 60%)

def _calculate_derived_metrics_for_storage(data_dict: Dict) -> Dict:
    """
    Helper identical to reports._calculate_derived_metrics, used for pre-calculating
    metrics before storing in AdPerformanceMetric. Avoids circular import.
    """
    impressions = data_dict.get('impressions', 0)
    clicks = data_dict.get('clicks', 0)
    spend = data_dict.get('spend', Decimal('0.00'))
    orders = data_dict.get('orders', 0)
    sales = data_dict.get('sales', Decimal('0.00'))

    data_dict['cpc'] = (spend / Decimal(clicks)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if clicks > 0 else Decimal('0.00')
    data_dict['ctr'] = float(Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else 0.0
    data_dict['cvr'] = float(Decimal(orders) / Decimal(clicks) * 100) if clicks > 0 else 0.0
    data_dict['acos'] = float((spend / sales) * 100) if sales > 0 else 0.0
    data_dict['roas'] = float(sales / spend) if spend > 0 else 0.0
    return data_dict

# --- Main Simulation Function ---

def run_weekly_simulation(user_id: int, current_sim_date: datetime.date):
    """
    Runs the main weekly simulation loop for a given user.
    Iterates 7 days, processing active campaigns, ad groups, keywords, and product targets.
    Calculates daily performance metrics and stores them.

    Args:
        user_id (int): The ID of the user for whom to run the simulation.
        current_sim_date (datetime.date): The starting date of the simulation week.
    """
    print(f"Running weekly simulation for user_id {user_id} for week starting {current_sim_date}...")

    # Fetch all campaigns for the user with related data to minimize DB queries in the loop
    user_campaigns = Campaign.objects.filter(user_id=user_id).prefetch_related(
        'advertised_products',
        'ad_groups__keywords', # Keywords within ad groups
        'ad_groups__product_targets' # Product targets within ad groups
    ).all()

    if not user_campaigns:
        print(f"No campaigns found for user_id {user_id}. Simulation ends.")
        return

    all_metrics_to_create = [] # List to hold AdPerformanceMetric objects for bulk creation

    # Loop through each campaign
    for campaign in user_campaigns:
        if not campaign.advertised_products.exists():
            # print(f"Campaign '{campaign.name}' (ID: {campaign.id}) has no advertised products. Skipping.")
            continue # Skip campaign if no products are associated

        advertised_products_in_campaign = list(campaign.advertised_products.all())

        # --- Daily Simulation Loop (for 7 days) ---
        for i in range(7):
            simulated_day_date = current_sim_date + datetime.timedelta(days=i)
            campaign_daily_spent_so_far = Decimal('0.00') # Track daily spend against campaign budget

            # Check if campaign is active for the simulated day
            if not (campaign.start_date <= simulated_day_date and \
                    (campaign.end_date is None or campaign.end_date >= simulated_day_date) and \
                    campaign.status == CampaignStatusChoices.ENABLED):
                # print(f"Campaign '{campaign.name}' not active on {simulated_day_date}. Skipping day for this campaign.")
                continue

            # Loop through ad groups in the campaign
            for ad_group in campaign.ad_groups.all():
                if ad_group.status != KeywordStatusChoices.ENABLED: # Assuming AdGroup uses similar status choices
                    # print(f"Ad Group '{ad_group.name}' not enabled. Skipping.")
                    continue

                # --- Keywords Simulation ---
                for keyword in ad_group.keywords.all():
                    if keyword.status != KeywordStatusChoices.ENABLED: continue
                    if campaign_daily_spent_so_far >= campaign.daily_budget: continue # Stop if daily budget exhausted

                    # Select a random product from the campaign's advertised list for this keyword interaction
                    # This simplifies by not linking keywords to specific products within an ad group if multiple exist
                    product_adv = random.choice(advertised_products_in_campaign)

                    # Impression Calculation Inputs
                    category_avg_bid = get_category_avg_bid(product_adv.competitive_intensity)
                    bid_impact_mult = calculate_bid_impact_multiplier(keyword.bid, category_avg_bid)
                    product_relevance_mult = get_product_relevance_multiplier(product_adv)
                    match_type_eff = get_match_type_efficiency(keyword.match_type)

                    # Base daily impressions (can be tuned or made dynamic later)
                    keyword_base_daily_impressions = 700 / 7.0 # Simplified from weekly
                    potential_impressions = keyword_base_daily_impressions * bid_impact_mult * product_relevance_mult * match_type_eff * random.uniform(0.8, 1.2)
                    daily_impressions = max(0, int(potential_impressions))

                    # CTR Calculation Inputs
                    keyword_relevance_ctr = get_keyword_relevance_for_ctr(keyword.text, product_adv)
                    # Simplified Ad Rank Factor: higher bid ratio can slightly improve CTR
                    ad_rank_factor_ctr = max(0.5, min(1.5, 1.0 + (bid_impact_mult - 1.0) * 0.2)) # Modest impact

                    # Base CTR (can be tuned, e.g., 0.6% for SP keywords)
                    dynamic_ctr = calculate_dynamic_ctr(0.006, product_relevance_mult, keyword_relevance_ctr * match_type_eff, ad_rank_factor_ctr)
                    potential_clicks = max(0, int(daily_impressions * dynamic_ctr))

                    # CPC, Spend, and Budget Capping
                    daily_clicks = 0; daily_spend = Decimal('0.00')
                    if potential_clicks > 0:
                        cpc = calculate_simulated_cpc(keyword.bid, category_avg_bid, product_adv.competitive_intensity)
                        potential_spend_for_clicks = Decimal(potential_clicks) * cpc

                        remaining_daily_budget = campaign.daily_budget - campaign_daily_spent_so_far
                        if remaining_daily_budget <= Decimal('0.01'): # Effectively no budget left
                            daily_clicks = 0; daily_spend = Decimal('0.00'); daily_impressions = 0 # No activity if no budget
                        elif potential_spend_for_clicks > remaining_daily_budget: # Not enough budget for all potential clicks
                            if cpc > 0: daily_clicks = math.floor(remaining_daily_budget / cpc) # Max clicks within budget
                            else: daily_clicks = potential_clicks # Free clicks if CPC is somehow zero
                            daily_spend = Decimal(daily_clicks) * cpc
                            # Adjust impressions proportionally if clicks are capped by budget
                            if potential_clicks > 0: daily_impressions = int(daily_impressions * (Decimal(daily_clicks)/Decimal(potential_clicks)))
                        else: # Enough budget
                            daily_clicks = potential_clicks; daily_spend = potential_spend_for_clicks

                        campaign_daily_spent_so_far += daily_spend

                    # If budget capped all spend, ensure impressions are also zeroed out if no clicks happened.
                    if campaign_daily_spent_so_far >= campaign.daily_budget and daily_spend == Decimal('0.00') and daily_clicks == 0 and daily_impressions > 0:
                         daily_impressions = 0

                    # CVR & Sales/Orders Logic for Keywords
                    daily_orders = 0; daily_sales = Decimal('0.00')
                    if daily_clicks > 0:
                        prod_quality_cvr_mult = get_product_quality_cvr_multiplier(product_adv)

                        # Check if the keyword text itself resembles a negative term for THIS product.
                        product_keyword_data = get_all_product_keyword_data_for_asin(product_adv.asin)
                        is_neg_example = any(
                            neg_kw.strip("[]\"").lower() in keyword.text.lower()
                            for neg_kw in product_keyword_data.get("negative_keywords", [])
                        )
                        search_term_rel_cvr_mult = get_search_term_relevance_cvr_multiplier(keyword.text, product_adv, is_neg_example)

                        # TODO: Integrate seasonality_cvr_mult later
                        dynamic_cvr = calculate_dynamic_cvr(product_adv.initial_cvr_baseline, prod_quality_cvr_mult, search_term_rel_cvr_mult)

                        # Simulate orders based on CVR for each click
                        for _ in range(daily_clicks):
                            if random.random() < dynamic_cvr:
                                daily_orders += 1
                        daily_sales = Decimal(daily_orders) * product_adv.avg_selling_price

                    # Pre-calculate all metrics for AdPerformanceMetric instance
                    metric_data_payload = {
                        'impressions': daily_impressions, 'clicks': daily_clicks, 'spend': daily_spend,
                        'orders': daily_orders, 'sales': daily_sales
                    }
                    derived_metrics = _calculate_derived_metrics_for_storage(metric_data_payload)

                    all_metrics_to_create.append(AdPerformanceMetric(
                        metric_date=simulated_day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=keyword.id,
                        impressions=daily_impressions, clicks=daily_clicks, spend=daily_spend.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                        orders=daily_orders, sales=daily_sales.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                        placement=random.choice(PlacementChoices.choices)[0], # Random placement for now
                        acos=derived_metrics['acos'], roas=derived_metrics['roas'],
                        cpc=derived_metrics['cpc'], ctr=derived_metrics['ctr'], cvr=derived_metrics['cvr']
                    ))

                # --- Product Targets Simulation ---
                for pt in ad_group.product_targets.all():
                    if pt.status != ProductTargetStatusChoices.ENABLED: continue # Use correct Enum
                    if campaign_daily_spent_so_far >= campaign.daily_budget: continue

                    product_adv = random.choice(advertised_products_in_campaign)
                    actual_bid = pt.bid or ad_group.default_bid or Decimal("0.50") # Use AdGroup default if PT bid is null

                    category_avg_bid = get_category_avg_bid(product_adv.competitive_intensity)
                    bid_impact_mult_pt = calculate_bid_impact_multiplier(actual_bid, category_avg_bid)
                    product_relevance_mult_pt = get_product_relevance_multiplier(product_adv)

                    # Base impressions for product targets (can be tuned)
                    base_imp_pt_daily = (400 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 1200) / 7.0
                    # Target efficiency (ASIN targeting might be more specific/lower volume than category)
                    target_type_eff_pt = 0.9 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 0.7

                    potential_imp_pt = base_imp_pt_daily * bid_impact_mult_pt * product_relevance_mult_pt * target_type_eff_pt * random.uniform(0.7, 1.3)
                    daily_pt_impressions = max(0, int(potential_imp_pt))

                    # CTR for Product Targets
                    ad_rank_factor_pt_ctr = max(0.6, min(1.4, 1.0 + (bid_impact_mult_pt - 1.0) * 0.15))
                    # Base CTR for product targets (e.g., 0.4%)
                    dynamic_ctr_pt = calculate_dynamic_ctr(0.004, product_relevance_mult_pt, target_type_eff_pt, ad_rank_factor_pt_ctr)
                    potential_pt_clicks = max(0, int(daily_pt_impressions * dynamic_ctr_pt))

                    # CPC, Spend, Budget Capping for Product Targets
                    daily_pt_clicks = 0; daily_pt_spend = Decimal('0.00')
                    if potential_pt_clicks > 0:
                        cpc_pt = calculate_simulated_cpc(actual_bid, category_avg_bid, product_adv.competitive_intensity)
                        potential_pt_spend_for_clicks = Decimal(potential_pt_clicks) * cpc_pt

                        remaining_daily_budget = campaign.daily_budget - campaign_daily_spent_so_far
                        if remaining_daily_budget <= Decimal('0.01'):
                            daily_pt_clicks = 0; daily_pt_spend = Decimal('0.00'); daily_pt_impressions = 0
                        elif potential_pt_spend_for_clicks > remaining_daily_budget:
                            if cpc_pt > 0: daily_pt_clicks = math.floor(remaining_daily_budget / cpc_pt)
                            else: daily_pt_clicks = potential_pt_clicks
                            daily_pt_spend = Decimal(daily_pt_clicks) * cpc_pt
                            if potential_pt_clicks > 0: daily_pt_impressions = int(daily_pt_impressions * (Decimal(daily_pt_clicks)/Decimal(potential_pt_clicks)))
                        else:
                            daily_pt_clicks = potential_pt_clicks; daily_pt_spend = potential_pt_spend_for_clicks
                        campaign_daily_spent_so_far += daily_pt_spend

                    if campaign_daily_spent_so_far >= campaign.daily_budget and daily_pt_spend == Decimal('0.00') and daily_pt_clicks == 0 and daily_pt_impressions > 0:
                        daily_pt_impressions = 0 # Zero out impressions if budget capped all spend

                    # CVR & Sales/Orders for Product Targets
                    daily_pt_orders = 0; daily_pt_sales = Decimal('0.00')
                    if daily_pt_clicks > 0:
                        prod_quality_cvr_mult_pt = get_product_quality_cvr_multiplier(product_adv)
                        # Simplified relevance for product targets (ASIN targeting generally more relevant than category)
                        pt_relevance_cvr_mult = 1.1 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 0.9
                        dynamic_pt_cvr = calculate_dynamic_cvr(product_adv.initial_cvr_baseline, prod_quality_cvr_mult_pt, pt_relevance_cvr_mult)

                        for _ in range(daily_pt_clicks):
                            if random.random() < dynamic_pt_cvr: daily_pt_orders += 1
                        daily_pt_sales = Decimal(daily_pt_orders) * product_adv.avg_selling_price

                    # Store metrics for Product Target
                    metric_data_payload_pt = {
                        'impressions': daily_pt_impressions, 'clicks': daily_pt_clicks, 'spend': daily_pt_spend,
                        'orders': daily_pt_orders, 'sales': daily_pt_sales
                    }
                    derived_metrics_pt = _calculate_derived_metrics_for_storage(metric_data_payload_pt)

                    all_metrics_to_create.append(AdPerformanceMetric(
                        metric_date=simulated_day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, product_target_id=pt.id,
                        impressions=daily_pt_impressions, clicks=daily_pt_clicks, spend=daily_pt_spend.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                        orders=daily_pt_orders, sales=daily_pt_sales.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                        placement=random.choice(PlacementChoices.choices)[0], # Random placement
                        acos=derived_metrics_pt['acos'], roas=derived_metrics_pt['roas'],
                        cpc=derived_metrics_pt['cpc'], ctr=derived_metrics_pt['ctr'], cvr=derived_metrics_pt['cvr']
                    ))
        # End of daily loop
    # End of campaign loop

    # Bulk create all collected AdPerformanceMetric objects for efficiency
    if all_metrics_to_create:
        try:
            with transaction.atomic(): # Ensure all metrics are created or none are
                AdPerformanceMetric.objects.bulk_create(all_metrics_to_create)
            print(f"Simulation for user {user_id} (week of {current_sim_date}): {len(all_metrics_to_create)} AdPerformanceMetric records created.")
        except Exception as e:
            print(f"Error bulk creating AdPerformanceMetric records for user {user_id} (week of {current_sim_date}): {e}")
            # Potentially re-raise or handle more gracefully depending on requirements
            raise
    else:
        print(f"No metrics generated for user {user_id} for the week of {current_sim_date}.")

# TODO:
# - Integrate SearchTermPerformance generation within this simulation loop.
#   - When keywords get impressions/clicks, simulate actual search terms that could have triggered them.
#   - Store these in SearchTermPerformance model.
# - Introduce more dynamic market factors (seasonality, competitor actions affecting category_avg_bid).
# - Model product lifecycle changes (review count growth, BSR changes) based on performance.
# - Refine placement simulation if specific placement bid adjustments are added.
# - Consider auto-targeting simulation logic if SP Auto campaigns are implemented.

import random
import datetime
from decimal import Decimal, ROUND_DOWN
import math
from typing import Optional # Ensure Optional is imported

from django.db import transaction
from django.conf import settings

from campaigns.models import (
    Campaign, Keyword, ProductTarget, CampaignStatusChoices,
    KeywordStatusChoices, ProductTargetStatusChoices, PlacementChoices,
    MatchTypeChoices, ProductTargetingTypeChoices
)
from products.models import Product
from products.keyword_data import get_all_product_keyword_data_for_asin
from .models import AdPerformanceMetric, SearchTermPerformance

User = settings.AUTH_USER_MODEL

# --- Helper Functions for Simulation ---

def get_category_avg_bid(competitive_intensity: Optional[str]) -> Decimal:
    if competitive_intensity == 'high': return Decimal("1.50")
    if competitive_intensity == 'low': return Decimal("0.50")
    return Decimal("1.00")

def calculate_bid_impact_multiplier(bid: Decimal, category_avg_bid: Decimal) -> float:
    if category_avg_bid == Decimal('0'): return 0.05 if bid <= Decimal('0') else 1.0
    bid_ratio = float(bid / category_avg_bid)
    if bid_ratio <= 0: return 0.05
    return bid_ratio ** 0.7

def get_product_relevance_multiplier(product: Product) -> float: # Used for Impressions & CTR
    multiplier = 1.0
    # Use current_* fields if available, else initial. (These fields will be added to Product model later)
    avg_star_rating = getattr(product, 'current_avg_star_rating', product.avg_star_rating)
    review_count = getattr(product, 'current_review_count', product.review_count)

    if avg_star_rating is not None:
        if avg_star_rating >= 4.5: multiplier += 0.15
        elif avg_star_rating >= 4.0: multiplier += 0.05
        elif avg_star_rating < 3.5: multiplier -= 0.1
    if review_count is not None:
        if review_count > 1000: multiplier += 0.15
        elif review_count > 100: multiplier += 0.05
        elif review_count < 20: multiplier -= 0.1
    if product.initial_cvr_baseline > 0.05: multiplier += 0.1
    elif product.initial_cvr_baseline < 0.01: multiplier -= 0.05
    return max(0.5, min(1.5, multiplier))

def get_match_type_efficiency(match_type: str) -> float: # For Impressions & CTR
    if match_type == MatchTypeChoices.EXACT: return 1.0
    if match_type == MatchTypeChoices.PHRASE: return 0.85
    if match_type == MatchTypeChoices.BROAD: return 0.65
    return 0.7

def get_keyword_relevance_for_ctr(keyword_text: str, product: Product) -> float: # For CTR
    product_data = get_all_product_keyword_data_for_asin(product.asin)
    if not product_data: return 0.8
    primary_keywords = [pk.strip("[]") for pk in product_data.get("primary_keywords", [])]
    if keyword_text in primary_keywords: return 1.2
    if keyword_text in product_data.get("general_search_terms", []): return 1.0
    if keyword_text.lower() in product.product_name.lower(): return 0.9
    return 0.7

def calculate_dynamic_ctr(base_ctr: float, product_relevance: float, target_specificity: float, ad_rank_factor: float) -> float:
    dynamic_ctr = base_ctr * product_relevance * target_specificity * ad_rank_factor
    return max(0.0001, min(dynamic_ctr, 0.15)) # Clamp CTR 0.01% to 15%

def calculate_simulated_cpc(student_bid: Decimal, category_avg_bid: Decimal, competitive_intensity: Optional[str]) -> Decimal:
    comp_factor = Decimal('1.0')
    if competitive_intensity == 'high': comp_factor = Decimal('1.1')
    elif competitive_intensity == 'low': comp_factor = Decimal('0.8')
    sim_competitor_bid_proxy = category_avg_bid * comp_factor * Decimal(random.uniform(0.7, 1.1))
    cpc = min(student_bid, sim_competitor_bid_proxy + Decimal(random.uniform(0.01, 0.05)))
    return max(Decimal("0.02"), cpc.quantize(Decimal("0.01")))

# --- New CVR Helper Functions ---
def get_product_quality_cvr_multiplier(product: Product) -> float:
    multiplier = 1.0
    avg_star_rating = getattr(product, 'current_avg_star_rating', product.avg_star_rating)
    review_count = getattr(product, 'current_review_count', product.review_count)

    if avg_star_rating is not None: # More sensitive impact for CVR
        if avg_star_rating >= 4.7: multiplier += 0.25
        elif avg_star_rating >= 4.2: multiplier += 0.12
        elif avg_star_rating < 3.8: multiplier -= 0.20
        elif avg_star_rating < 3.0: multiplier -= 0.40
    if review_count is not None:
        if review_count > 1500: multiplier += 0.25
        elif review_count > 200: multiplier += 0.12
        elif review_count < 50: multiplier -= 0.15
        elif review_count < 10: multiplier -= 0.30
    return max(0.2, min(1.8, multiplier)) # Clamp CVR quality multiplier

def get_search_term_relevance_cvr_multiplier(keyword_text_proxy: str, product: Product) -> float:
    # This function now uses keyword_text as a proxy for the actual search term.
    # The Search Term Report generation will use actual search terms later.
    product_data = get_all_product_keyword_data_for_asin(product.asin)
    if not product_data: return 0.9 # Default if no specific mapping

    primary_keywords = [pk.strip("[]") for pk in product_data.get("primary_keywords", [])]
    negative_examples = [nk.strip("[]\"") for nk in product_data.get("negative_keywords", [])]

    if keyword_text_proxy in primary_keywords: return 1.25 # Boost for highly relevant (primary keyword match)
    if any(neg_example in keyword_text_proxy for neg_example in negative_examples): return 0.1 # Penalize if it resembles a negative
    if keyword_text_proxy in product_data.get("general_search_terms", []): return 1.0
    if keyword_text_proxy.lower() in product.product_name.lower(): return 0.95
    return 0.8 # General fallback

def calculate_dynamic_cvr(base_cvr: float, quality_mult: float, search_term_rel_mult: float, seasonality_mult: float = 1.0) -> float:
    dynamic_cvr = base_cvr * quality_mult * search_term_rel_mult * seasonality_mult
    return max(0.00001, min(dynamic_cvr, 0.60)) # Clamp CVR (e.g., 0.001% to 60%)


def run_weekly_simulation(user_id: int, current_sim_date: datetime.date):
    print(f"Running weekly simulation for user_id {user_id} for week starting {current_sim_date}...")
    user_campaigns = Campaign.objects.filter(user_id=user_id).prefetch_related(
        'advertised_products', 'ad_groups__keywords', 'ad_groups__product_targets'
    ).all()

    if not user_campaigns: print(f"No campaigns for user_id {user_id}."); return
    all_metrics_to_create = []

    for campaign in user_campaigns:
        if not campaign.advertised_products.exists(): continue
        advertised_products_in_campaign = list(campaign.advertised_products.all())

        for i in range(7): # Daily loop
            simulated_day_date = current_sim_date + datetime.timedelta(days=i)
            campaign_daily_spent_so_far = Decimal('0.00')

            if not (campaign.start_date <= simulated_day_date and \
                    (not campaign.end_date or campaign.end_date >= simulated_day_date) and \
                    campaign.status == CampaignStatusChoices.ENABLED):
                continue

            for ad_group in campaign.ad_groups.all():
                if ad_group.status != KeywordStatusChoices.ENABLED: continue

                # --- Keywords ---
                for keyword in ad_group.keywords.all():
                    if keyword.status != KeywordStatusChoices.ENABLED: continue
                    if campaign_daily_spent_so_far >= campaign.daily_budget: continue

                    product_adv = random.choice(advertised_products_in_campaign)
                    cat_avg_bid = get_category_avg_bid(product_adv.competitive_intensity)
                    bid_mult = calculate_bid_impact_multiplier(keyword.bid, cat_avg_bid)
                    prod_rel_mult_imp_ctr = get_product_relevance_multiplier(product_adv) # For impressions & CTR
                    match_eff = get_match_type_efficiency(keyword.match_type)

                    kw_base_imp_week = 700
                    potential_imp = (kw_base_imp_week / 7.0) * bid_mult * prod_rel_mult_imp_ctr * match_eff * random.uniform(0.8, 1.2)
                    daily_impressions = max(0, int(potential_imp))

                    kw_rel_to_prod_ctr = get_keyword_relevance_for_ctr(keyword.text, product_adv) # Corrected: pass product object
                    ad_rank_mult = max(0.5, min(1.5, 1.0 + (bid_mult - 1.0) * 0.2))
                    dyn_ctr = calculate_dynamic_ctr(0.006, prod_rel_mult_imp_ctr, kw_rel_to_prod_ctr * match_eff, ad_rank_mult)
                    potential_clicks = max(0, int(daily_impressions * dyn_ctr))

                    daily_clicks = 0; daily_spend = Decimal('0.00')
                    if potential_clicks > 0:
                        cpc = calculate_simulated_cpc(keyword.bid, cat_avg_bid, product_adv.competitive_intensity)
                        potential_spend = Decimal(potential_clicks) * cpc
                        remaining_budget = campaign.daily_budget - campaign_daily_spent_so_far
                        if remaining_budget <= Decimal('0.01'): daily_clicks = 0; daily_spend = Decimal('0.00'); daily_impressions = 0
                        elif potential_spend > remaining_budget:
                            if cpc > 0: daily_clicks = math.floor(remaining_budget / cpc)
                            else: daily_clicks = potential_clicks
                            daily_spend = Decimal(daily_clicks) * cpc
                            if potential_clicks > 0: daily_impressions = int(daily_impressions * (Decimal(daily_clicks)/Decimal(potential_clicks)))
                        else:
                            daily_clicks = potential_clicks; daily_spend = potential_spend
                        campaign_daily_spent_so_far += daily_spend
                    if campaign_daily_spent_so_far >= campaign.daily_budget and daily_spend == Decimal('0.00') and daily_clicks == 0 and daily_impressions > 0 :
                         daily_impressions = 0

                    # --- CVR & Sales/Orders Logic for Keywords ---
                    daily_orders = 0; daily_sales = Decimal('0.00')
                    if daily_clicks > 0:
                        prod_quality_cvr_mult = get_product_quality_cvr_multiplier(product_adv)
                        # Using keyword.text as proxy for search term relevance for now
                        # A "negative match example" here means the keyword itself resembles a negative term for the product
                        product_keyword_data = get_all_product_keyword_data_for_asin(product_adv.asin)
                        is_neg_example = any(neg_kw.strip("[]\"") in keyword.text for neg_kw in product_keyword_data.get("negative_keywords", []))

                        search_term_rel_cvr_mult = get_search_term_relevance_cvr_multiplier(keyword.text, product_adv, is_neg_example)
                        # TODO: Add seasonality_cvr_mult later
                        dynamic_cvr = calculate_dynamic_cvr(product_adv.initial_cvr_baseline, prod_quality_cvr_mult, search_term_rel_cvr_mult)

                        for _ in range(daily_clicks):
                            if random.random() < dynamic_cvr:
                                daily_orders += 1
                        daily_sales = Decimal(daily_orders) * product_adv.avg_selling_price

                    # --- CVR & Sales/Orders Logic for Keywords ---
                    daily_orders = 0; daily_sales = Decimal('0.00')
                    if daily_clicks > 0:
                        prod_quality_cvr_mult = get_product_quality_cvr_multiplier(product_adv)
                        product_keyword_data = get_all_product_keyword_data_for_asin(product_adv.asin)
                        is_neg_example = any(neg_kw.strip("[]\"") in keyword.text for neg_kw in product_keyword_data.get("negative_keywords", []))
                        search_term_rel_cvr_mult = get_search_term_relevance_cvr_multiplier(keyword.text, product_adv, is_neg_example)
                        dynamic_cvr = calculate_dynamic_cvr(product_adv.initial_cvr_baseline, prod_quality_cvr_mult, search_term_rel_cvr_mult)
                        for _ in range(daily_clicks):
                            if random.random() < dynamic_cvr: daily_orders += 1
                        daily_sales = Decimal(daily_orders) * product_adv.avg_selling_price

                    # Pre-calculate derived metrics for AdPerformanceMetric
                    metric_data_dict = {
                        'impressions': daily_impressions, 'clicks': daily_clicks, 'spend': daily_spend,
                        'orders': daily_orders, 'sales': daily_sales
                    }
                    derived_metrics = _calculate_derived_metrics(metric_data_dict) # Use a helper similar to model's _calculate_metrics

                    all_metrics_to_create.append(AdPerformanceMetric(
                        metric_date=simulated_day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=keyword.id,
                        impressions=daily_impressions, clicks=daily_clicks, spend=daily_spend,
                        orders=daily_orders, sales=daily_sales, placement=random.choice(PlacementChoices.choices)[0],
                        acos=derived_metrics['acos'], roas=derived_metrics['roas'],
                        cpc=derived_metrics['cpc'], ctr=derived_metrics['ctr'], cvr=derived_metrics['cvr']
                    ))

                # --- Product Targets ---
                for pt in ad_group.product_targets.all():
                    if pt.status != ProductTargetStatusChoices.ENABLED: continue
                    if campaign_daily_spent_so_far >= campaign.daily_budget: continue

                    product_adv = random.choice(advertised_products_in_campaign)
                    actual_bid = pt.bid or ad_group.default_bid or Decimal("0.50")
                    cat_avg_bid = get_category_avg_bid(product_adv.competitive_intensity)
                    bid_mult = calculate_bid_impact_multiplier(actual_bid, cat_avg_bid)
                    prod_rel_mult_imp_ctr = get_product_relevance_multiplier(product_adv)

                    base_imp_pt_week = 400 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 1200
                    target_eff = 0.9 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 0.7
                    potential_imp_pt = (base_imp_pt_week / 7.0) * bid_mult * prod_rel_mult_imp_ctr * target_eff * random.uniform(0.7, 1.3)
                    daily_pt_impressions = max(0, int(potential_imp_pt))

                    ad_rank_mult_pt = max(0.6, min(1.4, 1.0 + (bid_mult - 1.0) * 0.15))
                    dyn_ctr_pt = calculate_dynamic_ctr(0.004, prod_rel_mult_imp_ctr, target_eff, ad_rank_mult_pt)
                    potential_pt_clicks = max(0, int(daily_pt_impressions * dyn_ctr_pt))

                    daily_pt_clicks = 0; daily_pt_spend = Decimal('0.00')
                    if potential_pt_clicks > 0:
                        cpc_pt = calculate_simulated_cpc(actual_bid, cat_avg_bid, product_adv.competitive_intensity)
                        potential_pt_spend = Decimal(potential_pt_clicks) * cpc_pt
                        remaining_budget = campaign.daily_budget - campaign_daily_spent_so_far
                        if remaining_budget <= Decimal('0.01'): daily_pt_clicks = 0; daily_pt_spend = Decimal('0.00'); daily_pt_impressions = 0
                        elif potential_pt_spend > remaining_budget:
                            if cpc_pt > 0: daily_pt_clicks = math.floor(remaining_budget / cpc_pt)
                            else: daily_pt_clicks = potential_pt_clicks
                            daily_pt_spend = Decimal(daily_pt_clicks) * cpc_pt
                            if potential_pt_clicks > 0: daily_pt_impressions = int(daily_pt_impressions * (Decimal(daily_pt_clicks)/Decimal(potential_pt_clicks))) # Should be daily_pt_impressions
                        else:
                            daily_pt_clicks = potential_pt_clicks; daily_pt_spend = potential_pt_spend
                        campaign_daily_spent_so_far += daily_pt_spend
                    if campaign_daily_spent_so_far >= campaign.daily_budget and daily_pt_spend == Decimal('0.00') and daily_pt_clicks == 0 and daily_pt_impressions > 0 :
                        daily_pt_impressions = 0

                    daily_pt_orders = 0; daily_pt_sales = Decimal('0.00')
                    if daily_pt_clicks > 0:
                        prod_quality_cvr_mult = get_product_quality_cvr_multiplier(product_adv)
                        pt_relevance_cvr_mult = 1.1 if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else 0.9
                        dynamic_pt_cvr = calculate_dynamic_cvr(product_adv.initial_cvr_baseline, prod_quality_cvr_mult, pt_relevance_cvr_mult)
                        for _ in range(daily_pt_clicks):
                            if random.random() < dynamic_pt_cvr: daily_pt_orders += 1
                        daily_pt_sales = Decimal(daily_pt_orders) * product_adv.avg_selling_price

                    metric_data_dict_pt = {
                        'impressions': daily_pt_impressions, 'clicks': daily_pt_clicks, 'spend': daily_pt_spend,
                        'orders': daily_pt_orders, 'sales': daily_pt_sales
                    }
                    derived_metrics_pt = _calculate_derived_metrics(metric_data_dict_pt)

                    all_metrics_to_create.append(AdPerformanceMetric(
                        metric_date=simulated_day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, product_target_id=pt.id,
                        impressions=daily_pt_impressions, clicks=daily_pt_clicks, spend=daily_pt_spend,
                        orders=daily_pt_orders, sales=daily_pt_sales, placement=random.choice(PlacementChoices.choices)[0],
                        acos=derived_metrics_pt['acos'], roas=derived_metrics_pt['roas'],
                        cpc=derived_metrics_pt['cpc'], ctr=derived_metrics_pt['ctr'], cvr=derived_metrics_pt['cvr']
                    ))

    if all_metrics_to_create:
        try:
            with transaction.atomic():
                AdPerformanceMetric.objects.bulk_create(all_metrics_to_create)
            print(f"Sim for user {user_id}: {len(all_metrics_to_create)} AdPerformanceMetric records created.")
        except Exception as e:
            print(f"Error bulk creating metrics for user {user_id}: {e}")
            raise
    else:
        print(f"No metrics generated for user {user_id} for week of {current_sim_date}.")

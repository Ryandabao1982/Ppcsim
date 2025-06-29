import random
import datetime
from decimal import Decimal

from django.db import transaction
from django.db.models import Q # For complex lookups if needed, not used in this version yet

# Import models using full path to avoid circular dependency issues if this module
# were to be imported by campaigns.models (though it's not currently)
from campaigns.models import Campaign, Keyword, ProductTarget, KeywordStatusChoices, ProductTargetStatusChoices, PlacementChoices
# Assuming Product model is in 'products.models'
from products.models import Product
from .models import AdPerformanceMetric, SearchTermPerformance
# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL # This will get users.CustomUser


def run_weekly_simulation(user_id: int, current_sim_date: datetime.date):
    """
    Runs the simulation logic for one week for a given user.
    Generates performance metrics for active campaigns, keywords, and product targets.
    """
    # In Django, views usually pass the request.user object directly.
    # If only user_id is available, fetch the user object first.
    # For this standalone logic, user_id is fine.

    print(f"Running weekly simulation for user_id {user_id} for week starting {current_sim_date}...")

    # Get all campaigns for the user, prefetch related data for efficiency
    user_campaigns = Campaign.objects.filter(user_id=user_id).prefetch_related(
        'advertised_products',
        'ad_groups__keywords',
        'ad_groups__product_targets'
    ).all()

    if not user_campaigns:
        print(f"No campaigns found for user_id {user_id}. Skipping simulation.")
        return

    metrics_to_create = []
    search_terms_to_create = []

    for campaign in user_campaigns:
        # Basic check for active campaign
        if campaign.start_date > current_sim_date or \
           (campaign.end_date and campaign.end_date < current_sim_date) or \
           campaign.status != CampaignStatusChoices.ENABLED:
            print(f"Campaign '{campaign.name}' (ID: {campaign.id}) is not active/enabled. Skipping.")
            continue

        if not campaign.advertised_products.exists():
            print(f"Campaign '{campaign.name}' (ID: {campaign.id}) has no advertised products. Skipping.")
            continue

        advertised_products_in_campaign = list(campaign.advertised_products.all())

        for ad_group in campaign.ad_groups.all():
            if ad_group.status != KeywordStatusChoices.ENABLED: # Assuming AdGroup reuses KeywordStatusChoices
                print(f"Ad Group '{ad_group.name}' (ID: {ad_group.id}) is not enabled. Skipping targets within.")
                continue

            # --- Simulate for Keywords ---
            for keyword in ad_group.keywords.all():
                if keyword.status != KeywordStatusChoices.ENABLED:
                    continue

                product_to_advertise = random.choice(advertised_products_in_campaign)

                base_impressions = random.randint(50, 500)
                bid_factor = float(keyword.bid) / 1.0
                impressions = int(base_impressions * bid_factor * (random.uniform(0.8, 1.2)))
                if impressions < 0: impressions = 0

                sim_ctr_percentage = random.uniform(0.1, 3.0)
                clicks = int(impressions * (sim_ctr_percentage / 100.0))
                if clicks < 0: clicks = 0

                spend = Decimal(clicks) * keyword.bid

                orders = 0
                if clicks > 0 and product_to_advertise.initial_cvr_baseline > 0:
                    for _ in range(clicks):
                        if random.random() < product_to_advertise.initial_cvr_baseline:
                            orders += 1

                sales = Decimal(orders) * product_to_advertise.avg_selling_price

                for i in range(7): # Create daily metrics for the week
                    day_date = current_sim_date + datetime.timedelta(days=i)
                    daily_imp = impressions // 7 + (impressions % 7 if i == 0 else 0)
                    daily_clk = clicks // 7 + (clicks % 7 if i == 0 else 0)
                    # For spend, orders, sales, it's better to divide at the end or store weekly and aggregate daily later.
                    # For now, simple division.
                    daily_sp = spend / 7
                    daily_ord = orders // 7 + (orders % 7 if i == 0 else 0)
                    daily_sls = sales / 7

                    metrics_to_create.append(AdPerformanceMetric(
                        metric_date=day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=keyword.id, product_target_id=None,
                        placement=random.choice(PlacementChoices.choices)[0],
                        impressions=daily_imp, clicks=daily_clk, spend=daily_sp,
                        orders=daily_ord, sales=daily_sls
                    ))

                # Generate dummy search terms for this keyword (weekly summary)
                if impressions > 0 : # Only generate search terms if there were impressions
                    num_search_terms = random.randint(1, min(3, clicks + 1)) # At most 3, or related to clicks
                    for _ in range(num_search_terms):
                        variation = random.choice([" extra", " online", " cheap", " review", " for sale", ""])
                        st_text = f"{keyword.text}{variation}".strip()
                        if not st_text: st_text = keyword.text # Ensure not empty

                        st_imp = impressions // num_search_terms
                        st_clk = clicks // num_search_terms
                        st_sp = spend / num_search_terms
                        st_ord = orders // num_search_terms
                        st_sls = sales / num_search_terms

                        search_terms_to_create.append(SearchTermPerformance(
                            report_date=current_sim_date, # Weekly for now
                            user_id=user_id, campaign_id=campaign.id, ad_group_id=ad_group.id,
                            search_term_text=st_text, matched_keyword_id=keyword.id,
                            impressions=st_imp, clicks=st_clk, spend=st_sp, orders=st_ord, sales=st_sls
                        ))

            # --- Simulate for Product Targets ---
            for pt in ad_group.product_targets.all():
                if pt.status != ProductTargetStatusChoices.ENABLED: # Assuming ProductTarget uses ProductTargetStatusChoices
                    continue

                product_to_advertise = random.choice(advertised_products_in_campaign)
                actual_bid_pt = pt.bid if pt.bid is not None else (ad_group.default_bid if ad_group.default_bid is not None else Decimal("0.50"))

                base_imp_pt = random.randint(30, 300) if pt.targeting_type == ProductTargetingTypeChoices.ASIN_SAME_AS else random.randint(100, 1000)
                bid_factor_pt = float(actual_bid_pt) / 1.0
                impressions = int(base_imp_pt * bid_factor_pt * random.uniform(0.7, 1.3))
                if impressions < 0: impressions = 0

                sim_ctr_pt = random.uniform(0.05, 1.5)
                clicks = int(impressions * (sim_ctr_pt / 100.0))
                if clicks < 0: clicks = 0

                spend = Decimal(clicks) * actual_bid_pt
                orders = 0
                if clicks > 0 and product_to_advertise.initial_cvr_baseline > 0:
                    for _ in range(clicks):
                        if random.random() < product_to_advertise.initial_cvr_baseline:
                            orders +=1
                sales = Decimal(orders) * product_to_advertise.avg_selling_price

                for i in range(7): # Daily metrics
                    day_date = current_sim_date + datetime.timedelta(days=i)
                    daily_imp = impressions // 7 + (impressions % 7 if i == 0 else 0)
                    daily_clk = clicks // 7 + (clicks % 7 if i == 0 else 0)
                    daily_sp = spend / 7
                    daily_ord = orders // 7 + (orders % 7 if i == 0 else 0)
                    daily_sls = sales / 7

                    metrics_to_create.append(AdPerformanceMetric(
                        metric_date=day_date, user_id=user_id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=None, product_target_id=pt.id,
                        placement=random.choice(PlacementChoices.choices)[0],
                        impressions=daily_imp, clicks=daily_clk, spend=daily_sp,
                        orders=daily_ord, sales=daily_sls
                    ))
                # Not generating SearchTermPerformance for product targets in this MVP pass

    if metrics_to_create or search_terms_to_create:
        try:
            with transaction.atomic(): # Ensure all or none are created
                AdPerformanceMetric.objects.bulk_create(metrics_to_create)
                SearchTermPerformance.objects.bulk_create(search_terms_to_create)
            print(f"Simulation for user_id {user_id} completed. {len(metrics_to_create)} AdPerformanceMetric records and {len(search_terms_to_create)} SearchTermPerformance records created.")
        except Exception as e:
            print(f"Error during bulk creation for simulation user_id {user_id}: {e}")
            # No rollback needed due to transaction.atomic()
            raise # Re-raise to be handled by the calling view if necessary
    else:
        print(f"No metrics generated for user_id {user_id} for week of {current_sim_date}.")

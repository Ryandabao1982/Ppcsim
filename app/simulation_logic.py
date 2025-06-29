import random
import datetime
from sqlalchemy.orm import Session, joinedload
from app import models, schemas, crud # Assuming crud has get_campaigns_by_user, etc.
from decimal import Decimal

def run_weekly_simulation(db: Session, user: models.User, current_sim_date: datetime.date):
    """
    Runs the simulation logic for one week for a given user.
    Generates performance metrics for active campaigns.
    """
    print(f"Running weekly simulation for user {user.username} for week of {current_sim_date}...")

    # Get all campaigns for the user, eager load necessary data
    user_campaigns = db.query(models.Campaign).options(
        joinedload(models.Campaign.advertised_products),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.keywords),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.product_targets) # Eager load product targets
    ).filter(models.Campaign.user_id == user.id).all()

    if not user_campaigns:
        print(f"No campaigns found for user {user.username}. Skipping simulation for this user.")
        return

    for campaign in user_campaigns:
        # Basic check for active campaign (e.g., based on start/end dates)
        if campaign.start_date > current_sim_date or (campaign.end_date and campaign.end_date < current_sim_date):
            print(f"Campaign '{campaign.campaign_name}' is not active. Skipping.")
            continue

        if not campaign.advertised_products:
            print(f"Campaign '{campaign.campaign_name}' has no advertised products. Skipping.")
            continue

        # For MVP, let's assume all keywords in the campaign advertise all products in the campaign.
        # A more complex setup might link products at AdGroup level or even Keyword level.
        advertised_products_in_campaign = campaign.advertised_products

        for ad_group in campaign.ad_groups:
            for keyword in ad_group.keywords:
                if keyword.status != models.KeywordStatusEnum.ENABLED:
                    print(f"Keyword '{keyword.keyword_text}' is not enabled. Skipping.")
                    continue

                # Pick a product for this keyword's performance (e.g., first one for MVP)
                # In a real scenario, this could be more complex or based on ad group settings
                if not advertised_products_in_campaign: # Should have been caught at campaign level
                    continue
                product_to_advertise = random.choice(advertised_products_in_campaign) # Or iterate all

                # --- Simulate Metrics for the Keyword ---
                # 1. Impressions: Highly simplified
                base_impressions_kw = random.randint(50, 500)
                bid_factor_kw = float(keyword.bid) / 1.0  # Simple factor, assuming $1 is a baseline bid
                impressions_kw = int(base_impressions_kw * bid_factor_kw * (random.uniform(0.8, 1.2)))
                if impressions_kw < 0: impressions_kw = 0

                # 2. Clicks: Based on a simulated CTR
                sim_ctr_percentage_kw = random.uniform(0.1, 3.0)
                clicks_kw = int(impressions_kw * (sim_ctr_percentage_kw / 100.0))
                if clicks_kw < 0: clicks_kw = 0

                # 3. Spend: Clicks * Bid
                spend_kw = Decimal(clicks_kw) * keyword.bid

                # 4. Orders (Conversions): Based on product's CVR
                orders_kw = 0
                if clicks_kw > 0 and product_to_advertise.initial_cvr_baseline > 0:
                    for _ in range(clicks_kw):
                        if random.random() < product_to_advertise.initial_cvr_baseline:
                            orders_kw += 1

                # 5. Sales: Orders * Product Price
                sales_kw = Decimal(orders_kw) * product_to_advertise.avg_selling_price

                # --- Calculate Derived Metrics for Keyword ---
                cpc_kw = spend_kw / Decimal(clicks_kw) if clicks_kw > 0 else Decimal(0)
                ctr_calc_kw = (Decimal(clicks_kw) / Decimal(impressions_kw) * 100) if impressions_kw > 0 else Decimal(0)
                cvr_calc_kw = (Decimal(orders_kw) / Decimal(clicks_kw) * 100) if clicks_kw > 0 else Decimal(0)
                acos_calc_kw = (spend_kw / sales_kw * 100) if sales_kw > 0 else Decimal(0)
                roas_calc_kw = sales_kw / spend_kw if spend_kw > 0 else Decimal(0)

                # --- Create AdPerformanceMetric record for Keyword ---
                for i in range(7): # Simulate 7 days in the week
                    day_date = current_sim_date + datetime.timedelta(days=i)
                    daily_impressions = impressions_kw // 7
                    daily_clicks = clicks_kw // 7
                    daily_spend = spend_kw / 7
                    daily_orders = orders_kw // 7
                    daily_sales = sales_kw / 7
                    if i == 6: # Ensure last day gets remainder
                        daily_impressions += impressions_kw % 7
                        daily_clicks += clicks_kw % 7

                    metric = models.AdPerformanceMetric(
                        metric_date=day_date, user_id=user.id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=keyword.id, product_target_id=None, # Explicitly None
                        placement=random.choice(list(models.PlacementEnum)),
                        impressions=daily_impressions, clicks=daily_clicks,
                        spend=daily_spend.quantize(Decimal("0.01")), orders=daily_orders,
                        sales=daily_sales.quantize(Decimal("0.01")), acos=float(acos_calc_kw),
                        roas=float(roas_calc_kw), cpc=float(cpc_kw), ctr=float(ctr_calc_kw), cvr=float(cvr_calc_kw)
                    )
                    db.add(metric)

                # --- Generate Dummy SearchTermPerformance records for Keyword ---
                num_search_terms_to_gen = random.randint(1,2)
                for _ in range(num_search_terms_to_gen):
                    variation = random.choice([" shoes", " online", " cheap", " review", " for sale", ""])
                    search_term_text = f"{keyword.keyword_text}{variation}".strip()

                    # Distribute some of the keyword's weekly performance to this search term
                    st_impressions = impressions_kw // (num_search_terms_to_gen * 2) # Example distribution
                    st_clicks = clicks_kw // (num_search_terms_to_gen * 2)
                    st_spend_val = spend_kw / Decimal(num_search_terms_to_gen * 2) # Renamed to avoid conflict with 'spend' parameter
                    st_orders = orders_kw // (num_search_terms_to_gen * 2)
                    st_sales_val = sales_kw / Decimal(num_search_terms_to_gen * 2) # Renamed

                    st_cpc = st_spend_val / Decimal(st_clicks) if st_clicks > 0 else Decimal(0)
                    st_ctr_calc = (Decimal(st_clicks) / Decimal(st_impressions) * 100) if st_impressions > 0 else Decimal(0)
                    st_cvr_calc = (Decimal(st_orders) / Decimal(st_clicks) * 100) if st_clicks > 0 else Decimal(0)
                    st_acos_calc = (st_spend_val / st_sales_val * 100) if st_sales_val > 0 else Decimal(0)
                    st_roas_calc = st_sales_val / st_spend_val if st_spend_val > 0 else Decimal(0)

                    search_term_metric = models.SearchTermPerformance(
                        report_date=current_sim_date, # Weekly report for search terms for MVP
                        search_term_text=search_term_text,
                        user_id=user.id,
                        campaign_id=campaign.id,
                        ad_group_id=ad_group.id,
                        matched_keyword_id=keyword.id,
                        impressions=st_impressions,
                        clicks=st_clicks,
                        spend=st_spend_val.quantize(Decimal("0.01")),
                        orders=st_orders,
                        sales=st_sales_val.quantize(Decimal("0.01")),
                        acos=float(st_acos_calc),
                        roas=float(st_roas_calc),
                        cpc=float(st_cpc),
                        ctr=float(st_ctr_calc),
                        cvr=float(st_cvr_calc)
                    )
                    db.add(search_term_metric)

            # Now, simulate for Product Targets in the same Ad Group
            for pt in ad_group.product_targets:
                if pt.status != models.ProductTargetStatusEnum.ENABLED:
                    print(f"Product Target '{pt.target_value}' ({pt.targeting_type.value}) is not enabled. Skipping.")
                    continue

                if not advertised_products_in_campaign: continue
                product_to_advertise = random.choice(advertised_products_in_campaign)

                # --- Simulate Metrics for the Product Target ---
                # Bid for product target: use its own bid if set, else ad group default, else a fallback (e.g., $0.50)
                actual_bid_pt = pt.bid if pt.bid is not None else (ad_group.default_bid if ad_group.default_bid is not None else Decimal("0.50"))

                # 1. Impressions (very simplified for PT)
                # Assume category targets get more impressions than ASIN targets for now
                base_impressions_pt = random.randint(100, 800) if pt.targeting_type == models.ProductTargetingTypeEnum.CATEGORY_SAME_AS else random.randint(20, 200)
                bid_factor_pt = float(actual_bid_pt) / 1.0
                impressions_pt = int(base_impressions_pt * bid_factor_pt * random.uniform(0.7, 1.3))
                if impressions_pt < 0: impressions_pt = 0

                # 2. Clicks (simulated CTR, generally lower for PT than specific keywords initially)
                sim_ctr_percentage_pt = random.uniform(0.05, 1.5)
                clicks_pt = int(impressions_pt * (sim_ctr_percentage_pt / 100.0))
                if clicks_pt < 0: clicks_pt = 0

                # 3. Spend
                spend_pt = Decimal(clicks_pt) * actual_bid_pt

                # 4. Orders
                orders_pt = 0
                if clicks_pt > 0 and product_to_advertise.initial_cvr_baseline > 0:
                    for _ in range(clicks_pt):
                        if random.random() < product_to_advertise.initial_cvr_baseline: # Simplified CVR
                            orders_pt +=1

                # 5. Sales
                sales_pt = Decimal(orders_pt) * product_to_advertise.avg_selling_price

                # --- Calculate Derived Metrics for Product Target ---
                cpc_pt = spend_pt / Decimal(clicks_pt) if clicks_pt > 0 else Decimal(0)
                ctr_calc_pt = (Decimal(clicks_pt) / Decimal(impressions_pt) * 100) if impressions_pt > 0 else Decimal(0)
                cvr_calc_pt = (Decimal(orders_pt) / Decimal(clicks_pt) * 100) if clicks_pt > 0 else Decimal(0)
                acos_calc_pt = (spend_pt / sales_pt * 100) if sales_pt > 0 else Decimal(0)
                roas_calc_pt = sales_pt / spend_pt if spend_pt > 0 else Decimal(0)

                # --- Create AdPerformanceMetric record for Product Target ---
                for i in range(7): # Simulate 7 days
                    day_date = current_sim_date + datetime.timedelta(days=i)
                    daily_impressions = impressions_pt // 7
                    daily_clicks = clicks_pt // 7
                    daily_spend = spend_pt / 7
                    daily_orders = orders_pt // 7
                    daily_sales = sales_pt / 7
                    if i == 6: # Remainder assignment
                        daily_impressions += impressions_pt % 7
                        daily_clicks += clicks_pt % 7

                    metric = models.AdPerformanceMetric(
                        metric_date=day_date, user_id=user.id, campaign_id=campaign.id,
                        ad_group_id=ad_group.id, keyword_id=None, product_target_id=pt.id, # Link to product_target
                        placement=random.choice(list(models.PlacementEnum)),
                        impressions=daily_impressions, clicks=daily_clicks,
                        spend=daily_spend.quantize(Decimal("0.01")), orders=daily_orders,
                        sales=daily_sales.quantize(Decimal("0.01")), acos=float(acos_calc_pt),
                        roas=float(roas_calc_pt), cpc=float(cpc_pt), ctr=float(ctr_calc_pt), cvr=float(cvr_calc_pt)
                    )
                    db.add(metric)

                # Note: SearchTermPerformance records are not generated for product targets in this MVP version.
                # This could be an enhancement (e.g. if a category target matches a search term).

    try:
        db.commit()
        print(f"Simulation for user {user.username} completed for week of {current_sim_date}. Metrics saved.")
    except Exception as e:
        db.rollback()
        print(f"Error during final commit for simulation: {e}")
        # Consider raising an exception here to be caught by the router
        raise

# We need a way to track the current simulation date for each user.
# For MVP, the router can just pass datetime.date.today() or a fixed date.
# A more advanced system would store `current_sim_date` per user in the User model or a dedicated table.
# For now, the simulation will generate metrics for 7 days starting from the passed `current_sim_date`.

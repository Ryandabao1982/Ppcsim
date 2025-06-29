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
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.keywords)
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
                # Base impressions could be higher for broader match types or higher bids
                base_impressions = random.randint(50, 500)
                bid_factor = float(keyword.bid) / 1.0  # Simple factor, assuming $1 is a baseline bid
                impressions = int(base_impressions * bid_factor * (random.uniform(0.8, 1.2)))
                if impressions < 0: impressions = 0

                # 2. Clicks: Based on a simulated CTR
                # For MVP, let's use a somewhat realistic CTR range (e.g. 0.1% to 3%)
                sim_ctr_percentage = random.uniform(0.1, 3.0)
                clicks = int(impressions * (sim_ctr_percentage / 100.0))
                if clicks < 0: clicks = 0

                # 3. Spend: Clicks * Bid
                spend = Decimal(clicks) * keyword.bid

                # 4. Orders (Conversions): Based on product's CVR
                # Ensure CVR is treated as a probability (e.g., 0.1 for 10%)
                orders = 0
                if clicks > 0 and product_to_advertise.initial_cvr_baseline > 0:
                    for _ in range(clicks): # Binomial distribution basically
                        if random.random() < product_to_advertise.initial_cvr_baseline:
                            orders += 1

                # 5. Sales: Orders * Product Price
                sales = Decimal(orders) * product_to_advertise.avg_selling_price

                # --- Calculate Derived Metrics ---
                cpc = spend / Decimal(clicks) if clicks > 0 else Decimal(0)
                ctr_calc = (Decimal(clicks) / Decimal(impressions) * 100) if impressions > 0 else Decimal(0)
                cvr_calc = (Decimal(orders) / Decimal(clicks) * 100) if clicks > 0 else Decimal(0)
                acos_calc = (spend / sales * 100) if sales > 0 else Decimal(0)
                roas_calc = sales / spend if spend > 0 else Decimal(0)

                # --- Create AdPerformanceMetric record ---
                # For MVP, we'll create one metric record per keyword per day for 7 days.
                # A real system might aggregate differently or have more granular "placement" data.
                for i in range(7): # Simulate 7 days in the week
                    day_date = current_sim_date + datetime.timedelta(days=i)
                    daily_impressions = impressions // 7
                    daily_clicks = clicks // 7
                    daily_spend = spend / 7
                    daily_orders = orders // 7
                    daily_sales = sales / 7

                    # Ensure last day gets remainder for integer division
                    if i == 6:
                        daily_impressions += impressions % 7
                        daily_clicks += clicks % 7
                        # Spend, orders, sales are decimal, so division is fine, but sum might be slightly off due to rounding.
                        # For simplicity, we'll assume this small diff is okay for MVP.

                    metric = models.AdPerformanceMetric(
                        metric_date=day_date,
                        user_id=user.id,
                        campaign_id=campaign.id,
                        ad_group_id=ad_group.id,
                        keyword_id=keyword.id,
                        placement=random.choice(list(models.PlacementEnum)), # Random placement for MVP
                        impressions=daily_impressions,
                        clicks=daily_clicks,
                        spend=daily_spend.quantize(Decimal("0.01")),
                        orders=daily_orders,
                        sales=daily_sales.quantize(Decimal("0.01")),
                        acos=float(acos_calc),
                        roas=float(roas_calc),
                        cpc=float(cpc),
                        ctr=float(ctr_calc),
                        cvr=float(cvr_calc)
                    )
                    db.add(metric)

                # --- Generate Dummy SearchTermPerformance records ---
                # Create 1-2 dummy search terms for this keyword this week
                num_search_terms_to_gen = random.randint(1,2)
                for _ in range(num_search_terms_to_gen):
                    variation = random.choice([" shoes", " online", " cheap", " review", " for sale", ""])
                    search_term_text = f"{keyword.keyword_text}{variation}".strip()

                    # Distribute some of the keyword's weekly performance to this search term
                    st_impressions = impressions // (num_search_terms_to_gen * 2) # Example distribution
                    st_clicks = clicks // (num_search_terms_to_gen * 2)
                    st_spend = spend / Decimal(num_search_terms_to_gen * 2)
                    st_orders = orders // (num_search_terms_to_gen * 2)
                    st_sales = sales / Decimal(num_search_terms_to_gen * 2)

                    st_cpc = st_spend / Decimal(st_clicks) if st_clicks > 0 else Decimal(0)
                    st_ctr_calc = (Decimal(st_clicks) / Decimal(st_impressions) * 100) if st_impressions > 0 else Decimal(0)
                    st_cvr_calc = (Decimal(st_orders) / Decimal(st_clicks) * 100) if st_clicks > 0 else Decimal(0)
                    st_acos_calc = (st_spend / st_sales * 100) if st_sales > 0 else Decimal(0)
                    st_roas_calc = st_sales / st_spend if st_spend > 0 else Decimal(0)

                    search_term_metric = models.SearchTermPerformance(
                        report_date=current_sim_date, # Weekly report for search terms for MVP
                        search_term_text=search_term_text,
                        user_id=user.id,
                        campaign_id=campaign.id,
                        ad_group_id=ad_group.id,
                        matched_keyword_id=keyword.id,
                        impressions=st_impressions,
                        clicks=st_clicks,
                        spend=st_spend.quantize(Decimal("0.01")),
                        orders=st_orders,
                        sales=st_sales.quantize(Decimal("0.01")),
                        acos=float(st_acos_calc),
                        roas=float(st_roas_calc),
                        cpc=float(st_cpc),
                        ctr=float(st_ctr_calc),
                        cvr=float(st_cvr_calc)
                    )
                    db.add(search_term_metric)

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

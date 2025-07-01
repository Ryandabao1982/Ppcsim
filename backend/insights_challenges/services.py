import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Avg, F, Case, When, Value, ExpressionWrapper, fields
from django.db.models.functions import Coalesce

from .models import Challenge, StudentChallengeProgress, ChallengeStatusChoices
from performance.models import AdPerformanceMetric # To fetch data for checking criteria
from products.models import Product # To get product details like COGS for criteria
from campaigns.models import Campaign # To link criteria to specific campaigns

# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL


def start_challenge_for_user(user_id: int, challenge_id: int, current_sim_date: datetime.date) -> Optional[StudentChallengeProgress]:
    """
    Starts a challenge for a user if they haven't started it or have a non-active attempt.
    Returns the StudentChallengeProgress object or None if already actively pursuing.
    """
    user = User.objects.get(id=user_id)
    challenge = Challenge.objects.filter(id=challenge_id, is_active=True).first()

    if not challenge:
        print(f"Challenge ID {challenge_id} not found or not active.")
        return None

    # Check for existing active challenge attempt
    existing_active_attempt = StudentChallengeProgress.objects.filter(
        user=user,
        challenge=challenge,
        status=ChallengeStatusChoices.ACTIVE
    ).first()

    if existing_active_attempt:
        print(f"User {user.email} already has an active attempt for challenge '{challenge.name}'.")
        return existing_active_attempt # Or return None/raise error

    # TODO: Implement logic for starting_conditions_json if it involves resetting parts of sim environment.
    # For now, we just record the start.

    progress = StudentChallengeProgress.objects.create(
        user=user,
        challenge=challenge,
        status=ChallengeStatusChoices.ACTIVE,
        start_sim_date=current_sim_date, # The week the challenge starts
        progress_details_json={"log": [{"event": "Challenge started", "date": current_sim_date.isoformat()}]}
    )
    print(f"Challenge '{challenge.name}' started for user {user.email} on sim date {current_sim_date}.")
    return progress


def check_single_challenge_progress(progress_instance: StudentChallengeProgress, current_sim_week_start_date: datetime.date):
    """
    Checks and updates the progress for a single active challenge instance.
    This is called after each simulation week.
    """
    if progress_instance.status != ChallengeStatusChoices.ACTIVE:
        return # Only process active challenges

    user = progress_instance.user
    challenge = progress_instance.challenge

    # Calculate how many full weeks have passed since the challenge started
    # current_sim_week_start_date is the beginning of the *current* week being processed by simulation
    # So, if a challenge started on this date, zero full weeks have passed yet.
    # If it started last week, one full week has passed.
    days_passed = (current_sim_week_start_date - progress_instance.start_sim_date).days
    weeks_passed = days_passed // 7
    # The metrics for the "current_sim_week_start_date" week are generated *after* this check would run for *that week*.
    # So, if current_sim_week_start_date is W2_Monday, and challenge started W1_Monday,
    # weeks_passed is 1. We analyze data from W1_Monday to W1_Sunday.

    challenge_period_start_date = progress_instance.start_sim_date
    # The end of the period to analyze is the Sunday of the last fully completed week.
    # If current_sim_week_start_date is the start of the current week,
    # then the data to analyze is up to `current_sim_week_start_date - 1 day`.
    challenge_period_end_date = current_sim_week_start_date + datetime.timedelta(days=6) # End of current sim week

    all_criteria_met = True
    current_metrics_snapshot = {}

    # --- Evaluate Success Criteria ---
    # This is a simplified V1 criteria evaluation.
    # Example criteria: {"metric": "ACoS", "scope": "product_asin", "scope_value": "B0XYZ123",
    #                    "condition": "less_than_or_equal_to", "target_value": 30.0}
    for criterion in challenge.success_criteria_json:
        metric_name = criterion.get("metric")
        scope = criterion.get("scope")
        scope_value = criterion.get("scope_value") # e.g., ASIN or Campaign Name/ID
        condition = criterion.get("condition") # "less_than_or_equal_to", "greater_than_or_equal_to"
        target_value = Decimal(str(criterion.get("target_value"))) # Ensure Decimal for comparison

        actual_value = None

        # Fetch relevant performance data for the challenge period so far
        base_query = AdPerformanceMetric.objects.filter(
            user=user,
            metric_date__range=(challenge_period_start_date, challenge_period_end_date)
        )

        if scope == "product_asin":
            # This requires linking AdPerformanceMetric to Product ASIN.
            # AdPerformanceMetric is linked to Keyword/ProductTarget, which are in AdGroups, in Campaigns, which have Products.
            # This is complex. For V1, let's assume 'scope_value' is a campaign_id for ACoS.
            # Or, if we assume the challenge is about a specific product, all campaigns for that product.
            # Simplified: Assume scope_value is campaign_id for now if metric is ACOS/Sales at campaign level.
            if metric_name in ["ACoS", "Sales", "Orders"] and scope_value: # Assuming scope_value is campaign_id
                try:
                    # Ensure the campaign belongs to the user
                    target_campaign = Campaign.objects.get(id=int(scope_value), user=user)
                    perf_data = base_query.filter(campaign=target_campaign).aggregate(
                        total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
                        total_sales=Coalesce(Sum('sales'), Decimal('0.00')),
                        total_orders=Coalesce(Sum('orders'), 0)
                    )
                    if metric_name == "ACoS":
                        actual_value = (perf_data['total_spend'] / perf_data['total_sales'] * 100) if perf_data['total_sales'] > 0 else Decimal('inf')
                    elif metric_name == "Sales":
                        actual_value = perf_data['total_sales']
                    elif metric_name == "Orders":
                         actual_value = perf_data['total_orders']
                except Campaign.DoesNotExist:
                    print(f"Challenge criterion campaign ID {scope_value} not found for user {user.email}.")
                    all_criteria_met = False; break

        current_metrics_snapshot[f"{metric_name}_{scope}_{scope_value or 'overall'}"] = float(actual_value) if actual_value is not None else None

        if actual_value is None: # Criterion could not be evaluated
            all_criteria_met = False; break

        if condition == "less_than_or_equal_to":
            if not (actual_value <= target_value): all_criteria_met = False; break
        elif condition == "greater_than_or_equal_to":
            if not (actual_value >= target_value): all_criteria_met = False; break
        # Add more conditions as needed

    # Update progress_details_json
    progress_log = progress_instance.progress_details_json.get("log", [])
    progress_log.append({
        "week": weeks_passed + 1, # Current week number being completed
        "date": current_sim_week_start_date.isoformat(),
        "snapshot": current_metrics_snapshot,
        "criteria_met_this_check": all_criteria_met # if all criteria were met with current data
    })
    progress_instance.progress_details_json["log"] = progress_log

    # --- Check for Challenge Completion or Failure ---
    if all_criteria_met:
        progress_instance.status = ChallengeStatusChoices.COMPLETED_SUCCESS
        progress_instance.outcome_determination_date = timezone.now()
        print(f"Challenge '{challenge.name}' COMPLETED SUCCESSFULLY by user {user.email}.")
    elif (weeks_passed + 1) >= challenge.simulated_weeks_duration:
        # If it's the last week (e.g. duration is 4 weeks, and weeks_passed is 3, meaning 4th week just finished)
        progress_instance.status = ChallengeStatusChoices.COMPLETED_FAILED_TIMEFRAME # Or FAILED_METRIC if not met
        if not all_criteria_met: # If criteria weren't met by the end of the last week
             progress_instance.status = ChallengeStatusChoices.COMPLETED_FAILED_METRIC
        progress_instance.outcome_determination_date = timezone.now()
        print(f"Challenge '{challenge.name}' FAILED (duration exceeded or metrics not met) for user {user.email}.")

    progress_instance.last_updated_at = timezone.now()
    progress_instance.save()


def check_all_active_challenge_progress_for_user(user_id: int, current_sim_week_start_date: datetime.date):
    """
    Iterates over all active challenges for a user and checks their progress.
    """
    active_progresses = StudentChallengeProgress.objects.filter(
        user_id=user_id,
        status=ChallengeStatusChoices.ACTIVE
    ).select_related('challenge', 'user') # Eager load for efficiency

    if not active_progresses.exists():
        print(f"No active challenges to check for user_id {user_id}.")
        return

    print(f"Checking progress for {active_progresses.count()} active challenge(s) for user_id {user_id}...")
    for progress in active_progresses:
        check_single_challenge_progress(progress, current_sim_week_start_date)
    print(f"Finished checking challenge progress for user_id {user_id}.")

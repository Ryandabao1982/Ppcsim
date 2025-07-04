import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple

from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Avg, F, Case, When, Value, ExpressionWrapper, fields, Q
from django.db.models.functions import Coalesce

from .models import Challenge, StudentChallengeProgress, ChallengeStatusChoices
from performance.models import AdPerformanceMetric
from products.models import Product
from campaigns.models import Campaign

from django.conf import settings
User = settings.AUTH_USER_MODEL


def start_challenge_for_user(user_id: int, challenge_id: int) -> Optional[StudentChallengeProgress]:
    """
    Starts a challenge for a user.
    A new StudentChallengeProgress record is created for each attempt.
    """
    try:
        user = User.objects.get(id=user_id)
        challenge = Challenge.objects.get(id=challenge_id, is_active=True)
    except User.DoesNotExist:
        print(f"User ID {user_id} not found.")
        return None
    except Challenge.DoesNotExist:
        print(f"Challenge ID {challenge_id} not found or not active.")
        return None

    # TODO: Implement logic for scenario_constraints_json if it involves resetting parts of sim environment
    # For V1, we just record the start. The student is expected to set up based on scenario_details.

    progress = StudentChallengeProgress.objects.create(
        user=user,
        challenge=challenge,
        status=ChallengeStatusChoices.ACTIVE,
        start_time=timezone.now(), # Records the actual server time when challenge is started
        progress_details={"log": [{"event": "Challenge started", "timestamp": timezone.now().isoformat()}]}
    )
    print(f"Challenge '{challenge.title}' started for user {user.email} at {progress.start_time}.")
    return progress


def _get_challenge_metric_value(
    progress_instance: StudentChallengeProgress,
    metric_config: Dict[str, Any],
    period_start_date: datetime.date,
    period_end_date: datetime.date
) -> Tuple[Optional[Decimal], str]:
    """
    Calculates the actual value of a specific metric for a challenge.
    Returns the value and a unit/description string.
    """
    user = progress_instance.user
    challenge = progress_instance.challenge
    metric_name = metric_config["name"]
    # scope = metric_config.get("scope") # e.g., "overall_challenge", "campaign_X", "product_asin_Y"
    # scope_value = metric_config.get("scope_value")

    # Determine relevant campaigns based on challenge.product_context_asins
    # This is a simplification; a more robust system might tag campaigns created/used for a challenge.
    relevant_campaign_ids = []
    if challenge.product_context_asins:
        relevant_campaign_ids = list(
            Campaign.objects.filter(
                user=user,
                advertised_products__asin__in=challenge.product_context_asins
            ).distinct().values_list('id', flat=True)
        )

    if not relevant_campaign_ids and challenge.product_context_asins: # If ASINs are specified but no campaigns found for them
        print(f"Warning: No campaigns found for user {user.id} advertising ASINs {challenge.product_context_asins} for challenge '{challenge.title}'.")
        # Depending on metric, this might mean it can't be calculated or defaults to 0/inf.

    base_query = AdPerformanceMetric.objects.filter(
        user=user,
        metric_date__range=(period_start_date, period_end_date)
    )
    if relevant_campaign_ids: # Filter by relevant campaigns if context ASINs led to some
        base_query = base_query.filter(campaign_id__in=relevant_campaign_ids)
    # If no product_context_asins, metrics are truly "overall" for the user during the period.

    if metric_name == "TotalAdAttributedSalesCount":
        aggregation = base_query.aggregate(total_orders=Coalesce(Sum('orders'), 0))
        return Decimal(aggregation['total_orders']), "orders"

    elif metric_name == "FinalOverallACoS": # ACoS over the entire challenge period for relevant campaigns
        aggregation = base_query.aggregate(
            total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
            total_sales=Coalesce(Sum('sales'), Decimal('0.00'))
        )
        if aggregation['total_sales'] > 0:
            return (aggregation['total_spend'] / aggregation['total_sales'] * 100), "% ACoS"
        return Decimal('inf') if aggregation['total_spend'] > 0 else Decimal('0.00'), "% ACoS"

    elif metric_name == "CampaignACoS": # This would need a scope_value for campaign_id
        # For V1, this specific metric might be hard if not tied to overall or product_context_asins.
        # Assuming it means overall ACoS for campaigns linked to product_context_asins.
        # This is effectively the same as FinalOverallACoS if product_context_asins are used.
        # If a specific campaign ID was stored in scenario_constraints, we could use it.
        # For now, let's make it behave like FinalOverallACoS.
        aggregation = base_query.aggregate(
            total_spend=Coalesce(Sum('spend'), Decimal('0.00')),
            total_sales=Coalesce(Sum('sales'), Decimal('0.00'))
        )
        if aggregation['total_sales'] > 0:
            return (aggregation['total_spend'] / aggregation['total_sales'] * 100), "% ACoS"
        return Decimal('inf') if aggregation['total_spend'] > 0 else Decimal('0.00'), "% ACoS"

    elif metric_name == "WeeklySalesVolumeIncreasePercent":
        # This requires a baseline. For V1, this is complex.
        # Ryan's spec: "maintaining or increasing weekly sales volume by at least 10%"
        # This implies comparison to a pre-challenge baseline or week-over-week within the challenge.
        # Simplified V1: Check if current week's sales (for relevant campaigns) are X% > Y.
        # This requires storing a baseline or more complex WoW logic.
        # For now, this metric will be hard to implement fully without baseline context.
        # Placeholder: Return 0, indicating not met or not calculable yet.
        # A real implementation would fetch sales for the current week of the challenge
        # and compare to a baseline (e.g., sales in the week prior to challenge.start_time,
        # or an average of prior weeks, or a fixed value from scenario_constraints_json).

        # Let's assume for "The ACoS Turnaround", the goal is against the sales of the *first week* of the challenge,
        # or a predefined baseline if we add it to scenario_constraints_json.
        # For "Scale to Dominate", it's also increase from baseline.

        # This needs more thought on how baselines are established or passed.
        # For this iteration, we will assume it means the total sales during the challenge period
        # must be a certain amount, which is simpler.
        # Let's redefine this in success_criteria to be "TotalSalesValue" for now.
        # Or, if it MUST be increase, we'd need to fetch data from *before* progress_instance.start_time.
        print(f"Warning: Metric '{metric_name}' requires baseline comparison, V1 implementation is simplified or placeholder.")

        # Example: If we had a baseline in constraints:
        # baseline_sales = Decimal(challenge.scenario_constraints_json.get("baseline_weekly_sales", "0"))
        # current_weekly_sales = base_query.filter(metric_date__range=(period_end_date - datetime.timedelta(days=6), period_end_date))\
        # .aggregate(current_sales=Coalesce(Sum('sales'), Decimal('0.00')))['current_sales']
        # if baseline_sales > 0:
        # return ((current_weekly_sales - baseline_sales) / baseline_sales * 100), "% increase"
        # return Decimal('inf') if current_weekly_sales > 0 else Decimal('0.00'), "% increase"
        return Decimal('0.00'), "% (placeholder)"


    print(f"Warning: Unknown metric name '{metric_name}' in challenge success criteria.")
    return None, ""


def check_single_challenge_progress(progress_instance: StudentChallengeProgress, current_sim_week_start_date: datetime.date):
    """
    Checks and updates the progress for a single active challenge instance.
    This is called after each simulation week (after its data is generated).
    """
    if progress_instance.status != ChallengeStatusChoices.ACTIVE:
        return

    user = progress_instance.user
    challenge = progress_instance.challenge

    # Determine the actual period of performance data to analyze for this check.
    # This check runs *after* the simulation for `current_sim_week_start_date`'s week has completed.
    # So, the data includes everything up to `current_sim_week_start_date + 6 days`.
    challenge_data_start_date = progress_instance.start_time.date()
    challenge_data_end_date = current_sim_week_start_date + datetime.timedelta(days=6)

    # Calculate how many full simulation weeks have passed since the challenge started.
    # If start_time was during current_sim_week_start_date's week, 0 full weeks have passed before this check.
    # The check is for the week *ending* on challenge_data_end_date.
    days_active = (challenge_data_end_date - challenge_data_start_date).days + 1 # Inclusive days
    weeks_completed = days_active // 7

    all_mandatory_criteria_met = True
    current_metrics_snapshot = {}

    time_limit_weeks = challenge.success_criteria.get("time_limit_weeks", float('inf'))

    for criterion_conf in challenge.success_criteria.get("metrics", []):
        target_value = Decimal(str(criterion_conf["target"]))
        condition_str = criterion_conf["condition"] # "ge", "le", "eq", "gt", "lt"

        actual_value, unit = _get_challenge_metric_value(progress_instance, criterion_conf, challenge_data_start_date, challenge_data_end_date)

        metric_key = f"{criterion_conf['name']}"
        current_metrics_snapshot[metric_key] = f"{actual_value:.2f} {unit}" if actual_value is not None and actual_value != Decimal('inf') else "N/A or Inf"

        if actual_value is None: # Criterion could not be evaluated
            all_mandatory_criteria_met = False
            continue # Check other criteria but overall won't pass

        met = False
        if condition_str == "ge": met = actual_value >= target_value
        elif condition_str == "le": met = actual_value <= target_value
        elif condition_str == "eq": met = actual_value == target_value
        elif condition_str == "gt": met = actual_value > target_value
        elif condition_str == "lt": met = actual_value < target_value

        if not met:
            all_mandatory_criteria_met = False
            # No break here, collect all metric snapshots for the log

    # Update progress_details JSON
    log_entry = {
        "checked_on_sim_week_starting": current_sim_week_start_date.isoformat(),
        "weeks_completed_in_challenge": weeks_completed,
        "snapshot": current_metrics_snapshot,
        "all_mandatory_criteria_met_this_check": all_mandatory_criteria_met
    }
    if "log" not in progress_instance.progress_details: progress_instance.progress_details["log"] = []
    progress_instance.progress_details["log"].append(log_entry)

    # --- Check for Challenge Completion or Failure ---
    final_status_determined = False
    if all_mandatory_criteria_met:
        progress_instance.status = ChallengeStatusChoices.COMPLETED_SUCCESS
        progress_instance.completion_time = timezone.now()
        final_status_determined = True
        print(f"Challenge '{challenge.title}' COMPLETED SUCCESSFULLY by user {user.email}.")

    if not final_status_determined and weeks_completed >= time_limit_weeks:
        # Time limit reached
        if all_mandatory_criteria_met: # Should have been caught above, but as a safeguard
            progress_instance.status = ChallengeStatusChoices.COMPLETED_SUCCESS
        else:
            progress_instance.status = ChallengeStatusChoices.COMPLETED_FAILED_METRIC # More specific than just timeframe
        progress_instance.completion_time = timezone.now()
        final_status_determined = True
        print(f"Challenge '{challenge.title}' for user {user.email} ended. Status: {progress_instance.status}.")

    if final_status_determined or progress_instance.is_dirty(): # is_dirty might not be available, save if log changed
        progress_instance.last_updated_at = timezone.now()
        progress_instance.save()


def check_all_active_challenge_progress_for_user(user_id: int, current_sim_week_start_date: datetime.date):
    """
    Iterates over all active challenges for a user and checks their progress.
    This is intended to be called after the simulation for `current_sim_week_start_date`'s week has run.
    """
    active_progresses = StudentChallengeProgress.objects.filter(
        user_id=user_id,
        status=ChallengeStatusChoices.ACTIVE
    ).select_related('challenge', 'user')

    if not active_progresses.exists():
        # print(f"No active challenges to check for user_id {user_id} for sim week starting {current_sim_week_start_date}.")
        return

    print(f"Checking progress for {active_progresses.count()} active challenge(s) for user_id {user_id} (sim week: {current_sim_week_start_date})...")
    for progress in active_progresses:
        check_single_challenge_progress(progress, current_sim_week_start_date)
    print(f"Finished checking challenge progress for user_id {user_id} (sim week: {current_sim_week_start_date}).")

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone # For default datetime values

# --- Enums ---
class InsightTypeChoices(models.TextChoices):
    HIGH_ACOS_GENERAL = 'high_acos_general', _('High ACoS (General)')
    WASTED_SPEND_STR = 'wasted_spend_str', _('Wasted Spend (Search Term Report)')
    BUDGET_CAPPED_GOOD_PERF = 'budget_capped_good_perf', _('Budget Capped (Good Performance)')
    BUDGET_CAPPED_POOR_PERF = 'budget_capped_poor_perf', _('Budget Capped (Poor Performance)')
    LOW_IMPRESSIONS_RELEVANT_KW = 'low_impressions_relevant_kw', _('Low Impressions (Relevant Keyword)')
    LOW_CVR_LISTING_ISSUE = 'low_cvr_listing_issue', _('Low CVR (Potential Listing Issue)')
    EXACT_MATCH_OPPORTUNITY = 'exact_match_opportunity', _('Exact Match Opportunity (STR)')
    SCALING_OPPORTUNITY_GENERAL = 'scaling_opportunity_general', _('Scaling Opportunity (General)')
    # Add more specific types as rules are developed

class ChallengeStatusChoices(models.TextChoices):
    NOT_STARTED = 'not_started', _('Not Started') # Not used in StudentChallengeProgress, but for Challenge itself
    ACTIVE = 'active', _('Active')
    COMPLETED_SUCCESS = 'completed_success', _('Completed Successfully')
    COMPLETED_FAILED_TIMEFRAME = 'completed_failed_timeframe', _('Failed (Timeframe Exceeded)')
    COMPLETED_FAILED_METRIC = 'completed_failed_metric', _('Failed (Metric Not Met)')
    # CANCELLED = 'cancelled', _('Cancelled') # Optional

# --- Models ---

class CoachInsightsLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_insights'
    )
    simulated_week_start_date = models.DateField(_("Simulated Week Start Date"))
    insight_type = models.CharField(
        _("Insight Type"),
        max_length=50,
        choices=InsightTypeChoices.choices
    )
    generated_message = models.TextField(_("Generated Coaching Message"))

    # Optional fields to link the insight to specific entities
    related_campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.SET_NULL, # Keep insight even if campaign is deleted
        null=True, blank=True,
        related_name='insights'
    )
    related_ad_group = models.ForeignKey(
        'campaigns.AdGroup',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='insights'
    )
    related_keyword = models.ForeignKey( # Could be a Keyword or NegativeKeyword if IDs are distinct
        'campaigns.Keyword', # Or a generic "TargetingEntity" if we had one
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='insights'
    )
    # For search term specific insights, storing the text might be better than an FK
    related_search_term_text = models.CharField(
        _("Related Search Term"),
        max_length=255,
        null=True, blank=True
    )

    is_read = models.BooleanField(_("Is Read by Student"), default=False)
    created_at = models.DateTimeField(_("Insight Generated At"), default=timezone.now)

    def __str__(self):
        return f"Insight for {self.user.email} on {self.simulated_week_start_date}: {self.get_insight_type_display()}"

    class Meta:
        verbose_name = _("Coach Insight Log")
        verbose_name_plural = _("Coach Insight Logs")
        ordering = ['-created_at']


class Challenge(models.Model):
    name = models.CharField(_("Challenge Name"), max_length=255, unique=True)
    description = models.TextField(_("Challenge Description"))
    objective_text = models.TextField(_("Challenge Objective Statement")) # e.g., "Achieve an ACoS below 30%..."

    difficulty_level = models.CharField(
        _("Difficulty Level"),
        max_length=50,
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')],
        default='Beginner'
    )
    simulated_weeks_duration = models.PositiveIntegerField(
        _("Duration in Simulated Weeks"),
        help_text=_("How many 'Advance Week' cycles the student has to complete this.")
    )

    # Store complex conditions as JSON
    # Example: {"initial_budget": 500, "focus_asins": ["B0XYZ123", "B0ABCDEF"], "pre_existing_campaigns": null}
    starting_conditions_json = models.JSONField(
        _("Starting Conditions (JSON)"),
        default=dict, blank=True,
        help_text=_("Defines the simulator state at the start of the challenge.")
    )

    # Example: [{"metric": "ACoS", "scope": "product_asin", "scope_value": "B0XYZ123", "condition": "less_than_or_equal_to", "target_value": 30.0},
    #           {"metric": "Sales", "scope": "overall", "condition": "greater_than_or_equal_to", "target_value": 1000.0}]
    success_criteria_json = models.JSONField(
        _("Success Criteria (JSON)"),
        default=list, blank=True,
        help_text=_("List of metric conditions that define successful completion.")
    )

    is_active = models.BooleanField(_("Is Challenge Active/Available"), default=True) # To enable/disable challenges
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Challenge")
        verbose_name_plural = _("Challenges")
        ordering = ['difficulty_level', 'name']


class StudentChallengeProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenge_attempts'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE, # If a challenge is deleted, progress is too
        related_name='student_attempts'
    )
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=ChallengeStatusChoices.choices,
        default=ChallengeStatusChoices.ACTIVE # Assumes created when started
    )
    start_sim_date = models.DateField(_("Challenge Start Simulation Date"), default=timezone.now) # Or set when user clicks "start"
    # end_sim_date could be calculated: start_sim_date + (challenge.duration * 7 days)
    # completed_at / failed_at might be better than end_sim_date if it's about when the outcome was determined
    outcome_determination_date = models.DateTimeField(_("Outcome Determination Date"), null=True, blank=True)

    # Store snapshots of relevant metrics or notes about progress
    # Example: {"week_1": {"acos": 45.0, "sales": 200}, "week_2": {"acos": 35.0, "sales": 300}}
    progress_details_json = models.JSONField(
        _("Progress Details (JSON)"),
        default=dict, blank=True,
        help_text=_("Stores periodic snapshots of metrics relevant to the challenge objectives.")
    )

    last_updated_at = models.DateTimeField(auto_now=True) # When this progress record was last checked/updated

    def __str__(self):
        return f"{self.user.email}'s progress on {self.challenge.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Student Challenge Progress")
        verbose_name_plural = _("Student Challenge Progresses")
        ordering = ['user', '-last_updated_at']
        unique_together = ('user', 'challenge') # If a user can only attempt a challenge once actively.
                                                # Or remove if re-attempts create new records.
                                                # For now, assume one active/completed attempt.

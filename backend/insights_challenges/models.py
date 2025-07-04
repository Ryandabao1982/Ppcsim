from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone # For default datetime values

# --- Enums ---
class InsightTypeChoices(models.TextChoices):
    # Aligned with Ryan's Strategic Input 1.1 - 1.3
    BUDGET_CAPPING_SCALING_OPPORTUNITY = 'budget_capping_scaling_opportunity', _('Budget Capping (Scaling Opportunity)')
    BUDGET_CAPPING_POOR_PERFORMANCE = 'budget_capping_poor_performance', _('Budget Capping (Poor Performance)')
    HIGH_SPEND_IRRELEVANT_SEARCH_TERMS = 'high_spend_irrelevant_search_terms', _('High Spend on Irrelevant Search Terms')
    UNDERBIDDING_RELEVANT_KEYWORDS = 'underbidding_relevant_keywords', _('Underbidding for Relevant Keywords')
    EXACT_MATCH_OPPORTUNITY_STR = 'exact_match_opportunity_str', _('Exact Match Opportunity (STR)')
    HIGH_ACOS_GENERAL_INEFFICIENCY = 'high_acos_general_inefficiency', _('High ACoS (General Inefficiency)')
    LOW_CVR_RELEVANT_TRAFFIC_LISTING_RED_FLAG = 'low_cvr_relevant_traffic_listing_red_flag', _('Low CVR Despite Relevant Traffic (Listing Red Flag)')
    # Fallback/generic if needed
    GENERAL_PERFORMANCE_TIP = 'general_performance_tip', _('General Performance Tip')


class ChallengeStatusChoices(models.TextChoices):
    NOT_STARTED = 'not_started', _('Not Started') # For a Challenge's general availability if needed, less for StudentChallengeProgress
    ACTIVE = 'active', _('Active')
    COMPLETED_SUCCESS = 'completed_success', _('Completed Successfully')
    COMPLETED_FAILED_TIMEFRAME = 'completed_failed_timeframe', _('Failed (Timeframe Exceeded)')
    COMPLETED_FAILED_METRIC = 'completed_failed_metric', _('Failed (Metric Not Met)')
    # CANCELLED = 'cancelled', _('Cancelled') # Optional, if users can abandon challenges

# --- Models ---

class CoachInsightsLog(models.Model):
    """
    Stores generated coaching insights for users based on their performance.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_insights',
        help_text=_("The student user who received this insight.")
    )
    simulated_week_start_date = models.DateField(
        _("Simulated Week Start Date"),
        help_text=_("The start date of the simulation week for which this insight was generated.")
    )
    insight_type = models.CharField(
        _("Insight Type"),
        max_length=100, # Increased length for new descriptive choices
        choices=InsightTypeChoices.choices,
        help_text=_("The specific type or category of the coaching insight.")
    )
    generated_message = models.TextField(
        _("Generated Coaching Message"),
        help_text=_("The actual advice/feedback message shown to the student.")
    )

    # Optional fields to link the insight to specific entities for context
    related_campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='insights',
        help_text=_("Campaign this insight pertains to, if applicable.")
    )
    related_ad_group = models.ForeignKey(
        'campaigns.AdGroup',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='insights',
        help_text=_("Ad group this insight pertains to, if applicable.")
    )
    related_keyword = models.ForeignKey(
        'campaigns.Keyword',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='insights',
        help_text=_("Keyword this insight pertains to, if applicable.")
    )
    related_search_term_text = models.CharField(
        _("Related Search Term"),
        max_length=255,
        null=True, blank=True,
        help_text=_("Search term this insight pertains to, if applicable (e.g., for STR insights).")
    )

    is_read = models.BooleanField(
        _("Is Read by Student"),
        default=False,
        help_text=_("Indicates if the student has viewed this insight.")
    )
    created_at = models.DateTimeField(
        _("Insight Generated At"),
        default=timezone.now,
        help_text=_("Timestamp when the insight was generated.")
    )

    def __str__(self):
        return f"Insight for {self.user.email} on {self.simulated_week_start_date}: {self.get_insight_type_display()}"

    class Meta:
        verbose_name = _("Coach Insight Log")
        verbose_name_plural = _("Coach Insight Logs")
        ordering = ['-created_at']


class Challenge(models.Model):
    """
    Defines a structured learning challenge or scenario within the simulator.
    """
    title = models.CharField(
        _("Challenge Title"),
        max_length=255,
        unique=True,
        help_text=_("The official title of the challenge.")
    )
    description = models.TextField(
        _("Challenge Description"),
        help_text=_("A brief overview of what the challenge is about.")
    )
    scenario_details = models.TextField(
        _("Scenario Details"),
        help_text=_("Narrative background or context for the challenge scenario."),
        blank=True
    )
    objective_summary = models.TextField(
        _("Objective Summary"),
        help_text=_("A concise statement of the main goal for the student.")
    )

    LEVEL_CHOICES = [
        ('Beginner', _('Beginner')),
        ('Intermediate', _('Intermediate')),
        ('Advanced', _('Advanced')),
    ]
    level = models.CharField(
        _("Difficulty Level"),
        max_length=50,
        choices=LEVEL_CHOICES,
        default='Beginner',
        help_text=_("The intended difficulty or experience level for this challenge.")
    )

    product_context_asins = models.JSONField(
        _("Product Context ASINs"),
        default=list, blank=True,
        help_text=_("A list of ASINs that are central to this challenge, if any.")
    )

    scenario_constraints_json = models.JSONField(
        _("Scenario Constraints (JSON)"),
        default=dict, blank=True,
        help_text=_("Defines specific starting conditions or limitations for the challenge, e.g., {'initial_budget': 25, 'allowed_ad_types': ['SP']}.")
    )

    success_criteria = models.JSONField(
        _("Success Criteria (JSON)"),
        default=dict, blank=True, # Changed from list to dict for structure like Ryan's input
        help_text=_("Structured criteria defining challenge completion, e.g., {'metrics': [{'name': 'ACoS', 'target': 30, 'condition': 'le'}], 'time_limit_weeks': 4}.")
    )

    is_active = models.BooleanField(
        _("Is Challenge Active/Available"),
        default=True,
        help_text=_("Toggles whether this challenge is available for students to start.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Challenge")
        verbose_name_plural = _("Challenges")
        ordering = ['level', 'title']


class StudentChallengeProgress(models.Model):
    """
    Tracks a student's progress and status for a specific challenge attempt.
    A new record can be created for re-attempts.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenge_attempts',
        help_text=_("The student undertaking the challenge.")
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='student_attempts',
        help_text=_("The challenge being attempted.")
    )
    status = models.CharField(
        _("Status"),
        max_length=50,
        choices=ChallengeStatusChoices.choices,
        default=ChallengeStatusChoices.ACTIVE, # Assumes created when a challenge is started
        help_text=_("Current status of the student's challenge attempt.")
    )
    start_time = models.DateTimeField(
        _("Challenge Start Time"),
        default=timezone.now,
        help_text=_("Timestamp when the student started this challenge attempt.")
    )
    completion_time = models.DateTimeField(
        _("Challenge Completion Time"),
        null=True, blank=True,
        help_text=_("Timestamp when the challenge attempt was concluded (success or failure).")
    )

    progress_details = models.JSONField(
        _("Progress Details (JSON)"),
        default=dict, blank=True,
        help_text=_("Stores periodic snapshots of metrics or notes relevant to the challenge objectives, e.g., weekly performance summaries.")
    )

    last_updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when this progress record was last checked or updated.")
    )

    def __str__(self):
        return f"{self.user.email}'s progress on {self.challenge.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Student Challenge Progress")
        verbose_name_plural = _("Student Challenge Progresses")
        ordering = ['user', '-start_time']
        # unique_together removed to allow re-attempts. Each attempt is a new record.

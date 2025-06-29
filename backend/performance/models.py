from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal # Import Decimal

# --- Enums (specific to performance or reused if general) ---
class PlacementChoices(models.TextChoices):
    TOP_OF_SEARCH = 'top_of_search', _('Top of Search')
    PRODUCT_PAGE = 'product_page', _('Product Page')
    REST_OF_SEARCH = 'rest_of_search', _('Rest of Search')
    UNKNOWN = 'unknown', _('Unknown')

# --- Performance Models ---
class AdPerformanceMetric(models.Model):
    metric_date = models.DateField(_("Metric Date"), db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ad_performance_metrics',
        db_index=True
    )
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='performance_metrics_for_campaign', # Changed related_name to avoid clash if campaigns app also defines it
        db_index=True
    )
    ad_group = models.ForeignKey(
        'campaigns.AdGroup',
        on_delete=models.CASCADE,
        related_name='performance_metrics_for_adgroup', # Changed related_name
        null=True, blank=True,
        db_index=True
    )
    keyword = models.ForeignKey(
        'campaigns.Keyword',
        on_delete=models.SET_NULL, # Keep metrics if keyword is deleted
        related_name='performance_metrics_for_keyword', # Changed related_name
        null=True, blank=True,
        db_index=True
    )
    product_target = models.ForeignKey(
        'campaigns.ProductTarget',
        on_delete=models.SET_NULL, # Keep metrics if product target is deleted
        related_name='performance_metrics_for_producttarget', # Changed related_name
        null=True, blank=True,
        db_index=True
    )

    placement = models.CharField(
        _("Placement"),
        max_length=50,
        choices=PlacementChoices.choices,
        default=PlacementChoices.UNKNOWN,
        null=True, blank=True
    )

    impressions = models.PositiveIntegerField(_("Impressions"), default=0)
    clicks = models.PositiveIntegerField(_("Clicks"), default=0)
    spend = models.DecimalField(_("Spend"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    orders = models.PositiveIntegerField(_("Orders"), default=0)
    sales = models.DecimalField(_("Sales"), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    acos = models.FloatField(_("ACoS (%)"), default=0.0, editable=False)
    roas = models.FloatField(_("ROAS"), default=0.0, editable=False)
    cpc = models.DecimalField(_("CPC"), max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    ctr = models.FloatField(_("CTR (%)"), default=0.0, editable=False)
    cvr = models.FloatField(_("CVR (%)"), default=0.0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.keyword_id and self.product_target_id:
            raise ValidationError(_('An AdPerformanceMetric cannot be linked to both a Keyword and a ProductTarget simultaneously.'))
        # Add more validation if needed, e.g., if ad_group is present, one target type might be required unless it's an auto-summary.

    def _calculate_metrics(self):
        if self.clicks > 0:
            self.cpc = (self.spend / Decimal(self.clicks)).quantize(Decimal('0.01'))
            self.cvr = float(Decimal(self.orders) / Decimal(self.clicks) * Decimal(100))
        else:
            self.cpc = Decimal('0.00')
            self.cvr = 0.0

        if self.impressions > 0:
            self.ctr = float(Decimal(self.clicks) / Decimal(self.impressions) * Decimal(100))
        else:
            self.ctr = 0.0

        if self.sales > 0: # Ensure sales > 0 for ACOS
            self.acos = float((self.spend / self.sales) * Decimal(100))
        else:
            self.acos = 0.0

        if self.spend > 0: # Ensure spend > 0 for ROAS
            self.roas = float(self.sales / self.spend)
        else:
            self.roas = 0.0

    def save(self, *args, **kwargs):
        self._calculate_metrics()
        # self.full_clean() # full_clean() might not be ideal in all save scenarios (e.g. bulk)
        super().save(*args, **kwargs)

    def __str__(self):
        target_info = f"K:{self.keyword_id}" if self.keyword_id else (f"PT:{self.product_target_id}" if self.product_target_id else "AdGroupLvl")
        return f"Metrics for Campaign {self.campaign_id or '-'}/{self.ad_group_id or '-'}/{target_info} on {self.metric_date}"

    class Meta:
        verbose_name = _("Ad Performance Metric")
        verbose_name_plural = _("Ad Performance Metrics")
        ordering = ['-metric_date', 'campaign', 'ad_group']
        constraints = [
            models.CheckConstraint(
                check=~models.Q(keyword__isnull=False, product_target__isnull=False),
                name='chk_metric_single_target_type'
            )
        ]


class SearchTermPerformance(models.Model):
    report_date = models.DateField(_("Report Date"), db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_term_performance_data', # Changed related_name
        db_index=True
    )
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='search_term_performance_data', # Changed related_name
        db_index=True
    )
    ad_group = models.ForeignKey(
        'campaigns.AdGroup',
        on_delete=models.CASCADE,
        related_name='search_term_performance_data', # Changed related_name
        db_index=True
    )
    search_term_text = models.CharField(_("Search Term"), max_length=255, db_index=True)

    matched_keyword = models.ForeignKey(
        'campaigns.Keyword',
        on_delete=models.SET_NULL,
        related_name='matched_search_term_data', # Changed related_name
        null=True, blank=True
    )
    # For MVP, not linking SearchTermPerformance directly to ProductTarget matches,
    # as it's more complex to determine which search term matched which broad category/ASIN target.
    # This can be an enhancement.

    impressions = models.PositiveIntegerField(_("Impressions"), default=0)
    clicks = models.PositiveIntegerField(_("Clicks"), default=0)
    spend = models.DecimalField(_("Spend"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    orders = models.PositiveIntegerField(_("Orders"), default=0)
    sales = models.DecimalField(_("Sales"), max_digits=12, decimal_places=2, default=Decimal('0.00'))

    acos = models.FloatField(_("ACoS (%)"), default=0.0, editable=False)
    roas = models.FloatField(_("ROAS"), default=0.0, editable=False)
    cpc = models.DecimalField(_("CPC"), max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    ctr = models.FloatField(_("CTR (%)"), default=0.0, editable=False)
    cvr = models.FloatField(_("CVR (%)"), default=0.0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def _calculate_metrics(self): # Same calculation logic as AdPerformanceMetric
        if self.clicks > 0:
            self.cpc = (self.spend / Decimal(self.clicks)).quantize(Decimal('0.01'))
            self.cvr = float(Decimal(self.orders) / Decimal(self.clicks) * Decimal(100))
        else:
            self.cpc = Decimal('0.00')
            self.cvr = 0.0

        if self.impressions > 0:
            self.ctr = float(Decimal(self.clicks) / Decimal(self.impressions) * Decimal(100))
        else:
            self.ctr = 0.0

        if self.sales > 0:
            self.acos = float((self.spend / self.sales) * Decimal(100))
        else:
            self.acos = 0.0

        if self.spend > 0:
            self.roas = float(self.sales / self.spend)
        else:
            self.roas = 0.0

    def save(self, *args, **kwargs):
        self._calculate_metrics()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Search Term: '{self.search_term_text}' on {self.report_date} for Campaign ID {self.campaign_id}"

    class Meta:
        verbose_name = _("Search Term Performance")
        verbose_name_plural = _("Search Term Performances")
        ordering = ['-report_date', 'search_term_text']
        # unique_together = ('report_date', 'campaign', 'ad_group', 'search_term_text', 'matched_keyword') # Removed matched_product_target for now
        # A search term might appear multiple times if it matches different keywords or has different daily records.
        # For simplicity, allow multiple entries and aggregate in reports.
        # Or, make (report_date, user, campaign, ad_group, search_term_text, matched_keyword) unique.
        # For MVP, keeping it simple without strict unique_together on all these fields.

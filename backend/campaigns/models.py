from django.db import models
from django.conf import settings # To link to AUTH_USER_MODEL
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# --- Enums ---
class AdTypeChoices(models.TextChoices):
    SPONSORED_PRODUCTS = 'sponsored_products', _('Sponsored Products')
    # SPONSORED_BRANDS = 'sponsored_brands', _('Sponsored Brands') # Future
    # SPONSORED_DISPLAY = 'sponsored_display', _('Sponsored Display') # Future

class CampaignStatusChoices(models.TextChoices):
    ENABLED = 'enabled', _('Enabled')
    PAUSED = 'paused', _('Paused')
    ARCHIVED = 'archived', _('Archived')
    # PENDING_START for scheduled campaigns could be a derived status or actual

class BiddingStrategyChoices(models.TextChoices):
    DYNAMIC_DOWN_ONLY = 'dynamic_bids_down_only', _('Dynamic bids - down only')
    DYNAMIC_UP_DOWN = 'dynamic_bids_up_and_down', _('Dynamic bids - up and down')
    FIXED_BIDS = 'fixed_bids', _('Fixed bids')

class TargetingTypeChoices(models.TextChoices): # For Campaign-level targeting type
    MANUAL = 'manual', _('Manual')
    AUTO = 'auto', _('Automatic')

class MatchTypeChoices(models.TextChoices): # For Keywords
    BROAD = 'broad', _('Broad')
    PHRASE = 'phrase', _('Phrase')
    EXACT = 'exact', _('Exact')

class KeywordStatusChoices(models.TextChoices): # Reusing for Keywords, Negatives
    ENABLED = 'enabled', _('Enabled')
    PAUSED = 'paused', _('Paused') # Not typical for negatives, but can be supported
    ARCHIVED = 'archived', _('Archived')

class ProductTargetingTypeChoices(models.TextChoices): # For Product Targets
    ASIN_SAME_AS = 'asin_same_as', _('ASIN')
    CATEGORY_SAME_AS = 'category_same_as', _('Category')

class ProductTargetStatusEnum(models.TextChoices): # Definition was missing or misplaced
    ENABLED = 'enabled', _('Enabled')
    PAUSED = 'paused', _('Paused')
    ARCHIVED = 'archived', _('Archived')

class NegativeMatchTypeChoices(models.TextChoices): # For Negative Keywords
    NEGATIVE_EXACT = 'negative_exact', _('Negative Exact')
    NEGATIVE_PHRASE = 'negative_phrase', _('Negative Phrase')

# --- Association Table for Campaign-Product M2M ---
# This table should be defined once. If it's used by `products` app too,
# it might be better in a shared location or defined in one app and used by other.
# For now, defining it here for clarity within the campaigns context.
# If products.models also defines/needs it, ensure consistency.
# Let's assume it's defined here for now.
class CampaignProductLink(models.Model):
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE) # Assuming products app and Product model

    class Meta:
        unique_together = ('campaign', 'product')
        verbose_name = _("Campaign-Product Link")
        verbose_name_plural = _("Campaign-Product Links")


# --- Core Models ---
class Campaign(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    name = models.CharField(_("Campaign Name"), max_length=255, db_index=True)
    ad_type = models.CharField(
        _("Ad Type"),
        max_length=50,
        choices=AdTypeChoices.choices,
        default=AdTypeChoices.SPONSORED_PRODUCTS
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=CampaignStatusChoices.choices,
        default=CampaignStatusChoices.ENABLED
    )
    daily_budget = models.DecimalField(_("Daily Budget"), max_digits=10, decimal_places=2)
    start_date = models.DateField(_("Start Date"), default=models.functions.Now) # Or timezone.now for datetime
    end_date = models.DateField(_("End Date"), null=True, blank=True)
    bidding_strategy = models.CharField(
        _("Bidding Strategy"),
        max_length=50,
        choices=BiddingStrategyChoices.choices,
        default=BiddingStrategyChoices.DYNAMIC_DOWN_ONLY
    )
    targeting_type = models.CharField( # Specific to SP campaigns usually
        _("Targeting Type"),
        max_length=20,
        choices=TargetingTypeChoices.choices,
        null=True, blank=True # Auto or Manual
    )

    # M2M relationship for advertised products
    advertised_products = models.ManyToManyField(
        'products.Product', # Assuming 'products.Product' is the model path
        through=CampaignProductLink,
        related_name='campaigns_featuring_product', # How products will refer back to campaigns
        blank=True # A campaign might be created without products initially
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering = ['-created_at']


class AdGroup(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='ad_groups')
    name = models.CharField(_("Ad Group Name"), max_length=255, db_index=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=KeywordStatusChoices.choices, # Reusing status enum
        default=KeywordStatusChoices.ENABLED
    )
    default_bid = models.DecimalField(
        _("Default Bid"),
        max_digits=10,
        decimal_places=2,
        null=True, blank=True,
        help_text=_("Default bid for keywords/targets in this ad group if their specific bid is not set.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Campaign: {self.campaign.name})"

    class Meta:
        verbose_name = _("Ad Group")
        verbose_name_plural = _("Ad Groups")
        ordering = ['name']


class Keyword(models.Model):
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, related_name='keywords')
    text = models.CharField(_("Keyword Text"), max_length=255, db_index=True)
    match_type = models.CharField(
        _("Match Type"),
        max_length=20,
        choices=MatchTypeChoices.choices
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=KeywordStatusChoices.choices,
        default=KeywordStatusChoices.ENABLED
    )
    bid = models.DecimalField(_("Bid"), max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} ({self.match_type})"

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")
        unique_together = ('ad_group', 'text', 'match_type') # Ensure keyword is unique within an ad group by text & match type


class ProductTarget(models.Model):
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, related_name='product_targets')
    targeting_type = models.CharField(
        _("Targeting Type"),
        max_length=50,
        choices=ProductTargetingTypeChoices.choices
    )
    target_value = models.CharField( # ASIN or Category ID/Name
        _("Target Value"),
        max_length=255,
        db_index=True
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=ProductTargetStatusEnum.choices, # Use its own enum
        default=ProductTargetStatusEnum.ENABLED
    )
    bid = models.DecimalField(
        _("Bid"),
        max_digits=10,
        decimal_places=2,
        null=True, blank=True,
        help_text=_("Optional: Overrides ad group default bid.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.targeting_type}: {self.target_value}"

    class Meta:
        verbose_name = _("Product Target")
        verbose_name_plural = _("Product Targets")
        unique_together = ('ad_group', 'targeting_type', 'target_value')


class NegativeKeyword(models.Model):
    keyword_text = models.CharField(_("Negative Keyword Text"), max_length=255, db_index=True)
    match_type = models.CharField(
        _("Match Type"),
        max_length=50,
        choices=NegativeMatchTypeChoices.choices
    )
    status = models.CharField( # Reusing KeywordStatus for Enabled/Archived
        _("Status"),
        max_length=20,
        choices=KeywordStatusChoices.choices,
        default=KeywordStatusChoices.ENABLED
    )

    # Scope: Links to either Campaign or AdGroup
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='negative_keywords',
        null=True, blank=True
    )
    ad_group = models.ForeignKey(
        AdGroup,
        on_delete=models.CASCADE,
        related_name='negative_keywords',
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if not (self.campaign_id or self.ad_group_id):
            raise ValidationError(_('NegativeKeyword must be associated with a Campaign or an AdGroup.'))
        if self.campaign_id and self.ad_group_id:
            raise ValidationError(_('NegativeKeyword cannot be associated with both a Campaign and an AdGroup.'))

    def save(self, *args, **kwargs):
        self.clean() # Perform validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        scope = f"Campaign: {self.campaign_id}" if self.campaign_id else f"AdGroup: {self.ad_group_id}"
        return f"{self.keyword_text} ({self.match_type}) - Scope: {scope}"

    class Meta:
        verbose_name = _("Negative Keyword")
        verbose_name_plural = _("Negative Keywords")
        # Add DB-level check constraint if possible and desired for stricter integrity,
        # though clean() method handles it at Python level.
        # For SQLite, complex check constraints involving NULL checks can be tricky.
        # models.CheckConstraint(
        #     check=(
        #         (models.Q(campaign__isnull=False) & models.Q(ad_group__isnull=True)) |
        #         (models.Q(campaign__isnull=True) & models.Q(ad_group__isnull=False))
        #     ),
        #     name='chk_negative_keyword_scope'
        # ) # This Q object approach is for querysets, not directly for CheckConstraint `check` param.
        # A raw SQL string is typically used for `check` in CheckConstraint.


class NegativeProductTarget(models.Model):
    target_asin = models.CharField(_("Target ASIN"), max_length=20, db_index=True)
    status = models.CharField( # Reusing KeywordStatus for Enabled/Archived
        _("Status"),
        max_length=20,
        choices=KeywordStatusChoices.choices,
        default=KeywordStatusChoices.ENABLED
    )

    # Scope
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='negative_product_targets',
        null=True, blank=True
    )
    ad_group = models.ForeignKey(
        AdGroup,
        on_delete=models.CASCADE,
        related_name='negative_product_targets',
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if not (self.campaign_id or self.ad_group_id):
            raise ValidationError(_('NegativeProductTarget must be associated with a Campaign or an AdGroup.'))
        if self.campaign_id and self.ad_group_id:
            raise ValidationError(_('NegativeProductTarget cannot be associated with both a Campaign and an AdGroup.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        scope = f"Campaign: {self.campaign_id}" if self.campaign_id else f"AdGroup: {self.ad_group_id}"
        return f"Negative Target ASIN: {self.target_asin} - Scope: {scope}"

    class Meta:
        verbose_name = _("Negative Product Target")
        verbose_name_plural = _("Negative Product Targets")
        # Similar CheckConstraint could be added here at DB level if desired.

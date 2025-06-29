from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    asin = models.CharField(_("ASIN"), max_length=20, unique=True, db_index=True)
    product_name = models.CharField(_("Product Name"), max_length=255)
    category = models.CharField(_("Category"), max_length=100, blank=True, null=True, db_index=True)
    # For simplicity, sub_category can be part of category string or a separate field if needed later

    avg_selling_price = models.DecimalField(
        _("Average Selling Price"),
        max_digits=10,
        decimal_places=2
    )
    cost_of_goods_sold = models.DecimalField(
        _("Cost of Goods Sold"),
        max_digits=10,
        decimal_places=2
    )
    initial_cvr_baseline = models.FloatField( # Conversion Rate as a float (e.g., 0.05 for 5%)
        _("Initial CVR Baseline"),
        help_text=_("Base conversion rate, e.g., 0.05 for 5%")
    )

    # Additional fields from design document
    initial_bestseller_rank = models.PositiveIntegerField(
        _("Initial Bestseller Rank"),
        null=True, blank=True
    )
    review_count = models.PositiveIntegerField(_("Review Count"), default=0)
    avg_star_rating = models.FloatField( # e.g., 4.5
        _("Average Star Rating"),
        null=True, blank=True,
        help_text=_("Average customer review star rating, e.g., 4.5")
    )

    # For seasonality and competition, using CharFields with choices or simple text fields for now.
    # More complex implementations could use separate models or more structured data.
    SEASONALITY_CHOICES = [
        ('evergreen', _('Evergreen Staple')),
        ('seasonal_toy', _('Seasonal Toy')),
        ('seasonal_clothing', _('Seasonal Clothing')),
        ('other', _('Other')),
    ]
    seasonality_profile = models.CharField(
        _("Seasonality Profile"),
        max_length=50,
        choices=SEASONALITY_CHOICES,
        default='evergreen',
        blank=True, null=True
    )

    COMPETITION_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    ]
    competitive_intensity = models.CharField(
        _("Competitive Intensity"),
        max_length=50,
        choices=COMPETITION_CHOICES,
        default='medium',
        blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} (ASIN: {self.asin})"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['product_name']

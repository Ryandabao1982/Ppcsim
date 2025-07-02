from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    Customizes how products are displayed and managed in the Django admin interface.
    """
    list_display = (
        'asin',
        'product_name',
        'category',
        'avg_selling_price',
        # 'cost_of_goods_sold',
        'initial_cvr_baseline',
        'review_count',
        'avg_star_rating',
        'seasonality_profile',
        'competitive_intensity'
    )
    list_filter = ('category', 'seasonality_profile', 'competitive_intensity', 'avg_star_rating')
    search_fields = ('asin', 'product_name', 'category')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('asin', 'product_name', 'category')
        }),
        ('Pricing & Cost', {
            'fields': ('avg_selling_price', 'cost_of_goods_sold')
        }),
        ('Performance Baselines', {
            'fields': ('initial_cvr_baseline', 'initial_bestseller_rank', 'review_count', 'avg_star_rating')
        }),
        ('Market Factors', {
            'fields': ('seasonality_profile', 'competitive_intensity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Collapsible section
        }),
    )

    def get_queryset(self, request):
        # Optimize query for list display if needed (e.g., select_related for FKs, though Product has none direct)
        return super().get_queryset(request)

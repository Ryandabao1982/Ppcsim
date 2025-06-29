from django.contrib import admin
from .models import AdPerformanceMetric, SearchTermPerformance

@admin.register(AdPerformanceMetric)
class AdPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = (
        'metric_date',
        'campaign_link',
        'ad_group_link',
        'keyword_link',
        'product_target_link',
        'impressions',
        'clicks',
        'spend',
        'orders',
        'sales',
        'acos',
        'roas'
    )
    list_filter = ('metric_date', 'placement', 'campaign__name', 'ad_group__name')
    search_fields = (
        'campaign__name',
        'ad_group__name',
        'keyword__text',
        'product_target__target_value'
    )
    date_hierarchy = 'metric_date'
    readonly_fields = ('created_at', 'acos', 'roas', 'cpc', 'ctr', 'cvr') # Calculated fields are not directly editable

    fieldsets = (
        (None, {'fields': ('metric_date', 'user', 'placement')}),
        ('Hierarchy', {'fields': ('campaign', 'ad_group')}),
        ('Targeting', {'fields': ('keyword', 'product_target')}),
        ('Core Metrics', {'fields': ('impressions', 'clicks', 'spend', 'orders', 'sales')}),
        ('Calculated Metrics', {'fields': ('acos', 'roas', 'cpc', 'ctr', 'cvr'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def campaign_link(self, obj):
        return obj.campaign.name if obj.campaign else None
    campaign_link.short_description = 'Campaign'
    campaign_link.admin_order_field = 'campaign__name'

    def ad_group_link(self, obj):
        return obj.ad_group.name if obj.ad_group else None
    ad_group_link.short_description = 'Ad Group'
    ad_group_link.admin_order_field = 'ad_group__name'

    def keyword_link(self, obj):
        return obj.keyword.text if obj.keyword else None
    keyword_link.short_description = 'Keyword'
    keyword_link.admin_order_field = 'keyword__text'

    def product_target_link(self, obj):
        return f"{obj.product_target.targeting_type}: {obj.product_target.target_value}" if obj.product_target else None
    product_target_link.short_description = 'Product Target'
    # product_target_link.admin_order_field = 'product_target__target_value' # Needs careful thought for complex objects


@admin.register(SearchTermPerformance)
class SearchTermPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'report_date',
        'search_term_text',
        'campaign_link',
        'ad_group_link',
        'matched_keyword_link',
        'impressions',
        'clicks',
        'spend',
        'orders',
        'sales'
    )
    list_filter = ('report_date', 'campaign__name', 'ad_group__name')
    search_fields = ('search_term_text', 'campaign__name', 'ad_group__name', 'matched_keyword__text')
    date_hierarchy = 'report_date'
    readonly_fields = ('created_at', 'acos', 'roas', 'cpc', 'ctr', 'cvr')

    fieldsets = (
        (None, {'fields': ('report_date', 'user', 'search_term_text')}),
        ('Hierarchy', {'fields': ('campaign', 'ad_group', 'matched_keyword', 'matched_product_target')}), # matched_product_target can be added if used
        ('Core Metrics', {'fields': ('impressions', 'clicks', 'spend', 'orders', 'sales')}),
        ('Calculated Metrics', {'fields': ('acos', 'roas', 'cpc', 'ctr', 'cvr'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def campaign_link(self, obj):
        return obj.campaign.name if obj.campaign else None
    campaign_link.short_description = 'Campaign'
    campaign_link.admin_order_field = 'campaign__name'

    def ad_group_link(self, obj):
        return obj.ad_group.name if obj.ad_group else None
    ad_group_link.short_description = 'Ad Group'
    ad_group_link.admin_order_field = 'ad_group__name'

    def matched_keyword_link(self, obj):
        return obj.matched_keyword.text if obj.matched_keyword else None
    matched_keyword_link.short_description = 'Matched Keyword'
    matched_keyword_link.admin_order_field = 'matched_keyword__text'

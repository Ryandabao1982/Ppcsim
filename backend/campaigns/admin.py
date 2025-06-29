from django.contrib import admin
from .models import (
    Campaign, CampaignProductLink, AdGroup, Keyword, ProductTarget,
    NegativeKeyword, NegativeProductTarget
)

class CampaignProductLinkInline(admin.TabularInline):
    model = CampaignProductLink
    extra = 1 # Number of empty forms to display

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'ad_type', 'status', 'daily_budget', 'start_date', 'end_date')
    list_filter = ('ad_type', 'status', 'bidding_strategy', 'targeting_type', 'user')
    search_fields = ('name', 'user__email') # Search by user's email
    inlines = [CampaignProductLinkInline]
    date_hierarchy = 'start_date'

@admin.register(AdGroup)
class AdGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'status', 'default_bid')
    list_filter = ('status', 'campaign__name') # Filter by campaign name
    search_fields = ('name', 'campaign__name')

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('text', 'ad_group', 'match_type', 'status', 'bid')
    list_filter = ('match_type', 'status', 'ad_group__campaign__name', 'ad_group__name')
    search_fields = ('text', 'ad_group__name', 'ad_group__campaign__name')
    list_editable = ('bid', 'status') # Allow direct editing in the list view

@admin.register(ProductTarget)
class ProductTargetAdmin(admin.ModelAdmin):
    list_display = ('target_value', 'targeting_type', 'ad_group', 'status', 'bid')
    list_filter = ('targeting_type', 'status', 'ad_group__campaign__name', 'ad_group__name')
    search_fields = ('target_value', 'ad_group__name', 'ad_group__campaign__name')
    list_editable = ('bid', 'status')

@admin.register(NegativeKeyword)
class NegativeKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword_text', 'match_type', 'status', 'campaign_display', 'ad_group_display')
    list_filter = ('match_type', 'status', 'campaign__name', 'ad_group__name')
    search_fields = ('keyword_text', 'campaign__name', 'ad_group__name')

    def campaign_display(self, obj):
        return obj.campaign.name if obj.campaign else None
    campaign_display.short_description = 'Campaign'

    def ad_group_display(self, obj):
        return obj.ad_group.name if obj.ad_group else None
    ad_group_display.short_description = 'Ad Group'

    # Ensure either campaign or ad_group is editable, but not both, or handle this via custom form.
    # For simplicity, admin might show both, but model's clean() method enforces one.

@admin.register(NegativeProductTarget)
class NegativeProductTargetAdmin(admin.ModelAdmin):
    list_display = ('target_asin', 'status', 'campaign_display', 'ad_group_display')
    list_filter = ('status', 'campaign__name', 'ad_group__name')
    search_fields = ('target_asin', 'campaign__name', 'ad_group__name')

    def campaign_display(self, obj):
        return obj.campaign.name if obj.campaign else None
    campaign_display.short_description = 'Campaign'

    def ad_group_display(self, obj):
        return obj.ad_group.name if obj.ad_group else None
    ad_group_display.short_description = 'Ad Group'

# Note: CampaignProductLink is managed via CampaignAdmin's inline.
# If direct management is needed, it can be registered too:
# @admin.register(CampaignProductLink)
# class CampaignProductLinkAdmin(admin.ModelAdmin):
#     list_display = ('campaign', 'product')

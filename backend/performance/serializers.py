from rest_framework import serializers
from campaigns.models import Campaign, AdGroup, Keyword, ProductTarget # For type hints or direct use if needed
from campaigns.serializers import CampaignSerializer as FullCampaignSerializer # For campaign details if needed
from decimal import Decimal

# Note: These serializers are for aggregated data, not directly ModelSerializers
# unless we create a specific (non-model) class to represent aggregated rows.
# For simplicity, they will define the fields expected in the API response.

class AggregatedPerformanceMetricsSerializer(serializers.Serializer):
    # Common metrics
    impressions = serializers.IntegerField(default=0)
    clicks = serializers.IntegerField(default=0)
    spend = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    orders = serializers.IntegerField(default=0)
    sales = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    acos = serializers.FloatField(default=0.0)
    roas = serializers.FloatField(default=0.0)
    cpc = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ctr = serializers.FloatField(default=0.0)
    cvr = serializers.FloatField(default=0.0)

    # Date fields for grouping if needed (though often the API defines the range)
    # start_date = serializers.DateField(required=False)
    # end_date = serializers.DateField(required=False)

class CampaignPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    # Campaign specific fields (from Campaign model, denormalized)
    campaign_id = serializers.IntegerField() # For linking or direct reference
    campaign_name = serializers.CharField(max_length=255)
    ad_type = serializers.CharField(max_length=50) # Using choices from model AdTypeChoices
    status = serializers.CharField(max_length=20)  # Using choices from CampaignStatusChoices
    daily_budget = serializers.DecimalField(max_digits=10, decimal_places=2)
    start_date = serializers.DateField()
    end_date = serializers.DateField(allow_null=True)
    # bidding_strategy = serializers.CharField(max_length=50) # Not in specified report columns

    # Note: The aggregation function in reports.py will construct dictionaries
    # matching this structure.

class AdGroupPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    ad_group_id = serializers.IntegerField()
    ad_group_name = serializers.CharField(max_length=255)
    campaign_id = serializers.IntegerField() # Parent campaign
    campaign_name = serializers.CharField(max_length=255) # Parent campaign name
    status = serializers.CharField(max_length=20)
    default_bid = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)


class KeywordPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    keyword_id = serializers.IntegerField()
    keyword_text = serializers.CharField(max_length=255)
    match_type = serializers.CharField(max_length=20) # From MatchTypeChoices
    bid = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=20) # From KeywordStatusChoices

    # Context
    ad_group_id = serializers.IntegerField()
    ad_group_name = serializers.CharField(max_length=255)
    campaign_id = serializers.IntegerField()
    campaign_name = serializers.CharField(max_length=255)


class ProductTargetPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    product_target_id = serializers.IntegerField()
    targeting_type = serializers.CharField(max_length=50) # From ProductTargetingTypeChoices
    target_value = serializers.CharField(max_length=255)
    bid = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    status = serializers.CharField(max_length=20) # From ProductTargetStatusChoices

    # Context
    ad_group_id = serializers.IntegerField()
    ad_group_name = serializers.CharField(max_length=255)
    campaign_id = serializers.IntegerField()
    campaign_name = serializers.CharField(max_length=255)


# Serializer for Search Term Report items (if needed here, though already in app.schemas for FastAPI)
# For Django DRF, if we build a new STR endpoint, it would look like:
# class SearchTermReportItemDRFSerializer(AggregatedPerformanceMetricsSerializer):
#     search_term_text = serializers.CharField()
#     keyword_triggered_text = serializers.CharField(allow_null=True, required=False) # Denormalized
#     keyword_triggered_match_type = serializers.CharField(allow_null=True, required=False) # Denormalized
#     campaign_id = serializers.IntegerField()
#     campaign_name = serializers.CharField()
#     ad_group_id = serializers.IntegerField()
#     ad_group_name = serializers.CharField()
    # ... and other fields as per your spec for STR:
    # Action Column: This would be a frontend concern, not part of serializer data usually.
    # The API would provide IDs (keyword_id, search_term_id etc.) for frontend to build actions.
    # report_date = serializers.DateField() # If STR items are daily/specific date
    # For now, focusing on Campaign, Keyword, ProductTarget performance.
    # The existing FastAPI STR API is based on the SearchTermPerformance model directly.
    # If we need a new Django DRF based STR API, this would be the place for its serializer.

"""
Serializers for the Performance application.

These serializers are primarily used to structure the output of aggregated performance data
for API responses. They are not ModelSerializers in the typical Django REST Framework sense,
as they represent data that is dynamically calculated and aggregated from one or more models
(primarily AdPerformanceMetric and SearchTermPerformance).

Each serializer defines the fields expected in the API response for a specific type of
performance report (e.g., campaign performance, keyword performance).
"""
from rest_framework import serializers
# from campaigns.models import Campaign, AdGroup, Keyword, ProductTarget # Not strictly needed here unless for choices or complex relations
from decimal import Decimal

# Note: These serializers are for aggregated data, not directly ModelSerializers.
# They define the structure of dictionaries that are constructed by the reporting functions
# in reports.py.

class AggregatedPerformanceMetricsSerializer(serializers.Serializer):
    """
    A base serializer defining common performance metrics.
    This is inherited by more specific performance serializers.
    All fields have default values to handle cases where data might be missing (e.g., zero spend).
    """
    # Common metrics
    impressions = serializers.IntegerField(default=0, help_text="Total impressions.")
    clicks = serializers.IntegerField(default=0, help_text="Total clicks.")
    spend = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total spend.")
    orders = serializers.IntegerField(default=0, help_text="Total orders attributed to ads.")
    sales = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Total sales revenue from ads.")

    # Calculated metrics
    acos = serializers.FloatField(default=0.0, help_text="Advertising Cost of Sales (Spend / Sales) * 100%.")
    roas = serializers.FloatField(default=0.0, help_text="Return on Ad Spend (Sales / Spend).")
    cpc = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Cost Per Click (Spend / Clicks).")
    ctr = serializers.FloatField(default=0.0, help_text="Click-Through Rate (Clicks / Impressions) * 100%.")
    cvr = serializers.FloatField(default=0.0, help_text="Conversion Rate (Orders / Clicks) * 100%.")

    # Date fields are typically handled by the view/query parameters defining the report range,
    # so they are not usually part of the serialized item itself unless it's a daily breakdown.
    # start_date = serializers.DateField(required=False)
    # end_date = serializers.DateField(required=False)

class CampaignPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    """
    Serializer for representing aggregated performance data at the campaign level.
    Includes campaign-specific details along with common performance metrics.
    """
    # Campaign specific fields (denormalized from the Campaign model)
    campaign_id = serializers.IntegerField(help_text="The ID of the campaign.")
    campaign_name = serializers.CharField(max_length=255, help_text="The name of the campaign.")
    ad_type = serializers.CharField(max_length=50, help_text="The ad type of the campaign (e.g., SPONSORED_PRODUCTS).") # Corresponds to AdTypeChoices
    status = serializers.CharField(max_length=20, help_text="The current status of the campaign (e.g., ENABLED).")  # Corresponds to CampaignStatusChoices
    daily_budget = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="The daily budget of the campaign.")
    start_date = serializers.DateField(help_text="The start date of the campaign.")
    end_date = serializers.DateField(allow_null=True, required=False, help_text="The end date of the campaign, if set.")
    # bidding_strategy = serializers.CharField(max_length=50) # Example: Not currently in specified report columns from user

class AdGroupPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    """
    Serializer for representing aggregated performance data at the ad group level.
    Includes ad group details and context from its parent campaign.
    """
    ad_group_id = serializers.IntegerField(help_text="The ID of the ad group.")
    ad_group_name = serializers.CharField(max_length=255, help_text="The name of the ad group.")
    campaign_id = serializers.IntegerField(help_text="The ID of the parent campaign.")
    campaign_name = serializers.CharField(max_length=255, help_text="The name of the parent campaign.")
    status = serializers.CharField(max_length=20, help_text="The status of the ad group.") # Assumes AdGroup model has status, maps to AdGroupStatusChoices
    default_bid = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, help_text="The default bid for the ad group.")


class KeywordPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    """
    Serializer for representing aggregated performance data at the keyword level.
    Includes keyword details and context from its parent ad group and campaign.
    """
    keyword_id = serializers.IntegerField(help_text="The ID of the keyword.")
    keyword_text = serializers.CharField(max_length=255, help_text="The text of the keyword.")
    match_type = serializers.CharField(max_length=20, help_text="The match type of the keyword (e.g., EXACT, BROAD).") # Corresponds to MatchTypeChoices
    bid = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="The bid for the keyword.")
    status = serializers.CharField(max_length=20, help_text="The status of the keyword.") # Corresponds to KeywordStatusChoices

    # Contextual information
    ad_group_id = serializers.IntegerField(help_text="The ID of the parent ad group.")
    ad_group_name = serializers.CharField(max_length=255, help_text="The name of the parent ad group.")
    campaign_id = serializers.IntegerField(help_text="The ID of the parent campaign.")
    campaign_name = serializers.CharField(max_length=255, help_text="The name of the parent campaign.")


class ProductTargetPerformanceSerializer(AggregatedPerformanceMetricsSerializer):
    """
    Serializer for representing aggregated performance data at the product target level.
    Includes product target details and context from its parent ad group and campaign.
    """
    product_target_id = serializers.IntegerField(help_text="The ID of the product target.")
    targeting_type = serializers.CharField(max_length=50, help_text="The type of product targeting (e.g., ASIN_SAME_AS, CATEGORY).") # Corresponds to ProductTargetingTypeChoices
    target_value = serializers.CharField(max_length=255, help_text="The value of the target (e.g., ASIN, category ID).")
    bid = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, help_text="The bid for the product target. Null if using ad group default bid.")
    status = serializers.CharField(max_length=20, help_text="The status of the product target.") # Corresponds to ProductTargetStatusChoices

    # Contextual information
    ad_group_id = serializers.IntegerField(help_text="The ID of the parent ad group.")
    ad_group_name = serializers.CharField(max_length=255, help_text="The name of the parent ad group.")
    campaign_id = serializers.IntegerField(help_text="The ID of the parent campaign.")
    campaign_name = serializers.CharField(max_length=255, help_text="The name of the parent campaign.")


# TODO: Consider adding a SearchTermReportItemDRFSerializer if the SearchTermReportView
# needs to return strictly typed/validated output matching a specific structure.
# Currently, SearchTermReportView returns a list of dictionaries directly from reports.py.
# Example structure for such a serializer:
#
# class SearchTermReportItemDRFSerializer(AggregatedPerformanceMetricsSerializer):
#     """
#     Serializer for representing items in a Search Term Report.
#     Each item typically corresponds to a unique search term and its performance metrics,
#     often within the context of a specific campaign, ad group, and matched keyword.
#     """
#     # Search term specific fields
#     search_term_text = serializers.CharField(help_text="The actual search term entered by the customer.")
#     report_date = serializers.DateField(required=False, help_text="The date of the search term record, if applicable (often aggregated over a period).")
#
#     # Context from where the search term originated or was matched
#     campaign_id = serializers.IntegerField(help_text="ID of the campaign related to this search term.")
#     campaign_name = serializers.CharField(max_length=255, help_text="Name of the campaign.")
#     ad_group_id = serializers.IntegerField(help_text="ID of the ad group related to this search term.")
#     ad_group_name = serializers.CharField(max_length=255, help_text="Name of the ad group.")
#
#     # Matched keyword details (if applicable, e.g., for SP manual campaigns)
#     matched_keyword_id = serializers.IntegerField(allow_null=True, required=False, help_text="ID of the keyword that matched this search term.")
#     matched_keyword_text = serializers.CharField(allow_null=True, required=False, max_length=255, help_text="Text of the matched keyword.")
#     match_type = serializers.CharField(allow_null=True, required=False, max_length=20, help_text="Match type of the keyword that was triggered.")
#
#     # Action Column: This is typically a frontend concern. The API provides necessary IDs
#     # (e.g., search_term_text, campaign_id, ad_group_id, matched_keyword_id) for the frontend
#     # to construct actions like "Add as keyword" or "Add as negative".
#
# This serializer would be used in SearchTermReportView if more structured output is preferred
# over the direct list of dictionaries.

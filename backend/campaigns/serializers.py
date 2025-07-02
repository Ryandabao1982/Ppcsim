from rest_framework import serializers
from .models import (
    Campaign, AdGroup, Keyword, ProductTarget,
    NegativeKeyword, NegativeProductTarget, CampaignProductLink
)
from products.models import Product # Assuming products app for Product model
from products.serializers import ProductSerializer # For nested display of products
from django.db import transaction # For atomic operations if creating nested objects

# --- Leaf Node Serializers ---

class KeywordSerializer(serializers.ModelSerializer):
    """Serializer for reading Keyword data."""
    class Meta:
        model = Keyword
        fields = ['id', 'ad_group', 'text', 'match_type', 'status', 'bid', 'created_at', 'updated_at']
        read_only_fields = ['id', 'ad_group', 'created_at', 'updated_at'] # ad_group set by parent

class KeywordCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Keywords."""
    class Meta:
        model = Keyword
        fields = ['text', 'match_type', 'status', 'bid'] # ad_group_id will be passed in view


class ProductTargetSerializer(serializers.ModelSerializer):
    """Serializer for reading ProductTarget data."""
    class Meta:
        model = ProductTarget
        fields = ['id', 'ad_group', 'targeting_type', 'target_value', 'status', 'bid', 'created_at', 'updated_at']
        read_only_fields = ['id', 'ad_group', 'created_at', 'updated_at']

class ProductTargetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating ProductTargets."""
    class Meta:
        model = ProductTarget
        fields = ['targeting_type', 'target_value', 'status', 'bid']


class NegativeKeywordSerializer(serializers.ModelSerializer):
    """Serializer for reading NegativeKeyword data."""
    class Meta:
        model = NegativeKeyword
        fields = ['id', 'campaign', 'ad_group', 'keyword_text', 'match_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'campaign', 'ad_group', 'created_at', 'updated_at']

class NegativeKeywordCreateUpdateSerializer(serializers.ModelSerializer):
    # For creation, campaign_id or ad_group_id will be set in the view based on the endpoint.
    # For update, these should not be changed.
    """Serializer for creating and updating NegativeKeywords."""
    class Meta:
        model = NegativeKeyword
        fields = ['keyword_text', 'match_type', 'status']
        # Exclude campaign and ad_group as they are set by context or immutable on update


class NegativeProductTargetSerializer(serializers.ModelSerializer):
    """Serializer for reading NegativeProductTarget data."""
    class Meta:
        model = NegativeProductTarget
        fields = ['id', 'campaign', 'ad_group', 'target_asin', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'campaign', 'ad_group', 'created_at', 'updated_at']

class NegativeProductTargetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating NegativeProductTargets."""
    class Meta:
        model = NegativeProductTarget
        fields = ['target_asin', 'status']


# --- AdGroup Serializers (may include nested children) ---

class AdGroupSerializer(serializers.ModelSerializer):
    """Serializer for reading AdGroup data, including nested targets."""
    keywords = KeywordSerializer(many=True, read_only=True)
    product_targets = ProductTargetSerializer(many=True, read_only=True)
    negative_keywords = NegativeKeywordSerializer(many=True, read_only=True)
    negative_product_targets = NegativeProductTargetSerializer(many=True, read_only=True)

    class Meta:
        model = AdGroup
        fields = [
            'id', 'campaign', 'name', 'status', 'default_bid',
            'keywords', 'product_targets', 'negative_keywords', 'negative_product_targets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'campaign', 'created_at', 'updated_at']


class AdGroupCreateUpdateSerializer(serializers.ModelSerializer):
    # For simplicity, nested creation of keywords/targets within AdGroup create/update
    # can be handled by separate endpoint calls after AdGroup is created/updated.
    # Or, implement create/update methods here if complex nested writes are needed.
    # For now, focusing on AdGroup fields.
    """Serializer for creating and updating AdGroups."""
    class Meta:
        model = AdGroup
        fields = ['name', 'status', 'default_bid'] # campaign_id will be passed in view


# --- Campaign Serializers (may include nested children) ---

class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for reading Campaign data, including nested ad groups and targets."""
    ad_groups = AdGroupSerializer(many=True, read_only=True)
    negative_keywords = NegativeKeywordSerializer(many=True, read_only=True) # Campaign-level
    negative_product_targets = NegativeProductTargetSerializer(many=True, read_only=True) # Campaign-level
    advertised_products = ProductSerializer(many=True, read_only=True) # Display product details
    user = serializers.StringRelatedField(read_only=True) # Display user email/username

    class Meta:
        model = Campaign
        fields = [
            'id', 'user', 'name', 'ad_type', 'status', 'daily_budget',
            'start_date', 'end_date', 'bidding_strategy', 'targeting_type',
            'advertised_products', 'ad_groups',
            'negative_keywords', 'negative_product_targets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CampaignCreateUpdateSerializer(serializers.ModelSerializer):
    # For M2M with products, we typically handle it in the view or by overriding create/update.
    # Pass a list of product IDs.
    advertised_product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False, # Allow creating campaign without products initially
        help_text="List of Product IDs to associate with this campaign."
    )
    # Nested creation of AdGroups or NegativeKeywords could be added here if desired,
    # but often it's cleaner to manage them via their own dedicated endpoints after campaign creation.
    # For now, this serializer focuses on Campaign fields + linking products.
    # Adding initial keywords and product targets for manual campaigns
    initial_keywords = KeywordCreateUpdateSerializer(many=True, required=False, write_only=True)
    initial_product_targets = ProductTargetCreateUpdateSerializer(many=True, required=False, write_only=True)
    # We could also add initial_negative_keywords etc. if the workflow demands it for campaign creation.
    """Serializer for creating and updating Campaigns, including linking products and initial targets."""
    class Meta:
        model = Campaign
        fields = [
            'name', 'ad_type', 'status', 'daily_budget',
            'start_date', 'end_date', 'bidding_strategy', 'targeting_type',
            'advertised_product_ids',
            'initial_keywords', 'initial_product_targets'
        ]
        # user field will be set in the view from request.user

    def create(self, validated_data):
        product_ids = validated_data.pop('advertised_product_ids', [])
        campaign = Campaign.objects.create(**validated_data)
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
            campaign.advertised_products.set(products) # Use set() for M2M
        return campaign

    def update(self, instance, validated_data):
        product_ids = validated_data.pop('advertised_product_ids', None)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update M2M relationship for products if product_ids were provided
        if product_ids is not None: # Allows clearing products by passing empty list
            products = Product.objects.filter(id__in=product_ids)
            instance.advertised_products.set(products)

        return instance

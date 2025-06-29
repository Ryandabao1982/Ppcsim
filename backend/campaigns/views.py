from rest_framework import viewsets, permissions, status, generics # Import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import (
    Campaign, AdGroup, Keyword, ProductTarget,
    NegativeKeyword, NegativeProductTarget
)
from .serializers import (
    CampaignSerializer, CampaignCreateUpdateSerializer,
    AdGroupSerializer, AdGroupCreateUpdateSerializer,
    KeywordSerializer, KeywordCreateUpdateSerializer,
    ProductTargetSerializer, ProductTargetCreateUpdateSerializer,
    NegativeKeywordSerializer, NegativeKeywordCreateUpdateSerializer,
    NegativeProductTargetSerializer, NegativeProductTargetCreateUpdateSerializer
)

# Custom Permission for checking object ownership against request.user
class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or view it.
    Assumes the object has a 'user' attribute (like Campaign) or a path to it.
    """
    def has_object_permission(self, request, view, obj):
        # For Campaign itself
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For objects linked to Campaign (AdGroup, campaign-level negatives)
        if hasattr(obj, 'campaign') and hasattr(obj.campaign, 'user'):
            return obj.campaign.user == request.user
        # For objects linked to AdGroup (Keyword, ProductTarget, adgroup-level negatives)
        if hasattr(obj, 'ad_group') and hasattr(obj.ad_group, 'campaign') and hasattr(obj.ad_group.campaign, 'user'):
            return obj.ad_group.campaign.user == request.user
        return False


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows campaigns to be viewed or edited.
    """
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Filter campaigns by the current authenticated user
        return Campaign.objects.filter(user=self.request.user).prefetch_related(
            'advertised_products',
            'ad_groups__keywords',
            'ad_groups__product_targets',
            'ad_groups__negative_keywords',
            'ad_groups__negative_product_targets',
            'negative_keywords', # Campaign-level
            'negative_product_targets' # Campaign-level
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CampaignCreateUpdateSerializer
        return CampaignSerializer

from decimal import Decimal # Import Decimal
from products.models import Product # For fetching product for competitive_intensity

# ... (IsOwner class remains the same) ...

class CampaignViewSet(viewsets.ModelViewSet):
    # ... (queryset and permission_classes remain the same) ...

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CampaignCreateUpdateSerializer
        return CampaignSerializer

    def perform_create(self, serializer):
        # Apply default daily budget if not provided
        daily_budget = serializer.validated_data.get('daily_budget')
        if daily_budget is None:
            # serializer.validated_data['daily_budget'] = Decimal("15.00") # Set default
            # This should be handled by the model default or serializer default if possible,
            # or set before calling serializer.save() if it's a view-level default.
            # For now, assume model default or serializer handles it.
            # If it must be done here, it's:
            # campaign = serializer.save(user=self.request.user, daily_budget=Decimal("15.00"))
            # Let's assume the serializer will pass it through or model has default.
            # The model does not have a default for daily_budget, so we should set it here.
            pass # Will handle defaults below before save or in serializer.

        # The serializer's create method already handles advertised_product_ids
        # We need to handle initial_keywords and initial_product_targets
        initial_keywords_data = serializer.validated_data.pop('initial_keywords', [])
        initial_product_targets_data = serializer.validated_data.pop('initial_product_targets', [])

        # Ensure default daily_budget
        if 'daily_budget' not in serializer.validated_data or serializer.validated_data['daily_budget'] is None:
            validated_data_with_defaults = {**serializer.validated_data, 'daily_budget': Decimal("15.00")}
        else:
            validated_data_with_defaults = serializer.validated_data

        campaign = serializer.save(user=self.request.user, **validated_data_with_defaults)


        # Determine default bid based on competitive intensity of one advertised product
        default_bid_for_targets = Decimal("1.00") # Base default
        if campaign.advertised_products.exists():
            first_product = campaign.advertised_products.first()
            if first_product: # Should exist if campaign.advertised_products.exists()
                if first_product.competitive_intensity == 'high':
                    default_bid_for_targets = Decimal("1.25")
                elif first_product.competitive_intensity == 'low':
                    default_bid_for_targets = Decimal("0.70")

        # Handle creation of default AdGroup and initial targets if applicable
        targeting_type = campaign.targeting_type # From validated_data or model default

        if targeting_type: # Only create default ad group if targeting type is set (e.g. for SP Manual/Auto)
            default_ad_group_name = "Default Auto Ad Group" if targeting_type == 'auto' else "Default Manual Ad Group"
            # Check if an ad group with this name already exists for this campaign to avoid duplicates if re-saving
            ad_group, created = AdGroup.objects.get_or_create(
                campaign=campaign,
                name=default_ad_group_name,
                defaults={'status': KeywordStatusChoices.ENABLED, 'default_bid': default_bid_for_targets}
            )

            if targeting_type == 'manual':
                if initial_keywords_data:
                    for kw_data in initial_keywords_data:
                        kw_data.pop('ad_group', None) # Remove if present, will be set
                        # Apply default bid if not provided in kw_data
                        if 'bid' not in kw_data or kw_data['bid'] is None:
                            kw_data['bid'] = default_bid_for_targets
                        Keyword.objects.create(ad_group=ad_group, **kw_data)

                if initial_product_targets_data:
                    for pt_data in initial_product_targets_data:
                        pt_data.pop('ad_group', None)
                        if 'bid' not in pt_data or pt_data['bid'] is None:
                            pt_data['bid'] = default_bid_for_targets
                        ProductTarget.objects.create(ad_group=ad_group, **pt_data)
        # serializer.save(user=self.request.user) # Original call

# ViewSets for resources nested under Campaign and AdGroup
# We'll use more specific ListCreateAPIView and RetrieveUpdateDestroyAPIView for nested resources
# to make URL parameter handling (campaign_pk, ad_group_pk) more explicit.

class AdGroupViewSet(viewsets.ModelViewSet):
    serializer_class = AdGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner] # IsOwner will check via obj.campaign.user

    def get_queryset(self):
        # Filter AdGroups by campaign_id from URL and ensure user owns the campaign
        campaign_pk = self.kwargs.get('campaign_pk')
        if campaign_pk:
            campaign = get_object_or_404(Campaign, pk=campaign_pk, user=self.request.user)
            return AdGroup.objects.filter(campaign=campaign).prefetch_related(
                'keywords', 'product_targets', 'negative_keywords', 'negative_product_targets'
            )
        return AdGroup.objects.none() # Should not happen if routed correctly

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AdGroupCreateUpdateSerializer
        return AdGroupSerializer

    def perform_create(self, serializer):
        campaign_pk = self.kwargs.get('campaign_pk')
        campaign = get_object_or_404(Campaign, pk=campaign_pk, user=self.request.user)
        serializer.save(campaign=campaign)


# Generic ViewSet for Ad Group Children (Keywords, ProductTargets, NegativeKeywords, NegativeProductTargets)
class BaseAdGroupChildViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner] # IsOwner checks via ad_group.campaign.user

    def get_ad_group(self):
        campaign_pk = self.kwargs.get('campaign_pk')
        ad_group_pk = self.kwargs.get('ad_group_pk')
        # Ensure user owns the campaign of the ad_group
        ad_group = get_object_or_404(
            AdGroup.objects.select_related('campaign__user'),
            pk=ad_group_pk,
            campaign_id=campaign_pk,
            campaign__user=self.request.user
        )
        return ad_group

    def get_queryset(self):
        ad_group = self.get_ad_group()
        # The actual model (e.g., Keyword, ProductTarget) will be set by subclasses
        return self.model.objects.filter(ad_group=ad_group)

    def perform_create(self, serializer):
        ad_group = self.get_ad_group()
        serializer.save(ad_group=ad_group)

class KeywordViewSet(BaseAdGroupChildViewSet):
    model = Keyword
    serializer_class = KeywordSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return KeywordCreateUpdateSerializer
        return KeywordSerializer

class ProductTargetViewSet(BaseAdGroupChildViewSet):
    model = ProductTarget
    serializer_class = ProductTargetSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductTargetCreateUpdateSerializer
        return ProductTargetSerializer

class AdGroupNegativeKeywordViewSet(BaseAdGroupChildViewSet):
    model = NegativeKeyword
    serializer_class = NegativeKeywordSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NegativeKeywordCreateUpdateSerializer
        return NegativeKeywordSerializer

    def perform_create(self, serializer): # Override to ensure campaign_id is None
        ad_group = self.get_ad_group()
        serializer.save(ad_group=ad_group, campaign_id=None)


class AdGroupNegativeProductTargetViewSet(BaseAdGroupChildViewSet):
    model = NegativeProductTarget
    serializer_class = NegativeProductTargetSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NegativeProductTargetCreateUpdateSerializer
        return NegativeProductTargetSerializer

    def perform_create(self, serializer): # Override to ensure campaign_id is None
        ad_group = self.get_ad_group()
        serializer.save(ad_group=ad_group, campaign_id=None)


# ViewSets for Campaign-Level Negatives
class BaseCampaignChildViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner] # IsOwner checks via campaign.user

    def get_campaign(self):
        campaign_pk = self.kwargs.get('campaign_pk')
        campaign = get_object_or_404(Campaign, pk=campaign_pk, user=self.request.user)
        return campaign

    def get_queryset(self):
        campaign = self.get_campaign()
        return self.model.objects.filter(campaign=campaign)

    def perform_create(self, serializer):
        campaign = self.get_campaign()
        serializer.save(campaign=campaign)


class CampaignNegativeKeywordViewSet(BaseCampaignChildViewSet):
    model = NegativeKeyword
    serializer_class = NegativeKeywordSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NegativeKeywordCreateUpdateSerializer
        return NegativeKeywordSerializer

    def perform_create(self, serializer): # Override to ensure ad_group_id is None
        campaign = self.get_campaign()
        serializer.save(campaign=campaign, ad_group_id=None)


class CampaignNegativeProductTargetViewSet(BaseCampaignChildViewSet):
    model = NegativeProductTarget
    serializer_class = NegativeProductTargetSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NegativeProductTargetCreateUpdateSerializer
        return NegativeProductTargetSerializer

    def perform_create(self, serializer): # Override to ensure ad_group_id is None
        campaign = self.get_campaign()
        serializer.save(campaign=campaign, ad_group_id=None)


# Generic update/delete for NegativeKeyword and NegativeProductTarget by their own ID
# These require checking ownership through their parent campaign/adgroup.
class NegativeKeywordDetailViewSet(generics.RetrieveUpdateDestroyAPIView): # Changed from viewsets
    queryset = NegativeKeyword.objects.all()
    serializer_class = NegativeKeywordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner] # IsOwner checks parentage

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NegativeKeywordCreateUpdateSerializer
        return NegativeKeywordSerializer

    # perform_update and perform_destroy will use IsOwner for permission check.

# Placeholder Views for Suggestions
class SuggestKeywordsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # product_ids = request.query_params.getlist('product_ids[]') # Or however IDs are passed
        # For now, return a hardcoded list or empty, awaiting actual logic
        # In a real implementation, fetch products, analyze names/descriptions/categories
        # and use the provided product-keyword mapping data.
        suggestions = [
            {"text": "suggested keyword 1", "match_type": "broad", "bid": "0.75"},
            {"text": "related term A", "match_type": "broad", "bid": "0.80"},
        ]
        return Response(suggestions)

class SuggestProductTargetsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # product_ids = request.query_params.getlist('product_ids[]')
        # Suggest related ASINs or categories based on input products
        suggestions = [
            {"targeting_type": "asin_same_as", "target_value": "B00EXAMPLE", "bid": "0.60"},
            {"targeting_type": "category_same_as", "target_value": "Electronics", "bid": "0.50"}, # Or category ID
        ]
        return Response(suggestions)

class NegativeProductTargetDetailViewSet(generics.RetrieveUpdateDestroyAPIView): # Changed from viewsets
    queryset = NegativeProductTarget.objects.all()
    serializer_class = NegativeProductTargetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NegativeProductTargetCreateUpdateSerializer
        return NegativeProductTargetSerializer

    # perform_update and perform_destroy will use IsOwner for permission check.

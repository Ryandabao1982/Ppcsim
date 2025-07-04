from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView # Import APIView
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
        # The line below was causing the IndentationError and seems to be a remnant of a bad merge/edit.
        # return CampaignSerializer # This was the original line before the duplicated imports and perform_create method.

    # The following perform_create method is the one that was correctly implemented
    # and should be the only one in this ViewSet.
    def perform_create(self, serializer):
        from decimal import Decimal # Import Decimal here, locally if not already at top
        from products.models import Product as ProductModel # For fetching product
        from campaigns.models import KeywordStatusChoices # For AdGroup defaults

        initial_keywords_data = serializer.validated_data.pop('initial_keywords', [])
        initial_product_targets_data = serializer.validated_data.pop('initial_product_targets', [])

        current_validated_data = serializer.validated_data.copy()
        if 'daily_budget' not in current_validated_data or current_validated_data['daily_budget'] is None:
            current_validated_data['daily_budget'] = Decimal("15.00")

        campaign = serializer.save(user=self.request.user, **current_validated_data)

        default_bid_for_targets = Decimal("1.00")
        if campaign.advertised_products.exists():
            first_product_instance = campaign.advertised_products.first()
            if first_product_instance:
                # Assuming ProductModel is the correct model for products, fetched via ORM
                # No need to re-fetch if first_product_instance is already a ProductModel instance.
                # If it's just an ID or a different representation, fetching might be needed.
                # For now, assume first_product_instance is a full Product object.
                if first_product_instance.competitive_intensity == 'high':
                    default_bid_for_targets = Decimal("1.25")
                elif first_product_instance.competitive_intensity == 'low':
                    default_bid_for_targets = Decimal("0.70")

        targeting_type = campaign.targeting_type

        if targeting_type:
            default_ad_group_name = "Default Auto Ad Group" if targeting_type == 'auto' else "Default Manual Ad Group"
            ad_group, created = AdGroup.objects.get_or_create(
                campaign=campaign,
                name=default_ad_group_name,
                defaults={'status': KeywordStatusChoices.ENABLED, 'default_bid': default_bid_for_targets}
            )

            if targeting_type == 'manual':
                if initial_keywords_data:
                    for kw_data in initial_keywords_data:
                        kw_data.pop('ad_group', None)
                        if 'bid' not in kw_data or kw_data['bid'] is None:
                            kw_data['bid'] = default_bid_for_targets
                        Keyword.objects.create(ad_group=ad_group, **kw_data)

                if initial_product_targets_data:
                    for pt_data in initial_product_targets_data:
                        pt_data.pop('ad_group', None)
                        if 'bid' not in pt_data or pt_data['bid'] is None:
                            pt_data['bid'] = default_bid_for_targets
                        ProductTarget.objects.create(ad_group=ad_group, **pt_data)

# ViewSets for resources nested under Campaign and AdGroup
# We'll use more specific ListCreateAPIView and RetrieveUpdateDestroyAPIView for nested resources
# to make URL parameter handling (campaign_pk, ad_group_pk) more explicit.

class AdGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AdGroups within a specific Campaign.
    Handles CRUD operations for AdGroups.
    """
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
    """
    Base ViewSet for resources that are children of an AdGroup (e.g., Keywords, ProductTargets).
    Handles queryset filtering and creation context based on ad_group_pk and campaign_pk from URL.
    """
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
    """ViewSet for managing Keywords within an AdGroup."""
    model = Keyword
    serializer_class = KeywordSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return KeywordCreateUpdateSerializer
        return KeywordSerializer

class ProductTargetViewSet(BaseAdGroupChildViewSet):
    """ViewSet for managing ProductTargets within an AdGroup."""
    model = ProductTarget
    serializer_class = ProductTargetSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductTargetCreateUpdateSerializer
        return ProductTargetSerializer

class AdGroupNegativeKeywordViewSet(BaseAdGroupChildViewSet):
    """ViewSet for managing NegativeKeywords at the AdGroup level."""
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
    """ViewSet for managing NegativeProductTargets at the AdGroup level."""
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
    """
    Base ViewSet for resources that are direct children of a Campaign (e.g., Campaign-level NegativeKeywords).
    Handles queryset filtering and creation context based on campaign_pk from URL.
    """
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
    """ViewSet for managing NegativeKeywords at the Campaign level."""
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
    """ViewSet for managing NegativeProductTargets at the Campaign level."""
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
class NegativeKeywordDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a specific NegativeKeyword by its ID.
    Ownership is checked via the IsOwner permission.
    """
    queryset = NegativeKeyword.objects.all()
    serializer_class = NegativeKeywordSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner] # IsOwner checks parentage

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NegativeKeywordCreateUpdateSerializer
        return NegativeKeywordSerializer

    # perform_update and perform_destroy will use IsOwner for permission check.

from products.keyword_data import get_keyword_suggestions_for_asins, PRODUCT_KEYWORD_MAPPINGS
from products.models import Product as ProductModel # Alias to avoid conflict if any

# Placeholder Views for Suggestions
class SuggestKeywordsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_asins_str = request.query_params.get('asins', '') # Expects comma-separated ASINs
        if not product_asins_str:
            return Response({"error": "Please provide ASINs to get suggestions."}, status=status.HTTP_400_BAD_REQUEST)

        product_asins = [asin.strip() for asin in product_asins_str.split(',')]

        # Validate ASINs against existing products (optional, but good practice)
        # existing_db_products = ProductModel.objects.filter(asin__in=product_asins).values_list('asin', flat=True)
        # valid_asins_for_suggestions = [asin for asin in product_asins if asin in existing_db_products and asin in PRODUCT_KEYWORD_MAPPINGS]

        # For now, directly use ASINs that are in our mapping
        valid_asins_for_suggestions = [asin for asin in product_asins if asin in PRODUCT_KEYWORD_MAPPINGS]

        if not valid_asins_for_suggestions:
            return Response({"suggestions": {"primary_keywords": [], "general_search_terms": []}, "message": "No valid ASINs found or no suggestions for provided ASINs."}, status=status.HTTP_200_OK)

        suggestions_data = get_keyword_suggestions_for_asins(valid_asins_for_suggestions)

        # Format for frontend (example: list of strings or list of dicts with more info)
        # The current get_keyword_suggestions_for_asins returns lists of strings.
        # The frontend might expect something like: [{"text": "kw", "match_type": "broad", "suggested_bid": "0.75"}]
        # For now, returning the raw structure from keyword_data.
        # TODO: Enhance with suggested bids and match types for general terms.

        formatted_suggestions = []
        for kw_text in suggestions_data.get("primary_keywords", []):
             # Primary keywords are often exact, but here we list them as text
            formatted_suggestions.append({"text": kw_text.strip("[]"), "match_type": "exact", "type": "primary"})
        for kw_text in suggestions_data.get("general_search_terms", []):
            formatted_suggestions.append({"text": kw_text, "match_type": "broad", "type": "general"}) # Defaulting general to broad

        return Response(formatted_suggestions)


class SuggestProductTargetsView(APIView): # Placeholder, not fully implemented with data
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # product_asins_str = request.query_params.get('asins', '')
        # TODO: Implement logic to suggest product targets (e.g., related categories, competitor ASINs)
        # This would likely involve analyzing the input products' categories, brands etc.
        # For now, returning hardcoded example.
        suggestions = [
            {"targeting_type": "asin_same_as", "target_value": "B0COMPETITOR1", "suggested_bid": "0.65"},
            {"targeting_type": "category_same_as", "target_value": "Related Category ID or Name", "suggested_bid": "0.55"},
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

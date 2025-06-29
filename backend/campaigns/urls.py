from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for top-level Campaign resources
router = DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')

# Routers for resources nested under Campaigns
# These will be for campaign-level negative keywords and negative product targets
campaign_level_neg_keywords_router = DefaultRouter()
campaign_level_neg_keywords_router.register(
    r'negative-keywords',
    views.CampaignNegativeKeywordViewSet,
    basename='campaign-negativekeyword'
)

campaign_level_neg_prodtarg_router = DefaultRouter()
campaign_level_neg_prodtarg_router.register(
    r'negative-product-targets',
    views.CampaignNegativeProductTargetViewSet,
    basename='campaign-negativeproducttarget'
)

# Routers for resources nested under AdGroups
# These will be for keywords, product targets, adgroup-level negative keywords, and adgroup-level negative product targets
adgroup_children_router = DefaultRouter() # A bit of a hack to use DefaultRouter for multiple children of adgroup
adgroup_children_router.register(r'keywords', views.KeywordViewSet, basename='adgroup-keyword')
adgroup_children_router.register(r'product-targets', views.ProductTargetViewSet, basename='adgroup-producttarget')
adgroup_children_router.register(r'negative-keywords', views.AdGroupNegativeKeywordViewSet, basename='adgroup-negativekeyword')
adgroup_children_router.register(r'negative-product-targets', views.AdGroupNegativeProductTargetViewSet, basename='adgroup-negativeproducttarget')


# We need to construct paths manually for nesting AdGroups under Campaigns,
# and then AdGroup children under AdGroups.
# DefaultRouter doesn't handle this nesting directly in a single router instance.

urlpatterns = [
    # Top-level campaign URLs (e.g., /api/campaign-manager/campaigns/)
    path('', include(router.urls)),

    # Campaign-specific resources
    # /api/campaign-manager/campaigns/{campaign_pk}/adgroups/
    path('campaigns/<int:campaign_pk>/adgroups/',
         views.AdGroupViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='campaign-adgroups-list'),
    path('campaigns/<int:campaign_pk>/adgroups/<int:pk>/',
         views.AdGroupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='campaign-adgroups-detail'),

    # Campaign-level negative keywords
    # /api/campaign-manager/campaigns/{campaign_pk}/negative-keywords/
    path('campaigns/<int:campaign_pk>/negative-keywords/',
         views.CampaignNegativeKeywordViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='campaign-negativekeywords-list'),
    path('campaigns/<int:campaign_pk>/negative-keywords/<int:pk>/', # This pk is negativekeyword id
         views.CampaignNegativeKeywordViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='campaign-negativekeywords-detail'),

    # Campaign-level negative product targets
    # /api/campaign-manager/campaigns/{campaign_pk}/negative-product-targets/
    path('campaigns/<int:campaign_pk>/negative-product-targets/',
         views.CampaignNegativeProductTargetViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='campaign-negativeproducttargets-list'),
    path('campaigns/<int:campaign_pk>/negative-product-targets/<int:pk>/', # This pk is negativeproducttarget id
         views.CampaignNegativeProductTargetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='campaign-negativeproducttargets-detail'),


    # AdGroup-specific resources (Keywords, ProductTargets, AdGroup-level Negatives)
    # /api/campaign-manager/campaigns/{campaign_pk}/adgroups/{ad_group_pk}/keywords/
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/keywords/',
         views.KeywordViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='adgroup-keywords-list'),
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/keywords/<int:pk>/',
         views.KeywordViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='adgroup-keywords-detail'),

    # /api/campaign-manager/campaigns/{campaign_pk}/adgroups/{ad_group_pk}/product-targets/
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/product-targets/',
         views.ProductTargetViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='adgroup-producttargets-list'),
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/product-targets/<int:pk>/',
         views.ProductTargetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='adgroup-producttargets-detail'),

    # /api/campaign-manager/campaigns/{campaign_pk}/adgroups/{ad_group_pk}/negative-keywords/
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/negative-keywords/',
         views.AdGroupNegativeKeywordViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='adgroup-negativekeywords-list'),
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/negative-keywords/<int:pk>/',
         views.AdGroupNegativeKeywordViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='adgroup-negativekeywords-detail'),

    # /api/campaign-manager/campaigns/{campaign_pk}/adgroups/{ad_group_pk}/negative-product-targets/
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/negative-product-targets/',
         views.AdGroupNegativeProductTargetViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='adgroup-negativeproducttargets-list'),
    path('campaigns/<int:campaign_pk>/adgroups/<int:ad_group_pk>/negative-product-targets/<int:pk>/',
         views.AdGroupNegativeProductTargetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='adgroup-negativeproducttargets-detail'),

    # Generic detail views for NegativeKeyword and NegativeProductTarget by their own ID
    # (These are already registered by the top-level router if we add them there,
    # but the ViewSets are designed to get pk from URL.
    # The generic update/delete views NegativeKeywordDetailViewSet and NegativeProductTargetDetailViewSet
    # are simpler to register with a top-level router if we want /api/campaign-manager/negative-keywords/{id})
    # For now, the nested structure above provides access.
    # We can add these later if needed for direct access by negative_keyword_id.
    # path('negative-keywords/<int:pk>/', views.NegativeKeywordDetailViewSet.as_view(), name='negativekeyword-detail'),
    # path('negative-product-targets/<int:pk>/', views.NegativeProductTargetDetailViewSet.as_view(), name='negativeproducttarget-detail'),

    # Suggestion endpoints (not part of a router, simple paths)
    path('suggest-keywords/', views.SuggestKeywordsView.as_view(), name='suggest-keywords'),
    path('suggest-product-targets/', views.SuggestProductTargetsView.as_view(), name='suggest-product-targets'),
]

# The router for top-level campaigns is already included in urlpatterns via path('', include(router.urls))
# The other "routers" (campaign_level_neg_*, adgroup_children_router) were conceptual for DefaultRouter
# but are not directly used when defining paths manually like this.
# The manual path definitions above cover the necessary CRUD for nested resources.

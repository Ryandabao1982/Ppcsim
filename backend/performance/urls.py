from django.urls import path
from .views import AdvanceWeekSimulationView

app_name = 'performance'

from .views import (
    AdvanceWeekSimulationView, DashboardMetricsView,
    CampaignPerformanceListView, AdGroupPerformanceListView,
    KeywordPerformanceListView
    # ProductTargetPerformanceListView
)

urlpatterns = [
    path('simulate/advance-week/', AdvanceWeekSimulationView.as_view(), name='simulate-advance-week'),

    # Dashboard API (might be better as a top-level /api/dashboard/ if not strictly "performance reports")
    # For now, keeping under performance app. The main project urls.py includes performance.urls under /api/
    # So this will be /api/dashboard/
    path('dashboard/', DashboardMetricsView.as_view(), name='dashboard-metrics'),

    # Specific Metrics Endpoints
    # These could also be nested under /api/campaign-manager/campaigns/{id}/metrics etc. for stricter REST.
    # Keeping them grouped under /api/metrics/ for now as per plan.
    path('metrics/campaigns/', CampaignPerformanceListView.as_view(), name='metrics-campaigns-list'),

    # For AdGroup and Keyword performance, they need parent IDs in the URL.
    # These paths might be better suited within the 'campaigns' app's router for true nesting.
    # Example: /api/campaign-manager/campaigns/{campaign_pk}/adgroups-performance/
    # Example: /api/campaign-manager/adgroups/{adgroup_pk}/keywords-performance/
    # For now, defining them here as flat paths under /api/ (via main urls.py inclusion)
    # This means the views will need to accept campaign_pk/adgroup_pk from URL kwargs.

    # Path for AdGroup performance for a specific campaign
    path('metrics/campaigns/<int:campaign_pk>/adgroups/', AdGroupPerformanceListView.as_view(), name='metrics-adgroups-list-for-campaign'),

    # Path for Keyword performance for a specific ad group
    # To make this work, AdGroupPerformanceListView and KeywordPerformanceListView need to expect these pks.
    # The views are already written to expect campaign_pk and ad_group_pk respectively from self.kwargs.
    path('metrics/adgroups/<int:ad_group_pk>/keywords/', KeywordPerformanceListView.as_view(), name='metrics-keywords-list-for-adgroup'),

    # TODO: Add path for ProductTargetPerformanceListView
    # path('metrics/adgroups/<int:ad_group_pk>/product-targets/', ProductTargetPerformanceListView.as_view(), name='metrics-producttargets-list-for-adgroup'),

    # Search Term Report API
    path('reports/search-terms/', views.SearchTermReportView.as_view(), name='report-search-terms'),
]

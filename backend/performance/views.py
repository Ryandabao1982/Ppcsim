from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.utils import timezone
import datetime # For date object
from typing import Optional

from .simulation_logic import run_weekly_simulation
from .serializers import (
    CampaignPerformanceSerializer, AdGroupPerformanceSerializer,
    CampaignPerformanceSerializer, AdGroupPerformanceSerializer,
    KeywordPerformanceSerializer, # ProductTargetPerformanceSerializer will be added later
    # We need a serializer for SearchTermReportItem if we're building that API here.
    # Let's assume it's defined or we use a generic approach for now.
    # For DRF, it's good to have a specific serializer.
    # from .serializers import SearchTermReportItemDRFSerializer # If defined
)
from .reports import (
    get_campaign_performance_summary, get_adgroup_performance_summary,
    get_keyword_performance_report, get_overall_dashboard_metrics,
    get_search_term_report_data # Import the function for STR
)
from campaigns.models import Campaign, AdGroup # For permission checks/filtering if needed
from django.shortcuts import get_object_or_404

# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL


class AdvanceWeekSimulationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_server_date = timezone.now().date()
        try:
            run_weekly_simulation(user_id=user.id, current_sim_date=current_server_date)
            return Response(
                {"message": f"Simulation successfully advanced for one week starting {current_server_date} for user {user.email}."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Error during simulation advancement for user {user.email}: {str(e)}")
            return Response(
                {"error": "An error occurred during simulation.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- Performance Report API Views ---

class DashboardMetricsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        data = get_overall_dashboard_metrics(
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date
        )
        # The data from get_overall_dashboard_metrics already matches DashboardMetrics schema structure
        # Pydantic schema for DashboardMetrics is in app.schemas, not performance.serializers
        # For now, returning raw dict. If strict schema validation needed here, import/use it.
        return Response(data)


class CampaignPerformanceListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        summary = get_campaign_performance_summary(
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date
        )
        serializer = CampaignPerformanceSerializer(summary, many=True)
        return Response(serializer.data)

class AdGroupPerformanceListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, campaign_pk=None, *args, **kwargs): # campaign_pk from URL
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # Ensure the user owns the campaign
        campaign = get_object_or_404(Campaign, pk=campaign_pk, user=request.user)

        summary = get_adgroup_performance_summary(
            user_id=request.user.id,
            campaign_id=campaign.id,
            start_date=start_date,
            end_date=end_date
        )
        serializer = AdGroupPerformanceSerializer(summary, many=True)
        return Response(serializer.data)


class KeywordPerformanceListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ad_group_pk=None, *args, **kwargs): # ad_group_pk from URL
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        # campaign_pk_filter = request.query_params.get('campaign_id') # Optional filter from query param

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # Ensure the user owns the ad_group (via its campaign)
        ad_group = get_object_or_404(AdGroup.objects.select_related('campaign__user'), pk=ad_group_pk)
        if ad_group.campaign.user != request.user:
            return Response({"detail": "Not authorized to access this ad group's data."}, status=status.HTTP_403_FORBIDDEN)

        summary = get_keyword_performance_report(
            user_id=request.user.id,
            ad_group_id=ad_group.id, # Filter by ad_group_pk from URL
            campaign_id=ad_group.campaign_id, # Pass campaign_id for context if needed by report func
            start_date=start_date,
            end_date=end_date
        )
        serializer = KeywordPerformanceSerializer(summary, many=True)
        return Response(serializer.data)

# TODO: Add ProductTargetPerformanceListView similar to KeywordPerformanceListView
# This will require:
# 1. `get_product_target_performance_report` function in reports.py
# 2. `ProductTargetPerformanceSerializer` in serializers.py (already created)
# 3. This view class definition.
# For now, focusing on the specified Campaign and Keyword reports.

class SearchTermReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        campaign_id_str = request.query_params.get('campaign_id')
        # ad_group_id_str = request.query_params.get('ad_group_id') # Future filter

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        campaign_id = int(campaign_id_str) if campaign_id_str else None
        # ad_group_id = int(ad_group_id_str) if ad_group_id_str else None

        # Permission check: if campaign_id is provided, ensure user owns it.
        if campaign_id:
            get_object_or_404(Campaign, pk=campaign_id, user=request.user)

        # Pagination parameters
        try:
            limit = int(request.query_params.get('limit', 100))
            skip = int(request.query_params.get('skip', 0)) # 'skip' for offset-based
            if limit < 1 or limit > 1000: limit = 100 # Bounds for limit
            if skip < 0: skip = 0
        except ValueError:
            limit = 100
            skip = 0

        report_data = get_search_term_report_data(
            db=None, # Django ORM is used directly in reports.py, no separate db session needed here
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date,
            campaign_id=campaign_id,
            # ad_group_id=ad_group_id,
            skip=skip,
            limit=limit
        )
        # The data from get_search_term_report_data is a list of dicts.
        # We need a DRF serializer for this data if we want typed output.
        # For MVP, returning list of dicts directly.
        # A SearchTermReportItemDRFSerializer would be used here.
        return Response(report_data)

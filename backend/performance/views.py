"""
API Views for the Performance application.

This module provides endpoints for:
- Triggering the weekly simulation process.
- Fetching aggregated performance metrics for dashboards and reports.
  - Overall dashboard metrics.
  - Campaign-level performance.
  - Ad Group-level performance.
  - Keyword-level performance.
  - Search Term Report data.

All views require user authentication.
Date filtering (start_date, end_date) is supported for most report views via query parameters.
"""
from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.utils import timezone
import datetime
from typing import Optional

from .simulation_logic import run_weekly_simulation
from .serializers import (
    CampaignPerformanceSerializer, AdGroupPerformanceSerializer,
    KeywordPerformanceSerializer,
    # ProductTargetPerformanceSerializer will be added later if a specific view is created for it.
    # SearchTermReportItemDRFSerializer could be defined for typed STR output if needed.
)
from .reports import (
    get_campaign_performance_summary, get_adgroup_performance_summary,
    get_keyword_performance_report, get_overall_dashboard_metrics,
    get_search_term_report_data
)
from campaigns.models import Campaign, AdGroup # For permission checks and fetching related objects
from django.shortcuts import get_object_or_404
from django.conf import settings # For User model if needed, though request.user is primary

# Import from insights_challenges app for post-simulation processing
from insights_challenges.rules import generate_insights_for_user
from insights_challenges.services import check_all_active_challenge_progress_for_user


class AdvanceWeekSimulationView(views.APIView):
    """
    Triggers the weekly simulation process for the authenticated user.
    This includes running the ad simulation, generating coach insights,
    and checking challenge progress.

    Requires authentication.
    Accepts POST requests.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to advance the simulation by one week.
        """
        user = request.user
        # Use the current server date as the start of the simulation week.
        # This could be adjusted if a specific simulation timeline is managed elsewhere.
        current_server_date = timezone.now().date()
        try:
            # Run core simulation logic
            run_weekly_simulation(user_id=user.id, current_sim_date=current_server_date)

            # After simulation, generate insights for the user for the week that just completed.
            # The 'current_sim_week_start_date' for insights should align with the simulation's date.
            generate_insights_for_user(user_id=user.id, current_sim_week_start_date=current_server_date)

            # After simulation, check progress on any active challenges.
            check_all_active_challenge_progress_for_user(user_id=user.id, current_sim_week_start_date=current_server_date)

            return Response(
                {"message": f"Simulation, insight generation, and challenge progress checks completed for week starting {current_server_date} for user {user.email}."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the error for debugging
            print(f"Error during weekly process for user {user.email} on {current_server_date}: {str(e)}")
            return Response(
                {"error": "An error occurred during the weekly simulation process.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- Performance Report API Views ---

class DashboardMetricsView(views.APIView):
    """
    Provides overall performance metrics for the user's dashboard.
    Supports date range filtering via 'start_date' and 'end_date' query parameters (YYYY-MM-DD).
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to fetch dashboard metrics.
        Query Params:
            start_date (str, optional): YYYY-MM-DD
            end_date (str, optional): YYYY-MM-DD
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        data = get_overall_dashboard_metrics(
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date
        )
        # The data from get_overall_dashboard_metrics is a dictionary.
        # No specific DRF serializer is used here for this simple structure, but one could be added for strict schema validation.
        return Response(data)


class CampaignPerformanceListView(views.APIView):
    """
    Provides a list of campaigns with their aggregated performance metrics.
    Supports date range filtering via 'start_date' and 'end_date' query parameters (YYYY-MM-DD).
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to fetch campaign performance data.
        Query Params:
            start_date (str, optional): YYYY-MM-DD
            end_date (str, optional): YYYY-MM-DD
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        summary = get_campaign_performance_summary(
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date
        )
        serializer = CampaignPerformanceSerializer(summary, many=True)
        return Response(serializer.data)

class AdGroupPerformanceListView(views.APIView):
    """
    Provides a list of ad groups within a specific campaign, with their aggregated performance metrics.
    The campaign ID is passed as a URL parameter (`campaign_pk`).
    Supports date range filtering via 'start_date' and 'end_date' query parameters (YYYY-MM-DD).
    Requires authentication and user ownership of the campaign.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, campaign_pk=None, *args, **kwargs): # campaign_pk from URL
        """
        Handles GET request to fetch ad group performance data for a campaign.
        Path Param:
            campaign_pk (int): The primary key of the campaign.
        Query Params:
            start_date (str, optional): YYYY-MM-DD
            end_date (str, optional): YYYY-MM-DD
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

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
    """
    Provides a list of keywords within a specific ad group, with their aggregated performance metrics.
    The ad group ID is passed as a URL parameter (`ad_group_pk`).
    Supports date range filtering via 'start_date' and 'end_date' query parameters (YYYY-MM-DD).
    Requires authentication and user ownership of the ad group (via its campaign).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ad_group_pk=None, *args, **kwargs): # ad_group_pk from URL
        """
        Handles GET request to fetch keyword performance data for an ad group.
        Path Param:
            ad_group_pk (int): The primary key of the ad group.
        Query Params:
            start_date (str, optional): YYYY-MM-DD
            end_date (str, optional): YYYY-MM-DD
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the user owns the ad_group (via its campaign)
        ad_group = get_object_or_404(AdGroup.objects.select_related('campaign__user'), pk=ad_group_pk)
        if ad_group.campaign.user != request.user:
            return Response({"detail": "Not authorized to access this ad group's data."}, status=status.HTTP_403_FORBIDDEN)

        summary = get_keyword_performance_report(
            user_id=request.user.id,
            ad_group_id=ad_group.id,
            campaign_id=ad_group.campaign_id, # Pass campaign_id for context if needed by report func
            start_date=start_date,
            end_date=end_date
        )
        serializer = KeywordPerformanceSerializer(summary, many=True)
        return Response(serializer.data)

# TODO: Add ProductTargetPerformanceListView similar to KeywordPerformanceListView
# This will require:
# 1. `get_product_target_performance_report` function in reports.py (similar to get_keyword_performance_report)
# 2. `ProductTargetPerformanceSerializer` in serializers.py (already created)
# 3. This view class definition, taking `ad_group_pk` and ensuring ownership.

class SearchTermReportView(views.APIView):
    """
    Provides Search Term Report (STR) data for the authenticated user.
    Supports filtering by date range ('start_date', 'end_date') and optionally by 'campaign_id'.
    Includes pagination via 'limit' and 'skip' query parameters.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to fetch Search Term Report data.
        Query Params:
            start_date (str, optional): YYYY-MM-DD
            end_date (str, optional): YYYY-MM-DD
            campaign_id (int, optional): Filter by a specific campaign ID.
            limit (int, optional): Number of records to return (default 100, max 1000).
            skip (int, optional): Number of records to skip for pagination (default 0).
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        campaign_id_str = request.query_params.get('campaign_id')
        # ad_group_id_str = request.query_params.get('ad_group_id') # Potential future filter

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
            campaign_id = int(campaign_id_str) if campaign_id_str else None
            # ad_group_id = int(ad_group_id_str) if ad_group_id_str else None
        except ValueError:
            return Response({"error": "Invalid date or ID format. Dates should be YYYY-MM-DD, IDs should be integers."}, status=status.HTTP_400_BAD_REQUEST)

        # Permission check: if campaign_id is provided, ensure user owns it.
        if campaign_id:
            get_object_or_404(Campaign, pk=campaign_id, user=request.user) # Raises 404 if not found or not owned (due to user filter)

        # Pagination parameters
        try:
            limit = int(request.query_params.get('limit', 100))
            skip = int(request.query_params.get('skip', 0))
            if not (1 <= limit <= 1000): limit = 100 # Bounds for limit
            if skip < 0: skip = 0
        except ValueError:
            limit = 100
            skip = 0

        report_data = get_search_term_report_data(
            user_id=request.user.id,
            start_date=start_date,
            end_date=end_date,
            campaign_id=campaign_id,
            # ad_group_id=ad_group_id, # Pass if implemented
            skip=skip,
            limit=limit
        )
        # The data from get_search_term_report_data is a list of dictionaries.
        # For more robust API design, a DRF serializer (e.g., SearchTermReportItemDRFSerializer)
        # could be defined in serializers.py and used here for response formatting and validation.
        # For MVP, returning the list of dicts directly is acceptable.
        return Response(report_data)

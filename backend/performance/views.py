from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.utils import timezone # For getting current date
import datetime # For date object

from .simulation_logic import run_weekly_simulation
# User model from settings
from django.conf import settings
User = settings.AUTH_USER_MODEL # This will get users.CustomUser

class AdvanceWeekSimulationView(views.APIView):
    """
    API endpoint to advance the simulation by one week for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Determine the current simulation date for the user.
        # For MVP, we'll use the current server date as the start of the week to simulate.
        # A more advanced system would persist and increment this date per user.
        # Let's assume the simulation generates data for the week *starting* from this date.
        # For example, if today is 2023-10-27, it simulates for 2023-10-27 to 2023-11-02.
        current_server_date = timezone.now().date()

        # To avoid re-simulating the same week repeatedly if called multiple times on the same day,
        # a real system might check the last simulated date for the user.
        # For this MVP, we'll just run it based on current_server_date.
        # The simulation logic itself generates 7 days of data from the passed date.

        try:
            run_weekly_simulation(user_id=user.id, current_sim_date=current_server_date)
            return Response(
                {"message": f"Simulation successfully advanced for one week starting {current_server_date} for user {user.email}."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the exception (e.g., using logging module)
            print(f"Error during simulation advancement for user {user.email}: {str(e)}") # Basic logging
            return Response(
                {"error": "An error occurred during simulation.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# from django.utils import timezone # Not strictly needed here anymore for start action

from .models import CoachInsightsLog, Challenge, StudentChallengeProgress, ChallengeStatusChoices
from .serializers import (
    CoachInsightsLogSerializer, ChallengeSerializer, StudentChallengeProgressSerializer
)
from .services import start_challenge_for_user

class CoachInsightsLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for student's coaching insights.
    Supports filtering by `is_read` status.
    Includes an action to mark an insight as read.
    """
    serializer_class = CoachInsightsLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CoachInsightsLog.objects.filter(user=user).order_by('-created_at')

        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            if is_read_param.lower() == 'true':
                queryset = queryset.filter(is_read=True)
            elif is_read_param.lower() == 'false':
                queryset = queryset.filter(is_read=False)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        """Marks a specific insight as read for the logged-in user."""
        insight = self.get_object() # Handles 404 and uses get_queryset for initial filtering
        # get_queryset already filters by user, so direct check might be redundant but safe.
        if insight.user != request.user:
             return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        insight.is_read = True
        insight.save()
        return Response(CoachInsightsLogSerializer(insight).data)

class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list available challenges and allow users to start them.
    """
    queryset = Challenge.objects.filter(is_active=True).order_by('level', 'title')
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated] # All authenticated users can see challenges

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        """Starts a challenge for the logged-in user."""
        challenge = self.get_object() # Gets challenge by pk from the default queryset

        # The start_challenge_for_user service now handles creation and uses timezone.now()
        progress = start_challenge_for_user(
            user_id=request.user.id,
            challenge_id=challenge.id
        )

        if progress:
            # Check if the progress object was newly created or if an existing one was returned
            # Based on current service, it always creates a new one, or returns None if challenge not found.
            # If service was changed to prevent multiple active attempts for the same challenge,
            # it might return an existing one or raise an exception.
            # For now, assuming service returns a new progress or None.
            return Response(StudentChallengeProgressSerializer(progress).data, status=status.HTTP_201_CREATED)
        else:
            # This 'else' case implies challenge was not found or not active, as per service logic.
            return Response({"detail": "Could not start challenge. It may not be active or found."}, status=status.HTTP_400_BAD_REQUEST)


class StudentChallengeProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view student's progress on their started challenges.
    Provides list and retrieve actions.
    """
    serializer_class = StudentChallengeProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Returns challenge progress records for the currently authenticated user."""
        return StudentChallengeProgress.objects.filter(user=self.request.user).select_related('challenge', 'user').order_by('-start_time')

    def get_object(self):
        """Ensures that the retrieved object belongs to the requesting user."""
        obj = super().get_object()
        if obj.user != self.request.user:
            # This check is technically redundant if get_queryset is always filtered by user,
            # but good for defense in depth, especially if get_queryset logic changes.
            # However, for a standard RetrieveUpdateDestroyAPIView, get_queryset is NOT called for single object retrieval by default.
            # The base get_object fetches directly using self.queryset.filter(pk=self.kwargs[self.lookup_field]).
            # So this check is important here.
            raise permissions.PermissionDenied("You do not have permission to view this challenge progress.")
        return obj

# MyStudentChallengeProgressListView is removed as its functionality is covered by StudentChallengeProgressViewSet's list action.

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone # For current_sim_date in starting challenge

from .models import CoachInsightsLog, Challenge, StudentChallengeProgress
from .serializers import (
    CoachInsightsLogSerializer, ChallengeSerializer, StudentChallengeProgressSerializer
)
from .services import start_challenge_for_user # Assuming services.py exists

class CoachInsightsLogViewSet(viewsets.ReadOnlyModelViewSet): # Mostly read-only
    """
    API endpoint for student's coaching insights.
    """
    serializer_class = CoachInsightsLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CoachInsightsLog.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        insight = self.get_object() # Gets insight by pk, checks ownership via get_queryset
        if insight.user != request.user: # Double check ownership
             return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        insight.is_read = True
        insight.save()
        return Response(CoachInsightsLogSerializer(insight).data)

class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list available challenges.
    """
    queryset = Challenge.objects.filter(is_active=True).order_by('difficulty_level', 'name')
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated] # All authenticated users can see challenges

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        challenge = self.get_object() # Gets challenge by pk
        # For current_sim_date, we'd ideally get this from a user's simulation state.
        # For MVP, using today's actual date as a proxy for when the challenge starts in sim time.
        # This should be refined later to use the user's actual current simulation week start date.
        current_sim_date_for_challenge_start = timezone.now().date()

        progress = start_challenge_for_user(
            user_id=request.user.id,
            challenge_id=challenge.id,
            current_sim_date=current_sim_date_for_challenge_start
        )
        if progress:
            return Response(StudentChallengeProgressSerializer(progress).data, status=status.HTTP_201_CREATED)
        else:
            # e.g., if challenge not found, not active, or user already has active attempt (depending on service logic)
            # The service function start_challenge_for_user prints reasons, here we give generic error.
            # Or the service could raise specific exceptions.
             existing_active = StudentChallengeProgress.objects.filter(
                user=request.user, challenge=challenge, status='active'
            ).first()
             if existing_active:
                return Response(
                    {"detail": "You are already actively pursuing this challenge.",
                     "progress_id": existing_active.id},
                    status=status.HTTP_400_BAD_REQUEST
                )
             return Response({"detail": "Could not start challenge."}, status=status.HTTP_400_BAD_REQUEST)


class StudentChallengeProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view student's progress on challenges.
    """
    serializer_class = StudentChallengeProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Path for all progress for current user: /api/challenges/my-progress/
        # Path for specific progress: /api/challenges/progress/{progress_id}/ (handled by retrieve)
        return StudentChallengeProgress.objects.filter(user=self.request.user).select_related('challenge', 'user').order_by('-last_updated_at')

    # get_object for retrieve (e.g. /api/challenges/progress/{id}/) is handled by ReadOnlyModelViewSet
    # It will automatically filter by pk. We just need to make sure user owns it.
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to view this challenge progress.")
        return obj

# Alternative way to list user's progress without a separate ViewSet action
class MyStudentChallengeProgressListView(generics.ListAPIView):
    serializer_class = StudentChallengeProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudentChallengeProgress.objects.filter(user=self.request.user).select_related('challenge', 'user').order_by('-last_updated_at')

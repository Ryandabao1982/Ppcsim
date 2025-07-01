from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Using DefaultRouter for standard ViewSet actions
router = DefaultRouter()
router.register(r'challenges', views.ChallengeViewSet, basename='challenge') # For /api/challenges/ and /api/challenges/{pk}/
router.register(r'student-insights', views.CoachInsightsLogViewSet, basename='student-insight') # For /api/student-insights/ and /api/student-insights/{pk}/
# StudentChallengeProgress by its direct ID is handled by its ViewSet's default retrieve
router.register(r'challenge-progress', views.StudentChallengeProgressViewSet, basename='student-challenge-progress')


urlpatterns = [
    path('', include(router.urls)), # Includes standard list/detail for ViewSets registered above

    # Custom path for listing all of current user's challenge progresses
    path('challenges/my-progress/',
         views.MyStudentChallengeProgressListView.as_view(),
         name='my-student-challenge-progress-list'),

    # Note: The 'start' action on ChallengeViewSet is automatically routed by DRF's router:
    # e.g. POST /api/challenges/{challenge_pk}/start/
    # The 'mark_read' action on CoachInsightsLogViewSet is also auto-routed:
    # e.g. POST /api/student-insights/{insight_pk}/mark_read/
]

# Final URLs will be prefixed by what's in the main project's urls.py, e.g., /api/
# So, for example:
# /api/challenges/
# /api/challenges/{id}/
# /api/challenges/{id}/start/
# /api/student-insights/
# /api/student-insights/{id}/mark_read/
# /api/challenges/my-progress/
# /api/challenge-progress/{id}/ (for a specific progress entry by its ID)

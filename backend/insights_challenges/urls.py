from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Using DefaultRouter for standard ViewSet actions
router = DefaultRouter()
router.register(r'challenges', views.ChallengeViewSet, basename='challenge')
router.register(r'coach-insights', views.CoachInsightsLogViewSet, basename='coach-insight')
router.register(r'student-challenges', views.StudentChallengeProgressViewSet, basename='student-challenge')


urlpatterns = [
    path('', include(router.urls)), # Includes standard list/detail and custom actions for ViewSets registered above

    # The MyStudentChallengeProgressListView path is removed as StudentChallengeProgressViewSet handles listing.

    # Note: The 'start' action on ChallengeViewSet is automatically routed by DRF's router:
    # e.g. POST /api/insights-challenges/challenges/{challenge_pk}/start/ (prefix depends on main urls.py)
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

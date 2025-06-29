from django.urls import path
from .views import AdvanceWeekSimulationView

app_name = 'performance'

urlpatterns = [
    path('simulate/advance-week/', AdvanceWeekSimulationView.as_view(), name='simulate-advance-week'),
]

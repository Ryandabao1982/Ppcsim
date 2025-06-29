from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView, # Login
    UserLogoutView,
    UserDetailsView
)

app_name = 'users' # Optional: for namespacing if using Django templates extensively

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # Login
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # Refresh JWT
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('me/', UserDetailsView.as_view(), name='user_details'),
]

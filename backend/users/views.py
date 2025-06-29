from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
# For blacklisting to work, ensure 'rest_framework_simplejwt.token_blacklist' is in INSTALLED_APPS
# and run migrations if you add it. For MVP, we might skip blacklist persistence.
# If not using blacklist app, logout is mostly a client-side token removal.
# The view below attempts blacklist if refresh token is provided.

from .serializers import UserRegistrationSerializer, UserDetailsSerializer
from .models import CustomUser

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Optionally, log the user in immediately and return a token
        # For now, just return user data and a success message
        return Response({
            # Returning UserDetailsSerializer data to avoid exposing password hash, etc.
            "user": UserDetailsSerializer(user, context=self.get_serializer_context()).data,
            "message": "User registered successfully. Please log in."
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    # This view handles login and issues JWT access and refresh tokens.
    # Uses TokenObtainPairSerializer by default which validates 'email' and 'password'.
    # Ensure your CustomUser model's USERNAME_FIELD is 'email'.
    pass

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # A stateless JWT logout primarily means the client discards the token.
        # Server-side logout for JWT often involves blacklisting the refresh token if used.
        # SimpleJWT's blacklist app is needed for true server-side invalidation of refresh tokens.
        # For MVP, if blacklist app is not set up, this endpoint is more of a formality
        # or relies on short-lived access tokens.
        try:
            refresh_token = request.data.get("refresh_token") # Standard field name for refresh token
            if refresh_token:
                token = RefreshToken(refresh_token)
                # To effectively blacklist, 'rest_framework_simplejwt.token_blacklist'
                # must be in INSTALLED_APPS and its migrations run.
                # If not using the blacklist app, this line will cause an error
                # or do nothing depending on SimpleJWT version/configuration.
                # For a simple logout without server-side blacklisting:
                # just return success, client handles token deletion.
                # token.blacklist() # Uncomment if blacklist app is configured

                # For now, assume client deletes token. Server just acknowledges.
                return Response({"detail": "Logout successful. Please discard your tokens."}, status=status.HTTP_200_OK)
            else:
                # If no refresh token, it implies client should just delete access token.
                return Response({"detail": "Logout successful (no refresh token provided). Please discard your access token."}, status=status.HTTP_200_OK)
        except Exception as e:
            # This might catch errors if blacklisting is attempted without setup.
            # print(f"Logout error: {e}") # For debugging
            return Response({"detail": "Logout processed. Ensure client tokens are discarded."}, status=status.HTTP_200_OK)


class UserDetailsView(generics.RetrieveAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access

    def get_object(self):
        # request.user will be the CustomUser instance due to JWTAuthentication
        return self.request.user

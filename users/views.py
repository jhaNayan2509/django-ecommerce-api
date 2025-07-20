from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer, UserProfileSerializer


# API view for user registration using Django REST Framework generics
class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    - create: POST /api/users/register/ (Register a new user)
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]




# API view for user logout
# This view blacklists the refresh token to log the user out
class LogoutView(generics.GenericAPIView):
    """
    API view for user logout.
    - post: POST /api/users/logout/ (Logs out the user by blacklisting their refresh token)
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """
        Expects a 'refresh' token in the request data to blacklist.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."},status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": f"Logout failed due to {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




# API view for user managing their profile
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for viewing and updating the authenticated user's profile.
    - get: GET /api/users/profile/ (View your profile)
    - put: PUT /api/users/profile/ (Update your profile)
    - patch: PATCH /api/users/profile/ (Partially update your profile)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        This view should return an object instance for the current authenticated user.
        """
        return self.request.user
from django.urls import path
from .views import UserRegistrationView, LogoutView, UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
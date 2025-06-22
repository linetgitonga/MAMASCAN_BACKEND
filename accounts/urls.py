# accounts/urls.py
from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserProfileView,
    UserProfileUpdateView, PasswordChangeView, SpecialistListView,
    logout_view, user_stats_view
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', logout_view, name='user_logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('specialists/', SpecialistListView.as_view(), name='specialist_list'),
    path('stats/', user_stats_view, name='user_stats'),
]
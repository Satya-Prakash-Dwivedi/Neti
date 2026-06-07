from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, PasswordResetRequestView, PasswordResetConfirmView, GoogleLoginView

urlpatterns = [
    # Registration endpoint
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # Login (token exchange) and refresh endpoints provided by SimpleJWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    
    # Authenticated user profile details
    path('profile/', UserProfileView.as_view(), name='auth_profile'),

    # Password Reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
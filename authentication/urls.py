from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView

urlpatterns = [
    # Registration endpoint
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # Login (token exchange) and refresh endpoints provided by SimpleJWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authenticated user profile details
    path('profile/', UserProfileView.as_view(), name='auth_profile'),
]
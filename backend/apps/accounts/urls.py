from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, MeView, logout_view, ProfileView,
    ApiKeyListCreateView, ApiKeyDetailView, CustomTokenObtainPairView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),

    # User
    path('me/', MeView.as_view(), name='me'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # API Keys
    path('api-keys/', ApiKeyListCreateView.as_view(), name='api_key_list'),
    path('api-keys/<int:pk>/', ApiKeyDetailView.as_view(), name='api_key_detail'),
]

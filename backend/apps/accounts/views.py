from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Profile, ApiKey, Sphere, IntegrationType
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    UserUpdateSerializer, ProfileSerializer, ApiKeySerializer,
    CustomTokenObtainPairSerializer, SphereSerializer, IntegrationTypeSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that accepts username or email
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Override post to add error handling
        """
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Login error: {type(e).__name__}: {str(e)}", exc_info=True)
            raise


class RegisterView(generics.CreateAPIView):
    """User registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    """Get/Update current user"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user (blacklist refresh token)"""
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update user profile (tenant-specific)"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get or create profile for current user in tenant schema
        profile, created = Profile.objects.get_or_create(
            user_id=self.request.user.id,
            defaults={
                'notification_email': self.request.user.email,
            }
        )
        return profile


class ApiKeyListCreateView(generics.ListCreateAPIView):
    """List and create API keys"""
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApiKeyDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve and delete API key"""
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)


class SphereViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving Spheres
    Read-only - spheres are managed through admin panel
    """
    queryset = Sphere.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = SphereSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class IntegrationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving Integration Types
    Can filter by sphere_id to get integrations for specific sphere
    Read-only - integration types are managed through admin panel
    """
    serializer_class = IntegrationTypeSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = IntegrationType.objects.filter(is_active=True).order_by('order', 'name')

        # Filter by sphere if sphere_id or sphere_slug is provided
        sphere_id = self.request.query_params.get('sphere_id', None)
        sphere_slug = self.request.query_params.get('sphere_slug', None)

        if sphere_id:
            queryset = queryset.filter(spheres__id=sphere_id)
        elif sphere_slug:
            queryset = queryset.filter(spheres__slug=sphere_slug)

        return queryset.distinct()

"""
New API views for sphere-based integrations
This file contains updated views that work with the new IntegrationType system
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Integration, IntegrationWorkingHours
from .serializers import (
    IntegrationSerializer, IntegrationCreateSerializer,
    IntegrationWorkingHoursSerializer
)


class IntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user integrations
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return integrations for the current user only"""
        return Integration.objects.filter(user_id=self.request.user.id).order_by('-created_at')

    def get_serializer_class(self):
        """Use different serializers for create and list/retrieve"""
        if self.action == 'create':
            return IntegrationCreateSerializer
        return IntegrationSerializer

    def perform_create(self, serializer):
        """Set user_id when creating integration"""
        serializer.save()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate integration"""
        integration = self.get_object()
        integration.status = 'active'
        integration.error_message = ''
        integration.save()
        return Response({'status': 'activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate integration"""
        integration = self.get_object()
        integration.status = 'disabled'
        integration.save()
        return Response({'status': 'deactivated'})

    @action(detail=True, methods=['get', 'post', 'put'])
    def working_hours(self, request, pk=None):
        """
        Manage working hours for integration
        GET: List working hours
        POST/PUT: Create or update working hours
        """
        integration = self.get_object()

        if request.method == 'GET':
            working_hours = integration.working_hours.all().order_by('weekday', 'start_time')
            serializer = IntegrationWorkingHoursSerializer(working_hours, many=True)
            return Response(serializer.data)

        elif request.method in ['POST', 'PUT']:
            # Expect list of working hours
            working_hours_data = request.data.get('working_hours', [])

            # Delete existing working hours
            integration.working_hours.all().delete()

            # Create new working hours
            created_hours = []
            for wh_data in working_hours_data:
                wh_data['integration'] = integration.id
                serializer = IntegrationWorkingHoursSerializer(data=wh_data)
                if serializer.is_valid(raise_exception=True):
                    created_hours.append(serializer.save())

            result_serializer = IntegrationWorkingHoursSerializer(created_hours, many=True)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class IntegrationWorkingHoursViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing integration working hours
    """
    serializer_class = IntegrationWorkingHoursSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return working hours for user's integrations only"""
        return IntegrationWorkingHours.objects.filter(
            integration__user_id=self.request.user.id
        ).order_by('weekday', 'start_time')

    def perform_create(self, serializer):
        """Validate that integration belongs to user"""
        integration = serializer.validated_data['integration']
        if integration.user_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to modify this integration")

        serializer.save()

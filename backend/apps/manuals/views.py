from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from .models import ManualCategory, Manual, ManualFeedback
from .serializers import ManualCategorySerializer, ManualSerializer, ManualFeedbackSerializer


class ManualCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для категорій мануалів
    """
    queryset = ManualCategory.objects.filter(is_active=True)
    serializer_class = ManualCategorySerializer
    permission_classes = [IsAuthenticated]


class ManualViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для мануалів
    """
    serializer_class = ManualSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Manual.objects.filter(is_published=True)

        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)

        # Filter by integration type
        integration = self.request.query_params.get('integration')
        if integration:
            queryset = queryset.filter(integration_type=integration)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(content__icontains=search)
            )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Отримання конкретного мануала з інкрементом переглядів
        """
        instance = self.get_object()

        # Increment views count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Отримання рекомендованих мануалів
        """
        language = request.query_params.get('language', 'en')
        manuals = Manual.objects.filter(
            is_published=True,
            is_featured=True,
            language=language
        )[:6]

        serializer = self.get_serializer(manuals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """
        Додати фідбек до мануала
        """
        manual = self.get_object()
        user_id = request.user.id

        is_helpful = request.data.get('is_helpful', True)
        comment = request.data.get('comment', '')

        # Create or update feedback
        feedback, created = ManualFeedback.objects.update_or_create(
            manual=manual,
            user_id=user_id,
            defaults={
                'is_helpful': is_helpful,
                'comment': comment
            }
        )

        # Update manual helpful count
        manual.helpful_count = manual.feedback.filter(is_helpful=True).count()
        manual.save(update_fields=['helpful_count'])

        serializer = ManualFeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

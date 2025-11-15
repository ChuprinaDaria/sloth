from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManualCategoryViewSet, ManualViewSet

router = DefaultRouter()
router.register(r'categories', ManualCategoryViewSet, basename='manual-category')
router.register(r'', ManualViewSet, basename='manual')

urlpatterns = [
    path('', include(router.urls)),
]

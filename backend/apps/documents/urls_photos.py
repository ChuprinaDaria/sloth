from django.urls import path
from .views import PhotoUploadView, PhotoListView

app_name = 'photos'

urlpatterns = [
    path('upload/', PhotoUploadView.as_view(), name='upload'),
    path('', PhotoListView.as_view(), name='list'),
]


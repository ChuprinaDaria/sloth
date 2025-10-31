from django.urls import path
from .views import VectorStoreView, search_view, rebuild_view

app_name = 'embeddings'

urlpatterns = [
    path('settings/', VectorStoreView.as_view(), name='settings'),
    path('search/', search_view, name='search'),
    path('rebuild/', rebuild_view, name='rebuild'),
]

from django.urls import path
from .views import VectorStoreView, search_view, rebuild_view, process_all_view, status_view

app_name = 'embeddings'

urlpatterns = [
    path('settings/', VectorStoreView.as_view(), name='settings'),
    path('search/', search_view, name='search'),
    path('rebuild/', rebuild_view, name='rebuild'),
    path('process-all/', process_all_view, name='process_all'),
    path('status/', status_view, name='status'),
]

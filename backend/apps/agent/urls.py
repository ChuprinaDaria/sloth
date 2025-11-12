from django.urls import path
from .views import (
    PromptView, chat_view, ConversationListView,
    ConversationDetailView, test_chat_view, smart_insights_view,
    dashboard_stats_view
)

app_name = 'agent'

urlpatterns = [
    path('prompt/', PromptView.as_view(), name='prompt'),
    path('chat/', chat_view, name='chat'),
    path('test/', test_chat_view, name='test'),
    path('history/', ConversationListView.as_view(), name='history_list'),
    path('history/<int:pk>/', ConversationDetailView.as_view(), name='history_detail'),
    path('analytics/insights/', smart_insights_view, name='smart_insights'),
    path('dashboard/stats/', dashboard_stats_view, name='dashboard_stats'),
]

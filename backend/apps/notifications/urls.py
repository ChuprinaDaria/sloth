from django.urls import path
from . import views

urlpatterns = [
    path('register-token/', views.register_push_token, name='register_push_token'),
    path('unregister-token/', views.unregister_push_token, name='unregister_push_token'),
    path('settings/', views.notification_settings, name='notification_settings'),
    path('history/', views.notification_history, name='notification_history'),
    path('test/', views.test_notification, name='test_notification'),
]

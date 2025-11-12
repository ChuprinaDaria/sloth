from django.urls import path
from . import views

urlpatterns = [
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-of-service/', views.terms_of_service, name='terms-of-service'),
    path('support-contact/', views.support_contact, name='support-contact'),
    path('app-download-links/', views.app_download_links, name='app-download-links'),
]

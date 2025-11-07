from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PrivacyPolicy, TermsOfService, SupportContact, AppDownloadLinks
from rest_framework import serializers


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['language', 'title', 'content', 'last_updated', 'version']


class TermsOfServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsOfService
        fields = ['language', 'title', 'content', 'last_updated', 'version']


class SupportContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportContact
        fields = ['email', 'telegram', 'phone', 'working_hours', 'response_time']


class AppDownloadLinksSerializer(serializers.ModelSerializer):
    ios_download_url = serializers.SerializerMethodField()
    android_download_url = serializers.SerializerMethodField()

    class Meta:
        model = AppDownloadLinks
        fields = ['ios_download_url', 'android_download_url', 'coming_soon']

    def get_ios_download_url(self, obj):
        return obj.get_ios_url()

    def get_android_download_url(self, obj):
        return obj.get_android_url()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def privacy_policy(request):
    """
    Get Privacy Policy by language

    Query params:
        lang: uk, en, pl, ru (default: uk)
    """
    lang = request.query_params.get('lang', 'uk')

    try:
        policy = PrivacyPolicy.objects.get(language=lang, is_active=True)
        serializer = PrivacyPolicySerializer(policy)
        return Response(serializer.data)
    except PrivacyPolicy.DoesNotExist:
        # Fallback to Ukrainian
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if policy:
            serializer = PrivacyPolicySerializer(policy)
            return Response(serializer.data)
        return Response({'error': 'Privacy Policy not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def terms_of_service(request):
    """
    Get Terms of Service by language

    Query params:
        lang: uk, en, pl, ru (default: uk)
    """
    lang = request.query_params.get('lang', 'uk')

    try:
        terms = TermsOfService.objects.get(language=lang, is_active=True)
        serializer = TermsOfServiceSerializer(terms)
        return Response(serializer.data)
    except TermsOfService.DoesNotExist:
        # Fallback to Ukrainian
        terms = TermsOfService.objects.filter(is_active=True).first()
        if terms:
            serializer = TermsOfServiceSerializer(terms)
            return Response(serializer.data)
        return Response({'error': 'Terms of Service not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def support_contact(request):
    """Get support contact information"""
    contact = SupportContact.get_active()
    if contact:
        serializer = SupportContactSerializer(contact)
        return Response(serializer.data)
    return Response({'email': 'support@lazysoft.pl'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def app_download_links(request):
    """Get mobile app download links"""
    links = AppDownloadLinks.get_active()
    if links:
        serializer = AppDownloadLinksSerializer(links)
        return Response(serializer.data)
    return Response({
        'ios_download_url': None,
        'android_download_url': None,
        'coming_soon': True
    })

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/referrals/', include('apps.referrals.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/photos/', include('apps.documents.urls_photos')),
    path('api/agent/', include('apps.agent.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom admin site configuration
admin.site.site_header = 'Sloth AI Agent Administration'
admin.site.site_title = 'Sloth Admin'
admin.site.index_title = 'Welcome to Sloth AI Platform'

"""
URL configuration for orphanage_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.core.views import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/children/', include('apps.children.urls')),
    path('api/v1/donations/', include('apps.donations.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/planning/', include('apps.planning.urls')),
    path('api/v1/families/', include('apps.families.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/core/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler400 = 'apps.core.views.bad_request'
handler403 = 'apps.core.views.permission_denied'
# handler404 = 'apps.core.views.page_not_found'
handler500 = 'apps.core.views.server_error'

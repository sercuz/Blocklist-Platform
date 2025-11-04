from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_key_views import APIKeyViewSet
from .log_views import ApiLogView

# Set up the router for viewsets
router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('login/', views.LoginView.as_view(), name='login'),
    
    # API logs endpoint
    path('api-logs/', ApiLogView.as_view(), name='api-logs'),
    
    # Blocklist management endpoints
    path('block/', views.BlockIndicatorView.as_view(), name='block'),
    path('unblock/', views.UnblockIndicatorView.as_view(), name='unblock'),
    path('blocklist/', views.BlocklistView.as_view(), name='blocklist'),
    path('logs/', views.LogsView.as_view(), name='logs'),
    
    # Direct access to blocklist files (authenticated JSON)
    path('ip-blocklist/', views.IPBlocklistView.as_view(), name='ip-blocklist'),
    path('domain-blocklist/', views.DomainBlocklistView.as_view(), name='domain-blocklist'),
    path('url-blocklist/', views.URLBlocklistView.as_view(), name='url-blocklist'),
    
    # Direct access to blocklist files (raw text, no auth)
    path('raw/ip-blocklist/', views.RawIPBlocklistView.as_view(), name='raw-ip-blocklist'),
    path('raw/domain-blocklist/', views.RawDomainBlocklistView.as_view(), name='raw-domain-blocklist'),
    path('raw/url-blocklist/', views.RawURLBlocklistView.as_view(), name='raw-url-blocklist'),
]

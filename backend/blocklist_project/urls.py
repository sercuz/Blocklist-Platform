from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.token_views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from api.root_views import api_root, terms_of_service, license_view

schema_view = get_schema_view(
   openapi.Info(
      title="Blocklist API",
      default_version='v1',
      description="API for managing blocklists of IPs, domains, and URLs. A security tool for legitimate cybersecurity operations.",
      terms_of_service="/terms-of-service",
      contact=openapi.Contact(email="alwaleedabosaq@gmail.com"),
      license=openapi.License(name="BSD 4-Clause License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', api_root, name='api-root'),  # Root endpoint
    path('terms-of-service', terms_of_service, name='terms-of-service'),
    path('license', license_view, name='license'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger documentation URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Custom error handlers
handler404 = 'api.root_views.custom_404_handler'
handler500 = 'api.root_views.custom_500_handler'

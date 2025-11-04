from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Permission, ContentType
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import APIKey
from .serializers import APIKeySerializer, APIKeyCreateSerializer
from .permissions import IsAdminUser

class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing API keys"""
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        request_body=APIKeyCreateSerializer,
        responses={
            201: APIKeySerializer,
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = APIKeyCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Generate a random API key
            key = get_random_string(length=40)
            
            # Create the API key
            api_key = APIKey.objects.create(
                key=key,
                name=serializer.validated_data['name'],
                user=request.user,
                read_only=serializer.validated_data.get('read_only', True)
            )
            
            # Ensure the user has the necessary permissions
            self._ensure_permissions_exist()
            
            # Return the created API key
            return Response(
                APIKeySerializer(api_key).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        responses={200: "API key regenerated", 404: "Not found"}
    )
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        try:
            api_key = self.get_queryset().get(pk=pk)
        except APIKey.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a new key
        api_key.key = get_random_string(length=40)
        api_key.save()
        
        return Response(APIKeySerializer(api_key).data)
    
    def _ensure_permissions_exist(self):
        """Ensure that all the necessary permissions exist in the database"""
        content_type, _ = ContentType.objects.get_or_create(app_label='api', model='blocklist')
        
        # Create permissions if they don't exist
        permissions_to_create = [
            ('view_blocklist', 'Can view blocklist'),
            ('add_blocklist', 'Can add to blocklist'),
            ('delete_blocklist', 'Can delete from blocklist'),
            ('view_logs', 'Can view logs'),
        ]
        
        for codename, name in permissions_to_create:
            Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )

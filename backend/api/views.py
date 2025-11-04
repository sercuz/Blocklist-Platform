from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.conf import settings
import os
from datetime import datetime

from .serializers import IndicatorSerializer, BlocklistItemSerializer, LogEntrySerializer
from . import services
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .permissions import IsAuthenticatedOrHasApiKey, ApiKeyPermission, IsAdminUser

# Parameter schemas for Swagger documentation
indicator_type_param = openapi.Parameter(
    'indicator_type', 
    openapi.IN_QUERY, 
    description="Type of indicator (ip, domain, url)", 
    type=openapi.TYPE_STRING,
    enum=['ip', 'domain', 'url']
)

# Request body schemas
block_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['indicator_type', 'indicators', 'reason'],
    properties={
        'indicator_type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of indicator (ip, domain, url)", enum=['ip', 'domain', 'url']),
        'indicators': openapi.Schema(type=openapi.TYPE_STRING, description="Indicators to block (one per line)"),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, description="Reason for blocking"),
    }
)

unblock_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['indicator_type', 'indicators', 'reason'],
    properties={
        'indicator_type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of indicator (ip, domain, url)", enum=['ip', 'domain', 'url']),
        'indicators': openapi.Schema(type=openapi.TYPE_STRING, description="Indicators to unblock (one per line)"),
        'reason': openapi.Schema(type=openapi.TYPE_STRING, description="Reason for unblocking"),
    }
)

# Response schemas
blocklist_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'entries': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'indicator': openapi.Schema(type=openapi.TYPE_STRING),
                    'added_by': openapi.Schema(type=openapi.TYPE_STRING),
                    'added_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    'reason': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)

log_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'entries': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'action': openapi.Schema(type=openapi.TYPE_STRING),
                    'indicator_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'indicator': openapi.Schema(type=openapi.TYPE_STRING),
                    'reason': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)

block_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'blocked': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        'existing': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        'invalid': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)

unblock_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING),
        'unblocked': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        'not_found': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        'invalid': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
    }
)

class BlockIndicatorView(APIView):
    # Allow authenticated users, but check API key permissions
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        # Use READ_WRITE permission for API keys
        return ApiKeyPermission.READ_WRITE if hasattr(self.request, 'api_key') else 'api.add_blocklist'
    
    @swagger_auto_schema(
        operation_description="Block indicators",
        request_body=block_request_schema,
        responses={201: block_response_schema, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        if serializer.is_valid():
            indicator_type = serializer.validated_data['indicator_type']
            indicators_text = serializer.validated_data['indicators']
            reason = serializer.validated_data['reason']
            
            # Split the indicators by line
            indicators = [line.strip() for line in indicators_text.split('\n') if line.strip()]
            
            # Add indicators to blocklist
            result = services.add_to_blocklist(
                indicator_type, 
                indicators, 
                request.user.username, 
                reason
            )
            
            added_indicators = result['added']
            invalid_indicators = result['invalid']
            existing_indicators = result['existing']
            
            response_data = {
                'message': f'Added {len(added_indicators)} indicators to the {indicator_type} blocklist',
                'blocked': added_indicators
            }
            
            # Add invalid indicators to the response if any
            if invalid_indicators:
                response_data['invalid'] = invalid_indicators
                response_data['message'] += f', {len(invalid_indicators)} indicators were invalid'
            
            # Add existing indicators to the response if any
            if existing_indicators:
                response_data['existing'] = existing_indicators
                response_data['message'] += f', {len(existing_indicators)} indicators already exist in the blocklist'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnblockIndicatorView(APIView):
    # Allow authenticated users, but check API key permissions
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        # Use READ_WRITE permission for API keys
        return ApiKeyPermission.READ_WRITE if hasattr(self.request, 'api_key') else 'api.delete_blocklist'
    
    @swagger_auto_schema(
        operation_description="Unblock indicators",
        request_body=unblock_request_schema,
        responses={200: unblock_response_schema, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        if serializer.is_valid():
            indicator_type = serializer.validated_data['indicator_type']
            indicators_text = serializer.validated_data['indicators']
            reason = serializer.validated_data['reason']
            
            # Split the indicators by line
            indicators = [line.strip() for line in indicators_text.split('\n') if line.strip()]
            
            # Remove indicators from blocklist
            result = services.remove_from_blocklist(
                indicator_type, 
                indicators, 
                request.user.username, 
                reason
            )
            
            removed_indicators = result['removed']
            non_existent_indicators = result['non_existent']
            
            response_data = {
                'message': f'Removed {len(removed_indicators)} indicators from the {indicator_type} blocklist',
                'unblocked': removed_indicators
            }
            
            # Add non-existent indicators to the response if any
            if non_existent_indicators:
                response_data['not_found'] = non_existent_indicators
                response_data['message'] += f', {len(non_existent_indicators)} indicators were not found in the blocklist'
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlocklistView(APIView):
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        return ApiKeyPermission.READ_ONLY if method == 'GET' else ApiKeyPermission.READ_WRITE
    
    @swagger_auto_schema(
        operation_description="Get all blocklist entries",
        manual_parameters=[indicator_type_param],
        responses={200: blocklist_response_schema}
    )
    def get(self, request):
        try:
            # Get all blocklist items
            blocklist_items = services.read_all_blocklists()
            
            # Filter by indicator type if provided
            indicator_type = request.query_params.get('indicator_type')
            if indicator_type:
                blocklist_items = [item for item in blocklist_items if item.get('type') == indicator_type]
            
            # Get log entries to enrich blocklist items with metadata
            logs = services.read_logs()
            
            # Create a mapping of indicator to its latest log entry
            indicator_logs = {}
            for log in logs:
                # Only consider BLOCK actions
                if log.get('action') == 'BLOCK':
                    # Create a key using indicator_type and indicator
                    key = f"{log.get('indicator_type')}:{log.get('indicator')}"
                    # Store the log entry or update if this is newer
                    if key not in indicator_logs or log.get('timestamp', '') > indicator_logs[key].get('timestamp', ''):
                        indicator_logs[key] = log
            
            # Enrich blocklist items with metadata from logs
            formatted_items = []
            for item in blocklist_items:
                # Create a key to look up in the logs
                key = f"{item.get('type')}:{item.get('indicator')}"
                
                # Start with default values
                formatted_item = {
                    'indicator': item.get('indicator', ''),
                    'type': item.get('type', ''),
                    'added_by': 'Unknown',
                    'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'reason': 'Unknown reason'
                }
                
                # Update with actual values from logs if available
                if key in indicator_logs:
                    log = indicator_logs[key]
                    formatted_item['added_by'] = log.get('username', 'Unknown')
                    formatted_item['added_at'] = log.get('timestamp', formatted_item['added_at'])
                    formatted_item['reason'] = log.get('reason', 'Unknown reason')
                
                formatted_items.append(formatted_item)
            
            # Sort by timestamp in descending order (newest first)
            formatted_items.sort(key=lambda x: x.get('added_at', ''), reverse=True)
            
            # Return the items directly
            return Response(formatted_items)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogsView(APIView):
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        return ApiKeyPermission.READ_ONLY if method == 'GET' else ApiKeyPermission.READ_WRITE
    
    @swagger_auto_schema(
        operation_description="Get audit logs",
        manual_parameters=[indicator_type_param],
        responses={200: log_response_schema}
    )
    def get(self, request):
        # Get logs from the log file
        try:
            logs = services.get_logs()
            
            # Filter by indicator type if provided
            indicator_type = request.query_params.get('indicator_type')
            if indicator_type:
                logs = [log for log in logs if log.get('indicator_type') == indicator_type]
            
            # Ensure we're returning a valid JSON array
            if not isinstance(logs, list):
                logs = []
                
            # Return logs directly as an array, not nested in an 'entries' field
            return Response(logs, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IPBlocklistView(APIView):
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        return 'api.view_blocklist'
    
    @swagger_auto_schema(
        operation_description="Get IP blocklist",
        responses={200: "List of IP addresses"}
    )
    def get(self, request, format=None):
        # Read the IP blocklist file
        try:
            with open(settings.IP_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return Response(content.splitlines())
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DomainBlocklistView(APIView):
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        return 'api.view_blocklist'
    
    @swagger_auto_schema(
        operation_description="Get domain blocklist",
        responses={200: "List of domains"}
    )
    def get(self, request, format=None):
        # Read the domain blocklist file
        try:
            with open(settings.DOMAIN_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return Response(content.splitlines())
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class URLBlocklistView(APIView):
    permission_classes = [IsAuthenticatedOrHasApiKey]
    
    def get_permission_required(self, method):
        return 'api.view_blocklist'
    
    @swagger_auto_schema(
        operation_description="Get URL blocklist",
        responses={200: "List of URLs"}
    )
    def get(self, request, format=None):
        # Read the URL blocklist file
        try:
            with open(settings.URL_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return Response(content.splitlines())
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Raw file download views (no authentication required for direct integration with other systems)
class RawIPBlocklistView(APIView):
    permission_classes = []
    
    @swagger_auto_schema(
        operation_description="Get raw IP blocklist (no authentication required)",
        responses={200: "Raw text file with one IP per line"}
    )
    def get(self, request, format=None):
        # Serve the raw IP blocklist file
        try:
            with open(settings.IP_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/plain')
        except Exception as e:
            return HttpResponse(str(e), status=500, content_type='text/plain')

class RawDomainBlocklistView(APIView):
    permission_classes = []
    
    @swagger_auto_schema(
        operation_description="Get raw domain blocklist (no authentication required)",
        responses={200: "Raw text file with one domain per line"}
    )
    def get(self, request, format=None):
        # Serve the raw domain blocklist file
        try:
            with open(settings.DOMAIN_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/plain')
        except Exception as e:
            return HttpResponse(str(e), status=500, content_type='text/plain')

class RawURLBlocklistView(APIView):
    permission_classes = []
    
    @swagger_auto_schema(
        operation_description="Get raw URL blocklist (no authentication required)",
        responses={200: "Raw text file with one URL per line"}
    )
    def get(self, request, format=None):
        # Serve the raw URL blocklist file
        try:
            with open(settings.URL_BLOCKLIST_FILE, 'r') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/plain')
        except Exception as e:
            return HttpResponse(str(e), status=500, content_type='text/plain')

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('django')

class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for user: {username}")
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Generate tokens manually
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            # Add custom claims
            refresh['username'] = user.username
            refresh['is_staff'] = user.is_staff
            
            logger.info(f"Login successful for user: {username}")
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'is_staff': user.is_staff
            })
        else:
            logger.warning(f"Login failed for user: {username}")
            return Response({'error': 'Invalid credentials'}, 
                            status=status.HTTP_401_UNAUTHORIZED)

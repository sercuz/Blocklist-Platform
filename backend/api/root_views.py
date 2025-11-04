from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import os


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root endpoint - provides information about available endpoints
    """
    return Response({
        'message': 'Blocklist Platform API',
        'version': '1.0',
        'description': 'A security tool for managing blocklists of potentially malicious indicators of compromise (IOCs).',
        'license': {
            'name': 'BSD 4-Clause License',
            'url': '/license'
        },
        'terms_of_service': '/terms-of-service',
        'contact': 'alwaleedabosaq@gmail.com',
        'endpoints': {
            'authentication': {
                'login': '/api/token/',
                'refresh': '/api/token/refresh/',
            },
            'blocklist_management': {
                'block_indicators': '/api/block/',
                'unblock_indicators': '/api/unblock/',
                'view_all_blocklists': '/api/blocklist/',
                'ip_blocklist': '/api/ip-blocklist/',
                'domain_blocklist': '/api/domain-blocklist/',
                'url_blocklist': '/api/url-blocklist/',
            },
            'raw_blocklists': {
                'ip_blocklist': '/api/raw/ip-blocklist/',
                'domain_blocklist': '/api/raw/domain-blocklist/',
                'url_blocklist': '/api/raw/url-blocklist/',
            },
            'logs': {
                'audit_logs': '/api/logs/',
            },
            'api_keys': {
                'manage_keys': '/api/api-keys/',
            },
            'documentation': {
                'swagger': '/swagger/',
                'redoc': '/redoc/',
            }
        },
        'important_notice': 'This service is intended solely for legitimate cybersecurity purposes. Misuse is strictly prohibited and may result in legal action.',
        'note': 'All endpoints except raw blocklists require authentication.'
    })


def custom_404_handler(request, exception=None):
    """
    Custom 404 handler that returns JSON response without exposing sensitive information
    """
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404,
        'available_endpoints': {
            'api_root': '/',
            'api': '/api/',
            'documentation': '/swagger/',
        }
    }, status=404)


def custom_500_handler(request):
    """
    Custom 500 handler that returns JSON response without exposing sensitive information
    """
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.',
        'status_code': 500
    }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def terms_of_service(request):
    """
    Serve the Terms of Service document
    """
    try:
        # Get the path to the TERMS_OF_SERVICE.md file
        base_dir = settings.BASE_DIR.parent
        tos_path = os.path.join(base_dir, 'TERMS_OF_SERVICE.md')
        
        if os.path.exists(tos_path):
            with open(tos_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/markdown')
        else:
            return Response({
                'error': 'Terms of Service document not found',
                'contact': 'alwaleedabosaq@gmail.com'
            }, status=404)
    except Exception as e:
        return Response({
            'error': 'Unable to load Terms of Service',
            'contact': 'alwaleedabosaq@gmail.com'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def license_view(request):
    """
    Serve the LICENSE file
    """
    try:
        # Get the path to the LICENSE file
        base_dir = settings.BASE_DIR.parent
        license_path = os.path.join(base_dir, 'LICENSE')
        
        if os.path.exists(license_path):
            with open(license_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/plain')
        else:
            return Response({
                'error': 'License file not found',
                'license': 'BSD 4-Clause License',
                'contact': 'alwaleedabosaq@gmail.com'
            }, status=404)
    except Exception as e:
        return Response({
            'error': 'Unable to load license',
            'license': 'BSD 4-Clause License',
            'contact': 'alwaleedabosaq@gmail.com'
        }, status=500)

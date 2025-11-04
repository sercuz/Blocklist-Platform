import json
import time
import logging
from django.utils import timezone

logger = logging.getLogger('api_calls')

class APICallLoggingMiddleware:
    """Middleware to log all API calls with detailed information."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip logging for static files and admin
        if request.path.startswith(('/static/', '/admin/')):
            return self.get_response(request)
            
        # Start timer
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # End timer
        duration = time.time() - start_time
        
        # Get user information
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        
        # Get API key information if available
        api_key = getattr(request, 'api_key_name', '') if hasattr(request, 'api_key_name') else ''
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        # Create log entry
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'user': user,
            'status_code': response.status_code,
            'duration': f"{duration:.4f}s",
            'api_key': api_key,
            'ip': ip,
            'query_params': dict(request.GET.items()),
            'request_body': self._get_request_body(request),
            'response_size': len(response.content) if hasattr(response, 'content') else 0,
        }
        
        # Log as JSON
        logger.info(f"API Call: {json.dumps(log_data)}")
        
        return response
    
    def _get_request_body(self, request):
        """Safely extract request body if possible."""
        try:
            if request.body and len(request.body) > 0:
                body = json.loads(request.body)
                # Remove sensitive data
                if 'password' in body:
                    body['password'] = '***'
                return body
        except Exception:
            pass
        return {}

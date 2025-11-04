from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    """Custom authentication using API keys"""
    
    keyword = 'ApiKey'
    
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth:
            return None
        
        parts = auth.split()
        if parts[0].lower() != self.keyword.lower():
            # If not API key auth, let other auth methods handle it
            return None
            
        if len(parts) != 2:
            msg = _('Invalid API key header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        
        key = parts[1]
        return self.authenticate_credentials(key, request)
    
    def authenticate_credentials(self, key, request):
        try:
            api_key = APIKey.objects.get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid API key.'))
        
        # Store API key in request for permission checking
        request.api_key = api_key
        
        # Create a custom user-like object that delegates permission checks to the API key
        user = api_key.user
        
        # Add the has_perm method to check permissions based on API key's read_only status
        user.api_key_has_perm = api_key.has_perm
        
        return (user, api_key)
    
    def authenticate_header(self, request):
        return self.keyword

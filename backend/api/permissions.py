from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.contrib.auth.models import Permission, ContentType

class ReadOnly(BasePermission):
    """Allow read-only access"""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class IsAdminUser(BasePermission):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class ApiKeyPermission(BasePermission):
    """Permission class for API key authentication that respects Django permissions"""
    # Constants for permission types
    READ_ONLY = 'read_only'
    READ_WRITE = 'read_write'
    
    def has_permission(self, request, view):
        # Check if authenticated with API key
        if hasattr(request, 'api_key'):
            # Get the permission codename for this view
            if hasattr(view, 'get_permission_required'):
                perm = view.get_permission_required(request.method)
                # Handle our custom permission constants
                if perm == self.READ_ONLY:
                    return request.method in SAFE_METHODS
                elif perm == self.READ_WRITE:
                    return request.method in SAFE_METHODS if request.api_key.read_only else True
                else:
                    # Use the API key's has_perm method for Django permissions
                    return request.user.api_key_has_perm(perm)
            # If no specific permission is required, use the read_only flag
            return request.method in SAFE_METHODS if request.api_key.read_only else True
        # Not authenticated with API key
        return False

class IsAuthenticatedOrHasApiKey(BasePermission):
    """Allow access to authenticated users or API key holders with appropriate permissions"""
    def has_permission(self, request, view):
        # Check if user is authenticated via session/token
        has_user_auth = IsAuthenticated().has_permission(request, view)
        
        # For API key authentication, check permissions
        if hasattr(request, 'api_key'):
            # Get the permission codename for this view
            if hasattr(view, 'get_permission_required'):
                perm = view.get_permission_required(request.method)
                # Handle our custom permission constants
                if perm == ApiKeyPermission.READ_ONLY:
                    return request.method in SAFE_METHODS
                elif perm == ApiKeyPermission.READ_WRITE:
                    return request.method in SAFE_METHODS if request.api_key.read_only else True
                else:
                    # Use the API key's has_perm method for Django permissions
                    return request.user.api_key_has_perm(perm)
            # If no specific permission is required, use the read_only flag
            return request.method in SAFE_METHODS if request.api_key.read_only else True
        
        # For regular authentication, check if user has appropriate permissions
        if has_user_auth and hasattr(view, 'get_permission_required'):
            perm = view.get_permission_required(request.method)
            # Skip permission check for our custom constants
            if perm in [ApiKeyPermission.READ_ONLY, ApiKeyPermission.READ_WRITE]:
                return True
            return request.user.has_perm(perm)
        
        # Allow if authenticated (and no specific permission is required)
        return has_user_auth

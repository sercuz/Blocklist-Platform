from django.db import models
from django.contrib.auth.models import User, Permission
import uuid

# Note: We're not using database models for this implementation
# as per requirements, we'll be using flat files for storage

class APIKey(models.Model):
    key = models.CharField(max_length=64, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    read_only = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def has_perm(self, perm):
        """Check if the associated user has the specified permission"""
        if self.read_only and not perm.startswith('view_'):
            return False
        return self.user.has_perm(perm)

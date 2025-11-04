from rest_framework import serializers
from django.contrib.auth.models import User
from .models import APIKey

class IndicatorSerializer(serializers.Serializer):
    indicator_type = serializers.CharField(max_length=10)
    indicators = serializers.CharField()
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)

class BlocklistItemSerializer(serializers.Serializer):
    indicator = serializers.CharField()
    added_by = serializers.CharField()
    added_at = serializers.CharField()
    reason = serializers.CharField()

class LogEntrySerializer(serializers.Serializer):
    timestamp = serializers.CharField()
    username = serializers.CharField()
    action = serializers.CharField()
    indicator_type = serializers.CharField()
    indicator = serializers.CharField()
    reason = serializers.CharField()

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'key', 'name', 'created_at', 'is_active', 'read_only']
        read_only_fields = ['id', 'key', 'created_at']

class APIKeyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['name', 'read_only']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']
        read_only_fields = ['id', 'is_staff']

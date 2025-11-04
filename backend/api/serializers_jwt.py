from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

logger = logging.getLogger('django')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        
        return token
        
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            
            # Add extra responses like user info
            data['username'] = self.user.username
            data['is_staff'] = self.user.is_staff
            
            logger.info(f"Token validated successfully for user: {self.user.username}")
            return data
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise

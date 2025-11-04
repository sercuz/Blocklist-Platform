from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
import logging
from .serializers_jwt import CustomTokenObtainPairSerializer

logger = logging.getLogger('django')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Token request received: {request.data}")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Token response: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Token error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

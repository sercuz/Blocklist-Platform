import os
import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.conf import settings

logger = logging.getLogger('django')

class ApiLogView(APIView):
    """View to retrieve API call logs"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            # Use the debug.log file instead of api_calls.log
            log_file = os.path.join(settings.BASE_DIR, 'debug.log')
            
            # Check if log file exists
            if not os.path.exists(log_file):
                logger.warning(f"Log file not found at {log_file}")
                return Response([], status=status.HTTP_200_OK)
            
            # Read log file
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
            
            # Parse JSON logs
            logs = []
            for line in log_lines:
                try:
                    # Extract the JSON part from the log line
                    # Format is typically: INFO YYYY-MM-DD HH:MM:SS middleware API Call: {"json": "data"}
                    if 'API Call:' in line:
                        json_start = line.find('API Call:') + 10  # Length of 'API Call: '
                        if json_start != -1 and json_start < len(line):
                            json_data = line[json_start:].strip()
                            log_entry = json.loads(json_data)
                            logs.append(log_entry)
                except Exception as e:
                    # Skip malformed log entries
                    logger.debug(f"Skipping malformed log entry: {e}")
                    continue
            
            # Sort logs by timestamp (newest first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limit to the most recent 100 logs
            logs = logs[:100]
            
            logger.info(f"Retrieved {len(logs)} API logs")
            return Response(logs, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to retrieve API logs: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve API logs: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from datetime import datetime
import logging

# the middleware to log the incoming request and response
class RequestResponseLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # initialize two loggers, one for request and one for response
        self.request_logger = logging.getLogger('request_logger')
        self.response_logger = logging.getLogger('response_logger')

    def __call__(self, request):
        # Log the incoming request
        request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = request.user if request.user.is_authenticated else 'Anonymous User'
        # self.request_logger.info(f"Request at {request_time} by {user}: {request.method} {request.path}")

        # Continue with the request processing
        response = self.get_response(request)

        # Log the corresponding response details
        response_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response_content = response.content.decode('utf-8') if response.has_header('Content-Type') and 'text' in \
                                                               response['Content-Type'] else '[Binary Content]'
        # self.response_logger.info(
        #     f"Response at {response_time} for {request.method} by {user}: {request.path}:Status Code: {response.status_code}")

        return response
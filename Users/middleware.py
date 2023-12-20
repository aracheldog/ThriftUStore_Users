from datetime import datetime
import logging
from google.cloud import storage


# the middleware to log the incoming request and response
class RequestResponseLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.bucket_name = 'thriftstore_log'

        # initialize two loggers, one for request and one for response
        self.request_logger = logging.getLogger('request_logger')
        self.response_logger = logging.getLogger('response_logger')

    def __call__(self, request):
        # Log the incoming request
        request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = request.user if request.user.is_authenticated else 'Anonymous User'
        self.write_to_cloud_storage('requests_test.log', 'requests_new.log',
                                    f"Request at {request_time} by {user}: {request.method} {request.path}\n")

        # Continue with the request processing
        response = self.get_response(request)

        # Log the corresponding response details
        response_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Write logs to Cloud Storage
        self.write_to_cloud_storage('responses_test.log','responses_new.log' ,f"Response at {response_time} for {request.method} by {user}: {request.path}, Status Code: {response.status_code}\n")

        return response

    def write_to_cloud_storage(self, filename, destination_blob_name, content):

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(filename)

        # # Download existing content if the blob exists
        # if blob.exists():
        #     current_content = blob.download_as_text()
        # else:
        #     current_content = ''
        # # Append the new content to the existing content
        # updated_content = current_content + content
        # # Upload the updated content
        # blob.upload_from_string(updated_content, content_type='text/plain')

        # check if the blob exist
        if blob.exists():

            # Create a new blob with the updated content
            updated_content = content
            updated_blob = bucket.blob(f"{filename}_updated")
            updated_blob.upload_from_string(updated_content, content_type='text/plain')
            # Compose the existing blob and the new blob
            blob.compose([blob, updated_blob])
            updated_blob.delete()
        else:
            blob.upload_from_string(content, content_type='text/plain')





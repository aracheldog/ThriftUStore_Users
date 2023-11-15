import os


from django.dispatch import Signal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Users.models import User

from google.cloud import pubsub_v1

from smartystreets_python_sdk import SharedCredentials, StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from smartystreets_python_sdk.us_street.match_type import MatchType
from datetime import datetime
import json


class UserRegistrationView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # check if the email and password is presented
        if not email or not password:
            return Response({'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)

        # check if email already in use
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user address details from the registration form
        address = request.POST.get('address')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        if address and state and zip_code:
        # Run SmartyStreets address validation
            is_valid_address = validate_address(address, zip_code, state)
            if not is_valid_address:
                return Response({'error': 'Address is not valid!'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(email=email, password=password, address = address, state = state, zip_code=zip_code)
        else:
            user = User.objects.create_user(email=email, password=password)

        # send user registered signal
        user_registered_signal.send(sender=self.__class__, user=user)

        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


def validate_address(address, zip_code, state):
    key = os.environ['SMARTY_AUTH_WEB']
    hostname = os.environ['SMARTY_WEBSITE_DOMAIN']
    credentials = SharedCredentials(key, hostname)

    client = ClientBuilder(credentials).with_licenses(["us-core-cloud"]).build_us_street_api_client()
    lookup = StreetLookup()
    lookup.street = address
    lookup.state = state
    lookup.zipcode = zip_code

    lookup.match = MatchType.STRICT

    try:
        client.send_lookup(lookup)
    except exceptions.SmartyException as err:
        print(err)
        return False

    result = lookup.result
    if result:

        print(result[0].components.street_name)
        print(result[0].components.zipcode)
    return bool(result)  # Returns True if there is at least one valid candidate

user_registered_signal = Signal()

# Connect a function to the signal to publish to Google Pub/Sub
def user_registered_handler(sender, **kwargs):
    user = kwargs['user']
    publish_to_pubsub(user.email)

user_registered_signal.connect(user_registered_handler)
def publish_to_pubsub(email):
    # Set topic path
    topic_path = 'projects/user-microservice-402518/topics/UserMicroRegisterationTopic'

    # Create Pub/Sub Publisher client
    publisher = pubsub_v1.PublisherClient()



    # Build message
    message_data = {
        'event_type': 'user_registered',
        'user_email': email,
        'registration_time': datetime.now().isoformat(),
    }
    message_str = json.dumps(message_data).encode('utf-8')

    # Publish message
    future = publisher.publish(topic_path, data=message_str)
    future.result()

    print(f'Message published to {topic_path}.')
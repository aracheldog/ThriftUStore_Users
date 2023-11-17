from datetime import datetime
import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.dispatch import Signal
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from google.cloud import pubsub_v1
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from Users.models import User
from .serializers import UserSerializer


from smartystreets_python_sdk import SharedCredentials, StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from smartystreets_python_sdk.us_street.match_type import MatchType
import os

from .utils.jwt import generate_jwt



def google_login_callback(request):
    # Get the authorization code from the query parameters
    authorization_code = request.GET.get('code')
    # Google OAuth token endpoint
    token_url = 'https://oauth2.googleapis.com/token'
    # Your Google OAuth client ID and secret
    client_id = '258239284713-8nb3h72ebnp38b2a1i093t6fd2og177p.apps.googleusercontent.com'
    client_secret = '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'
    redirect_uri = 'http://localhost:8000/users/google/login/callback/'
    # redirect_uri = 'https://user-microservice-402518.ue.r.appspot.com/users/google/login/callback/'
    # Prepare the data for the POST request to exchange the code for an access token
    data = {
        'code': authorization_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }
    # Make the POST request to the token endpoint
    response = requests.post(token_url, data=data)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to get the access token
        access_token = response.json().get('access_token')
        id_token = response.json().get('id_token')
        print(response.json())
        print("Access Token:", access_token)
        print("ID token: ", id_token)
        return redirect('hello_url')
    else:
        # Handle the error case
        print("Error exchanging code for access token:", response.text)
        return HttpResponse("Error retrieving access token.", status=response.status_code)


# Create your views here.
@api_view(["GET"])
def hello(request):
    if request.method == "GET":
        return Response(data="Hello from users API", status=status.HTTP_200_OK)




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

class UserSignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # add customized data to token
            personalized_claims = {
                "user_email": email,
            }
            # generate the token by using the google service account
            token = generate_jwt(sa_keyfile="user-microservice-apigw.json" ,personalized_claims=personalized_claims)
            login(request, user)
            return Response({'access_token': str(token)}, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self,request):
        return Response(data="Hello from users API", status=status.HTTP_200_OK)

class UserSignOutView(APIView):
    # check if user already logged in, otherwise will not have access to this api

    def post(self,request):
        logout(request)
        return Response({'detail': 'You have been logged out successfully.'}, status=status.HTTP_200_OK)

class UserProfileView(APIView):

    def get(self,request):
        user = request.user
        print(user)
        serializer = UserSerializer(user)
        user_json = JSONRenderer().render(serializer.data)
        return HttpResponse(user_json, content_type='application/json')



class UserDeleteView(APIView):

    def delete(self, request):
        user = request.user
        print(user)
        # if user exists, delete user
        if user:
            user.delete()
            logout(request)  # logout
            messages.success(request, 'Your account has been deleted.')
            return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)



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

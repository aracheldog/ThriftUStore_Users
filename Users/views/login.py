from django.contrib.auth import authenticate, logout, login
from django.shortcuts import redirect
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from Users.utils.jwt import generate_jwt
import requests


@api_view(["GET"])
def hello(request):
    if request.method == "GET":
        return Response(data="Hello from users API", status=status.HTTP_200_OK)

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
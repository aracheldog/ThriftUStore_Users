from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render, get_object_or_404, reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from google.oauth2 import id_token

from Users.serializers import UserSerializer
from Users.utils.jwt import generate_jwt



@api_view(["GET"])
def hello(request):
    # Print request GET parameters
    if request.method == "GET":
        # check if there is a bearer token in the request
        # if there is a bearer token, then return the JWT token
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            data = {'token': token}
            return Response(data = data, status=status.HTTP_200_OK)
        elif request.user.is_authenticated:
            token = request.session.get('token', {})
            data = {'token': token}
            return Response(data = data, status=status.HTTP_200_OK)
        # return the response when there is no bearer token in the request
        return Response(data="Hello from users API, you are not logged in, no token to retrieve", status=status.HTTP_200_OK)



# This is the user sign in view for logging in via email and password
class UserSignInView(APIView):
    # post method to sign in via user email and password
    def post(self, request):
        # retrieve the email and password from the request
        email = request.data.get('email')
        password = request.data.get('password')
        # authenticate the identity of the user via email and password
        user = authenticate(request, username=email, password=password)
        # log in successfully
        if user is not None:
            # generate extra fields to included in the JWT token
            personalized_claims = generate_token_claim(user.id)
            # generate the token by using the Google service account with extra fields generated before
            token = generate_jwt(sa_keyfile="user-microservice-apigw.json" ,personalized_claims=personalized_claims)
            login(request, user)
            return Response({'access_token': str(token)}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    # A simple test view
    def get(self,request):
        return Response(data="Hello from users API", status=status.HTTP_200_OK)


# A help function to generate extra data to included to the JWT token
def generate_token_claim(user_id):
    # find the user and use the serializer to retrieve the user info
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    basic_data= serializer.data
    # add social access token to the JWT token
    # check if the current login user has a social account associated with the user or not
    social_account = SocialAccount.objects.filter(user_id=user.id).first()
    if social_account:
        social_token = SocialToken.objects.filter(account_id=social_account.id).first()
        basic_data.update({"access_token": social_token.token})
    else:
        basic_data.update({"access_token": None})
    return basic_data


# This is the view for generating the JWT token when logging in via Google Oauth2
class GoogleOauthJwtView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        # get the user and the corresponding social account info
        user = request.user
        social_account = SocialAccount.objects.get(user_id=user.id)
        name = social_account.extra_data["name"]

        # update the username in the social account
        user.full_name = name
        user.save()
        # generate the personalized the data to encapsulate into the JWT token
        personalized_claims = generate_token_claim(user.id)
        token = generate_jwt(sa_keyfile="user-microservice-apigw.json", personalized_claims=personalized_claims)
        print("personalized claim info is: ", personalized_claims)
        print("generated jwt token after google oath2 is: ", token)
        request.session['token'] = token
        request.session["access_token"] = personalized_claims['access_token']
        return redirect("hello_url")


class ApiGWGoogleView(APIView):
    def get(self, request):
        return redirect("https://user-microservice-402518.ue.r.appspot.com/users/google/login/")






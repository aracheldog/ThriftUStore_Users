from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib.auth.decorators import login_required
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
        if request.user.is_authenticated:
            token = request.session.get('token', {})
            data = {'token': token}
            return Response(data = data, status=status.HTTP_200_OK)
        return Response(data="Hello from users API, you are not logged in, no token to retrieve", status=status.HTTP_200_OK)
        # return render(request, 'hello.html')

class UserSignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # add customized data to token
            personalized_claims = generate_token_claim(user.id)
            # generate the token by using the google service account
            token = generate_jwt(sa_keyfile="user-microservice-apigw.json" ,personalized_claims=personalized_claims)
            login(request, user)
            return Response({'access_token': str(token)}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self,request):
        return Response(data="Hello from users API", status=status.HTTP_200_OK)

@method_decorator(login_required)
def generate_token_claim(user_id):

    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    basic_data= serializer.data
    social_token = SocialToken.objects.get(account__user=user, account__provider="google")
    basic_data.update({"access_token": social_token.token})
    return basic_data

class GoogleOauthJwtView(APIView):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        social_account = SocialAccount.objects.get(user=user)
        name = social_account.extra_data["name"]
        user.full_name = name
        user.save()
        personalized_claims = generate_token_claim(user.id)

        token = generate_jwt(sa_keyfile="user-microservice-apigw.json", personalized_claims=personalized_claims)
        print(personalized_claims)
        request.session['token'] = token
        request.session["access_token"] = personalized_claims['access_token']
        return redirect("hello_url")










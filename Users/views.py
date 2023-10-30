from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from Users.models import User
from .serializers import UserSerializer



# Create your views here.
@api_view(["GET"])
@permission_classes([IsAuthenticated])
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

        user = User.objects.create_user(email=email, password=password)
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

class UserSignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            token = AccessToken.for_user(user)
            return Response({'access_token': str(token)}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserSignOutView(APIView):
    # check if user already logged in, otherwise will not have access to this api
    permission_classes = [IsAuthenticated]

    def post(self,request):
        messages.success(request, 'You have been logged out.')
        return redirect('hello_url')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        user_json = JSONRenderer().render(serializer.data)
        return HttpResponse(user_json, content_type='application/json')






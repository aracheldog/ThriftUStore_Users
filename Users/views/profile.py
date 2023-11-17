from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from Users.decorators import check_access_token
from Users.serializers import UserSerializer
import google.auth.jwt



class UserProfileView(APIView):
    @method_decorator(check_access_token())
    def get(self,request):
        print(request.headers)
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            payload = google.auth.jwt.decode(token, verify=False)
            print("payload is: ", payload)
            User = get_user_model()
            user = get_object_or_404(User, id=payload["id"])
            serializer = UserSerializer(user)
            user_json = JSONRenderer().render(serializer.data)
            return HttpResponse(user_json, content_type='application/json')
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @method_decorator(check_access_token())
    def put(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            payload = google.auth.jwt.decode(token, verify=False)
            # check if user logs in via google oauth2
            if "user_id" not in payload:
                social_account = SocialAccount.objects.get(uid=payload['sub'])
                user_id = social_account.user_id
                payload["user_id"] = user_id

            User = get_user_model()
            user = get_object_or_404(User, id=payload["user_id"])
            serializer = UserSerializer(user, data=request.data, partial=True)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                user = get_object_or_404(User, id=payload["user_id"])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_401_UNAUTHORIZED)



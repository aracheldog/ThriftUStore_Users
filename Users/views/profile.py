from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from Users.serializers import UserSerializer


class UserProfileView(APIView):
    def get(self,request):
        user = request.user
        print(user)
        print(user.email)
        serializer = UserSerializer(user)
        user_json = JSONRenderer().render(serializer.data)
        return HttpResponse(user_json, content_type='application/json')
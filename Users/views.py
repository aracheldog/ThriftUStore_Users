from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@api_view(["GET"])
def hello(request):
    if request.method == "GET":
        return Response(data="Hello from users API", status=status.HTTP_200_OK)
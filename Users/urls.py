from django.urls import path, include
from Users import views

urlpatterns = [
    path("", views.hello, name="hello_url")
]
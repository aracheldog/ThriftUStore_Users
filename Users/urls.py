from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView

from Users import views
from Users.views import UserSignInView, UserRegistrationView, UserSignOutView, UserProfileView

urlpatterns = [
    path("", views.hello, name="hello_url"),
    path('users/sign_in/', UserSignInView.as_view(), name='sign_in'),
    path('users/sign_up/', UserRegistrationView.as_view(), name='sign_up'),
    path('users/sign_out/', UserSignOutView.as_view(), name='sign_out'),
    path('users/verify/', TokenVerifyView.as_view(), name='verify'),
    path('users/<int:user_id>/profile/', UserProfileView.as_view(), name='user_profile'),

]
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from Users.models import User


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:
            return
        else:
            user = User.objects.get(email=user.email)
            sociallogin.connect(request, user)
            sociallogin.state['process'] = 'login'
            sociallogin.state['user'] = user

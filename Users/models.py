from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

# Create your models here.
class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    avatar_url = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(default="", null=False)
    zip_code = models.CharField(max_length=255, default="", null=False)
    state = models.CharField(max_length=255, default="", null=False)
    country = models.CharField(max_length=255, default="", null=False)
    description = models.TextField(default="", null=False)

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
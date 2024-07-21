from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from user.managers import CustomUserManager
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    username = None
    REQUIRED_FIELDS = []

    email = models.EmailField(_("email address"), unique=True)
    profile_pic = models.ImageField(upload_to="Profile pictures", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=6, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    postal_code = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=255, default="available")


    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    
    def get_name(self):
        name = self.first_name if self.first_name else ""
        if self.last_name:
            name += " " + self.last_name
        return name
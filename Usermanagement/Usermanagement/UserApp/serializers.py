from django.contrib.auth.models import User
from AuthApp.models import Profile
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class ProfilePictureSerializer():
    class Meta:
        model = Profile
        fields = []
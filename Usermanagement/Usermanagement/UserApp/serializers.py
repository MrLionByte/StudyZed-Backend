from django.contrib.auth.models import User
from AuthApp.serializers import UserSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from class_management.class_teacher import models

# Create your views here.


class CreateClassView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = []


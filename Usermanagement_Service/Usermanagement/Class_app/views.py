from django.shortcuts import render
from rest_framework import generics


# Create your views here.


class StudentDetailsView(generics.RetrieveAPIView):
    pass
from django.shortcuts import render
from AuthApp.models import Profile
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    UploadProfilePictureSerializer, UploadCoverPictureSerializer,
    UpdatePhoneNumberSerializer, ProfileSerializer
    )
from .utils.cloudnary import upload_file_to_cloudinary
from .utils.response import api_response

# Create your views here.

## USER PROFILE PIC UPDATE {

class UploadAndUpdateProfilePicView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadProfilePictureSerializer
    
    def post(self, request):
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
        
            file = serializer.validated_data['file']
            user = request.user
            
            try:
                image_url = upload_file_to_cloudinary(
                    file = file,
                    folder_name='Home/STUDYZED/profile_picture',
                    public_id=f"{user}_profile_pic",
                    crop='fill',
                    width=300,
                    height=300,
                )
                
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.profile_picture = image_url
                profile.save()

                return api_response(
                    success=True, message="Profile picture updated successfully",
                    data=ProfileSerializer(profile).data, status_code = 200
                )
            except ValueError as e:
                return api_response(False, "Failed to update profile picture",
                                    data=str(e), status_code=500)
        return api_response(False, "Invalid Profile Pic data",
                            data=serializer.errors,status_code=400)
        

## USER PROFILE PIC UPDATE }


## USER COVERPHOTO UPDATE {

class UploadAndUpdateCoverPicView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadCoverPictureSerializer
    
    def post(self, request):
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            user = request.user
            
            try:
                image_url = upload_file_to_cloudinary(
                    file=file,
                    folder_name='Home/STUDYZED/cover_picture',
                    public_id=f"{user}_cover_picture",
                    )

                profile, _ = Profile.objects.get_or_create(user=user)
                profile.cover_picture = image_url
                profile.save()
                
                return api_response(
                    True, "Cover photo updated successfully",
                    data=ProfileSerializer(profile).data
                )
            except ValueError as e:
                return api_response(False, "Failed to update cover photo",
                                    data=str(e), status_code=500)
        return api_response(False, "Invalid photo data",
                            data=serializer.errors, status_code=400)

## USER SIGN-UP PROFILE UPDATE }


## USER SIGN-UP PROFILE UPDATE {


class UpdatePhoneNumberView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePhoneNumberSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            user = request.user
            
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()
            
            return api_response(
                True, "Phone number updated successfully",
                data=ProfileSerializer(profile).data
            )
        return api_response(
            False, "Invalid phone number data",
            data=serializer.errors, status_code=400)


## USER SIGN-UP PROFILE UPDATE }

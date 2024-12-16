from django.shortcuts import render
from AuthApp.models import Profile
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

# Create your views here.

## USER PROFILE PIC UPDATE {

class UploadAndUpdateProfilePicView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print("PROFILE PIC UPLOAD", request.data)
        user = request.user
        print("FILES :", request.FILES)
        file = request.FILES.get('file')  # `file` should match the key used in FormData
        print("Uploaded file:", file)
        try:
            cloudinary_response = upload(
                file,
                folder='Home/STUDYZED/profile_picture',
                public_id=f"{user}_Profile Pic",
                overwrite=True,
                crop='fill',
                width=300,
                height=300,
                )
            image_url = cloudinary_response['secure_url']
            profile, created = Profile.objects.get_or_create(user=user)
            profile.profile_picture = image_url
            profile.save()
            
            print("PROFILE :", profile)
            return Response({
                'message':f'{profile.profile_picture}',
                'user':f'{profile.user.username}',
            })
        except Exception as e:
            print("ERROR :", e)
    
    def get(request, *args, **kwargs):
        pass
        
        

## USER PROFILE PIC UPDATE }


## USER COVERPHOTO UPDATE {

class UploadAndUpdateCoverPicView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        print("COVER PIC UPLOAD", request.data)
        user = request.user
        print("FILES :", request.FILES)
        file = request.FILES.get('file')  # `file` should match the key used in FormData
        print("Uploaded file:", file)
        try:
            cloudinary_response = upload(
                file,
                folder='Home/STUDYZED/cover_picture',
                public_id=f"{user}_cover_picture",
                overwrite=True,
                # crop='fill',
                # width=300,
                # height=300,
                )
            image_url = cloudinary_response['secure_url']
            profile, created = Profile.objects.get_or_create(user=user)
            profile.cover_picture = image_url
            profile.save()
            
            print("PROFILE :", profile)
            return Response({
                'message':f'{profile.cover_picture}',
                'user':f'{profile.user.username}',
            })
        except Exception as e:
            print("ERROR :", e)

## USER SIGN-UP PROFILE UPDATE }


## USER SIGN-UP PROFILE UPDATE {


class UpdatePhoneNumberView(generics.GenericAPIView):
    
    def post(self, request):
        pass


## USER SIGN-UP PROFILE UPDATE }

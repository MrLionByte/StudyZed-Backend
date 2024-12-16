from django.urls import path
from .views import UploadAndUpdateProfilePicView, UploadAndUpdateCoverPicView


urlpatterns = [
    
    path("upload-profile-pic/", UploadAndUpdateProfilePicView.as_view(),
         name="upload_profile_pic"),
    path("upload-cover-pic/", UploadAndUpdateCoverPicView.as_view(),
         name="upload_cover_pic"),
    
    
]

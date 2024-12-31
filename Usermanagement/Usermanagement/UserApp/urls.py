from django.urls import path
from .views import *


urlpatterns = [
    path(
        "upload-profile-pic/",
        UploadAndUpdateProfilePicView.as_view(),
        name="upload_profile_pic",
    ),
    path(
        "upload-cover-pic/",
        UploadAndUpdateCoverPicView.as_view(),
        name="upload_cover_pic",
    ),
    path("user-profile/", UserAddonRetrieveView.as_view(), name="user-profile"),
    path("update-profile/", ProfileUpdateView.as_view(), name="update-profile"),
]

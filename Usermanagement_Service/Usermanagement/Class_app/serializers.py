from rest_framework import serializers
from AuthApp.models import UserAddon, Profile
from UserApp.serializers import ProfileSerializer

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Profile
        fields = ["profile_picture", "cover_picture", "phone", "user"]

class AllStudentsInAClassSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = UserAddon
        fields = [
            "id",
            "username",
            "email",
            "role",
            "user_code",
            "first_name",
            "last_name",
            "profile",
        ]
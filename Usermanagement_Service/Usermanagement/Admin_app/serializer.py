from AuthApp.models import UserAddon, Profile
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    role = serializers.CharField(required=True)  
    first_name = serializers.CharField(required=True) 
    last_name = serializers.CharField(required=False, allow_blank=True)  
    password = serializers.CharField(write_only=True,required=True) 
    
    class Meta:
        model = UserAddon
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
                      

class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):
        username = self.context['request'].data.get('username')
        password = attrs.get("password")
        print(username, password)
        try:
            user = UserAddon.objects.get(username=username)
            
            if not user.check_password(password):
                print("password error")
                raise serializers.ValidationError('Invalid password.')
            if not user.is_superuser:
                print("not admin error")
                raise serializers.ValidationError('User is not a admin.')
            attrs['user'] = user
            return super().validate(attrs)
        except UserAddon.DoesNotExist:
            raise serializers.ValidationError('Invalid username or password.')
        


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'cover_picture', 'phone', 'user']

class UserAddonSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = UserAddon
        fields = ['id', 'username', 'email', 'role', 'profile', 'first_name', 'last_name', 'is_active']


class UserBlockSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()
    
    class Meta:
        model = UserAddon
        fields = ['is_active']

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance


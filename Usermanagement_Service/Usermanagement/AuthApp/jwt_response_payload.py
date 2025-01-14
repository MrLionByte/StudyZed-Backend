from .serializers import CustomTokenObtainPairSerializer

def jwt_response_payload_handler(token, user=None, request=None):
    print("AS JWT")
    print("AASCD :", token, user)
    return {
        'token': token,
        'user': CustomTokenObtainPairSerializer(user, context={'request':request}).data
    }
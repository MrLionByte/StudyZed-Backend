from rest_framework.serializers import Serializer, ModelSerializer
from .models import PriceOfSession

class GetAllSubSerializer(ModelSerializer):
    class Meta:
        model = PriceOfSession
        fields = "__all__"

class UpdatePriceSerializer(ModelSerializer):
    class Meta:
        model = PriceOfSession
        fields = ["amount"]
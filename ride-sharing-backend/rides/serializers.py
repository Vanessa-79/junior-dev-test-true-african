from rest_framework import serializers
from .models import Ride
from riders.models import Rider
from drivers.models import Driver


class RideSerializer(serializers.ModelSerializer):
    rider_id = serializers.PrimaryKeyRelatedField(
        queryset=Rider.objects.all(), source="rider"
    )

    class Meta:
        model = Ride
        fields = [
            "id",
            "rider_id",
            "pickup_place",
            "destination_place",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

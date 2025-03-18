from rest_framework import serializers
from .models import Ride
from drivers.models import Driver


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = [
            "id",
            "rider_id",
            "pickup_place",
            "destination_place",
            "status",
            "driver",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

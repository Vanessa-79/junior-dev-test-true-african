from rest_framework import serializers
from rides.models import Ride
from riders.serializers import RiderSerializer
from drivers.serializers import DriverSerializer


class RideSerializer(serializers.ModelSerializer):
    rider = RiderSerializer(read_only=True)
    rider_id = serializers.IntegerField(write_only=True)
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = (
            "id",
            "rider",
            "rider_id",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "destination_latitude",
            "destination_longitude",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

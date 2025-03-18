from rest_framework import serializers
from .models import Ride


class RideSerializer(serializers.ModelSerializer):
    rider_id = serializers.PrimaryKeyRelatedField(
        source="rider", queryset=Rider.objects.all()
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

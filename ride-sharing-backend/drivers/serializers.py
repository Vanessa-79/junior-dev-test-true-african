from rest_framework import serializers
from drivers.models import Driver
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = [
            "id",
            "user",
            "vehicle_number",
            "phone_number",
            "rating",
            "current_location",
            "is_available",
            "status",
            "created_at",
            "vehicle_model",
            "vehicle_plate",
        ]

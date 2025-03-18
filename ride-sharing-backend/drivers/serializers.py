from rest_framework import serializers
from drivers.models import Driver
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id",
            "user",
            "vehicle_number",
            "latitude",
            "longitude",
            "is_available",
            "created_at",
        ]

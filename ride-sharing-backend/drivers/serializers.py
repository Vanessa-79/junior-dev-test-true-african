from rest_framework import serializers
from django.contrib.auth.models import User
from drivers.models import Driver


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
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
            "vehicle_model",
            "vehicle_plate",
            "created_at",
        ]
        read_only_fields = ["id", "rating", "created_at"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

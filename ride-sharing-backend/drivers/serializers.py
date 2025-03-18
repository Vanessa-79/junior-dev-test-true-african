from rest_framework import serializers
from drivers.models import Driver
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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
            "latitude",
            "longitude",
            "is_available",
            "status",
            "created_at",
            "vehicle_model",
            "vehicle_plate",
        ]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

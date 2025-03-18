from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class DriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Driver
        fields = [
            "id",
            "username",
            "password",
            "email",
            "phone_number",
            "vehicle_model",
            "vehicle_number",
            "current_location",
            "status",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user_data = {
            "username": validated_data.pop("username"),
            "password": validated_data.pop("password"),
            "email": validated_data.pop("email"),
        }
        user = User.objects.create_user(**user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver


class DriverRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    # Driver fields
    phone_number = serializers.CharField()
    vehicle_model = serializers.CharField()
    vehicle_plate = serializers.CharField()
    current_location = serializers.CharField()

    def create(self, validated_data):
        # Create User instance
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        # Create Driver instance
        driver = Driver.objects.create(
            user=user,
            phone_number=validated_data["phone_number"],
            vehicle_model=validated_data["vehicle_model"],
            vehicle_plate=validated_data["vehicle_plate"],
            current_location=validated_data["current_location"],
        )

        return driver

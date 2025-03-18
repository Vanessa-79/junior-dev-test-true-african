from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Rider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RiderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Rider
        fields = ("id", "username", "password", "email", "phone_number")
        read_only_fields = ("id",)

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = validated_data.pop("email")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        rider = Rider.objects.create(
            user=user, phone_number=validated_data["phone_number"]
        )
        return rider

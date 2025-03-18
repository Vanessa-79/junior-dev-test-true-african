from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Rider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RiderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Rider
        fields = ["id", "username", "email", "phone_number"]
        read_only_fields = ["id"]

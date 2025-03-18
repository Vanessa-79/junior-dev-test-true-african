from rest_framework import serializers
from django.contrib.auth.models import User
from riders.models import Rider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class RiderSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Rider
        fields = ["id", "user", "rating", "created_at"]
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        rider = Rider.objects.create(user=user, **validated_data)
        return rider

from rest_framework import serializers
from .models import Ride


class RideSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = Ride
        fields = [
            "id",
            "username",
            "password",
            "email",
            "phone_number",
            "pickup_place",
            "destination_place",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def create(self, validated_data):
        # Remove user-related fields
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        phone_number = validated_data.pop("phone_number")

        # Get or create rider
        from django.contrib.auth.models import User
        from riders.models import Rider

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
            rider = Rider.objects.create(user=user, phone_number=phone_number)
        else:
            rider = Rider.objects.get(user=user)

        # Find available driver
        from drivers.models import Driver

        driver = Driver.objects.filter(status="available").first()

        # Create ride
        ride = Ride.objects.create(
            rider=rider,
            driver=driver,
            pickup_place=validated_data["pickup_place"],
            destination_place=validated_data["destination_place"],
            status="requested",
        )

        if driver:
            driver.status = "busy"
            driver.save()

        return ride

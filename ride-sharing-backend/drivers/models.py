from django.db import models
from django.contrib.auth.models import User


class Driver(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver_profile"
    )
    phone_number = models.CharField(max_length=15)
    vehicle_model = models.CharField(max_length=50)
    vehicle_number = models.CharField(max_length=20)
    current_location = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[("available", "Available"), ("busy", "Busy"), ("offline", "Offline")],
        default="available",
    )

    def __str__(self):
        return f"{self.user.username} - {self.status} at {self.current_location}"

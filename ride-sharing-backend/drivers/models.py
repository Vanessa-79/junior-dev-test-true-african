from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Driver(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("busy", "Busy"),
        ("offline", "Offline"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    phone_number = models.CharField(
        max_length=15, default="0000000000"
    )  # Added default
    rating = models.FloatField(
        default=5.0, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    current_location = models.CharField(
        max_length=255, default="Kampala"
    )  # Changed from lat/long to place name
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="offline")
    created_at = models.DateTimeField(auto_now_add=True)
    vehicle_model = models.CharField(max_length=50, default="")
    vehicle_plate = models.CharField(max_length=20, default="")

    def __str__(self):
        return (
            f"{self.user.username} - {self.vehicle_number} at {self.current_location}"
        )

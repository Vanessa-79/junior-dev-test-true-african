from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Driver(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("busy", "Busy"),
        ("offline", "Offline"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_model = models.CharField(max_length=100)
    vehicle_plate = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="offline")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_plate}"

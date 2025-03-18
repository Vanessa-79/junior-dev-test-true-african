from django.db import models
from drivers.models import Driver
from riders.models import Rider


class Ride(models.Model):
    RIDE_STATUS = (
        ("requested", "Requested"),
        ("matched", "Matched"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    pickup_place = models.CharField(max_length=100)
    destination_place = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_place} to {self.destination_place}"

from django.db import models
from django.contrib.auth.models import User
from riders.models import Rider
from drivers.models import Driver  # Use the Driver model from the drivers app


class Ride(models.Model):
    RIDE_STATUS = (
        ("requested", "Requested"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    rider_id = models.IntegerField(default=1)  # Add default value
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_place = models.CharField(max_length=100)
    destination_place = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "rides"

    def __str__(self):
        return f"Ride from {self.pickup_place} to {self.destination_place}"

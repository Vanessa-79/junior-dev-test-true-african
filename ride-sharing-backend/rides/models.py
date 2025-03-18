from django.db import models
from drivers.models import Driver
from riders.models import Rider


class Ride(models.Model):
    RIDE_STATUS = (
        ("requested", "Requested"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)
    pickup_place = models.CharField(max_length=255, default="Kampala")
    destination_place = models.CharField(max_length=255, default="Salaama")
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "rides"

    def __str__(self):
        return f"Ride from {self.pickup_place} to {self.destination_place}"

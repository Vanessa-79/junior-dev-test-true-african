"""
Core data model for ride management in the ride-sharing service.
"""

from django.db import models
from drivers.models import Driver
from riders.models import Rider


class Ride(models.Model):
    """
    Represents a ride request in the system.
    Tracks the complete lifecycle of a ride from request to completion.
    """
    
    RIDE_STATUS = (
        ("requested", "Requested"), 
        ("matched", "Matched"),      
        ("in_progress", "In Progress"),  
        ("completed", "Completed"),   
        ("cancelled", "Cancelled"),   
    )

    # Core relationships
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    
    # Location details
    pickup_place = models.CharField(max_length=100)
    destination_place = models.CharField(max_length=100)
    
    # Ride state
    status = models.CharField(max_length=20, choices=RIDE_STATUS, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_place} to {self.destination_place}"

from django.db import models
from django.contrib.auth.models import User


class Rider(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="rider_profile"
    )
    phone_number = models.CharField(max_length=15)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return f"{self.user.username}'s profile"

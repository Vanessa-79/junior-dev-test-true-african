import os
import requests
from django.conf import settings
from drivers.models import Driver


class GeoLocationAPI:
    """Integration with external geolocation API (Google Maps or OpenStreetMap)"""

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.MAPS_API_KEY

    def geocode_address(self, address):
        """Convert a text address to coordinates (lat, lng)"""
        # using Google Maps Geocoding API
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": self.api_key}

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            else:
                return None, None

        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None, None

    def get_directions(self, origin_lat, origin_lng, dest_lat, dest_lng):
        """Get directions between two points"""
        # using Google Maps Directions API
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "OK":
                route = data["routes"][0]["legs"][0]
                return {
                    "distance": route["distance"]["text"],
                    "duration": route["duration"]["text"],
                    "steps": route["steps"],
                }
            else:
                return None

        except Exception as e:
            print(f"Error getting directions: {e}")
            return None

    def update_driver_location(self, driver_id, latitude, longitude):
        """Update a driver's location in the database"""
        try:
            driver = Driver.objects.get(id=driver_id)
            driver.latitude = latitude
            driver.longitude = longitude
            driver.save()
            return True
        except Driver.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error updating driver location: {e}")
            return False



def simulate_driver_movement():
    """Simulate random movement of drivers for testing"""
    import random
    from decimal import Decimal

    # Get all available drivers
    drivers = Driver.objects.filter(status="available")

    for driver in drivers:
        # Simulate small movement (±0.001 degrees is roughly 100m)
        movement = Decimal(random.uniform(-0.001, 0.001))
        driver.latitude += movement

        movement = Decimal(random.uniform(-0.001, 0.001))
        driver.longitude += movement

        driver.save()

    return len(drivers)

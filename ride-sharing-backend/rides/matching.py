from math import radians, cos, sin, asin, sqrt
from drivers.models import Driver
from rides.models import Ride
from utils.geolocation import calculate_distance_between_places


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(
        radians, [float(lon1), float(lat1), float(lon2), float(lat2)]
    )

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 = lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers
    r = 6371
    return c * r


def find_nearest_driver(pickup_place, max_distance=10):
    """Find nearest available driver using place names"""
    # Try exact location match first
    exact_match = Driver.objects.filter(
        status="available", current_location=pickup_place
    ).first()

    if exact_match:
        return exact_match, 0

    # Find nearest using distance calculation
    available_drivers = Driver.objects.filter(status="available")
    nearest_driver = None
    min_distance = float("inf")

    for driver in available_drivers:
        distance = calculate_distance_between_places(
            pickup_place, driver.current_location
        )
        if distance and distance < min_distance and distance <= max_distance:
            min_distance = distance
            nearest_driver = driver

    return nearest_driver, min_distance if nearest_driver else None


def match_ride(ride_id):
    """Match a ride with the nearest available driver"""
    try:
        ride = Ride.objects.get(id=ride_id, status="requested")
    except Ride.DoesNotExist:
        return False, "Ride not found or not in requested status", None

    driver, distance = find_nearest_driver(ride.pickup_place)

    if not driver:
        return False, "No available drivers nearby", ride

    # Match driver to ride
    ride.driver = driver
    ride.status = "matched"
    ride.save()

    # Update driver status
    driver.status = "busy"
    driver.save()

    return True, "Driver matched successfully", ride

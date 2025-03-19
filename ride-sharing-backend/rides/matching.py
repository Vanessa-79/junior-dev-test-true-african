"""
Core ride-matching algorithm implementation using Haversine formula.
Optimized for Uganda's geographical context and driver availability patterns.
"""

from math import radians, cos, sin, asin, sqrt
from drivers.models import Driver
from rides.models import Ride
from utils.geolocation import calculate_distance_between_places


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points using Haversine formula.
    Specifically tuned for Uganda's equatorial coordinates.
    
    Args:
        lon1, lat1: Longitude and latitude of first point
        lon2, lat2: Longitude and latitude of second point
    
    Returns:
        Distance in kilometers between the points
    """
    # Convert decimal degrees to radians for spherical calculations
    lon1, lat1, lon2, lat2 = map(
        radians, [float(lon1), float(lat1), float(lon2), float(lat2)]
    )

    # Haversine formula components
    dlon = lon2 - lon1
    dlat = lat2 = lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    
    # Earth's radius in kilometers (optimized for equatorial region)
    r = 6371
    return c * r


def find_nearest_driver(pickup_place, max_distance=10):
    """
    Find the nearest available driver to a pickup location.
    Uses a two-step approach: exact location match, then distance-based search.
    
    Args:
        pickup_place: Name or coordinates of pickup location
        max_distance: Maximum acceptable distance in kilometers (default: 10km)
    
    Returns:
        Tuple of (nearest driver, distance to pickup)
    """
    # Optimization: Check for exact location match first
    exact_match = Driver.objects.filter(
        status="available", current_location=pickup_place
    ).first()

    if exact_match:
        return exact_match, 0

    # If no exact match, find nearest using Haversine distance
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
    """
    Match a requested ride with the most suitable driver.
    Implements the core business logic for ride-driver matching.
    
    Args:
        ride_id: ID of the ride request to match
    
    Returns:
        Tuple of (success boolean, message string, ride object)
    """
    try:
        ride = Ride.objects.get(id=ride_id, status="requested")
    except Ride.DoesNotExist:
        return False, "Ride not found or not in requested status", None

    # Find nearest driver using optimized algorithm
    driver, distance = find_nearest_driver(ride.pickup_place)

    if not driver:
        return False, "No available drivers nearby", ride

    # Update ride and driver status atomically
    ride.driver = driver
    ride.status = "matched"
    ride.save()

    driver.status = "busy"
    driver.save()

    return True, "Driver matched successfully", ride

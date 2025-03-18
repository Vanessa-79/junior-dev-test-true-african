from math import radians, cos, sin, asin, sqrt
from drivers.models import Driver
from rides.models import Ride


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
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers
    r = 6371
    return c * r


def find_nearest_driver(pickup_lat, pickup_lng, max_distance=10):
    """
    Find the nearest available driver within max_distance (km)
    Returns the driver object or None if no drivers found
    """
    available_drivers = Driver.objects.filter(status="available")

    if not available_drivers:
        return None

    # Calculate distance for each driver and find the closest one
    nearest_driver = None
    min_distance = float("inf")

    for driver in available_drivers:
        distance = haversine(pickup_lng, pickup_lat, driver.longitude, driver.latitude)

        if distance < min_distance and distance <= max_distance:
            min_distance = distance
            nearest_driver = driver

    return nearest_driver, min_distance if nearest_driver else None


def match_ride(ride_id):
    """
    Try to match a driver to a ride request
    Returns (success, message, ride_object)
    """
    try:
        ride = Ride.objects.get(id=ride_id, status="requested")
    except Ride.DoesNotExist:
        return False, "Ride not found or not in requested status", None

    # Find nearest driver
    driver, distance = find_nearest_driver(ride.pickup_latitude, ride.pickup_longitude)

    if not driver:
        return False, "No available drivers nearby", ride

    # Match driver to ride
    ride.driver = driver
    ride.status = "matched"
    ride.save()

    # Update driver status
    driver.status = "busy"
    driver.save()

    return True, f"Driver matched. Estimated arrival: {int(distance * 2)} minutes", ride

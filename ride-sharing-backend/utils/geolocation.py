from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.conf import settings
from django.core.cache import cache
from math import radians, sin, cos, sqrt, asin


def get_place_coordinates(place_name):
    """Convert place name to coordinates using OpenStreetMap with Redis caching"""
    # Try to get from cache first
    cache_key = f"coords:{place_name}"
    coords = cache.get(cache_key)
    
    if coords:
        return coords

    try:
        geolocator = Nominatim(user_agent="ride_sharing_test_app")
        location = geolocator.geocode(place_name)
        if location:
            coords = (location.latitude, location.longitude)
            # Cache the coordinates
            cache.set(cache_key, coords, settings.GEOLOCATION_CACHE_TTL)
            return coords
        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def calculate_distance_between_places(origin_place, destination_place):
    """Calculate distance between two places in kilometers with caching"""
    # Try to get from cache first
    cache_key = f"distance:{origin_place}:{destination_place}"
    distance = cache.get(cache_key)
    
    if distance:
        return distance

    origin_coords = get_place_coordinates(origin_place)
    dest_coords = get_place_coordinates(destination_place)

    if not all([origin_coords[0], dest_coords[0]]):
        return None

    distance = geodesic(origin_coords, dest_coords).kilometers
    # Cache the distance
    cache.set(cache_key, distance, settings.GEOLOCATION_CACHE_TTL)
    return distance


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate distance between two points in Uganda using the haversine formula.
    Optimized for locations within Uganda's geographical bounds:
    Latitude: -1.478 to 4.223
    Longitude: 29.573 to 35.036

    Args:
        lon1, lat1: Longitude and latitude of first point in decimal degrees
        lon2, lat2: Longitude and latitude of second point in decimal degrees
    Returns:
        Distance in kilometers
    """
    # Try to get from cache first
    cache_key = f"haversine:{lon1}:{lat1}:{lon2}:{lat2}"
    distance = cache.get(cache_key)
    
    if distance:
        return distance

    # Validate coordinates are within Uganda's bounds
    if not all(
        -1.478 <= lat <= 4.223 and 29.573 <= lon <= 35.036
        for lat, lon in [(lat1, lon1), (lat2, lon2)]
    ):
        raise ValueError("Coordinates must be within Uganda's boundaries")

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Earth's radius in kilometers
    r = 6371

    distance = c * r
    # Cache the result
    cache.set(cache_key, distance, settings.GEOLOCATION_CACHE_TTL)
    return distance

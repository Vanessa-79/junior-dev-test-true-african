from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.conf import settings


def get_location_coordinates(place_name):
    """Convert place name to coordinates using OpenStreetMap/Nominatim"""
    try:
        geolocator = Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def calculate_distance(origin_place, destination_place):
    """Calculate distance between two places"""
    origin_coords = get_location_coordinates(origin_place)
    dest_coords = get_location_coordinates(destination_place)

    if not all([origin_coords[0], dest_coords[0]]):
        return None

    return geodesic(origin_coords, dest_coords).kilometers

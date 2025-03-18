import pytest
from rides.matching import haversine, find_nearest_driver, match_ride
from drivers.models import Driver
from riders.models import Rider
from rides.models import Ride
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestMatching:
    @pytest.fixture
    def setup_data(self):
        # Create test user for rider
        rider_user = User.objects.create(username="testrider", email="rider@test.com")
        rider = Rider.objects.create(user=rider_user, phone_number="1234567890")

        # Create test users for drivers
        driver1_user = User.objects.create(
            username="testdriver1", email="driver1@test.com"
        )
        driver2_user = User.objects.create(
            username="testdriver2", email="driver2@test.com"
        )
        driver3_user = User.objects.create(
            username="testdriver3", email="driver3@test.com"
        )

        # Create test drivers at different locations
        driver1 = Driver.objects.create(
            user=driver1_user,
            vehicle_model="Toyota Camry",
            vehicle_number="ABC123",
            current_location="Kampala Central",
            status="available",
        )

        driver2 = Driver.objects.create(
            user=driver2_user,
            vehicle_model="Honda Civic",
            vehicle_number="DEF456",  # Changed from vehicle_plate
            current_location="Nakawa",
            status="available",
        )

        driver3 = Driver.objects.create(
            user=driver3_user,
            vehicle_model="Ford Focus",
            vehicle_number="GHI789",  # Changed from vehicle_plate
            current_location="Entebbe",
            status="busy",
        )

        # Create test ride
        ride = Ride.objects.create(
            rider=rider,
            pickup_place="Kampala Central",
            destination_place="Entebbe",
            status="requested",
        )

        return {
            "rider": rider,
            "driver1": driver1,
            "driver2": driver2,
            "driver3": driver3,
            "ride": ride,
        }

    def test_haversine_function(self):
        """Test the haversine distance calculation with Ugandan locations"""

        # Kampala to Entebbe (~40km direct distance)
        kampala_lat, kampala_lon = 0.3476, 32.5825
        entebbe_lat, entebbe_lon = 0.0611, 32.4619
        distance1 = haversine(kampala_lon, kampala_lat, entebbe_lon, entebbe_lat)
        assert 37 < distance1 < 42, f"Kampala-Entebbe distance was {distance1}km"

        # Kampala to Jinja (~79km direct distance)
        jinja_lat, jinja_lon = 0.4250, 33.2039
        distance2 = haversine(kampala_lon, kampala_lat, jinja_lon, jinja_lat)
        assert 77 < distance2 < 81, f"Kampala-Jinja distance was {distance2}km"

    def test_find_nearest_driver(self, setup_data):

        # Test finding driver by exact location match
        driver, distance = find_nearest_driver("Kampala Central")
        assert driver == setup_data["driver1"]
        assert distance == 0

    def test_match_ride(self, setup_data):
        success, message, ride = match_ride(setup_data["ride"].id)

        # Refresh ride from database
        ride.refresh_from_db()

        assert success is True
        assert ride.status == "matched"
        assert ride.driver is not None

        # Check driver status update
        ride.driver.refresh_from_db()
        assert ride.driver.status == "busy"

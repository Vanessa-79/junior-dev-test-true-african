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
            vehicle_plate="ABC123",
            latitude=0.12,  # Close to origin
            longitude=0.12,
            status="available",
        )

        driver2 = Driver.objects.create(
            user=driver2_user,
            vehicle_model="Honda Civic",
            vehicle_plate="DEF456",
            latitude=0.15,  # Further from origin
            longitude=0.15,
            status="available",
        )

        driver3 = Driver.objects.create(
            user=driver3_user,
            vehicle_model="Ford Focus",
            vehicle_plate="GHI789",
            latitude=10.0,  # Very far from origin
            longitude=10.0,
            status="busy",  # Not available
        )

        # Create test ride
        ride = Ride.objects.create(
            rider=rider,
            pickup_latitude=0.1,
            pickup_longitude=0.1,
            destination_latitude=0.2,
            destination_longitude=0.2,
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
        # Test the distance calculation function
        # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~344km
        distance = haversine(-0.1278, 51.5074, 2.3522, 48.8566)
        assert 340 < distance < 350

    def test_find_nearest_driver(self, setup_data):
        # Test finding the nearest available driver
        driver, distance = find_nearest_driver(0.1, 0.1)
        assert driver.id == setup_data["driver1"].id
        assert distance < 5  # Should be very close

    def test_match_ride(self, setup_data):
        # Test matching a ride with the closest driver
        success, message, ride = match_ride(setup_data["ride"].id)

        # Refresh ride from database
        ride = Ride.objects.get(id=setup_data["ride"].id)

        assert success is True
        assert ride.driver.id == setup_data["driver1"].id
        assert ride.status == "matched"

        # Check driver status has been updated
        driver = Driver.objects.get(id=setup_data["driver1"].id)
        assert driver.status == "busy"

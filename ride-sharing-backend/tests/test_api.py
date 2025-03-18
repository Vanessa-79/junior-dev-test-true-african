import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from riders.models import Rider
from drivers.models import Driver
from rides.models import Ride


@pytest.mark.django_db
class TestRideAPI:
    @pytest.fixture
    def setup_data(self):
        # Create test user for rider
        rider_user = User.objects.create_user(
            username="testrider", email="rider@test.com", password="testpass123"
        )
        rider = Rider.objects.create(user=rider_user, phone_number="1234567890")

        # Create test user for driver
        driver_user = User.objects.create_user(
            username="testdriver", email="driver@test.com", password="testpass123"
        )
        driver = Driver.objects.create(
            user=driver_user,
            vehicle_model="Toyota Camry",
            vehicle_plate="ABC123",
            latitude=0.12,
            longitude=0.12,
            status="available",
        )

        return {
            "rider": rider,
            "driver": driver,
            "rider_user": rider_user,
            "driver_user": driver_user,
        }

    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_request_ride(self, api_client, setup_data):
        # Login as rider
        api_client.force_authenticate(user=setup_data["rider_user"])

        # Request a ride
        response = api_client.post(
            "/api/rides/",
            {
                "rider_id": setup_data["rider"].id,
                "pickup_latitude": 0.1,
                "pickup_longitude": 0.1,
                "destination_latitude": 0.2,
                "destination_longitude": 0.2,
            },
        )

        # Check response
        assert response.status_code in [201, 202]  # Created or Accepted

        # Verify ride was created
        assert "ride" in response.data
        ride_id = response.data["ride"]["id"]

        # Verify ride exists in database
        ride = Ride.objects.get(id=ride_id)
        assert ride.rider.id == setup_data["rider"].id

        # The ride should either be matched with a driver or still in requested state
        assert ride.status in ["requested", "matched"]

        if ride.status == "matched":
            assert ride.driver is not None

    def test_get_ride_status(self, api_client, setup_data):
        # Create a ride first
        ride = Ride.objects.create(
            rider=setup_data["rider"],
            driver=setup_data["driver"],
            pickup_latitude=0.1,
            pickup_longitude=0.1,
            destination_latitude=0.2,
            destination_longitude=0.2,
            status="in_progress",
        )

        # Login as rider
        api_client.force_authenticate(user=setup_data["rider_user"])

        # Get ride status
        response = api_client.get(f"/api/rides/{ride.id}/status/")

        # Check response
        assert response.status_code == 200
        assert response.data["status"] == "in_progress"
        assert response.data["driver"] == setup_data["driver_user"].username

    def test_cancel_ride(self, api_client, setup_data):
        # Create a ride first
        ride = Ride.objects.create(
            rider=setup_data["rider"],
            driver=setup_data["driver"],
            pickup_latitude=0.1,
            pickup_longitude=0.1,
            destination_latitude=0.2,
            destination_longitude=0.2,
            status="matched",
        )

        # Set driver to busy
        driver = setup_data["driver"]
        driver.status = "busy"
        driver.save()

        # Login as rider
        api_client.force_authenticate(user=setup_data["rider_user"])

        # Cancel the ride
        response = api_client.post(f"/api/rides/{ride.id}/cancel/")

        # Check response
        assert response.status_code == 200

        # Verify ride status changed
        ride.refresh_from_db()
        assert ride.status == "cancelled"

        # Verify driver status changed back to available
        driver.refresh_from_db()
        assert driver.status == "available"

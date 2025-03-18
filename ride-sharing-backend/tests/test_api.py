import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from riders.models import Rider
from drivers.models import Driver
from rides.models import Ride
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestRideAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def auth_client(self, api_client, setup_data):
        # Create token for rider user
        token = Token.objects.create(user=setup_data["rider"].user)
        # Configure client to use token authentication
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return api_client

    @pytest.fixture
    def setup_data(self):
        # Create rider user and profile
        rider_user = User.objects.create_user(
            username="testrider", password="testpass123", email="rider@test.com"
        )
        rider = Rider.objects.create(user=rider_user, phone_number="1234567890")

        # Create driver user and profile
        driver_user = User.objects.create_user(
            username="testdriver", password="testpass123", email="driver@test.com"
        )
        driver = Driver.objects.create(
            user=driver_user,
            vehicle_model="Toyota Camry",
            vehicle_plate="ABC123",
            current_location="Kampala, Uganda",
            status="available",
        )

        return {"rider": rider, "driver": driver}

    def test_request_ride(self, auth_client, setup_data):
        """Test requesting a new ride"""
        url = reverse("ride-list")
        data = {
            "rider_id": setup_data["rider"].id, 
            "pickup_place": "Kampala, Uganda",
            "destination_place": "Entebbe, Uganda",
        }

        response = auth_client.post(url, data, format="json")
        print("\nResponse status:", response.status_code)
        print("Response data:", response.json())  # Print response body

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] in ["requested", "matched"]

    def test_get_ride_status(self, auth_client, setup_data):
        """Test getting ride status"""
        ride = Ride.objects.create(
            rider=setup_data["rider"],
            pickup_place="Kampala, Uganda",
            destination_place="Entebbe, Uganda",
            status="requested",
        )

        url = reverse("ride-detail", args=[ride.id])
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.data
        assert response.data["pickup_place"] == "Kampala, Uganda"

    def test_cancel_ride(self, auth_client, setup_data):
        """Test cancelling a ride"""
        ride = Ride.objects.create(
            rider=setup_data["rider"],
            pickup_place="Kampala, Uganda",
            destination_place="Entebbe, Uganda",
            status="requested",
        )

        url = reverse("ride-cancel", args=[ride.id])
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "cancelled"

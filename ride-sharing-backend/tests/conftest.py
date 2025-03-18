import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from riders.models import Rider
from drivers.models import Driver


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def test_driver(test_user):
    return Driver.objects.create(
        user=test_user,
        vehicle_number="TEST123",
        phone_number="1234567890",
        current_location="Kampala",
        is_available=True,
        status="available",
        vehicle_model="Test Car",
        vehicle_plate="TEST 123K",
    )


@pytest.fixture
def test_rider(test_user):
    return Rider.objects.create(user=test_user)

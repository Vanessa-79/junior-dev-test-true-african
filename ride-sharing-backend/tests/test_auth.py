import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthentication:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_user_login(self, api_client):
        # Test user (Vanessa) credentials
        username = "Vanessa"
        password = "@Vanie779"

        # Create test user if not exists
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()

        # Attempt login
        response = api_client.post(
            "/api/token/", {"username": username, "password": password}
        )

        assert response.status_code == 200
        assert "token" in response.data

        # Verify token works
        token = response.data["token"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Try accessing protected endpoint
        response = api_client.get("/api/riders/")
        assert response.status_code == 200

    def test_user_can_register(self, api_client):
        """Test user registration with expected response format"""
        url = reverse("user-register")
        data = {
            "username": "newuser",
            "password": "newpass123",
            "email": "newuser@example.com",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "success"
        assert "data" in response.data
        assert response.data["data"]["username"] == "newuser"
        assert response.data["data"]["email"] == "newuser@example.com"

    def test_user_can_login(self, api_client):
        # Create test user
        user = User.objects.create_user(username="testuser", password="testpass123")

        # Attempt login
        url = reverse("api_token")  # Using token auth endpoint
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data  # Check for token instead of 'access'

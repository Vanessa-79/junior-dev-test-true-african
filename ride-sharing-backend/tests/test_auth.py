import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


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

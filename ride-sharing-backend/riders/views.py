from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drivers.models import Driver
from drivers.serializers import DriverSerializer
from drivers.api import GeoLocationAPI
from .models import Rider
from .serializers import RiderSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    @action(detail=False, methods=["GET"])
    def available(self, request):
        """Get all available drivers"""
        drivers = Driver.objects.filter(status="available")
        serializer = self.get_serializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def update_location(self, request, pk=None):
        """Update a driver's location"""
        try:
            driver = self.get_object()
            lat = request.data.get("latitude")
            lng = request.data.get("longitude")

            if not lat or not lng:
                return Response(
                    {"error": "Latitude and longitude are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            driver.latitude = lat
            driver.longitude = lng
            driver.save()

            return Response({"status": "Location updated"})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["POST"])
    def toggle_status(self, request, pk=None):
        """Toggle driver's availability status"""
        driver = self.get_object()
        new_status = request.data.get("status")

        if new_status not in [s[0] for s in Driver.STATUS_CHOICES]:
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        driver.status = new_status
        driver.save()

        return Response({"status": f"Driver status updated to {new_status}"})


class RiderViewSet(viewsets.ModelViewSet):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer

    def get_permissions(self):
        """Allow registration without authentication"""
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if User.objects.filter(username=username).exists():
            return Response(
                {"status": "error", "message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user
        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        # Create rider profile
        rider = Rider.objects.create(
            user=user, phone_number=request.data.get("phone_number", "")
        )

        return Response(
            {
                "status": "success",
                "message": "User registered successfully",
                "token": "dummy_token",  # You would generate a real token here
            },
            status=status.HTTP_201_CREATED,
        )


class RiderRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RiderSerializer(data=request.data)
        if serializer.is_valid():
            rider = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Rider registered successfully",
                    "data": {
                        "id": rider.id,
                        "username": rider.user.username,
                        "email": rider.user.email,
                        "phone_number": rider.phone_number,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Invalid data provided",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create user and rider profile
        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        Rider.objects.create(user=user)

        return Response(
            {"status": "success", "message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

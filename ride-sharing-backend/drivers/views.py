from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import Driver
from .serializers import DriverSerializer, DriverRegistrationSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["GET"])
    def available(self, request):
        """List all available drivers"""
        location = request.query_params.get("location", None)
        drivers = Driver.objects.filter(is_available=True, status="available")

        if location:
            drivers = drivers.filter(current_location=location)

        serializer = self.get_serializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def update_location(self, request, pk=None):
        """Update a driver's location"""
        try:
            driver = self.get_object()
            location = request.data.get("location")

            if not location:
                return Response(
                    {"error": "Location is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            driver.current_location = location
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

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        driver = self.get_object()
        status = request.data.get("status")
        if status not in ["available", "busy", "offline"]:
            return Response(
                {"status": "error", "message": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        driver.status = status
        driver.save()
        return Response(
            {
                "status": "success",
                "message": "Driver status updated",
                "data": {"id": driver.id, "status": driver.status},
            },
            status=status.HTTP_200_OK,
        )


class DriverRegistrationView(APIView):
    permission_classes = []  # Allow unauthenticated registration

    def post(self, request):
        # Check if username already exists
        username = request.data.get("username")
        if User.objects.filter(username=username).exists():
            return Response(
                {
                    "status": "error",
                    "message": "Registration failed",
                    "errors": {"username": ["This username is already taken"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            try:
                driver = serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Driver registered successfully",
                        "data": {
                            "id": driver.id,
                            "username": driver.user.username,
                            "email": driver.user.email,
                            "phone_number": driver.phone_number,
                            "vehicle_model": driver.vehicle_model,
                            "vehicle_number": driver.vehicle_number,
                            "current_location": driver.current_location,
                            "status": driver.status,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "message": "Registration failed",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "status": "error",
                "message": "Invalid data provided",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

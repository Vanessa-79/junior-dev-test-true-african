from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drivers.models import Driver
from drivers.serializers import DriverSerializer
from drivers.api import GeoLocationAPI
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

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

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Driver
from .serializers import DriverSerializer


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

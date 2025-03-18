from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rides.models import Ride
from rides.serializers import RideSerializer
from rest_framework.permissions import IsAuthenticated
from drivers.models import Driver


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Request a ride endpoint
        POST /request-ride/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()

        # Find available driver in the pickup area
        available_driver = Driver.objects.filter(
            is_available=True, status="available", current_location=ride.pickup_place
        ).first()

        if available_driver:
            ride.driver = available_driver
            ride.status = "ongoing"
            ride.save()

            # Update driver status
            available_driver.is_available = False
            available_driver.status = "busy"
            available_driver.save()

            return Response(
                {
                    "message": "Ride created and driver assigned",
                    "ride": RideSerializer(ride).data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "No drivers available in your area",
                    "ride": RideSerializer(ride).data,
                },
                status=status.HTTP_202_ACCEPTED,
            )

    @action(detail=True, methods=["GET"])
    def status(self, request, pk=None):
        """
        Get ride status endpoint
        GET /ride-status/:id/
        """
        try:
            ride = self.get_object()
            response_data = {
                "id": ride.id,
                "status": ride.status,
                "pickup_place": ride.pickup_place,
                "destination_place": ride.destination_place,
                "created_at": ride.created_at,
                "updated_at": ride.updated_at,
            }

            if ride.driver:
                response_data["driver"] = {
                    "name": f"{ride.driver.user.first_name} {ride.driver.user.last_name}",
                    "phone": ride.driver.phone_number,
                    "vehicle": ride.driver.vehicle_model,
                    "plate": ride.driver.vehicle_plate,
                    "current_location": ride.driver.current_location,
                }

            return Response(response_data)
        except Ride.DoesNotExist:
            return Response(
                {"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["POST"])
    def cancel(self, request, pk=None):
        """Cancel a ride"""
        ride = self.get_object()

        if ride.status in ["completed", "cancelled"]:
            return Response(
                {"error": "Cannot cancel a completed or already cancelled ride"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Release the driver if one was assigned
        if ride.driver:
            driver = ride.driver
            driver.status = "available"
            driver.save()

        ride.status = "cancelled"
        ride.save()

        return Response({"status": "Ride cancelled successfully"})

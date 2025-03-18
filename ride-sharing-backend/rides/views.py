from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rides.models import Ride
from rides.serializers import RideSerializer
from rides.matching import match_ride
from rest_framework.permissions import IsAuthenticated


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

        # Try to match with a driver
        success, message, updated_ride = match_ride(ride.id)

        if success:
            return Response(
                {"message": message, "ride": RideSerializer(updated_ride).data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": message, "ride": RideSerializer(ride).data},
                status=status.HTTP_202_ACCEPTED,
            )

    @action(detail=True, methods=["GET"])
    def status(self, request, pk=None):
        """
        Get ride status endpoint
        GET /ride-status/:id/
        """
        ride = self.get_object()
        return Response(
            {
                "id": ride.id,
                "status": ride.status,
                "driver": (
                    {
                        "name": (
                            ride.driver.user.get_full_name() if ride.driver else None
                        ),
                        "phone": ride.driver.phone_number if ride.driver else None,
                        "vehicle": ride.driver.vehicle_model if ride.driver else None,
                        "plate": ride.driver.vehicle_plate if ride.driver else None,
                    }
                    if ride.driver
                    else None
                ),
                "pickup": {
                    "latitude": float(ride.pickup_latitude),
                    "longitude": float(ride.pickup_longitude),
                },
                "destination": {
                    "latitude": float(ride.destination_latitude),
                    "longitude": float(ride.destination_longitude),
                },
                "created_at": ride.created_at,
                "updated_at": ride.updated_at,
            }
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

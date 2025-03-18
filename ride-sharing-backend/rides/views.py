from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rides.models import Ride
from rides.serializers import RideSerializer
from rides.matching import match_ride


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def create(self, request, *args, **kwargs):
        """Create a new ride request and try to match with driver"""
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
        """Get the status of a ride"""
        ride = self.get_object()
        return Response(
            {
                "id": ride.id,
                "status": ride.status,
                "driver": ride.driver.user.username if ride.driver else None,
                "vehicle": ride.driver.vehicle_model if ride.driver else None,
                "plate": ride.driver.vehicle_plate if ride.driver else None,
                "created_at": ride.created_at,
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

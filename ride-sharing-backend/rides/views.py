from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rides.models import Ride
from rides.serializers import RideSerializer
from rest_framework.permissions import IsAuthenticated
from drivers.models import Driver
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a new ride request"""
        # Extract data from request
        rider_id = request.data.get("rider_id")
        pickup_place = request.data.get("pickup_place")
        destination_place = request.data.get("destination_place")

        # Validate required fields
        if not all([rider_id, pickup_place, destination_place]):
            return Response(
                {"error": "rider_id, pickup_place, and destination_place are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find available driver
        driver = Driver.objects.filter(
            is_available=True,
            status="available",
            current_location=pickup_place
        ).first()

        # Create ride
        ride = Ride.objects.create(
            rider_id=rider_id,
            pickup_place=pickup_place,
            destination_place=destination_place,
            status="ongoing" if driver else "requested",
            driver=driver
        )

        if driver:
            # Update driver status
            driver.is_available = False
            driver.status = "busy"
            driver.save()

        serializer = self.get_serializer(ride)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def status(self, request, pk=None):
        """
        Get ride status endpoint
        GET /ride-status/:id/
        """
        try:
            ride = self.get_object()
            serializer = self.get_serializer(ride)
            return Response(serializer.data)
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


class RequestRideView(APIView):
    def post(self, request):
        # Extract ride details from the request
        rider_id = request.data.get("rider_id")
        pickup_place = request.data.get("pickup_place")
        destination_place = request.data.get("destination_place")

        # Validate required fields
        if not rider_id or not pickup_place or not destination_place:
            return Response(
                {
                    "error": "All fields (rider_id, pickup_place, destination_place) are required."
                },
                status=400,
            )

        # Validate rider existence
        if not Ride.objects.filter(rider_id=rider_id).exists():
            return Response(
                {"error": "Invalid rider_id. Rider does not exist."}, status=400
            )

        # Find an available driver
        driver = Driver.objects.filter(
            is_available=True, status="available", current_location=pickup_place
        ).first()

        if not driver:
            return Response(
                {"message": "No available drivers at the moment"}, status=400
            )

        # Create the ride
        ride = Ride.objects.create(
            rider_id=rider_id,
            pickup_place=pickup_place,
            destination_place=destination_place,
            status="ongoing",
            driver=driver,
        )

        # Update the driver's status
        driver.is_available = False
        driver.status = "busy"
        driver.save()

        # Include driver details in the response
        response_data = {
            "id": ride.id,
            "rider_id": ride.rider_id,
            "pickup_place": ride.pickup_place,
            "destination_place": ride.destination_place,
            "status": ride.status,
            "driver": {
                "name": f"{driver.user.first_name} {driver.user.last_name}",
                "phone": driver.phone_number,
                "vehicle": driver.vehicle_model,
                "plate": driver.vehicle_plate,
                "current_location": driver.current_location,
            },
            "created_at": ride.created_at,
            "updated_at": ride.updated_at,
        }

        return Response(response_data, status=201)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import Ride
from .serializers import RideSerializer
from riders.models import Rider
from drivers.models import Driver
from rest_framework.decorators import action
from rest_framework.views import APIView


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            Rider.objects.create(user=user, phone_number=phone_number)

        try:
            rider = Rider.objects.get(user=user)
        except Rider.DoesNotExist:
            return Response(
                {"error": "No rider profile found for authenticated user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        available_driver = Driver.objects.filter(status="available").first()
        if not available_driver:
            return Response(
                {"error": "No available drivers at the moment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ride = serializer.save(rider=rider, driver=available_driver)
            available_driver.status = "busy"
            available_driver.save()
            return Response(
                {
                    "status": "success",
                    "message": "Ride requested successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Ride request failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            ride = self.get_object()
            return Response(
                {
                    "status": "success",
                    "data": {
                        "id": ride.id,
                        "pickup_place": ride.pickup_place,
                        "destination_place": ride.destination_place,
                        "status": ride.status,
                        "driver": (
                            {
                                "name": (
                                    ride.driver.user.username if ride.driver else None
                                ),
                                "phone": (
                                    ride.driver.phone_number if ride.driver else None
                                ),
                                "vehicle": (
                                    ride.driver.vehicle_model if ride.driver else None
                                ),
                            }
                            if ride.driver
                            else None
                        ),
                        "created_at": ride.created_at,
                        "updated_at": ride.updated_at,
                    },
                }
            )
        except Ride.DoesNotExist:
            return Response(
                {"status": "error", "message": "Ride not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

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
        ride.status = "cancelled"
        ride.save()
        return Response({"status": "cancelled"})


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

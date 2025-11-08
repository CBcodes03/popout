from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Event, EventJoinRequest, Notification
from .serializers import EventSerializer, EventJoinRequestSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from geopy.distance import geodesic


# Create Event
class EventCreateView(generics.CreateAPIView):
    """
    Allows authenticated users to create events.
    Automatically sets organizer to the logged-in user.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            event = serializer.save(organizer=request.user)

            # If start_time not provided, compute from join_expiry_minutes
            if not event.start_time:
                event.start_time = timezone.now() + timedelta(minutes=event.join_expiry_minutes)
                event.save()

            return Response({
                "message": "Event created successfully",
                "event": EventSerializer(event).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Send Join Request
class EventJoinRequestView(generics.CreateAPIView):
    serializer_class = EventJoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if event.organizer == request.user:
            return Response({"error": "You can't join your own event"}, status=400)
        
        req, created = EventJoinRequest.objects.get_or_create(event=event, user=request.user)
        if not created:
            return Response({"message": "Already requested"}, status=400)
        
        # Create notification for organizer
        Notification.objects.create(
            user=event.organizer,
            message=f"{request.user.username} requested to join your event '{event.title}'"
        )
        return Response({"message": "Join request sent"}, status=201)

# Accept/Reject Join Request
class RespondJoinRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        action = request.data.get("action")  # 'accept' or 'reject'
        join_request = EventJoinRequest.objects.get(id=request_id)

        if join_request.event.organizer != request.user:
            return Response({"error": "Not authorized"}, status=403)

        if action not in ["accept", "reject"]:
            return Response({"error": "Invalid action"}, status=400)

        join_request.status = "accepted" if action == "accept" else "rejected"
        join_request.save()

        # Notify user
        Notification.objects.create(
            user=join_request.user,
            message=f"Your request to join '{join_request.event.title}' was {join_request.status}"
        )

        return Response({"message": f"Request {join_request.status}"}, status=200)

from geopy.distance import geodesic

def nearby_events(user_location, max_distance_km=5):
    events = Event.objects.all()
    nearby = []
    for e in events:
        distance = geodesic(user_location, (e.lat, e.lon)).km
        if distance <= max_distance_km:
            nearby.append(e)
    return nearby


User = get_user_model()

class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        location = request.data.get("location")
        if not location:
            return Response({"detail": "No location provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.location = location
        user.save()
        return Response({"message": "Location updated successfully"}, status=status.HTTP_200_OK)

class NearbyEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.location:
            return Response({"detail": "User location not set"}, status=400)

        try:
            lat, lon = map(float, user.location.split(","))
        except ValueError:
            return Response({"detail": "Invalid user location format"}, status=400)

        max_distance_km = float(request.query_params.get("max_distance", 5))
        nearby = []
        for event in Event.objects.all():
            if event.lat and event.lon:
                distance = geodesic((lat, lon), (event.lat, event.lon)).km
                if distance <= max_distance_km:
                    nearby.append(event)

        serializer = EventSerializer(nearby, many=True)
        return Response(serializer.data, status=200)
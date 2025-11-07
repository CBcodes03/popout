from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Event, EventJoinRequest, Notification
from .serializers import EventSerializer, EventJoinRequestSerializer
from rest_framework.views import APIView


# Create Event
class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

# Send Join Request
class EventJoinRequestView(generics.CreateAPIView):
    serializer_class = EventJoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

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

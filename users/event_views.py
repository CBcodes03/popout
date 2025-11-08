from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Event, EventJoinRequest, Notification, ChatGroup
from .serializers import EventSerializer, EventJoinRequestSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from geopy.distance import geodesic
from .models import Event, EventJoinRequest
from django.utils import timezone
from django.db.models import Q

def is_user_busy(user, new_event_start=None, new_event_end=None):
    """
    Returns True if the user is already associated with any event
    (organizing or participating) that overlaps with the given time.
    If new_event_start and new_event_end are None, checks for ongoing events.
    """
    if new_event_start is None or new_event_end is None:
        now = timezone.now()
        new_event_start = now
        new_event_end = now

    # Check if user is organizer of overlapping events
    organizing = user.organized_events.filter(
        start_time__lt=new_event_end,
        end_time__gt=new_event_start
    )

    # Check if user is participant (accepted join requests) in overlapping events
    joining = user.event_requests.filter(
        status="accepted",
        event__start_time__lt=new_event_end,
        event__end_time__gt=new_event_start
    )

    return organizing.exists() or joining.exists()


# Create Event
class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        if not start_time or not end_time:
            return Response({"error": "Start and end time required"}, status=400)

        if is_user_busy(user, new_event_start=start_time, new_event_end=end_time):
            return Response(
                {"error": "You are already part of an overlapping event. Cannot create a new one."},
                status=400
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(organizer=user)
            # Create chat group for the event
            ChatGroup.objects.create(event=event)
            return Response({
                "message": "Event created successfully",
                "event": EventSerializer(event).data
            }, status=201)

        return Response(serializer.errors, status=400)



# Send Join Request
class EventJoinRequestView(generics.CreateAPIView):
    serializer_class = EventJoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        user = request.user
        event = Event.objects.get(id=event_id)

        if event.organizer == user:
            return Response({"error": "You can't join your own event"}, status=400)

        if is_user_busy(user, new_event_start=event.start_time, new_event_end=event.end_time):
            return Response(
                {"error": "You are already part of an overlapping event. Cannot join this event."},
                status=400
            )

        req, created = EventJoinRequest.objects.get_or_create(event=event, user=user)
        if not created:
            return Response({"message": "Already requested"}, status=400)

        # Notify organizer
        Notification.objects.create(
            user=event.organizer,
            message=f"{user.username} requested to join your event '{event.title}'"
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
        join_request.responded_at = timezone.now()
        join_request.save()

        # If accepted, user is automatically added to chat group (via ChatGroup.members property)
        # The chat group already exists and includes all accepted members dynamically

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

        max_distance_km = float(request.query_params.get("max_distance", 50))
        nearby_events = []

        for event in Event.objects.exclude(organizer=user):
            if event.lat is not None and event.lon is not None:
                distance = geodesic((lat, lon), (event.lat, event.lon)).km
                print("first if")
                if distance <= max_distance_km:
                    print("second if")
                    event_data = EventSerializer(event).data
                    join_request = EventJoinRequest.objects.filter(event=event, user=user).first()
                    if join_request:
                        print("third if")
                        event_data["join_status"] = "requested" if join_request.status=="pending" else join_request.status
                    else:
                        event_data["join_status"] = "not_requested"
                    event_data["distance_km"] = round(distance, 2)
                    nearby_events.append(event_data)
        print(nearby_events)
        return Response(nearby_events, status=200)

class MyEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Events the user organized
        organized = user.organized_events.all()

        # Events the user has joined (accepted)
        joined = Event.objects.filter(join_requests__user=user, join_requests__status="accepted")

        # Combine and remove duplicates if any
        all_events = (organized | joined).distinct()

        # Serialize
        serializer = EventSerializer(all_events, many=True)
        events_data = serializer.data

        # Mark whether user is organizer or participant
        for e in events_data:
            e["role"] = "organizer" if e["organizer"] == user.id else "participant"

        return Response({"events": events_data}, status=200)
    

class PendingJoinRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id, organizer=user)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found or not authorized"}, status=404)

        pending_requests = EventJoinRequest.objects.filter(event=event, status="pending")
        data = [{"id": r.id, "username": r.user.username} for r in pending_requests]

        return Response(data)
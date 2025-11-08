from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ChatGroup, ChatMessage, Event, EventJoinRequest
from django.utils import timezone

class GetChatGroupsView(APIView):
    """Get all chat groups for events the user is part of"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get events where user is organizer or accepted participant
        organized_events = Event.objects.filter(organizer=user)
        participated_events = Event.objects.filter(
            join_requests__user=user,
            join_requests__status="accepted"
        )
        all_events = (organized_events | participated_events).distinct()
        
        # Get chat groups for these events
        chat_groups = []
        for event in all_events:
            if hasattr(event, 'chat_group'):
                chat_group = event.chat_group
                # Get last message
                last_message = chat_group.messages.last()
                chat_groups.append({
                    "id": chat_group.id,
                    "event_id": event.id,
                    "event_title": event.title,
                    "last_message": {
                        "message": last_message.message if last_message else None,
                        "user": last_message.user.username if last_message else None,
                        "created_at": last_message.created_at.isoformat() if last_message else None
                    },
                    "unread_count": 0  # Can be enhanced later
                })
        
        return Response(chat_groups, status=status.HTTP_200_OK)

class GetChatMessagesView(APIView):
    """Get messages for a specific chat group"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_group_id):
        user = request.user
        
        try:
            chat_group = ChatGroup.objects.get(id=chat_group_id)
        except ChatGroup.DoesNotExist:
            return Response({"error": "Chat group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is a member
        if user not in chat_group.members:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Get messages
        messages = chat_group.messages.all()
        messages_data = [{
            "id": msg.id,
            "user": msg.user.username,
            "user_id": msg.user.id,
            "message": msg.message,
            "created_at": msg.created_at.isoformat()
        } for msg in messages]
        
        return Response(messages_data, status=status.HTTP_200_OK)

class SendChatMessageView(APIView):
    """Send a message to a chat group"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, chat_group_id):
        user = request.user
        message_text = request.data.get("message", "").strip()
        
        if not message_text:
            return Response({"error": "Message cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chat_group = ChatGroup.objects.get(id=chat_group_id)
        except ChatGroup.DoesNotExist:
            return Response({"error": "Chat group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is a member
        if user not in chat_group.members:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if event has ended
        if timezone.now() > chat_group.event.end_time:
            return Response({"error": "Event has ended. Chat is no longer available."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create message
        message = ChatMessage.objects.create(
            chat_group=chat_group,
            user=user,
            message=message_text
        )
        
        return Response({
            "id": message.id,
            "user": message.user.username,
            "user_id": message.user.id,
            "message": message.message,
            "created_at": message.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)


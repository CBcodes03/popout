from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Event, EventJoinRequest, Notification


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email.split('@')[0], password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email,
            },
        }
    
class EventSerializer(serializers.ModelSerializer):
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'location_name', 'lat', 'lon',
            'join_expiry_minutes', 'start_time', 'end_time',
            'max_participants', 'organizer', 'organizer_username'
        ]
        read_only_fields = ['organizer']
# Serializer for EventJoinRequest model
class EventJoinRequestSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventJoinRequest
        fields = ['id', 'event', 'event_title', 'user', 'user_username', 'status']
        read_only_fields = ['status', 'user']

# Serializer for Notification model
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'seen', 'created_at']
        read_only_fields = ['user', 'created_at']
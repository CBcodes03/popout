# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

# --------------------------
# Custom User
# --------------------------
class User(AbstractUser):
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    verified = models.BooleanField(default=False)
    total_events = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username

# --------------------------
# Event Model
# --------------------------
class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location_name = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    join_expiry_minutes = models.PositiveIntegerField(default=30)
    start_time = models.DateTimeField(editable=False)  # automatically computed
    end_time = models.DateTimeField()
    max_participants = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically set start_time based on join_expiry_minutes if not set."""
        if not self.start_time:
            self.start_time = timezone.now() + timedelta(minutes=self.join_expiry_minutes)
        super().save(*args, **kwargs)

    def can_join(self):
        """Check if users can still join this event."""
        now = timezone.now()
        return now < self.start_time

    @property
    def participants_count(self):
        return self.join_requests.filter(status="accepted").count()

    def __str__(self):
        return f"{self.title} by {self.organizer.username}"

# --------------------------
# Event Join Request Model
# --------------------------
class EventJoinRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="join_requests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)  # when organizer accepts/rejects

    class Meta:
        unique_together = ("event", "user")  # prevent duplicate requests

    def __str__(self):
        return f"{self.user.username} → {self.event.title} ({self.status})"

# --------------------------
# Notification Model
# --------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    related_event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True, related_name="notifications")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"

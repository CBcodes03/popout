# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location_name = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    join_expiry_minutes = models.PositiveIntegerField(default=30)  # joining window in minutes
    start_time = models.DateTimeField(editable=False)  # computed automatically
    end_time = models.DateTimeField()                  # event duration can be set by organizer
    max_participants = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically set start_time based on join_expiry_minutes if not set."""
        if not self.start_time:
            self.start_time = timezone.now() + timedelta(minutes=self.join_expiry_minutes)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.organizer.username}"

    def can_join(self):
        """Check if users can still join this event."""
        now = timezone.now()
        return now < self.start_time and now >= self.created_at

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"

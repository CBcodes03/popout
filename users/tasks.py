from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Event, EventJoinRequest, Notification

@shared_task
def cleanup_old_events_task():
    now = timezone.now()
    cutoff = now - timedelta(minutes=30)  # events older than 30 mins

    old_events = Event.objects.filter(end_time__lt=cutoff)

    count = old_events.count()

    for event in old_events:
        # Delete related join requests
        EventJoinRequest.objects.filter(event=event).delete()

        # Delete related notifications (if you store event reference)
        Notification.objects.filter(event=event).delete()

        # Delete the event itself
        event.delete()

    return f"Cleaned up {count} old events."

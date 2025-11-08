from django_cron import CronJobBase, Schedule
from django.utils import timezone
from datetime import timedelta
from .models import Event, EventJoinRequest, Notification, ChatGroup, ChatMessage

class DeleteOldEventsCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # every 5 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'users.delete_old_events_cron'  # unique code

    def do(self):
        now = timezone.now()
        cutoff = now - timedelta(minutes=30)

        # Delete join requests for old events
        old_requests = EventJoinRequest.objects.filter(event__end_time__lte=cutoff)
        old_requests.delete()

        # Optionally delete notifications for old events
        Notification.objects.filter(message__icontains="event")\
            .filter(user__event_requests__event__end_time__lte=cutoff).delete()

        # Delete chat messages for ended events (chat groups are deleted via CASCADE)
        ended_events = Event.objects.filter(end_time__lte=cutoff)
        for event in ended_events:
            if hasattr(event, 'chat_group'):
                ChatMessage.objects.filter(chat_group=event.chat_group).delete()
        
        # Delete old events (this will cascade delete chat groups)
        deleted_count, _ = Event.objects.filter(end_time__lte=cutoff).delete()
        print(f"[Cron] Deleted {deleted_count} old events, related join requests, and chat groups.")

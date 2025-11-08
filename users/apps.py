# users/apps.py
from django.apps import AppConfig
import threading
import time
from django.utils import timezone
from datetime import timedelta

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from django.conf import settings
        if settings.DEBUG:  # only run in dev

            def delete_old_events_task():
                from .models import Event, EventJoinRequest  # IMPORT INSIDE FUNCTION
                while True:
                    cutoff = timezone.now() - timedelta(minutes=30)
                    # Delete old join requests
                    EventJoinRequest.objects.filter(event__end_time__lte=cutoff).delete()
                    # Delete old events
                    Event.objects.filter(end_time__lte=cutoff).delete()
                    time.sleep(10)  # repeat every 5 minutes

            threading.Thread(target=delete_old_events_task, daemon=True).start()

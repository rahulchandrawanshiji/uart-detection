

# from django.apps import AppConfig

# class UiAppConfig(AppConfig):
#     name = 'ui_app'

#     def ready(self):
#         # Import and start serial forwarding here
#         from .serial_forwarder import start_forwarding
#         start_forwarding()
# ui_app/apps.py

from django.apps import AppConfig
import threading
from .serial_data import start_serial_thread
from .detection import start_detection_thread


class UiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui_app'

    def ready(self):
        # Prevent multiple threads when Django auto-reloads
        if hasattr(self, 'threads_started'):
            return

        start_serial_thread()
        start_detection_thread()

        self.threads_started = True

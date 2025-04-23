# from django.apps import AppConfig


# class UiAppConfig(AppConfig):
#     name = 'ui_app'

# ui_app/apps.py

from django.apps import AppConfig

class UiAppConfig(AppConfig):
    name = 'ui_app'

    def ready(self):
        # Import and start serial forwarding here
        from .serial_forwarder import start_forwarding
        start_forwarding()

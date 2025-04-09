# from django.urls import path
# from .views import home, start_detection

# urlpatterns = [
#     path('', home, name='home'),
#     path('start-detection/', start_detection, name='start_detection'),
# ]


# from django.urls import path
# from .views import home, start_detection, control_device  # Ensure these functions exist

# urlpatterns = [
#     path("", home, name="home"),
#     path("start-detection/", start_detection, name="start_detection"),
#     path("control-device/", control_device, name="control_device"),
# ]
from django.urls import path

# Main view functions
from .views import (
    home, start_detection, control_device, detection_page,
    video_feed, stop_detection, sensor_data, send_command_api
)

# UART APIs (correct relative import)
from . import uart_api

urlpatterns = [
    # Page views
    path("", home, name="home"),
    path("start_detection/", start_detection, name="start_detection"),
    path("control-device/", control_device, name="control_device"),
    path("detection/", detection_page, name="detection_page"),
    path("video_feed/", video_feed, name="video_feed"),
    path("stop_detection/", stop_detection, name="stop_detection"),
    path("sensor_data/", sensor_data, name="sensor_data"),
    path("api/send_command/", send_command_api, name="send_command_api"),

    # UART API routes
    path("api/fan/on/", uart_api.fan_on, name="fan_on"),
    path("api/fan/off/", uart_api.fan_off, name="fan_off"),
    path("api/fan/status/", uart_api.fan_status, name="fan_status"),

    path("api/lock/open/", uart_api.lock_open, name="lock_open"),
    path("api/lock/close/", uart_api.lock_close, name="lock_close"),

    path("api/light/on/", uart_api.light_on, name="light_on"),
    path("api/light/off/", uart_api.light_off, name="light_off"),
    path("api/light/all/on/", uart_api.light_all_on, name="light_all_on"),
    path("api/light/all/off/", uart_api.light_all_off, name="light_all_off"),
    path("api/light/status/", uart_api.light_status, name="light_status"),
]



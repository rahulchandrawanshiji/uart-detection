from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .detection import video_feed

# Main view functions
from .views import (
    home,new_ui, start_detection, control_device, detection_page,session_test,manage_button,
     stop_detection, sensor_data, send_command_api, read_uart_and_save,receive_post_command,get_sensor_data_from_queue,
     save_button_data,get_all_device_permissions
)

# UART APIs (correct relative import)
from . import uart_api

urlpatterns = [
    # Page views
    path("", home, name="home"),
    path('send_command/', receive_post_command,name="receive_post_command"),
    path("new_index/",new_ui,name="new_ui"),
    path("manage_sensors/",manage_button,name="manage_button"),
    path("start_detection/", start_detection, name="start_detection"),
    path("control-device/", control_device, name="control_device"),
    path("get_sensor_data_from_queue/", get_sensor_data_from_queue, name="get_sensor_data_from_queue"),
    # path("new_index/", new_index, name="new_index"),
    path("detection/", detection_page, name="detection_page"),
    path("video_feed/", video_feed, name="video_feed"),
    path("stop_detection/", stop_detection, name="stop_detection"),
    path("sensor_data/", sensor_data, name="sensor_data"),
    path("api/send_command/", send_command_api, name="send_command_api"),
    path("save_button_data/", save_button_data, name="save_button_data"),
    path("get_all_device_permissions/", get_all_device_permissions, name="get_all_device_permissions"),
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
    path("session-test/", session_test, name="session_test"), 
    path("api/read_uart/", read_uart_and_save, name="read_uart"),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



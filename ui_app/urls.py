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
from .views import home, start_detection, control_device, detection_page, video_feed, stop_detection

urlpatterns = [
    # ✅ Existing Routes (No Changes)
    path("", home, name="home"),
    path("start-detection/", start_detection, name="start_detection"),
    path("control-device/", control_device, name="control_device"),

    # ✅ New Object Detection Routes (Safely Added)
    path("detection/", detection_page, name="detection_page"),  # Page for object detection UI
    path("video_feed/", video_feed, name="video_feed"),  # Video streaming endpoint
    path("stop_detection/", stop_detection, name="stop_detection"),  # Stop detection command
]

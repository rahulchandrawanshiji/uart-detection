# from django.urls import path
# from .views import home, start_detection

# urlpatterns = [
#     path('', home, name='home'),
#     path('start-detection/', start_detection, name='start_detection'),
# ]


from django.urls import path
from .views import home, start_detection, control_device  # Ensure these functions exist

urlpatterns = [
    path("", home, name="home"),
    path("start-detection/", start_detection, name="start_detection"),
    path("control-device/", control_device, name="control_device"),
]

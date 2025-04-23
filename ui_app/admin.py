from django.contrib import admin
from .models import DetectedImage

@admin.register(DetectedImage)
class DetectedImageAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'detected_objects', 'timestamp', 'image_path')
    search_fields = ('detected_objects',)


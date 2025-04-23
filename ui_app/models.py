from django.db import models
from django.utils.html import mark_safe

class DetectedImage(models.Model):
    image_path = models.CharField(max_length=255)
    detected_objects = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.detected_objects} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def image_tag(self):
        return mark_safe(f'<img src="/{self.image_path}" width="150" />')

    image_tag.short_description = 'Preview'
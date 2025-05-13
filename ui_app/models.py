from django.db import models
from django.utils.html import mark_safe
from django.utils.timezone import now

class DetectedImage(models.Model):
    id = models.BigAutoField(primary_key=True) 
    image_path = models.CharField(max_length=255)
    detected_objects = models.TextField()
    head_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.detected_objects} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def image_tag(self):
        return mark_safe(f'<img src="/{self.image_path}" width="150" />')

    image_tag.short_description = 'Preview'

class SensorData(models.Model):
    # Define fields as per your requirements
    id = models.BigAutoField(primary_key=True)
    sensor = models.CharField(max_length=255)
    min_value = models.FloatField()
    max_value = models.FloatField()
    start = models.BooleanField(default=False)
    end = models.BooleanField(default=False)
    auto = models.BooleanField(default=False)
    auto_interval = models.IntegerField()
    event_interval = models.IntegerField()

    def __str__(self):
        return f"Sensor: {self.sensor}, Min: {self.min_value}, Max: {self.max_value}"
    
class UartData(models.Model):
    IAQ = models.IntegerField()
    PM2_5 = models.IntegerField()
    PM10 = models.IntegerField()
    CO2 = models.IntegerField()
    TVOC_Value = models.IntegerField()
    TVOC_Index = models.IntegerField()
    Viral_Value = models.IntegerField()
    Viral_Index = models.IntegerField()
    Humidity = models.IntegerField()
    Temperature_C = models.IntegerField()
    Temperature_F = models.IntegerField()
    PM1 = models.IntegerField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"IAQ: {self.IAQ}, PM2_5: {self.PM2_5}, Temperature_C: {self.Temperature_C}"
    


class Device_Permission(models.Model):
    id = models.BigAutoField(primary_key=True)
    Module_Name    = models.CharField(max_length=255)
    Device_Name    = models.CharField(max_length=255, unique=True)
    Button_Id      = models.CharField(max_length=255, null=True, blank=True)
    Operation_Type = models.IntegerField()
    Intensity = models.IntegerField(default=0)

    def __str__(self):
        return (f"Module: {self.Module_Name}, Device: {self.Device_Name}, "
                f"Button Id: {self.Button_Id}, Operation Type: {self.Operation_Type},Intensity: {self.Intensity}")

       
class Live_Device_Permission(models.Model):
    id = models.BigAutoField(primary_key=True)
    Device_Name = models.CharField(max_length=255)
    Button_Id = models.CharField(max_length=255)
    Operation_Type = models.IntegerField()
    Intensity_Value = models.IntegerField()
    Date_Time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.id},Device_Name: {self.Device_Name}, Button_Id: {self.Button_Id}, Operation_Type: {self.Operation_Type}, Intensity_Value: {self.Intensity_Value}, Date_Time: {self.Date_Time}"
    

class Device_Permission_Log(models.Model):
    Device_Name = models.CharField(max_length=255)
    Button_Id = models.CharField(max_length=255)
    Operation_Type = models.IntegerField()
    Intensity_Value = models.IntegerField()
    Date_Time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device_Name: {self.Device_Name}, Button_Id: {self.Button_Id}, Operation_Type: {self.Operation_Type}, Intensity_Value: {self.Intensity_Value}, Date_Time: {self.Date_Time}"
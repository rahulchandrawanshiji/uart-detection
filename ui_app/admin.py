from django.contrib import admin
from .models import DetectedImage, SensorData,UartData,Device_Permission,Live_Device_Permission,Device_Permission_Log

@admin.register(DetectedImage)
class DetectedImageAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'detected_objects', 'head_count', 'timestamp', 'image_path')
    search_fields = ('detected_objects',)

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'min_value', 'max_value', 'start', 'end', 'auto', 'auto_interval', 'event_interval')
    search_fields = ('sensor',)  # Search by sensor name
    list_filter = ('start', 'end', 'auto')  # Optional filters

@admin.register(UartData)
class UartDataAdmin(admin.ModelAdmin):
    list_display = ('IAQ', 'PM2_5', 'PM10', 'CO2', 'TVOC_Value', 'TVOC_Index', 'Viral_Value', 'Viral_Index', 'Humidity', 'Temperature_C', 'Temperature_F', 'PM1')

@admin.register(Device_Permission)
class Device_Permission(admin.ModelAdmin):
    list_display = ('Module_Name', 'Device_Name', 'Button_Id' , 'Operation_Type','Intensity')
    
@admin.register(Live_Device_Permission)
class Live_Device_Permission(admin.ModelAdmin):
    list_display = ('id','Device_Name', 'Button_Id', 'Operation_Type' , 'Intensity_Value','Date_Time')

@admin.register(Device_Permission_Log)
class Device_Permission_Log(admin.ModelAdmin):
    list_display = ('Device_Name', 'Button_Id', 'Operation_Type' , 'Intensity_Value','Date_Time')
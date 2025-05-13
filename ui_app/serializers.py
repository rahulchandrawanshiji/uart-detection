# ui_app/serializers.py
from rest_framework import serializers
from .models import Device_Permission,Live_Device_Permission,Device_Permission_Log

class DevicePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device_Permission
        fields = ['id', 'Module_Name', 'Device_Name', 'Button_Id' ,'Operation_Type','Intensity']

class Live_Device_Permission(serializers.ModelSerializer):
    class Meta:
        model = Live_Device_Permission
        fields = ['id','Device_Name', 'Button_Id', 'Operation_Type', 'Intensity_Value' ,'Date_Time']

class Device_Permission_Log(serializers.ModelSerializer):
    class Meta:
        model = Device_Permission_Log
        fields = ['Device_Name', 'Button_Id', 'Operation_Type', 'Intensity_Value' ,'Date_Time']
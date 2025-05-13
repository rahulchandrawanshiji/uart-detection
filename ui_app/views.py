from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import serial
import time
import uuid
from datetime import datetime, timedelta
import os
import cv2
import numpy as np
import json
import threading
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
from ui_app.detection import start_detection_thread, stop_detection
from django.shortcuts import render
from .models import DetectedImage
from .uart_parser import parse_uart_response
from .models import UartData
from .shared_queue import requst_cmd
from .shared_queue import data_to_android
from queue import Empty
from .serializers import DevicePermissionSerializer
from rest_framework.decorators import api_view
import urllib.parse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Device_Permission


frame_buffer = None
frame_lock = threading.Lock()
stop_flag = False
detection_thread = None

# Serial Configuration
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

# Global flags
stop_flag = False
detection_thread = None

# @api_view(['POST'])
# @csrf_exempt  # <- This goes AFTER @api_view
# def save_button_data(request):
#     data = {
#         'Operation_Type': request.POST.get('Operation_Type'),
#         'Device_Name': request.POST.get('Device_Name'),
#         'Module_Name': request.POST.get('Module_Name'),
#     }
#     serializer = DevicePermissionSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt  # <- This goes AFTER @api_view
def save_button_data(request):
    # Get the data from the request
    device_name = request.POST.get('Device_Name')
    button_id = request.POST.get('Button_Id')
    module_name = request.POST.get('Module_Name')
    operation_type = request.POST.get('Operation_Type')
    Intensity = request.POST.get('Intensity')

    # Check if the device already exists in the database
    try:
        device_permission = Device_Permission.objects.get(Device_Name=device_name)
        # If found, update the existing record
        device_permission.Module_Name = module_name
        device_permission.Button_Id = button_id
        device_permission.Operation_Type = operation_type
        device_permission.Intensity = Intensity
        device_permission.save()  # Save the updated object
        return Response(DevicePermissionSerializer(device_permission).data, status=status.HTTP_200_OK)
    except Device_Permission.DoesNotExist:
        # If not found, create a new entry
        data = {
            'Device_Name': device_name,
            'Button_Id': button_id,
            'Module_Name': module_name,
            'Operation_Type': operation_type,
            'Intensity': Intensity
        }
        serializer = DevicePermissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # Save the new object
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@csrf_exempt  # <- This goes AFTER @api_view
def get_all_device_permissions(request):
    permissions = Device_Permission.objects.all()
    serializer = DevicePermissionSerializer(permissions, many=True)
    return Response(serializer.data)

def get_sensor_data_from_queue(request):
    if request.method == "POST":
        try:
            if not data_to_android.empty():
                data = data_to_android.get(timeout=1)
                if data:
                    data = parse_uart_response(data)
                    print("Data present in queue : ",data)
                    # return JsonResponse({"response": data})
                    # Process the parsed data (e.g., send to Android)
        except Exception as e:
            print(f"Unexpected error: {e}")
    
# Function to read UART in background
def read_uart_background():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print("Raw UART:", line)
                parsed_data = parse_uart_response(line)
                if parsed_data:
                    uart_data = UartData(
                        IAQ=parsed_data.get('IAQ'),
                        PM2_5=parsed_data.get('PM2_5'),
                        PM10=parsed_data.get('PM10'),
                        CO2=parsed_data.get('CO2'),
                        TVOC_Value=parsed_data.get('TVOC_Value'),
                        TVOC_Index=parsed_data.get('TVOC_Index'),
                        Viral_Value=parsed_data.get('Viral_Value'),
                        Viral_Index=parsed_data.get('Viral_Index'),
                        Humidity=parsed_data.get('Humidity'),
                        Temperature_C=parsed_data.get('Temperature_C'),
                        Temperature_F=parsed_data.get('Temperature_F'),
                        PM1=parsed_data.get('PM1')
                    )
                    uart_data.save()
                    print("Data saved:", parsed_data)
                else:
                    print("Invalid or Unrecognized Data Format.\n")
            time.sleep(0.2)  # Adjust delay as needed
    except serial.SerialException as e:
        print("Serial Port Error:", e)
    except KeyboardInterrupt:
        print("\nStopped by user.")

# View to start UART reading and saving data
def read_uart_and_save(request):
    # Start UART reading in background thread
    threading.Thread(target=read_uart_background, daemon=True).start()
    return JsonResponse({"status": "Started UART reading in background."}, status=200)

def send_uart_command(command):
    try:
        print(f"Opening serial port {SERIAL_PORT}")
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            ser.flush()
            print(f"Sending command: {command}")
            ser.write(command.encode())

            time.sleep(0.1)
            response = ser.read_until(b"#", 100).decode(errors="ignore").strip()

            if response:
                print(f"Response received: {response}")
                return response
            else:
                print("No response received.")
                return "No response received."

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        return f"Serial Error: {e}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def session_test(request):
    request.session['test'] = 'value'
    if request.session.get('test') == 'value':
        return HttpResponse("Sessions are working!")
    return HttpResponse(" Session test failed!")


def control_device(request):
    if request.method == "POST":
        command = request.POST.get("command")
        response = send_uart_command(command)
        return JsonResponse({"command": command, "response": response})
    return render(request, "index.html")

# @csrf_exempt
# def new_index(request):
#     if request.method == "POST":
#         print("Raw body:", request.body)
#         data = urllib.parse.parse_qs(request.body.decode())
#         command = data.get("command", [None])[0]
#         print("Parsed command:", command)
#         if command:
#             return JsonResponse({"command": command, "response": "Success"})
#         else:
#             return JsonResponse({"error": "No command received"}, status=400)
#     return render(request, "new_index.html")



def home(request):
    return render(request, "index.html")

def new_ui(request):
    return render(request, "new_index.html")

def manage_button(request):
    return render(request, "manage_sensors.html")


def detection_page(request):
    return render(request, 'detection.html')


def start_detection(request):
    global detection_thread

    # Check if detection is already running
    if detection_thread and detection_thread.is_alive():
        return JsonResponse({"status": "Detection already running"})

    detection_thread = start_detection_thread()
    return JsonResponse({"status": "Detection started"})


def stop_detection_view(request):
    global stop_flag
    stop_flag = True
    return JsonResponse({"message": "Detection Stopped!"})


def sensor_data(request):
    data = {
        "temperature": 25,
        "humidity": 58,
        "detection_running": not stop_flag
    }
    return JsonResponse(data)


@csrf_exempt
def send_command_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            command = data.get("command")

            if not command:
                return JsonResponse({"error": "No command provided."}, status=400)

            response = send_uart_command(command)
            return JsonResponse({"command": command, "response": response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method allowed."}, status=405)

@csrf_exempt
def receive_post_command(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            requst_cmd.put(data)

            # Process it or push to queue
            print(f"Received: command={data}")

            return JsonResponse({'status': 'Received successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)


@csrf_exempt
def save_settings(request):
    if request.method == "POST":
        lock1_status = request.POST.get("lock1") == "on"
        lock2_status = request.POST.get("lock2") == "on"
        light1_status = request.POST.get("light1") == "on"
        light2_status = request.POST.get("light2") == "on"
# from django.shortcuts import render
# from django.http import JsonResponse
# import subprocess

# def home(request):
#     return render(request, 'index.html')

# def start_detection(request):
#     try:
#         subprocess.Popen(["python", "src/vision/object_detector.py"])  # Script path
#         return JsonResponse({"message": "Object detection started!"})
#     except Exception as e:
#         return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

# from django.shortcuts import render
# from django.http import JsonResponse
# import serial

# # Configure Serial Port
# SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your setup
# BAUD_RATE = 9600

# def send_uart_command(command):
#     try:
#         with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
#             ser.write(command.encode())
#             response = ser.readline().decode().strip()
#             return response
#     except Exception as e:
#         return str(e)

# def control_device(request):
#     if request.method == "POST":
#         command = request.POST.get("command")
#         response = send_uart_command(command)
#         return JsonResponse({"command": command, "response": response})
#     return render(request, "device_control.html")

# # Add missing views
# def home(request):
#     return render(request, "index.html")

# def start_detection(request):
#     return JsonResponse({"status": "Detection started"})


from django.shortcuts import render
from django.http import JsonResponse
import serial
import time
# Configure Serial Port
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your setup
BAUD_RATE = 115200

def send_uart_command(command):
    try:
        print(f"Opening serial port {SERIAL_PORT}")
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as ser:
            time.sleep(1)  # Allow serial port to initialize
            
            ser.flush()  # Clear any old data
            print(f"Sending command: {command}")
            ser.write(command.encode())  # Send command

            time.sleep(2)  # Wait for device response
            response = ser.read(500).decode().strip()  # Read response
            
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

def control_device(request):
    if request.method == "POST":
        command = request.POST.get("command")
        response = send_uart_command(command)
        return JsonResponse({"command": command, "response": response})
    return render(request, "index.html")  # Make sure "index.html" exists

def home(request):
    return render(request, "index.html")

def start_detection(request):
    return JsonResponse({"status": "Detection started"})

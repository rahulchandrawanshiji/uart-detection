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


# from django.shortcuts import render
# from django.http import JsonResponse
# import serial
# import time
# # Configure Serial Port
# SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your setup
# BAUD_RATE = 115200

# def send_uart_command(command):
#     try:
#         print(f"Opening serial port {SERIAL_PORT}")
#         with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as ser:
#             time.sleep(1)  # Allow serial port to initialize
            
#             ser.flush()  # Clear any old data
#             print(f"Sending command: {command}")
#             ser.write(command.encode())  # Send command

#             time.sleep(2)  # Wait for device response
#             response = ser.read(500).decode().strip()  # Read response
            
#             if response:
#                 print(f"Response received: {response}")
#                 return response
#             else:
#                 print("No response received.")
#                 return "No response received."

#     except serial.SerialException as e:
#         print(f"Serial Error: {e}")
#         return f"Serial Error: {e}"
#     except Exception as e:
#         print(f"Error: {e}")
#         return f"Error: {e}"

# def control_device(request):
#     if request.method == "POST":
#         command = request.POST.get("command")
#         response = send_uart_command(command)
#         return JsonResponse({"command": command, "response": response})
#     return render(request, "index.html")  # Make sure "index.html" exists

# def home(request):
#     return render(request, "index.html")

# def start_detection(request):
#     return JsonResponse({"status": "Detection started"})

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import serial
import time
import cv2
from ultralytics import YOLO
from django.views.decorators.csrf import csrf_exempt

# Configure Serial Port
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your setup
BAUD_RATE = 115200

# YOLO Model Setup
model = YOLO("yolov8n.pt")
stop_flag = False  # Global flag for object detection


# ==============================
# ✅ Existing Serial Communication Views (No Changes)
# ==============================
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
    return render(request, "index.html")

def home(request):
    return render(request, "index.html")

def start_detection(request):
    return JsonResponse({"status": "Detection started"})


# ==============================
# ✅ New Object Detection Views (Safely Added)
# ==============================

def detection_page(request):
    """Render the object detection UI."""
    return render(request, 'detection.html')

def generate_frames():
    """Capture and process frames with YOLO."""
    global stop_flag
    cap = cv2.VideoCapture(0)

    while not stop_flag:
        success, frame = cap.read()
        if not success:
            break

        # YOLO Object Detection
        results = model(frame)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = model.names[cls]

                if conf > 0.5:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label}: {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

def video_feed(request):
    """Provide the live video stream."""
    global stop_flag
    stop_flag = False  # Reset stop flag when starting detection
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def stop_detection(request):
    """Stop object detection."""
    global stop_flag
    stop_flag = True
    return JsonResponse({"message": "Detection Stopped!"})

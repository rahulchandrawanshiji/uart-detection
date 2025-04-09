# from django.shortcuts import render
# from django.http import JsonResponse, StreamingHttpResponse
# import serial
# import time
# import cv2
# import numpy as np
# import json
# import threading
# from django.views.decorators.csrf import csrf_exempt
# from django.http import StreamingHttpResponse, JsonResponse
# from django.shortcuts import render

# frame_buffer = None
# frame_lock = threading.Lock()
# stop_flag = False
# detection_thread = None

# # Serial Configuration
# SERIAL_PORT = "/dev/ttyUSB0"
# BAUD_RATE = 115200

# # Global flags
# stop_flag = False
# detection_thread = None


# def send_uart_command(command):
#     try:
#         print(f"Opening serial port {SERIAL_PORT}")
#         with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
#             ser.flush()
#             print(f"Sending command: {command}")
#             ser.write(command.encode())

#             time.sleep(0.1)
#             response = ser.read_until(b"#", 100).decode(errors="ignore").strip()

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
#     return render(request, "index.html")


# def home(request):
#     return render(request, "index.html")


# def detection_page(request):
#     return render(request, 'detection.html')


# def generate_frames():
#     global stop_flag, frame_buffer

#     # Load YOLOv4-tiny
#     net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
#     net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#     net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

#     with open("coco.names", "r") as f:
#         classes = [line.strip() for line in f.readlines()]

#     layer_names = net.getLayerNames()
#     output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

#     try:
#         while not stop_flag:
#             ret, frame = cap.read()
#             if not ret:
#                 continue

#             height, width = frame.shape[:2]
#             blob = cv2.dnn.blobFromImage(frame, 1/255.0, (320, 320), swapRB=True, crop=False)
#             net.setInput(blob)
#             start = time.time()
#             outs = net.forward(output_layers)
#             end = time.time()

#             boxes, confidences, class_ids = [], [], []

#             for out in outs:
#                 for detection in out:
#                     scores = detection[5:]
#                     class_id = int(np.argmax(scores))
#                     confidence = scores[class_id]
#                     if confidence > 0.5:
#                         center_x, center_y, w, h = (detection[0:4] * [width, height, width, height]).astype("int")
#                         x = int(center_x - w / 2)
#                         y = int(center_y - h / 2)
#                         boxes.append([x, y, int(w), int(h)])
#                         confidences.append(float(confidence))
#                         class_ids.append(class_id)

#             indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

#             if len(indexes) > 0:
#                 for i in indexes.flatten():
#                     x, y, w, h = boxes[i]
#                     label = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                     cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#             fps = 1 / (end - start)
#             cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

#             _, buffer = cv2.imencode('.jpg', frame)
#             with frame_lock:
#                 frame_buffer = buffer.tobytes()

#             time.sleep(0.05)

#     finally:
#         print("Releasing camera after detection stop.")
#         cap.release()




# def generate_frames_wrapper():
#     for _ in generate_frames():
#         if stop_flag:
#             break


# def video_feed(request):
#     def frame_generator():
#         global frame_buffer
#         while not stop_flag:
#             with frame_lock:
#                 if frame_buffer:
#                     yield (b'--frame\r\n'
#                            b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
#             time.sleep(0.05)

#     return StreamingHttpResponse(frame_generator(), content_type='multipart/x-mixed-replace; boundary=frame')



# def start_detection(request):
#     global stop_flag, detection_thread

#     if detection_thread and detection_thread.is_alive():
#         return JsonResponse({"status": "Detection already running"})

#     stop_flag = False
#     detection_thread = threading.Thread(target=generate_frames_wrapper)
#     detection_thread.start()
#     return JsonResponse({"status": "Detection started"})


# @csrf_exempt
# def stop_detection(request):
#     global stop_flag
#     stop_flag = True
#     return JsonResponse({"message": "Detection Stopped!"})


# def sensor_data(request):
#     data = {
#         "temperature": 25,
#         "humidity": 58,
#         "detection_running": not stop_flag
#     }
#     return JsonResponse(data)


# @csrf_exempt
# def send_command_api(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             command = data.get("command")

#             if not command:
#                 return JsonResponse({"error": "No command provided."}, status=400)

#             response = send_uart_command(command)
#             return JsonResponse({"command": command, "response": response})

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     else:
#         return JsonResponse({"error": "Only POST method allowed."}, status=405)





from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import serial
import time
import cv2
import numpy as np
import json
import threading
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render

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


def control_device(request):
    if request.method == "POST":
        command = request.POST.get("command")
        response = send_uart_command(command)
        return JsonResponse({"command": command, "response": response})
    return render(request, "index.html")


def home(request):
    return render(request, "index.html")


def detection_page(request):
    return render(request, 'detection.html')


def generate_frames():
    global stop_flag, frame_buffer

    net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    import uuid
    from datetime import datetime, timedelta
    import os

    os.makedirs("detected_images", exist_ok=True)

    last_saved_time = datetime.min
    save_interval = timedelta(seconds=5)

    detected_classes = set()  # Store object classes already captured

    try:
        while not stop_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            height, width = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (320, 320), swapRB=True, crop=False)
            net.setInput(blob)
            start = time.time()
            outs = net.forward(output_layers)
            end = time.time()

            boxes, confidences, class_ids = [], [], []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = int(np.argmax(scores))
                    confidence = scores[class_id]
                    if confidence > 0.7:
                        center_x, center_y, w, h = (detection[0:4] * [width, height, width, height]).astype("int")
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, int(w), int(h)])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            new_detection = False

            if len(indexes) > 0:
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]
                    class_id = class_ids[i]
                    label = f"{classes[class_id]}: {confidences[i]:.2f}"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # If object not already captured, mark for saving
                    if class_id not in detected_classes:
                        new_detection = True
                        detected_classes.add(class_id)

                # Save image only if a new object class is detected and after interval
                if new_detection and datetime.now() - last_saved_time > save_interval:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"detected_{timestamp}_{uuid.uuid4().hex[:6]}.jpg"
                    cv2.imwrite(f"detected_images/{filename}", frame)
                    last_saved_time = datetime.now()

            fps = 1 / (end - start)
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            with frame_lock:
                frame_buffer = buffer.tobytes()

            time.sleep(0.05)

    finally:
        print("Releasing camera after detection stop.")
        cap.release()







def generate_frames_wrapper():
    for _ in generate_frames():
        if stop_flag:
            break


def video_feed(request):
    def frame_generator():
        global frame_buffer
        while not stop_flag:
            with frame_lock:
                if frame_buffer:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
            time.sleep(0.05)

    return StreamingHttpResponse(frame_generator(), content_type='multipart/x-mixed-replace; boundary=frame')



def start_detection(request):
    global stop_flag, detection_thread

    if detection_thread and detection_thread.is_alive():
        return JsonResponse({"status": "Detection already running"})

    stop_flag = False
    detection_thread = threading.Thread(target=generate_frames_wrapper)
    detection_thread.start()
    return JsonResponse({"status": "Detection started"})


@csrf_exempt
def stop_detection(request):
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
import time
import uuid
import os
import cv2
import serial
import threading
import numpy as np
from datetime import datetime, timedelta
# from ui_app.models import DetectedImage
# from django.http import JsonResponse, StreamingHttpResponse

# Globals
stop_flag = False
frame_buffer = None
frame_lock = threading.Lock()

# Initialize UART once
uart_port = '/dev/ttyUSB0'
uart_baudrate = 115200
uart_timeout = 1
uart_lock = threading.Lock()

# try:
#     ser = serial.Serial(uart_port, uart_baudrate, timeout=uart_timeout)
#     print(f"[UART] connected to {uart_port}")
# except Exception as e:
#     print(f"[UART] Failed to connect to {uart_port}: {e}")
#     ser = None

# def send_uart_command(command):
#     global ser
#     if ser and ser.is_open:
#         try:
#             with uart_lock:
#                 ser.write(command.encode())
#                 print(f"[UART] Sent: {command.strip()}")
#         except Exception as e:
#             print(f"[UART] Error sending command: {e}")
#     else:
#         print("[UART] Serial not open or available")

def generate_frames():
    global stop_flag, frame_buffer

    # Load YOLO model
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

    os.makedirs("detected_images", exist_ok=True)
    last_saved_time = datetime.min
    save_interval = timedelta(seconds=5)
    detected_classes = set()
    last_uart_sent_time = datetime.min
    uart_send_interval = timedelta(seconds=10)

    try:
        while not stop_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            height, width = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (320, 320), swapRB=True, crop=False)
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
            head_count = 0
            object_names = []

            if len(indexes) > 0:
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]
                    class_id = class_ids[i]
                    label = f"{classes[class_id]}: {confidences[i]:.2f}"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    if class_id not in detected_classes:
                        new_detection = True
                        detected_classes.add(class_id)

                    name = classes[class_id]
                    object_names.append(name)
                    if name == "person":
                        head_count += 1

                # Save image and DB entry
                if new_detection and datetime.now() - last_saved_time > save_interval:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"detected_{timestamp}_{uuid.uuid4().hex[:6]}.jpg"
                    filepath = f"detected_images/{filename}"
                    cv2.imwrite(filepath, frame)
                    last_saved_time = datetime.now()

                #     try:
                #         detected_image = DetectedImage.objects.create(
                #             image_path=filepath,
                #             detected_objects=", ".join(set(object_names)),
                #             head_count=head_count
                #         )
                #         print(f"[DB] Saved Image ID: {detected_image.id}, Head Count: {head_count}")
                #     except Exception as e:
                #         print(f"[DB] Failed to save: {e}")

                    #  UART condition: send real-time data
                    try:
                        now = datetime.now()
                        timestamp_str = now.strftime("%Y%m%d_%H%M%S")  # Clean format
                        image_filename = os.path.basename(filepath)  # Only filename, not full path
                        object_str = '+'.join(object_names)  # Convert list to joined string

                        uart_string = f"$D10|{object_str}|{head_count}|{timestamp_str}|{image_filename}#"
                        # send_uart_command(uart_string)
                        print(">>[UART] Sent:", uart_string)
                    except Exception as e:
                        print("[UART] Error sending data:", e)

            #  UART condition: send if head count >= 10
            if head_count >= 10 and datetime.now() - last_uart_sent_time > uart_send_interval:
                # send_uart_command('$C03,99,01#')  # Example UART command
                print(">>[UART] send head count")
                last_uart_sent_time = datetime.now()

            fps = 1 / (end - start)
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            _, buffer = cv2.imencode('.jpg', frame)
            with frame_lock:
                frame_buffer = buffer.tobytes()

            time.sleep(0.05)

    finally:
        print("Releasing camera after detection stop.")
        cap.release()


def start_detection_thread():
    global stop_flag
    stop_flag = False
    detection_thread = threading.Thread(target=generate_frames)
    detection_thread.start()
    return detection_thread

def stop_detection(request):
    global stop_flag
    stop_flag = True
    return JsonResponse({"message": "Detection Stopped!"})

def video_feed(request):
    def generate():
        global frame_buffer
        while True:
            with frame_lock:
                if frame_buffer is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n\r\n')
            time.sleep(0.05)
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

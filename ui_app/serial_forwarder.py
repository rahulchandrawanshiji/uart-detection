# # ui_app/serial_forwarder.py

# import serial
# import time
# import threading

# running = False  # Prevent multiple threads from starting

# def setup_serial(port, baudrate=115200, timeout=1):
#     return serial.Serial(port, baudrate, timeout=timeout)

# def forward_data(source, destination):
#     print(f"Forwarding data from {source.port} to {destination.port}...")
#     try:
#         while running:
#             if source.in_waiting:
#                 data = source.readline().decode('utf-8', errors='ignore').strip()
#                 if data:
#                     print(f"Received from {source.port}: {data}")
#                     destination.write((data + '\n').encode())
#                     print(f"Sent to {destination.port}: {data}")
#             time.sleep(0.1)
#     except Exception as e:
#         print(f"Serial forwarding stopped due to error: {e}")
#     finally:
#         for s in [source, destination]:
#             if s and s.is_open:
#                 s.close()
#                 print(f"Closed port {s.port}")

# def start_forwarding():
#     global running
#     if running:
#         print("Serial forwarding already running.")
#         return
#     running = True

#     try:
#         ser_in = setup_serial('/dev/ttyUSB0')
#         ser_out = setup_serial('/dev/ttyUSB1')
#         t = threading.Thread(target=forward_data, args=(ser_in, ser_out), daemon=True)
#         t.start()
#         print("Serial forwarding thread started.")
#     except serial.SerialException as e:
#         print(f"Failed to start serial forwarding: {e}")
# ui_app/serial_forwarder.py

import serial
import time
import threading
import datetime
import os

running = False  # Prevent multiple threads from starting

def setup_serial(port, baudrate=115200, timeout=1):
    return serial.Serial(port, baudrate, timeout=timeout)

def set_system_time_from_timestamp(ts):
    try:
        # Convert the Unix timestamp into local time (Asia/Kolkata already set)
        dt_local = datetime.datetime.fromtimestamp(ts)
        formatted_time = dt_local.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Setting system time to: {formatted_time}")

        # Set system time
        os.system(f"sudo date -s \"{formatted_time}\"")
        # Sync hardware clock
        os.system("sudo hwclock -w")

    except Exception as e:
        print(f"Error setting system time: {e}")

def forward_data(source, destination):
    print(f"Forwarding data from {source.port} to {destination.port}...")
    try:
        while running:
            if source.in_waiting:
                data = source.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    print(f"Received from {source.port}: {data}")
                    
                    # Check if the data is a timestamp
                    if data.startswith("timestamp:"):
                        try:
                            ts = int(data.split(":")[1])
                            set_system_time_from_timestamp(ts)
                        except ValueError:
                            print(f"Invalid timestamp received: {data}")

                    destination.write((data + '\n').encode())
                    print(f"Sent to {destination.port}: {data}")
            time.sleep(0.1)
    except Exception as e:
        print(f"Serial forwarding stopped due to error: {e}")
    finally:
        for s in [source, destination]:
            if s and s.is_open:
                s.close()
                print(f"Closed port {s.port}")

def start_forwarding():
    global running
    if running:
        print("Serial forwarding already running.")
        return
    running = True

    try:
        ser_in = setup_serial('/dev/ttyUSB0')
        ser_out = setup_serial('/dev/ttyUSB1')
        t = threading.Thread(target=forward_data, args=(ser_in, ser_out), daemon=True)
        t.start()
        print("Serial forwarding thread started.")
    except serial.SerialException as e:
        print(f"Failed to start serial forwarding: {e}")

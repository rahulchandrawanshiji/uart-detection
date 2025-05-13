import serial
import time
import queue
from queue import Empty
import threading
from datetime import datetime
import json
import re
from .shared_queue import requst_cmd
from .shared_queue import data_to_android

# Queue initialization
#data_to_android = queue.Queue()

def read_from_ports(hardware_port):
    print(f"Reading from {hardware_port.port}")

    try:
        while True:
            # Read hardware_port [Response and Continous data will come]
            if hardware_port.in_waiting:
                data1 = hardware_port.readline().decode('utf-8', errors='ignore').strip()
                if data1:
                    print(f"[{hardware_port.port}] Hardware Received: {data1}")
                    data_to_android.put(data1)
                
            # Read android_port [Requests will come]
            # if android_port.in_waiting:
            #     data2 = android_port.readline().decode('utf-8', errors='ignore').strip()
            #     if data2:
            #         print(f"[{android_port.port}] Android Received: {data2}")
            #         requst_cmd.put(data2)

            time.sleep(0.1)           

    except KeyboardInterrupt:
        print("\nStopped reading.")
        hardware_port.close()
        # android_port.close()

def send_cmd_hardware(hardware_port):
    while True: 
        try:
            if requst_cmd or requst_cmd.strip()!="":
                json_str=requst_cmd.get(timeout=1)
                print(">>> Request Command Received....")
                print(json_str)
                #parts = re.findall(r'\{.*?\}', json_str)
                #json_str = parts[0]
                if json_str:
                    command = json_str #json.loads(json_str)
                    action = command.get("action")
                    uart_cmd = ""

                    if action == "lock_operate":
                        uart_cmd = f"$C01,{command['lock_no']},{command['state']}#"
                    elif action == "lock_status":
                        uart_cmd = f"$C11,{command['lock_no']},00#"
                    elif action == "fan_operate":
                        uart_cmd = f"$C02,{command['fan_no']},{command['state']}#"
                    elif action == "fan_status":
                        uart_cmd = f"$C12,{command['fan_no']},00#"
                    elif action == "fan_dimming":
                        uart_cmd = f"$C04,{command['fan_no']},{command['speed']}#"
                    elif action == "light_operate":
                        uart_cmd = f"$C03,{command['light_no']},{command['state']}#"
                    elif action == "light_status":
                        uart_cmd = f"$C13,{command['light_no']},00#"
                    elif action == "light_dimming":
                        uart_cmd = f"$C05,{command['light_no']},{command['intensity']}#"
                    elif action == "led_operate":
                        uart_cmd = f"$C06,{command['led_no']},{command['state']}#"
                    elif action == "all_locks":
                        uart_cmd = f"$C01,99,{command['state']}#"
                    elif action == "all_fans":
                        uart_cmd = f"$C02,99,{command['state']}#"
                    elif action == "all_lights":
                        uart_cmd = f"$C03,99,{command['state']}#"
                    elif action == "all_leds":
                        uart_cmd = f"$C06,99,{command['state']}#"
                    else:
                        print(f"Unknown action: {action}")
                        
                    print(">>> Sending command to hardware."+ uart_cmd)
                    hardware_port.write(uart_cmd.encode())
                    requst_cmd.task_done
        except Empty:
            print("No command received yet.")
        except json.JSONDecodeError:
            print("Invalid JSON received.")
            #return None
        except KeyError as e:
            print(f"Missing key in JSON: {e}")
            #return None

def parse_uart_response(uart_str):
    try:
        response_json=""
        if uart_str.startswith("$D01,") and uart_str.endswith("#"):
            uart_str = uart_str.strip("#").replace("$D01,", "")
            parts = uart_str.split(",")
            data = {}

            mapping = {
                "01": "IAQ",
                "02": "PM2_5",
                "03": "PM10",
                "04": "CO2",
                "05": "TVOC_Value",
                "06": "TVOC_Index",
                "07": "Viral_Value",
                "08": "Viral_Index",
                "09": "Humidity",
                "10": "Temperature_C",
                "11": "Temperature_F",
                "12": "PM1"
            }

            for part in parts:
                key, value = part.split(":")
                label = mapping.get(key, f"Unknown_{key}")
                data[label] = int(value)
            response_json = json.dumps(data)
            return response_json
        elif uart_str.startswith(("$A", "$R")) and uart_str.endswith("#"):
            parts = uart_str[1:-1].split(",")
            cmd = parts[0]
            device_no = parts[1]
            state = parts[2]

            # Handle $A responses (for status)
            
            if cmd == "A01":  # Lock
                response_json= json.dumps({"response": "lock_status", "lock_no": device_no, "state": state})
            elif cmd == "A02":  # Fan
                response_json= json.dumps({"response": "fan_status", "fan_no": device_no, "state": state})
            elif cmd == "A03":  # Light
                response_json= json.dumps({"response": "light_status", "light_no": device_no, "state": state})
            elif cmd == "A04":  # Fan dimming
                response_json= json.dumps({"response": "fan_dimming", "fan_no": device_no, "speed": state})
            elif cmd == "A05":  # Light dimming
                response_json= json.dumps({"response": "light_dimming", "light_no": device_no, "intensity": state})
            elif cmd == "A06":  # LED
                response_json= json.dumps({"response": "led_status", "led_no": device_no, "state": state})

            # Handle $R responses (for lock/fan/light status)
            elif cmd == "R11":  # Lock status response
                response_json= json.dumps({"response": "lock_status", "lock_no": device_no, "state": state})
            elif cmd == "R12":  # Fan status response
                response_json= json.dumps({"response": "fan_status", "fan_no": device_no, "state": state})
            elif cmd == "R13":  # Light status response
                response_json= json.dumps({"response": "light_status", "light_no": device_no, "state": state})
            else:
                print(f"Unknown UART response command: {cmd}")
                response_json= None
            return response_json
        else:
            print(f"Ignoring invalid UART response: {uart_str}")
            return None
    except Exception as e:
        print(f"Error parsing UART response: {e}")
        return None
    
def process_and_data_to_android(android_port):
    while True:
        try:
            if data_to_android:
                data = data_to_android.get(timeout=1)
                if data:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] [Hardware → {android_port.port}]: {data}")
                    data=parse_uart_response(data)
                    android_port.write((data).encode('utf-8'))
                    data_to_android.task_done()
                    time.sleep(0.1)
        except queue.Empty:
            continue # Nothing to send, loop again

def start_serial_thread():
    try:
        hardware_port = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
        # android_port = serial.Serial('/dev/ttyUSB1', baudrate=115200, timeout=1)

        # Start reading in a separate thread
        threading.Thread(target=read_from_ports, args=(hardware_port,), daemon=True).start()

        # Start the sending thread (send everything from queue to hardware_port)
        #threading.Thread(target=process_and_data_to_android, args=(android_port,), daemon=True).start()

        threading.Thread(target=send_cmd_hardware, args=(hardware_port,), daemon=True).start()

        # Keep main thread alive
        # while True:
        #     time.sleep(1)

    except serial.SerialException as e:
        print(f"Serial Error: {e}")

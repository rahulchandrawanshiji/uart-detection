import serial
import time
import json
import threading
import datetime
import os


running = False  # Prevent multiple threads from starting

# Setup serial connection with given port and settings
def setup_serial(port, baudrate=115200, timeout=1):
    return serial.Serial(port, baudrate, timeout=timeout)

# Convert incoming JSON command to UART command string
def convert_json_to_uart(json_str):
    try:
        command = json.loads(json_str)
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
            return None

        return uart_cmd

    except json.JSONDecodeError:
        print("Invalid JSON received.")
        return None
    except KeyError as e:
        print(f"Missing key in JSON: {e}")
        return None


# Parse UART response (like $A01,01,00# or $R11,01,00#) and return JSON string
def parse_uart_response(uart_str):
    try:
        if uart_str.startswith(("$A", "$R")) and uart_str.endswith("#"):
            parts = uart_str[1:-1].split(",")
            cmd = parts[0]
            device_no = parts[1]
            state = parts[2]

            # Handle $A responses (for status)
            if cmd == "A01":  # Lock
                return json.dumps({"response": "lock_status", "lock_no": device_no, "state": state})
            elif cmd == "A02":  # Fan
                return json.dumps({"response": "fan_status", "fan_no": device_no, "state": state})
            elif cmd == "A03":  # Light
                return json.dumps({"response": "light_status", "light_no": device_no, "state": state})
            elif cmd == "A04":  # Fan dimming
                return json.dumps({"response": "fan_dimming", "fan_no": device_no, "speed": state})
            elif cmd == "A05":  # Light dimming
                return json.dumps({"response": "light_dimming", "light_no": device_no, "intensity": state})
            elif cmd == "A06":  # LED
                return json.dumps({"response": "led_status", "led_no": device_no, "state": state})

            # Handle $R responses (for lock/fan/light status)
            elif cmd == "R11":  # Lock status response
                return json.dumps({"response": "lock_status", "lock_no": device_no, "state": state})
            elif cmd == "R12":  # Fan status response
                return json.dumps({"response": "fan_status", "fan_no": device_no, "state": state})
            elif cmd == "R13":  # Light status response
                return json.dumps({"response": "light_status", "light_no": device_no, "state": state})
            else:
                print(f"Unknown UART response command: {cmd}")
                return None
        else:
            print(f"Ignoring invalid UART response: {uart_str}")
            return None
    except Exception as e:
        print(f"Error parsing UART response: {e}")
        return None

def update_raspberry_pi_time(ts_string):
    try:
        ts = int(ts_string)
        dt_local = datetime.datetime.fromtimestamp(ts)
        formatted_time = dt_local.strftime("%Y-%m-%d %H:%M:%S")
        print("Setting Pi Time to:", formatted_time)

        os.system(f"sudo date -s \"{formatted_time}\"")
        os.system("sudo hwclock -w")
    except Exception as e:
        print(f"Failed to set time: {e}")

# Core forwarding logic between serial ports
def forward_data(source, destination):
    print(f"Forwarding data from {source.port} to {destination.port}...")
    try:
        while running:
            # If incoming data from source port (e.g., /dev/ttyUSB0)
            if source.in_waiting:
                json_data = source.readline().decode('utf-8', errors='ignore').strip()
                if json_data:
                     # 🔥 Check if this is a timestamp update
                    if json_data.startswith("timestamp:"):
                        ts = json_data.split(":")[1]
                        update_raspberry_pi_time(ts)
                        continue  # Don't forward timestamp, skip rest of loop
                    
                    print(f"Received JSON: {json_data}")
                    uart_cmd = convert_json_to_uart(json_data)

                    # Send UART command to hardware
                    if uart_cmd:
                        destination.write((uart_cmd + '\n').encode())
                        print(f"Sent UART: {uart_cmd}")

                        # Wait and read UART response from hardware
                        time.sleep(0.1)
                        if destination.in_waiting:
                            uart_response = destination.readline().decode('utf-8', errors='ignore').strip()
                            print(f"Received UART response: {uart_response}")
                            json_response = parse_uart_response(uart_response)

                            # Send parsed response back as JSON
                            if json_response:
                                source.write((json_response + '\n').encode())  #  full JSON as a string
                                print(f"Sent JSON Response: {json_response}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped forwarding.")

# Start the serial forwarding in a separate thread to prevent blocking
def start_forwarding():
    global running
    if running:
        print("Serial forwarding already running.")
        return
    running = True

    try:
        # Set up serial connections
        ser_in = setup_serial('/dev/ttyUSB1', timeout=1)  # Incoming JSON commands
        ser_out = setup_serial('/dev/ttyUSB0', timeout=1)  # Outgoing UART commands

        # Start the forwarding thread
        t = threading.Thread(target=forward_data, args=(ser_in, ser_out), daemon=True)
        t.start()
        
        print("Serial forwarding thread started.")

    except serial.SerialException as e:
        print(f"Failed to start serial forwarding: {e}")

# Main function to initialize the serial forwarding
if __name__ == "__main__":
    start_forwarding()

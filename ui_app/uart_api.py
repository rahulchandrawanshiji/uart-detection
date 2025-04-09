from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import serial
import time
import threading

# Serial config
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your setup
BAUD_RATE = 115200

serial_lock = threading.Lock()

def send_uart_command(command):
    try:
        with serial_lock:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5) as ser:
                time.sleep(1)
                ser.flush()
                ser.write(command.encode())
                time.sleep(2)
                response = ser.read(500).decode().strip()
                return response if response else "No response received."
    except Exception as e:
        return f"Error: {str(e)}"

# Helper function
def handle_command_response(command):
    response = send_uart_command(command)
    return JsonResponse({"command": command, "response": response})


#  Fan Control
@csrf_exempt
def fan_on(request):
    return handle_command_response("$C02,99,01#")

@csrf_exempt
def fan_off(request):
    return handle_command_response("$C02,99,00#")

@csrf_exempt
def fan_status(request):
    return handle_command_response("$C12,99,00#")


#  Lock Control
@csrf_exempt
def lock_open(request):
    return handle_command_response("$C01,99,01#")

@csrf_exempt
def lock_close(request):
    return handle_command_response("$C01,99,00#")


#  Light Control (updated to correct working commands)
@csrf_exempt
def light_on(request):
    return handle_command_response("$C03,01,01#")  

@csrf_exempt
def light_off(request):
    return handle_command_response("$C03,01,00#")

@csrf_exempt
def light_all_on(request):
    return handle_command_response("$C03,99,01#") 

@csrf_exempt
def light_all_off(request):
    return handle_command_response("$C03,99,00#")  # All Lights Off

@csrf_exempt
def light_status(request):
    return handle_command_response("$C03,99,00#")  # Get Light 1 Status


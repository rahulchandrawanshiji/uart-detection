import serial
import time

def parse_uart_response(response):
    if not response.startswith("$D01,") or not response.endswith("#"):
        return None  # Invalid format

    response = response.strip("#").replace("$D01,", "")
    parts = response.split(",")
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

    return data

# ✅ For Django background usage
def read_uart_background():
    import os
    import django
    from django.utils.timezone import now

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_ui_project.settings")
    django.setup()

    from .models import UartData

    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)
        print("Listening on /dev/ttyUSB1 for UART background...\n")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("Raw UART:", line)
                parsed = parse_uart_response(line)
                if parsed:
                    print("Parsed Data:", parsed)
                    UartData.objects.create(**parsed, timestamp=now())
            time.sleep(0.2)

    except serial.SerialException as e:
        print("UART Serial Error:", e)
    except Exception as e:
        print("UART Reader Error:", e)

# ✅ For standalone script usage
def main():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)
        print("Listening on /dev/ttyUSB1...\n")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("Raw UART:", line)
                parsed_data = parse_uart_response(line)
                if parsed_data:
                    print("Parsed Data:", parsed_data)
                else:
                    print("Invalid UART response")
            time.sleep(0.1)

    except serial.SerialException as e:
        print("Serial Port Error:", e)
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()

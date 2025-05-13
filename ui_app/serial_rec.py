# import serial
# import time

# def main():
#     try:
#         ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)
#         print("Listening on /dev/ttyUSB0...\n")

#         while True:
#             line = ser.readline().decode('utf-8', errors='ignore').strip()
#             if line:
#                 print("Raw UART:", line)
#             time.sleep(0.1)

#     except serial.SerialException as e:
#         print("Serial Port Error:", e)
#     except KeyboardInterrupt:
#         print("\nStopped by user.")

# if __name__ == "__main__":
#     main()

# # uart_parser.py

# def parse_uart_response(response):
#     if not response.startswith("$D01,") or not response.endswith("#"):
#         return None  # Invalid format

#     response = response.strip("#").replace("$D01,", "")
#     parts = response.split(",")
#     data = {}

#     mapping = {
#         "01": "IAQ",
#         "02": "PM2_5",
#         "03": "PM10",
#         "04": "CO2",
#         "05": "TVOC_Value",
#         "06": "TVOC_Index",
#         "07": "Viral_Value",
#         "08": "Viral_Index",
#         "09": "Humidity",
#         "10": "Temperature_C",
#         "11": "Temperature_F",
#         "12": "PM1"
#     }

#     for part in parts:
#         key, value = part.split(":")
#         label = mapping.get(key, f"Unknown_{key}")
#         data[label] = int(value)

#     return data


# # Example usage
# if __name__ == "__main__":
#     uart_data = "$D01,01:0036,02:0013,03:0013,04:0471,05:0000,06:0000,07:0000,08:0000,09:0034,10:0033,11:0092,12:0012#"
#     parsed = parse_uart_response(uart_data)
#     if parsed:
#         print("Parsed Data:", parsed)
#     else:
#         print("Invalid UART response")
import serial
import time

# uart_parser.py

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

# Main Script
def main():
    try:
        # Initialize the serial port (change the port if needed)
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)
        print("Listening on /dev/ttyUSB0...\n")

        while True:
            # Read the incoming line from UART
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            # If line is not empty, process it
            if line:
                print("Raw UART:", line)
                
                # Parse the response using the parsing function
                parsed_data = parse_uart_response(line)
                
                # If valid parsed data, print it
                if parsed_data:
                    print("Parsed Data:", parsed_data)
                else:
                    print("Invalid UART response")
            
            time.sleep(0.1)  # Wait briefly before the next read

    except serial.SerialException as e:
        print("Serial Port Error:", e)
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()


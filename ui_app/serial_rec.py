import serial

# Replace with your actual serial port and baud rate
SERIAL_PORT = '/dev/ttyUSB1'  # e.g., COM3 on Windows, /dev/ttyUSB0 on Linux
BAUD_RATE = 115200

def send_data(ser, message):
    """
    Function to send data over the serial connection.
    """
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.write(message.encode('utf-8'))
    print(f"Sent: {message}")
def read_serial():
    try:
        # Open the serial port
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")

        while True:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').strip()
                print(f"Received: {data}")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    read_serial()

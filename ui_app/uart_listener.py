import threading
import time
import serial  # or socket if you're using TCP/UDP for mobile comm

def uart_listener():
    while True:
        try:
            # Example logic for receiving from mobile and sending to UART
            # This could be TCP socket listening or Bluetooth etc.
            # And send command to UART like:
            # uart.write(received_data)
            print("Listening for mobile commands...")
            time.sleep(2)
        except Exception as e:
            print(f"Error in listener: {e}")

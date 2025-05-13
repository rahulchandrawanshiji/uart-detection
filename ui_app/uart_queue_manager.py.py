# import serial
# import threading
# import time
# from queue import Queue

# # Create a queue to hold UART commands
# uart_queue = Queue()
# # Open the serial port (with a small timeout to avoid blocking)
# uart_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, exclusive=False)

# # Worker function to process UART commands from the queue
# def uart_worker():
#     while True:
#         command = uart_queue.get()
#         if command:
#             try:
#                 # Ensure the serial port is open before sending the command
#                 if uart_port.is_open:
#                     uart_port.write((command + '\n').encode('utf-8'))
#                     print(f"[UART] Sent: {command}")
#                 else:
#                     print("[UART] Port is not open.")
#             except Exception as e:
#                 print(f"[UART] Write error: {e}")
#         uart_queue.task_done()
#         time.sleep(0.1)  # prevent spamming

# # Start the worker thread
# def start_uart_queue():
#     threading.Thread(target=uart_worker, daemon=True).start()

# # Function to add UART commands to the queue
# def send_to_uart(command: str):
#     uart_queue.put(command)

# # Example usage of send_to_uart
# # Uncomment the following lines to start the thread and send commands
# # start_uart_queue()
# # send_to_uart('$C01,99,00#')

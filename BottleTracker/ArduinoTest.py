import serial
import time

# Python side: sends bytes to Arduino over COM3

serialPort = "COM3"   # change if your Arduino is on another port
baudrate  = 115200
timeout   = 1

try:
    arduino = serial.Serial(port=serialPort, baudrate=baudrate, timeout=timeout)
    time.sleep(2)  # wait for Arduino to reset

    print("Connected to", arduino.name)
    print("Sending 120 every 0.5 seconds. Press Ctrl+C to stop.\n")

    while True:
        outputX = 90
        arduino.write(f"{outputX}\n".encode())
        print(f"Sent: {outputX}")

        time.sleep(0.5)

except serial.SerialException as e:
    print("Serial error:", e)
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    arduino.close()
    print("Serial port closed")
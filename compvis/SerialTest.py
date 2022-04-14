import serial
import time
import struct

def main():
    distance = 215.863972    # actual float value: 215.8639678955078125 (43 57 dd 2d)
    orientation = 182.379814 # actual float value: 182.3798065185546875 (43 36 61 3b)
    packet = struct.pack('!2f', distance, orientation)

    # print("packet: ", end='')
    # print(' '.join([f'{b:02x}' for b in packet[:4]]), 
    #     '/', 
    #     ' '.join([f'{b:02x}' for b in packet[4:]]),
    #     )

    ser = serial.Serial('/dev/cu.usbmodem1101', baudrate=9600, timeout=1)
    ser.reset_input_buffer()

    while True:
        ser.write(packet)
        time.sleep(1)

if __name__ == '__main__':
    main()

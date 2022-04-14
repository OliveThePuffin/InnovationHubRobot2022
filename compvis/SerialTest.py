import serial
import time
import ctypes

def make_arduino_info(distance, orientation):
    c_distance = ctypes.c_float(distance)
    bytes_distance = ctypes.c_int.from_address(ctypes.addressof(c_distance)).value
    c_orientation = ctypes.c_float(orientation)
    bytes_orientation = ctypes.c_int.from_address(ctypes.addressof(c_distance)).value
    


    serial_data = [0 for i in range(8)]
    serial_data[0] = (bytes_distance & 0x000000FF)
    serial_data[1] = (bytes_distance & 0x0000FF00) >> 8
    serial_data[2] = (bytes_distance & 0x00FF0000) >> 16
    serial_data[3] = (bytes_distance & 0xFF000000) >> 24

    serial_data[4] = (bytes_orientation & 0x000000FF)
    serial_data[5] = (bytes_orientation & 0x0000FF00) >> 8
    serial_data[6] = (bytes_orientation & 0x00FF0000) >> 16
    serial_data[7] = (bytes_orientation & 0xFF000000) >> 24
    
    serial_data = bytearray(serial_data)

    return(serial_data)



def main():
<<<<<<< HEAD
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
    message = bytearray([97, 98, 99])
=======
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
    ser.reset_input_buffer())

    while True:
        ser.write(b"serial test\n")
        time.sleep(1)
>>>>>>> 8ac8af525fa90262119ad571e66df712cffdae9d

    while True:
        ser.write(make_arduino_info(30, 100))
        time.sleep(1)

    # ser = serial.Serial(
    #     port='/dev/ttyACM0',
    #     baudrate=9600,
    #     timeout=1,
    #     parity=serial.PARITY_NONE,
    #     stopbits = serial.STOPBITS_ONE,
    #     bytesize = serial.EIGHTBITS
    # )
    #
    # ser.write("U")
    #
    # while (True):
    # # 15 x white pixels
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0001) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 1
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0002) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 2
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0003) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 3
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0004) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 4
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0005) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 5
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0006) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 6
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0007) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 7
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0008) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 8
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0009) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 9
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000A) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 10
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000B) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 11
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000C) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 12
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000D) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 13
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000E) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 14


if __name__ == '__main__':
    main()

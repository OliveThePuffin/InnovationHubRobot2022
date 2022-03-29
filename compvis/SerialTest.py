import serial
import time


def main():
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
    message = "Serial Test\n"

    ser.write(bytes(message, 'utf-8'))


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
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x000F) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 15
    #     ser.write(chr(0x0050) + chr(0x0000) + chr(0x0010) + chr(0x0000) + chr(0x000A) + chr(0x00FF) + chr(0x00FF))  # 16


if __name__ == '__main__':
    main()

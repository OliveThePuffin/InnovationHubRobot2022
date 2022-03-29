import serial


def main():
    ser = serial.Serial('/dev/ttyACM0', baudrate=9600)
    message = "Serial Test\n"
    while True:
        ser.write(bytes(message, 'utf-8'))

    ser.close()


if __name__ == '__main__':
    main()

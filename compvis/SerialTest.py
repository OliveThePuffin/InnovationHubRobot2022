import serial


def main():
    ser = serial.Serial('/dev/ttyACM0')
    message = "Serial Test"
    ser.write(bytes(message, 'utf-8'))

    ser.close()


if __name__ == '__main__':
    main()

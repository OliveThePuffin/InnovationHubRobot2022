import serial
import random


def main():
    x = random.randint(0, 10)
    y = random.randint(0, 10)
    ser = serial.Serial('/dev/ttyACM0')

    for i in range(100):
        ser.write(x)
        ser.write(y)

        x = random.randint(0, 10)
        y = random.randint(0, 10)

    ser.close()


if __name__ == '__main__':
    main()

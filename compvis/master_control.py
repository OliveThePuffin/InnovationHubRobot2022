#!/bin/python3.9

# MASTER CONTROLLER
# Calls fuzzy logic and object detection programs

import fuzzy_logic
import object_detection_fast as od
import marvelmind
import serial
import struct
import time


def main():
    get_y_interval = 0.5    # seconds, delay interval between successive checks for new y position
    alert_people_interval = 5   # seconds, delay interval to prevent robot from spamming "excuse me" to alert people
    alert_people_start = time.time()
    get_y_start = time.time()

    person_exists = False

    # hard coded tour locations: (eventually these should be read from a .txt file or something so that new stops
    # can be added easily
    x_destination = 2
    y_destination = 10

    od.reset_camera()

    pipeline, config = od.initialize_pipeline()
    
    hedge = MarvelmindHedge(tty = "/dev/ttyACM0", adr=None, debug=False) # create MarvelmindHedge thread
    
    hedge.start()
    
    while True:

        current_time = time.time()

        # get marvelmind y position at beginning of loop, this will be compared to next y position
        # to find delta_y_error
        _, previous_y = hedge.get_position()

        # get three distances to objects from camera
        distance_left, distance_center, distance_right = od.get_depths(pipeline, config)

        # prevents robot from spamming "excuse me" voice line every time it detects a person
        # if the current time at this loop iteration minus the start time (last time voice line was used)
        # we can alert people
        if current_time - alert_people_start >= alert_people_interval:
            person_exists = od.detect_person()
            alert_people_start = time.time()

        current_x, current_y = hedge.get_position()
        x_error = current_x - x_destination
        delta_y_error = current_y - previous_y

        if abs(current_x - x_destination) <= 0.3 and abs(current_y - y_destination) <= 0.3:
            speed = 0
            heading = 90

            # open serial port
            ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
            ser.reset_input_buffer()

            # pack speed and heading into struct to be sent to Arduino
            packet = struct.pack('!2f', speed, heading)

            # write packet to serial
            ser.write(packet)
            break

        # call fuzzy logic controller to get speed and heading output
        speed, heading = fuzzy_logic.calculate_output(distance_left, distance_center, distance_right,
                                                      x_error, delta_y_error)

        # open serial port
        ser = serial.Serial('/dev/ttyACM0', baudrate=9600, timeout=1)
        ser.reset_input_buffer()

        # pack speed and heading into struct to be sent to Arduino
        packet = struct.pack('!2f', speed, heading)

        # write packet to serial
        ser.write(packet)


if __name__ == '__main__':
    main()

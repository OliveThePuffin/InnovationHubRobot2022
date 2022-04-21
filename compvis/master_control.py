#!/bin/python3.9

# MASTER CONTROLLER
# Calls fuzzy logic and object detection programs

import fuzzy_logic
import object_detection as od
import serial
import struct

def main():

    loop_count = 0
    num_loops = 100000
    can_alert_person = True
    person_exists = False

    #  od.reset_camera
    
    while True:
        # get three distances to objects from camera
        distance_left, distance_center, distance_right = od.get_depths()

        # prevents robot from spamming "excuse me" voice line every time it detects a person
        if can_alert_person >= num_loops:
            # person_exists = od.detect_person()
            loop_count = 0

        # increment loop for "excuse me" voice line timer
        loop_count = loop_count + 1

        x_error = 0
        delta_y_error = -1.8

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
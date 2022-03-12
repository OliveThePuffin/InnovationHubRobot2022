import math
from _testcapi import INT_MAX

import skfuzzy
import numpy as np
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


class Rectangle:
    """ A class of Python object that describes the properties of a rectangle"""

    def __init__(self, x1, x2, y1, y2):
        self.angle = None
        self.y_min_distance = None
        self.x_min_distance = None
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def compute_xy_distance(self, x_loc, y_loc):
        x1_distance = self.x1 - x_loc
        x2_distance = self.x2 - x_loc
        x_min_distance = min(abs(x1_distance), abs(x2_distance))
        y1_distance = self.y1 - y_loc
        y2_distance = self.y2 - y_loc
        y_min_distance = min(abs(y1_distance), abs(y2_distance))
        self.x_min_distance = x_min_distance
        self.y_min_distance = y_min_distance

    def compute_distance(self):
        return math.sqrt(math.pow(self.x_min_distance, 2) + math.pow(self.y_min_distance, 2))

    def compute_angle(self):
        self.angle = 90 + math.atan(self.x_min_distance / self.y_min_distance) * 180/math.pi


class Robot:
    def __init__(self, x, y, x_destination, y_destination):
        self.delta_y_error = 0
        self.heading = 90
        self.distance = 0
        self.x = x
        self.y = y
        self.x_destination = x_destination
        self.y_destination = y_destination
        self.x_error = x_destination - x
        self.y_error = y_destination - y

    def update_heading(self, heading):
        self.heading = heading

    def calculate_distance_moved(self, speed):
        # TODO round to interval
        self.distance = speed / 300

    def update_xy(self):
        self.delta_y_error = self.y - self.distance * math.sin(self.heading)
        self.x = self.x + self.distance * math.sin((90 - self.heading) * 180/math.pi)
        self.y = self.y + self.distance * math.cos((90 - self.heading) * 180/math.pi)

        self.x_error = self.x_destination - self.x
        # if self.x_error > 2:
        #     self.x_error = 2

        self.y_error = self.y_destination - self.y

def main():
    distance = ctrl.Antecedent(np.arange(0, 3.2, 0.08), 'distance')  # meters
    angle = ctrl.Antecedent(np.arange(0, 181, 1), 'angle')  # meters
    x_error = ctrl.Antecedent(np.arange(-4, 4.1, 0.1), 'x_error')  # meters
    delta_y_error = ctrl.Antecedent(np.arange(-2, 2.08, 0.08), "delta_y_error")  # meters

    speed = ctrl.Consequent(np.arange(0, 401, 1), 'speed')  # motor input
    heading = ctrl.Consequent(np.arange(0, 181, 1), 'heading')  # degrees

    # ANTECEDENTS
    distance['zero'] = skfuzzy.trimf(distance.universe, [0, 0.25, 0.5])
    distance['low'] = skfuzzy.trimf(distance.universe, [.25, 1.5, 2.08])
    distance['high'] = skfuzzy.trimf(distance.universe, [1.8, 2.5, 3.12])

    angle['left'] = skfuzzy.trimf(angle.universe, [0, 0, 45])
    angle['mid_left'] = skfuzzy.trimf(angle.universe, [0, 45, 90])
    angle['center'] = skfuzzy.trimf(angle.universe, [75, 90, 105])
    angle['mid_right'] = skfuzzy.trimf(angle.universe, [90, 135, 180])
    angle['right'] = skfuzzy.trimf(angle.universe, [135, 180, 180])

    x_error['negative'] = skfuzzy.trimf(x_error.universe, [-4, 0, 0])
    x_error['zero'] = skfuzzy.trimf(x_error.universe, [-1, 0, 1])
    x_error['positive'] = skfuzzy.trapmf(x_error.universe, [1, 4, 4, 4])

    delta_y_error['negative'] = skfuzzy.trimf(delta_y_error.universe, [-2, -2, 0])
    delta_y_error['zero'] = skfuzzy.trimf(delta_y_error.universe, [-0.5, 0, 0.5])
    delta_y_error['positive'] = skfuzzy.trimf(delta_y_error.universe, [0, 2, 2])

    # CONSEQUENTS
    speed['zero'] = skfuzzy.trimf(speed.universe, [0, 0, 50])
    speed['low'] = skfuzzy.trimf(speed.universe, [25, 100, 200])
    speed['high'] = skfuzzy.trimf(speed.universe, [100, 300, 400])

    heading['left'] = skfuzzy.trapmf(heading.universe, [0, 0, 45, 90])
    heading['forward'] = skfuzzy.trimf(heading.universe, [45, 90, 135])
    heading['right'] = skfuzzy.trapmf(heading.universe, [90, 135, 180, 180])

    # distance.view()
    # angle.view()

    # speed.view()
    # heading.view()

    # RULES
    rule1 = ctrl.Rule(distance['high'] | (angle['right'] | angle['left']), speed['high'])
    rule2 = ctrl.Rule(distance['low'] & (angle['mid_left'] | angle['center'] | angle['mid_right']), speed['low'])
    rule3 = ctrl.Rule(distance['zero'] & (angle['mid_left'] | angle['center'] | angle['mid_right']), speed['zero'])
    rule4 = ctrl.Rule(distance['low'] & angle['mid_right'], heading['left'])
    rule5 = ctrl.Rule(distance['low'] & (angle['mid_left'] | angle['center']), heading['right'])
    rule6 = ctrl.Rule(distance['high'] | (angle['right'] | angle['left']), heading['forward'])
    rule7 = ctrl.Rule(distance['high'] | (angle['right'] | angle['left']), speed['high'])
    rule8 = ctrl.Rule(distance['zero'] & angle['mid_right'], heading['left'])
    rule9 = ctrl.Rule(distance['zero'] & (angle['mid_left'] | angle['center']), heading['right'])
    rule10 = ctrl.Rule(x_error['positive'], heading['left'])
    rule11 = ctrl.Rule(x_error['negative'], heading['right'])
    rule12 = ctrl.Rule(x_error['zero'], heading['forward'])
    rule13 = ctrl.Rule(delta_y_error['positive'] & x_error['negative'], heading['left'])
    rule14 = ctrl.Rule(delta_y_error['positive'] & (x_error['positive'] | x_error['zero']), heading['right'])
    rule15 = ctrl.Rule(delta_y_error['negative'], heading['forward'])

    speed_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                        rule11, rule12, rule13, rule14, rule15])
    speed_sim = ctrl.ControlSystemSimulation(speed_control)

    # Object locations at
    rectangle1 = Rectangle(6, 7, 6, 7)
    objects = [rectangle1]

    # Creates robot start location and destination locations
    robot = Robot(6, 0, 6, 10)

    # Calculate the min distance to one of the 4 corners
    for i in range(len(objects)):
        objects[i].compute_xy_distance(robot.x, robot.y)

    min_xy_distance = INT_MAX
    index = 0

    for i in range(len(objects)):
        objects[i].compute_xy_distance(robot.x, robot.y)
        temp_distance = objects[i].compute_distance()
        if temp_distance < float(min_xy_distance):
            min_xy_distance = temp_distance
            index = i

    if min_xy_distance > 3:
        min_xy_distance = 3

    objects[index].compute_angle()

    x = np.array([])
    y = np.array([])

    np.append(x, robot.x)
    np.append(y, robot.y)

    while (x_error and robot.y_error) >= .1:
        speed_sim.input['x_error'] = robot.x_error
        speed_sim.input['distance'] = min_xy_distance
        speed_sim.input['delta_y_error'] = robot.delta_y_error
        speed_sim.input['angle'] = objects[index].angle

        speed_sim.compute()

        new_speed = speed_sim.output['speed']
        new_heading = speed_sim.output['heading']

        # Calculate new x_error and y_error
        robot.update_heading(new_heading)
        robot.calculate_distance_moved(new_speed)
        robot.update_xy()

        np.append(x, robot.x)
        np.append(y, robot.y)

        for i in range(len(objects)):
            objects[i].compute_xy_distance(robot.x, robot.y)
            temp_distance = objects[i].compute_distance()
            if temp_distance < float(min_xy_distance):
                min_xy_distance = temp_distance
                index = i

        if min_xy_distance > 3:
            min_xy_distance = 3

        objects[index].compute_angle()

        # speed_sim.input['x_error'] = robot.x_error
        # speed_sim.input['distance'] = min_xy_distance
        # speed_sim.input['delta_y_error'] = robot.delta_y_error
        # speed_sim.input['angle'] = objects[index].angle
        print("x:" + str(robot.x))
        print("y:" + str(robot.y))
        # print("Speed: ")
        # print(speed_sim.output['speed'])
        # print("Heading: ")
        # print(speed_sim.output['heading'])

    plt.plot(x, y)
    plt.show()


    # CONSEQUENTS:
    speed.view(sim=speed_sim)
    heading.view(sim=speed_sim)
    x_error.view(sim=speed_sim)

    # ANTECEDENTS:
    distance.view(sim=speed_sim)
    angle.view(sim=speed_sim)

    # print("Speed: ")
    # print(speed_sim.output['speed'])
    # print("Heading: ")
    # print(speed_sim.output['heading'])

    plt.show()


if __name__ == '__main__':
    main()

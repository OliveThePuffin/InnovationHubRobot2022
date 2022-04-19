import math
import random
from _testcapi import INT_MAX

import skfuzzy
import numpy as np
from matplotlib.collections import LineCollection
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

    def get_obj_loc(self):
        return self.x1, self.x2, self.y1, self.y2

    def compute_xy_distance(self, x_loc, y_loc):
        x_center = (self.x1 + self.x2) / 2
        y_center = (self.y1 + self.y2) / 2
        x_min_distance = abs(x_center - x_loc)
        y_min_distance = abs(y_center - y_loc)

        self.x_min_distance = x_min_distance
        self.y_min_distance = y_min_distance

    def compute_distance(self):
        return math.sqrt(math.pow(self.x_min_distance, 2) + math.pow(self.y_min_distance, 2))

    def compute_angle(self, robot_heading):
        self.angle = (90 + math.atan(self.x_min_distance / self.y_min_distance) * 180 / math.pi) + (robot_heading - 90)


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

    def get_heading(self):
        return self.heading

    def calculate_distance_moved(self, speed):
        self.distance = speed / 20000

    def update_xy(self):
        self.delta_y_error = -self.distance * math.cos((self.heading - 90) * math.pi / 180)
        self.x = self.x + self.distance * math.sin((self.heading - 90) * math.pi / 180)
        self.y = self.y + self.distance * math.cos((self.heading - 90) * math.pi / 180)

        self.x_error = self.x - self.x_destination
        if self.x_error > 4:
            self.x_error = 3.8

        if self.x_error < -4:
            self.x_error = -3.8

        self.y_error = self.y_destination - self.y


def main():
    # distance = ctrl.Antecedent(np.arange(0, 3.2, 0.08), 'distance')  # meters
    distance = ctrl.Antecedent(np.arange(0, 1, 0.1), 'distance')  # meters
    angle = ctrl.Antecedent(np.arange(0, 181, 1), 'angle')  # meters
    x_error = ctrl.Antecedent(np.arange(-4, 4.1, 0.1), 'x_error')  # meters
    delta_y_error = ctrl.Antecedent(np.arange(-.2, .2, 0.01), "delta_y_error")  # meters

    speed = ctrl.Consequent(np.arange(0, 401, 1), 'speed')  # motor input
    heading = ctrl.Consequent(np.arange(0, 181, 1), 'heading')  # degrees

    # ANTECEDENTS
    # distance['zero'] = skfuzzy.trimf(distance.universe, [0, 0.25, 0.5])
    # distance['low'] = skfuzzy.trimf(distance.universe, [.25, 1.5, 2.08])
    # distance['high'] = skfuzzy.trimf(distance.universe, [1.8, 2.5, 3.12])
    distance['zero'] = skfuzzy.trimf(distance.universe, [0, 0.15, 0.3])
    distance['low'] = skfuzzy.trimf(distance.universe, [0.3, 0.5, 0.7])
    distance['high'] = skfuzzy.trimf(distance.universe, [0.6, 0.8, 1])

    angle['left'] = skfuzzy.trimf(angle.universe, [-30, -30, 45])
    angle['mid_left'] = skfuzzy.trimf(angle.universe, [0, 45, 90])
    angle['center'] = skfuzzy.trimf(angle.universe, [75, 90, 105])
    angle['mid_right'] = skfuzzy.trimf(angle.universe, [90, 135, 180])
    angle['right'] = skfuzzy.trimf(angle.universe, [135, 210, 210])

    x_error['negative'] = skfuzzy.trimf(x_error.universe, [-4, -4, 0])
    x_error['zero'] = skfuzzy.trimf(x_error.universe, [-1, 0, 1])
    x_error['positive'] = skfuzzy.trimf(x_error.universe, [0, 4, 4])

    delta_y_error['negative'] = skfuzzy.trimf(delta_y_error.universe, [-.2, -.2, 0])
    delta_y_error['zero'] = skfuzzy.trimf(delta_y_error.universe, [-0.05, 0, 0.05])
    delta_y_error['positive'] = skfuzzy.trimf(delta_y_error.universe, [0, .2, .2])

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
    # x_error.view()
    # plt.show()

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

    """ TESTING SINGLE FUZZY LOGIC OUTPUTS """
    # speed_sim.input['x_error'] = 0
    # speed_sim.input['distance'] = .9
    # speed_sim.input['delta_y_error'] = .19
    # speed_sim.input['angle'] = 179
    #
    # speed_sim.compute()
    #
    # print("Speed: " + str(speed_sim.output['speed']))
    # print("Heading: " + str(speed_sim.output['heading']))
    #
    # # CONSEQUENTS:
    # # speed.view(sim=speed_sim)
    # # heading.view(sim=speed_sim)
    # delta_y_error.view(sim=speed_sim)
    #
    # # ANTECEDENTS:
    # # distance.view(sim=speed_sim)
    # # angle.view(sim=speed_sim)
    #
    # print("Speed: ")
    # print(speed_sim.output['speed'])
    # print("Heading: ")
    # print(speed_sim.output['heading'])

    # Object locations at
    objects = []
    for i in range(30):
        rand1 = random.random() * 10
        # rand1 = random.random() * ((8 - 5) + 1) + 3
        rand2 = random.random() * 10
        while rand1 == 6 and rand2 == 0:
            rand1 = random.random() * 10
            # rand1 = random.random() * ((8 - 5) + 1) + 3
            rand2 = random.random() * 10
        objects.append(Rectangle(rand1, rand1 + .03, rand2, rand2 + .3))

    # Creates robot start location and destination locations
    robot = Robot(0, 0, 4, 15)

    # Calculate the min distance to one of the 4 corners
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

    objects[index].compute_angle(robot.get_heading())
    x_path = []
    y_path = []
    speed_at_loc = []

    x_path.append(robot.x)
    y_path.append(robot.y)
    speed_at_loc.append(0)
    robot.update_xy()

    while abs(robot.x_error) > .5 or abs(robot.y_error) > .1:
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

        x_path.append(robot.x)
        y_path.append(robot.y)
        speed_at_loc.append(new_speed)

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

        objects[index].compute_angle(robot.get_heading())

    fig, ax = plt.subplots()
    plt.xlim([0, 12])
    plt.ylim([0, 17])
    ax.plot(x_path, y_path)

    loc_list = []
    for i in range(len(objects)):
        loc_list.append(objects[i].get_obj_loc())
        width = loc_list[i][1] - loc_list[i][0]
        height = loc_list[i][3] - loc_list[i][2]

        ax.add_patch(plt.Rectangle((loc_list[i][0], loc_list[i][2]), width, height, fc='r'))

    ax.add_patch(plt.Circle((robot.x_destination, robot.y_destination), .2, fc='g'))

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(min(speed_at_loc), max(speed_at_loc))
    points = np.array([x_path, y_path]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap='viridis', norm=norm)
    # Set the values used for colormapping
    lc.set_array(speed_at_loc)
    lc.set_linewidth(2)
    line = ax.add_collection(lc)
    fig.colorbar(line, ax=ax)

    plt.show()

    # # CONSEQUENTS:
    # speed.view(sim=speed_sim)
    # heading.view(sim=speed_sim)
    # x_error.view(sim=speed_sim)
    #
    # # ANTECEDENTS:
    # distance.view(sim=speed_sim)
    # angle.view(sim=speed_sim)

    # print("Speed: ")
    # print(speed_sim.output['speed'])
    # print("Heading: ")
    # print(speed_sim.output['heading'])


if __name__ == '__main__':
    main()

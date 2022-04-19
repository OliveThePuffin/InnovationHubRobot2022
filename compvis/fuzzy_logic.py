#!/bin/python3.9

import skfuzzy
import numpy as np
from skfuzzy import control as ctrl


def initialize_controller():
    distance_left = ctrl.Antecedent(np.arange(0, 3.1, 0.1), 'distance_left')  # meters
    distance_center = ctrl.Antecedent(np.arange(0, 3.1, 0.1), 'distance_center')  # meters
    distance_right = ctrl.Antecedent(np.arange(0, 3.1, 0.1), 'distance_right')  # meters

    x_error = ctrl.Antecedent(np.arange(-2, 2.1, 0.1), 'x_error')  # meters
    delta_y_error = ctrl.Antecedent(np.arange(-2, 2.08, 0.08), "delta_y_error")  # meters

    speed = ctrl.Consequent(np.arange(0, 401, 1), 'speed')  # motor input
    heading = ctrl.Consequent(np.arange(0, 181, 1), 'heading')  # degrees

    # ANTECEDENTS
    distance_left['zero'] = skfuzzy.trimf(distance_left.universe, [0, 0, 0.5])
    distance_left['low'] = skfuzzy.trapmf(distance_left.universe, [.3, 0.5, 1.8, 2.3])
    distance_left['high'] = skfuzzy.trapmf(distance_left.universe, [1.8, 2.3, 3, 3])

    distance_center['zero'] = skfuzzy.trimf(distance_center.universe, [0, 0, 0.5])
    distance_center['low'] = skfuzzy.trapmf(distance_center.universe, [.3, 0.5, 1.8, 2.3])
    distance_center['high'] = skfuzzy.trapmf(distance_center.universe, [1.8, 2.3, 3, 3])

    distance_right['zero'] = skfuzzy.trimf(distance_right.universe, [0, 0, 0.5])
    distance_right['low'] = skfuzzy.trapmf(distance_right.universe, [.3, 0.5, 1.8, 2.3])
    distance_right['high'] = skfuzzy.trapmf(distance_right.universe, [1.8, 2.3, 3, 3])

    x_error['negative'] = skfuzzy.trimf(x_error.universe, [-2, -2, 0])
    x_error['zero'] = skfuzzy.trimf(x_error.universe, [-0.5, 0, 0.5])
    x_error['positive'] = skfuzzy.trapmf(x_error.universe, [0, 2, 2, 2])

    delta_y_error['negative'] = skfuzzy.trimf(delta_y_error.universe, [-2, -2, 0.5])
    delta_y_error['positive'] = skfuzzy.trimf(delta_y_error.universe, [-0.5, 2, 2])

    # CONSEQUENTS
    speed['zero'] = skfuzzy.trimf(speed.universe, [0, 0, 50])
    speed['low'] = skfuzzy.trimf(speed.universe, [25, 100, 200])
    speed['high'] = skfuzzy.trimf(speed.universe, [100, 400, 400])

    heading['left'] = skfuzzy.trapmf(heading.universe, [0, 0, 45, 90])
    heading['forward'] = skfuzzy.trimf(heading.universe, [45, 90, 135])
    heading['right'] = skfuzzy.trapmf(heading.universe, [90, 135, 180, 180])

    # RULES
    # object avoidance rules
    rule1 = ctrl.Rule(distance_left['high'] & distance_center['high'] & distance_right['high'], speed['high'])
    rule2 = ctrl.Rule(distance_left['high'] & distance_center['high'] & distance_right['high'], heading['forward'])
    rule3 = ctrl.Rule(distance_left['low'] | distance_center['low'] | distance_right['low'], speed['low'])
    rule4 = ctrl.Rule(distance_left['zero'] | distance_center['zero'] | distance_right['zero'], speed['zero'])
    rule5 = ctrl.Rule(((distance_left['low'] | distance_left['zero']) |
                       (distance_center['low'] | distance_center['zero'])) & distance_right['high'], heading['right'])
    rule6 = ctrl.Rule((distance_right['low'] | distance_right['zero']) &
                      (distance_center['low'] | distance_center['zero']) & distance_left['high'], heading['left'])
    rule7 = ctrl.Rule((distance_left['low'] | distance_left['zero']) &
                      (distance_center['low'] | distance_center['zero']) & (distance_right['low'] |
                                                                            distance_right['zero']), heading['right'])

    # x and y position rules
    rule8 = ctrl.Rule(x_error['positive'], heading['left'])
    rule9 = ctrl.Rule(x_error['negative'], heading['right'])
    rule10 = ctrl.Rule(x_error['zero'], heading['forward'])
    rule11 = ctrl.Rule(delta_y_error['positive'] & x_error['negative'], heading['left'])
    rule12 = ctrl.Rule(delta_y_error['positive'] & (x_error['positive'] | x_error['zero']), heading['right'])
    rule13 = ctrl.Rule(delta_y_error['negative'], heading['forward'])

    speed_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11,
                                        rule12, rule13])
    speed_sim = ctrl.ControlSystemSimulation(speed_control)

    return speed_sim


def calculate_output(distance_left, distance_center, distance_right, x_error, delta_y_error):

    speed_sim = initialize_controller()

    speed_sim.input['x_error'] = x_error
    speed_sim.input['delta_y_error'] = delta_y_error

    speed_sim.input['distance_left'] = distance_left
    speed_sim.input['distance_center'] = distance_center
    speed_sim.input['distance_right'] = distance_right

    speed_sim.compute()

    return speed_sim.output['speed'], speed_sim.output['heading']

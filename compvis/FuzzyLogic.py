import skfuzzy
import numpy as np
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


def main():
    distance = ctrl.Antecedent(np.arange(0, 3.2, 0.08), 'distance')  # meters
    angle = ctrl.Antecedent(np.arange(0, 181, 1), 'angle')  # meters
    x_error = ctrl.Antecedent(np.arange(-2, 2.1, 0.1), 'x_error')  # meters
    y_error = ctrl.Antecedent(np.arange(0, 24.08, 0.08), 'y_error')  # meter
    delta_y_error = ctrl.Antecedent(np.arange(-2, 2.08, 0.08), "delta_y_error")  # meters

    speed = ctrl.Consequent(np.arange(0, 401, 1), 'speed')  # motor input
    heading = ctrl.Consequent(np.arange(0, 181, 1), 'heading')  # degrees

    # ANTECEDENTS
    distance['zero'] = skfuzzy.trimf(distance.universe, [0, 0.25, 0.5])
    distance['low'] = skfuzzy.trimf(distance.universe, [.25, 1.5, 2.08])
    distance['high'] = skfuzzy.trimf(distance.universe, [1.8, 2.5, 3.12])

    angle['left'] = skfuzzy.trimf(angle.universe, [0, 0, 45])
    angle['mid_left'] = skfuzzy.trimf(angle.universe, [0, 45, 90])
    angle['center']= skfuzzy.trimf(angle.universe, [75, 90, 105])
    angle['mid_right'] = skfuzzy.trimf(angle.universe, [90, 135, 180])
    angle['right'] = skfuzzy.trimf(angle.universe, [135, 180, 180])

    x_error['negative'] = skfuzzy.trimf(x_error.universe, [-2, -2, 0])
    x_error['zero'] = skfuzzy.trimf(x_error.universe, [-0.5, 0, 0.5])
    x_error['positive'] = skfuzzy.trapmf(x_error.universe, [0, 2, 2, 2])

    y_error['zero'] = skfuzzy.trimf(y_error.universe, [0, 0, 1.5])
    y_error['high'] = skfuzzy.trapmf(y_error.universe, [0, 1.5, 16, 16])

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
    rule8 = ctrl.Rule(distance['zero'] & angle['mid_right'],  heading['left'])
    rule9 = ctrl.Rule(distance['zero'] & (angle['mid_left'] | angle['center']),  heading['right'])
    rule10 = ctrl.Rule(x_error['positive'], heading['left'])
    rule11 = ctrl.Rule(x_error['negative'], heading['right'])
    rule12 = ctrl.Rule(x_error['zero'], heading['forward'])

    speed_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                        rule11, rule12])
    speed_sim = ctrl.ControlSystemSimulation(speed_control)

    speed_sim.input['x_error'] = -1
    speed_sim.input['distance'] = 0.1
    speed_sim.input['angle'] = 90

    speed_sim.compute()

    # CONSEQUENTS:
    speed.view(sim=speed_sim)
    heading.view(sim=speed_sim)
    x_error.view(sim=speed_sim)

    # ANTECEDENTS:
    distance.view(sim=speed_sim)
    angle.view(sim=speed_sim)

    print("Speed: ")
    print(speed_sim.output['speed'])
    print("Heading: ")
    print(speed_sim.output['heading'])

    plt.show()


if __name__ == '__main__':
    main()

import matplotlib.pyplot as plt
from SimulationView import SimulationView


def initialize_simulation():
    return SimulationView()


def display_simulation():
    plt.show()


def run_simulation():
    simulation = initialize_simulation()
    display_simulation()


if __name__ == '__main__':
    run_simulation()

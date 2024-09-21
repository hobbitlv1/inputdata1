import sys
from PyQt5.QtWidgets import QApplication
from simulation_view import SimulationView


def run_simulation():
    app = QApplication(sys.argv)
    simulation_view = SimulationView()
    simulation_view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_simulation()

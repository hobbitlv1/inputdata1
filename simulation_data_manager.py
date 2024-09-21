import json
from dataclasses import dataclass, asdict
from typing import Dict, Any
import os
import numpy as np


@dataclass
class SimulationParameters:
    animation_speed: int
    grid_size: int
    initial_carviz_count: int
    initial_erbast_count: int
    carviz_lifespan: int
    erbast_lifespan: int
    water_coverage: int


@dataclass
class SimulationResults:
    simulation_completed: bool
    duration: str
    max_carviz_population: int
    max_erbast_population: int
    total_hunts: int


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


class SimulationDataManager:
    def __init__(
        self, params: SimulationParameters, results: SimulationResults
    ):
        self.parameters = params
        self.results = results
        self.data_file = "simulation_data.json"

    def save_simulation_data(self):
        simulation_data = {
            'Parameters': asdict(self.parameters),
            'Results': asdict(self.results)
        }

        existing_data = self._load_existing_data()
        existing_data.append(simulation_data)

        self._write_data_to_file(existing_data)
        print(
            f"{self._color_text('green')}Simulation data saved successfully."
            f"{self._color_text('reset')}\n"
        )

    def _load_existing_data(self) -> list:
        if not os.path.exists(self.data_file):
            return []

        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            print(
                f"{self._color_text('yellow')}Warning: Unable to load existing data. "
                f"Starting with fresh data.{self._color_text('reset')}"
            )
            return []

    def _write_data_to_file(self, data: list):
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=2, cls=NumpyEncoder)

    def load_and_display_data(self):
        self.content = self._load_existing_data()

    @staticmethod
    def _color_text(color: str) -> str:
        colors = {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "reset": "\033[0m",
        }
        return colors.get(color, "")

import pickle
from dataclasses import dataclass, asdict
from typing import Dict, Any
import os


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


class SimulationDataManager:
    def __init__(
        self, params: SimulationParameters, results: SimulationResults
    ):
        self.parameters = params
        self.results = results
        self.data_file = "simulation_data.pickle"

    def save_simulation_data(self):
        simulation_data = {
            'Parameters': asdict(self.parameters),
            'Results': asdict(self.results)
        }

        existing_data = self._load_existing_data()
        updated_data = {**existing_data, **simulation_data}

        self._write_data_to_file(updated_data)
        print(
            f"{self._color_text('green')}Simulation data saved successfully."
            f"{self._color_text('reset')}\n"
        )

    def _load_existing_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_file):
            return {}

        try:
            with open(self.data_file, 'rb') as file:
                data = pickle.load(file)
                return data if isinstance(data, dict) else {}
        except (pickle.UnpicklingError, ModuleNotFoundError, AttributeError):
            print(
                f"{self._color_text('yellow')}Warning: Unable to load existing data."
                f" Starting with fresh data.{self._color_text('reset')}"
            )
            return {}

    def _write_data_to_file(self, data: Dict[str, Any]):
        with open(self.data_file, "wb") as file:
            pickle.dump(data, file)

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

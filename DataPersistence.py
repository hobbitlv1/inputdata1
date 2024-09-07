from constants import GREEN, RESET
import pickle

class DataPersistence:

    def __init__(self, interval, num_cells, num_carviz, num_erbast, lft_carviz, lft_erbast, 
                 scl_water, run_flag, title, car_max, erb_max, hunt_tot):
        self.interval = interval
        self.num_cells = num_cells
        self.num_carviz = num_carviz
        self.num_erbast = num_erbast
        self.lft_carviz = lft_carviz
        self.lft_erbast = lft_erbast
        self.scl_water = scl_water
        self.run_flag = run_flag
        self.title = title
        self.car_max = car_max
        self.erb_max = erb_max
        self.hunt_tot = hunt_tot

    def get_init_values(self):
        return {
            'Interval    ': self.interval,
            'NUM_Cells   ': self.num_cells,
            'NUM_Carviz  ': self.num_carviz,
            'NUM_Erbast  ': self.num_erbast,
            'LFT_Carviz  ': self.lft_carviz,
            'LFT_Erbast  ': self.lft_erbast,
            'SCL_Water   ': self.scl_water,
        }

    def get_final_values(self):
        return {
            'RUN_Amount  ': self.run_flag,
            'RUN_Time    ': self.title,
            'MAX_Carviz  ': self.car_max,
            'MAX_Erbast  ': self.erb_max,
            'TOT_Kills   ': self.hunt_tot,
        }

    def save_simulation_data(self):
        simulation_data = {
            'Initial Values': self.get_init_values(),
            'Final Values': self.get_final_values()
        }

        prev_values = self._load_previous_data()
        updated_values = {**prev_values, **simulation_data}

        self._save_to_file(updated_values)
        print(f"{GREEN}Simulation data saved successfully.{RESET}\n")

    @staticmethod
    def _load_previous_data():
        try:
            with open('simulation_data.pickle', 'rb') as file:
                data = pickle.load(file)
                return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}

    @staticmethod
    def _save_to_file(data):
        with open('simulation_data.pickle', 'wb') as file:
            pickle.dump(data, file)

    def read_pickle_file(self, file_path):
        with open(file_path, 'rb') as file:
            self.content = pickle.load(file)

        self._print_content()

    def _print_content(self):
        for title, content in self.content.items():
            print(f"\n{RESET}{title}\n")
            for key, value in content.items():
                print(f"{key}: {value}")
            print()

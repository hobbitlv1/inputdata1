
import random
from itertools import chain

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QGroupBox,
    QGridLayout,
    QSplitter,
)
from PyQt5.QtCore import QTimer, Qt

from simulation_controller import SimulationController
from cell import Cell
from creatures import Vegetob, Carviz, Erbast, Creatures
from constants import MAX_DAYS, MAX_LIFE_E, MAX_LIFE_C, GRID_SIZE
from simulation_data_manager import (
    SimulationParameters,
    SimulationResults,
    SimulationDataManager,
)


class SimulationView(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialize_simulation()
        self._setup_color_palette()
        self._setup_ui()
        self.simulation_controller = SimulationController()
        self._create_animation()

    def _initialize_simulation(self):
        self._set_default_parameters()
        self._initialize_data_structures()

    def _set_default_parameters(self):
        self.max_days = MAX_DAYS
        self.erbast_lifespan = MAX_LIFE_E
        self.carviz_lifespan = MAX_LIFE_C
        self.grid_size = GRID_SIZE
        self.current_day = 0
        self.erbast_count = self.carviz_count = self.hunt_count = 0
        self.time_data = [0]
        self.erbast_population_data = [self.erbast_count]
        self.carviz_population_data = [self.carviz_count]
        self.hunt_data = [self.hunt_count]
        self.erbast_population_history = [self.erbast_population_data]
        self.carviz_population_history = [self.carviz_population_data]
        self.carviz_peak = self.erbast_peak = self.total_hunts = 0
        self.initial_carviz = 10
        self.initial_erbast = 20
        self.water_density = 15
        self.simulation_active = True
        self.simulation_started = False
        self.animation_paused = True
        self.frame_interval = 50
        self.simulation_completed = False

    def _initialize_data_structures(self):
        self.grid = np.empty((self.grid_size, self.grid_size), dtype=object)
        self.water_map = np.zeros((self.grid_size, self.grid_size), dtype=bool)
        self.color_map = np.zeros((self.grid_size, self.grid_size))

    def _setup_color_palette(self):
        self.color_palette = mcolors.ListedColormap(
            ["blue", "green", "brown", "orange", "purple"]
        )
        self.color_norm = mcolors.BoundaryNorm(
            [0, 10, 20, 30, 40, 50], self.color_palette.N
        )
        self.erbast_color = "brown"
        self.carviz_color = "orange"

    def _setup_ui(self):
        self.setWindowTitle("Ecosystem Simulation")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self._create_plot_layout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self._create_control_panel(right_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)

    def _create_plot_layout(self, layout):
        self.fig = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.terrain_ax, self.population_ax = self.fig.subplots(2, 1)
        self.fig.subplots_adjust(hspace=0.3)
        self._setup_plot_axes()
        self._initialize_plot_data()

    def _create_control_panel(self, layout):
        # Simulation parameters
        param_group = QGroupBox("Simulation Parameters")
        param_layout = QGridLayout()
        self._create_input_fields(param_layout)

        # Add Restore Default button
        restore_default_button = QPushButton("Restore Defaults")
        restore_default_button.clicked.connect(
            self._restore_default_parameters
        )
        param_layout.addWidget(
            restore_default_button, len(self.input_fields), 0, 1, 2
        )

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Control buttons
        button_group = QGroupBox("Simulation Control")
        button_layout = QHBoxLayout()
        self._create_control_buttons(button_layout)
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)

        # Statistics
        stats_group = QGroupBox("Simulation Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("No simulation data available")
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

    def _create_input_fields(self, layout):
        input_params = [
            ("Animation Speed", "50"),
            ("Grid Size", "50"),
            ("Carviz Population", "10"),
            ("Carviz Lifespan", "10"),
            ("Erbast Population", "20"),
            ("Erbast Lifespan", "10"),
            ("Water Density", "10"),
        ]
        self.input_fields = []

        for i, (label, initial) in enumerate(input_params):
            layout.addWidget(QLabel(label), i, 0)
            line_edit = QLineEdit(initial)
            self.input_fields.append(line_edit)
            layout.addWidget(line_edit, i, 1)

    def _create_control_buttons(self, layout):
        button_config = ["Start", "Pause", "Resume", "Reset"]
        self.control_buttons = []

        for label in button_config:
            button = QPushButton(label)
            self.control_buttons.append(button)
            layout.addWidget(button)

        self.control_buttons[0].clicked.connect(self.start_simulation)
        self.control_buttons[1].clicked.connect(self.pause_simulation)
        self.control_buttons[2].clicked.connect(self.resume_simulation)
        self.control_buttons[3].clicked.connect(self.reset_simulation)

    def _setup_plot_axes(self):
        for ax in (self.terrain_ax, self.population_ax):
            ax.minorticks_off()
        (self.erbast_line,) = self.population_ax.plot(
            [], [], label="Erbasts", color=self.erbast_color
        )
        (self.carviz_line,) = self.population_ax.plot(
            [], [], label="Carviz", color=self.carviz_color
        )
        self.population_ax.legend(loc="upper right", fontsize="small")
        self.population_ax.set_xlabel("Days", fontsize=8)
        self.population_ax.set_ylabel("Population", fontsize=8)

    def _initialize_plot_data(self):
        self.terrain_plot = self.terrain_ax.imshow(
            self.color_map, cmap=self.color_palette, norm=self.color_norm
        )

    def _create_animation(self):
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_frame)
        self.animation_timer.setInterval(self.frame_interval)

    def configure_simulation(self):
        params = [int(field.text()) for field in self.input_fields]
        (
            self.frame_interval,
            self.grid_size,
            self.initial_carviz,
            self.carviz_lifespan,
            self.initial_erbast,
            self.erbast_lifespan,
            self.water_density,
        ) = params
        self.animation_timer.setInterval(self.frame_interval)
        self._initialize_data_structures()
        self.terrain_plot = self.terrain_ax.imshow(
            self.color_map, cmap=self.color_palette, norm=self.color_norm
        )

    def initialize_grid(self):
        Creatures.update_num_cells(self.grid_size)
        self._generate_landscape()
        self._place_water_bodies()

    def _generate_landscape(self):
        total_cells = self.grid_size * self.grid_size
        water_cells = int(total_cells * self.water_density / 100)
        all_cells = [
            (i, j)
            for i in range(self.grid_size)
            for j in range(self.grid_size)
        ]
        num_water_bodies = random.randint(2, 4)
        water_body_sizes = self._distribute_water_cells(
            water_cells, num_water_bodies
        )

        for size in water_body_sizes:
            center = random.choice(all_cells)
            self._create_water_body(center, size)

        for i, j in np.ndindex(self.grid_size, self.grid_size):
            if not self.water_map[i, j]:
                vg = Vegetob()
                vg.row, vg.column = i, j
                vg.density = vg.generate_density()
                self.grid[i, j] = Cell(i, j, "Ground", vg)

    @staticmethod
    def _distribute_water_cells(total_cells, num_bodies):
        sizes = [
            random.randint(1, total_cells // num_bodies)
            for _ in range(num_bodies)
        ]
        total = sum(sizes)
        return [int(size * total_cells / total) for size in sizes]

    def _create_water_body(self, center, size):
        i, j = center
        cells_to_fill = [(i, j)]
        filled_cells = set()

        while len(filled_cells) < size and cells_to_fill:
            i, j = cells_to_fill.pop(random.randint(0, len(cells_to_fill) - 1))
            if (
                0 <= i < self.grid_size
                and 0 <= j < self.grid_size
                and (i, j) not in filled_cells
            ):
                self.water_map[i, j] = True
                filled_cells.add((i, j))
                for di, dj in [
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1),
                    (-1, -1),
                    (-1, 1),
                    (1, -1),
                    (1, 1),
                ]:
                    if random.random() < 0.7:
                        cells_to_fill.append((i + di, j + dj))

        return filled_cells

    def _place_water_bodies(self):
        for i, j in np.ndindex(self.grid_size, self.grid_size):
            if self.water_map[i, j]:
                self.grid[i, j] = Cell(i, j, "Water", None)

    def update_population_statistics(self):
        self.erbast_count = self.carviz_count = self.hunt_count = 0
        for cell in chain.from_iterable(self.grid):
            self._update_cell_statistics(cell)

    def _update_cell_statistics(self, cell):
        if cell.terrain_type == "Water":
            self.color_map[cell.row, cell.column] = 5
        elif cell.erbast and cell.pride:
            self.carviz_count += 1
            self.erbast_count += 1
            self.hunt_count += 1
            self.color_map[cell.row, cell.column] = 45
        elif cell.erbast:
            self.erbast_count += 1
            self.color_map[cell.row, cell.column] = 25
        elif cell.pride:
            self.color_map[cell.row, cell.column] = 35
            self.carviz_count += 1
        elif cell.terrain_type == "Ground":
            self.color_map[cell.row, cell.column] = 15

    def update_frame(self):
        if self.simulation_started:
            self.simulation_controller.simulate(self.grid)
            self.update_population_statistics()
            self._update_simulation_data()
            self._refresh_plots()
            self._check_simulation_end()
        self.canvas.draw()

    def _update_simulation_data(self):
        self.current_day += 1
        self.time_data.append(self.current_day)
        new_erbast_data, new_carviz_data = [self.erbast_count], [
            self.carviz_count
        ]
        prev_erbast_data, prev_carviz_data = (
            self.erbast_population_history[-1],
            self.carviz_population_history[-1],
        )
        self.erbast_population_history.append(
            np.concatenate([prev_erbast_data, new_erbast_data])
        )
        self.carviz_population_history.append(
            np.concatenate([prev_carviz_data, new_carviz_data])
        )
        self.erbast_population_data, self.carviz_population_data = (
            self.erbast_population_history[-1],
            self.carviz_population_history[-1],
        )
        self.hunt_data.append(self.hunt_count)
        self.erbast_time_data, self.carviz_time_data = np.arange(
            len(self.erbast_population_history)
        ), np.arange(len(self.carviz_population_history))

    def _refresh_plots(self):
        self._update_terrain_plot()
        self._update_population_plot()
        self._update_statistics()

    def _update_terrain_plot(self):
        self.terrain_plot.set_array(self.color_map)
        centuries, years, months = (
            self.current_day // 1000,
            (self.current_day % 1000) // 10,
            self.current_day % 10,
        )
        time_parts = [
            f"{centuries} Centuries" if centuries else "",
            f"{years} Years" if years else "",
            f"{months} Months" if months else "",
        ]
        title = ", ".join(filter(None, time_parts))
        self.terrain_ax.set_title(title, fontsize=8)
        self.simulation_title = title

    def _update_population_plot(self):
        self.erbast_line.set_data(
            self.erbast_time_data, self.erbast_population_data
        )
        self.carviz_line.set_data(
            self.carviz_time_data, self.carviz_population_data
        )
        max_population = max(
            max(self.erbast_population_data), max(self.carviz_population_data)
        )
        max_time = max(len(self.erbast_time_data), len(self.carviz_time_data))
        margin = 0.02 * max(max_time, max_population)
        self.population_ax.set_xlim(0, max_time + margin)
        self.population_ax.set_ylim(0, max_population + margin)
        self.erbast_peak = max(self.erbast_population_data)
        self.carviz_peak = max(self.carviz_population_data)
        self.total_hunts = sum(self.hunt_data)
        legend = self.population_ax.get_legend()
        legend.get_texts()[0].set_color(self.erbast_color)
        legend.get_texts()[1].set_color(self.carviz_color)

    def _update_statistics(self):
        stats_text = (
            "Erbasts: {} (Peak: {})\n"
            "Carviz: {} (Peak: {})\n"
            "Total Hunts: {}\n"
        ).format(
            self.erbast_count,
            self.erbast_peak,
            self.carviz_count,
            self.carviz_peak,
            self.total_hunts,
        )
        self.stats_label.setText(stats_text)

        if self.erbast_count > self.erbast_peak:
            self.erbast_peak = self.erbast_count
        if self.carviz_count > self.carviz_peak:
            self.carviz_peak = self.carviz_count

    def _check_simulation_end(self):
        if not self.animation_paused and not self.simulation_completed:
            if self.erbast_count == 0 and self.carviz_count == 0:
                self._end_simulation("Both species are extinct")
            elif self.carviz_count == 0:
                self._end_simulation("Carviz are extinct")
            elif self.erbast_count == 0:
                self._end_simulation("Erbasts are extinct")
            elif self.current_day >= self.max_days:
                self._end_simulation("Maximum simulation days reached")

    def _end_simulation(self, reason):
        self.simulation_completed = True
        self.animation_timer.stop()
        self._save_simulation_results()
        self.animation_paused = True

        print("\n\033[94m{}\033[0m".format("=" * 60))
        print("\033[1m\033[95mSimulation Summary\033[0m")
        print("\033[94m{}\033[0m\n".format("=" * 60))

        print("\033[1m\033[96mReason for Simulation End:\033[0m {}".format(reason))
        print(
            "\033[1m\033[96mSimulation Duration:\033[0m {}".format(
                self.simulation_title
            )
        )

        print("\n\033[1m\033[93mErbast Statistics:\033[0m")
        print("  Final Population: {}".format(self.erbast_count))
        print("  Peak Population: {}".format(self.erbast_peak))
        print(
            "  Survival Rate: {:.2f}%".format(
                (self.erbast_count / self.initial_erbast) * 100
            )
        )

        print("\n\033[1m\033[91mCarviz Statistics:\033[0m")
        print("  Final Population: {}".format(self.carviz_count))
        print("  Peak Population: {}".format(self.carviz_peak))
        print(
            "  Survival Rate: {:.2f}%".format(
                (self.carviz_count / self.initial_carviz) * 100
            )
        )

        print("\n\033[1m\033[92mEcosystem Statistics:\033[0m")
        print("  Total Hunts: {}".format(self.total_hunts))
        print(
            "  Average Hunts per Day: {:.2f}".format(
                self.total_hunts / self.current_day
            )
        )
        print("  Water Coverage: {}%".format(self.water_density))

        print("\n\033[94m{}\033[0m".format("=" * 60))

        self.state_manager.load_and_display_data()

    def _save_simulation_results(self):
        params = SimulationParameters(
            animation_speed=self.frame_interval,
            grid_size=self.grid_size,
            initial_carviz_count=self.initial_carviz,
            initial_erbast_count=self.initial_erbast,
            carviz_lifespan=self.carviz_lifespan,
            erbast_lifespan=self.erbast_lifespan,
            water_coverage=self.water_density,
        )

        results = SimulationResults(
            simulation_completed=self.simulation_active,
            duration=self.simulation_title,
            max_carviz_population=self.carviz_peak,
            max_erbast_population=self.erbast_peak,
            total_hunts=self.total_hunts,
        )

        self.state_manager = SimulationDataManager(params, results)
        self.state_manager.save_simulation_data()

    def start_simulation(self):
        self._reset_simulation_state()
        self.configure_simulation()
        self.initialize_grid()
        self.simulation_started = True
        self.terrain_plot.set_array(self.color_map)
        if self.animation_paused:
            self.animation_paused = False
            self._populate_creatures()
            self.control_buttons[0].setEnabled(False)
            self.animation_timer.start()
        elif not self.animation_paused and self.simulation_started:
            self._populate_creatures()

    def _reset_simulation_state(self):
        self.current_day = self.erbast_count = self.carviz_count = (
            self.hunt_count
        ) = 0
        self.time_data = [0]
        self.erbast_population_data = [self.erbast_count]
        self.carviz_population_data = [self.carviz_count]
        self.hunt_data = [self.hunt_count]
        self.erbast_population_history = [self.erbast_population_data]
        self.carviz_population_history = [self.carviz_population_data]

    def _populate_creatures(self):
        if not self.animation_paused:
            self._spawn_carviz()
            self._spawn_erbast()

    def _spawn_carviz(self):
        for _ in range(self.initial_carviz):
            carviz = Carviz(lifetime=self.carviz_lifespan)
            self._place_creature(carviz, self.grid, "pride")

    def _spawn_erbast(self):
        for _ in range(self.initial_erbast):
            erbast = Erbast(lifetime=self.erbast_lifespan)
            self._place_creature(erbast, self.grid, "erbast", check_empty=True)

    def _place_creature(self, creature, grid, attribute, check_empty=False):
        while True:
            row, column = random.randint(
                0, self.grid_size - 1
            ), random.randint(0, self.grid_size - 1)
            if (
                row < self.grid_size
                and column < self.grid_size
                and grid[row, column].terrain_type != "Water"
            ):
                if check_empty and getattr(grid[row, column], attribute):
                    continue
                creature.row, creature.column = row, column
                getattr(grid[row, column], attribute).append(creature)
                break

    def reset_simulation(self):
        self.animation_paused = False
        self.animation_timer.start()
        self.start_simulation()
        self.simulation_completed = False

    def pause_simulation(self):
        if not self.animation_paused:
            self.animation_timer.stop()
            self.animation_paused = True

    def resume_simulation(self):
        if self.animation_paused:
            self.animation_timer.start()
            self.animation_paused = False

    def _restore_default_parameters(self):
        default_values = ["50", "50", "10", "10", "20", "10", "15"]
        for field, value in zip(self.input_fields, default_values):
            field.setText(value)

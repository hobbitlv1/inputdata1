import sys
import time
import noise
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.style as mplstyle
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button

from DataPersistence import DataPersistence
from SimulationController import SimulationController
from CellModel import Cell
from Creatures import Vegetob, Carviz, Erbast, Creatures
from constants import NUM_CELLS, MAX_DAYS, MAX_LIFE_E, MAX_LIFE_C, GREEN, YELLOW, RED, RESET

sys.path.append(".")
mplstyle.use(['ggplot', 'fast'])
plt.switch_backend('TkAgg')


class SimulationView:
    def __init__(self):
        self._initialize_simulation_parameters()
        self._initialize_simulation_data()  # Move this line up
        self._setup_plots()
        self._setup_ui_elements()
        self.simulation_controller = SimulationController()
        self._initialize_animation()

    def _initialize_simulation_parameters(self):
        self.max_days = MAX_DAYS
        self.erb_lifetime = MAX_LIFE_E
        self.car_lifetime = MAX_LIFE_C
        self.num_cells = NUM_CELLS
        self.day = 0
        self.erb_counter = self.car_counter = self.hunt_counter = 0
        self.x_data = [0]
        self.y_erb_data = [self.erb_counter]
        self.y_car_data = [self.car_counter]
        self.y_hunt_data = [self.hunt_counter]
        self.pop_erb = [self.y_erb_data]
        self.pop_car = [self.y_car_data]
        self.car_max = self.erb_max = self.hunt_tot = 0
        self.num_car = 10
        self.num_erb = 20
        self.water_scale = 15
        self.run_flag = 1
        self.has_started = False
        self.animation_paused = True
        self.interval = 60
        self.has_finished = False

    def _setup_plots(self):
        plt.style.use('default')
        self.cmap = colors.ListedColormap(
            ['blue', 'green', 'gray', 'brown', 'black'])
        self.bounds = [0, 10, 20, 30, 40, 50]
        self.norm = colors.BoundaryNorm(self.bounds, self.cmap.N)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
        self._setup_axes()
        self.im = self.ax1.imshow(
            self.colorsList, cmap=self.cmap, norm=self.norm)

    def _setup_axes(self):
        self.ax1.minorticks_off()
        self.ax2.minorticks_off()
        self.line_erb = self.ax2.plot(
            self.x_data, self.y_erb_data, color='gray', label='Erbast')
        self.line_car = self.ax2.plot(
            self.x_data, self.y_car_data, color='brown', label='Carviz')
        self.fig.subplots_adjust(
            bottom=0.35, top=0.95, left=0.1, right=0.9, wspace=0.3)

    def _setup_ui_elements(self):
        self._setup_textboxes()
        self._setup_buttons()
        self._setup_button_events()

    def _setup_textboxes(self):
        textbox_params = [
            ('Animation Speed', '60'), ('Number Cells', '50'), ('Carviz Pop', '10'),
            ('Carviz Life', '10'), ('Erbast Pop', '20'), ('Erbast Life', '10'),
            ('Water Amount', '15')
        ]
        self.textboxes = []
        for i, (label, initial) in enumerate(textbox_params):
            ax = self.fig.add_axes(
                [0.15 if i < 4 else 0.6, 0.25 - 0.05 * (i % 4), 0.25, 0.03])
            self.textboxes.append(TextBox(ax, label, initial=initial))

    def _setup_buttons(self):
        button_params = [
            ('Start', 0.3), ('Pause/Resume', 0.45), ('Reset', 0.6)]
        self.buttons = []
        for label, pos in button_params:
            ax = self.fig.add_axes([pos, 0.05, 0.1, 0.04])
            self.buttons.append(Button(ax, label))

    def _setup_button_events(self):
        self.buttons[0].on_clicked(self.start_animation)
        self.buttons[1].on_clicked(self.pause_animation)
        self.buttons[2].on_clicked(self.reset_animation)

    def _initialize_simulation_data(self):
        self.cellsList = np.empty(
            (self.num_cells, self.num_cells), dtype=object)
        self.water_cells = np.zeros(
            (self.num_cells, self.num_cells), dtype=bool)
        self.colorsList = np.zeros((self.num_cells, self.num_cells))

    def _initialize_animation(self):
        self.animation = FuncAnimation(
            self.fig, self.update, interval=self.interval, save_count=200)
        self.animation.pause()

    def setup_animation_values(self):
        self.interval, self.num_cells, self.num_car, self.car_lifetime, \
            self.num_erb, self.erb_lifetime, self.water_scale = [
                int(float(tb.text)) for tb in self.textboxes]
        self._initialize_simulation_data()
        self.im = self.ax1.imshow(
            self.colorsList, cmap=self.cmap, norm=self.norm)

    def initialize_cells_list(self):
        Creatures.update_num_cells(self.num_cells)
        self._generate_terrain()
        self._initialize_water_cells()

    def _generate_terrain(self):
        scale = self.water_scale
        for i in range(self.num_cells):
            for j in range(self.num_cells):
                noise_value = noise.pnoise2(i / scale, j / scale, octaves=6, persistence=0.5,
                                            lacunarity=2.0, repeatx=self.num_cells, repeaty=self.num_cells)
                vg = Vegetob()
                vg.row, vg.column = i, j
                vg.density = vg.generateDensity()
                if noise_value > 0.25:
                    self.water_cells[i][j] = True
                else:
                    self.cellsList[i][j] = Cell(i, j, "Ground", vg)

    def _initialize_water_cells(self):
        for i in range(self.num_cells):
            for j in range(self.num_cells):
                if self.water_cells[i][j]:
                    if i > 0 and self.cellsList[i - 1][j].terrainType == "Water":
                        self.cellsList[i][j] = self.cellsList[i - 1][j]
                    elif j > 0 and self.cellsList[i][j - 1].terrainType == "Water":
                        self.cellsList[i][j] = self.cellsList[i][j - 1]
                    else:
                        self.cellsList[i][j] = Cell(i, j, "Water", None)

    def update_population_counts(self):
        self.erb_counter = self.car_counter = self.hunt_counter = 0
        for row in range(self.num_cells):
            for column in range(self.num_cells):
                if row < len(self.cellsList) and column < len(self.cellsList[row]):
                    cell = self.cellsList[row][column]
                    self._update_cell_color(cell, row, column)

    def _update_cell_color(self, cell, row, column):
        if cell.terrainType == "Water":
            self.colorsList[row][column] = 5
        elif len(cell.erbast) > 0 and len(cell.pride) > 0:
            self.car_counter += 1
            self.erb_counter += 1
            self.hunt_counter += 1
            self.colorsList[row][column] = 45
        elif len(cell.erbast) > 0:
            self.erb_counter += 1
            self.colorsList[row][column] = 25
        elif len(cell.pride) > 0:
            self.colorsList[row][column] = 35
            self.car_counter += 1
        elif cell.terrainType == "Ground":
            self.colorsList[row][column] = 15

    def update(self, frame):
        if self.has_started:
            self.simulation_controller.simulate(self.cellsList)
            self.update_population_counts()
            self._update_simulation_state()
            self._update_plots()
            self._check_simulation_end()
        return self.im, self.line_erb, self.line_car

    def _update_simulation_state(self):
        self.day += 1
        self.x_data.append(self.day)
        new_erb_pop, new_car_pop = [self.erb_counter], [self.car_counter]
        prev_erb_pop, prev_car_pop = self.pop_erb[-1], self.pop_car[-1]
        self.pop_erb.append(np.concatenate([prev_erb_pop, new_erb_pop]))
        self.pop_car.append(np.concatenate([prev_car_pop, new_car_pop]))
        self.y_erb_data, self.y_car_data = self.pop_erb[-1], self.pop_car[-1]
        self.y_hunt_data.append(self.hunt_counter)
        self.x_erb_data, self.x_car_data = np.arange(
            len(self.pop_erb)), np.arange(len(self.pop_car))

    def _update_plots(self):
        self._update_main_plot()
        self._update_population_plot()

    def _update_main_plot(self):
        self.im.set_array(self.colorsList)
        centuries, decades, years, months = self.day // 1000, (
            self.day % 1000) // 100, (self.day % 100) // 10, self.day % 10
        title_parts = [f"{centuries} Centuries" if centuries > 0 else "", f"{decades} Decades" if decades >
                       0 else "", f"{years} Years" if years > 0 else "", f"{months} Months" if months > 0 else ""]
        title = ", ".join(filter(None, title_parts))
        self.ax1.set_title(title)
        self.ax1.title.set_fontsize(8)
        self.title = title

    def _update_population_plot(self):
        self.line_erb[0].set_data(self.x_erb_data, self.y_erb_data)
        self.line_car[0].set_data(self.x_car_data, self.y_car_data)
        max_y = max(max(self.y_erb_data), max(self.y_car_data))
        max_x = max(len(self.x_erb_data), len(self.x_car_data))
        gap = 0.02 * max(max_x, max_y)
        self.ax2.set_xlim(0, max_x + gap)
        self.ax2.set_ylim(0, max_y + gap)
        self.erb_max = max(self.y_erb_data)
        self.car_max = max(self.y_car_data)
        self.hunt_tot = sum(self.y_hunt_data)
        self.ax2.set_xlabel('Days', fontsize=8)
        self.ax2.set_ylabel('Population', fontsize=8)
        self.ax2.set_title(
            f'\n\n Max Carviz: {self.car_max}      Max Erbast: {self.erb_max}      Cur Carviz: {self.car_counter}      Cur Erbast: {self.erb_counter}      Tot Kills: {self.hunt_tot}')
        self.ax2.title.set_fontsize(8)

    def _check_simulation_end(self):
        if self.day >= 0 and self.car_counter == 0 and not self.animation_paused and not self.has_finished:
            self.has_finished = True
            print(f"\n{GREEN}Simulation Successfully Finished!\n{RESET}")
            self.run_flag += 1
            time.sleep(0.1)
            self.animation.event_source.stop()
            if self.erb_counter > 0:
                print(f"{YELLOW}Erbasts Survived!{RESET}\n")
            if self.erb_counter == 0:
                print(f"{RED}Carvizes Survived!{RESET}\n")
            self._save_simulation_data()
            self.animation_paused = True
            self.dp.read_pickle_file('simulation_data.pickle')

    def _save_simulation_data(self):
        self.dp = DataPersistence(
            self.interval, self.num_cells, self.num_car, self.num_erb,
            self.car_lifetime, self.erb_lifetime, self.water_scale,
            self.run_flag, self.title, self.car_max, self.erb_max, self.hunt_tot
        )
        self.dp.get_init_values()
        self.dp.get_final_values()
        self.dp.save_simulation_data()

    def start_animation(self, event=None):
        self._reset_simulation_state()
        self.setup_animation_values()
        self.initialize_cells_list()
        self.has_started = True
        self.im.set_array(self.colorsList)
        if self.animation_paused:
            self.animation_paused = False
            self._populate_simulation()
            self.buttons[0].set_active(False)
            self.buttons[0].color = 'gray'
        elif not self.animation_paused and self.has_started:
            self._populate_simulation()
            self.animation.new_frame_seq()

    def _reset_simulation_state(self):
        self.day = self.erb_counter = self.car_counter = self.hunt_counter = 0
        self.x_data = [0]
        self.y_data = [0]
        self.y_erb_data = [self.erb_counter]
        self.y_car_data = [self.car_counter]
        self.y_hunt_data = [self.hunt_counter]
        self.pop_erb = [self.y_erb_data]
        self.pop_car = [self.y_car_data]

    def _populate_simulation(self):
        if not self.animation_paused:
            self._populate_carviz()
            self._populate_erbast()

    def _populate_carviz(self):
        for _ in range(self.num_car):
            carv = Carviz(lifetime=self.car_lifetime)
            self._place_creature(carv, self.cellsList, 'pride')

    def _populate_erbast(self):
        for _ in range(self.num_erb):
            erb = Erbast(lifetime=self.erb_lifetime)
            self._place_creature(erb, self.cellsList,
                                 'erbast', check_empty=True)

    def _place_creature(self, creature, cellsList, attribute, check_empty=False):
        creature_placed = False
        while not creature_placed:
            row = random.randint(0, self.num_cells - 1)
            column = random.randint(0, self.num_cells - 1)
            if (row < self.num_cells and column < self.num_cells and
                row < len(cellsList) and column < len(cellsList[row]) and
                    cellsList[row][column].terrainType != "Water"):
                if check_empty and len(getattr(cellsList[row][column], attribute)) > 0:
                    continue
                creature.row = row
                creature.column = column
                getattr(cellsList[row][column], attribute).append(creature)
                creature_placed = True

    def reset_animation(self, event=None):
        self.animation_paused = False
        self.animation.event_source.start()
        self.start_animation()
        self.has_finished = False

    def pause_animation(self, event):
        if not self.animation_paused:
            self.animation.event_source.stop()
            self.animation_paused = True
        else:
            self.animation.event_source.start()
            self.animation_paused = False

import random
import numpy as np


class Creatures:
    NUM_CELLS = None

    def __init__(self):
        self._row = 0
        self._column = 0
        self.kernel = np.empty((0, 0), dtype=object)

    @classmethod
    def update_num_cells(cls, num_cells):
        cls.NUM_CELLS = num_cells

    @staticmethod
    def get_adjacent_cells(row, col):
        adjacent_cells = []
        max_row, max_col = Creatures.NUM_CELLS, Creatures.NUM_CELLS
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (0 <= i < max_row and 0 <= j < max_col) and (
                    i != row or j != col
                ):
                    adjacent_cells.append([i, j])
        return np.array(adjacent_cells)

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, new_row):
        self._row = new_row

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, new_column):
        self._column = new_column


class Vegetob(Creatures):
    def __init__(self):
        super().__init__()
        self._density = 0

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, new_density):
        self._density = int(new_density)

    @staticmethod
    def generate_density():
        return np.random.randint(1, 100)

    def grow(self):
        if self.density < 100:
            self.density += 1


class Erbast(Creatures):
    def __init__(self, lifetime=10):
        super().__init__()
        self._energy = np.random.randint(35, 95)
        self.lifetime = lifetime
        self.age = 0
        self.soc_attitude = 1
        self.has_moved = False

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new_energy):
        self._energy = new_energy

    def aging(self, list_of_creatures):
        self.age += 1
        if self.energy <= 1.0 or self.age >= self.lifetime:
            if self.energy >= 20 and self.age >= self.lifetime:
                self.spawn_offsprings(list_of_creatures)
            list_of_creatures.remove(self)
        elif self.age % self.lifetime == 0:
            self.energy -= 1

    def decide_movement(self, list_of_herds, is_soc_attitude_high):
        movement_coords = self.find_herd(list_of_herds)
        if is_soc_attitude_high and self.energy >= 30:
            if np.array_equal(movement_coords, [self.row, self.column]):
                movement_coords = self.find_food(list_of_herds)
            if np.array_equal(movement_coords, [self.row, self.column]):
                if list_of_herds[self.row][self.column].vegetob.density >= 35:
                    return np.array([self.row, self.column])
                if self.kernel.size > 0:
                    return np.array(
                        self.kernel[np.random.randint(0, len(self.kernel))]
                    )
        else:
            movement_coords = self.find_food(list_of_herds)
            if (
                np.array_equal(movement_coords, [self.row, self.column])
                and list_of_herds[self.row][self.column].vegetob.density >= 15
            ):
                return np.array([self.row, self.column])
        return movement_coords

    def spawn_offsprings(self, list_of_creatures):
        energy_of_offsprings = self.energy // 2
        for _ in range(2):
            erb = Erbast()
            erb.energy = energy_of_offsprings
            erb.row, erb.column = self.row, self.column
            list_of_creatures.append(erb)

    def find_herd(self, list_of_herds):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        max_erbast = 0
        max_erbast_cells = []
        for kernel_row, kernel_col in self.kernel:
            if list_of_herds[kernel_row][kernel_col].terrain_type == "Ground":
                len_of_erbast = list_of_herds[kernel_row][
                    kernel_col
                ].len_of_erbast()
                if len_of_erbast > max_erbast:
                    max_erbast = len_of_erbast
                    max_erbast_cells = [(kernel_row, kernel_col)]
                elif len_of_erbast == max_erbast:
                    max_erbast_cells.append((kernel_row, kernel_col))
        return (
            np.array(random.choice(max_erbast_cells))
            if max_erbast_cells
            else np.array([self.row, self.column])
        )

    def find_food(self, list_of_vegetobs):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        max_density = 0
        max_density_cells = []
        for kernel_row, kernel_col in self.kernel:
            if (
                list_of_vegetobs[kernel_row][kernel_col].terrain_type
                == "Ground"
            ):
                density = list_of_vegetobs[kernel_row][
                    kernel_col
                ].vegetob.density
                if density > max_density:
                    max_density = density
                    max_density_cells = [(kernel_row, kernel_col)]
                elif density == max_density:
                    max_density_cells.append((kernel_row, kernel_col))
        return (
            np.array(random.choice(max_density_cells))
            if max_density_cells
            else np.array([self.row, self.column])
        )

    def move(self, list_of_vegetobs, coordinates):
        old_row, old_col = self.row, self.column
        new_row, new_col = coordinates
        list_of_vegetobs[old_row][old_col].erbast.remove(self)
        list_of_vegetobs[new_row][new_col].erbast.append(self)
        self.row, self.column = new_row, new_col
        self.energy -= 1

    def graze(self, list_of_vegetobs, amount_to_eat):
        energy_to_eat = min(100 - self.energy, amount_to_eat)
        self.energy += energy_to_eat
        list_of_vegetobs[self.row][
            self.column
        ].vegetob.density -= energy_to_eat


class Carviz(Creatures):
    def __init__(self, lifetime=10):
        super().__init__()
        self.previous_position = None
        self._energy = np.random.randint(35, 95)
        self.lifetime = lifetime
        self._age = 0
        self.soc_attitude = 1
        self.previously_visited = None
        self.has_moved = False

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new_energy):
        self._energy = new_energy

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, new_age):
        self._age = new_age

    def aging(self, list_of_creatures):
        self.age += 1
        if self.energy <= 1.0 or self.age >= self.lifetime:
            if self.energy >= 20 and self.age >= self.lifetime:
                self.spawn_offsprings(list_of_creatures)
            list_of_creatures.remove(self)
        elif self.age % self.lifetime == 0:
            self.energy -= 1

    def spawn_offsprings(self, list_of_creatures):
        energy_of_offsprings = self.energy // 2
        for _ in range(2):
            carv = Carviz()
            carv.energy = energy_of_offsprings
            carv.row, carv.column = self.row, self.column
            list_of_creatures.append(carv)

    def find_herd(self, list_of_herds):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        max_erbast = 0
        max_erbast_cells = []
        for kernel_row, kernel_col in self.kernel:
            herd = list_of_herds[kernel_row][kernel_col]
            if herd.terrain_type == "Ground":
                len_of_erbast = herd.len_of_erbast()
                if len_of_erbast > max_erbast:
                    max_erbast = len_of_erbast
                    max_erbast_cells = [(herd.row, herd.column)]
                elif len_of_erbast == max_erbast:
                    max_erbast_cells.append((herd.row, herd.column))
        return (
            np.array(random.choice(max_erbast_cells))
            if max_erbast_cells
            else np.array([self.row, self.column])
        )

    def find_pride(self, list_of_prides):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        pride = list_of_prides[self.row][self.column]
        amount_of_pride = pride.len_of_carviz()
        row, column = self.row, self.column
        for kernel_row, kernel_col in self.kernel:
            pride_cell = list_of_prides[kernel_row][kernel_col]
            if pride_cell.terrain_type == "Ground":
                len_of_carviz = pride_cell.len_of_carviz()
                if amount_of_pride < len_of_carviz:
                    amount_of_pride = len_of_carviz
                    row, column = pride_cell.row, pride_cell.column
        return np.array([row, column])

    def move(self, list_of_vegetobs, coordinates):
        old_row, old_col = self.row, self.column
        self.previous_position = (old_row, old_col)
        self.row, self.column = coordinates
        list_of_vegetobs[self.row][self.column].append_pride(self)
        list_of_vegetobs[old_row][old_col].del_pride(self)
        self.energy -= 1

    def hunt(self, list_of_vegetobs):
        erbast = list_of_vegetobs[self.row][self.column].erbast
        erb_swap = max(erbast, key=lambda erb: erb.energy, default=None)
        if erb_swap is not None:
            energy_to_eat = min(100 - self.energy, erb_swap.energy)
            self.energy += energy_to_eat
            erbast.remove(erb_swap)

    def decide_movement(self, list_of_prides, is_soc_attitude_high):
        movement_coordinates = np.array([self.row, self.column])
        if list_of_prides[self.row][self.column].len_of_erbast() > 0:
            if is_soc_attitude_high and self.energy >= 40:
                movement_coordinates = self.find_pride(list_of_prides)
            elif not is_soc_attitude_high and self.energy >= 40:
                movement_coordinates = self.find_herd(list_of_prides)
        else:
            if is_soc_attitude_high:
                movement_coordinates = self.find_pride(list_of_prides)
            else:
                movement_coordinates = self.find_herd(list_of_prides)

        if (
            np.array_equal(movement_coordinates, [self.row, self.column])
            and self.kernel.size > 0
        ):
            movement_coordinates = self.kernel[
                np.random.choice(self.kernel.shape[0])
            ]

        return movement_coordinates

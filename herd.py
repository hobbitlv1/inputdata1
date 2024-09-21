import numpy as np


class Herd(list):
    """
    Herd class inherits from Python's list to store Erbast entities in the same cell.
    """

    def __init__(self, row, column):
        super().__init__()
        self.row = row
        self.column = column

    def herd_decision(self, cells_list):
        population = cells_list[self.row][self.column].len_of_erbast()
        herd_coords = np.array([self.row, self.column])

        for erbast in self:
            social_attitude = self._calculate_social_attitude(
                population, erbast.energy
            )
            movement_coords = erbast.decide_movement(
                cells_list, social_attitude >= 50
            )
            self._handle_erbast_movement(
                erbast, movement_coords, herd_coords, cells_list
            )

    @staticmethod
    def _calculate_social_attitude(population, energy):
        population_invers = 100 - population if population != 100 else 1
        return population_invers * energy / 100

    @staticmethod
    def _handle_erbast_movement(
        erbast, movement_coords, herd_coords, cells_list
    ):
        if np.array_equal(movement_coords, herd_coords):
            erbast.has_moved = False
        else:
            erbast.move(cells_list, movement_coords)

    def herd_graze(self, list_of_cells):
        starving_erbasts = self._get_starving_erbasts()
        vegetob_density = list_of_cells[self.row][self.column].vegetob.density
        energy_to_eat = self._calculate_energy_to_eat(
            starving_erbasts, vegetob_density
        )

        erbasts_in_cell = list_of_cells[self.row][self.column].erbast
        self._perform_grazing(
            starving_erbasts,
            erbasts_in_cell,
            vegetob_density,
            energy_to_eat,
            list_of_cells,
        )

    def _get_starving_erbasts(self):
        return [
            erb_idx
            for erb_idx, erb in enumerate(self)
            if erb.energy <= 40 and not erb.has_moved
        ]

    def _calculate_energy_to_eat(self, starving_erbasts, vegetob_density):
        population = len(self)
        return (
            vegetob_density / len(starving_erbasts)
            if starving_erbasts
            else vegetob_density / population
        )

    def _perform_grazing(
        self,
        starving_erbasts,
        erbasts_in_cell,
        vegetob_density,
        energy_to_eat,
        list_of_cells,
    ):
        if len(starving_erbasts) < vegetob_density:
            self._graze_starving_erbasts(
                starving_erbasts, erbasts_in_cell, energy_to_eat, list_of_cells
            )
        elif len(starving_erbasts) > vegetob_density:
            self._graze_limited_erbasts(
                vegetob_density, erbasts_in_cell, energy_to_eat, list_of_cells
            )
        else:
            self._graze_all_erbasts(energy_to_eat, list_of_cells)

    @staticmethod
    def _graze_starving_erbasts(
        starving_erbasts, erbasts_in_cell, energy_to_eat, list_of_cells
    ):
        for erb_idx in starving_erbasts:
            if erb_idx < len(erbasts_in_cell):
                erbasts_in_cell[erb_idx].graze(list_of_cells, energy_to_eat)

    @staticmethod
    def _graze_limited_erbasts(
        vegetob_density, erbasts_in_cell, energy_to_eat, list_of_cells
    ):
        for erb_idx in range(vegetob_density):
            if erb_idx < len(erbasts_in_cell):
                erbasts_in_cell[erb_idx].graze(list_of_cells, energy_to_eat)

    def _graze_all_erbasts(self, energy_to_eat, list_of_cells):
        for erb in self:
            erb.graze(list_of_cells, energy_to_eat)

    def group_aging(self):
        """Calls aging for all Erbasts in the herd."""
        for erb in self:
            erb.aging(self)

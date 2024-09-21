import statistics
import random
import numpy as np
from collections import defaultdict


class Pride(list):
    """Pride class inherits from list to store Carviz entities in the same cell."""

    def __init__(self, row, column):
        super().__init__()
        self.row = row
        self.column = column

    def calculate_social_attitude(self, pride_obj, cells_list):
        return [
            self._calculate_individual_social_attitude(carviz, cells_list)
            for carviz in pride_obj
        ]

    @staticmethod
    def _calculate_individual_social_attitude(carviz, cells_list):
        population = cells_list[carviz.row][carviz.column].len_of_carviz()
        population_inverse = 1 if population == 100 else 100 - population
        return population_inverse * carviz.energy / 100

    def fight_between_prides(self, carviz_list, cells_list):
        prides = self._group_carviz_into_prides(carviz_list)
        if len(prides) < 2:
            return prides

        median_social_attitudes = self._calculate_median_social_attitudes(
            prides, cells_list
        )
        winner_index = self._determine_winner(median_social_attitudes)
        remaining_prides = [
            pride for i, pride in enumerate(prides) if i != winner_index
        ]

        if len(remaining_prides) > 1:
            remaining_prides = self._join_prides_if_possible(
                remaining_prides, cells_list
            )

        return self._create_new_pride(remaining_prides)

    @staticmethod
    def _group_carviz_into_prides(carviz_list):
        prides_dict = defaultdict(lambda: Pride(0, 0))
        for carviz in carviz_list:
            prides_dict[carviz.previously_visited].append(carviz)
        return list(prides_dict.values())

    def _calculate_median_social_attitudes(self, prides, cells_list):
        return [
            statistics.median(
                self.calculate_social_attitude(pride, cells_list)
            )
            for pride in prides
        ]

    @staticmethod
    def _determine_winner(median_social_attitudes):
        return random.choices(range(len(median_social_attitudes)), k=1)[0]

    def _join_prides_if_possible(self, prides, cells_list):
        median_social_attitudes = self._calculate_median_social_attitudes(
            prides, cells_list
        )
        join_threshold = 10
        if all(
            attitude >= join_threshold for attitude in median_social_attitudes
        ):
            joined_pride = Pride(self.row, self.column)
            for pride in prides:
                joined_pride.extend(pride)
            return [joined_pride]
        return prides

    def _create_new_pride(self, prides):
        new_pride = Pride(self.row, self.column)
        new_pride.extend(prides)
        return new_pride

    def average_energy(self):
        if not self:
            return 0
        total_energy = sum(carv.energy for carv in self)
        return int(total_energy / len(self))

    def pride_decision(self, cells_list):
        for carv in self:
            self._handle_carviz_movement(carv, cells_list)

    def _handle_carviz_movement(self, carv, cells_list):
        social_attitude = self._calculate_individual_social_attitude(
            carv, cells_list
        )
        movement_coords = carv.decide_movement(
            cells_list, social_attitude >= 50
        )

        if np.array_equal(movement_coords, [self.row, self.column]):
            carv.has_moved = False
        else:
            carv.move(cells_list, movement_coords)

    @staticmethod
    def pride_move(group, list_of_cells, coordinates):
        for carv in group:
            carv.move(list_of_cells, coordinates)

    def group_aging(self):
        for carv in self:
            carv.aging(self)

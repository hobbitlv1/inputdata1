import statistics
import random
import numpy as np
from collections import defaultdict


class Pride(list):
    """
    This class is inherited from a python list and stores a list of Carviz on the same cell.
    """

    def __init__(self, row, column):
        super().__init__()
        self.row = row
        self.column = column

    def calculate_social_attitude(self, pride_obj, cellsList):
        return [
            self._calculate_individual_social_attitude(carviz, cellsList)
            for carviz in pride_obj
        ]

    def _calculate_individual_social_attitude(self, carviz, cellsList):
        population = cellsList[carviz.row][carviz.column].lenOfCarviz()
        population_inverse = 1 if population == 100 else 100 - population
        return population_inverse * carviz.energy / 100

    def fight_between_prides(self, carviz_list, cellsList):
        prides = self._group_carviz_into_prides(carviz_list)
        if len(prides) < 2:
            return prides

        median_social_attitudes = self._calculate_median_social_attitudes(
            prides, cellsList)
        winner_index = self._determine_winner(median_social_attitudes)
        remaining_prides = [pride for i, pride in enumerate(
            prides) if i != winner_index]

        if len(remaining_prides) > 1:
            remaining_prides = self._join_prides_if_possible(
                remaining_prides, cellsList)

        return self._create_new_pride(remaining_prides)

    def _group_carviz_into_prides(self, carviz_list):
        prides_dict = defaultdict(lambda: Pride(0, 0))
        for carviz in carviz_list:
            prides_dict[carviz.previouslyVisited].append(carviz)
        return list(prides_dict.values())

    def _calculate_median_social_attitudes(self, prides, cellsList):
        return [statistics.median(self.calculate_social_attitude(pride, cellsList)) for pride in prides]

    def _determine_winner(self, median_social_attitudes):
        return random.choices(range(len(median_social_attitudes)), k=1)[0]

    def _join_prides_if_possible(self, prides, cellsList):
        median_social_attitudes = self._calculate_median_social_attitudes(
            prides, cellsList)
        join_threshold = 10
        if all(attitude >= join_threshold for attitude in median_social_attitudes):
            joined_pride = Pride(self.row, self.column)
            for pride in prides:
                joined_pride.extend(pride)
            return [joined_pride]
        return prides

    def _create_new_pride(self, prides):
        new_pride = Pride(self.row, self.column)
        new_pride.extend(prides)
        return new_pride

    def averageEnergy(self):
        if not self:
            return 0
        total_energy = sum(carv.energy for carv in self)
        return int(total_energy / len(self))

    def prideDecision(self, cellsList):
        for carv in self:
            self._handle_carviz_movement(carv, cellsList)

    def _handle_carviz_movement(self, carv, cellsList):
        population = cellsList[self.row][self.column].lenOfErbast()
        social_attitude = self._calculate_individual_social_attitude(
            carv, cellsList)
        movement_coords = carv.decideMovement(cellsList, social_attitude >= 50)

        if np.array_equal(movement_coords, [self.row, self.column]):
            carv.hasMoved = False
        else:
            carv.move(cellsList, movement_coords)

    def prideMove(self, group, listOfCells, coordinates):
        for carv in group:
            carv.move(listOfCells, coordinates)

    def groupAging(self):
        for carv in self:
            carv.aging(self)

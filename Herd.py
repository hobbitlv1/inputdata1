import numpy as np


class Herd(list):
    """
    This class is inherited from a python list and stores an list of Erbast on the same cell.
    """

    def __init__(self, row, column):
        super().__init__()
        self.row = row
        self.column = column

    def herdDecision(self, cellsList):
        population = cellsList[self.row][self.column].lenOfErbast()
        herd_coords = np.array([self.row, self.column])

        for erbast in self:
            socialAttitude = self._calculate_social_attitude(
                population, erbast.energy)
            movementCoords = erbast.decideMovement(
                cellsList, socialAttitude >= 50)
            self._handle_erbast_movement(
                erbast, movementCoords, herd_coords, cellsList)

    def _calculate_social_attitude(self, population, energy):
        populationInvers = 100 - population if population != 100 else 1
        return populationInvers * energy / 100

    def _handle_erbast_movement(self, erbast, movementCoords, herd_coords, cellsList):
        if np.array_equal(movementCoords, herd_coords):
            erbast.hasMoved = False
        else:
            erbast.move(cellsList, movementCoords)

    def herdGraze(self, listOfCells):
        starving_erbasts = self._get_starving_erbasts()
        vegetob_density = listOfCells[self.row][self.column].vegetob.density
        energy_to_eat = self._calculate_energy_to_eat(
            starving_erbasts, vegetob_density)

        erbasts_in_cell = listOfCells[self.row][self.column].erbast
        self._perform_grazing(starving_erbasts, erbasts_in_cell,
                              vegetob_density, energy_to_eat, listOfCells)

    def _get_starving_erbasts(self):
        return [erb_idx for erb_idx, erb in enumerate(self) if erb.energy <= 40 and not erb.hasMoved]

    def _calculate_energy_to_eat(self, starving_erbasts, vegetob_density):
        population = len(self)
        return vegetob_density / len(starving_erbasts) if starving_erbasts else vegetob_density / population

    def _perform_grazing(self, starving_erbasts, erbasts_in_cell, vegetob_density, energy_to_eat, listOfCells):
        if len(starving_erbasts) < vegetob_density:
            self._graze_starving_erbasts(
                starving_erbasts, erbasts_in_cell, energy_to_eat, listOfCells)
        elif len(starving_erbasts) > vegetob_density:
            self._graze_limited_erbasts(
                vegetob_density, erbasts_in_cell, energy_to_eat, listOfCells)
        else:
            self._graze_all_erbasts(energy_to_eat, listOfCells)

    def _graze_starving_erbasts(self, starving_erbasts, erbasts_in_cell, energy_to_eat, listOfCells):
        for erb_idx in starving_erbasts:
            if erb_idx < len(erbasts_in_cell):
                erbasts_in_cell[erb_idx].graze(listOfCells, energy_to_eat)

    def _graze_limited_erbasts(self, vegetob_density, erbasts_in_cell, energy_to_eat, listOfCells):
        for erb_idx in range(vegetob_density):
            if erb_idx < len(erbasts_in_cell):
                erbasts_in_cell[erb_idx].graze(listOfCells, energy_to_eat)

    def _graze_all_erbasts(self, energy_to_eat, listOfCells):
        for erb in self:
            erb.graze(listOfCells, energy_to_eat)

    def groupAging(self):
        """
        An interface to call aging for all erbasts on the same cell.
        :return:
        """
        for erb in self:
            erb.aging(self)

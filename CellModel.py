from Creatures import Vegetob, Erbast
from Herd import Herd
from Pride import Pride


class Cell:

    def __init__(self, row, column, terrainType, vegetob):
        self.row = row
        self.column = column
        self.terrainType = terrainType
        self.vegetob = vegetob
        self.erbast = Herd(row, column)
        self.pride = Pride(row, column)

    def lenOfErbast(self):
        return len(self.erbast)

    def delErbast(self, erb):
        self.erbast.remove(erb)

    def lenOfCarviz(self):
        return len(self.pride)

    def appendPride(self, pride):
        self.pride.append(pride)

    def delPride(self, pride):
        self.pride.remove(pride)

    def death_from_vegetob(self, listOfVegetobs):
        if self.erbast or self.pride:
            kernel = self._get_kernel(listOfVegetobs)
            if len(kernel) == 8:
                vegetob_full_density_counter = self._count_full_density_vegetobs(kernel, listOfVegetobs)
                if vegetob_full_density_counter == 8:
                    self._clear_creatures()

    def _get_kernel(self, listOfVegetobs):
        creature = self.erbast[0] if self.erbast else self.pride[0] if self.pride else None
        return creature.get_adjacent_cells(self.row, self.column) if creature else []

    def _count_full_density_vegetobs(self, kernel, listOfVegetobs):
        return sum(1 for row, col in kernel 
                   if listOfVegetobs[row][col].vegetob and 
                   listOfVegetobs[row][col].vegetob.density == 100)

    def _clear_creatures(self):
        if self.erbast:
            self.erbast.clear()
        if self.pride:
            self.pride.clear()

    def __str__(self):
        if self.terrainType == "Ground":
            return f"({self.row}, {self.column}, {self.terrainType}, {self.vegetob.density}, {self.erbast}, {self.pride})"

        return f"({self.row}, {self.column}, {self.terrainType}, {self.vegetob}, erbast: {self.erbast}, carviz: {self.pride})"

    def __repr__(self):
        return self.__str__()




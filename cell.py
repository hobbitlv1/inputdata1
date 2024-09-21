from herd import Herd
from pride import Pride


class Cell:
    def __init__(self, row, column, terrain_type, vegetob):
        self.row = row
        self.column = column
        self.terrain_type = terrain_type
        self.vegetob = vegetob
        self.erbast = Herd(row, column)
        self.pride = Pride(row, column)

    def len_of_erbast(self):
        return len(self.erbast)

    def del_erbast(self, erb):
        self.erbast.remove(erb)

    def len_of_carviz(self):
        return len(self.pride)

    def append_pride(self, pride):
        self.pride.append(pride)

    def del_pride(self, pride):
        self.pride.remove(pride)

    def death_from_vegetob(self, list_of_vegetobs):
        if self.erbast or self.pride:
            kernel = self._get_kernel(list_of_vegetobs)
            if len(kernel) == 8:
                vegetob_full_density_counter = (
                    self._count_full_density_vegetobs(kernel, list_of_vegetobs)
                )
                if vegetob_full_density_counter == 8:
                    self._clear_creatures()

    def _get_kernel(self, list_of_vegetobs):
        creature = (
            self.erbast[0]
            if self.erbast
            else self.pride[0] if self.pride else None
        )
        return (
            creature.get_adjacent_cells(self.row, self.column)
            if creature
            else []
        )

    @staticmethod
    def _count_full_density_vegetobs(kernel, list_of_vegetobs):
        return sum(
            1
            for row, col in kernel
            if list_of_vegetobs[row][col].vegetob
            and list_of_vegetobs[row][col].vegetob.density == 100
        )

    def _clear_creatures(self):
        if self.erbast:
            self.erbast.clear()
        if self.pride:
            self.pride.clear()

    def __str__(self):
        if self.terrain_type == "Ground":
            return f"({self.row}, {self.column}, {self.terrain_type}, {self.vegetob.density}, {self.erbast}, {self.pride})"

        return f"({self.row}, {self.column}, {self.terrain_type}, {self.vegetob}, erbast: {self.erbast}, carviz: {self.pride})"

    def __repr__(self):
        return self.__str__()

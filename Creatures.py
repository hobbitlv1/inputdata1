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

    def get_adjacent_cells(self, row, col):
        adjacent_cells = []
        max_row, max_col = Creatures.NUM_CELLS, Creatures.NUM_CELLS
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (0 <= i < max_row and 0 <= j < max_col) and (i != row or j != col):
                    adjacent_cells.append([i, j])
        return np.array(adjacent_cells)

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, newRow):
        self._row = newRow

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, newColumn):
        self._column = newColumn

class Vegetob(Creatures):
    def __init__(self):
        super().__init__()
        self._density = 0

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, newDensity):
        self._density = int(newDensity)

    def generateDensity(self):
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
        self.hasMoved = False

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, newEnergy):
        self._energy = newEnergy

    def aging(self, listOfCreatures):
        self.age += 1
        if self.energy <= 1.0 or self.age >= self.lifetime:
            if self.energy >= 20 and self.age >= self.lifetime:
                self.spawnOffsprings(listOfCreatures)
            listOfCreatures.remove(self)
        elif self.age % self.lifetime == 0:
            self.energy -= 1

    def decideMovement(self, listOfHerd, isSocAttitudeHigh):
        movement_coordinates = self.findHerd(listOfHerd)
        if isSocAttitudeHigh and self.energy >= 30:
            if np.array_equal(movement_coordinates, [self.row, self.column]):
                movement_coordinates = self.findFood(listOfHerd)
            if np.array_equal(movement_coordinates, [self.row, self.column]):
                if listOfHerd[self.row][self.column].vegetob.density >= 35:
                    return np.array([self.row, self.column])
                elif len(self.kernel) > 0:
                    return np.array(self.kernel[np.random.randint(0, len(self.kernel))])
        else:
            movement_coordinates = self.findFood(listOfHerd)
            if np.array_equal(movement_coordinates, [self.row, self.column]) and listOfHerd[self.row][self.column].vegetob.density >= 15:
                return np.array([self.row, self.column])
        return movement_coordinates

    def spawnOffsprings(self, listOfCreatures):
        energyOfOffsprings = self.energy // 2
        for _ in range(2):
            erb = Erbast()
            erb.energy = energyOfOffsprings
            erb.row, erb.column = self.row, self.column
            listOfCreatures.append(erb)

    def findHerd(self, listOfHerds):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        maxErbast = 0
        maxErbastCells = []
        for kernel_row, kernel_col in self.kernel:
            if listOfHerds[kernel_row][kernel_col].terrainType == "Ground":
                lenOfErbast = listOfHerds[kernel_row][kernel_col].lenOfErbast()
                if lenOfErbast > maxErbast:
                    maxErbast = lenOfErbast
                    maxErbastCells = [(kernel_row, kernel_col)]
                elif lenOfErbast == maxErbast:
                    maxErbastCells.append((kernel_row, kernel_col))
        return np.array(random.choice(maxErbastCells)) if maxErbastCells else np.array([self.row, self.column])

    def findFood(self, listOfVegetobs):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        maxDensity = 0
        maxDensityCells = []
        for kernel_row, kernel_col in self.kernel:
            if listOfVegetobs[kernel_row][kernel_col].terrainType == "Ground":
                density = listOfVegetobs[kernel_row][kernel_col].vegetob.density
                if density > maxDensity:
                    maxDensity = density
                    maxDensityCells = [(kernel_row, kernel_col)]
                elif density == maxDensity:
                    maxDensityCells.append((kernel_row, kernel_col))
        return np.array(random.choice(maxDensityCells)) if maxDensityCells else np.array([self.row, self.column])

    def move(self, listOfVegetobs, coordinates):
        oldRow, oldCol = self.row, self.column
        newRow, newCol = coordinates
        listOfVegetobs[oldRow][oldCol].erbast.remove(self)
        listOfVegetobs[newRow][newCol].erbast.append(self)
        self.row, self.column = newRow, newCol
        self.energy -= 1

    def graze(self, listOfVegetobs, amountToEat):
        energyToEat = min(100 - self.energy, amountToEat)
        self.energy += energyToEat
        listOfVegetobs[self.row][self.column].vegetob.density -= energyToEat

class Carviz(Creatures):
    def __init__(self, lifetime=10):
        super().__init__()
        self.previous_position = None
        self._energy = np.random.randint(35, 95)
        self.lifetime = lifetime
        self._age = 0
        self.soc_attitude = 1
        self.previouslyVisited = None
        self.hasMoved = False

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, newEnergy):
        self._energy = newEnergy

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, newAge):
        self._age = newAge

    def aging(self, listOfCreatures):
        self.age += 1
        if self.energy <= 1.0 or self.age >= self.lifetime:
            if self.energy >= 20 and self.age >= self.lifetime:
                self.spawnOffsprings(listOfCreatures)
            listOfCreatures.remove(self)
        elif self.age % self.lifetime == 0:
            self.energy -= 1

    def spawnOffsprings(self, listOfCreatures):
        energyOfOffsprings = self.energy // 2
        for _ in range(2):
            carv = Carviz()
            carv.energy = energyOfOffsprings
            carv.row, carv.column = self.row, self.column
            listOfCreatures.append(carv)

    def findHerd(self, listOfHerds):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        maxErbast = 0
        maxErbastCells = []
        for kernel_row, kernel_col in self.kernel:
            herd = listOfHerds[kernel_row][kernel_col]
            if herd.terrainType == "Ground":
                lenOfErbast = herd.lenOfErbast()
                if lenOfErbast > maxErbast:
                    maxErbast = lenOfErbast
                    maxErbastCells = [(herd.row, herd.column)]
                elif lenOfErbast == maxErbast:
                    maxErbastCells.append((herd.row, herd.column))
        return np.array(random.choice(maxErbastCells)) if maxErbastCells else np.array([self.row, self.column])

    def findPride(self, listOfPrides):
        self.kernel = self.get_adjacent_cells(self.row, self.column)
        pride = listOfPrides[self.row][self.column]
        amountOfPride = pride.lenOfCarviz()
        row, column = self.row, self.column
        for kernel_row, kernel_col in self.kernel:
            pride_cell = listOfPrides[kernel_row][kernel_col]
            if pride_cell.terrainType == "Ground":
                lenOfCarviz = pride_cell.lenOfCarviz()
                if amountOfPride < lenOfCarviz:
                    amountOfPride = lenOfCarviz
                    row, column = pride_cell.row, pride_cell.column
        return np.array([row, column])

    def move(self, listOfVegetobs, coordinates):
        oldRow, oldCol = self.row, self.column
        self.previous_position = (oldRow, oldCol)
        self.row, self.column = coordinates
        listOfVegetobs[self.row][self.column].appendPride(self)
        listOfVegetobs[oldRow][oldCol].delPride(self)
        self.energy -= 1

    def hunt(self, listOfVegetobs):
        erbast = listOfVegetobs[self.row][self.column].erbast
        erbSwap = max(erbast, key=lambda erb: erb.energy, default=None)
        if erbSwap is not None:
            energy_to_eat = min(100 - self.energy, erbSwap.energy)
            self.energy += energy_to_eat
            erbast.remove(erbSwap)

    def decideMovement(self, listOfPride, isSocAttitudeHigh):
        movement_coordinates = np.array([self.row, self.column])
        if listOfPride[self.row][self.column].lenOfErbast() > 0:
            if isSocAttitudeHigh and self.energy >= 40:
                movement_coordinates = self.findPride(listOfPride)
            elif not isSocAttitudeHigh and self.energy >= 40:
                movement_coordinates = self.findHerd(listOfPride)
        else:
            if isSocAttitudeHigh:
                movement_coordinates = self.findPride(listOfPride)
            else:
                movement_coordinates = self.findHerd(listOfPride)

        if np.array_equal(movement_coordinates, [self.row, self.column]) and self.kernel.size > 0:
            movement_coordinates = self.kernel[np.random.choice(self.kernel.shape[0])]

        return movement_coordinates

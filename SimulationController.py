class SimulationController:
    """
    SimulationController class is only used in FuncAnimation update method
    of the View module, since the simulate method requires an updating cellsList
    """

    def simulate(self, cellsList):
        self._grow_vegetob(cellsList)
        self._handle_creature_death(cellsList)
        self._handle_creature_decisions(cellsList)
        self._handle_pride_fights(cellsList)
        self._handle_creature_actions(cellsList)
        self._handle_creature_aging(cellsList)

    def _grow_vegetob(self, cellsList):
        for sublist in cellsList:
            for cell in sublist:
                if cell.terrainType != "Water":
                    cell.vegetob.grow()

    def _handle_creature_death(self, cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast or cell.pride:
                    cell.death_from_vegetob(cellsList)

    def _handle_creature_decisions(self, cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herdDecision(cellsList)
                if cell.pride:
                    cell.pride.prideDecision(cellsList)

    def _handle_pride_fights(self, cellsList):
        for row in cellsList:
            for cell in row:
                if cell.pride:
                    cell.pride.fight_between_prides(cell.pride, cellsList)

    def _handle_creature_actions(self, cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herdGraze(cellsList)
                if cell.pride:
                    for carviz in cell.pride:
                        if cell.erbast:
                            carviz.hunt(cellsList)

    def _handle_creature_aging(self, cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.groupAging()
                if cell.pride:
                    cell.pride.groupAging()
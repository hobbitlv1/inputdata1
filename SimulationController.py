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

    @staticmethod
    def _grow_vegetob(cellsList):
        for sublist in cellsList:
            for cell in sublist:
                if cell.terrainType != "Water":
                    cell.vegetob.grow()

    @staticmethod
    def _handle_creature_death(cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast or cell.pride:
                    cell.death_from_vegetob(cellsList)

    @staticmethod
    def _handle_creature_decisions(cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herdDecision(cellsList)
                if cell.pride:
                    cell.pride.prideDecision(cellsList)

    @staticmethod
    def _handle_pride_fights(cellsList):
        for row in cellsList:
            for cell in row:
                if cell.pride:
                    cell.pride.fight_between_prides(cell.pride, cellsList)

    @staticmethod
    def _handle_creature_actions(cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herdGraze(cellsList)
                if cell.pride:
                    for carviz in cell.pride:
                        if cell.erbast:
                            carviz.hunt(cellsList)

    @staticmethod
    def _handle_creature_aging(cellsList):
        for row in cellsList:
            for cell in row:
                if cell.erbast:
                    cell.erbast.groupAging()
                if cell.pride:
                    cell.pride.groupAging()

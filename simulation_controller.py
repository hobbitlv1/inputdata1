class SimulationController:
    """
    SimulationController class manages the simulation steps.
    """

    def simulate(self, cells_list):
        self._grow_vegetob(cells_list)
        self._handle_creature_death(cells_list)
        self._handle_creature_decisions(cells_list)
        self._handle_pride_fights(cells_list)
        self._handle_creature_actions(cells_list)
        self._handle_creature_aging(cells_list)

    @staticmethod
    def _grow_vegetob(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.terrain_type != "Water":
                    cell.vegetob.grow()

    @staticmethod
    def _handle_creature_death(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.erbast or cell.pride:
                    cell.death_from_vegetob(cells_list)

    @staticmethod
    def _handle_creature_decisions(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herd_decision(cells_list)
                if cell.pride:
                    cell.pride.pride_decision(cells_list)

    @staticmethod
    def _handle_pride_fights(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.pride:
                    cell.pride.fight_between_prides(cell.pride, cells_list)

    @staticmethod
    def _handle_creature_actions(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.erbast:
                    cell.erbast.herd_graze(cells_list)
                if cell.pride:
                    for carviz in cell.pride:
                        if cell.erbast:
                            carviz.hunt(cells_list)

    @staticmethod
    def _handle_creature_aging(cells_list):
        for row in cells_list:
            for cell in row:
                if cell.erbast:
                    cell.erbast.group_aging()
                if cell.pride:
                    cell.pride.group_aging()

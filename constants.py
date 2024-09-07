# planisuss_constants.py
"""
Collection of the main constants defined for the "Planisuss" project.
Values can be modified according to the envisioned behavior of the simulated world.
---
v 1.00
Stefano Ferrari
2023-02-07
"""
import sys
sys.path.append(".")

# Game constants
MAX_DAYS = 10000     # Length of the simulation in days
NUM_CELLS = 50       # size of the (square) grid (NUMCELLS x NUMCELLS)

# Creature lifetimes
MAX_LIFE_C = 10
MAX_LIFE_E = 10

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[1m'

# Grid geometry
NUMCELLS_R = 1000    # number of rows of the (potentially non-square) grid
NUMCELLS_C = 1000    # number of columns of the (potentially non-square) grid

# Social group parameters
# radius of the region that a social group can evaluate to decide the movement
NEIGHBORHOOD = 1
NEIGHBORHOOD_E = 1   # radius of the region that a herd can evaluate to decide the movement
NEIGHBORHOOD_C = 1   # radius of the region that a pride can evaluate to decide the movement

# Group size limits
MAX_HERD = 1000      # maximum numerosity of a herd
MAX_PRIDE = 100      # maximum numerosity of a pride

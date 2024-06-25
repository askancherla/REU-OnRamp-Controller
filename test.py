import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from Vehicle import Vehicle


# A = [[1], [2], [3]]
# B = [['Pos'], ['Vel'], ['Pos', 'Vel']]
# C = [[[0]], [[1]], [[2]]]

# combinations = [list(combo) for combo in itertools.product(A, B, C)]

# # Print each combination
# for combo in combinations:
#     print(f"Combination is: {combo}")


vehicles = [
    Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
    Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
    Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
    Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
    Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
]

columns = [veh.id for veh in vehicles]
print(f"All veh ids: {columns}")

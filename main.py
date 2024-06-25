from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
# import the Simulation class from Simulation.py
from Simulation import Simulation
import numpy as np

vehicles = [
    Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
    Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
    Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
    Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
    Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
]

sim = Simulation(vehicles, 20, 0.1)
if sim.check == 1:
    sim.mergeSimulator()

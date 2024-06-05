# main.py
import numpy as np
from OnRampController import Vehicle, simulate_vehicles


# Simulation parameters
delta_t = 0.1  # Time step size (s)
total_time = 60.0  # Total simulation time (s)
steps = int(total_time / delta_t)  # Number of simulation steps


# Initialize vehicles
# Main lane vehicles: Initial position spaced 30m apart, initial velocity 25.0 m/s
# Ramp vehicles: Initial position starting from 3000m, spaced 30m apart, initial velocity 25.0 m/s
vehicles = [Vehicle(position=i*30, velocity=25.0) for i in range(10)] + \
          [Vehicle(position=3000 + i*30, velocity=25.0) for i in range(5)]


# Control gains
Q1 = 0.1  # Gain for position error
Q2 = 0.1  # Gain for velocity error
R = 0.0   # Constant term, set to 0 to avoid constant acceleration bias


# Simulate vehicles
simulate_vehicles(vehicles, steps, delta_t, Q1, Q2, R)




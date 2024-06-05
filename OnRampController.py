# OnRampController.py
import numpy as np


class Vehicle:
   def __init__(self, position, velocity):
       self.position = position  # Vehicle's initial position
       self.velocity = velocity  # Vehicle's initial velocity
       self.acceleration = 0.0   # Vehicle's initial acceleration


   def update(self, delta_t):
       # Update velocity using the calculated acceleration
       self.velocity += self.acceleration * delta_t
       # Update position using the updated velocity
       self.position += self.velocity * delta_t


   def control(self, target_position, target_velocity, Q1, Q2, R):
       # Calculate the position error
       position_error = target_position - self.position
       # Calculate the velocity error
       velocity_error = target_velocity - self.velocity


       # Check for NaN values and handle them
       if np.isnan(position_error):
           position_error = 0.0
       if np.isnan(velocity_error):
           velocity_error = 0.0


       # Calculate acceleration based on control gains and errors
       self.acceleration = Q1 * position_error + Q2 * velocity_error + R
       # Ensure acceleration is not NaN
       if np.isnan(self.acceleration):
           self.acceleration = 0.0


def simulate_vehicles(vehicles, steps, delta_t, Q1, Q2, R):
   for step in range(steps):
       for i, vehicle in enumerate(vehicles):
           if i < 10:
               # Main lane vehicles
               target_position = vehicle.position + 30  # Maintain a 30m gap
               target_velocity = 25.0  # Desired velocity for main lane vehicles
           else:
               # Ramp vehicles
               target_position = vehicles[i-10].position - 30  # Merge with a 30m gap
               target_velocity = vehicles[i-10].velocity  # Match velocity with main lane vehicle


           # Apply control law to determine acceleration
           vehicle.control(target_position, target_velocity, Q1, Q2, R)
           # Update vehicle's position and velocity
           vehicle.update(delta_t)


       # Print status every 100 steps
       if step % 100 == 0:
           print(f"Step {step}/{steps}")
           for i, vehicle in enumerate(vehicles):
               print(f"Vehicle {i} updated: Position = {vehicle.position:.2f}, Velocity = {vehicle.velocity:.2f}")


   # Print final status of all vehicles
   for i, vehicle in enumerate(vehicles):
       print(f"Vehicle {i}: Position = {vehicle.position:.2f}, Velocity = {vehicle.velocity:.2f}")




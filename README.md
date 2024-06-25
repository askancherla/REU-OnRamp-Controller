# V2V Communication-Based On-Ramp Merging Simulation

## Summary of the Python Program

The provided Python program simulates the scenario of on-ramp vehicles merging into mainline traffic using vehicle-to-vehicle (V2V) communication, as described in the research paper "Coordinated Merge Control Based on V2V Communication."

## Road Layout

  <img src="Merge Road Layout.PNG" alt="Merge Road Layout." style="zoom:100%;" />

Merge vehicles should be merged into the mainlane vehicles before the merge point (MP), which is (0,0). The position value of all vehicles at the left of MP are negative. The length of the acceleration lane is 200 m based on the paper. We can initialize any number of mainlane and merge vehicles at the left of acceleration lane before the simulation as long as their relative time and space headways are larger than the safety values. We do not consider any lane change on the mainlane and mergelane, therefore we only have the rightmost lane in the mainlane traffic.

## How to run the program

In "main.py", we can change the vehicle numbers on each lane initially, their ids (positive for mainlane CAVs, negative for mergelane CAVs), initial position and velocity values. We can also change the total simulation time and time step. Then, run "main.py".

## How the Code Relates to the Paper

### Initialization

The program starts by defining the initial positions and speeds of the vehicles on the mainline and the on-ramp. This setup is a simplified version of the traffic scenario described in the paper.

### Speed Coordination

The `speed_coordination` function in the Vehicle class implements Equation (2) from the paper. This equation adjusts the acceleration of the on-ramp vehicle to match the average speed of the mainline traffic. The gain `k` is a control parameter.

### Gap Alignment

The `gap_alignment` function in the Vehicle class determines the virtual leader (VL) and virtual follower (VF) for the on-ramp vehicle. This is crucial for aligning the on-ramp vehicle with a gap in the mainline traffic.

### Virtual Platoon Control

The `virtual_platoon_control` function in the Vehicle class implements Equation (4) from the paper. This function ensures that the on-ramp vehicle adjusts its speed to maintain a safe distance within the virtual platoon.

<!-- ### Sensor Noise Model

The `sensor_noise` function implements the Gauss-Markov noise model from Equations (6), (7), and (8). This simulates GPS position measurement errors, which affect the accuracy of vehicle position data used in the V2V communication. -->

### Simulation Class

The Simulation class runs for a specified number of time steps, updating the positions and speeds of the vehicles at each step.

## How It Relates to the Paper

### High-Fidelity Traffic Microsimulation

The program models the merging behavior of vehicles using high-fidelity microsimulation, similar to the approach described in the paper.

### V2V Communication

The core idea of using V2V communication for coordinating the merging of on-ramp vehicles with mainline traffic is implemented through the functions that manage speed coordination, gap alignment, and virtual platoon control.

-Based on the research paper: https://ieeexplore.ieee.org/abstract/document/7835933

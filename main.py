import numpy as np

# Constants and control gains
k = 0.1
kp = 0.5
kd = 0.1
hd = 1.3
dt = 0.1
beta = 1 / 600
sigma_g = 0.202
sigma_r = 0.0027

# Initialize vehicle positions and speeds
mainline_vehicles = [{'x': 100, 'v': 20}, {'x': 200, 'v': 20}, {'x': 300, 'v': 20}]
on_ramp_vehicle = {'x': 0, 'v': 15}
v_ref = np.mean([vehicle['v'] for vehicle in mainline_vehicles])

# Function to update position and speed
def update_position(vehicle, a):
    vehicle['v'] += a * dt
    vehicle['x'] += vehicle['v'] * dt
    return vehicle

# Speed coordination (Equation 2)
def speed_coordination(vehicle, v_ref):
    a_k_s = k * (v_ref - vehicle['v'])
    return a_k_s

# Gap alignment (finding VL and VF)
def gap_alignment(on_ramp_vehicle, mainline_vehicles):
    sorted_vehicles = sorted(mainline_vehicles, key=lambda v: v['x'])
    for i in range(len(sorted_vehicles) - 1):
        if sorted_vehicles[i]['x'] <= on_ramp_vehicle['x'] <= sorted_vehicles[i+1]['x']:
            return sorted_vehicles[i], sorted_vehicles[i+1]
    return None, None

# Virtual platoon control (Equation 4)
def virtual_platoon_control(vl, vf, on_ramp_vehicle):
    x_k_s = on_ramp_vehicle['x']
    x_k_t = vl['x']
    v_k_s = on_ramp_vehicle['v']
    v_k_t = vl['v']
    v_k_minus_1_s = vf['v']
    
    desired_speed = v_k_minus_1_s + kp * (x_k_s - x_k_t - hd * v_k_s) + kd * (v_k_s - v_k_t - hd * v_k_minus_1_s)
    a_k_s = (desired_speed - v_k_s) / dt
    return a_k_s

# Sensor noise model (Equation 6, 7, 8)
def sensor_noise():
    m_k = np.random.normal(0, sigma_g)
    n_k = m_k + np.random.normal(0, sigma_r)
    return m_k, n_k

# Simulation loop
time_steps = 100
for t in range(time_steps):
    # Speed coordination for on-ramp vehicle
    a = speed_coordination(on_ramp_vehicle, v_ref)
    on_ramp_vehicle = update_position(on_ramp_vehicle, a)
    
    # Gap alignment
    vl, vf = gap_alignment(on_ramp_vehicle, mainline_vehicles)
    
    # Virtual platoon control if gap alignment successful
    if vl and vf:
        a = virtual_platoon_control(vl, vf, on_ramp_vehicle)
        on_ramp_vehicle = update_position(on_ramp_vehicle, a)
    
    # Update mainline vehicle positions
    for vehicle in mainline_vehicles:
        vehicle = update_position(vehicle, 0)
    
    # Print positions and speeds for debugging
    print(f"Time {t * dt:.1f}s")
    print(f"On-ramp vehicle: Position {on_ramp_vehicle['x']:.1f}m, Speed {on_ramp_vehicle['v']:.1f}m/s")
    for i, vehicle in enumerate(mainline_vehicles):
        print(f"Mainline vehicle {i+1}: Position {vehicle['x']:.1f}m, Speed {vehicle['v']:.1f}m/s")
    print("-" * 40)

import numpy as np


class Vehicle():

    def __init__(self, lane, init_Vel, init_Pos, dt, t):
        self.lane = lane      # 0 mainline and 1 merge lane
        self.Vel = init_Vel   # will record the speed of the self object at each time step
        self.Pos = init_Pos   # will record the position of the self object at each time step
        self.Acc = 0   # Assume all vehicles are running at a constant speed initially
        self.dt = dt   # time interval
        self.t = t     # current time step
        self.safe_time_headway = 1.5   # second
        self.maxAcc = 2                # m/(s^2)
        self.comfortable_Acc = 1       # m/(s^2)
        self.min_gap = 2               # meters
        self.desired_Vel = 20          # m/s
        self.length = 4.5  # meters, length of the vehicle

    """Acc of each vehicle if it does not have a vehicle to follow. 
       Based on the paper [An Enhanced Microscopic Traffic Simulation Model for Application to Connected Automated Vehicles] """

    def manualDriverModel(self):
        ffspeed = 30  # free flow speed m/s
        alpha = 3  # sensitivity exponent

        self.Acc = self.maxAcc*[1-((self.Vel)/(ffspeed))**alpha]

    """Acc of each vehicle if it has a vehicle to follow. 
       Based on the paper [Congested Traffic States in Empirical Observations and Microscopic Simulations] """

    # assume the simulation will gives the leading_vehicle object
    def intelligent_driver_model(self, leading_vehicle):
        # IDM parameters
        T = self.safe_time_headway
        a = self.maxAcc
        b = self.comfortable_Acc
        delta = 4
        s0 = self.min_gap
        v0 = self.desired_Vel

        if leading_vehicle:    # if self has a leading vehicle object
            delta_v = self.Vel - leading_vehicle.Vel
            s_star = s0 + max(0, self.Vel * T +
                              (self.Vel * delta_v) / (2 * np.sqrt(a * b)))
            gap = leading_vehicle.Pos - leading_vehicle.length - self.Pos
            self.Acc = a * (1 - (self.Vel / v0) **
                            delta - (s_star / gap) ** 2)
        else:
            self.Acc = a * (1 - (self.Vel / v0) ** delta)

    """Acc of each vehicle if it is in the merging section. 
       Based on the paper [Coordinated Merge Control Based on V2V Communication] """

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

        desired_speed = v_k_minus_1_s + kp * \
            (x_k_s - x_k_t - hd * v_k_s) + kd * \
            (v_k_s - v_k_t - hd * v_k_minus_1_s)
        a_k_s = (desired_speed - v_k_s) / dt
        return a_k_s

     # Function to update position and speed

    def updateStatus(self, Acc):
        self.Vel += self.Acc * self.dt
        self.Pos += self.dt*self.Vel+((self.dt ^ 2)/2)*self.Acc


if __name__ == '__main__':
    vehicle = Vehicle(Vel=20, Pos=100, dt=0.1, t=0, lane=0)

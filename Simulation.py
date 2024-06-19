from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
import numpy as np
import pandas as pd


class Simulation:
    def __init__(self, vehicles, total_time, time_interval):
        self.vehicles = vehicles    # get all vehicles' initial status
        # initialize to store the transmitInfo from all CAVs
        self.min_gap = 2          # meter, same as the one in Vehicle Class
        self.safe_time_headway = 1.5   # second, same as the one in Vehicle Class
        self.minVel = 5    # m/s
        self.maxVel = 30   # m/s= 108km/h ~= 67 mph
        self.minAcc = -4   # m/s^2
        self.maxAcc = 2    # m/s^2
        self.mainVeh_list = []    # store all mainlane CAV objects
        self.mergeVeh_list = []   # store all merge CAV objects
        self.veh_transmitInfo_list = []  # store the info from all CAVs broadcast

        # [[id=1, Vel=20, Pos = -300,..],
        #  [id=2, Vel=22, Pos = -400,..]
        #  ...
        #  [                           ]]

        self.total_time = total_time
        self.dt = time_interval
        self.Veh_Pos_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])  # initialize a dataframe for ploting. rows: # of time step, column: # of CAVs
        self.Veh_Vel_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])
        self.Veh_Acc_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])
        # 0 if there is something wrong in the initial settings, otherwise 1
        self.check = self.mergeInitialCheck()

    ##################################################
    # Check the initial settings of all CAVs object
    ##################################################

    def mergeInitialCheck(self):
        for veh in self.vehicles:
            """ 1. Check the initial velocity of CAVs """
            if veh.Vel > self.maxVel or veh.Vel < self.minVel:
                print(
                    "CAVs need to be reset: All CAVs velocity should between min and max")
                return 0

            """ 2. Separate CAVs on the mainlane and mergelane"""
            if veh.lane == 0:            # 0: mainlane
                self.mainVeh_list.append(veh)
            elif veh.lane == 1:          # 1: mergelane
                self.mergeVeh_list.append(veh)
            else:
                print("Error in the lane ID, neither 0 or 1")
                return 0

        # sorted the vehicles by their position (from large to small value)
        # 'x' is a temporate variable which refers to the element of the list
        self.mainVeh_list.sort(key=lambda x: x.Pos, reverse=True)
        self.mergeVeh_list.sort(key=lambda x: x.Pos, reverse=True)

        """ 3. Check all CAVs should behind the acceleration lane initially"""
        if ((self.mainVeh_list[0].Pos > -200) or (self.mergeVeh_list[0].Pos > -200)):
            print(
                "CAVs need to be reset: All CAVs should be behind the acceleration lane")
            return 0

        """ 4. Check the time and space headway of the CAVs are large enough initially"""
        for i in range(len(self.mainVeh_list)-1):
            if (abs((self.mainVeh_list[i+1].Pos - self.mainVeh_list[i].Pos)) < self.min_gap) or (abs((self.mainVeh_list[i+1].Pos - self.mainVeh_list[i].Pos))/self.mainVeh_list[i+1].Vel < self.safe_time_headway):
                print(f"Initial States of mainlane CAV{i} need to be reset")
                return 0

        for i in range(len(self.mergeVeh_list)-1):
            if (abs((self.mergeVeh_list[i+1].Pos - self.mergeVeh_list[i].Pos)) < self.min_gap) or (abs((self.mergeVeh_list[i+1].Pos - self.mergeVeh_list[i].Pos))/self.mergeVeh_list[i+1].Vel < self.safe_time_headway):
                print(f"Initial States of mergelane CAV{i} need to be reset")
                return 0

        return 1

    ##################################################
    # Run the Simulator for on-ramp merging scenario
    ##################################################
    def mergeSimulator(self):

        for t in np.arange(0, self.total_time, self.dt):
            """1. Each CAV shares its info to others"""
            self.veh_transmitInfo_list = [
            ]   # empty the self.veh_transmitInfo_list before collecting information
            for veh in self.vehicles:
                # veh_transmitInfo should be a list with element [id, lane, Acc, Vel, Pos, vl_id, vf_id)
                veh_transmitInfo = veh.transmitInfo()
                self.veh_transmitInfo_list.append(veh_transmitInfo)

            """2. Each CAV receives info, and updates its Acc based on manualDriverModel and IDM"""
            for veh in self.vehicles:
                veh.receiveInfo(self.veh_transmitInfo_list)
                veh.manualDriverModel()   # Acc updates for each CAV based on manualDriverModel
                veh.intelligent_driver_model()  # Acc updates for each CAV based on IDM

            """3. Each CAV updates its acc if it is in the merging area"""
            for veh in self.vehicles:
                ########################################################
                # Add bias to self.veh_transmitInfo_list to
                # implement the attacks during speed coordination!!!!!
                ########################################################
                veh.receiveInfo(self.veh_transmitInfo_list)
                veh.speed_coordination()   # merge CAV will updates its Acc Based on speed coordination
                veh.gap_alignment()        # merge CAV will change its vl_id and vf_id

            """4. Each CAV shares its info to others (especially updated vl_id and vf_id)"""
            self.veh_transmitInfo_list = []  # empty the self.veh_transmitInfo_list
            for veh in self.vehicles:
                # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
                veh_transmitInfo = veh.transmitInfo()
                self.veh_transmitInfo_list.append(veh_transmitInfo)

            print(
                f"Info list before virtual platooning, {self.veh_transmitInfo_list}")

            """5. Each CAV updates its acc based on virtual platooning"""
            for veh in self.vehicles:
                ########################################################
                # Add bias to self.veh_transmitInfo_list to
                # implement the attacks during virtual platonning!!!!!
                ########################################################
                veh.receiveInfo(self.veh_transmitInfo_list)
                # Acc update based on virtual platoon control
                veh.virtual_platoon_control(self.dt)
                # update states for current time step
                veh.updateStatus(self.dt)
                # store the update states to the dataframe for plotting
                self.Veh_Pos_plot.loc[t, veh.id] = veh.Pos
                self.Veh_Vel_plot.loc[t, veh.id] = veh.Vel
                self.Veh_Acc_plot.loc[t, veh.id] = veh.Acc

                # (Pos)                           CAV_ID1,    CAV_ID2,  ....  ,CAV_id -3,
                # step = 0                          -200        -300
                # step = 1                          -440
                # ...                               -500
                # step =  self.total_time/self.dt

        self.plot_results()

    def plot_results(self):
        print("A")
        # x-axis (timestep)
        # y-axis (Pos of all CAVS)


if __name__ == '__main__':

    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=28, init_Pos=-300),
        Vehicle(id=3, lane=0, init_Vel=27, init_Pos=-350),
        Vehicle(id=4, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500),
        Vehicle(id=-3, lane=1, init_Vel=30, init_Pos=-560)
    ]

    sim = Simulation(vehicles, 60, 0.1)
    if sim.check == 1:
        sim.mergeSimulator()
        print(f"Position Plot: {sim.Veh_Pos_plot}")
        print(f"Velocity Plot: {sim.Veh_Vel_plot}")
        print(f"Acc Plot: {sim.Veh_Acc_plot}")

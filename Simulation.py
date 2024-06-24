from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
import matplotlib.pyplot as plt
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

        self.total_time = total_time*10
        self.dt = time_interval*10
        self.Veh_Pos_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])  # initialize a dataframe for ploting. rows: # of time step, column: # of CAVs
        self.Veh_Vel_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])
        self.Veh_Acc_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])
        # 0 if there is something wrong in the initial settings, otherwise 1
        self.check = self.mergeInitialCheck()

        # for debugging purpose
        self.Veh_vl_id_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])
        self.Veh_vf_id_plot = pd.DataFrame(0, index=range(
            int(self.total_time / self.dt)), columns=[veh.id for veh in self.vehicles])

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

    # ##################################################
    # # Apply mutation attack function
    # ##################################################
    # def apply_mutation_attack(self, time_step):
    #     attackVictim = [1, 3]  # Example victims
    #     attackDuration = [[[10, 20]], [[15, 25]]]  # Example durations as lists of lists
    #     attackChannel = ['Pos', 'Vel']  # Example channels (Position, Velocity)
    #     freqType = ['Continuous', 'Cluster']  # Example frequency types
    #     freqValue = [[0], [2, 3]]  # Example frequency values
    #     biasType = ['Constant', 'Linear']  # Example bias types
    #     biasValue = [[5], [2, 3]]  # Example bias values

    #     time_steps = np.arange(0, self.total_time, self.dt / 10)
    #     bias_df = mutationAttackBias(time_steps, attackVictim, attackDuration, attackChannel, freqType, freqValue, biasType, biasValue)

    #     for veh in self.vehicles:
    #         if veh.id in attackVictim and time_step in bias_df.index:
    #             bias = bias_df.at[time_step, veh.id]
    #             veh.Vel += bias  # Apply bias to velocity or any other attribute
    #             veh.Acc += bias  # Apply bias to acceleration or any other attribute

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

            # print(
            #     f"Info list before virtual platooning at time step {t}, {self.veh_transmitInfo_list}")

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
                # # Mutation attack (make sure this makes sense)
                # self.apply_mutation_attack(t)
                # store the update states to the dataframe for plotting
                self.Veh_Pos_plot.loc[t, veh.id] = veh.Pos
                self.Veh_Vel_plot.loc[t, veh.id] = veh.Vel
                self.Veh_Acc_plot.loc[t, veh.id] = veh.Acc
                self.Veh_vl_id_plot.loc[t, veh.id] = veh.vl_id
                self.Veh_vf_id_plot.loc[t, veh.id] = veh.vf_id

                # (Pos)                           CAV_ID1,    CAV_ID2,  ....  ,CAV_id -3,
                # step = 0                          -200        -300
                # step = 1                          -440
                # ...                               -500
                # step =  self.total_time/self.dt

        self.plot_results()

    def plot_results(self):
        time = np.arange(0, self.total_time, self.dt)

        # Plot Position
        fig1, ax1 = plt.subplots()
        for veh in self.vehicles:
            line_style = '--' if veh.lane == 1 else '-'
            ax1.plot(time, self.Veh_Pos_plot[veh.id],
                     label=f'Vehicle {veh.id}', linestyle=line_style)
        ax1.set_ylabel('Position (m)')
        ax1.set_title('Vehicle Positions Over Time')
        ax1.legend(loc='upper left')
        ax1.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.show()

        # Plot Velocity
        fig2, ax2 = plt.subplots()
        for veh in self.vehicles:
            line_style = '--' if veh.lane == 1 else '-'
            ax2.plot(time, self.Veh_Vel_plot[veh.id],
                     label=f'Vehicle {veh.id}', linestyle=line_style)
        ax2.set_ylabel('Velocity (m/s)')
        ax2.set_title('Vehicle Velocities Over Time')
        ax2.legend(loc='upper left')
        ax2.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.show()

        # Plot Acceleration
        fig3, ax3 = plt.subplots()
        for veh in self.vehicles:
            line_style = '--' if veh.lane == 1 else '-'
            ax3.plot(time, self.Veh_Acc_plot[veh.id],
                     label=f'Vehicle {veh.id}', linestyle=line_style)
        ax3.set_ylabel('Acceleration (m/s²)')
        ax3.set_title('Vehicle Accelerations Over Time')
        ax3.legend(loc='upper left')
        ax3.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.show()

        # Plot VL ID
        fig4, ax4 = plt.subplots()
        for veh in self.vehicles:
            line_style = '--' if veh.lane == 1 else '-'
            ax4.plot(time, self.Veh_vl_id_plot[veh.id],
                     label=f'Vehicle {veh.id}', linestyle=line_style)
        ax4.set_ylabel('Virtual Leader ID')
        ax4.set_title('Vehicle Virtual Leader IDs Over Time')
        ax4.legend(loc='upper left')
        ax4.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.show()

        # Plot VF ID
        fig5, ax5 = plt.subplots()
        for veh in self.vehicles:
            line_style = '--' if veh.lane == 1 else '-'
            ax5.plot(time, self.Veh_vf_id_plot[veh.id],
                     label=f'Vehicle {veh.id}', linestyle=line_style)
        ax5.set_ylabel('Virtual Follower ID')
        ax5.set_title('Vehicle Virtual Follower IDs Over Time')
        ax5.legend(loc='upper left')
        ax5.set_xlabel('Time (s)')
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':

    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
        Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
    ]

    sim = Simulation(vehicles, 1, 0.1)
    if sim.check == 1:
        sim.mergeSimulator()
        # print(f"Position Plot: {sim.Veh_Pos_plot}")
        # print(f"Velocity Plot: {sim.Veh_Vel_plot}")
        # print(f"Acc Plot: {sim.Veh_Acc_plot}")
        # print(f"vl_id Plot: {sim.Veh_vl_id_plot}")

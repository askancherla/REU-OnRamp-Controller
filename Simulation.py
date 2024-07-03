from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
from AttackGeneratorModule import CyberAttacker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Simulation:
    def __init__(self, vehicles, total_time, time_interval):
        self.vehicles = vehicles    # get all vehicles' initial status
        # initialize to store the transmitInfo from all CAVs
        self.min_gap = 2          # meter, same as the one in Vehicle Class
        self.safe_time_headway = 1.1   # second, same as the one in Vehicle Class
        self.minVel = 5    # m/s
        self.maxVel = 30   # m/s= 108km/h ~= 67 mph
        self.minAcc = -4   # m/s^2
        self.maxAcc = 2    # m/s^2
        self.allVeh_list = []  # store all CAV objects sorted by position smallest to largest
        # store all mainlane CAV objects sorted based on position from largest to smallest
        self.mainVeh_list = []
        # store all merge CAV objects sort from largest to smallest position
        self.mergeVeh_list = []
        # store the info from all CAVs broadcast, e.g. [[id1, lane1, Acc1, Vel1, Pos1, vl_id1, vf_id1], ... , [idn, lanen, Accn, Veln, Posn, vl_idn, vf_idn]]
        self.veh_transmitInfo_list = []
        self.total_time = total_time
        self.dt = time_interval

        # for plotting (possibly because of precision and floating-point arithmetic in Python), we have to make sure the variables in the index are integers to make it work
        self.total_time_plot = self.total_time * 10
        self.dt_plot = self.dt*10

        self.Veh_Pos_plot = pd.DataFrame(0, index=range(
            int(self.total_time_plot / self.dt_plot)), columns=[veh.id for veh in self.vehicles])  # initialize a dataframe for ploting. rows: # of time step, column: # of CAVs
        self.Veh_Vel_plot = pd.DataFrame(0, index=range(
            int(self.total_time_plot / self.dt_plot)), columns=[veh.id for veh in self.vehicles])
        self.Veh_Acc_plot = pd.DataFrame(0, index=range(
            int(self.total_time_plot / self.dt_plot)), columns=[veh.id for veh in self.vehicles])
        self.Veh_vl_id_plot = pd.DataFrame(0, index=range(
            int(self.total_time_plot / self.dt_plot)), columns=[veh.id for veh in self.vehicles])
        self.Veh_vf_id_plot = pd.DataFrame(0, index=range(
            int(self.total_time_plot / self.dt_plot)), columns=[veh.id for veh in self.vehicles])

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

    def mergeSimulator(self, Pos_FIV_bias_df_list_speedCoop, Vel_FIV_bias_df_list_speedCoop, Pos_FIV_bias_df_list_VP, Vel_FIV_bias_df_list_VP):

        # 't' shows the index of the control time step
        for t in np.arange(0, int(self.total_time_plot / self.dt_plot), 1):
            """1. Each CAV shares its info to others"""
            self.veh_transmitInfo_list = [
            ]   # empty the self.veh_transmitInfo_list before collecting information
            for veh in self.vehicles:
                # veh_transmitInfo should be a list with element [id, lane, Acc, Vel, Pos, vl_id, vf_id)
                veh_transmitInfo = veh.transmitInfo()
                self.veh_transmitInfo_list.append(veh_transmitInfo)

            """2. Sort the three lists of vehicles"""
            self.mainVeh_list = []
            self.mergeVeh_list = []
            self.allVeh_list = []
            for veh in self.vehicles:
                self.allVeh_list.append(veh)
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
            self.allVeh_list.sort(key=lambda x: x.Pos, reverse=True)

            """3. Each CAV receives info, and updates its Acc based on manualDriverModel or IDM"""
            for veh in self.allVeh_list:
                veh.receiveInfo(self.veh_transmitInfo_list)
                veh.manualDriverModel()   # Acc updates for each CAV based on manualDriverModel
                veh.intelligent_driver_model()  # Acc updates for each CAV based on IDM

            """4. Each CAV updates its acc if it is in the merging area"""

            ######################################################################
            # Make a copy of self.veh_transmitInfo_list for each CAV (vehInfoV2V)
            # If the CAV is victim, bias will be added to vehInfoV2V
            # Add bias to self.veh_transmitInfo_list to
            # implement the attacks during speed coordination!!!!!
            ######################################################################
            for veh in self.allVeh_list:
                # make a copy of self.veh_transmitInfo_list, do not mutate self.veh_transmitInfo_list
                vehInfoV2V = self.veh_transmitInfo_list
                # print(
                #     f"Original vehInfoV2V: {vehInfoV2V} at time step {t}")
                for i in range(len(Pos_FIV_bias_df_list_speedCoop)):
                    if veh.id == Pos_FIV_bias_df_list_speedCoop[i][0]:
                        for j, col in enumerate(Pos_FIV_bias_df_list_speedCoop[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[4] += Pos_FIV_bias_df_list_speedCoop[i][1].loc[t, col]

                for i in range(len(Vel_FIV_bias_df_list_speedCoop)):
                    if veh.id == Vel_FIV_bias_df_list_speedCoop[i][0]:
                        for j, col in enumerate(Vel_FIV_bias_df_list_speedCoop[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[3] += Vel_FIV_bias_df_list_speedCoop[i][1].loc[t, col]

                # print(
                #     f"Mutated vehInfoV2V: {vehInfoV2V} at time step {t}")

                veh.receiveInfo(vehInfoV2V)
                veh.speed_coordination()   # merge CAV will updates its Acc Based on speed coordination
                veh.gap_alignment()        # merge CAV will change its vl_id and vf_id

            """5. Each CAV shares its info to others (especially updated vl_id and vf_id)"""
            self.veh_transmitInfo_list = []  # empty the self.veh_transmitInfo_list
            for veh in self.allVeh_list:
                # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
                veh_transmitInfo = veh.transmitInfo()
                self.veh_transmitInfo_list.append(veh_transmitInfo)

            # print(
            #     f"Info list before virtual platooning at time step {t}, {self.veh_transmitInfo_list}")

            """6. Each CAV updates its acc based on virtual platooning"""
            ########################################################
            # Add bias to self.veh_transmitInfo_list to
            # implement the attacks during virtual platonning!!!!!
            ########################################################
            for veh in self.mainVeh_list:
                # make a copy of self.veh_transmitInfo_list, do not mutate self.veh_transmitInfo_list
                vehInfoV2V = self.veh_transmitInfo_list
                # print(
                #     f"Original vehInfoV2V: {vehInfoV2V} at time step {t}")
                for i in range(len(Pos_FIV_bias_df_list_VP)):
                    if veh.id == Pos_FIV_bias_df_list_VP[i][0]:
                        for j, col in enumerate(Pos_FIV_bias_df_list_VP[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[4] += Pos_FIV_bias_df_list_VP[i][1].loc[t, col]

                for i in range(len(Vel_FIV_bias_df_list_VP)):
                    if veh.id == Vel_FIV_bias_df_list_VP[i][0]:
                        for j, col in enumerate(Vel_FIV_bias_df_list_VP[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[3] += Vel_FIV_bias_df_list_VP[i][1].loc[t, col]
                veh.receiveInfo(vehInfoV2V)
                # Acc update based on virtual platoon control
                veh.virtual_platoon_control(self.dt)

            # manually set the implementation with the reverse order
            for veh in reversed(self.mergeVeh_list):
                # make a copy of self.veh_transmitInfo_list, do not mutate self.veh_transmitInfo_list
                vehInfoV2V = self.veh_transmitInfo_list
                # print(
                #     f"Original vehInfoV2V: {vehInfoV2V} at time step {t}")
                for i in range(len(Pos_FIV_bias_df_list_VP)):
                    if veh.id == Pos_FIV_bias_df_list_VP[i][0]:
                        for j, col in enumerate(Pos_FIV_bias_df_list_VP[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[4] += Pos_FIV_bias_df_list_VP[i][1].loc[t, col]

                for i in range(len(Vel_FIV_bias_df_list_VP)):
                    if veh.id == Vel_FIV_bias_df_list_VP[i][0]:
                        for j, col in enumerate(Vel_FIV_bias_df_list_VP[i][1].columns):
                            for sublist in vehInfoV2V:
                                if sublist[0] == col:
                                    sublist[3] += Vel_FIV_bias_df_list_VP[i][1].loc[t, col]

                veh.receiveInfo(vehInfoV2V)
                # Acc update based on virtual platoon control
                veh.virtual_platoon_control(self.dt)

            for veh in self.allVeh_list:
                # update states for current time step
                veh.updateStatus(self.dt)
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

        # self.plot_results_integrate()
        self.plot_results_separate()

    # def plot_results_integrate(self):
    #     fig, axs = plt.subplots(4, 1, sharex=True)  # figsize=(14, 18)
    #     time = np.arange(0, int(self.total_time_plot / self.dt_plot), 1)

    #     # Plot Position
    #     for veh in self.vehicles:
    #         line_style = '--' if veh.lane == 1 else '-'
    #         axs[0].plot(time, self.Veh_Pos_plot[veh.id],
    #                     label=f'Vehicle {veh.id}', linestyle=line_style)
    #     axs[0].set_ylabel('Position (m)')
    #     axs[0].set_title('Vehicle Positions Over Time')
    #     axs[0].legend(loc='upper left')
    #     # Add rectangular zone
    #     axs[0].axhspan(-200, 0, color='grey', alpha=0.3,
    #                    label='Acceleration Zone')
    #     # Add text label
    #     axs[0].text(100, -100, 'Acceleration Zone', fontsize=12, color='black',
    #                 horizontalalignment='center', verticalalignment='center')

    #     # Plot Velocity
    #     for veh in self.vehicles:
    #         line_style = '--' if veh.lane == 1 else '-'
    #         axs[1].plot(time, self.Veh_Vel_plot[veh.id],
    #                     label=f'Vehicle {veh.id}', linestyle=line_style)
    #     axs[1].set_ylabel('Velocity (m/s)')
    #     axs[1].set_title('Vehicle Velocities Over Time')
    #     axs[1].legend(loc='upper left')

    #     # Plot Acceleration
    #     for veh in self.vehicles:
    #         line_style = '--' if veh.lane == 1 else '-'
    #         axs[2].plot(time, self.Veh_Acc_plot[veh.id],
    #                     label=f'Vehicle {veh.id}', linestyle=line_style)
    #     axs[2].set_ylabel('Acceleration (m/s²)')
    #     axs[2].set_title('Vehicle Accelerations Over Time')
    #     axs[2].legend(loc='upper left')

    #     # Plot VL ID
    #     for veh in self.vehicles:
    #         line_style = '--' if veh.lane == 1 else '-'
    #         axs[3].plot(time, self.Veh_vl_id_plot[veh.id],
    #                     label=f'Vehicle {veh.id}', linestyle=line_style)
    #     axs[3].set_ylabel('Virtual Leader ID')
    #     axs[3].set_title('Vehicle Virtual Leader IDs Over Time')
    #     axs[3].legend(loc='upper left')
    #     # plt.tight_layout()
    #     plt.show()

    def plot_results_separate(self):
        time = np.arange(0, int(self.total_time_plot / self.dt_plot), 1)

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
        # Add rectangular zone
        ax1.axhspan(-200, 0, color='grey', alpha=0.3,
                    label='Acceleration Zone')

        # Add text label
        ax1.text(100, -100, 'Acceleration Zone', fontsize=12, color='black',
                 horizontalalignment='center', verticalalignment='center')
        plt.tight_layout()
        plt.show()

        # ## Plot Velocity
        # fig2, ax2 = plt.subplots()
        # for veh in self.vehicles:
        #     line_style = '--' if veh.lane == 1 else '-'
        #     ax2.plot(time, self.Veh_Vel_plot[veh.id],
        #              label=f'Vehicle {veh.id}', linestyle=line_style)
        # ax2.set_ylabel('Velocity (m/s)')
        # ax2.set_title('Vehicle Velocities Over Time')
        # ax2.legend(loc='upper left')
        # ax2.set_xlabel('Time (s)')
        # plt.tight_layout()
        # plt.show()

        # # Plot Acceleration
        # fig3, ax3 = plt.subplots()
        # for veh in self.vehicles:
        #     line_style = '--' if veh.lane == 1 else '-'
        #     ax3.plot(time, self.Veh_Acc_plot[veh.id],
        #              label=f'Vehicle {veh.id}', linestyle=line_style)
        # ax3.set_ylabel('Acceleration (m/s²)')
        # ax3.set_title('Vehicle Accelerations Over Time')
        # ax3.legend(loc='upper left')
        # ax3.set_xlabel('Time (s)')
        # plt.tight_layout()
        # plt.show()

        # # Plot VL ID
        # fig4, ax4 = plt.subplots()
        # for veh in self.vehicles:
        #     line_style = '--' if veh.lane == 1 else '-'
        #     ax4.plot(time, self.Veh_vl_id_plot[veh.id],
        #              label=f'Vehicle {veh.id}', linestyle=line_style)
        # ax4.set_ylabel('Virtual Leader ID')
        # ax4.set_title('Vehicle Virtual Leader IDs Over Time')
        # ax4.legend(loc='upper left')
        # ax4.set_xlabel('Time (s)')
        # plt.tight_layout()
        # plt.show()

        # # Plot VF ID
        # fig5, ax5 = plt.subplots()
        # for veh in self.vehicles:
        #     line_style = '--' if veh.lane == 1 else '-'
        #     ax5.plot(time, self.Veh_vf_id_plot[veh.id],
        #              label=f'Vehicle {veh.id}', linestyle=line_style)
        # ax5.set_ylabel('Virtual Follower ID')
        # ax5.set_title('Vehicle Virtual Follower IDs Over Time')
        # ax5.legend(loc='upper left')
        # ax5.set_xlabel('Time (s)')
        # plt.tight_layout()
        # plt.show()


if __name__ == '__main__':

    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-370),
        Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-380),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-430)
    ]

    simEndtime = 20
    simTimestep = 0.1

    sim = Simulation(vehicles, simEndtime, simTimestep)
    if sim.check == 1:

        # if we don't want to implement attacks
        Pos_FIV_df_list_empty = [[0, pd.DataFrame(0, index=range(int(simEndtime / simTimestep)), columns=[
            veh.id for veh in vehicles])]]
        Vel_FIV_df_list_empty = [[0, pd.DataFrame(0, index=range(int(simEndtime / simTimestep)), columns=[
            veh.id for veh in vehicles])]]
        # if we don't want to implement attacks, uncomment this part and comments the next part of attacks

        # if we want to implement attacks
        attacker = CyberAttacker(vehicles)
        attackCase = [
            [-1],   # attackedVictim
            [[2]],  # maliChannelSource
            [[[[10, 50]]]],  # attackDuration:
            [[[['Pos']]]],  # attackChannel:
            [[[['Continuous']]]],  # freqType:
            [[[[[0]]]]],  # freqParaValue:
            [[[['Constant']]]],  # biasType:
            [[[[[-50]]]]]   # biasParaValue:
        ]
        Pos_FIV_df_list, Vel_FIV_df_list = attacker.mutAttackFalsifyInfoVectorGen(
            attackCase, 0, simEndtime, simTimestep)
        # if we want to implement attacks, uncomment this part and comments the above part of no attack

        def plot_results(FIV_df_list):
            for i in range(len(FIV_df_list)):      # go through each victim
                for column in FIV_df_list[i][1].columns:
                    plt.plot(FIV_df_list[i][1].index,
                             FIV_df_list[i][1][column], label=column)

            # Adding labels and title
            plt.xlabel('Control Time Step')
            plt.ylabel('Bias Value')
            plt.title(
                f'Bias Value of Vel Channel on Victim {FIV_df_list[i][0]}')

            # Adding a legend
            plt.legend()

            # Display the plot
            plt.show()

        plot_results(Pos_FIV_df_list)

        sim.mergeSimulator(Pos_FIV_bias_df_list_speedCoop=Pos_FIV_df_list_empty,
                           Vel_FIV_bias_df_list_speedCoop=Vel_FIV_df_list_empty,
                           Pos_FIV_bias_df_list_VP=Pos_FIV_df_list,
                           Vel_FIV_bias_df_list_VP=Vel_FIV_df_list)
        # print(f"Position Plot: {sim.Veh_Pos_plot}")
        # print(f"Velocity Plot: {sim.Veh_Vel_plot}")
        # print(f"Acc Plot: {sim.Veh_Acc_plot}")
        # print(f"vl_id Plot: {sim.Veh_vl_id_plot}")

import numpy as np


class Vehicle():

    def __init__(self, id, lane, init_Vel, init_Pos):
        self.id = id          # positive for mainlane CAVs, negative for mergelane CAVs
        self.lane = lane      # 0 mainline and 1 merge lane
        self.Vel = init_Vel   # will record the speed of the self object at each time step
        self.Pos = init_Pos   # will record the position of the self object at each time step
        self.Acc = 0   # Assume all vehicles are running at a constant speed initially
        self.vl_id = 0    # ID of its virtual leader, 0 if it does not have
        self.vf_id = 0    # ID of its virtual follower, 0 if it does not have
        # store the Vel of the previous iteration for the function "virtual_platoon_control()"
        self.prev_Vel = 0
        # each CAV needs to receive other CAVs info through perception channel, which is implemented through a list of tuples
        self.vehiclesInfo = []
        self.mainVeh_list = []   # store the info of other mainlane CAVs if self is on mainlane
        self.mergeVeh_list = []  # store the info of other mergelane CAVs if self is on mergelane

        # Constant Vehicle properties
        self.length = 4.5  # meters, length of the vehicle
        self.maxAcc = 2                # m/(s^2)
        self.minAcc = -4                # m/(s^2)
        self.minVel = 5    # m/s
        self.maxVel = 30   # m/s= 108km/h ~= 67 mph
        self.comfortable_Acc = 1       # m/(s^2)
        self.safe_time_headway = 1.1   # second
        self.min_gap = 2               # meters
        self.desired_ffVel = 35          # m/s, desired speed in free-flow traffic conditions

    ###########################################################################################
    # Assume each CAV could get all CAVs' state initially for implementation (include itself),
    # Will filter the accessible channels based on info topo in future
    ###########################################################################################

    def receiveInfo(self, vehinfoV2X):
        # "vehinfoV2X" should be a list of sublists, each sublist is from a CAV, which contains
        #  [id, lane, Acc, Vel, Pos, vl_id, vf_id]
        # the Simulator will provide "vehinfoV2X". It could be benign or mutated
        self.vehiclesInfo = vehinfoV2X
        # filter out all CAVs based on their lane, and sorted based on Pos (from large to small value)
        self.mainVeh_list = []   # initialize to empty every time receive the info
        self.mergeVeh_list = []  # initialize to empty every time receive the info

        for i in range(len(self.vehiclesInfo)):
            if self.vehiclesInfo[i][1] == 0:     # CAV.lane == 0
                self.mainVeh_list.append(self.vehiclesInfo[i])
            else:                                # CAV.lane == 1
                self.mergeVeh_list.append(self.vehiclesInfo[i])

        # sort each list based on their positions (large to small)
        # based on the order of sublist, x[4] should be Pos
        self.mainVeh_list.sort(key=lambda x: x[4], reverse=True)
        self.mergeVeh_list.sort(key=lambda x: x[4], reverse=True)

    def transmitInfo(self):
        # transmit the info of the self vehicle as a list
        return [self.id, self.lane, self.Acc, self.Vel, self.Pos, self.vl_id, self.vf_id]

    #########################################################################################################
    # Acc of each vehicle if it does not have a vehicle to follow.
    # Based on the paper
    # [An Enhanced Microscopic Traffic Simulation Model for Application to Connected Automated Vehicles]
    #########################################################################################################

    def manualDriverModel(self):
        alpha = 3  # sensitivity exponent

        self.Acc = max(min(
            self.maxAcc*(1-((self.Vel)/(self.desired_ffVel))**alpha), self.maxAcc), self.minAcc)
        # print(f"CAV{self.id}'s vel is {self.Vel} from MDM")
        # print(f"CAV{self.id}'s acc is {self.Acc} from MDM")

    #####################################################################################
    # Acc of each vehicle if it has a vehicle to follow.
    # Based on the paper
    # [Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data]
    #####################################################################################

    # the self vehicle should find its physical preceding vehicle based on "vehiclesInfo"
    def intelligent_driver_model(self):
        # IDM parameters
        # minimum steady-state time gap (from paper)
        T = self.safe_time_headway
        a = self.maxAcc              #
        b = 2                        # desired deceleration  (from paper)
        delta = 4                    # Free acceleration exponent(from paper)
        # vehicle-vehicle clearance in stand-still situations (from paper)
        s0 = 0
        v0 = self.desired_ffVel      # desired speed in free-flow traffic conditions

        if self.lane == 0:
            index_mainVeh = -1  # Initialize to an invalid index
            # (id, lane, Acc, Vel, Pos, vl_id, vf_id)
            for index, mainVeh in enumerate(self.mainVeh_list):
                if mainVeh[0] == self.id:
                    index_mainVeh = index    # return the index of self vehicle in the mainVeh_list

            if index_mainVeh != 0:    # since the self.mainVeh_list is sorted already, if self is not the 1st element in the list, it should have a physical preceding CAV
                delta_v = self.Vel - self.mainVeh_list[index_mainVeh-1][3]
                s_star = s0 + max(0, self.Vel * T +
                                  (self.Vel * delta_v) / (2 * np.sqrt(a * b)))
                s = self.mainVeh_list[index_mainVeh -
                                      1][4] - self.length - self.Pos
                self.Acc = max(min(a * (1 - (self.Vel / v0) ** delta -
                               (s_star / s)), self.maxAcc), self.minAcc)

                # print(f"CAV{self.id}'s vel is {self.Vel} from IDM")
                # print(f"CAV{self.id}'s acc is {self.Acc} from IDM")

        else:
            index_mergeVeh = -1  # Initialize to an invalid index
            # (id, lane, Acc, Vel, Pos, vl_id, vf_id)
            for index, mergeVeh in enumerate(self.mergeVeh_list):
                if mergeVeh[0] == self.id:
                    index_mergeVeh = index    # return the index of self vehicle in the mergeVeh_list

            if index_mergeVeh != 0:
                delta_v = self.Vel - self.mergeVeh_list[index_mergeVeh-1][3]
                s_star = s0 + max(0, self.Vel * T +
                                  (self.Vel * delta_v) / (2 * np.sqrt(a * b)))
                s = self.mergeVeh_list[index_mergeVeh -
                                       1][4] - self.length - self.Pos
                self.Acc = max(min(a * (1 - (self.Vel / v0) **
                                        delta - (s_star / s)), self.maxAcc), self.minAcc)

                # print(f"CAV{self.id}'s vel is {self.Vel} from IDM")
                # print(f"CAV{self.id}'s acc is {self.Acc} from IDM")

    ###########################################################
    # Acc of each vehicle if it is in the merging section.
    # Based on the paper
    # [Coordinated Merge Control Based on V2V Communication]
    ###########################################################

    # Speed coordination (Equation 2)

    # assume the simulation will give us all vehicle objects
    # This function should be run only on the ramp vehicles!!!

    def speed_coordination(self):      # should get veh_transmitInfo_list
        k = 0.1  # control design gain for Eq2. Cannot find the value in paper.
        main_vel_list = []  # initialize a list to store the velocity of all mainlane vehicles

        if self.lane == 1:  # only mergelane CAV should do speed coordination
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for i in range(len(self.mainVeh_list)):
                main_vel_list.append(self.mainVeh_list[i][3])

            # calculate the average speed based on subsection "2) Speed coordination" in the paper
            v_ref = sum(main_vel_list)/len(main_vel_list)
            self.Acc = max(min(k * (v_ref - self.Vel),
                           self.maxAcc), self.minAcc)
            # print(f"CAV{self.id}'s vel is {self.Vel} from speed coordination")
            # print(f"CAV{self.id}'s acc is {self.Acc} from speed coordination")

    # Gap alignment (finding VL and VF)
    # This function should be run only on the ramp vehicles!!!

    def gap_alignment(self):
        # initialize a list to store the position of all mainlane vehicles with their corresponding id as a tuple
        main_pos_id_list = []

        if self.lane == 1:  # only mergelane CAV should do gap alignment
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for i in range(len(self.mainVeh_list)):
                main_pos_id_list.append(
                    (self.mainVeh_list[i][4], self.mainVeh_list[i][0]))  # (pos, id)

            print(f"main_pos_id_list: {main_pos_id_list}")

            # main_pos_id_list should be sorted based on the position (large to small)
            # if the self vehicle is behind the last mainlane vehicle
            if self.Pos <= main_pos_id_list[len(main_pos_id_list)-1][0]:
                self.vl_id = main_pos_id_list[len(main_pos_id_list)-1][1]
                self.vf_id = 0
                print(f"CAV ID: {self.id}, VL: {self.vl_id}")
            # if the self vehicle is ahead of the first mainlane vehicle
            elif self.Pos > main_pos_id_list[0][0]:
                self.vf_id = main_pos_id_list[0][1]
                self.vl_id = 0
            else:
                for i in range(len(main_pos_id_list)-1):
                    if ((main_pos_id_list[i][0] >= self.Pos) and (self.Pos > main_pos_id_list[i+1][0])):
                        self.vl_id = main_pos_id_list[i][1]
                        self.vf_id = main_pos_id_list[i+1][1]
                        break

                else:
                    print(
                        f"Cannot find the VL or VF for merge CAV {self.id} at {self.Pos} compared with {main_pos_id_list[len(main_pos_id_list)-1][0]} and {main_pos_id_list[0][0]}")

    # Virtual platoon control (Equation 4)
    # all CAV should share its info about VL and VF before running this function
    # it should get "self.vehiclesInfo" of all other vehicles [id, lane, Acc, Vel, Pos, vl_id, vf_id]
    # only the merge vehicles update their vl_id and vf_id for now
    # for self vehicle, only knows its vl is enough

    def virtual_platoon_control(self, dt):

        if self.lane == 1:
            # if the self merge CAV has its physical preceding CAV, and its vl_id is same as the preceding
            # its vl should be its physical preceding CAV
            # otherwise it should keep its vl_id
            for i in reversed(range(len(self.mergeVeh_list))):
                if ((self.id == self.mergeVeh_list[i][0]) and (i != 0)):
                    if self.vl_id == self.mergeVeh_list[i-1][5]:
                        self.vl_id = self.mergeVeh_list[i-1][0]

        else:
            # if self is in mainlane, if will read the vf_id of all merge CAVs,
            # if one/multi merge CAV's vf_id matches, self will follow the last one
            # otherwise self.Acc will keep from the manualmodel or IDM
            for i in self.mergeVeh_list:
                if i[6] == self.id:
                    self.vl_id = i[0]
                else:
                    self.vl_id = self.id - 1   # mainlane vehicle should follow its physical preceding

        # refer the paper [Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data]
        kp = 0.45
        kd = 0.25   # refer the paper [Modeling ...]
        hd = 1.3    # [Coordinated Merge Control Based on V2V Communication]

        if self.vl_id != 0:
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for index, Veh in enumerate(self.vehiclesInfo):
                if self.vl_id == Veh[0]:
                    self.vp_Vel = self.Vel + kp*(self.Pos - self.vehiclesInfo[index][4]-hd*self.Vel) + kd*(
                        self.Vel-self.vehiclesInfo[index][3]-hd*self.Acc)
                    self.Acc = max(min((self.vp_Vel-self.Vel)/dt,
                                       self.maxAcc), self.minAcc)
                    # print(
                    #     f"CAV{self.id}'s vel is {self.Vel} from virtual platoon control")
                    # print(
                    #     f"CAV{self.id}'s acc is {self.Acc} from virtual platoon control")

    # Function to update position and speed

    def updateStatus(self, dt):
        self.prev_Vel = self.Vel
        self.Vel += self.Acc * dt
        self.Pos += self.prev_Vel * dt + self.Acc * ((dt ** 2)/2)


if __name__ == '__main__':

    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=28, init_Pos=-270),
        Vehicle(id=3, lane=0, init_Vel=27, init_Pos=-330),
        Vehicle(id=4, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500),
        Vehicle(id=-3, lane=1, init_Vel=30, init_Pos=-550)
    ]

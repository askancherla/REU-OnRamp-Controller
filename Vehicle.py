import numpy as np


class Vehicle():

    def __init__(self, id, lane, init_Vel, init_Pos):
        self.id = id          # positive for mainlane CAVs, negative for mergelane CAVs
        self.lane = lane      # 0 for mainlane and 1 for mergelane
        self.Vel = init_Vel   # will record the speed of the self object at each time step
        self.Pos = init_Pos   # will record the position of the self object at each time step
        self.Acc = 0   # Assume all vehicles are running at a constant speed initially
        self.vl_id = 0    # ID of its virtual leader, 0 if it does not have one
        self.vf_id = 0    # ID of its virtual follower, 0 if it does not have one
        # store the Vel of the previous control step for the function "updateStatus()"
        self.prev_Vel = 0
        # each CAV needs to receive other CAVs' info through perception channels, which is stored through a list of sublists
        # e.g. [[id1, lane1, Acc1, Vel1, Pos1, vl_id1, vf_id1], ... , [idn, lanen, Accn, Veln, Posn, vl_idn, vf_idn]]
        self.vehiclesInfo = []
        # split and store the info of all mainlane CAVs from self.vehiclesInfo
        self.mainVehInfo_list = []
        # split and store the info of all mergelane CAVs from self.vehiclesInfo
        self.mergeVehInfo_list = []

        # Constant Vehicle properties
        self.length = 4.5  # meters, length of the vehicle
        self.maxAcc = 2                # m/(s^2)
        self.minAcc = -4               # m/(s^2)
        self.minVel = 5    # m/s
        self.maxVel = 30   # m/s= 108km/h ~= 67 mph
        self.comfortable_Acc = 1       # m/(s^2)
        self.safe_time_headway = 1.1   # second
        self.min_gap = 2               # meters
        self.desired_ffVel = 35        # m/s, desired speed in free-flow traffic conditions

    ###########################################################################################
    # Assume each CAV could get all CAVs' state initially for implementation (include itself),
    # Will filter the accessible channels based on info topo in future
    ###########################################################################################

    def receiveInfo(self, vehinfoV2X):
        # "vehinfoV2X" should be a list of sublists, each sublist is from a CAV, which contains
        #  [id, lane, Acc, Vel, Pos, vl_id, vf_id]
        # the Simulator will provide "vehinfoV2X". It could be benign or mutated
        self.vehiclesInfo = vehinfoV2X
        # filter out all CAVs based on their lane, and sorted based on their Pos (from large to small value)
        self.mainVehInfo_list = []   # initialize to empty every time receive the info
        self.mergeVehInfo_list = []  # initialize to empty every time receive the info

        for i in range(len(self.vehiclesInfo)):
            if self.vehiclesInfo[i][1] == 0:     # CAV.lane == 0
                self.mainVehInfo_list.append(self.vehiclesInfo[i])
            else:                                # CAV.lane == 1
                self.mergeVehInfo_list.append(self.vehiclesInfo[i])

        # sort each list based on their positions (large to small)
        # based on the order of sublist, x[4] should be Pos
        self.mainVehInfo_list.sort(key=lambda x: x[4], reverse=True)
        self.mergeVehInfo_list.sort(key=lambda x: x[4], reverse=True)

    def transmitInfo(self):
        # broadcast the info of the self vehicle as a list
        return [self.id, self.lane, self.Acc, self.Vel, self.Pos, self.vl_id, self.vf_id]

    #########################################################################################################
    # Acc of each vehicle if it does not have a vehicle to follow.
    # Based on the paper
    # [An Enhanced Microscopic Traffic Simulation Model for Application to Connected Automated Vehicles]
    #########################################################################################################

    def manualDriverModel(self):
        alpha = 3  # sensitivity exponent

        self.Acc = self.maxAcc*(1-((self.Vel)/(self.desired_ffVel))**alpha)
        # make sure Acc is inside the rage of min and max
        self.Acc = max(min(self.Acc, self.maxAcc), self.minAcc)
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
        s0 = 0                       # from paper
        v0 = self.desired_ffVel      # desired speed in free-flow traffic conditions

        if self.lane == 0:
            index_mainVeh = -1  # Initialize to an invalid index
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for index, mainVeh in enumerate(self.mainVehInfo_list):
                if mainVeh[0] == self.id:
                    index_mainVeh = index    # return the index of self vehicle in the mainVehInfo_list

            if index_mainVeh != 0:    # since the self.mainVehInfo_list is sorted already, if self is not the 1st element in the list, it should have a physical preceding CAV
                delta_v = self.Vel - self.mainVehInfo_list[index_mainVeh-1][3]
                s_star = s0 + max(0, self.Vel * T +
                                  (self.Vel * delta_v) / (2 * np.sqrt(a * b)))
                s = self.mainVehInfo_list[index_mainVeh -
                                          1][4] - self.length - self.Pos
                self.Acc = a * (1 - (self.Vel / v0) ** delta - (s_star / s))
                self.Acc = max(min(self.Acc, self.maxAcc), self.minAcc)

                # print(f"CAV{self.id}'s vel is {self.Vel} from IDM")
                # print(f"CAV{self.id}'s acc is {self.Acc} from IDM")

        else:
            index_mergeVeh = -1  # Initialize to an invalid index
            # (id, lane, Acc, Vel, Pos, vl_id, vf_id)
            for index, mergeVeh in enumerate(self.mergeVehInfo_list):
                if mergeVeh[0] == self.id:
                    index_mergeVeh = index    # return the index of self vehicle in the mergeVehInfo_list

            if index_mergeVeh != 0:
                delta_v = self.Vel - \
                    self.mergeVehInfo_list[index_mergeVeh-1][3]
                s_star = s0 + max(0, self.Vel * T +
                                  (self.Vel * delta_v) / (2 * np.sqrt(a * b)))
                s = self.mergeVehInfo_list[index_mergeVeh -
                                           1][4] - self.length - self.Pos
                self.Acc = a * (1 - (self.Vel / v0) ** delta - (s_star / s))
                self.Acc = max(min(self.Acc, self.maxAcc), self.minAcc)

                # print(f"CAV{self.id}'s vel is {self.Vel} from IDM")
                # print(f"CAV{self.id}'s acc is {self.Acc} from IDM")

    ###########################################################
    # Acc of each vehicle if it is in the merging section.
    # Based on the paper
    # [Coordinated Merge Control Based on V2V Communication]
    ###########################################################

    ###################################
    # Speed coordination (Equation 2)
    ###################################

    # assume the simulation will give us all vehicle objects info beforehand
    # Only ramp vehicles should run this function!!!

    # should get veh_transmitInfo_list before running this function
    def speed_coordination(self):
        k = 0.1  # control design gain for Eq2. Cannot find the value in paper.
        main_vel_list = []  # initialize a local list to store the velocity of all mainlane vehicles

        if self.lane == 1:  # only mergelane CAV should do speed coordination
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for i in range(len(self.mainVehInfo_list)):
                main_vel_list.append(self.mainVehInfo_list[i][3])

            # calculate the average speed based on subsection "2) Speed coordination" in the paper
            v_ref = sum(main_vel_list)/len(main_vel_list)
            self.Acc = k * (v_ref - self.Vel)
            self.Acc = max(min(self.Acc, self.maxAcc), self.minAcc)
            # print(f"CAV{self.id}'s vel is {self.Vel} from speed coordination")
            # print(f"CAV{self.id}'s acc is {self.Acc} from speed coordination")

    #####################################
    # Gap alignment (finding VL and VF)
    #####################################

    # Only ramp vehicles should run this function!!!

    def gap_alignment(self):
        # initialize a list to store the position of all mainlane vehicles with their corresponding id as a tuple
        main_pos_id_list = []

        if self.lane == 1:  # only mergelane CAVs should do gap alignment
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for i in range(len(self.mainVehInfo_list)):
                main_pos_id_list.append(
                    (self.mainVehInfo_list[i][4], self.mainVehInfo_list[i][0]))  # (pos, id)

            # print(f"main_pos_id_list: {main_pos_id_list}")

            # main_pos_id_list should be sorted based on the position (large to small) since mainVehInfo_list should be sorted already
            # if the self merge vehicle is behind the last mainlane vehicle, it's vl_id should be the last mainlane vehicle
            if self.Pos <= main_pos_id_list[len(main_pos_id_list)-1][0]:
                self.vl_id = main_pos_id_list[len(main_pos_id_list)-1][1]
                self.vf_id = 0
                # print(f"CAV ID: {self.id}, VL: {self.vl_id}")
            # if the self vehicle is ahead of the first mainlane vehicle, it does not have a vl
            elif self.Pos > main_pos_id_list[0][0]:
                self.vf_id = main_pos_id_list[0][1]
                self.vl_id = 0
            else:
                for i in range(len(main_pos_id_list)-1):
                    if ((main_pos_id_list[i][0] >= self.Pos) and (self.Pos > main_pos_id_list[i+1][0])):
                        self.vl_id = main_pos_id_list[i][1]
                        self.vf_id = main_pos_id_list[i+1][1]

                if self.vl_id == 0 and self.vf_id == 0:
                    print(
                        f"Cannot find the VL or VF for merge CAV {self.id} at {self.Pos} compared with {main_pos_id_list[len(main_pos_id_list)-1][0]} and {main_pos_id_list[0][0]}")

    ########################################
    # Virtual platoon control (Equation 4)
    ########################################

    # all CAVs should share their own info about VL and VF before running this function
    # it should get "self.vehiclesInfo" of all other vehicles [id, lane, Acc, Vel, Pos, vl_id, vf_id]
    # only the merge vehicles have updated their vl_id and vf_id for now
    # for self vehicle, only knows its vl is enough

    def virtual_platoon_control(self, dt):

        if self.lane == 1:
            # if the self merge CAV has its physical preceding merge CAV, and its vl_id is same as the preceding
            # its vl should be its physical preceding merge CAV
            # otherwise it should keep its vl_id
            for i in range(len(self.mergeVehInfo_list)):
                if ((self.id == self.mergeVehInfo_list[i][0]) and (i != 0)):
                    if self.vl_id == self.mergeVehInfo_list[i-1][5]:
                        self.vl_id = self.mergeVehInfo_list[i-1][0]
            # print(self.vehiclesInfo)

        else:
            # if self is in mainlane, if will read the vf_id of all merge CAVs,
            # if one/multi merge CAV's vf_id matches, self will follow the last merge CAV
            # otherwise self will follow its preceding mainlane CAV if it has one
            count = 0
            for i in self.mergeVehInfo_list:
                if self.id != i[6]:
                    continue
                else:
                    self.vl_id = i[0]
                    count += 1      # if at least one merge CAV's vf_id = mainlane self id, count !=0

            # no merge CAV's vf_id == mainlane self.id and mainlane self.id is the first vehicle in the mainlane
            if (count == 0) and (self.id == self.mainVehInfo_list[0][0]):
                self.vl_id = 0
            elif (count == 0) and (self.id != self.mainVehInfo_list[0][0]):
                self.vl_id = self.id - 1
            else:
                pass

        # refer the paper [Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data]
        kp = 0.45
        kd = 0.25   # refer the paper [Modeling ...]
        hd = 1.3    # [Coordinated Merge Control Based on V2V Communication]

        if self.vl_id != 0:
            # [id, lane, Acc, Vel, Pos, vl_id, vf_id]
            for index, Veh in enumerate(self.vehiclesInfo):
                if self.vl_id == Veh[0]:
                    # vp_Vel is the desired speed. Since we update the speed at the end in updateStatus(), we use a different Identifier here
                    self.vp_Vel = self.Vel + kp*(abs(self.Pos - self.vehiclesInfo[index][4])-hd*self.Vel) + kd*(
                        self.Vel-self.vehiclesInfo[index][3]-hd*self.Acc)
                    self.Acc = (self.vp_Vel-self.Vel)/dt
                    self.Acc = max(min(self.Acc, self.maxAcc), self.minAcc)

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

from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools


########################################################################################################################################
# Since Python does not have 3D dataframe, and using 3D nparray will lose the label for each row and column
# Here we build 2D Falsify Information Vector for attack channel since the number of channel type is limited compared to the other two
########################################################################################################################################
class CyberAttacker():
    def __init__(self, vehicles):
        self.vehicles = vehicles

    def mutAttackFalsifyInfoVectorCal(self, attackStartTime, t, mutFreqType, mutFreqParaValue, mutBiasType, mutBiasParaValue, currVic, currSour, currDura, currChan):
        FIV_value = 0  # initialize the returned bias value
        # "mutBiasType[currVic][currSour][currDura][currChan]" should only have 1 element when "Constant"
        if mutBiasType[currVic][currSour][currDura][currChan] == 'Constant':
            con_bias = mutBiasParaValue[currVic][currSour][currDura][currChan][0]
            FIV_value = con_bias
        # "mutBiasType[currVic][currSour][currDura][currChan]" should have 2 elements when "Linear"
        elif mutBiasType[currVic][currSour][currDura][currChan] == 'Linear':
            lin_bias = mutBiasParaValue[currVic][currSour][currDura][currChan][0]*(t-attackStartTime) + \
                mutBiasParaValue[currVic][currSour][currDura][currChan][1]      # y = ax + b
            FIV_value = lin_bias
        # "mutBiasType[currVic][currSour][currDura][currChan]" should have 4 elements when "Sinusoidal"
        elif mutBiasType[currVic][currSour][currDura][currChan] == 'Sinusoidal':
            sin_bias = mutBiasParaValue[currVic][currSour][currDura][currChan][0] * np.sin(2 * np.pi * mutBiasParaValue[currVic][currSour][currDura]
                                                                                           [currChan][1] * (t-attackStartTime) + mutBiasParaValue[currVic][currSour][currDura][currChan][2]) + mutBiasParaValue[currVic][currSour][currDura][currChan][3]
            FIV_value = sin_bias

        ##########################################################################
        # If there is a new mutation bias type, just add another branch here
        ##########################################################################
        else:
            print(
                f"Error in Mutation Bias Type in fv{currVic} at duration{currDura} on Channel{currChan}")

        if mutFreqType[currVic][currSour][currDura][currChan] == 'Continuous':
            mask = 1
            FIV_value = FIV_value * mask
        elif mutFreqType[currVic][currSour][currDura][currChan] == 'Cluster':
            period = mutFreqParaValue[currVic][currSour][currDura][currChan][0] + \
                mutFreqParaValue[currVic][currSour][currDura][currChan][1]

            if (t-attackStartTime) % period < mutFreqParaValue[currVic][currSour][currDura][currChan][0]:
                mask = 1
            else:
                mask = 0

            FIV_value = FIV_value * mask

        elif mutFreqType[currVic][currSour][currDura][currChan] == 'AntiCluster':
            period = mutFreqParaValue[currVic][currSour][currDura][currChan][0] + \
                mutFreqParaValue[currVic][currSour][currDura][currChan][1]

            if (t-attackStartTime) % period < mutFreqParaValue[currVic][currSour][currDura][currChan][0]:
                mask = 0
            else:
                mask = 1

            FIV_value = FIV_value * mask

        ##########################################################################
        # If there is a new mutation freq type, just add another branch here
        ##########################################################################

        else:
            print(
                f"Error in Mutation Bias Type in fv{currVic} at duration{currDura} on Channel{currChan}")

        ###############################################################
        # If there is a new characteristic found in future
        # other than frequency and bias, just add another branch here
        ###############################################################

        return FIV_value

    ######################################################################################################################
    # Assume the attackStartTime/attackEndTime is same as the simulation start/end time in the Simulation.py first!!!!!!
    ######################################################################################################################

    def mutAttackFalsifyInfoVectorGen(self, attackCase, attackStartTime, attackEndTime, controlTimeInterval):

        ####################################
        # 1. Extract All Attack Parameters
        ####################################

        # attackCase = [attackedVictim, maliChannelSource, attackDuration, attackChannel, freqType, freqParaValue, biasType, biasParaValue]
        # One example:
        # attackedVictim:      [                                          -1                             ,         -2         ]
        # maliChannelSource:   [  [                          1                ,             3          ] , [        1       ] ]
        # attackDuration:      [  [[        [10, 20]         , [   15,25  ]]  , [       [10, 20]     ] ] , [[   [10, 20]   ]] ]  # make sure all of them should between 'attackStartTime' and 'attackEndTime'
        # attackChannel:       [  [   [['Pos'   ,   'Vel' ]  , [   'Pos'  ]]  , [        ['Vel']     ] ] , [[[    'Pos'   ]]] ]
        # freqType:            [  [['Continuous', 'Cluster'] , [ 'Cluster']]  , [  [  'Continuous' ] ] ] , [[['Continuous']]] ]
        # freqParaValue:       [  [[    [0]    ,   [2,3]  ]  , [   [5,2]  ]]  , [  [       [0]     ] ] ] , [[[     [0]    ]]] ]
        # biasType:            [  [[ 'Linear'  ,'Constant']  , ['Constant']]  , [  [ 'Sinusoidal'  ] ] ] , [[[ 'Constant' ]]] ]
        # biasParaValue:       [  [[   [2,3]   ,    [4]   ]  , [    [6]   ]]  , [  [[10, 0.5, 0, 5]] ] ] , [[[     [4]    ]]] ]

        # Simplist example:
        # attackedVictim:      [        -1        ]
        # maliChannelSource:   [[        1       ]]
        # attackDuration:      [[[   [10, 20]   ]]]  # make sure all of them should between 'attackStartTime' and 'attackEndTime'
        # attackChannel:       [[[[    'Pos'   ]]]]
        # freqType:            [[[['Continuous']]]]
        # freqParaValue:       [[[[     [0]    ]]]]
        # biasType:            [[[[ 'Constant' ]]]]
        # biasParaValue:       [[[[     [4]    ]]]]

        attackedVictim = attackCase[0]
        maliChannelSource = attackCase[1]
        attackDuration = attackCase[2]
        attackChannel = attackCase[3]
        freqType = attackCase[4]
        freqParaValue = attackCase[5]
        biasType = attackCase[6]
        biasParaValue = attackCase[7]

        #############################################################################################
        # 2. Initialize 2D Falsify Information Vectors(FIV) which will store the bias
        #  for each CAV at each control time step. The number of FIV depends on total channel types
        #############################################################################################

        # Calculate the total time steps for easier implementation when calling "mutAttackFalsifyInfoVectorCal()"
        totalTimestep = int(
            (attackEndTime-attackStartTime)/controlTimeInterval)

        # initialize the dataframe to store the mutation bias for each channel type for each victim. rows: # of time step, column: # of CAVs
        # initialize lists, each list refers to a channel type and stores dataframes for different victims
        Pos_FIV_df_list = []
        Vel_FIV_df_list = []
        for i in range(len(attackedVictim)):
            Pos_FIV_df = pd.DataFrame(0, index=range(totalTimestep), columns=[
                veh.id for veh in self.vehicles])
            Vel_FIV_df = pd.DataFrame(0, index=range(totalTimestep), columns=[
                veh.id for veh in self.vehicles])
            Pos_FIV_df_list.append([attackedVictim[i], Pos_FIV_df])
            Vel_FIV_df_list.append([attackedVictim[i], Vel_FIV_df])

        """If there are totally 5 CAVs involved in the application, Pos_FIV_df_list should have a dataframe, and only one dataframe for each victim!!!,
        the dataframe will store the bias of the Pos type channels transmitted to the victim"""

        ####################################
        # 3. Generate FIVs
        ####################################

        # loop on each control time step
        for t in range(int(
                (attackEndTime-attackStartTime)/controlTimeInterval)):
            # loop on each victim
            for V in range(len(attackedVictim)):
                # several channel sources to the victim might be mutated
                for S in range(len(maliChannelSource[V])):
                    # the channels from the source to victim might be mutated at different durations
                    for D in range(len(attackDuration[V][S])):
                        # attackDuration[V][S][D][0]: start time of the current attack duration; attackDuration[V][S][D][1]: end time of the current attack duration
                        if attackDuration[V][S][D][0] <= t and t <= attackDuration[V][S][D][1]:
                            # for each victim in each attack duration, multiple channels might be attacked
                            for C in range(len(attackChannel[V][S][D])):
                                if attackChannel[V][S][D][C] == 'Pos':
                                    FIV_Pos = self.mutAttackFalsifyInfoVectorCal(attackDuration[V][S][D][0], t, freqType, freqParaValue, biasType,
                                                                                 biasParaValue, currVic=V, currSour=S, currDura=D, currChan=C)
                                    # check current victim (attackedVictim[V]), then find corresponding df, then replace the value to the corresponding place in the df
                                    for i in range(len(Pos_FIV_df_list)):
                                        if Pos_FIV_df_list[i][0] == attackedVictim[V]:
                                            Pos_FIV_df_list[i][1].loc[t,
                                                                      maliChannelSource[V][S]] = FIV_Pos

                                elif attackChannel[V][S][D][C] == 'Vel':
                                    FIV_Vel = self.mutAttackFalsifyInfoVectorCal(attackDuration[V][S][D][0], t, freqType, freqParaValue, biasType,
                                                                                 biasParaValue, currVic=V, currSour=S, currDura=D, currChan=C)
                                    for i in range(len(Vel_FIV_df_list)):
                                        if Vel_FIV_df_list[i][0] == attackedVictim[V]:
                                            Vel_FIV_df_list[i][1].loc[t,
                                                                      maliChannelSource[V][S]] = FIV_Vel

                        else:
                            continue   # skip iteration since no attack at current control step

        return Pos_FIV_df_list, Vel_FIV_df_list


if __name__ == "__main__":
    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
        Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
    ]

    # attackCase = [[3],                # attackVictim
    #               [[[10, 20]]],        # attackDuration
    #               [[['Pos']]],        # attackChannel
    #               [[['Continuous']]],  # freqType
    #               [[[[0]]]],          # freqValue
    #               [[['Linear']]],     # biasType
    #               [[[[0.2, 5]]]],      # biasValue y = ax + b
    #               ]

    attackCase = [
        [-1],   # attackedVictim
        [[1]],  # maliChannelSource
        [[[[10, 20]]]],  # attackDuration:
        [[[['Pos']]]],  # attackChannel:
        [[[['Continuous']]]],  # freqType:
        [[[[[0]]]]],  # freqParaValue:
        [[[['Constant']]]],  # biasType:
        [[[[[4]]]]]   # biasParaValue:
    ]

    # attackVictim = [1, 3]
    # attackDuration = [[10, 20], [15, 25]]
    # attackChannel = [["Pos"], ["Vel"]]
    # freqType = [["Continuous"], ["Cluster"]]
    # freqValue = [[0], [2, 3]]
    # biasType = [["Linear"], ["Constant"]]
    # biasValue = [[2, 3], [5]]

    attacker = CyberAttacker(vehicles)

    # attackCaseList = attacker.mutAttackCaseGenerator_1Vic1Dura1Chan(duration_startT=10,
    #                                                                 duration_maxlength=20,
    #                                                                 duration_interval=10,
    #                                                                 allMaliChannelList=[
    #                                                                     'Pos', 'Vel'],
    #                                                                 allFreqTypeList=[
    #                                                                     'Continuous'],
    #                                                                 freqValue=[
    #                                                                     0],
    #                                                                 allBiasTypeList=[
    #                                                                     'Constant'],
    #                                                                 allBiasParaValue=[1, 10, 1])

    # print(attackCaseList)

    Pos_FIV_df_list, Vel_FIV_df_list = attacker.mutAttackFalsifyInfoVectorGen(
        attackCase, 0, 10, 0.1)

    print(f"Pos_FIV_df_list: {Pos_FIV_df_list}")
    # print(Vel_FIV_df_list)

    def plot_results(Pos_FIV_df_list):
        for i in range(len(Pos_FIV_df_list)):      # go through each victim
            for column in Pos_FIV_df_list[i][1].columns:
                plt.plot(Pos_FIV_df_list[i][1].index,
                         Pos_FIV_df_list[i][1][column], label=column)

        # Adding labels and title
        plt.xlabel('Control Time Step')
        plt.ylabel('Bias Value')
        plt.title(
            f'Bias Value of Pos Channel on Victim {Pos_FIV_df_list[i][0]}')

        # Adding a legend
        plt.legend()

        # Display the plot
        plt.show()

    plot_results(Pos_FIV_df_list)
    # plot_results(Vel_FIV_df_list, 'Velocity')


######################################################
# An example on how to generate a list of attackCases
# Need to be debugged
######################################################


# def mutAttackCaseGenerator_1Vic1Dura1Chan(self,
#                                               # a list. [veh.id for veh in self.vehicles] if you want to add all vehicles
#                                               allVehID,
#                                               duration_startT,
#                                               duration_maxlength,
#                                               duration_interval,
#                                               allMaliChannelList,
#                                               allFreqTypeList,
#                                               freqValue,
#                                               allBiasTypeList,
#                                               allBiasParaValue
#                                               ):

#         # victim_num:         the number of victims,  only consider 1 victim
#         # source_num:         the number of source to victim, only consider 1 source
#         # duration_num:       the number of attackdurations, consider 1 only
#         # duration_startT:    start time of the attack duration, fixed
#         # duration_maxlength: the max length of duration
#         # duration_interval:  the increase interval of duration actual length
#         # allMaliChannelList: all channel types that are malicious
#         # allFreqTypeList:    all freq types we are going to implement (only consider 'Continuous' for now since the impact of continuous is likely more compared to Cluster)
#         # freqValue:          since we only consider 'Continuous' for now, it should be 0
#         # allBiasTypeList:    all bias types we are going to implement
#         # allBiasParaValue:   depend on the type of bias

#         victim_num = 1
#         source_num = 1
#         duration_num = 1

#         attackCaseList = []

#         ####################################################################
#         # 1. Generate all possible "attackVictim" and store them as a list
#         ####################################################################

#         # Generate all possible combinations for each specified victim vehicle number
#         # store all possible attackVictim list for different number of victims
#         victim_veh_tuple_all = []
#         for length in range(1, victim_num+1):
#             # generate all possible attackVictim list for all attackCases
#             victim_veh_tuple = itertools.combinations(allVehID, length)
#             victim_veh_tuple_all.extend(victim_veh_tuple)

#         # Convert the combinations from tuples to lists
#         attackVictimList = [list(combo)
#                             for combo in victim_veh_tuple_all]   # if victim_num=1 and allVehID = [veh.id for veh in self.vehicles], the result should be [[1], [2], [3], [-1], [-2]]
#         # print(f"attackVictimList: {attackVictimList}")

#         #######################################################################
#         # 2. Generate all possible "maliChannelSource" and store them as a list
#         #    Only consider 1 maliChannelSource for 1 victim for now
#         #    (You have to make sure that the maliChannelSource is not same as the Victim,
#         #     or if they are the same, the bias would be 0)
#         #######################################################################

#         #######################################################################
#         # 2. Generate all possible "attackDuration" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         attackDurationList = [[[[duration_startT, duration_startT + duration_interval * i]]]
#                               for i in range(int(duration_maxlength/duration_interval))]

#         # print(f"attackDurationList: {attackDurationList}")

#         #######################################################################
#         # 3. Generate all possible "attackChannel" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         attackChannelList = [[[['Pos']]], [[['Vel']]]]

#         #######################################################################
#         # 4. Generate all possible "freqType" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         freqTypeList = [[[['Continuous']]]]

#         #######################################################################
#         # 5. Generate all possible "freqParaValue" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         freqParaValueList = [[[[[0]]]]]

#         #######################################################################
#         # 6. Generate all possible "biasType" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         biasTypeList = [[[['Constant']]]]

#         #######################################################################
#         # 7. Generate all possible "biasParaValue" and store them as a list
#         #    Only consider 1 attackDuration for 1 victim for now
#         #######################################################################

#         # For 'Constant' bias type, allBiasParaValue should have 3 elements
#         # 1st element shows the Bias we want to add initially
#         # 2nd element shows the Bias we want to add at the end
#         # 3rd element shows the step we increase the Bias value

#         initialBias = allBiasParaValue[0]
#         endBias = allBiasParaValue[1]
#         increaseStep = allBiasParaValue[2]

#         biasParaValueList = [[[[[initialBias+increaseStep*i]]]]
#                              for i in range(int((endBias-initialBias)/increaseStep))]

#         # print(f"biasParaValueList: {biasParaValueList}")

#         #######################################################################
#         # Generate all possible attackCase based on the 7 lists above
#         #######################################################################

#         attackCaseList = [list(attackCase) for attackCase in itertools.product(attackVictimList, attackDurationList,
#                                                                                attackChannelList, freqTypeList, freqParaValueList, biasTypeList, biasParaValueList)]

#         return attackCaseList

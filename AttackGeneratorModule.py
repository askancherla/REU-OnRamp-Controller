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

    def mutAttackFalsifyInfoVectorCal(self, attackStartTime, t, mutFreqType, mutFreqParaValue, mutBiasType, mutBiasParaValue, currVic, currDura, currChan):
        FIV_value = 0  # initialize the returned bias value
        # "mutBiasType[currVic][currDura][currChan]" should only have 1 element when "Constant"
        if mutBiasType[currVic][currDura][currChan] == 'Constant':
            con_bias = mutBiasParaValue[currVic][currDura][currChan][0]
            FIV_value = con_bias
        # "mutBiasType[currVic][currDura][currChan]" should have 2 elements when "Linear"
        elif mutBiasType[currVic][currDura][currChan] == 'Linear':
            lin_bias = mutBiasParaValue[currVic][currDura][currChan][0]*(t-attackStartTime) + \
                mutBiasParaValue[currVic][currDura][currChan][1]      # y = ax + b
            FIV_value = lin_bias
        # "mutBiasType[currVic][currDura][currChan]" should have 4 elements when "Sinusoidal"
        elif mutBiasType[currVic][currDura][currChan] == 'Sinusoidal':
            sin_bias = mutBiasParaValue[currVic][currDura][currChan][0] * np.sin(2 * np.pi * mutBiasParaValue[currVic][currDura]
                                                                                 [currChan][1] * (t-attackStartTime) + mutBiasParaValue[currVic][currDura][currChan][2]) + mutBiasParaValue[currVic][currDura][currChan][3]
            FIV_value = sin_bias

        ##########################################################################
        # If there is a new mutation bias type, just add another branch here
        ##########################################################################
        else:
            print(
                f"Error in Mutation Bias Type in fv{currVic} at duration{currDura} on Channel{currChan}")

        if mutFreqType[currVic][currDura][currChan] == 'Continuous':
            mask = 1
            FIV_value = FIV_value * mask
        elif mutFreqType[currVic][currDura][currChan] == 'Cluster':
            period = mutFreqParaValue[currVic][currDura][currChan][0] + \
                mutFreqParaValue[currVic][currDura][currChan][1]

            if (t-attackStartTime) % period < mutFreqParaValue[currVic][currDura][currChan][0]:
                mask = 1
            else:
                mask = 0

            FIV_value = FIV_value * mask

        elif mutFreqType[currVic][currDura][currChan] == 'AntiCluster':
            period = mutFreqParaValue[currVic][currDura][currChan][0] + \
                mutFreqParaValue[currVic][currDura][currChan][1]

            if (t-attackStartTime) % period < mutFreqParaValue[currVic][currDura][currChan][0]:
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

    def mutAttackFalsifyInfoVectorGen(self, attackCase, attackStartTime, attackEndTime, controlTimeInterval):

        ####################################
        # 1. Extract All Attack Parameters
        ####################################

        # attackCase = [attackVictim, attackDuration, attackChannel, freqType, freqParaValue, biasType, biasParaValue]
        # One example:
        # attackVictim:   [                            1                ,             3            ]
        # attackDuration: [  [         [10, 20]        , [   15,25  ]]  , [        [20, 30]      ] ]  # make sure all of them should between 'attackStartTime' and 'attackEndTime'
        # attackChannel:  [  [[   'Pos'   ,   'Vel'  ] , [   'Pos'  ]]  , [  [      'Vel'      ] ] ]
        # freqType:       [  [['Continuous, 'Cluster'] , [ 'Cluster']]  , [  [  'Continuous'   ] ] ]
        # freqParaValue:  [  [[    [0]    ,   [2,3]  ] , [   [5,2]  ]]  , [  [       [0]       ] ] ]
        # biasType:       [  [[ 'Linear'  ,'Constant'] , ['Constant']]  , [  [  'Sinusoidal'   ] ] ]
        # biasParaValue:  [  [[   [2,3]   ,    [4]   ] , [    [6]   ]]  , [  [ [10, 0.5, 0, 5] ] ] ]

        attackVictim = attackCase[0]
        attackDuration = attackCase[1]
        attackChannel = attackCase[2]
        freqType = attackCase[3]
        freqParaValue = attackCase[4]
        biasType = attackCase[5]
        biasParaValue = attackCase[6]

        #############################################################################################
        # 2. Initialize 2D Falsify Information Vectors(FIV) which will store the bias
        #  for each CAV at each control time step. The number of FIV depends on total channel types
        #############################################################################################

        # Calculate the total time steps for easier implementation when calling "mutAttackFalsifyInfoVectorCal()"
        totalTimestep = int(
            (attackEndTime-attackStartTime)/controlTimeInterval)

        # initialize a dataframe for ploting. rows: # of time step, column: # of CAVs
        Pos_FIV_df = pd.DataFrame(0, index=range(totalTimestep), columns=[
                                  veh.id for veh in vehicles])

        Vel_FIV_df = pd.DataFrame(0, index=range(totalTimestep), columns=[
                                  veh.id for veh in vehicles])

        ####################################
        # 3. Generate FIVs
        ####################################

        # loop on each control time step
        for t in range(int(
                (attackEndTime-attackStartTime)/controlTimeInterval)):
            # loop on each victim
            for V in range(len(attackVictim)):
                # each victim may be attacked at differernt time duration
                for D in range(len(attackDuration[V])):
                    # attackDuration[V][D][0]: start time of the current attack duration; attackDuration[V][D][1]: end time of the current attack duration
                    if attackDuration[V][D][0] <= t and t <= attackDuration[V][D][1]:
                        # for each victim in each attack duration, multiple channels might be attacked
                        for C in range(len(attackChannel[V][D])):
                            if attackChannel[V][D][C] == 'Pos':
                                FIV_Pos = self.mutAttackFalsifyInfoVectorCal(attackDuration[V][D][0], t, freqType, freqParaValue, biasType,
                                                                             biasParaValue, currVic=V, currDura=D, currChan=C)
                                Pos_FIV_df.loc[t, attackVictim[V]] = FIV_Pos

                            elif attackChannel[V][D][C] == 'Vel':
                                FIV_Vel = self.mutAttackFalsifyInfoVectorCal(attackDuration[V][D][0], t, freqType, freqParaValue, biasType,
                                                                             biasParaValue, currVic=V, currDura=D, currChan=C)
                                Vel_FIV_df.loc[t, attackVictim[V]] = FIV_Vel

                    else:
                        continue   # skip iteration since no attack at current control step

        return Pos_FIV_df, Vel_FIV_df

    def mutAttackCaseGenerator_1Vic1Dura1Chan(self,
                                              duration_startT,
                                              duration_maxlength,
                                              duration_interval,
                                              allMaliChannelList,
                                              allFreqTypeList,
                                              freqValue,
                                              allBiasTypeList,
                                              allBiasParaValue
                                              ):

        # victim_num:         the number of victims
        # duration_num:       the number of attackdurations, consider 1 only
        # duration_startT:    start time of the attack duration, fixed
        # duration_maxlength: the max length of duration
        # duration_interval:  the increase interval of duration actual length
        # allMaliChannelList: all channel types that are malicious
        # allFreqTypeList:    all freq types we are going to implement (only consider 'Continuous' for now since the impact of continuous is likely more compared to Cluster)
        # freqValue:          since we only consider 'Continuous' for now, it should be 0
        # allBiasTypeList:    all bias types we are going to implement
        # allBiasParaValue:   depend on the type of bias

        victim_num = 1
        duration_num = 1

        attackCaseList = []

        ####################################################################
        # 1. Generate all possible "attackVictim" and store them as a list
        ####################################################################

        # a list which contains all vehicle IDs
        allVehID = [veh.id for veh in self.vehicles]
        # Generate all possible combinations for each specified victim vehicle number
        # store all possible attackVictim list for different number of victims
        victim_veh_tuple_all = []
        for length in range(1, victim_num+1):
            # generate all possible attackVictim list for all attackCases
            victim_veh_tuple = itertools.combinations(allVehID, length)
            victim_veh_tuple_all.extend(victim_veh_tuple)

        # Convert the combinations from tuples to lists
        attackVictimList = [list(combo)
                            for combo in victim_veh_tuple_all]   # if victim_num=1, it should be [[1], [2], [3], [-1], [-2]]
        # print(f"attackVictimList: {attackVictimList}")

        #######################################################################
        # 2. Generate all possible "attackDuration" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        attackDurationList = [[[[duration_startT, duration_startT + duration_interval * i]]]
                              for i in range(int(duration_maxlength/duration_interval))]

        # print(f"attackDurationList: {attackDurationList}")

        #######################################################################
        # 3. Generate all possible "attackChannel" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        attackChannelList = [[[['Pos']]], [[['Vel']]]]

        #######################################################################
        # 4. Generate all possible "freqType" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        freqTypeList = [[[['Continuous']]]]

        #######################################################################
        # 5. Generate all possible "freqParaValue" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        freqParaValueList = [[[[[0]]]]]

        #######################################################################
        # 6. Generate all possible "biasType" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        biasTypeList = [[[['Constant']]]]

        #######################################################################
        # 7. Generate all possible "biasParaValue" and store them as a list
        #    Only consider 1 attackDuration for 1 victim for now
        #######################################################################

        # For 'Constant' bias type, allBiasParaValue should have 3 elements
        # 1st element shows the Bias we want to add initially
        # 2nd element shows the Bias we want to add at the end
        # 3rd element shows the step we increase the Bias value

        initialBias = allBiasParaValue[0]
        endBias = allBiasParaValue[1]
        increaseStep = allBiasParaValue[2]

        biasParaValueList = [[[[[initialBias+increaseStep*i]]]]
                             for i in range(int((endBias-initialBias)/increaseStep))]

        # print(f"biasParaValueList: {biasParaValueList}")

        #######################################################################
        # Generate all possible attackCase based on the 7 lists above
        #######################################################################

        attackCaseList = [list(attackCase) for attackCase in itertools.product(attackVictimList, attackDurationList,
                                                                               attackChannelList, freqTypeList, freqParaValueList, biasTypeList, biasParaValueList)]

        return attackCaseList


if __name__ == "__main__":
    vehicles = [
        Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
        Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
        Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
        Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
        Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
    ]

    attackCase = [[3],                # attackVictim
                  [[[10, 20]]],        # attackDuration
                  [[['Pos']]],        # attackChannel
                  [[['Continuous']]],  # freqType
                  [[[[0]]]],          # freqValue
                  [[['Linear']]],     # biasType
                  [[[[0.2, 5]]]],      # biasValue y = ax + b
                  ]

    # attackVictim = [1, 3]
    # attackDuration = [[10, 20], [15, 25]]
    # attackChannel = [["Pos"], ["Vel"]]
    # freqType = [["Continuous"], ["Cluster"]]
    # freqValue = [[0], [2, 3]]
    # biasType = [["Linear"], ["Constant"]]
    # biasValue = [[2, 3], [5]]

    attacker = CyberAttacker(vehicles)

    attackCaseList = attacker.mutAttackCaseGenerator_1Vic1Dura1Chan(duration_startT=10,
                                                                    duration_maxlength=20,
                                                                    duration_interval=10,
                                                                    allMaliChannelList=[
                                                                        'Pos', 'Vel'],
                                                                    allFreqTypeList=[
                                                                        'Continuous'],
                                                                    freqValue=[
                                                                        0],
                                                                    allBiasTypeList=[
                                                                        'Constant'],
                                                                    allBiasParaValue=[1, 10, 1])

    print(attackCaseList)

    # Pos_FIV_df, Vel_FIV_df = attacker.mutAttackFalsifyInfoVectorGen(
    #     attackCase, 0, 10, 0.1)

    # print(Pos_FIV_df)
    # print(Vel_FIV_df)

    def plot_results(df, channel):
        for column in df.columns:
            plt.plot(df.index, df[column], label=column)

        # Adding labels and title
        plt.xlabel('Control Time Step')
        plt.ylabel('Bias Value')
        plt.title(f'Bias Value of {channel} Channel')

        # Adding a legend
        plt.legend()

        # Display the plot
        plt.show()

    # plot_results(Pos_FIV_df, 'Position')
    # plot_results(Vel_FIV_df, 'Velocity')


# def mutationAttackBias(num_veh,
#                        total_time,
#                        time_interval,
#                        attackVictim,
#                        attackDuration,
#                        attackChannel,
#                        freqType,
#                        freqValue,
#                        biasType, biasValue):

#     # Attack Victim: [1, 3]
#     # Attack Duration: [[10, 20], [15, 25]]
#     # Attack Channel: [Pos, Vel]
#     # Freq Type: [Continuous, Cluster]
#     # Freq Value: [[0], [2, 3]]
#     # Bias Type: [Linear, Constant]
#     # Bias Value: [[2, 3], [5]]

#     return bias_df1, bias_df2, ...

#     """1. Could be a pandas dataframe, 2D numpy array, etc.
#        2. Could have one or multiple bias 2D charts, classified based on the victim CAV, channel type, etc."""


# def mutationAttackBias(time_steps, attackVictim, attackDuration, attackChannel, freqType, freqValue, biasType, biasValue):
#     bias_df = pd.DataFrame(0, index=time_steps, columns=attackVictim)

#     for victim, duration, channel, f_type, f_value, b_type, b_value in zip(attackVictim, attackDuration, attackChannel, freqType, freqValue, biasType, biasValue):
#         # Expect duration to be a list of [start, end] pairs
#         for start, end in duration:
#             start_idx = int(start)
#             end_idx = int(end)
#             print(
#                 f"Processing victim: {victim}, duration: {duration}, biasType: {b_type}, b_value: {b_value}")
#             try:
#                 # Ensure indices are within bounds
#                 if start_idx not in bias_df.index or end_idx not in bias_df.index:
#                     print(
#                         f"Indices out of bounds: start_idx {start_idx}, end_idx {end_idx}")
#                     continue

#                 if b_type == 'Constant':
#                     bias_df.loc[start:end, victim] = b_value[0]
#                 elif b_type == 'Linear':
#                     linear_values = np.linspace(
#                         b_value[0], b_value[1], end_idx - start_idx + 1)
#                     print(
#                         f"Setting linear values from {b_value[0]} to {b_value[1]} over range {start_idx} to {end_idx}")
#                     if len(bias_df.loc[start:end, victim]) != len(linear_values):
#                         print(
#                             f"Mismatch in length: DataFrame slice length is {len(bias_df.loc[start:end, victim])}, linear values length is {len(linear_values)}")
#                     bias_df.loc[start:end, victim] = linear_values
#                 elif b_type == 'Sinusoidal':
#                     sinusoidal_values = b_value[0] * np.sin(
#                         b_value[1] * np.arange(start_idx, end_idx + 1))
#                     print(
#                         f"Setting sinusoidal values with amplitude {b_value[0]} and frequency {b_value[1]} over range {start_idx} to {end_idx}")
#                     bias_df.loc[start:end, victim] = sinusoidal_values
#             except Exception as e:
#                 print(
#                     f"Error while processing victim {victim} from {start} to {end}: {e}")
#                 raise e

#     return bias_df

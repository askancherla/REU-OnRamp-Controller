from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
# import the Simulation class from Simulation.py
from Simulation import Simulation
from AttackGeneratorModule import CyberAttacker
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

vehicles = [
    Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
    Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-370),
    Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
    Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-380),
    Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-430)
]

simEndtime = 20
simTimestep = 0.1

Pos_FIV_df = []
Vel_FIV_df = []
sim = Simulation(vehicles, 20, 0.1)
if sim.check == 1:
    # if we don't want to implement attacks
    Pos_FIV_df_list_empty = [[0, pd.DataFrame(0, index=range(int(simEndtime / simTimestep)), columns=[
        veh.id for veh in vehicles])]]
    Vel_FIV_df_list_empty = [[0, pd.DataFrame(0, index=range(int(simEndtime / simTimestep)), columns=[
        veh.id for veh in vehicles])]]
    # if we don't want to implement attacks, uncomment this part and comments the next part of attacks

    # if we want to implement attacks
    attacker = CyberAttacker(vehicles)
    # attackCase = [
    #    [-1],   # attackedVictim
    #    [[2]],  # maliChannelSource
    #    [[[[10, 50]]]],  # attackDuration:
    #    [[[['Pos']]]],  # attackChannel:
    #    [[[['Continuous']]]],  # freqType:
    #    [[[[[0]]]]],  # freqParaValue:
    #    [[[['Constant']]]],  # biasType:
    #    [[[[[-50]]]]]   # biasParaValue:
    # ]
    
    attackCase = [
       [-1],   # attackedVictim
       [[2]],  # maliChannelSource
       [[[[10, 50]]]],  # attackDuration:
       [[[['Pos']]]],  # attackChannel:
       [[[['Cluster']]]],  # freqType:
       [[[[[2,20]]]]],  # freqParaValue:
       [[[['Constant']]]],  # biasType:
       [[[[[-50]]]]]   # biasParaValue:
    ]


    attackCaseList = attacker.mutAttackCaseGenerator_1Vic1Dura1Chan(allVehID = [1,2],
                                                                     mailChannelSource=1,
                                                                     duration_startT=10,
                                                                     duration_maxlength=20,
                                                                     duration_interval=10,
                                                                     allMaliChannelList=[
                                                                         'Pos'],
                                                                     allFreqTypeList=[
                                                                         'Continuous'],
                                                                     freqValue=[
                                                                         0],
                                                                     allBiasTypeList=[
                                                                         'Constant'],
                                                                     allBiasParaValue=[1,10])

    attackCaseList = list(attackCaseList)
    print(f"attackCaseList : {attackCaseList}")
    
    Pos_FIV_df_list = []
    Vel_FIV_df_list = []

    ######################
    ### Using attackCaseList
    #####################
    
    
    # Iterate over each attack case and apply it
    # for attackCase in attackCaseList:
    #     pos_fiv_df, vel_fiv_df = attacker.mutAttackFalsifyInfoVectorGen(
    #         attackCase, 0, simEndtime, simTimestep)
    #     Pos_FIV_df_list.append(pos_fiv_df)
    #     Vel_FIV_df_list.append(vel_fiv_df)
        
    Pos_FIV_df_list, Vel_FIV_df_list = attacker.mutAttackFalsifyInfoVectorGen(
    attackCase, 0, simEndtime, simTimestep)


    # def plot_results(FIV_df_list):
    #     for attack_index in range(len(FIV_df_list)):  # Process each attack case
    #         fig1, ax1 = plt.subplots()
    #         print(f"Processing FIV_df_list[{attack_index}]")  # Debugging
    #         if len(FIV_df_list[attack_index]) > 0:
    #             victim_id = FIV_df_list[attack_index][0][0]
    #             df = FIV_df_list[attack_index][0][1]
    #             time = df.index * simTimestep  # Assuming time steps need to be scaled by simTimestep
    #             for veh in vehicles:
    #                 line_style = '--' if veh.lane == 1 else '-'
    #                 ax1.plot(time, df[veh.id], label=f'Vehicle {veh.id}', linestyle=line_style)

    #             ax1.set_ylabel('Position (m)')
    #             ax1.set_xlabel('Time (s)')
    #             ax1.set_title(f'Vehicle Positions Over Time for Attack Case {attack_index + 1}')
    #             ax1.legend(loc='upper left')

    #             # Add rectangular zone
    #             ax1.axhspan(-200, 0, color='grey', alpha=0.3, label='Acceleration Zone')

    #             # Add text label
    #             ax1.text(100, -100, 'Acceleration Zone', fontsize=12, color='black',
    #                      horizontalalignment='center', verticalalignment='center')

    #             plt.tight_layout()
    #             plt.show()

    # plot_results(Pos_FIV_df_list)

   # if we want to implement a single attack on any process, use the argument 'Pos_FIV_df_list' or 'Vel_FIV_df_list' based on which channel type you want to attack
   # otherwise use the argument with '_empty'
    # sim.mergeSimulator(Pos_FIV_bias_df_list_speedCoop=Pos_FIV_df_list_empty,
    #                   Vel_FIV_bias_df_list_speedCoop=Vel_FIV_df_list_empty,
    #                   Pos_FIV_bias_df_list_VP=Pos_FIV_df_list,
    #                   Vel_FIV_bias_df_list_VP=Vel_FIV_df_list)
    
    sim.mergeSimulator(Pos_FIV_bias_df_list_speedCoop=Pos_FIV_df_list_empty,
                      Vel_FIV_bias_df_list_speedCoop=Vel_FIV_df_list_empty,
                      Pos_FIV_bias_df_list_VP=Pos_FIV_df_list,
                      Vel_FIV_bias_df_list_VP=Vel_FIV_df_list)
    
    # for pos_fiv_df, vel_fiv_df in zip(Pos_FIV_df_list, Vel_FIV_df_list):
    #     sim.mergeSimulator(Pos_FIV_bias_df_list_speedCoop=Pos_FIV_df_list_empty,
    #                       Vel_FIV_bias_df_list_speedCoop=Vel_FIV_df_list_empty,
    #                       Pos_FIV_bias_df_list_VP=[pos_fiv_df],
    #                       Vel_FIV_bias_df_list_VP=[vel_fiv_df])
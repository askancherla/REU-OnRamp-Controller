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

    # if we want to implement a single attack on any process, use the argument 'Pos_FIV_df_list' or 'Vel_FIV_df_list' based on which channel type you want to attack
    # otherwise use the argument with '_empty'
    sim.mergeSimulator(Pos_FIV_bias_df_list_speedCoop=Pos_FIV_df_list_empty,
                       Vel_FIV_bias_df_list_speedCoop=Vel_FIV_df_list_empty,
                       Pos_FIV_bias_df_list_VP=Pos_FIV_df_list,
                       Vel_FIV_bias_df_list_VP=Vel_FIV_df_list)

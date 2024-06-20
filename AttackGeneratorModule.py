from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
import numpy as np
import pandas as pd


def mutationAttackBias(num_veh,
                       total_time,
                       time_interval,
                       attackVictim,
                       attackDuration,
                       attackChannel,
                       freqType,
                       freqValue,
                       biasType, biasValue):

    # Attack Victim: [1, 3]
    # Attack Duration: [[10, 20], [15, 25]]
    # Attack Channel: [Pos, Vel]
    # Freq Type: [Continuous, Cluster]
    # Freq Value: [[0], [2, 3]]
    # Bias Type: [Linear, Constant]
    # Bias Value: [[2, 3], [5]]

    return bias_df1, bias_df2, ...

    """1. Could be a pandas dataframe, 2D numpy array, etc.
       2. Could have one or multiple bias 2D charts, classified based on the victim CAV, channel type, etc."""

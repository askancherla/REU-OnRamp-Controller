from Vehicle import Vehicle   # import the Vehicle class from Vehicle.py
import pandas as pd
import numpy as np

def mutationAttackBias(time_steps, attackVictim, attackDuration, attackChannel, freqType, freqValue, biasType, biasValue):
    bias_df = pd.DataFrame(0, index=time_steps, columns=attackVictim)

    for victim, duration, channel, f_type, f_value, b_type, b_value in zip(attackVictim, attackDuration, attackChannel, freqType, freqValue, biasType, biasValue):
        for start, end in duration:  # Expect duration to be a list of [start, end] pairs
            start_idx = int(start)
            end_idx = int(end)
            print(f"Processing victim: {victim}, duration: {duration}, biasType: {b_type}, b_value: {b_value}")
            try:
                # Ensure indices are within bounds
                if start_idx not in bias_df.index or end_idx not in bias_df.index:
                    print(f"Indices out of bounds: start_idx {start_idx}, end_idx {end_idx}")
                    continue

                if b_type == 'Constant':
                    bias_df.loc[start:end, victim] = b_value[0]
                elif b_type == 'Linear':
                    linear_values = np.linspace(b_value[0], b_value[1], end_idx - start_idx + 1)
                    print(f"Setting linear values from {b_value[0]} to {b_value[1]} over range {start_idx} to {end_idx}")
                    if len(bias_df.loc[start:end, victim]) != len(linear_values):
                        print(f"Mismatch in length: DataFrame slice length is {len(bias_df.loc[start:end, victim])}, linear values length is {len(linear_values)}")
                    bias_df.loc[start:end, victim] = linear_values
                elif b_type == 'Sinusoidal':
                    sinusoidal_values = b_value[0] * np.sin(b_value[1] * np.arange(start_idx, end_idx + 1))
                    print(f"Setting sinusoidal values with amplitude {b_value[0]} and frequency {b_value[1]} over range {start_idx} to {end_idx}")
                    bias_df.loc[start:end, victim] = sinusoidal_values
            except Exception as e:
                print(f"Error while processing victim {victim} from {start} to {end}: {e}")
                raise e

    return bias_df





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

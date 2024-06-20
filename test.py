import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# # List of dictionaries
# list_of_dicts = [
#     {'name': 'John', 'age': -28},
#     {'name': 'Jane', 'age': -23},
#     {'name': 'Doe', 'age': -32},
#     {'name': 'Emily', 'age': -25}
# ]

# # Sort by the 'age' key
# sorted_list = sorted(list_of_dicts, key=lambda x: x['age'], reverse=True)

# print(sorted_list)

# for i in reversed(range(5)):
#     print(f"Number: {i}")

# total_time = 10
# dt = 0.1
# for t in np.arange(0, total_time, dt):
#     print(t)

# Veh_Pos_plot = pd.DataFrame(0, index=range(
#     int(total_time / dt)), columns=["a", "b"])
# print(Veh_Pos_plot)


my_tuple_list = [(-240, 1), (-300, 2), (-350, 3)]
a = my_tuple_list[0][0]
b = my_tuple_list[1][1]
print(f"a: {a}, b: {b}, len: {len(my_tuple_list)-1}")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from Vehicle import Vehicle


# A = [[1], [2], [3]]
# B = [['Pos'], ['Vel'], ['Pos', 'Vel']]
# C = [[[0]], [[1]], [[2]]]

# combinations = [list(combo) for combo in itertools.product(A, B, C)]

# # Print each combination
# for combo in combinations:
#     print(f"Combination is: {combo}")


# def plot_results(self):
#         time = np.arange(0, int(self.total_time_plot / self.dt_plot), 1)

#         # Plot Position
#         fig1, ax1 = plt.subplots()
#         for veh in self.vehicles:
#             line_style = '--' if veh.lane == 1 else '-'
#             ax1.plot(time, self.Veh_Pos_plot[veh.id],
#                      label=f'Vehicle {veh.id}', linestyle=line_style)
#         ax1.set_ylabel('Position (m)')
#         ax1.set_title('Vehicle Positions Over Time')
#         ax1.legend(loc='upper left')
#         ax1.set_xlabel('Time (s)')
#         # Add rectangular zone
#         ax1.axhspan(-200, 0, color='grey', alpha=0.3,
#                     label='Acceleration Zone')

#         # Add text label
#         ax1.text(100, -100, 'Acceleration Zone', fontsize=12, color='black',
#                  horizontalalignment='center', verticalalignment='center')
#         plt.tight_layout()
#         plt.show()

#         # Plot Velocity
#         fig2, ax2 = plt.subplots()
#         for veh in self.vehicles:
#             line_style = '--' if veh.lane == 1 else '-'
#             ax2.plot(time, self.Veh_Vel_plot[veh.id],
#                      label=f'Vehicle {veh.id}', linestyle=line_style)
#         ax2.set_ylabel('Velocity (m/s)')
#         ax2.set_title('Vehicle Velocities Over Time')
#         ax2.legend(loc='upper left')
#         ax2.set_xlabel('Time (s)')
#         plt.tight_layout()
#         plt.show()

#         # Plot Acceleration
#         fig3, ax3 = plt.subplots()
#         for veh in self.vehicles:
#             line_style = '--' if veh.lane == 1 else '-'
#             ax3.plot(time, self.Veh_Acc_plot[veh.id],
#                      label=f'Vehicle {veh.id}', linestyle=line_style)
#         ax3.set_ylabel('Acceleration (m/s²)')
#         ax3.set_title('Vehicle Accelerations Over Time')
#         ax3.legend(loc='upper left')
#         ax3.set_xlabel('Time (s)')
#         plt.tight_layout()
#         plt.show()

#         # Plot VL ID
#         fig4, ax4 = plt.subplots()
#         for veh in self.vehicles:
#             line_style = '--' if veh.lane == 1 else '-'
#             ax4.plot(time, self.Veh_vl_id_plot[veh.id],
#                      label=f'Vehicle {veh.id}', linestyle=line_style)
#         ax4.set_ylabel('Virtual Leader ID')
#         ax4.set_title('Vehicle Virtual Leader IDs Over Time')
#         ax4.legend(loc='upper left')
#         ax4.set_xlabel('Time (s)')
#         plt.tight_layout()
#         plt.show()

#         # # Plot VF ID
#         # fig5, ax5 = plt.subplots()
#         # for veh in self.vehicles:
#         #     line_style = '--' if veh.lane == 1 else '-'
#         #     ax5.plot(time, self.Veh_vf_id_plot[veh.id],
#         #              label=f'Vehicle {veh.id}', linestyle=line_style)
#         # ax5.set_ylabel('Virtual Follower ID')
#         # ax5.set_title('Vehicle Virtual Follower IDs Over Time')
#         # ax5.legend(loc='upper left')
#         # ax5.set_xlabel('Time (s)')
#         # plt.tight_layout()
#         # plt.show()


vehicles = [
    Vehicle(id=1, lane=0, init_Vel=25, init_Pos=-240),
    Vehicle(id=2, lane=0, init_Vel=27, init_Pos=-320),
    Vehicle(id=3, lane=0, init_Vel=26, init_Pos=-400),
    Vehicle(id=-1, lane=1, init_Vel=30, init_Pos=-400),
    Vehicle(id=-2, lane=1, init_Vel=30, init_Pos=-500)
]

# columns = [veh.id for veh in vehicles]
# print(f"All veh ids: {columns}")

totalTimestep = int((10)/0.1)
print(f"total time steps: {totalTimestep}")

Veh_Pos_plot = pd.DataFrame(0, index=range(
    int(10 / 0.1)), columns=[veh.id for veh in vehicles])


print(Veh_Pos_plot)


A = [[1, 2, 3, 4, 5, 6, 7],
     [1, 2, 3, 4, 5, 6, 7],
     [1, 2, 3, 4, 5, 6, 7],
     [1, 2, 3, 4, 5, 6, 7],
     [1, 2, 3, 4, 5, 6, 7]]

B = pd.DataFrame(1, index=range(
    int(10 / 0.1)), columns=[veh.id for veh in vehicles])

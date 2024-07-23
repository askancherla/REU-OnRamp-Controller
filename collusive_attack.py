# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 14:34:12 2022

@author: HP
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import time
import random

import matplotlib.gridspec as gridspec
import math

def Add_Collusive_Anomaly(lead_traj, 
                bias_dict, # bias_dict = {"Ego_Acc": -2, "Ego_Vel": None}
                freq_type_dict, # freq_type_dict = {"Ego_Acc": 'continuous', "Ego_Vel": None}
                attack_ip_list, # attack_ip_list = ['Ego_Acc', 'Ego_Vel']
                bias_type_dict, # bias_type_dict = {"Ego_Acc": 'constant', "Ego_Vel": None}
                sin_freq_dict = None,
                start = 1500,
                end = 3000,
                cluster_window = 200,
                max_delta_dict = None,
                max_sin_freq_dict = None,
                num_clusters = 2,
                shift = 0):
    
    leader_attack_traj = lead_traj.copy()   
    stealth_mask_dict = {}
    if max_delta_dict is None:
        max_delta_dict = {}
        max_delta_dict['Ego_Acc'] = 2.0
        max_delta_dict['Ego_Vel'] = 2.0
        max_delta_dict['Ego_Pos'] = 2.0
    if max_sin_freq_dict is None:
        max_sin_freq_dict = {}
        max_sin_freq_dict['Ego_Acc'] = 0.8
        max_sin_freq_dict['Ego_Vel'] = 0.8
        max_sin_freq_dict['Ego_Pos'] = 0.8
    if sin_freq_dict is None:
        sin_freq_dict = {}
        sin_freq_dict['Ego_Acc'] = 0.5
        sin_freq_dict['Ego_Vel'] = 0.5
        sin_freq_dict['Ego_Pos'] = 0.5
    
    # if ("Ego_Acc" in attack_ip_list):
    #     primary_attack_ip = "Ego_Acc"
        
    # else:
    #     primary_attack_ip = "Ego_Vel"
    
    #attack_ip_list.remove(primary_attack_ip)
    primary_attack_ip = attack_ip_list[0]
    secondary_attack_ip = attack_ip_list[1]
        
        
    attack_ip = primary_attack_ip
    freq_type = freq_type_dict[attack_ip]
    bias_type = bias_type_dict[attack_ip]
    bias = bias_dict[attack_ip]
    sin_freq = sin_freq_dict[attack_ip]
    stealth_mask = np.zeros(len(lead_traj))
    max_delta = max_delta_dict[attack_ip]   
    max_sin_freq = max_sin_freq_dict[attack_ip]
    
    ############################
    # Compute stealth mask
    ############################
    
    if freq_type == 'continuous':
        stealth_mask[start:end] = 1
    elif freq_type == 'cluster':            
        rand_idxs = [] 

        my_start = start 

        partition_size = int((end-start)/num_clusters) 

        print("Partition_size", partition_size) 

        my_end = start + partition_size 

        for i in range(num_clusters): 

            my_end = start + (i+1)*partition_size 

            rand_idx = random.randint(my_start, my_end-cluster_window) 

            stealth_mask[rand_idx : rand_idx + cluster_window] = 1 

            my_start = rand_idx + cluster_window 

            rand_idxs.append(rand_idx) 
    else:
        print("Unknown freq_type")
    
    stealth_mask_dict[attack_ip] = stealth_mask.copy()
    stealth_mask_dict[secondary_attack_ip] = stealth_mask.copy()


    

    signed_max_delta = math.copysign(max_delta, bias)
    
    if bias_type == 'constant':
        
        if freq_type == 'continuous':
            linear_window = int(np.abs((bias/max_delta)))
            time_array = signed_max_delta*np.linspace(0, linear_window-1, linear_window)
            leader_attack_traj[attack_ip].iloc[start:start+linear_window] += time_array
            leader_attack_traj[attack_ip].iloc[start+linear_window:end] += bias
        
        elif freq_type == 'cluster':
            # linear_window = int(np.abs((bias/max_delta)))
            # if cluster_window < linear_window:
            #     cluster_window = linear_window
            # constant_window = int(cluster_window - 2*linear_window)
            for rand_idx in rand_idxs: 

                 leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+cluster_window]+=bias
            # for rand_idx in rand_idxs:
            #     time_array_1 = signed_max_delta*np.linspace(0, linear_window-1, linear_window)
            #     time_array_2 = signed_max_delta*np.linspace(linear_window-1, 0, linear_window)
                    
            #     leader_attack_traj[attack_ip].iloc[rand_idx:rand_idx+linear_window]+=time_array_1
            #     leader_attack_traj[attack_ip].iloc[rand_idx+linear_window: rand_idx+linear_window+constant_window]+=bias               
            #     leader_attack_traj[attack_ip].iloc[rand_idx+linear_window+constant_window: rand_idx+cluster_window]+=time_array_2
                
                
        
    elif bias_type == 'linear':
        if np.abs(bias) > max_delta:
            if bias>0:
                bias = max_delta
            else:
                bias = -max_delta
            
        if freq_type == 'continuous':
            time_array = bias*np.linspace(0, np.sum(stealth_mask) -1, int(np.sum(stealth_mask)))
            leader_attack_traj[attack_ip].iloc[start:end]+=time_array 
        elif freq_type == 'cluster':
            # n = int((max_delta * cluster_window)/(np.abs(bias) + max_delta))
            # time_array_1 = bias*np.linspace(0, n-1, n)
            # time_array_2 = ((bias*n)/(cluster_window- n))*np.linspace(cluster_window-n-1,0,cluster_window-n)
            time_array = bias*np.linspace(0, cluster_window-1, cluster_window)
            for rand_idx in rand_idxs: 

                leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+cluster_window]+=time_array
            # for rand_idx in rand_idxs:
            #     leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+n]+=time_array_1
            #     leader_attack_traj[attack_ip].iloc[rand_idx+n: rand_idx+cluster_window]+=time_array_2
    
    
    elif bias_type == 'sinusoidal':
        if sin_freq > max_sin_freq:
            sin_freq = max_sin_freq
        time_array = np.arange(0, len(stealth_mask[stealth_mask==1])/100, 0.01)
        sin_bias = bias*np.sin(time_array*sin_freq)
        leader_attack_traj[attack_ip].loc[stealth_mask==1] = leader_attack_traj[attack_ip].loc[stealth_mask==1] + sin_bias[:np.count_nonzero(stealth_mask==1)]
    else:
        print('Unknown bias_type')
       
    leader_attack_traj.reset_index(inplace=True, drop = True)
    #leader_attack_traj = Clip_Params(lead_traj = leader_attack_traj.copy())
    
    #########################################
    # Corrupting the secondary input collusively
    #########################################
    if secondary_attack_ip == "Ego_Vel":
        if freq_type == 'continuous':
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            v_array = np.zeros(len(lead_traj))
            v_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            v_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                v_array[i] = v_array[i-1] + a_array[idx-1]*dT_array[idx-1]
            leader_attack_traj["Ego_Vel"] = v_array
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                v_array = np.zeros(len(a_array))
                v_array[0] = leader_attack_traj['Ego_Vel'].iloc[rand_idx+shift]
                for i in np.arange(1, len(a_array)):
                    v_array[i] = v_array[i-1] + a_array[i-1]*dT_array[i-1]
                leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window] = v_array
                
    elif secondary_attack_ip == "Ego_Pos":
        if freq_type == 'continuous':
            # u_array = np.zeros(len(lead_traj))
            # u_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            # u_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            # s_array = np.zeros(len(lead_traj))
            # s_array[0:start+shift+1] = u_array[0:start+shift+1]*dT_array[0:start+shift+1] + 0.5*a_array[0:start+shift+1]*(dT_array[0:start+shift+1]**2)
            u_array = leader_attack_traj["Ego_Vel"].iloc[start+shift+1:end].values
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
            pos_array = np.zeros(len(lead_traj))
            pos_array[0:start+shift+1] = leader_attack_traj['Ego_Pos'].iloc[0:start+shift+1].values
            pos_array[end:] = leader_attack_traj['Ego_Pos'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                # u_array[i] = u_array[i-1] + a_array[idx-1]*dT_array[idx-1]
                # s = u_array[i-1]*dT_array[idx-1] + 0.5*a_array[idx-1]*(dT_array[idx-1]**2)
                pos_array[i] = pos_array[i-1] + s_array[idx-1]
            leader_attack_traj["Ego_Pos"] = pos_array
            # leader_attack_traj["Ego_Pos"].iloc[start+shift+1:end+1] = pos_array
            
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                u_array = leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
                pos_array = np.zeros(len(a_array))
                pos_array[0] = leader_attack_traj['Ego_Pos'].iloc[rand_idx+shift]
                for i in np.arange(1, len(pos_array)):
                    # u_array[i] = u_array[i-1] + a_array[i-1]*dT_array[i-1]
                    # s = u_array[i-1]*dT_array[i-1] + 0.5*a_array[i-1]*(dT_array[i-1]**2)                    
                    pos_array[i] = pos_array[i-1] + s_array[i-1]
                leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift:rand_idx+shift+cluster_window] = pos_array   

    # elif secondary_attack_ip == "Ego_Pos":
    #     if freq_type == 'continuous':
    #         u_array = leader_attack_traj["Ego_Vel"].iloc[start+shift-1:end+shift-1]
    #         a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift-1:end+shift-1]
    #         dT_array = leader_attack_traj["dT"].iloc[start+shift-1:end+shift-1]
    #         s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
    #         leader_attack_traj["Ego_Pos"].iloc[start+shift:end+shift] = leader_attack_traj["Ego_Pos"].iloc[start+shift-1:end+shift-1] + s_array # pos(t) = pos(t-1) + s; s= ut+0.5at^2 
    #     elif freq_type == 'cluster':
    #         for rand_idx in rand_idxs:
    #             u_array = leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
    #             leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift:rand_idx+shift+cluster_window] = leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1] + s_array # pos(t) = pos(t-1) + s; s= ut+0.5at^2       
        
        
    leader_attack_traj.reset_index(inplace=True, drop = True)
    leader_attack_traj = Clip_Params(lead_traj = leader_attack_traj.copy())
    
    
    return leader_attack_traj



def Add_Collusive_Anomaly_3C(lead_traj, 
                bias_dict, # bias_dict = {"Ego_Acc": -2, "Ego_Vel": None}
                freq_type_dict, # freq_type_dict = {"Ego_Acc": 'continuous', "Ego_Vel": None}
                attack_ip_list, # attack_ip_list = ['Ego_Acc', 'Ego_Vel']
                bias_type_dict, # bias_type_dict = {"Ego_Acc": 'constant', "Ego_Vel": None}
                sin_freq_dict = None,
                start = 1500,
                end = 3000,
                cluster_window = 200,
                max_delta_dict = None,
                max_sin_freq_dict = None,
                num_clusters = 2,
                shift = 0):
    
    leader_attack_traj = lead_traj.copy()   
    stealth_mask_dict = {}
    if max_delta_dict is None:
        max_delta_dict = {}
        max_delta_dict['Ego_Acc'] = 2.0
        max_delta_dict['Ego_Vel'] = 2.0
        max_delta_dict['Ego_Pos'] = 2.0
    if max_sin_freq_dict is None:
        max_sin_freq_dict = {}
        max_sin_freq_dict['Ego_Acc'] = 0.8
        max_sin_freq_dict['Ego_Vel'] = 0.8
        max_sin_freq_dict['Ego_Pos'] = 0.8
    if sin_freq_dict is None:
        sin_freq_dict = {}
        sin_freq_dict['Ego_Acc'] = 0.5
        sin_freq_dict['Ego_Vel'] = 0.5
        sin_freq_dict['Ego_Pos'] = 0.5
    
    # if ("Ego_Acc" in attack_ip_list):
    #     primary_attack_ip = "Ego_Acc"
        
    # else:
    #     primary_attack_ip = "Ego_Vel"
    
    #attack_ip_list.remove(primary_attack_ip)
    primary_attack_ip = attack_ip_list[0]
    secondary_attack_ip = attack_ip_list[1]
    tertiary_attack_ip = attack_ip_list[2]    
        
    attack_ip = primary_attack_ip
    freq_type = freq_type_dict[attack_ip]
    bias_type = bias_type_dict[attack_ip]
    bias = bias_dict[attack_ip]
    sin_freq = sin_freq_dict[attack_ip]
    stealth_mask = np.zeros(len(lead_traj))
    max_delta = max_delta_dict[attack_ip]   
    max_sin_freq = max_sin_freq_dict[attack_ip]
    
    ############################
    # Compute stealth mask
    ############################
    
    if freq_type == 'continuous':
        stealth_mask[start:end] = 1
    elif freq_type == 'cluster':            
        rand_idxs = [] 

        my_start = start 

        partition_size = int((end-start)/num_clusters) 

        print("Partition_size", partition_size) 

        my_end = start + partition_size 

        for i in range(num_clusters): 

            my_end = start + (i+1)*partition_size 

            rand_idx = random.randint(my_start, my_end-cluster_window) 

            stealth_mask[rand_idx : rand_idx + cluster_window] = 1 

            my_start = rand_idx + cluster_window 

            rand_idxs.append(rand_idx) 
    else:
        print("Unknown freq_type")
    
    stealth_mask_dict[attack_ip] = stealth_mask.copy()
    stealth_mask_dict[secondary_attack_ip] = stealth_mask.copy()
    stealth_mask_dict[tertiary_attack_ip] = stealth_mask.copy()

    

    signed_max_delta = math.copysign(max_delta, bias)
    
    if bias_type == 'constant':
        
        if freq_type == 'continuous':
            linear_window = int(np.abs((bias/max_delta)))
            time_array = signed_max_delta*np.linspace(0, linear_window-1, linear_window)
            leader_attack_traj[attack_ip].iloc[start:start+linear_window] += time_array
            leader_attack_traj[attack_ip].iloc[start+linear_window:end] += bias
        
        elif freq_type == 'cluster':
            # linear_window = int(np.abs((bias/max_delta)))
            # if cluster_window < linear_window:
            #     cluster_window = linear_window
            # constant_window = int(cluster_window - 2*linear_window)
            # for rand_idx in rand_idxs:
            #     time_array_1 = signed_max_delta*np.linspace(0, linear_window-1, linear_window)
            #     time_array_2 = signed_max_delta*np.linspace(linear_window-1, 0, linear_window)
             
                
             for rand_idx in rand_idxs: 

                 leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+cluster_window]+=bias
                
                # leader_attack_traj[attack_ip].iloc[rand_idx:rand_idx+linear_window]+=time_array_1
                # leader_attack_traj[attack_ip].iloc[rand_idx+linear_window: rand_idx+linear_window+constant_window]+=bias               
                # leader_attack_traj[attack_ip].iloc[rand_idx+linear_window+constant_window: rand_idx+cluster_window]+=time_array_2
                
                
        
    elif bias_type == 'linear':
        if np.abs(bias) > max_delta:
            if bias>0:
                bias = max_delta
            else:
                bias = -max_delta
            
        if freq_type == 'continuous':
            time_array = bias*np.linspace(0, np.sum(stealth_mask) -1, int(np.sum(stealth_mask)))
            leader_attack_traj[attack_ip].iloc[start:end]+=time_array 
        elif freq_type == 'cluster':
            # n = int((max_delta * cluster_window)/(np.abs(bias) + max_delta))
            # time_array_1 = bias*np.linspace(0, n-1, n)
            # time_array_2 = ((bias*n)/(cluster_window- n))*np.linspace(cluster_window-n-1,0,cluster_window-n)
            # for rand_idx in rand_idxs:
            #     leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+n]+=time_array_1
            #     leader_attack_traj[attack_ip].iloc[rand_idx+n: rand_idx+cluster_window]+=time_array_2
            time_array = bias*np.linspace(0, cluster_window-1, cluster_window) 

            for rand_idx in rand_idxs: 

                leader_attack_traj[attack_ip].iloc[rand_idx: rand_idx+cluster_window]+=time_array
    
    
    elif bias_type == 'sinusoidal':
        if sin_freq > max_sin_freq:
            sin_freq = max_sin_freq
        time_array = np.arange(0, len(stealth_mask[stealth_mask==1])/100, 0.01)
        sin_bias = bias*np.sin(time_array*sin_freq)
        leader_attack_traj[attack_ip].loc[stealth_mask==1] = leader_attack_traj[attack_ip].loc[stealth_mask==1] + sin_bias[:np.count_nonzero(stealth_mask==1)]
    else:
        print('Unknown bias_type')
       
    leader_attack_traj.reset_index(inplace=True, drop = True)
    #leader_attack_traj = Clip_Params(lead_traj = leader_attack_traj.copy())
    
    #########################################
    # Corrupting the secondary input collusively
    #########################################
    if secondary_attack_ip == "Ego_Vel":
        if freq_type == 'continuous':
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            v_array = np.zeros(len(lead_traj))
            v_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            v_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                v_array[i] = v_array[i-1] + a_array[idx-1]*dT_array[idx-1]
            leader_attack_traj["Ego_Vel"] = v_array
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                v_array = np.zeros(len(a_array))
                v_array[0] = leader_attack_traj['Ego_Vel'].iloc[rand_idx+shift]
                for i in np.arange(1, len(a_array)):
                    v_array[i] = v_array[i-1] + a_array[i-1]*dT_array[i-1]
                leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window] = v_array
                
    elif secondary_attack_ip == "Ego_Pos":
        if freq_type == 'continuous':
            # u_array = np.zeros(len(lead_traj))
            # u_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            # u_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            # s_array = np.zeros(len(lead_traj))
            # s_array[0:start+shift+1] = u_array[0:start+shift+1]*dT_array[0:start+shift+1] + 0.5*a_array[0:start+shift+1]*(dT_array[0:start+shift+1]**2)
            u_array = leader_attack_traj["Ego_Vel"].iloc[start+shift+1:end].values
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
            pos_array = np.zeros(len(lead_traj))
            pos_array[0:start+shift+1] = leader_attack_traj['Ego_Pos'].iloc[0:start+shift+1].values
            pos_array[end:] = leader_attack_traj['Ego_Pos'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                # u_array[i] = u_array[i-1] + a_array[idx-1]*dT_array[idx-1]
                # s = u_array[i-1]*dT_array[idx-1] + 0.5*a_array[idx-1]*(dT_array[idx-1]**2)
                pos_array[i] = pos_array[i-1] + s_array[idx-1]
            leader_attack_traj["Ego_Pos"] = pos_array
            # leader_attack_traj["Ego_Pos"].iloc[start+shift+1:end+1] = pos_array
            
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                u_array = leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
                pos_array = np.zeros(len(a_array))
                pos_array[0] = leader_attack_traj['Ego_Pos'].iloc[rand_idx+shift]
                for i in np.arange(1, len(pos_array)):
                    # u_array[i] = u_array[i-1] + a_array[i-1]*dT_array[i-1]
                    # s = u_array[i-1]*dT_array[i-1] + 0.5*a_array[i-1]*(dT_array[i-1]**2)                    
                    pos_array[i] = pos_array[i-1] + s_array[i-1]
                leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift:rand_idx+shift+cluster_window] = pos_array   


    if tertiary_attack_ip == "Ego_Vel":
        if freq_type == 'continuous':
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            v_array = np.zeros(len(lead_traj))
            v_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            v_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                v_array[i] = v_array[i-1] + a_array[idx-1]*dT_array[idx-1]
            leader_attack_traj["Ego_Vel"] = v_array
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window].values
                v_array = np.zeros(len(a_array))
                v_array[0] = leader_attack_traj['Ego_Vel'].iloc[rand_idx+shift]
                for i in np.arange(1, len(a_array)):
                    v_array[i] = v_array[i-1] + a_array[i-1]*dT_array[i-1]
                leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift+1:rand_idx+shift+cluster_window] = v_array
                
    elif tertiary_attack_ip == "Ego_Pos":
        if freq_type == 'continuous':
            # u_array = np.zeros(len(lead_traj))
            # u_array[0:start+shift+1] = leader_attack_traj['Ego_Vel'].iloc[0:start+shift+1].values
            # u_array[end:] = leader_attack_traj['Ego_Vel'].iloc[end:].values
            # s_array = np.zeros(len(lead_traj))
            # s_array[0:start+shift+1] = u_array[0:start+shift+1]*dT_array[0:start+shift+1] + 0.5*a_array[0:start+shift+1]*(dT_array[0:start+shift+1]**2)
            u_array = leader_attack_traj["Ego_Vel"].iloc[start+shift+1:end].values
            a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift+1:end].values
            dT_array = leader_attack_traj["dT"].iloc[start+shift+1:end].values
            s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
            pos_array = np.zeros(len(lead_traj))
            pos_array[0:start+shift+1] = leader_attack_traj['Ego_Pos'].iloc[0:start+shift+1].values
            pos_array[end:] = leader_attack_traj['Ego_Pos'].iloc[end:].values
            for i in np.arange(start+shift+1 , end):
                idx = i - (start+shift)
                # u_array[i] = u_array[i-1] + a_array[idx-1]*dT_array[idx-1]
                # s = u_array[i-1]*dT_array[idx-1] + 0.5*a_array[idx-1]*(dT_array[idx-1]**2)
                pos_array[i] = pos_array[i-1] + s_array[idx-1]
            leader_attack_traj["Ego_Pos"] = pos_array
            # leader_attack_traj["Ego_Pos"].iloc[start+shift+1:end+1] = pos_array
            
        elif freq_type == 'cluster':
            for rand_idx in rand_idxs:
                u_array = leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift:rand_idx+shift+cluster_window].values
                s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
                pos_array = np.zeros(len(a_array))
                pos_array[0] = leader_attack_traj['Ego_Pos'].iloc[rand_idx+shift]
                for i in np.arange(1, len(pos_array)):
                    # u_array[i] = u_array[i-1] + a_array[i-1]*dT_array[i-1]
                    # s = u_array[i-1]*dT_array[i-1] + 0.5*a_array[i-1]*(dT_array[i-1]**2)                    
                    pos_array[i] = pos_array[i-1] + s_array[i-1]
                leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift:rand_idx+shift+cluster_window] = pos_array
    # elif secondary_attack_ip == "Ego_Pos":
    #     if freq_type == 'continuous':
    #         u_array = leader_attack_traj["Ego_Vel"].iloc[start+shift-1:end+shift-1]
    #         a_array = leader_attack_traj["Ego_Acc"].iloc[start+shift-1:end+shift-1]
    #         dT_array = leader_attack_traj["dT"].iloc[start+shift-1:end+shift-1]
    #         s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
    #         leader_attack_traj["Ego_Pos"].iloc[start+shift:end+shift] = leader_attack_traj["Ego_Pos"].iloc[start+shift-1:end+shift-1] + s_array # pos(t) = pos(t-1) + s; s= ut+0.5at^2 
    #     elif freq_type == 'cluster':
    #         for rand_idx in rand_idxs:
    #             u_array = leader_attack_traj["Ego_Vel"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             a_array = leader_attack_traj["Ego_Acc"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             dT_array = leader_attack_traj["dT"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1]
    #             s_array = u_array*dT_array + 0.5*a_array*(dT_array**2)
    #             leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift:rand_idx+shift+cluster_window] = leader_attack_traj["Ego_Pos"].iloc[rand_idx+shift-1:rand_idx+shift+cluster_window-1] + s_array # pos(t) = pos(t-1) + s; s= ut+0.5at^2       
        
        
    leader_attack_traj.reset_index(inplace=True, drop = True)
    leader_attack_traj = Clip_Params(lead_traj = leader_attack_traj.copy())
    
    
    return leader_attack_traj


def Clip_Params(lead_traj,
                min_bounds = None,
                max_bounds = None):
    
    if min_bounds is None:
        min_bounds = {}
        min_bounds['Acc'] = -8.0
        min_bounds['Vel'] = 0.0
    if max_bounds is None:
        max_bounds ={}
        max_bounds['Acc'] = 8.0
        max_bounds['Vel'] = 50.0
    
    lead_traj['Ego_Acc'] = np.clip(lead_traj['Ego_Acc'].values, min_bounds['Acc'], max_bounds['Acc'])
    lead_traj['Ego_Vel'] = np.clip(lead_traj['Ego_Vel'].values, min_bounds['Vel'], max_bounds['Vel'])
    lead_traj['Ego_Pos'].loc[lead_traj['Ego_Pos']<0] = 0

    return lead_traj
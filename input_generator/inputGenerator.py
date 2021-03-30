#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 18:29:07 2021

@author: marie
"""

import numpy as np
import os
import datetime
import random
import pandas as pd
import uuid 
import matplotlib.pyplot as plt
import scipy.stats as stats
import time
from sklearn.utils import shuffle
from configparser import ConfigParser
import json
import os
import argparse
import sys

print_in_terminal=False

##############################################################################
############################ Load Config######################################
##############################################################################

def generate(config_path="parking_10lanes/config_script.txt", show_plots=None, congestion_coef=None):

    if os.path.exists(config_path):
        parser = ConfigParser()
        parser.read(config_path)
    else :
        if print_in_terminal:
            print("invalid path for configuration file")
        sys.exit()

    if print_in_terminal:
        print("-----LOAD DATA-----")

    ################## paths to save
    path_to_save = parser.get('paths', 'path_to_save')
    mvts_path = path_to_save + parser.get('paths', 'mvts_fileName')

    try:
        if os.path.exists(path_to_save) == False :
            os.mkdir(path_to_save)
    except :
        if print_in_terminal:
            print("invalid path to save files")
        sys.exit()
        
    ##################simulation data
    try :
        start_date = parser.get('simulation_parameters', 'start_date')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = parser.get('simulation_parameters', 'end_date')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')    
        if(end_date <= start_date):
            print("invalid simulation dates")
            sys.exit()
    except :
        print("invalid simulation dates")
        sys.exit()
    
    if print_in_terminal:
        print("Simulation of daily movements from " + str(start_date) + " to " + str(end_date))

    simulation_duration = int((end_date - start_date).days)

    if show_plots is None:
        show_plots = parser.get('simulation_parameters', 'show_plots', fallback = True) == "True"
        
    control_capacity = parser.get('simulation_parameters', 'control_capacity', fallback = True) == "True"

    if print_in_terminal:
        print("Show plots: " + str(show_plots))
        print("Control capacity: " + str(show_plots))

    #time to find entrances/exits number with respect to capacity
    timeout = int(parser.get('simulation_parameters', 'timeout', fallback = 300))

    # Congestion control
    #multiplicative coef of entrances/exits mean
    if congestion_coef is None:
        congestion_coef = float(parser.get('simulation_parameters', 'congestion_coef', fallback = 1.0)) 

    if print_in_terminal:
        print("Congestion coefficient: " + str(congestion_coef))

    days_without_exits = float(parser.get('simulation_parameters', 'n_days_without_exits', fallback = 1)) 

    ################## Parking data

    #be carefull to set a feasable max_operations_per_day
    #ie concordant with maxVehiclesPerDay so that there is always a way to find feasable hours
    max_operations_per_hour = int(parser.get('parking_rules', 'max_operations_per_hour', fallback = 100000))  

    min_movements_per_day = json.loads(parser.get('parking_rules', 'min_movements_per_day', fallback = "[0, 0, 0, 0, 0, 0, 0]"))
    max_movements_per_day = json.loads(parser.get('parking_rules', 'max_movements_per_day', fallback = "[100000, 100000, 100000, 100000, 100000, 100000, 100000]"))
    #Site capacity
    max_vehicles_on_site = int(parser.get('parking_rules', 'max_vehicles_on_site', fallback = 100000)) 
    if print_in_terminal:
        print("Site capacity: " + str(max_vehicles_on_site))

    min_stay_duration = int(parser.get('parking_rules', 'min_stay_duration', fallback = 1))
    max_stay_duration = int(parser.get('parking_rules', 'max_stay_duration', fallback = 100))

    ##############################################################################
    ################################ PARKING STATS ###############################
    ##############################################################################

    hours = np.arange(0,24)
    days = np.arange(0,7)
    DAYS = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

    ######################################STAY DURATIONS
    stay_duration_values = np.arange(min_stay_duration, max_stay_duration +1)
    stay_duration_probabilities = np.zeros(max_stay_duration - min_stay_duration +1)

    #Initialize with mixed distribution :
    #truncated Poisson distributions + uniform (otherwise probabilities of long stay are too low)

    # TODO update later with real data 
    # TODO may be use a distribution conditionnaly to deposit weekday ? 
    mean_stay_duration = int(parser.get('parking_stats', 'mean_stay_duration', fallback = 7)) - min_stay_duration
    min_proba = float(0.20/(simulation_duration+1))
    normalizationCoef = 1-stats.poisson.pmf(max_stay_duration - min_stay_duration + 1, mean_stay_duration) + min_proba*(max_stay_duration - min_stay_duration + 1)
    for i in range(max_stay_duration  - min_stay_duration +1):
        stay_duration_probabilities[i] = (stats.poisson.pmf(i, mean_stay_duration) + min_proba)/normalizationCoef

    if round(sum(stay_duration_probabilities),2) != 1 :
        print("stayDurationProbabilitiesdon't sum to 1")

    if show_plots :
        plt.bar(stay_duration_values, stay_duration_probabilities)
        plt.title("Stay Duration probabilities")
        plt.show()

    ############################# TOTAL ENTRANCES AND EXITS DISTRIBUTIONS PER DAY
    #use gaussian, set mu and sigma per day here
    #Adjust saturation by changing these values

    mu_entrances = congestion_coef * np.asarray(json.loads(parser.get('parking_stats', 'mu_entrances')))
    sigma_entrances = congestion_coef * np.asarray(json.loads(parser.get('parking_stats', 'sigma_entrances')))

    mu_exits = congestion_coef * np.asarray(json.loads(parser.get('parking_stats', 'mu_exits')))
    sigma_exits = congestion_coef * np.asarray(json.loads(parser.get('parking_stats', 'sigma_exits')))

    if show_plots :
        x = np.linspace(mu_entrances[6] - 3*sigma_entrances[6] , mu_entrances[6]  + 3*sigma_entrances[6] , 100)
        plt.plot(x, stats.norm.pdf(x, mu_entrances[0] , sigma_entrances[0] ))
        plt.title("Entrances distribution on saturday")
        plt.show()
        
        x = np.linspace(mu_entrances[3] - 3*sigma_entrances[3] , mu_entrances[3]  + 3*sigma_entrances[3] , 100)
        plt.plot(x, stats.norm.pdf(x, mu_entrances[3] , sigma_entrances[3] ))
        plt.title("Entrances distribution on wednesday")
        plt.show()


    ###################################### ENTRANCES AND EXITS DISTRIBUTIONS
    #Deposit distributions
    #Number of deposit per day + distribution per hour
    #10% 0 à 6h, 42% 6h à 12h, 28% de 12h à 18h, 20% 18h à 24h
    #better to calibrate on real data
    entrances_dist_per_hour = np.asarray(json.loads(parser.get('parking_stats', 'entrances_dist_per_hour')))

    if round(sum(entrances_dist_per_hour),2) != 1 :
        print("entranceDistributionPerHour don't sum to 1")

    #Retrievals distributions
    exits_dist_per_hour = np.asarray(json.loads(parser.get('parking_stats', 'entrances_dist_per_hour')))

    if round(sum(exits_dist_per_hour),2) != 1 :
        print("exitDistributionPerHour don't sum to 1")


    if show_plots :   
        plt.bar(hours, entrances_dist_per_hour )
        plt.title("Entrances per hour probabilitiess")
        plt.show()
        
        plt.bar(hours, exits_dist_per_hour)
        plt.title("Exit per hour probabilitiess")
        plt.show()
        

    ##############################################################################
    ###################### Generate Movements & events ###########################
    ##############################################################################
    if print_in_terminal:
        print("-----CREATE BOOKINGS-----")
    ################## number of movements per day 
        
    #create data frame to export 
    mvts = pd.DataFrame(columns = ["INCOMING_FOR_DEPOSIT","SCAN_FOR_RETRIEVAL","SR_BOOKING_UUID"])

    columns = ["Date", "Deposits", "Retrievals", "Saturation", "theoric_retrievals"]
    for h in hours :
        columns.append(str(h) + "h")

    #control parking state day by day
    parking_state = pd.DataFrame(index = np.arange(simulation_duration +2), columns = columns)
    #index 0 is initial state (before start_date")
    #index simulation_duration+2 is final state (after end_date")
    parking_state.loc[0,"Date"] = str(start_date - datetime.timedelta(1))
    parking_state.loc[simulation_duration+2 ,"Date"] = str(end_date + datetime.timedelta(1))
    parking_state[["Deposits"]] = 0
    parking_state[["Retrievals"]] = 0
    parking_state[["theoric_retrievals"]] = 0
    parking_state[["Saturation"]] = 0
    for h in hours :
        parking_state[[str(h)+"h"]] = 0

    #Initialize parking State by computing expected deposits and retrievals and check for parking saturation
    #compute saturation : check that there are never more vehicles on site than the parking capacity

    for n in range(simulation_duration +1):    
        date = start_date + datetime.timedelta(n)
        weekday = date.weekday()
        parking_state.loc[n+1, "Date"] = str(date)
        
        #TODO: to improve
        #we are testing that saturation + arrivals of the day + exits < max
        test = False
        nb_entrances = 0
        nb_exits = 0
        limit_time =  time.time() + timeout
        while test == False and  time.time() < limit_time:
            test = True
            #get a random number of entrances during the day
            if max_movements_per_day[weekday] > 0 :
                nb_entrances = int(random.normalvariate (mu_entrances[weekday], sigma_entrances[weekday]))
                while nb_entrances < min_movements_per_day[weekday] or nb_entrances > max_movements_per_day[weekday] :
                    nb_entrances = int(random.normalvariate (mu_entrances[weekday], sigma_entrances[weekday]))
                
                nb_exits = int(random.normalvariate (mu_exits[weekday], sigma_exits[weekday]))
                while nb_exits < min_movements_per_day[weekday] or nb_exits > max_movements_per_day[weekday] :
                    nb_exits= int(random.normalvariate (mu_exits[weekday], sigma_exits[weekday]))
                    
                # ugly hack to avoid impossible restitution during first days
                if n < days_without_exits:
                    nb_exits = 0
                    #no entrances if site is already saturated
                    if parking_state.loc[n, "Saturation"] >= max_vehicles_on_site - min_movements_per_day[weekday] - 1 :
                        nb_entrances = 0
                
                #not really precise ! it's possible to generate all movements 
                # and then verify and add/delete movements to fit with wanted saturation level
                if parking_state.loc[n, "Saturation"] +  nb_entrances - nb_exits > max_vehicles_on_site :
                    test = False
                    
                if nb_entrances + nb_exits > max_movements_per_day[weekday] :
                    test = False
            else :
                nb_entrances = 0
                nb_exits = 0
        if test == False :
            print("Can't find a feasable scenario for day " + str(n))
        
        parking_state.loc[n+1,"Deposits"] = nb_entrances 
        parking_state.loc[n+1,"theoric_retrievals"] = nb_exits
        parking_state.loc[n+1, "Saturation"] = parking_state.loc[n, "Saturation"] - parking_state.loc[n+1,"theoric_retrievals"]  +  parking_state.loc[n+1,"Deposits"]          

            
            

    ################## list of movements for each day

    # iterate on every day of the simulation period
    # simulate a number of deposits and a number of retrievals for the day
    # start by creating entrance movements and save their corresponding retrieval movement
    # generate exits to fit with simulated amount of exits on the day
    # save parking state at the end of each day 



    for n in range(simulation_duration +1):
        date = start_date + datetime.timedelta(n)
        weekday = date.weekday()
        nb_entrances = parking_state.loc[n+1,"Deposits"]     
        
        #granularity is in seconds - may be minutes are enough
        #granularity can have an impact on order/robot assignment (?)
        for i in range(nb_entrances):
            #get random entrance hour
            entrance_hour = np.random.choice(hours, size = 1, p = entrances_dist_per_hour)[0]
            while parking_state.loc[n+1, str(entrance_hour) + "h"] >= max_operations_per_hour :
                entrance_hour = np.random.choice(hours, size = 1, p = entrances_dist_per_hour)[0]
            entrance_date = date + datetime.timedelta(seconds = random.randint(entrance_hour * 3600, entrance_hour * 3600 + 3599))    
            
            #get booking duration
            #duration have to respect total amount of expected retrievals
            booking_duration = np.random.choice(stay_duration_values, size = 1, p=stay_duration_probabilities)[0] 
            while parking_state.loc[min(n+1+booking_duration, simulation_duration+2), "Retrievals"] >= parking_state.loc[min(n+1+booking_duration, simulation_duration+2), "theoric_retrievals"] and n+1+booking_duration <= simulation_duration+1: 
                booking_duration = np.random.choice(stay_duration_values, size = 1, p=stay_duration_probabilities)[0] 
            
            exit_date_index = min(n+1+booking_duration, simulation_duration+2)
            
            #get exit date with random hour
            exit_date = date + datetime.timedelta(days = float(booking_duration))
            exit_hour = np.random.choice(hours, size = 1, p = exits_dist_per_hour)[0]
            while parking_state.loc[exit_date_index, str(exit_hour) + "h"] >= max_operations_per_hour and exit_date_index < simulation_duration +2:
                exit_hour = np.random.choice(hours, size = 1, p = exits_dist_per_hour)[0]
            exit_date += datetime.timedelta(seconds = random.randint(exit_hour * 3600, exit_hour * 3600 + 3599))
            
            #update parking_state
            parking_state.loc[n+1, str(entrance_hour) + "h"] +=1
            parking_state.loc[exit_date_index, str(exit_hour) + "h"] +=1
            parking_state.loc[exit_date_index, "Retrievals"] +=1
            #create new booking
            sr_booking = str(uuid.uuid4())
            mvts = mvts.append({"SR_BOOKING_UUID" : sr_booking,"SCAN_FOR_RETRIEVAL" : str(exit_date.isoformat())+"Z", "INCOMING_FOR_DEPOSIT" : str(entrance_date.isoformat())+"Z"}, ignore_index=True)        
        
        #update saturation
        parking_state.loc[n+1, "Saturation"] = parking_state.loc[n, "Saturation"] - parking_state.loc[n+1,"Retrievals"]  +  parking_state.loc[n+1,"Deposits"]          



    ##############################################################################
    ######################## Plots on created scenario ###########################
    ##############################################################################

    if show_plots :
        #parking saturation
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
        axes[0].bar(parking_state.index, parking_state['Saturation'])
        axes[0].hlines( max_vehicles_on_site, 0, parking_state.shape[0], linestyles = 'dashed', colors = "red")
        axes[0].set_title("parking saturation")
        
        axes[1].bar(parking_state.index, parking_state['Deposits'])
        axes[1].bar(parking_state.index, -parking_state['Retrievals'])
        axes[1].set_title("daily movements")
        fig.show()
        
        
        # exemple of one day distribution per hour
        random_day = datetime.datetime.strptime(np.random.choice(parking_state[parking_state.Deposits > 0]['Date']), '%Y-%m-%d %H:%M:%S') 
        deposits = np.zeros(24)
        retrievals = np.zeros(24)
        
        for ind, row in mvts.iterrows():
            depo = datetime.datetime.strptime(row['INCOMING_FOR_DEPOSIT'], '%Y-%m-%dT%H:%M:%SZ')
            retr = datetime.datetime.strptime(row['SCAN_FOR_RETRIEVAL'], '%Y-%m-%dT%H:%M:%SZ')
            
            if depo > random_day and depo < random_day + datetime.timedelta(1) :
                deposits[int(depo.hour)]+=1
            if retr > random_day and retr < random_day + datetime.timedelta(1) :
                retrievals[int(retr.hour)]+=1       
        
        fig, ax = plt.subplots()        
        ax.bar(hours, deposits)
        ax.bar(hours, - retrievals)
        ax.set_title("Movements for day "+ str(random_day.day) + "/" + str(random_day.month) + "/" +str(random_day.year))
        fig.show()
        
                        
    ##############################################################################
    ############################# Save Files #####################################
    ##############################################################################

    if print_in_terminal:
        print("-----SAVE FILES-----")

    #save movements.csv and events.csv
    mvts.to_csv(mvts_path, index = False)

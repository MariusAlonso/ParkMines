
import numpy as np
import datetime
import random
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from sklearn.utils import shuffle

# En jours
mu_deposit_order = 2
sigma_deposit_order = 1

mu_retrieval_order = 12
sigma_retrieval_order = 6

mu_stay_duration = 10
sigma_stay_duration = 10

# En nb de véhicules quotidiens
mu_entrances = [15, 10, 10, 10, 10, 10, 15]
sigma_entrances = [10, 5, 5, 5, 5, 10, 10]


entrances_dist_per_hour = [0.01, 0.00, 0.00, 0.00, 0.02, 0.06, 
                                        0.08, 0.12, 0.09, 0.06, 0.05, 0.03,
                                        0.02, 0.02, 0.03, 0.05 ,0.07 ,0.09,
                                        0.10, 0.04, 0.03, 0.01, 0.01, 0.01]

exits_dist_per_hour = [0.01, 0.00, 0.00, 0.00, 0.03, 0.06, 
                                    0.10, 0.05, 0.03, 0.01, 0.01, 0.01,
                                        0.08, 0.11, 0.09, 0.06, 0.05, 0.04,
                                        0.03, 0.03, 0.04, 0.07 ,0.07 ,0.02]

def random_hour(typ):
    if typ == "entrance":
        distribution = entrances_dist_per_hour
    else:
        distribution = exits_dist_per_hour

    s = 0
    x = random.random()
    for hour, weight in enumerate(distribution):
        s += weight
        if x <= s:
            break
    
    return datetime.timedelta(hours=hour)

def generate(flux_density=1, time=datetime.timedelta(days=31), start_date=datetime.datetime(2021, 1, 1, 0, 0, 0, 0)):

    vehicle_id = 0

    mvmts = pd.DataFrame(columns = ["DEPOSIT", "RETRIEVAL", "ID", "ORDER_DEPOSIT", "ORDER_RETRIEVAL"])

    date = start_date

    while date - start_date < time:

        weekday = date.weekday()
        nb_entrances = max(0, int(np.round(flux_density*random.normalvariate(mu_entrances[weekday], sigma_entrances[weekday]))))

        for n in range(nb_entrances):
            
            days_to_retrieval = max(0, int(np.round(random.normalvariate(mu_stay_duration, sigma_stay_duration))))

            while True:
                hour_deposit = random_hour("entrance") + datetime.timedelta(seconds=int(3600*random.random()))
                hour_retrieval = random_hour("exit") + datetime.timedelta(seconds=int(3600*random.random()))
                
                date_deposit = date + hour_deposit
                date_retrieval = date + datetime.timedelta(days=days_to_retrieval) + hour_retrieval
               
                if datetime.timedelta(hours=1) <= date_retrieval - date_deposit:
                    break
            
            seconds_from_order_deposit = max(0, int(86400*random.normalvariate(mu_deposit_order, sigma_deposit_order)))
            date_order_deposit = date_deposit - datetime.timedelta(seconds=seconds_from_order_deposit)

            seconds_from_order_retrieval = min(max(0, int(86400*random.normalvariate(mu_retrieval_order, sigma_retrieval_order))), (date_retrieval - date_order_deposit).total_seconds())
            date_order_retrieval = date_retrieval - datetime.timedelta(seconds=seconds_from_order_retrieval)

            mvmts.loc[vehicle_id, "ORDER_DEPOSIT"] = str(date_order_deposit.isoformat())+"Z"
            mvmts.loc[vehicle_id, "DEPOSIT"] = str(date_deposit.isoformat())+"Z"
            mvmts.loc[vehicle_id, "ORDER_RETRIEVAL"] = str(date_order_retrieval.isoformat())+"Z"
            mvmts.loc[vehicle_id, "RETRIEVAL"] = str(date_retrieval.isoformat())+"Z"
            mvmts.loc[vehicle_id, "ID"] = vehicle_id
            vehicle_id += 1
        
        date += datetime.timedelta(days=1)

    mvmts.to_csv("inputs\\mvmts.csv", index=False)

generate(0.1)




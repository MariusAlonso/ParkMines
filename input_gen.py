
import datetime
import random
import pandas as pd
import time as comptime
import numpy as np
from sklearn.mixture import GaussianMixture
# import matplotlib.pyplot as plt

# En jours
mu_deposit_order = 2
sigma_deposit_order = 1

mu_retrieval_order = 12
sigma_retrieval_order = 6

mu_stay_duration = 10
sigma_stay_duration = 10

# En nb de véhicules quotidiens
mu_entrances = [1.5, 1, 1, 1, 1, 1, 1.5]
sigma_entrances = [1, 0.5, 0.5, 0.5, 0.5, 1, 1]


entrances_dist_per_hour =   [0.01, 0.00, 0.00, 0.00, 0.02, 0.06, 
                            0.08, 0.12, 0.09, 0.06, 0.05, 0.03,
                            0.02, 0.02, 0.03, 0.05 ,0.07 ,0.09,
                            0.10, 0.04, 0.03, 0.01, 0.01, 0.01]

exits_dist_per_hour =   [0.01, 0.00, 0.00, 0.00, 0.03, 0.06, 
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

def generate(vehicles_per_day=5, time=datetime.timedelta(days=31), start_date=datetime.datetime(2021, 1, 1, 0, 0, 0, 0), path="inputs\\mvmts.csv"):
    """
    Génère un stock de véhicules sous un format csv, enregistré dans *path*.
    Dans le stock, un nombre *vehicles_per_day* de véhicules est déposé en moyenne à partir de *start_date*, sur une durée de *time*.
    """
    vehicle_id = 1
    mvmts = pd.DataFrame(columns = ["DEPOSIT", "RETRIEVAL", "ID", "ORDER_DEPOSIT", "ORDER_RETRIEVAL"])
    date = start_date

    gm = GaussianMixture(n_components=7, covariance_type='spherical')
    gm.weights_ = np.array([0.12,0.32,0.125,0.05,0.02,0.005,0.36])
    gm.means_ = np.array([[3.],[7.],[14.],[21.],[28.],[35.],[12.]])
    gm.covariances_ = np.array([3.,1.,1.,1.,1.,1.,30.])

    while date - start_date < time:

        weekday = date.weekday()
        nb_entrances = max(0, int(round(vehicles_per_day*random.normalvariate(mu_entrances[weekday], sigma_entrances[weekday]))))

        for _ in range(nb_entrances):
    
            while True:
                days_to_retrieval = int(np.round(gm.sample()[0]))
                if days_to_retrieval >= 0:
                    break
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
    
    mvmts.to_csv(path)


def generateStock(Vehicle, vehicles_per_day=5, time=datetime.timedelta(days=31), start_date=datetime.datetime(2021, 1, 1, 0, 0, 0, 0)):
    """
    Génère un stock de véhicules, et renvoie une classe Stock.
    Dans le stock, un nombre *vehicles_per_day* de véhicules est déposé en moyenne à partir de *start_date*, sur une durée de *time*.
    """
    date = start_date
    dict_vehicles = {}

    gm = GaussianMixture(n_components=7, covariance_type='spherical')
    gm.weights_ = np.array([0.12,0.32,0.125,0.05,0.02,0.005,0.36])
    gm.means_ = np.array([[3.],[7.],[14.],[21.],[28.],[35.],[12.]])
    gm.covariances_ = np.array([3.,1.,1.,1.,1.,1.,30.])

    while date - start_date < time:

        weekday = date.weekday()
        nb_entrances = max(0, int(round(vehicles_per_day*random.normalvariate(mu_entrances[weekday], sigma_entrances[weekday]))))

        for _ in range(nb_entrances):
    
            while True:
                days_to_retrieval = int(np.round(gm.sample()[0]))
                if days_to_retrieval >= 0:
                    break

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
            
            vehicle = Vehicle(date_deposit, date_retrieval, date_order_deposit, date_order_retrieval)
            dict_vehicles[vehicle.id] = vehicle
        
        date += datetime.timedelta(days=1)
    
    if dict_vehicles:
        return dict_vehicles
    else:
        return generateStock(Vehicle, vehicles_per_day, time, start_date)

if __name__ == "__main__":

    """
    t00 = comptime.time()
    for _ in range(100):
        generate(5)
    print("time to generate 100 csv:", comptime.time()-t00)
    """

    gm = GaussianMixture(n_components=7, covariance_type='spherical')
    gm.weights_ = np.array([0.12,0.32,0.125,0.05,0.02,0.005,0.36])
    gm.means_ = np.array([[3.],[7.],[14.],[21.],[28.],[35.],[12.]])
    gm.covariances_ = np.array([3.,1.,1.,1.,1.,1.,30.])

    res = []
    for _ in range(100000):
        while True:
            days_to_retrieval = int(np.round(gm.sample()[0]))
            if days_to_retrieval >= 0:
                break
        res.append(days_to_retrieval)
    """
    plt.hist(res, bins = range(40), density = True)
    plt.show()
    """




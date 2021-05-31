import datetime
from copy import deepcopy
import argparse
from vehicle import Vehicle
import sys
from input_gen import generate

#### récupération du path ####

def getPath():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", nargs='?', default="inputs/mvmts.csv", help="path of the file to load", type=str)
    args = parser.parse_args()
    return args.path

#### import des véhicules à partir d'un fichier texte ####

def importFromFile(path=None):

    Vehicle.next_id = 1

    vehicles_list = []
    if path is None:
        path = getPath()

    with open(path, "r") as vehicles:
        first_line = True

        for line in vehicles:

            # non-traitement de l'en-tête
            if first_line:
                first_line = False
            else:

                vehicle = line.split(",")
                # reformatage des données véhicule

                deposit = vehicle[1]
                retrieval = vehicle[2]

                if len(vehicle) > 2:
                    order_deposit = vehicle[4]
                    order_retrieval = vehicle[5]                   

                # reformatage des dates
                delimiters = [':', 'T', 'Z']
                for delimiter in delimiters:
                    deposit = deposit.replace(delimiter, '-')
                    retrieval = retrieval.replace(delimiter, '-')
                    if len(vehicle) > 2:
                        order_deposit = order_deposit.replace(delimiter, '-')
                        order_retrieval = order_retrieval.replace(delimiter, '-') 
                
                deposit = deposit.split('-')[:-1]
                retrieval = retrieval.split('-')[:-1]
                order_deposit = order_deposit.split('-')[:-1]
                order_retrieval = order_retrieval.split('-')[:-1]

                # conversion au format datetime
                deposit = datetime.datetime(*(int(item) for item in deposit))
                retrieval = datetime.datetime(*(int(item) for item in retrieval))
                order_deposit = datetime.datetime(*(int(item) for item in order_deposit))
                order_retrieval = datetime.datetime(*(int(item) for item in order_retrieval))

                vehicles_list.append(Vehicle(deposit, retrieval, order_deposit, order_retrieval))

    return vehicles_list
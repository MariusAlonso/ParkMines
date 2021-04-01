import datetime
from copy import deepcopy
import argparse
from vehicle import Vehicle
import sys
from input_gen import generate

#path = "inputs/movements.csv"

#### récupération du path ####

def getPath():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", nargs='?', default="inputs/mvmts.csv", help="path of the file to load", type=str)
    args = parser.parse_args()
    return args.path

#### import des véhicules à partir d'un fichier texte ####

def importFromFile(congestion_coeff=1.):

    movements_list = []
    path = getPath()

    generate(congestion_coeff)

    with open(path, "r") as movements:
        first_line = True

        for line in movements:

            # non-traitement de l'en-tête
            if first_line:
                first_line = False
            else:

                movement = line.split(",")
                # reformatage des données véhicule

                deposit = movement[0]
                retrieval = movement[1]

                if len(movement) > 2:
                    order_deposit = movement[3]
                    order_retrieval = movement[4]                   

                # reformatage des dates
                delimiters = [':', 'T', 'Z']
                for delimiter in delimiters:
                    deposit = deposit.replace(delimiter, '-')
                    retrieval = retrieval.replace(delimiter, '-')
                    if len(movement) > 2:
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

                movements_list.append(Vehicle(deposit, retrieval, order_deposit, order_retrieval))

    return movements_list
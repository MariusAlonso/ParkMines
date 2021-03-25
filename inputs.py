import datetime
from copy import deepcopy
import argparse
from vehicle import Vehicle
import sys
from input_generator.inputGenerator import generate

#path = "inputs/movements.csv"

#### récupération du path ####

def getPath():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", nargs='?', default="inputs/movements.csv", help="path of the file to load", type=str)
    args = parser.parse_args()
    return args.path

#### import des véhicules à partir d'un fichier texte ####

def generateMovements(congestion_coeff):

    with open("input_generator\parking_10lanes\config_script.txt", "r") as config_base:
        with open("input_generator\config_parkmines.txt", "w") as config:
            for line in config_base:
                line.strip()
                if line[:15] == "congestion_coef":
                    line = line[:18] + str(congestion_coeff)
                """
                if line[:20] == "max_vehicles_on_site":
                    line = line[:23] + str(int(congestion_coeff*int(line[23:])))
                if line[:23] == "max_operations_per_hour":
                    line = line[:26] + str(int(congestion_coeff*int(line[26:])))
                """
                print(line, file=config)
        
    generate("input_generator/config_parkmines.txt", False)

def importFromFile():

    movements_list = []
    path = getPath()

    generateMovements(1.0)

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
                # booking_id non utilisé dans la suite
                booking_id = movement[2].strip()

                # reformatage des dates
                delimiters = [':', 'T', 'Z']
                for delimiter in delimiters:
                    deposit = deposit.replace(delimiter, '-')
                    retrieval = retrieval.replace(delimiter, '-')
                
                deposit = deposit.split('-')[:-1]
                retrieval = retrieval.split('-')[:-1]

                # conversion au format datetime
                deposit = datetime.datetime(*(int(item) for item in deposit))
                retrieval = datetime.datetime(*(int(item) for item in retrieval))
                order_deposit = deepcopy(deposit)
                order_retrieval = deepcopy(retrieval)

                movements_list.append(Vehicle(deposit, retrieval, order_deposit, order_retrieval))

    return movements_list
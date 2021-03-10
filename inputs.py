import datetime
from copy import deepcopy
import argparse
from vehicle import Vehicle
import sys

path = "inputs/movements.csv"

#### récupération du path ####

def get_path():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", nargs='?', default="inputs/movements.csv", help="path of the file to load", type=str)
    print(sys.argv)
    args = parser.parse_args()
    return args.path

#### import des véhicules à partir d'un fichier texte ####

def import_from_file():

    movements_list = []
    #path = get_path()

    with open(path, "r") as movements:
        first_line = True

        for line in movements:

            #non-traitement de l'en-tête
            if first_line:
                first_line = False
            else:

                movement = line.split(",")
                #reformatage des données véhicule

                deposit = movement[0]
                retrieval = movement[1]
                #booking_id non utilisé dans la suite
                booking_id = movement[2].strip()

                #reformatage des dates
                delimiters = [':', 'T', 'Z']
                for delimiter in delimiters:
                    deposit = deposit.replace(delimiter, '-')
                    retrieval = retrieval.replace(delimiter, '-')
                
                deposit = deposit.split('-')[:-1]
                retrieval = retrieval.split('-')[:-1]

                #conversion au format datetime
                deposit = datetime.datetime(*(int(item) for item in deposit))
                retrieval = datetime.datetime(*(int(item) for item in retrieval))
                order_deposit = deepcopy(deposit)
                order_retrieval = deepcopy(retrieval)

                movements_list.append(Vehicle(deposit, retrieval, order_deposit, order_retrieval))

    return movements_list

print(import_from_file()[0].deposit)
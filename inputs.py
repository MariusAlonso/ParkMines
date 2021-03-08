import datetime as dt
import re

movements_list = []
first_line = True

with open("inputs/movements.csv", "r") as movements:
    for line in movements:

        #non-traitement de l'en-tête
        if first_line:
            first_line = False
        else:

            movement = line.split(",")
            #reformatage des données véhicule
            deposit = movement[0]
            retrieval = movement[1]

            delimiters = [':', 'T', 'Z']
            for delimiter in delimiters:
                deposit = deposit.replace(delimiter, '-')
                retrieval = retrieval.replace(delimiter, '-')
            
            deposit = deposit.split('-')[:-1]
            retrieval = retrieval.split('-')[:-1]

            deposit = dt.datetime(*(int(item) for item in deposit))
            retrieval = dt.datetime(*(int(item) for item in retrieval))
            
            booking_id = movement[2].strip()

            movements_list.append([deposit, retrieval, booking_id])

for item in movements_list[0]:
    print(item)
import matplotlib.pyplot as plt
import datetime
from copy import deepcopy
import numpy as np

path = "inputs/movements.csv"
movements_list = []

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

            movements_list.append(np.array([order_deposit, order_retrieval, deposit, retrieval]))

movements_list = np.array(movements_list)

plt.figure()
plt.plot(np.arange(len(movements_list)), movements_list[:, 0])
plt.plot(np.arange(len(movements_list)), movements_list[:, 1])
plt.plot(np.arange(len(movements_list)), movements_list[:, 2])
plt.plot(np.arange(len(movements_list)), movements_list[:, 3])
plt.show()
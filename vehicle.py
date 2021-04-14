import datetime
import time as comptime
from input_gen import generateStock


class Vehicle():
    next_id = 1
    def __init__(self, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.effective_deposit  =None
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        self.id = self.__class__.next_id
        self.__class__.next_id += 1
        if Vehicle.next_id >= 1000000:
            raise ValueError("La représentation d'un block ne fonctionne que si les ids des véhicules contiennent au plus cinq chiffres")
    
    def __repr__(self):
        return self.id.__repr__()

class Stock():

    def __init__(self, vehicles):
        """
        Construit le dictionnaire self.vehicles associant à un id de véhicule l'objet correspondant
        """
        self.vehicles = {}
        for v in vehicles:
            self.vehicles[v.id] = v
    
    def __len__(self):
        return len(self.vehicles)
   
    def add(self, vehicle):
        self.vehicles[vehicle.id] = vehicle
    
    def remove(self, vehicle):
        del self.vehicles[vehicle.id]

class RandomStock(Stock):

    def __init__(self, vehicles_per_day=5, time=datetime.timedelta(days=31), start_date=datetime.datetime(2021, 1, 1, 0, 0, 0, 0)):
        Vehicle.next_id = 1
        self.vehicles = generateStock(Vehicle, vehicles_per_day, time, start_date)

if __name__ == "__main__":
    t000 = comptime.time()
    for x in range(1000):
        stock = RandomStock(10)
    print("time to generate 1000 random stocks:", comptime.time()-t000)
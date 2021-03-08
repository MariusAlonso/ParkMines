

class Simulation():
    def __init__(self, t0, stock, nb_robots):
        self.nb_robots = nb_robots
        self.events = []
        for v in stock.vehicles.values():
            self.events.append(Event(v, v.order_deposit, "d"))
            self.events.append(Event(v, v.order_retrieval, "r"))
        self.events.sort()

class Event():

    def __init__(self, vehicle, date, typ):
        self.vehicle = vehicle
        self.date = date
        self.typ = typ
    
    def __lt__(self, other):
        return self.date < other.date

class Algorithm():
    def __init__(self):
        pass

class Vehicle():
    def __init__(self, id_vehicle, deposit, retrieval, order_deposit, order_retrieval):
        self.deposit = deposit
        self.retrieval = retrieval
        self.order_deposit = order_deposit
        self.order_retrieval = order_retrieval
        self.id = id_vehicle


class Stock():
    def __init__(self, vehicles):
        self.vehicles = {}
        for v in vehicles:
            self.vehicles[v.id] = v
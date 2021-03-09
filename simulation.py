
import bisect
import random

class Simulation():
    def __init__(self, t0, stock, nb_robots, parking, occupation):
        self.stock = stock
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking
        self.occupation = occupation
        self.events = []
        for v in stock.vehicles.values():
            self.events.append(Event(v, v.order_deposit, True))
            self.events.append(Event(v, v.order_retrieval, False))
        self.events.sort()
    
    def next_event(self):
        self.t = max(self.t, self.events[0].date)
        for event in self.events:
            if event.date <= self.t:
                pass
        algorithm = AlgorithmRandom(self.t, self.stock, self.nb_robots, self.parking, self.occupation)
        algorithm.solve()



class Event():

    def __init__(self, vehicle, date, is_deposit):
        self.vehicle = vehicle
        self.date = date
        self.is_deposit = is_deposit
    
    def __eq__(self, other):
        return self.date == other.date
    
    def __lt__(self, other):
        return self.date < other.date


class Algorithm():
    def __init__(self, t0, stock, nb_robots, parking, occupation):
        self.nb_robots = nb_robots
        self.stock = stock
        self.t0 = t0
        self.parking = parking
        self.occupation = occupation


class AlgorithmRandom(Algorithm):
    
    def solve(self):
        for v in self.stock.vehicles.values():
            if v.deposit <= self.t0:
                while True :
                    rand_block = random.choice(self.parking.blocks)
                    rand_lane = random.choice(rand_block.lanes)
                    #if random.randrange(2):
                    if True : #rand_lane.top_position >= v.length :
                        rand_lane.push_top(v.id)
                        break
                

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
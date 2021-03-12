
import bisect
import random
from vehicle import Vehicle
import heapq
import datetime

class Simulation():

    def __init__(self, t0, stock, nb_robots, parking):
        self.stock = stock
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking

        self.events = []
        for v in self.stock.vehicles.values():
            heapq.heappush(self.events, Event(v, v.order_deposit, True, True))
            heapq.heappush(self.events, Event(v, v.order_retrieval, True, False))
        
        self.algorithm = AlgorithmRandom(self.t, self.stock, self.nb_robots, self.parking, self.events)

        while self.events:
            if self.events[0].date >= self.t:
                break
            self.execute(heapq.heappop(self.events))

    def execute(self, event):
        vehicle = event.vehicle
        if event.is_order:
            if event.is_deposit:
                heapq.heappush(self.events, Event(vehicle, vehicle.deposit, False, True))
            else:
                heapq.heappush(self.events, Event(vehicle, vehicle.retrieval, False, False))
        else:
            if event.is_deposit:
                print(f"Deposit of {vehicle.id}")
                self.algorithm.place(vehicle)
                print(self.parking)
                print("")
            else:
                print(f"Retrieval of {vehicle.id}")
                self.algorithm.pick(vehicle)
                print(self.parking)
                print("")

    def next_event(self, repeat = 1):
        for _ in range(repeat):
            if self.events:
                event = heapq.heappop(self.events)
                self.t = event.date
                self.execute(event)
            else:
                print("THE SIMULATION IS COMPLETED")
                break
        return bool(self.events)
            
    
    def complete(self):
        while self.next_event():
            pass



class Event():

    def __init__(self, vehicle, date, is_order, is_deposit):
        self.vehicle = vehicle
        self.date = date
        self.is_order = is_order
        self.is_deposit = is_deposit
        # self.is_deposit vaut True ssi l'évènement est une entrée de véhicule ou le passage d'une commande d'entrée de véhicule
    
    def __eq__(self, other):
        return self.date == other.date
    
    def __lt__(self, other):
        return self.date < other.date


class Algorithm():

    def __init__(self, t0, stock, nb_robots, parking, events):
        self.nb_robots = nb_robots
        self.stock = stock
        self.t0 = t0
        self.parking = parking
        self.events = events

    def pick(self, vehicle):
        i_block, i_lane, position = self.parking.occupation[vehicle.id]
        lane_vehicle = self.parking.blocks[i_block].lanes[i_lane]
        if lane_vehicle.bottom_access and lane_vehicle.bottom_position - position < position - lane_vehicle.top_position:
            while True:
                moved_vehicle = self.stock.vehicles[lane_vehicle.pop_bottom()]
                print(f"{moved_vehicle} is out of position")
                del self.parking.occupation[moved_vehicle.id]
                if lane_vehicle.bottom_position != None and lane_vehicle.bottom_position - position >= 0:
                    self.place(moved_vehicle, forbidden_access = (lane_vehicle, "bottom"))
                    print(self.parking)
                else:
                    break
        else:
            while True:
                moved_vehicle = self.stock.vehicles[lane_vehicle.pop_top()]
                print(f"{moved_vehicle} is out of position")
                del self.parking.occupation[moved_vehicle.id]
                if lane_vehicle.top_position != None and position - lane_vehicle.top_position >= 0:
                    self.place(moved_vehicle, forbidden_access = (lane_vehicle, "top"))
                    print(self.parking)
                else:
                    break



class AlgorithmRandom(Algorithm):
    
    def place(self, vehicle, forbidden_access = None):
        while True:
            rand_i_block = random.randrange(len(self.parking.blocks))
            rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
            lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
            if random.randrange(2):
                if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "top" == forbidden_access[1]):
                    if lane_chosen.is_top_available():
                        lane_chosen.push_top(vehicle.id)
                        self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.top_position)
                        break
            else:
                if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "bottom" == forbidden_access[1]):
                    if lane_chosen.is_bottom_available():
                        lane_chosen.push_bottom(vehicle.id)
                        self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.bottom_position)
                        break
                                               

class Stock():

    def __init__(self, vehicles):

        self.vehicles = {}
        for v in vehicles:
            self.vehicles[v.id] = v
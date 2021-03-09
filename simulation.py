
import bisect
import random

class Simulation():
    def __init__(self, t0, stock, nb_robots, parking):
        self.stock = stock
        for i, event in enumerate(self.stock.order_events) :
            if event.date >= t0 :
                break
        self.i_order_events = i
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking
    
    def next_event(self):
        """
        self.t = max(self.t, stock.events[0].date)
        for event in self.events:
            if event.date <= self.t:
                pass
        """
        algorithm = AlgorithmRandom(self.t, self.stock, self.nb_robots, self.parking)
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
    def __init__(self, t0, stock, nb_robots, parking):
        self.nb_robots = nb_robots
        self.stock = stock
        self.t0 = t0
        self.parking = parking
    
    def simple_pick_up(self, vehicle):
        pass


class AlgorithmRandom(Algorithm):
    
    def solve(self):
        for v in self.stock.vehicles.values():
            if v.deposit <= self.t0:
                while True :
                    rand_i_block = random.randrange(len(self.parking.blocks))
                    rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
                    lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
                    if random.randrange(2):
                        if True : #rand_lane.top_position >= v.length :
                            lane_chosen.push_top(v.id)
                            self.parking.occupation[v.id] = (rand_i_block, rand_i_lane, lane_chosen.top_position)
                            break
                    else:
                        if True : #lane_chosen.top_position >= v.length :
                            lane_chosen.push_bottom(v.id)
                            self.parking.occupation[v.id] = (rand_i_block, rand_i_lane, lane_chosen.bottom_position)
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
        self.order_events = []
        for v in self.vehicles.values():
            self.order_events.append(Event(v, v.order_deposit, True))
            self.order_events.append(Event(v, v.order_retrieval, False))
        self.order_events.sort()
        self.events = []
        for v in self.vehicles.values():
            self.events.append(Event(v, v.deposit, True))
            self.events.append(Event(v, v.retrieval, False))
        self.events.sort()

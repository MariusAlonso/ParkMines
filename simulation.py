
import bisect
import random
from vehicle import Vehicle

class Simulation():

    def __init__(self, t0, stock, nb_robots, parking):
        self.stock = stock
        for i, event in enumerate(self.stock.order_events):
            if event.date >= t0:
                break
        self.i_order_events = i
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking
    
    def next_event(self):
        algorithm = AlgorithmRandom(self.t, self.stock, self.nb_robots, self.parking)
        algorithm.solve()

        while True:
            self.i_order_events += 1

            if self.i_order_events == len(self.stock.order_events):
                print("END OF THE SIMULATION")
                break

            if self.stock.order_events[self.i_order_events].date > self.t:
                self.t = self.order_events[self.i_order_events].date
                break



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

    def simple_retrieval(self, vehicle):
        i_block, i_lane, positon = self.parking.occupation[vehicle.id]
        lane_vehicle = self.parking.blocks[i_block].lanes[i_lane]
        if lane_vehcle.bottom_position - position > position - lane_vehcle.top_position:
            while lane_vehcle.bottom_position - position >= 0:
                lane_chosen.pop_bottom(vehicle.id)
                del self.parking.occupation[vehicle.id]
        else:
            while position - lane_vehcle.top_position >= 0:
                lane_chosen.pop_top(vehicle.id)
                del self.parking.occupation[vehicle.id]]



class AlgorithmRandom(Algorithm):
    
    def solve(self):

        known_events_i = []
        for i, event in enumerate(self.stock.events):
            if event.is_deposit:
                if self.t0 > event.vehicle.order_deposit:
                    known_events_i.append(i)
            else:
                if self.t0 > event.vehicle.order_retrieval:
                    known_events_i.append(i)              

        ##########################################################################
        for i, event in enumerate(self.stock.events):
            if event.date >= self.t0:
                break
        self.i_events = i

        for j in range(self.i_events):
            vehicle = self.stock.events[j].vehicle
            if vehicle.id not in self.parking.occupation:
                while True:
                    rand_i_block = random.randrange(len(self.parking.blocks))
                    rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
                    lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
                    if random.randrange(2):
                        if True:#lane_chosen.is_top_available():
                            lane_chosen.push_top(vehicle.id)
                            self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.top_position)
                            break
                    else:
                        if True:#lane_chosen.is_bottom_available():
                            lane_chosen.push_bottom(vehicle.id)
                            self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.bottom_position)
                            break
                                               

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

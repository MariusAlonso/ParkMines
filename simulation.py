
import random
from vehicle import Vehicle
import heapq
import datetime

class Simulation():

    def __init__(self, t0, stock, nb_robots, parking, AlgorithmType):
        """
        t0 : date d'initialisation
        """
        self.stock = stock
        self.nb_robots = nb_robots
        self.t = t0
        self.parking = parking

        # Création de la file d'événements : ajout des commandes
        self.events = []
        for v in self.stock.vehicles.values():
            heapq.heappush(self.events, Event(v, v.order_deposit, "order_deposit"))
            heapq.heappush(self.events, Event(v, v.order_retrieval, "order_retrieval"))
        
        self.algorithm = AlgorithmType(self.t, self.stock, self.nb_robots, self.parking, self.events)

        # Exécution de tous les évènements antérieurs à la date d'initialisation
        while self.events:
            if self.events[0].date >= self.t:
                break
            self.execute(heapq.heappop(self.events))

    def execute(self, event):
        vehicle = event.vehicle
        if event.event_type == "order_deposit":
            heapq.heappush(self.events, Event(vehicle, vehicle.deposit, "deposit"))
        
        elif event.event_type == "order_retrieval":
            heapq.heappush(self.events, Event(vehicle, vehicle.retrieval, "retrieval"))

        elif event.event_type == "deposit":
            print(f"Deposit of {vehicle.id}")
            self.algorithm.place(vehicle)
            print(self.parking)
            print("")

        elif event.event_type == "retrieval":
            print(f"Retrieval of {vehicle.id}")
            self.algorithm.pick(vehicle)
            print(self.parking)
            print("")


    def next_event(self, repeat = 1):
        """
        Exécute un nombre d'évènements égal à repeat
        """
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
        """
        Finit la simulation
        """
        try:
            while self.next_event():
                pass
        
        # si un placement n'a pu être mené à bien
        except ValueError:
            break

class Event():

    def __init__(self, vehicle, date, event_type):
        """
        Les valeurs possibles du string event_type sont :
        - 'order_deposit'
        - 'order_retrieval'
        - 'deposit'
        - 'retrieval'
        """
        self.vehicle = vehicle
        self.date = date
        self.event_type = event_type
    
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

        #paramètres liés à la mesure de la performance de l'algorithme
        self.nb_placements = 0

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
    
    def place(self, vehicle, forbidden_access = None, max_iter=1000):
        """
        forbidden_access : tuple (Lane, "top"/"bottom")
        """
        self.nb_placements += 1
        print(f"{self.nb_placements} placements")
        nb_iter = 0
        while nb_iter < max_iter:
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
            if nb_iter == max_iter:
                raise ValueError("le placement n'a pas pu être effectué")
            
                                               

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
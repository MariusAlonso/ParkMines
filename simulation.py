
import random
from vehicle import Vehicle
import heapq
import datetime
from robot import *
import time

class Simulation():

    def __init__(self, t0, stock, robots, parking, AlgorithmType, print_in_terminal=False, display=None):
        """
        t0 : date d'initialisation
        """
        self.stock = stock
        self.robots = robots
        self.t = t0
        self.parking = parking
        self.print_in_terminal = print_in_terminal

        self.before_deposit_delays = []
        self.after_deposit_delays = []
        self.retrieval_delays = []

        self.display = display
        self.time_execution = 0

        # Création de la file d'événements : ajout des commandes
        self.events = []
        for v in self.stock.vehicles.values():
            heapq.heappush(self.events, Event(v, v.order_deposit, "order_deposit"))
            heapq.heappush(self.events, Event(v, v.order_retrieval, "order_retrieval"))

        self.pending_deposits = []
        self.pending_retrievals = []
    
        # Dictionnaire des extrémités de lanes
        self.locked_lanes = {}
        for block_id, block in enumerate(self.parking.blocks):
            for lane_id, lane in enumerate(block.lanes):
                self.locked_lanes[(block_id, lane_id, "top")] = not lane.top_access
                self.locked_lanes[(block_id, lane_id, "bottom")] = not lane.bottom_access
        
        self.algorithm = AlgorithmType(self.t, self.stock, self.robots, self.parking, self.events, self.locked_lanes)

        # Exécution de tous les évènements antérieurs à la date d'initialisation
        while self.events:
            if self.events[0].date >= t0:
                break
            event = heapq.heappop(self.events)
            self.t = event.date
            self.execute(event)

    def execute(self, event):
        if self.print_in_terminal:
            print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nEXECUTION at time {self.t}")
            print("event :", event)
            if not (event.robot is None) and not (event.robot.target is None) and event.event_type != event.robot.target.event_type:
                print("target of the robot:", event.robot.target)
            print("-------------")
            #print([k for k in self.locked_lanes if self.locked_lanes[k]])


        vehicle = event.vehicle
        if event.event_type == "order_deposit":
            heapq.heappush(self.events, Event(vehicle, vehicle.deposit, "deposit"))
        
        elif event.event_type == "order_retrieval":
            heapq.heappush(self.events, Event(vehicle, vehicle.retrieval, "retrieval"))
            time_wake_up = max(self.t, vehicle.retrieval - datetime.timedelta(hours=1))
            heapq.heappush(self.events, Event(vehicle, time_wake_up, "wake_up_robots"))
        
        elif event.event_type == "wake_up_robots":
            self.wake_up_robots()

        elif event.event_type == "deposit":

            lane_id = self.parking.blocks[0].empty_lane()
            if lane_id == "full":
                heapq.heappush(self.pending_deposits, event)
            else:
                self.parking.blocks[0].lanes[lane_id].push(vehicle.id, "top")
                self.parking.occupation[vehicle.id] = (0, lane_id, 0)

                vehicle.effective_deposit = self.t

                # ajout du retard (nul) à la liste des retards au dépôt
                self.before_deposit_delays.append(datetime.timedelta(0, 0, 0, 0, 0, 0))

                self.wake_up_robots()
                
                if self.display:
                    self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"Deposit of {vehicle.id}")
                print(self.parking)
                print("")

        elif event.event_type == "retrieval":
            
            if vehicle.id in self.parking.occupation:
                i_block, i_lane, position = self.parking.occupation[vehicle.id]
                if i_block == 0:
                    self.parking.blocks[0].lanes[i_lane].pop("top")

                    if self.display:
                        self.display.erase_vehicle(vehicle)

                    del self.parking.occupation[event.vehicle.id]

                    if self.print_in_terminal:
                        print(f"Retrieval of {vehicle.id}")
                        print(self.parking)
                        print("")
                else:
                    heapq.heappush(self.pending_retrievals, event)
            else:
                heapq.heappush(self.pending_retrievals, event)


        elif event.event_type == "robot_arrival":

            if vehicle.id not in self.parking.occupation:
                
                event.robot.start_position = event.robot.goal_position
                event.robot.start_time = self.t
                event.robot.goal_time = None
                    
                if self.print_in_terminal:
                    print(f"Robot {event.robot} waits in interface zone")
                    print(self.parking)
                    print("")

            else :

                block_id, lane_id, side = event.robot.goal_position

                moved_vehicle = self.stock.vehicles[self.parking.blocks[block_id].lanes[lane_id].pop(side)]

                if self.display:
                    self.display.erase_vehicle(moved_vehicle)

                del self.parking.occupation[moved_vehicle.id]

                if block_id == 0:
                    # ajout du retard éventuel à la liste des retards au dépôt
                    self.after_deposit_delays.append(self.t - vehicle.effective_deposit)

                if self.print_in_terminal:
                    print(f"Robot {event.robot} loads {moved_vehicle.id}")
                    print(self.parking)
                    print("")

                if block_id == 0:
                    self.parking.blocks[0].nb_places_available += 1
                    if self.pending_deposits:
                        event_deposit = heapq.heappop(self.pending_deposits)
                        self.parking.blocks[0].lanes[lane_id].push(event_deposit.vehicle.id, "top")
                        self.parking.occupation[event_deposit.vehicle.id] = (0, lane_id, 0)

                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - event_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        event_deposit.vehicle.effective_deposit = self.t

                        self.wake_up_robots()
                
                event.robot.start_position = event.robot.goal_position
                event.robot.start_time = self.t

                if event.robot.target.event_type == "retrieval" and moved_vehicle.id == event.robot.target.vehicle.id:
                    i_lane = self.parking.blocks[0].empty_lane()
                    if i_lane != "full":
                        self.locked_lanes[event.robot.goal_position] = False
                        self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                        #On place le vehicule a l'interface
                        event.robot.goal_position = (0, i_lane, "bottom")
                        self.parking.blocks[0].nb_places_available -= 1
                        
                        event.robot.goal_time = self.t + self.parking.travel_time(event.robot.start_position, event.robot.goal_position)
                        heapq.heappush(self.events, Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot))

                    else:
                        self.assign_task(event.robot)
                        self.whistle()
                else:
                    event.robot.goal_position = self.algorithm.place(moved_vehicle, event.robot.goal_position)
                    
                    event.robot.goal_time = self.t + self.parking.travel_time(event.robot.start_position, event.robot.goal_position)
                    heapq.heappush(self.events, Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot))
                


        elif event.event_type == "robot_end_task":

            event.robot.start_position = event.robot.goal_position
            event.robot.start_time = self.t

            
            block_id, lane_id, side = event.robot.start_position
            lane = self.parking.blocks[block_id].lanes[lane_id]
            
            lane.push(vehicle.id, side)
            if side == "top":
                self.parking.occupation[event.vehicle.id] = (block_id, lane_id, lane.top_position)
            else:
                self.parking.occupation[event.vehicle.id] = (block_id, lane_id, lane.bottom_position)

            if self.display:
                self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"{event.robot} places {vehicle.id} ")
                print(self.parking)
                print("")

            if block_id == 0:
                # ajout du retard éventuel à la liste des retards à la sortie
                self.retrieval_delays.append(self.t - event.robot.target.date)
            
                # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                if event.robot.target.date < self.t:
                    self.execute(event.robot.target)
                    self.pending_retrievals.remove(event.robot.target)

            event.robot.target = None
            self.assign_task(event.robot)
            
            self.whistle()



    def next_event(self, repeat = 1):
        """
        Exécute un nombre d'évènements égal à repeat
        """
        for _ in range(repeat):
            if self.events:
                time_start = time.time()
                event = heapq.heappop(self.events)
                self.t = event.date
                self.execute(event)
                self.time_execution += time.time() - time_start
            else:
                if self.print_in_terminal:
                    print("THE SIMULATION IS COMPLETED")
                break
        return bool(self.events)
            
    def complete(self):
        """
        Finit la simulation
        """
        while True:
            try:
                if not self.next_event():
                    break
            
            # si un placement n'a pu être mené à bien
            except ValueError:
                break
        if self.print_in_terminal:
            print(f"Temps d'exécution : {self.time_execution:.2f}s")
    
    def assign_task(self, robot):
        are_available_places_interface = False
        for lane_id, lane in enumerate(self.parking.blocks[0].lanes):
            if not lane.list_vehicles[0] is None:
                vehicle = self.stock.vehicles[lane.list_vehicles[0]]
                if vehicle.order_retrieval > self.t or vehicle.retrieval - self.t > datetime.timedelta(hours=1):
                    robot.start_position = robot.goal_position
                    robot.goal_position = (0, lane_id, "bottom")
                    robot.start_time = self.t

                    robot.goal_time = self.t + self.parking.travel_time((0, lane_id, "bottom"), robot.goal_position)

                    heapq.heappush(self.events, Event(self.stock.vehicles[vehicle.id], robot.goal_time, "robot_arrival", robot))

                    event = Event(self.stock.vehicles[vehicle.id], robot.goal_time, "empty_interface", robot)

                    robot.target = event
                    
                    return event
            else:
                are_available_places_interface = True
        
        event = self.find_unassigned_events(are_available_places_interface)

        if event:
            if self.print_in_terminal:
                print(f" -> event {event} assigned to {robot}")
            block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
            lane_vehicle = self.parking.blocks[block_id].lanes[lane_id]

            if lane_vehicle.bottom_access and lane_vehicle.bottom_position - position < position - lane_vehicle.top_position:
                side = "bottom"
            else:
                side = "top"

            robot.start_position = robot.goal_position
            robot.goal_position = block_id, lane_id, side
            robot.start_time = self.t
            robot.goal_time = self.t + self.parking.travel_time(position, robot.goal_position)

            event.robot = robot
            heapq.heappush(self.events, Event(event.vehicle, robot.goal_time, "robot_arrival", robot))

            robot.target = event

            return event
        

    def find_unassigned_events(self, are_available_places_interface):
        i = 0
        while i < len(self.pending_retrievals):
            event = self.pending_retrievals[i]
            if event.event_type == "retrieval":
                if event.unassigned_tasks == None:
                    if event.vehicle.id in self.parking.occupation:
                        block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                        vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]
                        if vehicle_lane.bottom_access and vehicle_lane.bottom_position - position < position - vehicle_lane.top_position:
                            event.unassigned_tasks = vehicle_lane.bottom_position - position + 1
                            self.locked_lanes[(block_id, lane_id, "bottom")] = True
                        else:
                            event.unassigned_tasks = position - vehicle_lane.top_position + 1
                            self.locked_lanes[(block_id, lane_id, "top")] = True
            if event.unassigned_tasks:
                if event.unassigned_tasks != 1 or are_available_places_interface:                       
                    event.unassigned_tasks -= 1
                    return event
            i += 1
        i = 0
        while i < len(self.events):
            event = self.events[i]
            if event.event_type == "retrieval" and event.date - self.t <= datetime.timedelta(hours=1):
                if event.unassigned_tasks == None:
                    if event.vehicle.id in self.parking.occupation:
                        block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                        vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]
                        if vehicle_lane.bottom_access and vehicle_lane.bottom_position - position < position - vehicle_lane.top_position:
                            event.unassigned_tasks = vehicle_lane.bottom_position - position + 1
                            self.locked_lanes[(block_id, lane_id, "bottom")] = True
                        else:
                            event.unassigned_tasks = position - vehicle_lane.top_position + 1
                            self.locked_lanes[(block_id, lane_id, "top")] = True
            if event.event_type == "retrieval" and event.unassigned_tasks:
                if event.unassigned_tasks != 1 or are_available_places_interface:                       
                    event.unassigned_tasks -= 1
                    return event
            i += 1

    def wake_up_robots(self):
        for robot in self.robots:
            if robot.target == None:
                self.assign_task(robot)
    
    def whistle(self):
        pass
            

    


class Event():

    def __init__(self, vehicle, date, event_type, robot=None, unassigned_tasks=None):
        """
        Les valeurs possibles du string event_type sont :
        - 'order_deposit'
        - 'order_retrieval'
        - 'deposit'
        - 'retrieval'
        - 'robot_arrrival'
        """
        self.vehicle = vehicle
        self.date = date
        self.event_type = event_type
        self.robot = robot
        self.unassigned_tasks = unassigned_tasks
    
    def __bool__(self):
        return True
    
    def __eq__(self, other):
        return (not (other is None)) and self.date == other.date
    
    def __lt__(self, other):
        return self.date < other.date
    
    def __repr__(self):
        return f"{self.event_type} ; due to {self.date} ; vehicle {self.vehicle} ;"


class Algorithm():

    def __init__(self, t0, stock, robots, parking, events, locked_lanes):
        self.robots = robots
        self.stock = stock
        self.t0 = t0
        self.parking = parking
        self.events = events
        self.locked_lanes = locked_lanes

        #paramètres liés à la mesure de la performance de l'algorithme
        self.nb_placements = 0
    """
    def pick(self, vehicle):
        i_block, i_lane, position = self.parking.occupation[vehicle.id]
        lane_vehicle = self.parking.blocks[i_block].lanes[i_lane]
        if lane_vehicle.bottom_access and lane_vehicle.bottom_position - position < position - lane_vehicle.top_position:
            while True:
                moved_vehicle = self.stock.vehicles[lane_vehicle.pop_bottom()]
                del self.parking.occupation[moved_vehicle.id]
                if lane_vehicle.bottom_position != None and lane_vehicle.bottom_position - position >= 0:
                    self.place(moved_vehicle, forbidden_access = (lane_vehicle, "bottom"))
                else:
                    break
        else:
            while True:
                moved_vehicle = self.stock.vehicles[lane_vehicle.pop_top()]
                del self.parking.occupation[moved_vehicle.id]
                if lane_vehicle.top_position != None and position - lane_vehicle.top_position >= 0:
                    self.place(moved_vehicle, forbidden_access = (lane_vehicle, "top"))
                else:
                    break
    """

class AlgorithmRandom(Algorithm):
    
    def place_old(self, vehicle, forbidden_access = None, max_iter=1000):
        """
        forbidden_access : tuple (Lane, "top"/"bottom")
        """
        self.nb_placements += 1
        nb_iter = 0
        while nb_iter < max_iter:
            rand_i_block = random.randrange(1, len(self.parking.blocks))
            rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
            lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
            if random.randrange(2):
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "top")]:
                    #if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "top" == forbidden_access[1]):
                    if lane_chosen.is_top_available():
                        lane_chosen.push_top(vehicle.id)
                        self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.top_position)
                        break
            else:
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "bottom")]:
                    #if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "bottom" == forbidden_access[1]):
                    if lane_chosen.is_bottom_available():
                        lane_chosen.push_bottom(vehicle.id)
                        self.parking.occupation[vehicle.id] = (rand_i_block, rand_i_lane, lane_chosen.bottom_position)
                        break
            nb_iter += 1
            if nb_iter == max_iter:
                raise ValueError("le placement n'a pas pu être effectué")

    def place(self, vehicle, forbidden_access = None, max_iter=1000):
        """
        forbidden_access : tuple (Lane, "top"/"bottom")
        """
        self.nb_placements += 1
        nb_iter = 0
        while nb_iter < max_iter:
            rand_i_block = random.randrange(1, len(self.parking.blocks))
            rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
            lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
            if random.randrange(2):
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "top")]:
                    #if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "top" == forbidden_access[1]):
                    if lane_chosen.is_top_available():
                        return (rand_i_block, rand_i_lane, "top")
            else:
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "bottom")]:
                    #if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "bottom" == forbidden_access[1]):
                    if lane_chosen.is_bottom_available():
                        return (rand_i_block, rand_i_lane, "bottom")
            nb_iter += 1
            if nb_iter == max_iter:
                print("ERREUR DE PLACEMENT")
                print(self.parking)
                print(self.locked_lanes)
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


import random
from vehicle import Vehicle, Stock
import heapq
import datetime
from robot import Robot
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

        self.vehicles_to_retrieve = []
    
        # Dictionnaire des extrémités de lanes
        self.locked_lanes = {}
        for block_id, block in enumerate(self.parking.blocks):
            for lane_id, lane in enumerate(block.lanes):
                self.locked_lanes[(block_id, lane_id, "top")] = int(not lane.top_access)
                self.locked_lanes[(block_id, lane_id, "bottom")] = int(not lane.bottom_access)
        
        self.algorithm = AlgorithmType(self.t, self.stock, self.robots, self.parking, self.events, self.locked_lanes)

        # Exécution de tous les évènements antérieurs à la date d'initialisation
        while self.events:
            if self.events[0].date >= t0:
                break
            event = heapq.heappop(self.events)
            self.t = event.date
            self.execute(event)

    def execute(self, event):
        if self.display:
            self.display.show_robot()
        if self.print_in_terminal:
            print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nEXECUTION at time {self.t}")
            print("event :", event)
            print("-------------")
            for robot in self.robots:
                print(f" - {robot}")
                print(f"doing :", robot.doing)
                print(f"target:", robot.target)
                print(f"vehicle carrying:", robot.vehicle)
                print(f"goal_position:", robot.goal_position)
            print("-------------")
            #print([k for k in self.locked_lanes if self.locked_lanes[k]])


        vehicle = event.vehicle
        if event.event_type == "order_deposit":
            heapq.heappush(self.events, Event(vehicle, vehicle.deposit, "deposit"))
            time_wake_up = max(self.t, vehicle.deposit - datetime.timedelta(hours=0.25))
            heapq.heappush(self.events, Event(vehicle, time_wake_up, "wake_up_robots_deposit"))
          
        elif event.event_type == "order_retrieval":
            event_retrieval = Event(vehicle, vehicle.retrieval, "retrieval")
            heapq.heappush(self.events, event_retrieval)
            time_wake_up = max(self.t, vehicle.retrieval - datetime.timedelta(hours=1))
            heapq.heappush(self.events, Event(vehicle, time_wake_up, "wake_up_robots_retrieval", event_retrieval=event_retrieval))
        
        elif event.event_type == "wake_up_robots_retrieval":

            # Si un robot est en train de transporter un véhicule cible d'un retrieval
            for robot in self.robots:
                if not (robot.vehicle is None) and robot.vehicle.id == event.vehicle.id:
                    i_lane = self.parking.blocks[0].empty_lane()
                    if i_lane != "full":
                        block_id, lane_id, side = robot.goal_position
                        self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                        self.parking.blocks[0].lanes[i_lane].push_reserve("bottom")
                        self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                        #On place le vehicule a l'interface
                        robot.goal_position = (0, i_lane, "bottom")
                        self.parking.blocks[0].nb_places_available -= 1
                        # Calcul du temps de trajet faux
                        robot.goal_time = self.t + self.parking.travel_time(robot.start_position, robot.goal_position)
                        robot.target = event.event_retrieval
                        event.event_retrieval.unassigned_tasks = 0
                        
                        event_end_task = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                        heapq.heappush(self.events, event_end_task)

                        robot.doing.canceled = True
                        robot.doing = event_end_task

            # Si un véhicule cible d'un retrieval est garé sur le parking
            if event.vehicle.id in self.parking.occupation:
                block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                if block_id != 0:
                    vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]
                    
                    if vehicle_lane.bottom_access and vehicle_lane.bottom_position - position < position - vehicle_lane.top_position:
                        side = "bottom"
                        # event.event_retrieval.unassigned_tasks = vehicle_lane.bottom_position - position + 1
                    else:
                        side = "top"
                        # event.event_retrieval.unassigned_tasks = position - vehicle_lane.top_position + 1
                    
                    self.locked_lanes[(block_id, lane_id, side)] += 1

                    # Si un robot voulait placer un véhicule dans la lane et le côté par lequel on veut sortir le véhicule cible du retrieval
                    for robot in self.robots:                           
                        if not (robot.vehicle is None) and robot.goal_position == (block_id, lane_id, side):
                            self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                            robot.goal_position = self.algorithm.place(robot.vehicle)
                            # Calcul du temps de trajet faux
                            robot.goal_time  = self.t + self.parking.travel_time(robot.start_position, robot.goal_position)
                            event_end_task = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                            heapq.heappush(self.events, event_end_task)

                            robot.doing.canceled = True
                            robot.doing = event_end_task

            # Si un robot veut retirer de l'interface un véhicule cible d'un retrieval   
            for robot in self.robots:
                if (not robot.target is None) and robot.target.event_type == "empty_interface" and robot.target.vehicle.id == event.vehicle.id:
                    robot.target = None
                    robot.doing.canceled = True
                    robot.doing = None
                    _, lane_id, _ = robot.goal_position
                    self.parking.blocks[0].targeted[lane_id] = False
                    self.parking.blocks[0].lanes[lane_id].pop_cancel_reserve("bottom")
                    robot.goal_position = robot.start_position
                    self.assign_task(robot)

            self.wake_up_robots()

        elif event.event_type == "wake_up_robots_deposit":
            pass
            # self.wake_up_robots()

        elif event.event_type == "deposit":

            lane_id = self.parking.blocks[0].empty_lane()
            if lane_id == "full":
                heapq.heappush(self.pending_deposits, event)
            else:
                self.parking.blocks[0].lanes[lane_id].push_reserve("top")
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
                i_block, i_lane, _ = self.parking.occupation[vehicle.id]
                if i_block == 0:
                    # Le client récupère son véhicle (seul endroit dans simulation où cela se produit)
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

            if event == event.robot.doing:

                block_id, lane_id, side = event.robot.goal_position

                if vehicle.id not in self.parking.occupation and block_id == 0:
                    
                    event.robot.start_position = event.robot.goal_position
                    event.robot.start_time = self.t
                    event.robot.goal_time = None
                    event.robot.target = None
                    event.robot.doing = None
                        
                    if self.print_in_terminal:
                        print(f"Robot {event.robot} waits in interface zone")
                        print(self.parking)
                        print("")

                else :
                    if side == "top":
                        position = self.parking.blocks[block_id].lanes[lane_id].top_position
                    else:
                        position = self.parking.blocks[block_id].lanes[lane_id].bottom_position
                    moved_vehicle = self.stock.vehicles[self.parking.blocks[block_id].lanes[lane_id].list_vehicles[position]]

                    # Dans le cas où le robot ne peut pas placer dans l'interface le véhicule attendu pour un retrieval
                    if moved_vehicle.order_retrieval <= self.t and moved_vehicle.retrieval - self.t <= datetime.timedelta(hours=1):
                        i_lane = self.parking.blocks[0].empty_lane()
                        if i_lane == "full":
                            self.parking.blocks[block_id].lanes[lane_id].pop_cancel_reserve(side)
                            event.robot.target = None
                            event.robot.doing = None
                            return None                                             

                    if self.display:
                        self.display.erase_vehicle(moved_vehicle)
                    
                    self.parking.blocks[block_id].lanes[lane_id].pop(side)

                    del self.parking.occupation[moved_vehicle.id]
                    event.robot.vehicle = moved_vehicle

                    if block_id == 0:
                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.after_deposit_delays.append(self.t - vehicle.effective_deposit)
                        # la place n'est plus le siège d'un évènement empty_interface
                        self.parking.blocks[0].targeted[lane_id] = False

                    if self.print_in_terminal:
                        print(f"Robot {event.robot} loads {moved_vehicle.id}")
                        print(self.parking)
                        print("")

                    if block_id == 0:
                        self.parking.blocks[0].nb_places_available += 1
                        if self.pending_deposits:
                            event_deposit = heapq.heappop(self.pending_deposits)
                            self.parking.blocks[0].lanes[lane_id].push_reserve("top")
                            self.parking.blocks[0].lanes[lane_id].push(event_deposit.vehicle.id, "top")
                            self.parking.occupation[event_deposit.vehicle.id] = (0, lane_id, 0)

                            # ajout du retard éventuel à la liste des retards au dépôt
                            self.before_deposit_delays.append(self.t - event_deposit.date)
                            # mise à jour de la date de dépôt effectif du véhicule
                            event_deposit.vehicle.effective_deposit = self.t

                            self.wake_up_robots()
                    
                    event.robot.start_position = event.robot.goal_position
                    event.robot.start_time = self.t

                    if moved_vehicle.order_retrieval <= self.t and moved_vehicle.retrieval - self.t <= datetime.timedelta(hours=1):
                        i_lane = self.parking.blocks[0].empty_lane()
                        self.locked_lanes[event.robot.goal_position] -= 1
                        self.parking.blocks[0].lanes[i_lane].push_reserve("bottom")
                        self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                        #On place le vehicule a l'interface
                        event.robot.goal_position = (0, i_lane, "bottom")
                        self.parking.blocks[0].nb_places_available -= 1
                        
                        event.robot.goal_time = self.t + self.parking.travel_time(event.robot.start_position, event.robot.goal_position)
                        event_end_task = Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot)
                        heapq.heappush(self.events, Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot))
                        event.robot.doing = event_end_task

                    else:
                        # Effet de bord de l'appel : bloque le side de la lane si avec l'ajout du moved_vehicle il est rempli
                        event.robot.goal_position = self.algorithm.place(moved_vehicle, event.robot.goal_position)
                        
                        event.robot.goal_time = self.t + self.parking.travel_time(event.robot.start_position, event.robot.goal_position)
                        event_end_task = Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot)
                        heapq.heappush(self.events, Event(moved_vehicle, event.robot.goal_time, "robot_end_task", event.robot))
                        event.robot.doing = event_end_task
                


        elif event.event_type == "robot_end_task":

            # On vérifie que le robot n'ai pas été dérouté
            if event == event.robot.doing:

                event.robot.start_position = event.robot.goal_position
                event.robot.start_time = self.t

                
                block_id, lane_id, side = event.robot.start_position
                lane = self.parking.blocks[block_id].lanes[lane_id]

                lane.push(vehicle.id, side)
                event.robot.vehicle = None
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
                
                    for pdg_retrieval in self.pending_retrievals:
                        # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                        if pdg_retrieval == event.robot.target:
                            self.execute(event.robot.target)
                            self.pending_retrievals.remove(event.robot.target)
                            break


                event.robot.target = None
                event.robot.doing = None
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
            if not lane.list_vehicles[0] in [None, "Lock"] and not self.parking.blocks[0].targeted[lane_id]:
                vehicle = self.stock.vehicles[lane.list_vehicles[0]]
                if vehicle.order_retrieval > self.t or vehicle.retrieval - self.t > datetime.timedelta(hours=1):
                    robot.start_position = robot.goal_position
                    robot.goal_position = (0, lane_id, "bottom")
                    lane.pop_reserve("bottom")

                    robot.start_time = self.t
                    robot.goal_time = self.t + self.parking.travel_time((0, lane_id, "bottom"), robot.goal_position)

                    event_arrival = Event(self.stock.vehicles[vehicle.id], robot.goal_time, "robot_arrival", robot)
                    heapq.heappush(self.events, event_arrival)
                    robot.doing = event_arrival

                    event = Event(self.stock.vehicles[vehicle.id], robot.goal_time, "empty_interface", robot)

                    robot.target = event

                    self.parking.blocks[0].targeted[lane_id] = True
                    
                    if self.print_in_terminal:
                        print(f" -> event {event} assigned to {robot}")
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
            robot.goal_position = (block_id, lane_id, side)
            lane_vehicle.pop_reserve(side)

            robot.start_time = self.t
            robot.goal_time = self.t + self.parking.travel_time(position, robot.goal_position)

            event.robot = robot
            event_arrival = Event(event.vehicle, robot.goal_time, "robot_arrival", robot)
            heapq.heappush(self.events, event_arrival)

            robot.doing = event_arrival
            robot.target = event

            return event
        
    """
    def find_unassigned_events(self, are_available_places_interface):
        i = 0
        while i < len(self.pending_retrievals):
            event = self.pending_retrievals[i]
            if event.unassigned_tasks and event.vehicle.id in self.parking.occupation:
                if event.unassigned_tasks != 1 or are_available_places_interface:                       
                    event.unassigned_tasks -= 1
                    return event
            i += 1

        i = 0
        while i < len(self.events):
            event = self.events[i]
            if event.event_type == "retrieval" and event.unassigned_tasks and event.vehicle.id in self.parking.occupation:
                if event.unassigned_tasks != 1 or are_available_places_interface:                       
                    event.unassigned_tasks -= 1
                    return event
            i += 1
    """
    def find_unassigned_events(self, are_available_places_interface):
        i = 0
        while i < len(self.pending_retrievals):
            event = self.pending_retrievals[i]
            if event.vehicle.id in self.parking.occupation:
                block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                if block_id != 0:
                    vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]

                    if vehicle_lane.bottom_access and (not vehicle_lane.future_bottom_position is None) and vehicle_lane.future_bottom_position - position < position - vehicle_lane.future_top_position:
                        if vehicle_lane.future_bottom_position - position >= 0:
                            return event
                    elif not vehicle_lane.future_top_position is None:
                        if position - vehicle_lane.future_top_position >= 0:
                            return event
            i += 1

        i = 0
        while i < len(self.events):
            event = self.events[i]
            if event.date - self.t > datetime.timedelta(hours=1):
                break
            if event.event_type == "retrieval" and event.vehicle.id in self.parking.occupation:
                block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                if block_id != 0:
                    vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]

                    if vehicle_lane.bottom_access and (not vehicle_lane.future_bottom_position is None) and vehicle_lane.future_bottom_position - position < position - vehicle_lane.future_top_position:
                        if vehicle_lane.future_bottom_position - position >= 0:
                            return event
                    elif not vehicle_lane.future_top_position is None:
                        if position - vehicle_lane.future_top_position >= 0:
                            return event
            i += 1

    def wake_up_robots(self):
        for robot in self.robots:
            if robot.target is None:
                self.assign_task(robot)
    
    def whistle(self):
        pass
            

    


class Event():

    def __init__(self, vehicle, date, event_type, robot=None, unassigned_tasks=None, goal_position=None, event_retrieval=None):
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
        self.goal_position = goal_position
        self.canceled = False
        self.event_retrieval = event_retrieval
    
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
                        lane_chosen.push_reserve("top")
                        return (rand_i_block, rand_i_lane, "top")
            else:
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "bottom")]:
                    #if (not forbidden_access) or not (lane_chosen == forbidden_access[0] and "bottom" == forbidden_access[1]):
                    if lane_chosen.is_bottom_available():
                        lane_chosen.push_reserve("bottom")
                        return (rand_i_block, rand_i_lane, "bottom")
            nb_iter += 1
            if nb_iter == max_iter:
                print("ERREUR DE PLACEMENT")
                print(self.parking)
                print(self.locked_lanes)
                raise ValueError("le placement n'a pas pu être effectué")
            


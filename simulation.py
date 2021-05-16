
import random
from vehicle import Vehicle, Stock, RandomStock
import heapq
import datetime
from robot import Robot
import time
from display import Display


class Simulation():

    def __init__(self, t0, stock, robots, parking, AlgorithmType, order=True, print_in_terminal=False, display=None):
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

        # nb_events_tracker : dictionnaire contenant le nombre d'évènements dans la file de priorité à chaque date
        self.nb_events_tracker = {}

        # Création de la file d'événements : ajout des commandes
        self.events = []
        for v in self.stock.vehicles.values():
            if order:
                heapq.heappush(self.events, Event(v, v.order_deposit, "order_deposit"))
                heapq.heappush(self.events, Event(v, v.order_retrieval, "order_retrieval"))
            else:
                heapq.heappush(self.events, Event(v, v.deposit, "deposit"))
                heapq.heappush(self.events, Event(v, v.retrieval, "retrieval"))                


        self.pending_deposits = []
        self.pending_retrievals = []

        self.vehicles_to_retrieve = []
    
        # Dictionnaire des extrémités de lanes
        self.locked_lanes = {}
        for block_id, block in enumerate(self.parking.blocks):
            for lane_id, lane in enumerate(block.lanes):
                self.locked_lanes[(block_id, lane_id, "top")] = int(not lane.top_access)
                self.locked_lanes[(block_id, lane_id, "bottom")] = int(not lane.bottom_access)
        
        args = (self.t, self.stock, self.robots, self.parking, self.events, self.locked_lanes, self.pending_retrievals)
        self.algorithm = AlgorithmType(*args, print_in_terminal=self.print_in_terminal) # /!\ provisoire

        # Dictionnaires pour l'analyse de flux
        self.nb_entree = {}
        self.nb_sortie = {}
        self.nb_sortie_interface = {}

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
            print([(k,self.locked_lanes[k]) for k in self.locked_lanes if self.locked_lanes[k]])
            print("-------------")
            for block_id, lane_id, side in self.locked_lanes:
                lane = self.parking.blocks[block_id].lanes[lane_id]
                print((block_id, lane_id, side), lane.top_position, lane.argmax_retrieval, lane.bottom_position)
                print((block_id, lane_id, side), lane.future_top_position, lane.future_bottom_position)
            print("-------------")
            print(self.pending_retrievals)
            print("-------------")

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
            self.algorithm.check_redirections(event, self.t)
            self.algorithm.update(self.t)

            """
            elif event.event_type == "wake_up_robots_deposit":
                pass
                # self.wake_up_robots()
            """
        
        elif event.event_type == "wake_up_robots":
            self.algorithm.reward -= 1.
            self.algorithm.update(self.t)

        elif event.event_type == "deposit":
            nb_jour = (self.t - self.stock.first_day).days
            if nb_jour in self.nb_entree.keys():
                self.nb_entree[nb_jour] += 1
            else:
                self.nb_entree[nb_jour] = 1

            lane_id = self.parking.blocks[0].empty_lane()
            if lane_id == "full":
                heapq.heappush(self.pending_deposits, event)
            else:
                self.parking.blocks[0].lanes[lane_id].push_reserve(vehicle.id, "top")
                self.parking.blocks[0].lanes[lane_id].push(vehicle.id, "top", self.stock)
                self.parking.occupation[vehicle.id] = (0, lane_id, 0)

                vehicle.effective_deposit = self.t

                # ajout du retard (nul) à la liste des retards au dépôt
                self.before_deposit_delays.append(datetime.timedelta(0, 0, 0, 0, 0, 0))

                self.algorithm.update_deposit(self.t)
                
                if self.display:
                    self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"Deposit of {vehicle.id}")
                print(self.parking)
                print("")

        elif event.event_type == "retrieval":
            nb_jour = (self.t - self.stock.first_day).days

            if vehicle.id in self.parking.occupation:
                i_block, i_lane, _ = self.parking.occupation[vehicle.id]
                if i_block == 0:
                    if nb_jour in self.nb_sortie.keys():
                        self.nb_sortie[nb_jour] += 1
                    else:
                        self.nb_sortie[nb_jour] = 1

                    if self.display:
                        self.display.erase_vehicle(vehicle)

                    # Le client récupère son véhicule (seul endroit dans simulation où cela se produit)
                    self.parking.blocks[0].lanes[i_lane].pop_reserve("top")
                    self.parking.blocks[0].lanes[i_lane].pop("top")


                    del self.parking.occupation[event.vehicle.id]

                    if self.pending_deposits:
                        event_deposit = heapq.heappop(self.pending_deposits)
                        self.parking.blocks[0].lanes[i_lane].push_reserve(event_deposit.vehicle.id, "top")
                        self.parking.blocks[0].lanes[i_lane].push(event_deposit.vehicle.id, "top", self.stock)
                        self.parking.occupation[event_deposit.vehicle.id] = (0, i_lane, 0)

                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - event_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        event_deposit.vehicle.effective_deposit = self.t

                        if self.display:
                            self.display.draw_vehicle(event_deposit.vehicle)

                        for pdg_retrieval in self.pending_retrievals:
                            # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                            if pdg_retrieval.vehicle.id == event_deposit.vehicle.id:
                                self.execute(pdg_retrieval)
                                self.pending_retrievals.remove(pdg_retrieval)
                                break

                    if self.print_in_terminal:
                        print(f"Retrieval of {vehicle.id}")
                        print(self.parking)
                        print("")
                    
                    self.algorithm.update_retrieval(vehicle, self.t)

                else:
                    heapq.heappush(self.pending_retrievals, event)
            else:
                for pdg_deposit in self.pending_deposits:
                    if vehicle.id == pdg_deposit.vehicle.id:
                        self.pending_deposits.remove(pdg_deposit)
                else:
                    heapq.heappush(self.pending_retrievals, event)


        elif event.event_type == "robot_arrival":

            # On vérifie qu'il s'agit bien de l'évènement que le robot était en train de considérer
            # Cela pourrait ne pas être le cas si le robot a changé de tâche en cours de route
            if event == event.robot.doing:
                self.execute_robot_arrival(event, vehicle)
                                                

        elif event.event_type == "robot_end_task":

            # On vérifie qu'il s'agit bien de l'évènement que le robot était en train de considérer
            # Cela pourrait ne pas être le cas si le robot a changé de tâche en cours de route
            if event == event.robot.doing:
                self.execute_robot_end_task(event, vehicle)


    def execute_robot_end_task(self, event, vehicle):

        block_id, lane_id, side = event.robot.goal_position
        lane = self.parking.blocks[block_id].lanes[lane_id]

        event.robot.start_position = event.robot.goal_position
        event.robot.start_time = self.t
        event.robot.goal_time = None
        event.robot.doing = None
        event.robot.target = None

        success = False # Pourl'instant ...

        # On vérifie qu'ily ait bien la place de mettre le véhicule
        if lane.end_position(side) is None or abs(lane.end_position(side) - lane.end_limit(side)) > 0:

            success = True
            """
            Exécution du dépôt du véhicule
            """
            lane.push(vehicle.id, side, self.stock)
            event.robot.vehicle = None
            self.parking.occupation[vehicle.id] = (block_id, lane_id, lane.end_position(side))

            if block_id == 0:
                # ajout du retard éventuel à la liste des retards à la sortie
                self.retrieval_delays.append(self.t - vehicle.retrieval)
            
                for pdg_retrieval in self.pending_retrievals:
                    # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                    if pdg_retrieval.vehicle.id == vehicle.id:
                        self.execute(pdg_retrieval)
                        self.pending_retrievals.remove(pdg_retrieval)
                        break
            
            """
            Affichage du dépôt du véhicule 
            """
            if vehicle.id in self.parking.occupation and self.display:
                self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"{event.robot} places {vehicle.id} ")
                print(self.parking)
                print("")

        """
        Mise à jour des tâches des robots et de la file de priorité
        """
        self.algorithm.update_robot_end_task(event.robot, event.robot.start_position, success, self.t)

    def execute_robot_arrival(self, event, vehicle):
        
        block_id, lane_id, side = event.robot.goal_position
        pos_moved_vehicle = self.parking.blocks[block_id].lanes[lane_id].end_position(side)

        event.robot.start_position = event.robot.goal_position
        event.robot.start_time = self.t
        event.robot.goal_time = None
        event.robot.doing = None

        moved_vehicle = None # Pour l'instant ...
        success = False

        # On vérifie qu'il y ait bien un véhicule à récupérer
        if not (pos_moved_vehicle is None):

            moved_vehicle = self.stock.vehicles[self.parking.blocks[block_id].lanes[lane_id].list_vehicles[pos_moved_vehicle]]

            # On vérifie que l'algorithme souhaite toujours que le robot récupère le véhicule
            if self.algorithm.check_pick(event.robot.start_position, moved_vehicle, self.t):
                """
                Exécution du retrait du véhicule
                """
                                
                if self.display:
                    self.display.erase_vehicle(moved_vehicle)
            
                self.parking.blocks[block_id].lanes[lane_id].pop(side)
                del self.parking.occupation[moved_vehicle.id]
                event.robot.vehicle = moved_vehicle   
                success = True

                # On vérifie si une place est libérée dans l'interface pour un éventuel client qui attendait pour un deposit
                if block_id == 0:
                    self.parking.blocks[0].nb_places_available += 1
                    if self.pending_deposits:
                        event_deposit = heapq.heappop(self.pending_deposits)
                        self.parking.blocks[0].lanes[lane_id].push_reserve(event_deposit.vehicle.id, "top")
                        self.parking.blocks[0].lanes[lane_id].push(event_deposit.vehicle.id, "top", self.stock)
                        self.parking.occupation[event_deposit.vehicle.id] = (0, lane_id, 0)

                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - event_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        event_deposit.vehicle.effective_deposit = self.t

                        if self.display:
                            self.display.draw_vehicle(event_deposit.vehicle)

                        for pdg_retrieval in self.pending_retrievals:
                            # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                            if pdg_retrieval.vehicle.id == event_deposit.vehicle.id:
                                self.execute(pdg_retrieval)
                                self.pending_retrievals.remove(pdg_retrieval)
                                break

                if block_id == 0:
                    # ajout du retard éventuel à la liste des retards au dépôt
                    self.after_deposit_delays.append(self.t - moved_vehicle.effective_deposit)
                    # la place n'est plus le siège d'un évènement empty_interface
                    self.parking.blocks[0].targeted[lane_id] = False  

                """
                Affichage du retrait du véhicule
                """

                if self.print_in_terminal:
                    print(f"Robot {event.robot} loads {moved_vehicle.id}")
                    print(self.parking)
                    print("")   

        elif block_id == 0:
            # Je ne sais pas ce que c'est que ça
            nb_jour = (self.t - self.stock.first_day).days
            if nb_jour in self.nb_sortie_interface.keys():
                self.nb_sortie_interface[nb_jour] += 1
            else:
                self.nb_sortie_interface[nb_jour] = 1

        """
        Mise à jour des tâches des robots et de la file de priorité
        """
        self.algorithm.update_robot_arrival(event.robot, event.robot.start_position, success, moved_vehicle, self.t)

    def next_event(self, until = None, repeat = 1):
        """
        Exécute un nombre d'évènements égal à repeat
        Renvoie un couple (bouléen, évènement)
        """
        event = None
        r = 0
        while (r is None or r < repeat) and (until is None or until > self.t):
            if self.events:
                time_start = time.time()
                event = heapq.heappop(self.events)
                self.t = event.date
                self.nb_events_tracker[self.t] = len(self.events)
                self.execute(event)
                self.time_execution += time.time() - time_start
                r += 1
                if self.display:
                    self.display.update()

            else:
                if self.print_in_terminal:
                    print("THE SIMULATION IS COMPLETED")  
                break    
        return bool(self.events), event
            
    def complete(self):
        """
        Finit la simulation
        """
        while True:
            if not self.next_event():
                break
        
        # simulation terminée : on nettoie les dictionnaires d'état du parking et des robots
        self.parking.occupation = {}
        for robot in self.robots:
            robot = Robot(robot.id_robot)

        if self.print_in_terminal:
            print(f"Temps d'exécution : {self.time_execution:.2f}s")
    
    def start_display(self, place_width=15, place_length=20, time_interval=0.):
        Display(self, place_width, place_length, time_interval)


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
        if self is None or other is None:
            return False
        if self.vehicle == None or other.vehicle == None:                    #si jamais le event n'a pas de véhicule associé
            return (not (other is None)) and self.date == other.date
        return (not (other is None)) and self.date == other.date and self.vehicle.id == other.vehicle.id
    
    def __lt__(self, other):
        return self.date < other.date
    
    def __repr__(self):
        return f"{self.event_type} ; due to {self.date} ; vehicle {self.vehicle} ;"


class Algorithm():

    def __init__(self, t0, stock, robots, parking, events, *args, print_in_terminal=False):
        self.robots = robots
        self.stock = stock
        self.t0 = t0
        self.parking = parking
        self.events = events
        self.print_in_terminal = print_in_terminal

        #paramètres liés à la mesure de la performance de l'algorithme
        self.nb_placements = 0
    
    def update(self, current_time):
        pass
    
    def update_deposit(self, current_time):
        pass

    def update_retrieval(self, vehicle, current_time):
        pass

    def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):
        pass

    def update_robot_end_task(self, robot, lane_end, success, current_time):
        pass

class BaseAlgorithm(Algorithm):

    def __init__(self, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, print_in_terminal=False):

        super().__init__(t0, stock, robots, parking, events, print_in_terminal=False)

        self.locked_lanes = locked_lanes
        self.side_chosen_to_retrieve = {}
        self.pending_retrievals = pending_retrievals


    def check_pick(self, lane_end, moved_vehicle, current_time):
        block_id, lane_id, side = lane_end
        if moved_vehicle.order_retrieval <= current_time and moved_vehicle.retrieval - current_time < datetime.timedelta(hours=1):
            i_lane = self.parking.blocks[0].empty_lane()
            if i_lane == "full":
                self.parking.blocks[block_id].lanes[lane_id].pop_cancel_reserve(side)
                return False
        return True

    def check_redirections(self, event, current_time):

        # Si un robot est en train de transporter un véhicule cible d'un retrieval
        for robot in self.robots:
            if not (robot.vehicle is None) and robot.vehicle.id == event.vehicle.id:
                i_lane = self.parking.blocks[0].empty_lane()
                if i_lane != "full":
                    block_id, lane_id, side = robot.goal_position
                    self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                    self.parking.blocks[0].lanes[i_lane].push_reserve(robot.vehicle.id, "bottom", mark=False)
                    self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                    #On place le vehicule a l'interface
                    robot.goal_position = (0, i_lane, "bottom")
                    self.parking.blocks[0].nb_places_available -= 1
                    # Calcul du temps de trajet faux
                    robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
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
                print(vehicle_lane.bottom_position, vehicle_lane.top_position)
                print(vehicle_lane.list_vehicles[position])
                if vehicle_lane.bottom_access and vehicle_lane.bottom_position - position < position - vehicle_lane.top_position:
                    side = "bottom"
                else:
                    side = "top"
                
                self.locked_lanes[(block_id, lane_id, side)] += 1
                self.side_chosen_to_retrieve[event.vehicle.id] = side

                # Si un robot voulait placer un véhicule dans la lane et le côté par lequel on veut sortir le véhicule cible du retrieval
                for robot in self.robots:                           
                    if not (robot.vehicle is None) and robot.goal_position == (block_id, lane_id, side):
                        self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                        robot.goal_position = self.place(robot.vehicle, robot.start_position, current_time)
                        # Calcul du temps de trajet faux
                        robot.goal_time  = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
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
                self.assign_task(robot, current_time)
    
    def update_deposit(self, current_time):
        self.update(current_time)

    def update_retrieval(self, vehicle, current_time):
        self.update(current_time)
    
    def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):

        if success:
            # Si un véhicule a été déposé dans la place libérée de l'interface
            if lane_end[0] == 0 and not self.parking.blocks[0].lanes[lane_end[1]].list_vehicles[0] in [0, "Lock"]:
                self.update(current_time)

            if moved_vehicle.order_retrieval <= current_time and moved_vehicle.retrieval - current_time < datetime.timedelta(hours=1):
                i_lane = self.parking.blocks[0].empty_lane()
                side_chosen_initially = self.side_chosen_to_retrieve[moved_vehicle.id]
                self.locked_lanes[robot.goal_position[:2] + (side_chosen_initially,)] -= 1
                self.parking.blocks[0].lanes[i_lane].push_reserve(moved_vehicle.id, "bottom", mark=False)
                self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                #On place le vehicule a l'interface
                robot.goal_position = (0, i_lane, "bottom")
                self.parking.blocks[0].nb_places_available -= 1
                
                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                event_end_task = Event(moved_vehicle, robot.goal_time, "robot_end_task", robot)
                heapq.heappush(self.events, Event(moved_vehicle, robot.goal_time, "robot_end_task", robot))
                robot.doing = event_end_task

            else:
                # Effet de bord de l'appel : bloque le side de la lane si avec l'ajout du moved_vehicle il est rempli
                robot.goal_position = self.place(moved_vehicle, robot.goal_position, current_time)
                
                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                event_end_task = Event(moved_vehicle, robot.goal_time, "robot_end_task", robot)
                heapq.heappush(self.events, Event(moved_vehicle, robot.goal_time, "robot_end_task", robot))
                robot.doing = event_end_task

    def update_robot_end_task(self, robot, lane_end, success, current_time):
        self.update(current_time)

    def place(self, *args):
        """
        Tout algorithme "BaseAlgorithm" a une méthode place
        """
        return (None, None, None)

    def assign_task(self, robot, current_time):

        are_available_places_interface = False
        for lane_id, lane in enumerate(self.parking.blocks[0].lanes):
            if not lane.list_vehicles[0] in [0, "Lock"] and not self.parking.blocks[0].targeted[lane_id]:
                vehicle = self.stock.vehicles[lane.list_vehicles[0]]
                if vehicle.order_retrieval > current_time or vehicle.retrieval - current_time > datetime.timedelta(hours=1):
                    robot.start_position = robot.goal_position
                    robot.goal_position = (0, lane_id, "bottom")
                    lane.pop_reserve("bottom")

                    robot.start_time = current_time
                    robot.goal_time = current_time + self.parking.travel_time((0, lane_id, "bottom"), robot.goal_position)

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
        
        event = self.find_unassigned_events(are_available_places_interface, current_time)

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

            robot.start_time = current_time
            robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

            event.robot = robot
            event_arrival = Event(event.vehicle, robot.goal_time, "robot_arrival", robot)
            heapq.heappush(self.events, event_arrival)

            robot.doing = event_arrival
            robot.target = event

            return event
        
    def find_unassigned_events(self, are_available_places_interface, current_time):
        # On verifie d'abord si des retrievals sont en retard
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

        # On s'intéresse ensuite aux retrievals qui sont prévus dans moins d'une heure
        i = 0
        while i < len(self.events):
            event = self.events[i]
            if event.date - current_time > datetime.timedelta(hours=1):
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
       
    def update(self, current_time):
        for robot in self.robots:
            if robot.doing is None:
                self.assign_task(robot, current_time)

class AlgorithmRandom(BaseAlgorithm):

    def place(self, vehicle, start_position, time, max_iter=1000):
        self.nb_placements += 1
        nb_iter = 0
        while nb_iter < max_iter:
            rand_i_block = random.randrange(1, len(self.parking.blocks))
            rand_i_lane = random.randrange(len(self.parking.blocks[rand_i_block].lanes))
            lane_chosen = self.parking.blocks[rand_i_block].lanes[rand_i_lane]
            if random.randrange(2):
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "top")]:
                    if lane_chosen.is_top_available():
                        lane_chosen.push_reserve(vehicle.id, "top")
                        return (rand_i_block, rand_i_lane, "top")
            else:
                if not self.locked_lanes[(rand_i_block, rand_i_lane, "bottom")]:
                    if lane_chosen.is_bottom_available():
                        lane_chosen.push_reserve(vehicle.id, "bottom")
                        return (rand_i_block, rand_i_lane, "bottom")
            nb_iter += 1
            if nb_iter == max_iter:
                if self.print_in_terminal:
                    print("ERREUR DE PLACEMENT")
                    print(self.parking)
                    print(self.locked_lanes)
                raise ValueError("le placement n'a pas pu être effectué")

class AlgorithmUnimodal(BaseAlgorithm):

    def place(self, vehicle, start_position, time):
        self.nb_placements += 1
        min_weight = None
        min_lane_end = None
        """
        self.locked_lanes.keys() contient l'ensemble des extrémités de lane (bloquées ou non !)
        On parcourt l'ensemble de ces extrémités et on cherche celle de poids minimal
        """
        for lane_end, is_locked in self.locked_lanes.items():
            if not is_locked and (start_position is None or start_position != lane_end):
                block_id, lane_id, side = lane_end
                if block_id != 0:
                    lane = self.parking.blocks[block_id].lanes[lane_id]
                    if lane.is_end_available(side):

                        # On simule l'évolution de la lane
                        time_of_arrival = time + self.parking.travel_time(start_position, lane_end)
                        events_to_reverse = self.parking.future_config(block_id, lane_id, self.robots, self.stock, max_time = time_of_arrival)
                        lane.push(vehicle.id, side, self.stock)
                        # x : position du véhicule dans la lane       
                        x = lane.end_position(side)          
                        events_to_reverse.append((side,))
                        events_to_reverse.extend(self.parking.future_config(block_id, lane_id, self.robots, self.stock, min_time = time_of_arrival))

                        if side == "top":
                            distance_to_lane_end = lane.top_position
                        else:
                            distance_to_lane_end = lane.length - lane.bottom_position - 1
    
                        # Poids de l'extrémité si on ne peut pas conserver l'unimodalité (apparente)
                        weight = 1000000
                        if lane.top_position == x and lane.bottom_position == x:
                            # Poids de l'extrémité si le véhicule est seul dans sa lane
                            weight = 10000
                        elif lane.top_position <= x and lane.bottom_position >= x:
                            if x == lane.argmax_retrieval:
                                # Le véhicule est le nouveau "maximum" de la lane
                                if lane.top_position < x:
                                    weight = (vehicle.retrieval - self.stock.vehicles[lane.list_vehicles[x-1]].retrieval).total_seconds()//60
                                    if lane.bottom_position > x:
                                        weight = min(weight, (vehicle.retrieval - self.stock.vehicles[lane.list_vehicles[x+1]].retrieval).total_seconds()//60)
                                else:
                                     weight = (vehicle.retrieval - self.stock.vehicles[lane.list_vehicles[x+1]].retrieval).total_seconds()//60
                            elif x > lane.argmax_retrieval:
                                # Le véhicule est à droite du "maximum" de la lane
                                if self.stock.vehicles[lane.list_vehicles[x-1]].retrieval >= vehicle.retrieval:
                                    if lane.bottom_position == x or vehicle.retrieval >= self.stock.vehicles[lane.list_vehicles[x+1]].retrieval:
                                        weight = (self.stock.vehicles[lane.list_vehicles[x-1]].retrieval - vehicle.retrieval).total_seconds()//60
                            elif x < lane.argmax_retrieval:
                                # Le véhicule est à gauche du "maximum" de la lane
                                if self.stock.vehicles[lane.list_vehicles[x+1]].retrieval >= vehicle.retrieval:
                                    if lane.top_position == x or vehicle.retrieval >= self.stock.vehicles[lane.list_vehicles[x-1]].retrieval:
                                        weight = (self.stock.vehicles[lane.list_vehicles[x+1]].retrieval - vehicle.retrieval).total_seconds()//60

                        # On nettoie
                        self.parking.reverse_config(block_id, lane_id, events_to_reverse, self.stock)
                        
                        if min_weight is None or min_weight > weight:
                            min_weight = weight
                            min_lane_end = lane_end
        
        if not min_weight is None:
            block_id, lane_id, side = min_lane_end
            lane = self.parking.blocks[block_id].lanes[lane_id]
            lane.push_reserve(vehicle.id, side)
            return min_lane_end
        else:
            if self.print_in_terminal:
                print("ERREUR DE PLACEMENT")
                print(self.parking)
                print(self.locked_lanes)
            raise ValueError("le placement n'a pas pu être effectué")

class RLAlgorithm(Algorithm):

    def take_decision(self, robot_actions_lanes, robot_actions_sides, current_time):
        #print(robot_actions_lanes)
        for i_robot, robot in enumerate(self.robots):
            
            lane_global_id, side_bool = robot_actions_lanes[i_robot], robot_actions_sides[i_robot]

            if lane_global_id:
                if side_bool:
                    side = "bottom"
                else:
                    side = "top"
                block_id, lane_id = self.parking.dict_lanes[lane_global_id]
                robot.goal_position = (block_id, lane_id, side)

                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)

                if robot.vehicle is None:
                    event = Event(None, robot.goal_time, "robot_arrival", robot)
                    #self.parking.blocks[block_id].lanes[lane_id].list_vehicles[0] = 5
                else:
                    event = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                robot.doing = event
                heapq.heappush(self.events, event)
    
    def check_pick(self, lane_end, moved_vehicle, current_time):
        return True
    
    def update(self, current_time):
        self.pending_action = True

    def update_retrieval(self, vehicle, current_time):
        self.reward += 5.

    def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):
        self.update(current_time)
        self.reward -= 1.

    def update_robot_end_task(self, robot, lane_end, success, current_time):
        self.update(current_time)
        self.reward -= 1.
# Imports

import random
from numpy.lib.utils import deprecate
from vehicle import Vehicle, Stock, RandomStock
import datetime
from robot import Robot
import time
from display import Display
from sortedcontainers import SortedList


class Simulation():
    """
    Contient les méthodes de base pour la simulation évènementielle de l'évolution du parking
    """

    def __init__(self, t0, stock, robots, parking, AlgorithmType, order=True, print_in_terminal=False, display=None, max_t=None, optimization_parameters=None):
        """
        Exécute une simulation du fonctionnement du parking soumis à un stock de véhicule donné

        Paramètres :
        - t0 : date d'initialisation
        - stock : la liste des véhicules qui vont arriver dans le parking (avec leurs dates d'entrées, de sortie, et les dates de commande associées)
        - robots : la liste des robots s'occupant des voitures
        - parking : parking sur lequel est réalisé la simulation
        - AlgorithmType : algorithme régissant le placement des véhicules
        - order :
        - print_in_terminal : verbosité de l'écriture dans le terminal
        - display : affichage du parking on cours de la simulation ou non
        - max_t : 
        - optimization_parameters : paramètres utilisés par les algorithmes de placement et de sélection des tâches
        """

        # récupération des paramètres
        self.stock = stock
        self.robots = robots
        self.t = t0
        self.max_t = max_t
        self.parking = parking
        self.print_in_terminal = print_in_terminal
        self.optimization_parameters = optimization_parameters
        print(f"paramètre : {self.optimization_parameters}")
        self.last_printed_date = None
        self.display = display
        self.time_execution = 0

        # collecte de données pour le calcul des performances
        self.before_deposit_delays = []
        self.after_deposit_delays = []
        self.retrieval_delays = []

        # nb_events_tracker : dictionnaire contenant le nombre d'évènements dans la file de priorité à chaque date
        self.nb_events_tracker = {}

        # création de la file d'évènements
        self.events = SortedList()
        # création de la file des dépôts pas encore effectués
        self.deposit_events = SortedList()

        # remplissage de la file d'évènements avec les dates de commande d'entrées et de sorties de véhicules
        self.events.add(Event(None, t0, "start"))
        for v in self.stock.vehicles.values():
            if order:
                self.events.add(Event(v, v.order_deposit, "order_deposit"))
                self.events.add(Event(v, v.order_retrieval, "order_retrieval"))
            else:
                deposit_event = Event(v, v.deposit, "deposit")
                self.events.add(deposit_event)
                self.events.add(Event(v, v.retrieval, "retrieval"))    
                self.deposit_events.add(deposit_event)

        ### Création de files d'évènements pour certains types d'évènements particuliers

        # File des déposits des clients qui patientent à l'interface
        self.pending_deposits = SortedList()
        # File des retrievals des clients qui patientent à l'interface
        self.pending_retrievals = SortedList()
        # File des véhicules dans le parking classés selon leur date de retrieval
        self.retrievals_in_parking = SortedList()
        # Ensemble des véhicules qu'il reste à traiter dans la simulation
        self.vehicles_left_to_handle = set(self.stock.vehicles.keys())

        # liste de véhicules à sortir
        self.vehicles_to_retrieve = []
    
        # Dictionnaire des extrémités de lanes
        self.locked_lanes = {}
        for block_id, block in enumerate(self.parking.blocks):
            for lane_id, lane in enumerate(block.lanes):
                self.locked_lanes[(block_id, lane_id, "top")] = int(not lane.top_access)
                self.locked_lanes[(block_id, lane_id, "bottom")] = int(not lane.bottom_access)
        
        # Génération de l'algorithme de placement
        args = (self, self.t, self.stock, self.robots, self.parking, self.events, self.locked_lanes, self.pending_retrievals)
        self.algorithm = AlgorithmType(*args, print_in_terminal=self.print_in_terminal, optimization_parameters=self.optimization_parameters)

        # Dictionnaires pour l'analyse de flux
        self.nb_entree = {}
        self.nb_sortie = {}
        self.nb_sortie_interface = {}
        self.nb_vehicles_interface = {}
        self.max_interface = 0
        self.nb_interface = 0

        # Exécution de tous les évènements antérieurs à la date d'initialisation
        while self.events:
            if self.events[-1].date == t0:
                break
            event = self.events.pop()
            self.t = event.date
            self.execute(event)

    def execute(self, event):
        """
        Méthode effectuant le parcours de la file d'évènements
        """

        if self.display:
            self.display.show_robot()
        #if self.last_printed_date is None or self.t - self.last_printed_date > datetime.timedelta(days=7):
        #    print(self.t)
        #    self.last_printed_date = self.t
        if self.print_in_terminal:
            print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nEXECUTION at time {self.t}")
            print("event :", event)
            print(self.parking.blocks[0].targeted)
            # c = 0
            # for x in self.parking.blocks[0].targeted:
            #     if x:
            #         c += 1
            #         if c > 2:
            #             raise Error
            print("-------------")
            for robot in self.robots:
                print(f" - {robot}")
                print(f"doing :", robot.doing)
                print(f"target:", robot.target)
                print(f"vehicle carrying:", robot.vehicle)
                print(f"goal_position:", robot.goal_position)
            """
            print("-------------")
            print([(k,self.locked_lanes[k]) for k in self.locked_lanes if self.locked_lanes[k]])
            """
            print("-------------")
            for block_id, lane_id, side in self.locked_lanes:
                lane = self.parking.blocks[block_id].lanes[lane_id]
                print((block_id, lane_id, side), lane.top_position, lane.argmax_retrieval, lane.bottom_position)
                print((block_id, lane_id, side), lane.future_top_position, lane.future_bottom_position)
            print("-------------")
            print(self.pending_retrievals)
            print("-------------")
            print(self.parking.occupation)
            print("-------------")

        ### EXECUTION DE L'EVENEMENT
            
        vehicle = event.vehicle

        if event.event_type == "start":
            self.algorithm.update_start()

        elif event.event_type == "order_deposit":
            deposit_event = Event(vehicle, vehicle.deposit, "deposit")
            self.events.add(deposit_event)
            time_wake_up = max(self.t, vehicle.deposit - datetime.timedelta(hours=0.25))
            self.events.add(Event(vehicle, time_wake_up, "wake_up_robots_deposit"))
            self.deposit_events.add(deposit_event)
          
        elif event.event_type == "order_retrieval":
            event_retrieval = Event(vehicle, vehicle.retrieval, "retrieval")
            self.events.add(event_retrieval)
            time_wake_up = max(self.t, vehicle.retrieval - self.algorithm.max_anticipation_time)
            self.events.add(Event(vehicle, time_wake_up, "wake_up_robots_retrieval", event_retrieval=event_retrieval))

        elif event.event_type == "wake_up_robots_retrieval":
            self.algorithm.check_redirections(event, self.t)
            self.algorithm.update(self.t)

        
        elif event.event_type == "wake_up_robots":
            if event == self.algorithm.current_wake_up:
                self.algorithm.update(self.t)

        elif event.event_type == "deposit":

            success = False

            self.nb_interface += 1 # une voiture entre dans l'interface
            nb_jour = (self.t - self.stock.first_day).days

            if nb_jour in self.nb_entree.keys():
                self.nb_entree[nb_jour] += 1
            else:
                self.nb_entree[nb_jour] = 1
            
            if nb_jour in self.nb_vehicles_interface.keys():
                if self.nb_interface > self.max_interface: 
                    self.nb_vehicles_interface[nb_jour] = self.nb_interface
                    self.max_interface = self.nb_interface
            else: #Si c'est un nouveau jour, on ajoute le nb d'interface au 1er instant
                self.nb_vehicles_interface[nb_jour] = self.nb_interface

            lane_id = self.parking.blocks[0].empty_lane()
            if lane_id == "full":
                self.pending_deposits.add(event)
            else:
                success = True
                self.deposit_events.pop()
                self.retrievals_in_parking.add(vehicle)
                self.parking.blocks[0].lanes[lane_id].push_reserve(vehicle.id, "top")
                self.parking.blocks[0].lanes[lane_id].push(vehicle.id, "top", self.stock)
                self.parking.occupation[vehicle.id] = (0, lane_id, 0)

                vehicle.effective_deposit = self.t

                # ajout du retard (nul) à la liste des retards au dépôt
                self.before_deposit_delays.append(datetime.timedelta(0, 0, 0, 0, 0, 0))
                
                if self.display:
                    self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"Deposit of {vehicle.id}")
                print(self.parking)
                print("")
            
            self.algorithm.update_deposit(vehicle, success, self.t)

        elif event.event_type == "retrieval":
            nb_jour = (self.t - self.stock.first_day).days

            success = False

            # On regarde si le véhicule attendu est stationné sur le parking
            if vehicle.id in self.parking.occupation:
    
                i_block, i_lane, _ = self.parking.occupation[vehicle.id]

                # On regarde si le véhicule attendu est dans l'interface
                if i_block == 0:
                    
                    success = True
                    self.retrieval_delays.append(self.t - vehicle.retrieval)

                    # La prise en charge du véhicule est terminée
                    self.vehicles_left_to_handle.remove(vehicle.id)

                    if vehicle in self.retrievals_in_parking:
                        self.retrievals_in_parking.remove(vehicle)
                    else:
                        print("ERROR")

                    if nb_jour in self.nb_sortie.keys():
                        self.nb_sortie[nb_jour] += 1
                    else:
                        self.nb_sortie[nb_jour] = 1

                    if self.display:
                        self.display.erase_vehicle(vehicle)

                    # Le client récupère son véhicule (seul endroit dans simulation où cela se produit)
                    self.parking.blocks[0].lanes[i_lane].pop_reserve("top")
                    self.parking.blocks[0].lanes[i_lane].pop("top")

                    
                    self.nb_interface -= 1 # un véhicule sort de l'interface pour être rendu

                    del self.parking.occupation[event.vehicle.id]

                    # On vérifie si un client peut déposer son véhicule dans la place libérée de l'interface
                    if self.pending_deposits:
                        self.deposit_events.pop()
                        event_deposit = self.pending_deposits.pop()
                        self.parking.blocks[0].lanes[i_lane].push_reserve(event_deposit.vehicle.id, "top")
                        self.parking.blocks[0].lanes[i_lane].push(event_deposit.vehicle.id, "top", self.stock)
                        self.parking.occupation[event_deposit.vehicle.id] = (0, i_lane, 0)
                        self.retrievals_in_parking.add(event_deposit.vehicle)

                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - event_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        event_deposit.vehicle.effective_deposit = self.t
                        # on signale à l'algorithme qu'il y a eu un deposit
                        self.algorithm.update_deposit(event_deposit.vehicle, True, self.t)

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

                else:
                    # Si le véhicule n'est pas disponible dans l'interface, on l'ajoute à la liste triée des véhicules attendus par leur propriétaire
                    self.pending_retrievals.add(event)
            
            else:
                for pdg_deposit in self.pending_deposits:
                    # Si un client veut récupérer son véhicule alors qu'il attent pour le déposer
                    if vehicle.id == pdg_deposit.vehicle.id:
                        self.vehicles_left_to_handle.remove(vehicle.id)
                        self.pending_deposits.remove(pdg_deposit)
                        self.deposit_events.remove(pdg_deposit)
                        self.algorithm.update_deposit(pdg_deposit.vehicle, True, self.t)
                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - pdg_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        pdg_deposit.vehicle.effective_deposit = self.t

                        break
                else:
                    self.pending_retrievals.add(event)
            
            # On signale à l'algorithme qu'il y a eu un retrieval
            self.algorithm.update_retrieval(vehicle, success, self.t)

            self.algorithm.update_anticipation_time()


        elif event.event_type == "robot_arrival":

            nb_jour = (self.t - self.stock.first_day).days

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

        # On vérifie qu'il y ait bien la place de mettre le véhicule
        if lane.end_position(side) is None or abs(lane.end_position(side) - lane.end_limit(side)) > 0:

            success = True
            
            ### Exécution du dépôt du véhicule
            
            lane.push(vehicle.id, side, self.stock)
            event.robot.vehicle = None
            self.parking.occupation[vehicle.id] = (block_id, lane_id, lane.end_position(side))

            if block_id == 0:
                for pdg_retrieval in self.pending_retrievals:
                    # Dans le cas où l'on a mis dans l'interface un véhicule qui était attendu par son client
                    if pdg_retrieval.vehicle.id == vehicle.id:
                        self.execute(pdg_retrieval)
                        self.pending_retrievals.remove(pdg_retrieval)
                        break
            
            ### Affichage du dépôt du véhicule 
            
            if vehicle.id in self.parking.occupation and self.display:
                self.display.draw_vehicle(vehicle)

            if self.print_in_terminal:
                print(f"{event.robot} places {vehicle.id} ")
                print(self.parking)
                print("")

        ### Mise à jour des tâches des robots et de la file de priorité
        
        self.algorithm.update_robot_end_task(event.robot, event.robot.start_position, success, self.t)

    def execute_robot_arrival(self, event, vehicle):
        
        block_id, lane_id, side = event.robot.goal_position
        pos_moved_vehicle = self.parking.blocks[block_id].lanes[lane_id].end_position(side)

        event.robot.start_position = event.robot.goal_position
        event.robot.start_time = self.t
        event.robot.goal_time = None # Pour l'instant ...
        

        moved_vehicle = None # Pour l'instant ...
        success = False

        # On vérifie qu'il y ait bien un véhicule à récupérer
        if not (pos_moved_vehicle is None):

            moved_vehicle = self.stock.vehicles[self.parking.blocks[block_id].lanes[lane_id].list_vehicles[pos_moved_vehicle]]

            # On vérifie que l'algorithme souhaite toujours que le robot récupère le véhicule
            if self.algorithm.check_pick(event.robot.start_position, moved_vehicle, self.t):
                
                ### Exécution du retrait du véhicule
                                
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
                        self.deposit_events.pop()
                        event_deposit = self.pending_deposits.pop()
                        self.parking.blocks[0].lanes[lane_id].push_reserve(event_deposit.vehicle.id, "top")
                        self.parking.blocks[0].lanes[lane_id].push(event_deposit.vehicle.id, "top", self.stock)
                        self.parking.occupation[event_deposit.vehicle.id] = (0, lane_id, 0)
                        self.retrievals_in_parking.add(event_deposit.vehicle)

                        # ajout du retard éventuel à la liste des retards au dépôt
                        self.before_deposit_delays.append(self.t - event_deposit.date)
                        # mise à jour de la date de dépôt effectif du véhicule
                        event_deposit.vehicle.effective_deposit = self.t

                        self.algorithm.update_deposit(event_deposit.vehicle, True, self.t)

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
                    try:
                        self.after_deposit_delays.append(self.t - moved_vehicle.effective_deposit)
                    except:
                        self.after_deposit_delays.append(self.t - moved_vehicle.deposit)
                    # la place n'est plus le siège d'un évènement empty_interface
                    self.parking.blocks[0].targeted[lane_id] = False

                ### Affichage du retrait du véhicule

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

        ### Mise à jour des tâches des robots et de la file de priorité
        
        event.robot.doing = None
        self.algorithm.update_robot_arrival(event.robot, event.robot.start_position, success, moved_vehicle, self.t)

    def next_event(self, until = None, repeat = 1):
        """
        Exécute un nombre d'évènements égal à repeat
        Renvoie un couple (bouléen, évènement) heapq
        """
        event = None
        r = 0
        while (repeat is None or r < repeat) and (until is None or until > self.t):
            if self.events:
                time_start = time.time()
                event = self.events.pop()
                self.t = event.date
                self.nb_events_tracker[self.t] = len(self.events)
                self.execute(event)
                self.time_execution += time.time() - time_start
                r += 1
            else:
                if self.print_in_terminal:
                    print("THE SIMULATION IS COMPLETED")  
                break

        if self.display and (self.display.speed or event.event_type not in ["wake_up_robots_deposit", "wake_up_robots_retrieval", "order_deposit", "order_retrieval"]) :
            self.display.update()
            self.display.time_interval = 0*max(self.display.time_interval*0.995, 0.1)

        if self.max_t:
            return (bool(self.vehicles_left_to_handle) and self.t <= self.max_t and self.events), event
        else:
            return (bool(self.vehicles_left_to_handle) and self.events), event
            
    def complete(self):
        """
        Finit la simulation
        """
        while True:
            if not self.next_event()[0]:
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

    next_id = 0

    def __init__(self, vehicle, date, event_type, robot=None, unassigned_tasks=None, goal_position=None, event_retrieval=None):
        """
        Les valeurs possibles du string event_type sont :
        - 'order_deposit'
        - 'order_retrieval'
        - 'deposit'
        - 'retrieval'
        - 'robot_arrrival'
        - 'wake_up_robots_retrieval'
        - 'wake_up_robots'
        """
        self.vehicle = vehicle
        self.date = date
        self.event_type = event_type
        self.robot = robot
        self.unassigned_tasks = unassigned_tasks # No longer used
        self.goal_position = goal_position
        self.canceled = False # Not usedd
        self.event_retrieval = event_retrieval
        self.id = self.__class__.next_id
        self.__class__.next_id += 1
    
    def __bool__(self):
        return True

    def __eq__(self, other):
        if self is None or other is None:
            return False
        return self.id == other.id

    def __lt__(self, other):
        if self.date == other.date:
            return self.id > other.id
        return self.date > other.date
    
    def __repr__(self):
        if self.robot is not None: 
            return f"{self.event_type} ; due to {self.date} ; vehicle {self.vehicle} ; concerning robot {self.robot.id_robot}"
        else: 
            return f"{self.event_type} ; due to {self.date} ; vehicle {self.vehicle}"


class Algorithm():

    def __init__(self, simulation, t0, stock, robots, parking, events, *args, print_in_terminal=False):
        self.simulation = simulation
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
    
    def update_deposit(self, vehicle, success, current_time):
        pass

    def update_retrieval(self, vehicle, success, current_time):
        pass

    def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):
        pass

    def update_robot_end_task(self, robot, lane_end, success, current_time):
        pass

    def update_start(self):
        pass


class BaseAlgorithm(Algorithm):
    """
    Un BaseAlgorithm comporte une méthode assign_task qui attribue à un robot une tâche lorsqu'il n'a plus rien à faire
    """

    def __init__(self, simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, anticipation_time=datetime.timedelta(hours=1), print_in_terminal=False, optimization_parameters = None):
        super().__init__(simulation, t0, stock, robots, parking, events, print_in_terminal)

        self.locked_lanes = locked_lanes
        # Pour chaque véhicule, le côté de sa lane choisi pour le récupérer
        self.side_chosen_to_retrieve = {}
        self.pending_retrievals = pending_retrievals
        self.anticipation_time = anticipation_time
        self.optimization_parameters = optimization_parameters

        #paramètres liés à la mesure de la performance de l'algorithme
        self.nb_placements = 0
        self.min_anticipation_time = datetime.timedelta(hours = self.optimization_parameters[4])
        self.max_anticipation_time = datetime.timedelta(hours = self.optimization_parameters[5])

    def assign_task(self, robot):
        """Assigne une tâche à un robot

        :param robot: Un robot sans tâche
        :type robot: Robot
        :return: None si aucune tâche n'a été trouvée, l'event correspondant à la tâche sinon.
        :rtype: Event
        """

        retrieval_event = self.find_unassigned_retrieval()
        deposit_event = self.find_unassigned_deposit()

        # on vérifie qu'il y a bien des choses à faire
        if retrieval_event is None and deposit_event is None:
            return None

        # sinon il y a des choses à faire : on choisi entre un deposit et un retrieval
        if self.isRetrievalBetterThanDeposit(retrieval_event=retrieval_event, deposit_event=deposit_event) :    # on juge plus important de sortir un véhicule que d'en placer un

            if self.print_in_terminal:
                print(f" -> event {retrieval_event} assigned to {robot}")

            # on récupère la position du véhicule que l'on va chercher à placer
            block_id, lane_id, position = self.parking.occupation[retrieval_event.vehicle.id]
            lane_vehicle = self.parking.blocks[block_id].lanes[lane_id]

            # on détermine par quel côté le véhicule doit sortir
            if lane_vehicle.bottom_access and lane_vehicle.bottom_position - position < position - lane_vehicle.top_position:
                side = "bottom"
            else:
                side = "top"

            # mise à jour des positions actuelle et d'arrivée du robot
            robot.start_position = robot.goal_position
            robot.goal_position = (block_id, lane_id, side)
            # on informe qu'on est en train de retirer ce véhicule
            lane_vehicle.pop_reserve(side)

            # mise à jour des dates actuelle et d'arrivée du robot
            robot.start_time = self.simulation.t
            robot.goal_time = self.simulation.t + self.parking.travel_time(robot.start_position, robot.goal_position)

            # affectation du robot à l'évènement
            retrieval_event.robot = robot
            # création de l'event d'arrivée
            event_arrival = Event(retrieval_event.vehicle, robot.goal_time, "robot_arrival", robot)
            # ajout de l'event à la pile des events
            self.events.add(event_arrival)

            robot.doing = event_arrival     # event en cours
            # Utilisé pour contrôler ce que fait le robot
            robot.target = retrieval_event

            return retrieval_event
        
        else:   # on juge plus important de placer un véhicule que d'en sortir un
            
            # récupération de la position du véhicule à placer
            lane_id = self.parking.occupation[deposit_event.vehicle.id][1]
            lane = self.parking.blocks[0].lanes[lane_id]
            
            # mise à jour des positions actuelle et cible du robot
            robot.start_position = robot.goal_position
            robot.goal_position = (0, lane_id, "bottom")
            # on informe qu'on est en train de retirer ce véhicule
            lane.pop_reserve("bottom")

            # mise à jour des dates actuelle et d'arrivée du robot
            robot.start_time = self.simulation.t
            robot.goal_time = self.simulation.t + self.parking.travel_time((0, lane_id, "bottom"), robot.goal_position)
            # création de l'event d'arrivée (sur l'interface pour récupération)
            event_arrival = Event(self.stock.vehicles[deposit_event.vehicle.id], robot.goal_time, "robot_arrival", robot)
            # ajout de l'event à la pile des events
            self.events.add(event_arrival)
            robot.doing = event_arrival     # event en cours

            # Utilisé pour contrôler ce que fait le robot
            robot.target = deposit_event

            # on déclare que la lane est ciblée pour éviter qu'un autre robot ne vienne chercher le même véhicule
            self.parking.blocks[0].targeted[lane_id] = True
            
            if self.print_in_terminal:
                print(f" -> event {deposit_event} assigned to {robot}")
            return deposit_event
        

    def find_unassigned_retrieval(self):
        """
        Choisit, s'il y en a un, le retrieval à faire en priorité
        """
        # On verifie d'abord si des retrievals sont en retard
        i = 1
        while i <= len(self.pending_retrievals):
            event = self.pending_retrievals[-i]
            if event.vehicle.id in self.parking.occupation:
                block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                if block_id != 0:
                    lane = self.parking.blocks[block_id].lanes[lane_id]
                    try:
                        future_lane = self.parking.future_config(lane, block_id, lane_id, self.robots, self.stock)
                        if future_lane.list_vehicles[position] == event.vehicle.id:
                            return event
                    except IndexError:
                        pass
            i += 1

        # On s'intéresse ensuite aux retrievals qui sont prévus dans moins d'une heure
        i = 1
        while i <= len(self.events):
            event = self.events[-i]
            if event.date - self.simulation.t > self.anticipation_time:
                break
            if event.event_type == "retrieval" and event.vehicle.id in self.parking.occupation:
                block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
                if block_id != 0:
                    lane = self.parking.blocks[block_id].lanes[lane_id]
                    try:
                        future_lane = self.parking.future_config(lane, block_id, lane_id, self.robots, self.stock)
                        if future_lane.list_vehicles[position] == event.vehicle.id:
                            return event
                    except IndexError:
                        pass
            i += 1
    
    def find_unassigned_deposit(self):
        """
        Choisit, s'il y en a un, le deposit à faire en priorité
        """

        best_vehicle = None
        best_mark = None
        # on parcourt toutes les places de l'interface pour voir si il y a un véhicule à placer
        for lane_id, lane in enumerate(self.parking.blocks[0].lanes):
            # on vérifie qu'il y a bien un véhicule dans la place d'interface considérée et qu'il n'est pas déjà ciblé par un autre robot 
            if not lane.list_vehicles[0] in [0, "Lock"] and not self.parking.blocks[0].targeted[lane_id]:
                # on récupère le véhicule que l'on va chercher à placer
                vehicle = self.stock.vehicles[lane.list_vehicles[0]]
                # on vérifie que le véhicule ne va pas être récupérer par le client bientôt (et qu'il est en cours de sortie)
                if vehicle.order_retrieval > self.simulation.t or vehicle.retrieval - self.simulation.t > self.anticipation_time:
                    mark = vehicle.retrieval
                    # On cherche la place ayant la note la plus élévée 
                    if best_mark is None or mark < best_mark:
                        best_mark = mark
                        best_vehicle = vehicle

        if not best_vehicle is None:
            deposit_event = Event(self.stock.vehicles[best_vehicle.id], best_vehicle.deposit, "empty_interface", None)
            return deposit_event

    def place(self, *args):
        return (None, None, None)

    def check_pick(self, lane_end, moved_vehicle, current_time):
        block_id, lane_id, side = lane_end # datetime.timedelta
        if moved_vehicle.order_retrieval <= current_time and moved_vehicle.retrieval - current_time < self.anticipation_time:
            i_lane = self.parking.blocks[0].empty_lane()
            if i_lane == "full":
                self.parking.blocks[block_id].lanes[lane_id].pop_cancel_reserve(side)
                return False
        return True

    def check_redirections(self, event, current_time):
        """
        S'exécute lorsque l'algorithme est notifié d'un futur retrieval
        """
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
                    self.events.add(event_end_task)

                    if not robot.doing is None:     # ajout par Pierre pour éviter un bug
                        robot.doing.canceled = True
                    robot.doing = event_end_task
                
                else:
                    block_id, lane_id, side = robot.goal_position
                    self.locked_lanes[(block_id, lane_id, side)] += 1
                    self.side_chosen_to_retrieve[robot.vehicle.id] = side

                    # Si un robot voulait placer un véhicule dans la lane et le côté par lequel on veut sortir le véhicule cible du retrieval
                    for robot in self.robots:
                        if not (robot.vehicle is None) and robot.doing and robot.goal_position == (block_id, lane_id, side):
                            self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                            robot.goal_position = self.place(robot.vehicle, robot.start_position, current_time)
                            # Calcul du temps de trajet faux
                            robot.goal_time  = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                            event_end_task = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                            self.events.add(event_end_task)

                            robot.doing.canceled = True
                            robot.doing = event_end_task


        # Si un véhicule cible d'un retrieval est garé sur le parking
        if event.vehicle.id in self.parking.occupation:
            block_id, lane_id, position = self.parking.occupation[event.vehicle.id]
            if block_id != 0:
                vehicle_lane = self.parking.blocks[block_id].lanes[lane_id]
                if vehicle_lane.bottom_access and vehicle_lane.bottom_position - position < position - vehicle_lane.top_position:
                    side = "bottom"
                else:
                    side = "top"
                
                self.locked_lanes[(block_id, lane_id, side)] += 1
                self.side_chosen_to_retrieve[event.vehicle.id] = side

                # Si un robot voulait placer un véhicule dans la lane et le côté par lequel on veut sortir le véhicule cible du retrieval
                for robot in self.robots:
                    if not (robot.vehicle is None) and robot.doing and robot.goal_position == (block_id, lane_id, side):
                        self.parking.blocks[block_id].lanes[lane_id].push_cancel_reserve(side)
                        robot.goal_position = self.place(robot.vehicle, robot.start_position, current_time)
                        # Calcul du temps de trajet faux
                        robot.goal_time  = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                        event_end_task = Event(robot.vehicle, robot.goal_time, "robot_end_task", robot)
                        self.events.add(event_end_task)

                        robot.doing.canceled = True
                        robot.doing = event_end_task

        # Si un robot veut retirer de l'interface un véhicule cible d'un retrieval   
        for robot in self.robots:
            if (not robot.goal_position is None) and robot.doing:
                block_id, lane_id, side = robot.goal_position
                if block_id == 0 and self.parking.blocks[0].lanes[lane_id].list_vehicles[0] == event.vehicle.id:
                    robot.target = None
                    robot.doing.canceled = True
                    robot.doing = None
                    self.parking.blocks[0].targeted[lane_id] = False
                    self.parking.blocks[0].lanes[lane_id].pop_cancel_reserve("bottom")
                    robot.goal_position = robot.start_position
                    self.assign_task(robot)

    def update_anticipation_time(self):
        # calcul du nombre de dépôts à venir dans d'ici anticipation_time : parcours de self.deposit_events
        queue = self.simulation.deposit_events[:]
        nb_incoming_deposit = 0
        while True:
            if len(queue) == 0:
                break
            else:
                next_event = queue[-1]
                queue = queue[:-1]
                if next_event.date - self.simulation.t > self.anticipation_time:
                    nb_incoming_deposit += 1
                else:
                    break
        
        self.anticipation_time = self.min_anticipation_time + (1/(1+nb_incoming_deposit))*(self.max_anticipation_time - self.min_anticipation_time)


    def update_deposit(self, vehicle, success, current_time):
        self.update(current_time)

    def update_retrieval(self, vehicle, success, current_time):
        if success:
            self.update(current_time)
    
    def update_robot_arrival(self, robot, lane_end, success, moved_vehicle, current_time):

        if success:

            if moved_vehicle.order_retrieval <= current_time and moved_vehicle.retrieval - current_time < self.anticipation_time:
                i_lane = self.parking.blocks[0].empty_lane()
                if moved_vehicle.id not in self.side_chosen_to_retrieve:
                    self.side_chosen_to_retrieve[moved_vehicle.id] = robot.start_position[2]
                else:
                    side_chosen_initially = self.side_chosen_to_retrieve[moved_vehicle.id]
                    if self.locked_lanes[robot.goal_position[:2] + (side_chosen_initially,)] > 0:
                        self.locked_lanes[robot.goal_position[:2] + (side_chosen_initially,)] -= 1
                self.parking.blocks[0].lanes[i_lane].push_reserve(moved_vehicle.id, "bottom", mark=False)
                self.parking.blocks[0].lanes[i_lane].list_vehicles[0] = "Lock"
                # On place le vehicule a l'interface
                robot.goal_position = (0, i_lane, "bottom")
                self.parking.blocks[0].nb_places_available -= 1
                
                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                event_end_task = Event(moved_vehicle, robot.goal_time, "robot_end_task", robot)
                self.events.add(event_end_task)
                robot.doing = event_end_task

            else:
                # Effet de bord de l'appel : bloque le side de la lane si avec l'ajout du moved_vehicle il est rempli
                robot.goal_position = self.place(moved_vehicle, robot.goal_position, current_time)
                
                robot.goal_time = current_time + self.parking.travel_time(robot.start_position, robot.goal_position)
                event_end_task = Event(moved_vehicle, robot.goal_time, "robot_end_task", robot)
                self.events.add(event_end_task)
                robot.doing = event_end_task
            

    def update_robot_end_task(self, robot, lane_end, success, current_time):
        self.update(current_time)
   
    # def isRetrievalBetterThanDeposit(self, retrieval_event, deposit_event):
    #     # calcul nombre véhicules dans l'interface
    #     nb_vehicules_interface = 0
    #     interface_size = 0
    #     for place_lane in self.parking.blocks[0].lanes:
    #         interface_size += 1
    #         if place_lane.list_vehicles[0] != 0:
    #             nb_vehicules_interface += 1

    #     # calcul du nombre de dépôts à venir dans d'ici anticipation_time : parcours de self.deposit_events
    #     queue = self.simulation.deposit_events[:]
    #     nb_incoming_deposit = 0
    #     while True:
    #         if len(queue) == 0:
    #             break
    #         else:
    #             next_event = queue[-1]
    #             queue = queue[:-1]
    #             if next_event.date - self.simulation.t > self.anticipation_time:
    #                 nb_incoming_deposit += 1
    #             else:
    #                 break

    #     if retrieval_event is None:
    #         return False
    #     if deposit_event is None:
    #         return True
        
    #     return nb_vehicules_interface + nb_incoming_deposit < interface_size

    def update(self, current_time):
        for robot in self.robots:
            if robot.doing is None:
                self.assign_task(robot)

class AlgorithmRandom(BaseAlgorithm):

    def __init__(self, simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, anticipation_time=datetime.timedelta(hours=1), print_in_terminal=False, optimization_parameters=None):
        super().__init__(simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, anticipation_time, print_in_terminal, optimization_parameters)

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

    def isRetrievalBetterThanDeposit(self, retrieval_event, deposit_event):
        if not deposit_event is None:
            return False
        elif not retrieval_event is None:
            return True

    @classmethod
    def __repr__(self):
        return "Random"

###########################################################################
#################### Changement de classe d'algorithmes ###################
###########################################################################

class WeightAlgorithm(BaseAlgorithm):

    def __init__(self, simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, anticipation_time=datetime.timedelta(hours=1), print_in_terminal=False, optimization_parameters=None):
        super().__init__(simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, anticipation_time, print_in_terminal, optimization_parameters=optimization_parameters)

    
    def place(self, vehicle, start_position, date):
        
        #Algorithme de placement avec fonction de coût/pondération externalisée, cette fonction n'a pas à changer quel que soit l'algorithme de placement
        
        # paramètre utilisé dans performances (mesure)
        self.nb_placements += 1
        
        # initialisation des extrémité de lane et poids associé pour la recherche du minimum
        min_weight = None
        min_lane_end = None

        # self.locked_lanes = {extrémité de lane: bloquée ou non}
        # On parcourt l'ensemble de ces extrémités et on cherche celle de poids minimal
        for lane_end, is_locked in self.locked_lanes.items():
            # on s'assure que la lane n'est pas bloquée (qu'il n'y a pas de véhicule à sortir par cette extrémité) 
            # et qu'on ne replace pas le véhicule là où il est déjà
            if not is_locked and (start_position is None or start_position != lane_end):
                block_id, lane_id, side = lane_end
                # on vérifie que l'extrémité choisie n'est pas dans l'interface : on ne peut pas effectuer de placement dans l'interface (bloc 0)
                if block_id != 0:
                    lane = self.parking.blocks[block_id].lanes[lane_id]
                    # on vérifie que l'extrémité de lane n'est pas pleine
                    if lane.is_end_available(side):
                        # l'extrémité n'est pas pleine, pas bloquée, pas dans l'interface et pas notre position de départ : 
                        # on peut envisager de placer le véhicule ici
                        # calcul du poids dans une autre fonction
                        weight = self.weight(vehicle, start_position, lane_end, date)

                        # mise à jour du minimum si on a trouvé un meilleur candidat
                        if (not weight is None) and (min_weight is None or min_weight > weight):
                            min_weight = weight
                            min_lane_end = lane_end
        
        # si on a trouvé une lane pour placer le véhicule
        if not (min_weight is None):
            block_id, lane_id, side = min_lane_end
            lane = self.parking.blocks[block_id].lanes[lane_id]
            # on ajoute le véhicule à l'extrémité de la lane choisi (le calcul du temps pris par le robot pour le faire est effectué ailleurs)
            lane.push_reserve(vehicle.id, side)
            return min_lane_end
        # sinon c'est qu'aucune extrémité de lane n'est disponible (le poids minimum reste à None) : erreur
        else:
            raise ValueError("le placement n'a pas pu être effectué")
    
    def weight(self, vehicle, start_position, lane_end, date):
        return 0


class AlgorithmZeroMinus(WeightAlgorithm):

    def __init__(self, simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, print_in_terminal=False, optimization_parameters=None):
        super().__init__(simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, print_in_terminal=print_in_terminal, optimization_parameters=optimization_parameters)
        
        #paramètres de contrôle des poids
        alpha, beta, start_new_lane_weight, distance_to_lane_end_coef = optimization_parameters[:4]

        self.alpha = alpha
        self.beta = beta
        self.start_new_lane_weight = start_new_lane_weight
        self.distance_to_lane_end_coef = distance_to_lane_end_coef

        self.optimization_parameters = list(optimization_parameters)    # /!\ changement de type

    def weight(self, vehicle, start_position, lane_end, date):

        # détermination de la place cible et simulation éventuelle des arrivées entre temps

        block_id, lane_id, side = lane_end
        lane = self.parking.blocks[block_id].lanes[lane_id]

        # On simule l'évolution de la lane : il ne faut pas prendre en compte les véhicules qui seront partis quand le notre arrivera (/!\ est-ce bien utile / pas risqué ?)
        travel_time = self.parking.travel_time(start_position, lane_end)
        time_of_arrival = date + travel_time
        try:
            future_lane = self.parking.future_config(lane, block_id, lane_id, self.robots, self.stock, max_time = time_of_arrival)
            future_lane.push(vehicle.id, side, self.stock)
            self.parking.future_config(future_lane, block_id, lane_id, self.robots, self.stock, min_time = time_of_arrival, on_place=True)
        except IndexError:
            return None


        ### détermination des variables régissant le poids ###

        # overweight : somme des pénalités pour les cas dégénérés
        overweight = 0

        # détermination du nombre de places restantes dans la lane
        if side == "top":
            distance_to_lane_end = future_lane.top_position
        else:
            distance_to_lane_end = future_lane.length - future_lane.bottom_position - 1
        
        # détermination de delta_t (en minutes)
        try:
            delta_t = (vehicle.retrieval - future_lane.next_retrieval(side, self.stock, exception=vehicle.retrieval)).total_seconds()/60
        except TypeError:   # cas où la lane ne contient pas d'autre véhicule
            delta_t = 0
            overweight += self.start_new_lane_weight

        # détermination du temps de trajet en minutes
        travel_time = travel_time.total_seconds()/60

        # calcul du poids
        weight = self.alpha*delta_t + self.beta*abs(delta_t) + self.distance_to_lane_end_coef*distance_to_lane_end + overweight + travel_time

        return weight

    def isRetrievalBetterThanDeposit(self, retrieval_event, deposit_event):
        # calcul nombre véhicules dans l'interface
        nb_vehicules_interface = 0
        interface_size = 0
        for place_lane in self.parking.blocks[0].lanes:
            interface_size += 1
            if place_lane.list_vehicles[0] != 0:
                nb_vehicules_interface += 1

        # calcul du nombre de dépôts à venir dans d'ici anticipation_time : parcours de self.deposit_events
        queue = self.simulation.deposit_events[:]
        nb_incoming_deposit = 0
        while True:
            if len(queue) == 0:
                break
            else:
                next_event = queue[-1]
                queue = queue[:-1]
                if next_event.date - self.simulation.t > self.anticipation_time:
                    nb_incoming_deposit += 1
                else:
                    break

        if retrieval_event is None:
            return False
        if deposit_event is None:
            return True
        
        return nb_vehicules_interface + nb_incoming_deposit < interface_size

    @classmethod
    def __repr__(self):
        return "0-"



class AlgorithmUnimodal(WeightAlgorithm):

    def __init__(self, simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, print_in_terminal=False, optimization_parameters=(1., 100000., 100., -10.)):
        super().__init__(simulation, t0, stock, robots, parking, events, locked_lanes, pending_retrievals, print_in_terminal=print_in_terminal)
        
        #paramètres de contrôle des poids
        self.alpha, self.break_unimodality_weight, self.start_new_lane_weight, self.distance_to_lane_end_coef = (1., 100., 1., -1.)  #optimization_parameters

        self.optimization_parameters = list(optimization_parameters)    # /!\ changement de type

    def weight(self, vehicle, start_position, lane_end, date):

        # détermination de la place cible et simulation éventuelle des arrivées entre temps

        block_id, lane_id, side = lane_end
        lane = self.parking.blocks[block_id].lanes[lane_id]

        # On simule l'évolution de la lane : il ne faut pas prendre en compte les véhicules qui seront partis quand le notre arrivera (/!\ est-ce bien utile / pas risqué ?)
        travel_time = self.parking.travel_time(start_position, lane_end)
        time_of_arrival = date + travel_time
        try:
            future_lane = self.parking.future_config(lane, block_id, lane_id, self.robots, self.stock, max_time = time_of_arrival)
            future_lane.push(vehicle.id, side, self.stock)
            self.parking.future_config(future_lane, block_id, lane_id, self.robots, self.stock, min_time = time_of_arrival, on_place=True)
        except IndexError:
            return None

        # overweight : somme des pénalités pour les cas dégénérés
        overweight = 0

        # détermination du nombre de places restantes dans la lane
        if side == "top":
            distance_to_lane_end = future_lane.top_position
        else:
            distance_to_lane_end = future_lane.length - future_lane.bottom_position - 1
        
        ### détermination des variables régissant le poids ###
        
        # détermination de la place cible et simulation éventuelle des arrivées entre temps

        block_id, lane_id, side = lane_end
        lane = self.parking.blocks[block_id].lanes[lane_id]

        # On simule l'évolution de la lane : il ne faut pas prendre en compte les véhicules qui seront partis quand le notre arrivera (/!\ est-ce bien utile / pas risqué ?)
        time_of_arrival = date + self.parking.travel_time(start_position, lane_end)
        before_time_of_arrival = time_of_arrival - datetime.timedelta(minutes=1)
        try:
            future_lane = self.parking.future_config(lane, block_id, lane_id, self.robots, self.stock, max_time = before_time_of_arrival)
            future_lane.push(vehicle.id, side, self.stock)
            self.parking.future_config(future_lane, block_id, lane_id, self.robots, self.stock, min_time = before_time_of_arrival, on_place=True)
        except IndexError:
            return None
      
        # détermination de delta_t (en minutes)
        try:
            delta_t = (vehicle.retrieval - future_lane.next_retrieval(side, self.stock, exception=vehicle.retrieval)).total_seconds()/60
            # on regarde si l'on viole l'unimodalité
            if delta_t > 0:
                overweight += self.break_unimodality_weight

        except TypeError:   # cas où la lane ne contient pas d'autre véhicule
            delta_t = 0
            overweight += self.start_new_lane_weight

        # détermination du temps de trajet en minutes
        travel_time = travel_time.total_seconds()/60

        # calcul du poids
        weight = self.alpha*delta_t + self.distance_to_lane_end_coef*distance_to_lane_end + overweight + travel_time

        return weight

    @classmethod
    def __repr__(self):
        return "Unimodal"

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Dict, Discrete, Box, Tuple, MultiDiscrete
from simulation import *
from parking import *



class MLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        self.number_robots = 4
        self.simulation_length = 30
        self.daily_flow = 30
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        
        self.max_number_vehicles = int(self.simulation_length*self.daily_flow*2)
        self.t0 = datetime.datetime(2021,1,1,0,0,0,0)
        self.tmax  = self.t0 + datetime.timedelta(days=self.simulation_length+45)
        #print(self.tmax)

        # self.max_stock_visible = 100 + self.parking.size
        self.max_stock_visible = self.max_number_vehicles

        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)

        #action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté)
        #               ensuite un Box qui donne le temps d'oisiveté (nombre réel entre 0 et 100)
        """
        dictionary = {
            "robot_actions_lanes": MultiDiscrete([self.parking.number_lanes + 1 for _ in range(self.number_robots)]),
            "robot_actions_sides": MultiDiscrete([2 for _ in range(self.number_robots)]),
            "idleness_date": Discrete(10000000)
        }
        """
        self.action_space = MultiDiscrete([10e4] + [self.parking.number_lanes + 1 for _ in range(self.number_robots)] + [2 for _ in range(self.number_robots)])

        print("action_space_created")
        
        
        #observation_space : Parking, liste de véhicules avec dates,  véhicule porté par chaque robot

        L = []
        self.equivalent_places_lanes = {} #recoit numero de lane, transforme en somme de places depuis la lane 0 (renvoie le numero de la premiere place de la lane)
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            lane_length = self.parking.blocks[block_id].lanes[lane_id].length
            self.equivalent_places_lanes[lane_global_id] = len(L)    
            L = L + [self.max_number_vehicles + 1 for _ in range(lane_length)]
            
        self.total_number_places = len(L)


        #[current_time, robot1_lane, robot2_lane..., robot1_side, robot2_side,..., stock_date_deposit_vehicule1, ..., stock_date_retrieval_vehicule1, ....]
        self.observation_space = MultiDiscrete([10e8] + L + [(self.parking.number_lanes + 1) for _ in range(self.number_robots)] + [2 for _ in range(self.number_robots)] + [10e8 for _ in range(2*self.max_stock_visible)])

        print("observation_space_created")

        self.number_arguments = self.total_number_places + 2*self.number_robots + 2*self.max_stock_visible 

        self.observation = [0]*self.number_arguments
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            init, end = self._dict("lanes", number=lane_global_id)
            self.observation[init:end] = self.parking.blocks[block_id].lanes[lane_id].list_vehicles


        init, end = self._dict("robot_actions_lanes")
        self.observation[init:end] = [0]*self.number_robots

        init, end = self._dict("robot_actions_sides")
        self.observation[init:end] = [0]*self.number_robots
        
        #self.observation["stock_is_active"] = [0]*self.max_stock_visible
        #self.observation["stock_vehicle_id"] = [0]*self.max_stock_visible

        init=self._dict("stock_dates")
        self.observation[init:] =[0]*(2*self.max_stock_visible)
        for i_vehicle, vehicle in enumerate(self.stock.vehicles.values()):
            #self.observation["stock_is_active"][i_vehicle] = 1
            #self.observation["stock_vehicle_id"][i_vehicle] = vehicle.id
            deposit_in_sec = (vehicle.deposit - self.t0).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.t0).total_seconds()
            self.observation[self._dict("stock_dates", number=i_vehicle)] = deposit_in_sec
            self.observation[self._dict("stock_dates", number=i_vehicle, retrieval=True)] =retrieval_in_sec
        

        self.done = False


    def _dict(self, string, number=None, place=None, retrieval=False):
        """
        fonction pour utiliser une liste comme un dictionnaire. Reçoit le nom de ce qui nous intéresse et renvoit l'indice conrrespondant de la liste
        number (id_vehicle ou id_robot) doit commencer en 0, pareil pour place
        """
        if (string == "current_time") or (string =="idleness_date"):
            return 0
        
                
        elif string == "robot_actions_lanes":
            if number == None:
                return 1, self.number_robots+1
            else:
                return 1+number

        elif string == "robot_actions_sides":
            if number == None:
                return  self.number_robots+1,  2*self.number_robots+1
            else:
                return 1+number + self.number_robots

        elif string == "lanes":
            if number == None:    #number lane
                return 2*self.number_robots+1, 2*self.number_robots+ self.total_number_places+1
            elif number != None and not place:
              
                if number == self.parking.number_lanes:
                    return 1+self.equivalent_places_lanes[number] + 2*self.number_robots, self.total_number_places+1 + 2*self.number_robots
                return 1+self.equivalent_places_lanes[number]+2*self.number_robots, 1+self.equivalent_places_lanes[number+1]+2*self.number_robots
            else:
                return  1+self.equivalent_places_lanes[number] + place +2*self.number_robots

        elif string == "stock_dates":
            if number == None:
                return self.total_number_places +2*self.number_robots+1
            else:
                return self.total_number_places + 2*self.number_robots+1 + number + int(retrieval)*self.max_stock_visible
        


    
    def step(self, action):
        self.simulation.algorithm.reward = 0
        self.simulation.algorithm.pending_action = False
        #print( action[self._dict("idleness_date")])
        wake_up_date = self.simulation.t + datetime.timedelta(seconds = int(action[self._dict("idleness_date")]))
        init, end = self._dict("robot_actions_lanes")
        init2, end2 = self._dict("robot_actions_sides")
        self.simulation.algorithm.take_decision(action[init:end], action[init2:end2], self.simulation.t)

        
        while True:
            if self.simulation.t > self.tmax:
                self.done = True
                break          
            if not (self.simulation.events) and not(self.simulation.pending_retrievals):
                self.done = True
                break
            
            if not (self.simulation.events) or self.simulation.events[0].date > wake_up_date:
                heapq.heappush(self.simulation.events, Event(None, wake_up_date, "wake_up_robots", None))
              
                
            self.simulation.next_event()
            # On vérifie si un évènement appelle à une décision
            if self.simulation.algorithm.pending_action:
                break
        
        # On met à jour l'observation
        self.observation[self._dict("current_time")] = (self.simulation.t - self.t0).total_seconds 
        for i_robot, robot in enumerate(self.simulation.robots):
            if robot.doing is None:
                
                self.observation[self._dict("robot_actions_lanes", number=i_robot)] = 0
            else:
                self.observation[self._dict("robot_actions_lanes", number=i_robot)] = self.parking.to_global_id[robot.goal_position[:2]]
                if robot.goal_position[2] == "bottom":
                    self.observation[self._dict("robot_actions_sides", number=i_robot)] = 1
                else:
                    self.observation[self._dict("robot_actions_sides", number=i_robot)] = 0

        self.done = self.done or (not (self.simulation.events) and not(self.simulation.pending_retrievals))

        if self.done:
            #input()
            pass
        return self.observation, self.simulation.algorithm.reward, self.done, {}

    def reset(self):

        self.parking = self.parking._empty_copy()
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)

        self.observation = [0]*self.number_arguments
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            init, end = self._dict("lanes", number=lane_global_id)
            self.observation[init:end] = self.parking.blocks[block_id].lanes[lane_id].list_vehicles
        
        
        init, end = self._dict("robot_actions_lanes")
        self.observation[init:end] = [0]*self.number_robots

        init, end = self._dict("robot_actions_sides")
        self.observation[init:end] = [0]*self.number_robots
        
     

        init=self._dict("stock_dates")
        self.observation[init:] =[0]*(2*self.max_stock_visible)
        for i_vehicle, vehicle in enumerate(self.stock.vehicles.values()):
            #self.observation["stock_is_active"][i_vehicle] = 1
            #self.observation["stock_vehicle_id"][i_vehicle] = vehicle.id
            deposit_in_sec = (vehicle.deposit - self.t0).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.t0).total_seconds()
            self.observation[self._dict("stock_dates", number=i_vehicle)] = deposit_in_sec
            self.observation[self._dict("stock_dates", number=i_vehicle, retrieval=True)] =retrieval_in_sec
        
        
        self.done = False

    def render(self, mode='human', close=False):
        #print(self.simulation.t)
        pass
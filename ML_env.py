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
        print(self.tmax)

        # self.max_stock_visible = 100 + self.parking.size
        self.max_stock_visible = self.max_number_vehicles

        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)

        #action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté)
        #               ensuite un Box qui donne le temps d'oisiveté (nombre réel entre 0 et 100)
    
        dictionary = {
            "robot_actions_lanes": MultiDiscrete([self.parking.number_lanes + 1 for _ in range(self.number_robots)]),
            "robot_actions_sides": MultiDiscrete([2 for _ in range(self.number_robots)]),
            "idleness_date": Discrete(10000000)
        }
        self.action_space = Dict(dictionary)

        print("action_space_created")
        
        
        #observation_space : Parking, liste de véhicules avec dates,  véhicule porté par chaque robot

        d = {}
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            lane_length = self.parking.blocks[block_id].lanes[lane_id].length
            d[f"lane_{lane_global_id}"] = MultiDiscrete([self.max_number_vehicles + 1 for _ in range(lane_length)])
           
        
        d["current_time"] = Box(low=0., high=np.inf, shape=(1,), dtype="float64")
        d["robot_actions_lanes"] = MultiDiscrete([self.parking.number_lanes + 1 for _ in range(self.number_robots)])
        d["robot_actions_sides"] = MultiDiscrete([2 for _ in range(self.number_robots)])
        d["robot_is_carrying"] = MultiDiscrete([self.max_number_vehicles + 1 for _ in range(self.number_robots)])
    
        d["stock_is_active"] = MultiDiscrete([2 for _ in range(self.max_stock_visible)])
  
        #d["stock_vehicle_id"] = MultiDiscrete([list(range(1, (self.max_number_vehicles + 1))) for _ in range(self.max_stock_visible)])
     
        d["stock_dates"] = Box(low=0., high=np.inf, shape=(self.max_stock_visible,2), dtype="float64")
   
        print(d)
        self.observation_space = Dict(d)

        print("observation_space_created")

        self.observation = {}
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            self.observation[f"lane_{lane_global_id}"] = self.parking.blocks[block_id].lanes[lane_id].list_vehicles
        
        self.observation["robot_actions_lanes"] = [0]*self.number_robots
        self.observation["robot_actions_sides"] = [0]*self.number_robots
        
        self.observation["stock_is_active"] = [0]*self.max_stock_visible
        #self.observation["stock_vehicle_id"] = [0]*self.max_stock_visible
        self.observation["stock_dates"] = np.zeros((self.max_stock_visible,2))
        for i_vehicle, vehicle in enumerate(self.stock.vehicles.values()):
            self.observation["stock_is_active"][i_vehicle] = 1
            #self.observation["stock_vehicle_id"][i_vehicle] = vehicle.id
            deposit_in_sec = (vehicle.deposit - self.t0).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.t0).total_seconds()
            self.observation["stock_dates"][i_vehicle] = np.array([deposit_in_sec, retrieval_in_sec])
        

        self.done = False

    def step(self, action):
        self.simulation.algorithm.reward = 0
        self.simulation.algorithm.pending_action = False
        wake_up_date = self.simulation.t + datetime.timedelta(seconds = action["idleness_date"])
        self.simulation.algorithm.take_decision(action["robot_actions_lanes"], action["robot_actions_sides"], self.simulation.t)

        
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
        self.observation["current_time"] = (self.simulation.t - self.t0).total_seconds 
        for i_robot, robot in enumerate(self.simulation.robots):
            if robot.doing is None:
                self.observation["robot_actions_lanes"][i_robot] = 0
            else:
                self.observation["robot_actions_lanes"][i_robot] = self.parking.to_global_id[robot.goal_position[:2]]
                if robot.goal_position[2] == "bottom":
                    self.observation["robot_actions_sides"][i_robot] = 1
                else:
                    self.observation["robot_actions_sides"][i_robot] = 0

        self.done = self.done or (not (self.simulation.events) and not(self.simulation.pending_retrievals))

        if self.done:
            #input()
            pass
        return self.observation, self.simulation.algorithm.reward, self.done, {}

    def reset(self):

        self.parking = self.parking._empty_copy()
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)

        self.observation = {}
        for lane_global_id in range(1, self.parking.number_lanes+1):
            block_id, lane_id = self.parking.dict_lanes[lane_global_id]
            self.observation[f"lane_{lane_global_id}"] = self.parking.blocks[block_id].lanes[lane_id].list_vehicles
        
        self.observation["robot_actions_lanes"] = [0]*self.number_robots
        self.observation["robot_actions_sides"] = [0]*self.number_robots
        
        self.observation["stock_is_active"] = [0]*self.max_stock_visible
        #self.observation["stock_vehicle_id"] = [0]*self.max_stock_visible
        self.observation["stock_dates"] = np.zeros((self.max_stock_visible,2))
        for i_vehicle, vehicle in enumerate(self.stock.vehicles.values()):
            self.observation["stock_is_active"][i_vehicle] = 1
            #self.observation["stock_vehicle_id"][i_vehicle] = vehicle.id
            deposit_in_sec = (vehicle.deposit - self.t0).total_seconds()
            retrieval_in_sec = (vehicle.retrieval - self.t0).total_seconds()
            self.observation["stock_dates"][i_vehicle] = np.array([deposit_in_sec, retrieval_in_sec])
        
        
        self.done = False

    def render(self, mode='human', close=False):
        #print(self.simulation.t)
        pass
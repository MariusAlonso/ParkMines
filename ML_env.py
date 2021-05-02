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
        self.dict_lanes = self.parking.dict_lanes
        self.number_robots = 4
        self.stock = RandomStock(30, time = datetime.timedelta(days=1000))
        self.number_vehicles = 100
        self.number_lanes = self.parking.number_lanes

        self.simulation = Simulation(datetime.datetime(1,1,1,0,0,0,0), self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, print_in_terminal=False)

        #action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté)
        #               ensuite un Box qui donne le temps d'oisiveté (nombre réel entre 0 et 100)
    
        self.action_space = Dict({"robot_actions": MultiDiscrete([list(range(0, (self.number_lanes + 1))) for _ in range(self.number_robots)]), "idleness_time": Box(0, 100, (1,))})
        
        #observation_space : Parking, liste de véhicules avec dates,  véhicule porté par chaque robot
        
        self.observation_space = Dict({"parking": Box(0, self.number_vehicles, (self.parking.number_lanes, self.parking.nb_max_lanes)),"tasks": Box() , "robot_is_doing": MultiDiscrete([list(range(0, (self.number_vehicles + 1))) for _ in range(self.number_robots)])})


        self.done = False

    def step(self, action):
        self.simulation.algorithm.reward = 0
        self.simulation.algorithm.pending_action = False
        wake_up_date = action["idleness_time"]
        self.simulation.algorithm.take_decision(action["robot_actions"], self.simulation.t)

        while True:
            if not (self.simulation.events) and not(self.simulation.pending_retrievals):
                self.done = True
                break
            if not (self.simulation.events) or self.simulation.events[0].date > wake_up_date:
                heapq.heappush(self.simulation.events, Event(None, wake_up_date, "wake_up_robots", None))
            self.simulation.next_event()
            # On vérifie si un évènement appelle à une décision
            if self.simulation.algorithm.pending_action:
                break
        
        # Il reste à construire l'observation

        self.done = not (self.simulation.events) and not(self.simulation.pending_retrievals)
        return self.simulation.algorithm.reward, self.done, self.observation

    def reset(self):

        self.parking = self.parking._empty_copy()
        self.stock = RandomStock(30, time = datetime.timedelta(days=1000))
        self.simulation = Simulation(datetime.datetime(1,1,1,0,0,0,0), self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, print_in_terminal=False)

        self.done = False

    def render(self, mode='human', close=False):
        pass
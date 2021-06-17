import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Dict, Discrete, Box, Tuple, MultiDiscrete
from parking import *
from vehicle import *



class MLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.parking_init = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 15, 10), Block([Lane(1, 4), Lane(2, 4)]), Block([],6,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        self.dict_lanes = self.parking_init.dict_lanes
        self.number_robots = 4
        self.stock = RandomStock(30, time = datetime.timedelta(days=1000))
        self.number_vehicles = 100
        self.number_lanes = self.parking_init.number_lanes

        #action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté)
        #               ensuite un Box qui donne le temps d'oisiveté (nombre réel entre 0 et 100)
    
        self.action_space = Dict({"robot_actions": MultiDiscrete([list(range(0, (self.number_lanes + 1))) for _ in range(self.number_robots)]), "idleness_time": Box(0, 100, (4,))})
        
        #observation_space : Parking, liste de véhicules avec dates,  véhicule porté par chaque robot
        
        self.observation_space = Dict({"parking": Box(0, self.number_vehicules, (self.parking_init.number_lanes, self.parking_init.nb_max_lanes)),"tasks": Box() , "robot_is_doing": Multidiscrete([list(range(0, (self.number_vehicles + 1))) for _ in range(self.number_robots)])})


        self.reward = 0
        self.done = False

    def step(self, action):
        #si fin de partie
        if (self.taux_occupation_parking > 0.9):
            self.reset()

        #
        

        return self.reward, self.done, self.observation
    def reset(self):
        pass
    def render(self, mode='human', close=False):
        pass
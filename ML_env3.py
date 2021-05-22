import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Dict, Discrete, Box, Tuple, MultiDiscrete
from simulation import *
from parking import *
from rl import rl_algorithm_builder



class MLEnv(gym.Env):
    

    def __init__(self, display = False):
        real_parking = Parking([BlockInterface([],10,1), Block([], 15, 7,"leftrigth"), Block([], 14, 7,"leftrigth"), Block([], 13, 6,"leftrigth"), Block([], 8, 7,"leftrigth"), Block([], 18, 7,"leftrigth"), Block([], 10, 11), Block([], 15, 1, "leftrigth")], [['s','s', 'f0:6', 'f0:6', 'e', 4, 6], [7,1,1,2,'f0:3', 4,6], [7,1,1,2,3,'f0:2', 6], [7,1,1,2,3,5,6], [7,'e','e','e',3,5,6], [7,'e','e','e','e',5,6], [7,'f7:0',0,0,0,5,6]])
        tiny_parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 1, 2), Block([Lane(1, 2), Lane(2, 2)]), Block([],1,3)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
        self.parking = tiny_parking
        self.number_robots = 1
        self.simulation_length = 3
        self.daily_flow = 9
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        self.max_number_vehicles = int(self.simulation_length*self.daily_flow*3)
        self.display = display
        self.last_step_t = None
        self.max_stock_visible = self.max_number_vehicles
        self.number_arguments = self.parking.number_lanes + self.number_robots + self.max_stock_visible +1
        
        self.t0 = datetime.datetime(2021,1,1,0,0,0,0)
        self.tmax  = self.t0 + datetime.timedelta(days=self.simulation_length+45)
        

        RLAlgorithm = rl_algorithm_builder(None, self._dict, self.number_arguments)
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=True)

        if self.display:
            #self.simulation.start_display(time_interval=1.)
            pass

        #action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté)
        #               ensuite un Box qui donne le temps d'oisiveté (nombre réel entre 0 et 100)
        
        #self.action_space = MultiDiscrete([10e2] + [self.parking.number_lanes + 1 for _ in range(self.number_robots)] + [2 for _ in range(self.number_robots)])
        Linf = np.array([0]*(2*self.number_robots + 1))
        #Lsup = np.array([10e4]+[self.parking.number_lanes + 0.9]*self.number_robots + [1]*self.number_robots)
        #self.action_space = Box(low=Linf, high=Lsup, shape=(2*self.number_robots + 1,))

        Lsup2 = [1000]+[self.parking.number_lanes + 1]*self.number_robots + [2]*self.number_robots
        self.action_space = MultiDiscrete(Lsup2)
        


        print(self.action_space)
        print("action_space_created")
        
        
        


        #[current_time, robot1_lane, robot2_lane..., robot1_side, robot2_side,..., stock_date_deposit_vehicule1, ..., stock_date_retrieval_vehicule1, ....]
        
        
        Linf = np.zeros((self.number_arguments, self.parking.nb_max_lanes+2))
        Lsup = np.zeros((self.number_arguments, self.parking.nb_max_lanes+2))
        Lsup[0,0] = np.inf
        for id_robot in range(self.number_robots):    #id des robots commencent a 0
            Lsup[id_robot+1,0], Lsup[id_robot+1,1] = self.parking.number_lanes, 1
            Lsup[id_robot+1,2], Lsup[id_robot+1,3] = 1, np.inf
        
        for id_global_lane in range (1, self.parking.number_lanes+1):
            id_block, id_lane = self.parking.dict_lanes[id_global_lane]
            lane = self.parking.blocks[id_block].lanes[id_lane]
            Lsup[self.number_robots+id_global_lane, 0:2] = np.array([lane.length]*2)
            Lsup[self.number_robots+id_global_lane, 2:(lane.length+2)] = np.array([np.inf]*lane.length)

        Lsup[self.number_robots+self.parking.number_lanes+1:, 0:2] = np.inf*np.ones((self.max_stock_visible, 2))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 2] = np.ones((self.max_stock_visible,))
        
        self.observation_space = Box(low=Linf, high=Lsup, shape=(self.number_arguments, self.parking.nb_max_lanes+2))

        #input()
        print(self.observation_space)
        print("observation_space_created")
       
        self.observation = self.simulation.algorithm.observation

        self.done = False


    def _dict(self, string, number=None, place=None, retrieval=False, action_space = False):
        """
        fonction pour utiliser une liste comme un dictionnaire. Reçoit le nom de ce qui nous intéresse et renvoit l'indice conrrespondant de la liste
        number (id_vehicle ou id_robot) doit commencer en 0, pareil pour place
        """
        if (string == "current_time"):
            return (0,0)

        elif (string =="idleness_date"):
            return 0
        
                
        elif string == "robot_actions_lanes":
            if number == None:
                return 1, self.number_robots+1
            else:
                return 1+number, 0

        elif string == "robot_actions_sides":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 1
            else:
                if number == None:
                    return  1+self.number_robots, 2*self.number_robots+1
                else:
                    return 1+number+self.number_robots

        elif string == "robot_actions_is_carrying":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 2
            else:
                pass

        elif string == "robot_actions_vehicles":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 3
            else:
                pass


        elif string == "lanes_ends":
            return self.number_robots+number

        elif string == "lanes":
            if number == None:    #number lane
                return self.number_robots+1, self.number_robots + self.parking.number_lanes +1

            elif number is not None and place is None:
                id_block, id_lane = self.parking.dict_lanes[number]
                lane = self.parking.blocks[id_block].lanes[id_lane]
                return self.number_robots+number, lane.length 
              
            else:
                return  self.number_robots+number, place+2

        elif string == "stock_dates":
            if number == None:
                return self.parking.number_lanes + self.number_robots+1, int(retrieval)
            else:
                return self.parking.number_lanes + self.number_robots+1 + number, int(retrieval)
        


    
    def step(self, action):
        self.last_step_t = self.simulation.t
        self.simulation.algorithm.reward = 0
        self.simulation.algorithm.pending_action = False
        #if action[0]=='nan':
            #return self.observation, -10e20, True, {}
        wake_up_date = self.simulation.t + datetime.timedelta(minutes= 10*int(action[self._dict("idleness_date")]))
        init, end = self._dict("robot_actions_lanes")
        init2, end2 = self._dict("robot_actions_sides", action_space=True)
        self.simulation.algorithm.take_decision(action[init:end].astype(int), np.around(action[init2:end2]).astype(int), self.simulation.t)
        
        #self.simulation.algorithm.take_decision(action, self.simulation.t)

        
        while True:

            if self.simulation.t > self.tmax:
                self.done = True
                print("Ohh... la simulation est arrivée à la fin des temps")
                break          
            if not self.simulation.vehicles_left_to_handle:
                self.done = True
                print("Bien joué, vous avez réussi tous les évènements")
                break

            self.simulation.next_event()
            # On vérifie si un évènement appelle à une décision
            if self.simulation.algorithm.pending_action:
                break

        # Calcul de la récompense
        
        for event_deposit in self.simulation.pending_deposits:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - event_deposit.vehicle.deposit).total_seconds()/3600
            else:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - max(self.last_step_t, event_deposit.vehicle.deposit)).total_seconds()/3600
        for event_retrieval in self.simulation.pending_retrievals:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - event_retrieval.vehicle.retrieval).total_seconds()/3600
            else:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - max(self.last_step_t, event_retrieval.vehicle.retrieval)).total_seconds()/3600
        """
        for lane in self.observation.data[self._dict("lanes")[0]: self._dict("lanes")[1]]:
            self.lanes_occupated = 0
            if not (lane==0.).all():
                self.lanes_occupated += 1
        self.simulation.algorithm.reward -= 10*self.lanes_occupated
        """
        if not (self.simulation.events) and not(self.simulation.pending_retrievals):
            print("Bien joué, vous avez réussi tous les évènements !")
        #self.done = self.done or (not (self.simulation.events) and not(self.simulation.pending_retrievals))

        self.done = self.done or not self.simulation.vehicles_left_to_handle

        return self.observation.data, self.simulation.algorithm.reward, self.done, {}

    def reset(self):

        self.parking = self.parking._empty_copy()
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        self.last_step_t = None
        if self.display:
            #self.simulation.display.shutdown()
            pass
        RLAlgorithm = rl_algorithm_builder(None, self._dict, self.number_arguments)
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)
        if self.display:
            #self.simulation.start_display(time_interval=1.)
            pass

        
        self.observation = self.simulation.algorithm.observation
        
        self.done = False
        return self.observation.data
        

    def render(self, mode='human', close=False):
        print(self.simulation.t)
        #display = Display(self.simulation.t, self.stock, [Robot(1), Robot(2)], real_parking, AlgorithmUnimodal, 12, 20, print_in_terminal = False)
        #print("stock_dates=", self.observation.data[self._dict("stock_dates")[0]:self._dict("stock_dates")[0]+7, 0:2])
        print("lanes=", self.observation.data[self._dict("lanes")[0]: self._dict("lanes")[1]])
        print("robot_actions_lanes=", self.observation.data[self._dict("robot_actions_lanes")[0]:self._dict("robot_actions_lanes")[1], 0])
        print(self.simulation.pending_deposits)
        print(self.simulation.pending_retrievals)
        print(self.simulation.parking)
        #print(self.observation)


        if self.display:
            """
            self.simulation.start_display()       
            self.simulation.display.update()
            self.simulation.display.shutdown()
            """
            pass


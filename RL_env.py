import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Dict, Discrete, Box, Tuple, MultiDiscrete
from simulation import *
from RL_algorithm import rl_algorithm_builder



class MLEnv(gym.Env):
    

    def __init__(self, parking, max_stock_visible, number_robots, daily_flow, simulation_length, display = False):

        ###########################################################################################
        ########################### Hyperparamètres ###############################################
        ###########################################################################################

        self.parking = parking

        # Nombre de véhicules visibles pour l'algorithme (on ne montre pas la totalité des véhicules en même temps pour de soucis de complexité)
        self.max_stock_visible = max_stock_visible

        self.number_robots = number_robots

        # Duree de la simulation
        self.simulation_length = simulation_length

        # Nombre moyen de véhicules qui arrivent au parking par jour
        self.daily_flow = daily_flow
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        

        ###########################################################################################
        ######################## Paramètres et Rewards ############################################
        ###########################################################################################

        
        # Temps maximal de retard admis
        self.time_max_waiting = 1*24*3600   

        # Reward infligée à l'algorithme lors de l'apprentissage lorsqu'il se suicide
        self.max_penalty = 1e7

        # Penalisation pour chaque client qui attend (deposit et retrieval)
        self.penalty_lateness = 0


        ###########################################################################################
        ############################## Statistiques ###############################################
        ###########################################################################################

        # Proportion des réveils où l'algorithme donne quelquechose à faire au robot, par rapport au nombre de réveil total dans la simulation
        self.robot_action_avg = 0.
        
        # Nombre d'appels à l'algorithme de RL
        self.nb_actions = 0

        # Nombre d'heures cumulées d'attente client pour une simulation
        self.client_unsatisfaction = 0.

        # Durée d'une simulation
        self.sim_duration = 0.


        ###########################################################################################
        ###################### Temps et autres paramètres #########################################
        ###########################################################################################

        # Date de dernière prise de décision du robot
        self.last_step_t = None 
        self.t0 = datetime.datetime(2021,1,1,0,0,0,0)

        # Temps maximal de la simulation, au-delà duquel la simulation s'arrête
        self.tmax  = self.t0 + datetime.timedelta(days=self.simulation_length+45)

        # Nombre total de variables de décision 
        self.number_arguments = self.parking.number_lanes + self.number_robots + self.max_stock_visible +1

        # Largeur de l'observation_space
        self.table_width = max(self.parking.longest_lane + 2, 7)

        # Création de l'algorithme et de la simulation
        RLAlgorithm = rl_algorithm_builder(None, self._dict, self.number_arguments, self.max_stock_visible)
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=True)

        
        ###########################################################################################
        ################################ Action_space #############################################
        ###########################################################################################

        # action_space : pour chaque robot un Discrete avec le numéro de lane où il va effectuer la tâche (0 correpond à oisiveté) 
        #                et 0 ou 1 pour indiquer le côte de la lane (top / bottom). Enfin un paramètre (0/1) pour savoir si le robot va ètre actif
        #                lors du prochain step
        #                 
        # Structure : 
        #               [1] : n'a aucun rôle
        #               [2]*self.number_robots + [self.parking.number_lanes]*self.number_robots : side et lane où le robot commence l'action
        #               [2]*self.number_robots + [self.parking.number_lanes]*self.number_robots : side et lane où le robot finit l'action

        action_space = [1]+[2]*self.number_robots+[self.parking.number_lanes]*self.number_robots + [2]*self.number_robots+[self.parking.number_lanes]*self.number_robots + [2]*self.number_robots
        self.action_space = MultiDiscrete(action_space)
        print(self.action_space)
        print("action_space_created")
        
        
        ###########################################################################################
        ########################### Observation_space #############################################
        ###########################################################################################        

        # observation_space : matrice
        #
        # Structure : 
        #               temps courant
        #               
        #
        #

        #[current_time, robot1_lane, robot2_lane..., robot1_side, robot2_side,..., stock_date_deposit_vehicule1, ..., stock_date_retrieval_vehicule1, ....]
        
        Linf = np.zeros((self.number_arguments, self.table_width))
        Lsup = np.zeros((self.number_arguments, self.table_width))
        Lsup[0,0] = 0
        for id_robot in range(self.number_robots):    #id des robots commencent a 0
            Lsup[id_robot+1,0], Lsup[id_robot+1,1] = self.parking.number_lanes, 1
            Lsup[id_robot+1,2], Lsup[id_robot+1,3] = self.parking.number_lanes, 1
            Lsup[id_robot+1,4], Lsup[id_robot+1,5] = 1, np.inf
            Linf[id_robot+1,5] = - np.inf
        
        for id_global_lane in range (1, self.parking.number_lanes+1):
            id_block, id_lane = self.parking.dict_lanes[id_global_lane]
            lane = self.parking.blocks[id_block].lanes[id_lane]
            Lsup[self.number_robots+id_global_lane, 0:2] = np.array([lane.length]*2)
            Lsup[self.number_robots+id_global_lane, 2:(lane.length+2)] = np.array([np.inf]*lane.length)
            Linf[self.number_robots+id_global_lane, 2:(lane.length+2)] = - np.array([np.inf]*lane.length)

        Lsup[self.number_robots+self.parking.number_lanes+1:, 0:2] = np.inf*np.ones((self.max_stock_visible, 2))
        Linf[self.number_robots+self.parking.number_lanes+1:, 0:2] = - np.inf*np.ones((self.max_stock_visible, 2))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 2] = np.ones((self.max_stock_visible,))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 3] = np.inf*np.ones((self.max_stock_visible,))
        Linf[self.number_robots+self.parking.number_lanes+1:, 3] = - np.inf*np.ones((self.max_stock_visible,))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 4] = self.parking.number_lanes*np.ones((self.max_stock_visible,))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 5] = self.parking.longest_lane*np.ones((self.max_stock_visible,))
        Lsup[self.number_robots+self.parking.number_lanes+1:, 6] = np.ones((self.max_stock_visible,))
        
        self.observation_space = Box(low=Linf, high=Lsup, shape=(self.number_arguments, self.table_width))

        #input()
        print(self.observation_space)
        print("observation_space_created")
       
        self.observation = self.simulation.algorithm.observation

        self.done = False
        self.simulation.next_event()


    def _dict(self, string, number=None, place=None, retrieval=False, action_space = False):
        """
        fonction pour utiliser une liste comme un dictionnaire. Reçoit le nom de ce qui nous intéresse et renvoit l'indice conrrespondant de la liste
        number (id_vehicle ou id_robot) doit commencer en 0, pareil pour place
        """
        if (string == "current_time"):
            return (0,0)

        elif (string =="idleness_date"):
            return 0
        
                
        elif string == "robot_pick_lane":
            if not action_space:
                if number == None:
                    return 1, self.number_robots+1
                else:
                    return 1+number, 0
            else:
                if number == None:
                    return  1+self.number_robots, 2*self.number_robots+1
                else:
                    return 1+number+self.number_robots

        elif string == "robot_pick_side":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 1
            else:
                if number == None:
                    return  1+2*self.number_robots, 3*self.number_robots+1
                else:
                    return 1+number+self.number_robots

        elif string == "robot_drop_lane":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 2
            else:
                if number == None:
                    return  1+3*self.number_robots, 4*self.number_robots+1
                else:
                    return 1+number+2*self.number_robots

        elif string == "robot_drop_side":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 3
            else:
                if number == None:
                    return  1+4*self.number_robots, 5*self.number_robots+1
                else:
                    return 1+number+3*self.number_robots

            
        elif string == "robot_actions_is_carrying":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 4
            else:
                pass

        elif string == "robot_actions_vehicles":
            if not action_space:
                if number == None:
                    return  1, self.number_robots+1
                else:
                    return 1+number, 5
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
        
        self.robot_action_avg = (self.robot_action_avg*self.nb_actions + action[1])/(self.nb_actions+1)
        self.nb_actions += 1
        self.simulation.algorithm.take_decision(action, self.simulation.t)

        
        while True:
            #print(self.observation.data)

            if self.simulation.t > self.tmax:
                self.done = True
                break          
            if not self.simulation.vehicles_left_to_handle:
                self.done = True
                break

            self.simulation.next_event()
            # On vérifie si un évènement appelle à une décision
            if self.simulation.algorithm.pending_action:
                break

        # Calcul de la récompense

            """

        # REWARD Pendalisation pour chaque client qui attend, proportionnellement au temps attendu (deposit et retrieval)

        for event_deposit in self.simulation.pending_deposits:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - event_deposit.vehicle.deposit).total_seconds()/3600
            else:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - max(self.last_step_t, event_deposit.vehicle.deposit)).total_seconds()/3600

                # SUICIDE la simulation s'arrête lorsqu'un véhicule attend plus que self.time_max_waiting et il est pénalisé

                if (self.simulation.t - event_deposit.vehicle.deposit).total_seconds() > self.time_max_waiting:
                    self.simulation.algorithm.reward = - self.max_penalty
                    self.done = True
                    
        for event_retrieval in self.simulation.pending_retrievals:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - event_retrieval.vehicle.retrieval).total_seconds()/3600
                
            else:
                self.simulation.algorithm.reward -= 50*(self.simulation.t - max(self.last_step_t, event_retrieval.vehicle.retrieval)).total_seconds()/3600

                # SUICIDE la simulation s'arrête lorsqu'un véhicule attend plus que self.time_max_waiting et il est pénalisé

                if (self.simulation.t - event_retrieval.vehicle.retrieval).total_seconds() > self.time_max_waiting:
                    self.simulation.algorithm.reward = - self.max_penalty
                    self.done = True
            """

        # REWARD Pendalisation de -1 pour chaque client qui attend (deposit et retrieval)

        for event_deposit in self.simulation.pending_deposits:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= self.penalty_lateness
                self.total_waiting_time += (self.simulation.t - event_deposit.vehicle.deposit).total_seconds()/3600
            else:
                self.simulation.algorithm.reward -= self.penalty_lateness
                self.total_waiting_time += (self.simulation.t - max(self.last_step_t, event_deposit.vehicle.deposit)).total_seconds()/3600

                # SUICIDE la simulation s'arrête lorsqu'un véhicule attend plus que self.time_max_waiting et il est pénalisé

                if (self.simulation.t - event_deposit.vehicle.deposit).total_seconds() > self.time_max_waiting:
                    # self.simulation.algorithm.reward = - self.max_penalty
                    self.done = True

        for event_retrieval in self.simulation.pending_retrievals:
            if self.last_step_t is None:
                self.simulation.algorithm.reward -= self.penalty_lateness
                self.total_waiting_time += (self.simulation.t - event_retrieval.vehicle.retrieval).total_seconds()/3600
                
            else:
                self.simulation.algorithm.reward -= self.penalty_lateness
                self.total_waiting_time += (self.simulation.t - max(self.last_step_t, event_retrieval.vehicle.retrieval)).total_seconds()/3600

                # SUICIDE la simulation s'arrête lorsqu'un véhicule attend plus que self.time_max_waiting et il est pénalisé

                if (self.simulation.t - event_retrieval.vehicle.retrieval).total_seconds() > self.time_max_waiting:
                    # self.simulation.algorithm.reward = - self.max_penalty
                    self.done = True

        
                   
        """
        # Pénalisation lorsque le robot commence de nouvelles lanes

        for lane in self.observation.data[self._dict("lanes")[0]: self._dict("lanes")[1]]:
            self.lanes_occupated = 0
            if not (lane==0.).all():
                self.lanes_occupated += 1
        self.simulation.algorithm.reward -= 10*self.lanes_occupated
        """
        self.done = self.done or not self.simulation.vehicles_left_to_handle

        if self.done:
            self.sim_duration = (self.simulation.t - self.t0).total_seconds()/3600
            self.client_unsatisfaction = self.total_waiting_time
    

        return self.observation.data, self.simulation.algorithm.reward, self.done, {}

    def reset(self):

        self.parking = self.parking._empty_copy()
        self.stock = RandomStock(self.daily_flow, time = datetime.timedelta(days=self.simulation_length))
        self.last_step_t = None
        self.robot_action_avg = 0.
        self.total_waiting_time = 0
        self.nb_actions = 0
        self.nb_services_completed = 0
        RLAlgorithm = rl_algorithm_builder(None, self._dict, self.number_arguments, self.max_stock_visible)
        self.simulation = Simulation(self.t0, self.stock, [Robot(k) for k in range(self.number_robots)], self.parking, RLAlgorithm, order=False, print_in_terminal=False)
        self.observation = self.simulation.algorithm.observation
        
        self.done = False
        self.simulation.next_event()

        return self.observation.data
        

    def render(self, mode='human', close=False):

        print(self.simulation.t)
        print(self.simulation.pending_deposits)
        print(self.simulation.pending_retrievals)
        print(self.simulation.parking)

if __name__ == "__main__":
    """
    Test de l'environement en mode aléatoire
    """
    parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 1, 2), Block([Lane(1, 2), Lane(2, 2)]), Block([],1,4)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
    env = MLEnv(parking, 10, 1)

    episodes = 0

    for episode in range(1, episodes+1):
        env.reset()
        done = False
        score = 0 
        while not done:
            
            env.render()
            action = env.action_space.sample()
            
            n_state, reward, done, info = env.step(action)
            score+=reward
            print(score)

        print('Episode:{} Score:{}'.format(episode, score))
    env.close()


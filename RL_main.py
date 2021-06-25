import gym
import numpy as np
import copy
import RL_save
from parking import *
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from RL_env import MLEnv
from performances import Performance
from RL_algorithm import rl_algorithm_builder
from robot import Robot
from simulation import Simulation
from vehicle import RandomStock
import datetime

import tensorflow as tf
from stable_baselines.common.callbacks import BaseCallback

class TensorboardCallback(BaseCallback):
    """
    Custom callback for plotting additional values in tensorboard.
    """
    def __init__(self, verbose=0):
        self.is_tb_set = False
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Log scalar value (here a random variable)
        environment = self.model.get_env()
        value = environment.envs[0].robot_action_avg
        summary = tf.Summary(value=[tf.Summary.Value(tag='robot_activity', simple_value=value)])
        self.locals['writer'].add_summary(summary, self.num_timesteps)

        value = environment.envs[0].client_unsatisfaction
        summary = tf.Summary(value=[tf.Summary.Value(tag='client_unsatisfaction', simple_value=value)])
        self.locals['writer'].add_summary(summary, self.num_timesteps)

        return True




        #########################################################################################
        ############################## Apprentissage ############################################
        #########################################################################################

learning = True           #True si on veut procéder à l'apprentissage d'un modèle
saving = True              #True si on veut sauvegarder le modèle
timesteps = int(8e5)         #Nombre de timesteps dans l'apprentissage

# parking et environnement pour l'apprentissage du modèle

parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 1, 5), Block([Lane(1, 2), Lane(2, 2)]), Block([],1,4)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
env = MLEnv(parking, 10, 1, 3, 3)

if learning:
    model = PPO2(MlpPolicy, env, verbose=1, tensorboard_log="./RL12tensorboard/")
    model.learn(total_timesteps=timesteps, callback=TensorboardCallback())
    RLAlgorithm = rl_algorithm_builder(model, env._dict, env.number_arguments, env.max_stock_visible, True)
    if saving:
        brain = RL_save.Brain()
        brain.save(model, timesteps, env.max_stock_visible, env.number_robots, env.daily_flow, env.simulation_length)


        #########################################################################################
        ############## Résultat du modèle entraîné sur une simulation ###########################
        #########################################################################################


# Le nom du fichier où se trouve le modèle qu'on veut visualiser

name = "models_RL/800000_2021-06-21T17-01-54"  

# Récupération du modèle et création de l'environnement adapté

brain = RL_save.Brain()
model, max_stock_visible, number_robots, daily_flow, simulation_length = brain.load(name)
env = MLEnv(parking, max_stock_visible, number_robots, daily_flow, simulation_length)
RLAlgorithm = rl_algorithm_builder(model, env._dict, env.number_arguments, env.max_stock_visible)
stock = RandomStock(env.daily_flow, datetime.timedelta(days=env.simulation_length))

# Simulation 

simulation = Simulation(env.t0, stock, [Robot(1)], env.parking, RLAlgorithm, order=False, print_in_terminal = True)
simulation.start_display(12, 20)
simulation.display.run()



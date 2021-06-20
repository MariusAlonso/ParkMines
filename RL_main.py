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



parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 1, 2), Block([Lane(1, 2), Lane(2, 2)]), Block([],1,4)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
env = MLEnv(parking, 10, 1, 3, 3)


        #########################################################################################
        ############################## apprentissage ############################################
        #########################################################################################

learning = True            #True si on veut procéder à l'apprentissage d'un modèle
saving = True              #True si on veut sauvegarder le modèle
timesteps = int(1e6)         #Nombre de timesteps dans l'apprentissage


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

name = "models_RL/1000000_2021-06-20T15-19-19"

brain = RL_save.Brain()
model, max_stock_visible, number_robots, daily_flow, simulation_length = brain.load(name)
env = MLEnv(parking, max_stock_visible, number_robots, daily_flow, simulation_length)
RLAlgorithm = rl_algorithm_builder(model, env._dict, env.number_arguments, env.max_stock_visible)

stock = RandomStock(env.daily_flow, datetime.timedelta(days=env.simulation_length))
simulation = Simulation(env.t0, stock, [Robot(1)], env.parking, RLAlgorithm, order=False, print_in_terminal = True)
simulation.start_display(12, 20)
simulation.display.run()

def evaluate_model(model, repetition, _input=False):
    statics = []
    for iteration in range(repetition):
        obs = env.reset()
        #input()
        done = False
        score = 0
        i=0
        last_obs_lane = obs[env._dict("lanes")[0]: env._dict("lanes")[1]]
        while not done:
            print(env.observation.data)
            print(env.simulation.t)
            input("")
            action, _states = model.predict(obs)
            obs, reward, done, info = env.step(action)
            i+=1
            obs_lane = obs[env._dict("lanes")[0]: env._dict("lanes")[1]]
            if i==1000 and not _input:
                print("score=", score)
                i=0
                env.render()
            score+=reward
            if _input:
                if (last_obs_lane != obs_lane).any():
                    env.render()
                    input()
                last_obs_lane = copy.deepcopy(obs_lane)
        env.render()
        print(f'score final={score} of iteration {iteration+1}/{repetition}')
        statics.append(score)
    return statics


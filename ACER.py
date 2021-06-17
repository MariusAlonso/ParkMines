import gym
import numpy as np
import copy
from parking import *
"""
import ray
from ray import tune
from ray.rllib.agents.ppo import PPOTrainer
"""
# from stable_baselines import ACER
from stable_baselines.common.vec_env import DummyVecEnv
# from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from ML_env4 import MLEnv
from performances import Performance
from rl import rl_algorithm_builder
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
        return True


"""
environment_name =

env = gym.make(environment_name)
"""
parking = Parking([BlockInterface([Lane(1, 1), Lane(2, 1), Lane(3, 1)]), Block([], 1, 2), Block([Lane(1, 2), Lane(2, 2)]), Block([],1,4)], [[0,0,0,0],["s",1,1,1],[2,2,3,"e"]])
env = MLEnv(parking, 10, 1)
print("Enivronnement créé")
#fonctionnement aleatoire

episodes = 0
for episode in range(1, episodes+1):
    env.reset()
    done = False
    score = 0 
    while not done:
        
        env.render()
        action = env.action_space.sample()
        
        n_state, reward, done, info = env.step(action)
        """
        if reward !=0:
            print(n_state[env._dict("stock_dates")[0]:,0], reward, done, info)
        """
        #input()
        score+=reward
        print(score)
    print('Episode:{} Score:{}'.format(episode, score))
env.close()




#apprentissage

# env = DummyVecEnv([lambda: env])

learning = True
saving = True
timesteps = 10000000




if learning:
    model = PPO2(MlpPolicy, env, verbose=1, tensorboard_log="./RL10tensorboard/")

    model.learn(total_timesteps=timesteps, callback=TensorboardCallback())

    if saving:

        model.save("RL11")
        del model # remove to demonstrate saving and loading

model = PPO2.load("RL11")


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

            #input()

        env.render()
        print(f'score final={score} of iteration {iteration+1}/{repetition}')
        statics.append(score)
        #env.render()
    return statics


#statics = evaluate_model(model, 10, _input=True)
#print(f'statics_{timesteps} = {statics}')

RLAlgorithm = rl_algorithm_builder(model, env._dict, env.number_arguments, env.max_stock_visible, True)
"""
performance = Performance(env.t0, (env.daily_flow, datetime.timedelta(days=env.simulation_length)), [Robot(k) for k in range(env.number_robots)], env.parking, RLAlgorithm)
performance.printAverageDashboard(10)
"""
stock = RandomStock(env.daily_flow, datetime.timedelta(days=env.simulation_length))
simulation = Simulation(env.t0, stock, [Robot(1)], env.parking, RLAlgorithm, order=False, print_in_terminal = True)
simulation.start_display(12, 20)
simulation.display.run()


"""
# ray.init(include_dashboard=False)
tune.run(PPOTrainer, config={"env": env}) 
"""


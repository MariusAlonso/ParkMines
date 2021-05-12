import gym 

from ray import tune
from ray.rllib.agents.ppo import PPOTrainer
# from stable_baselines import ACER
from stable_baselines.common.vec_env import DummyVecEnv
# from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from ML_env3 import MLEnv

"""
environment_name =

env = gym.make(environment_name)
"""
env = MLEnv()
print("Enivronnement créé")
#fonctionnement aleatoire

episodes = 10
for episode in range(1, episodes+1):
    env.reset()
    done = False
    score = 0 
    
    while not done:
        
        env.render()
        action = env.action_space.sample()
        #print(env.step(action))
        n_state, reward, done, info = env.step(action)
        #input()
        score+=reward
    print('Episode:{} Score:{}'.format(episode, score))
env.close()




#apprentissage

env = MLEnv()

# env = DummyVecEnv([lambda: env])
model = PPO2(MlpPolicy, env, verbose=1)


model.learn(total_timesteps=100000)

"""
tune.run(PPOTrainer, config={"env": env}) 
"""

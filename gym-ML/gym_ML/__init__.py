from gym.envs.registration import register

register(
    id='ML-v0',
    entry_point='gym_ML.envs:MLEnv')
import gym
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.env_checker import check_env
from stable_baselines import PPO2

import EP_Environment as epenv
import os

import ray
from ray.tune.registry import register_env

config = {"num_team_a": 1, "num_team_b": 1, "width": 5, "height": 3, "density": 0.0, "max_turns": 50}
a_config = {"hp": 30, "skill": 50, "fray": 40, "dmg": "2d10+6"}
b_config = {"hp": 30, "skill": 50, "fray": 40, "dmg": "2d10+6"}

ray.init()

env = epenv.EP_Environment(config, a_config, b_config)
check_env(env)

register_env("ep_environment", lambda _: epenv.EP_Environment(config, a_config, b_config))

trainer = PPO2(env=env, config={
    "multiagent": {
        "policies": {
            "one": (None, env.observation_space, env.action_space, {}),
            "two": (None, env.observation_space, env.action_space, {}),            
         }
    }    
})


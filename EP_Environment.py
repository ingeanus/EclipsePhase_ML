import gym
import numpy as np
from random import uniform
from random import randint
import re


# Embeddings
EMPTY_EMB = 0
WALL_EMB = 1
ONE_EMB = 2
TWO_EMB = 3

# Multi agent Labels
LBL_ONE = "one"
LBL_TWO = "two"
LBL_ALL = "__all__"

class EP_Environment:
    
    def generate_grid(self, height, width, density):
        grid = grid = np.zeros(width * height, int)
        grid[0] = 2
        grid[height*width-1] = 3

        for i in range(height*width):
                if uniform(0,1) <= density and grid[i] <= 1:
                    grid[i] = 1
        return grid

    def __init__(self, config: dict, one_config: dict, two_config: dict):
        self.config = config
        
        height = config["height"]
        width = config["width"]
        self.size = height * width
        self.grid = self.generate_grid(height, width, config["density"])
        self.base_grid = self.grid
        self.turn = 1
        self.done = False

        self.one = Agent(one_config)
        self.two = Agent(two_config)
        self.one.location = (0)
        self.two.location = (self.size-1)


        self.defending = (False, False)
        self.aiming = (False, False)

        # Observations:
        # Each array index, HP1, HP2
        self.observation_space = gym.spaces.Discrete(self.size+2)
        # Actions:
        # Action: Attack a spot, Full Defense
        # Quick: Move to a spot, Aim
        # [Action, Quick Action]. Size is number of spots on board +1 each for Full Defense & Aim.
        # Last is whether to perform the Full Action (0) or Quick Action (1) first
        self.action_space = gym.spaces.Box(low=[0,0,0], high=[self.size+1, self.size+1, 1])
    
    def reset(self, one_config, two_config):
        self.turn = 1
        self.grid = self.base_grid
        self.one = Agent(one_config)
        self.two = Agent(two_config)
        self.done = False

        return self.get_obs();

    def get_obs(self):
        obs = self.grid
        obs.append(self.hp1)
        obs.append(self.hp2)

        return obs

    def calculate_reward(self):
        one_reward = -1 + self.one.hp - self.two.hp
        two_reward = -1 + self.two.hp - self.one.hp

        if self.one.hp <= 0:
            two_reward += 100
        if self.two.hp <= 0:
            one_reward += 100

        return (one_reward, two_reward)

    def take_action(self, actor, action):
        full_action = action[0]
        quick_action = action[1]
        order = action[2]

        if order == 0:
            take_full_action(actor, full_action)
            take_quick_action(actor, quick_action)
        else:
            take_quick_action(actor, quick_action)
            take_full_action(actor, full_action)

    def take_full_action(self, actor, action):
        if action > self.size:
            self.defending[actor] = True
        else:
            if self.grid[action] > 1:
                roll = uniform(1,100)
                skill = self.one.skill if actor == 0 else self.two.skill
                if aiming[actor]:
                    skill += 10
                    aiming[actor] = False

                if actor == 0 and self.grid[action] == 3:
                    if roll <= self.one.skill:
                        dmg = self.one.dmg
                        dmg = re.split('d|\+', dmg)

                        for dice in range(dmg[0]):
                            self.two.hp -= randint(1, dmg[1])

                        if len(dmg) > 2:
                            self.two.hp -= dmg[2]
                elif actor == 1 and self.grid[action] == 2:
                    if roll <= self.two.skill:
                        dmg = self.two.dmg
                        dmg = re.split('d|\+', dmg)

                        for dice in range(dmg[0]):
                            self.one.hp -= randint(1, dmg[1])

                        if len(dmg) > 2:
                            self.one.hp -= dmg[2]
                    
    def take_quick_action(self, actor, action):
        if action > self.size:
            self.aiming[actor] = True
        else:
            if actor == 0 and self.grid[action] == 0:
                self.grid[self.one.location] = 0
                self.grid[action] = 2
                self.one.location = action
            elif actor == 1 and self.grid[action] == 0:
                self.grid[self.two.location] = 0
                self.grid[action] = 3
                self.two.location = action

    def step(self, actions: dict):
        if self.turn % 2 == 0:
            self.take_action(1, actions[LBL_TWO])
        else:
            self.take_action(0, actions[LBL_ONE])

        env_rewards = self.calculate_reward()

        env_obs = self.get_obs()

        self.turn += 1

        if self.one.hp <= 0 or self.two.hp <= 0 or self.turn >= self.config["max_turns"]:
            done = True

        obs = {LBL_ONE: env_obs, LBL_TWO: env_obs}
        rewards = {LBL_ONE: env_rewards[0], LBL_TWO: env_rewards[1]}
        dones = {LBL_ONE: done, LBL_TWO: done, LBL_ALL: done}

        return obs, rewards, dones, {}

    def render(self, mode='human', close=False):
        vals = (self.grid, self.one.hp, self.two.hp)
        print(vals)
        return vals

class Agent:

    def __init__(self, config):
        self.hp = config["hp"]
        self.skill = config["skill"]
        self.fray = config["fray"]
        self.dmg = config["dmg"]

config = {"width": 30, "height": 15, "density": 0.0, "max_turns": 25}
one_config = {"hp": 30, "skill": 50, "fray": 40, "dmg": "2d10+6"}
two_config = {"hp": 30, "skill": 50, "fray": 40, "dmg": "2d10+6"}
env = EP_Environment(config, one_config, two_config)
print(env.grid.reshape(15, 30))

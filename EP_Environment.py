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

class EP_Environment(gym.Env):
    metadata = {'render.modes': ['human']}   
    
    def generate_grid(self, height, width, density):
        grid = grid = np.zeros(width * height, int)

        for i in range(len(self.a_agents)):
            grid[i] = 2
            self.a_agents.pos = i
        for i in range(len(self.b_agents)):
            grid[size-i-1] = 3
            self.b_agents.pos = i

        for i in range(height*width):
                if uniform(0,1) <= density and grid[i] <= 1:
                    grid[i] = 1
        return grid

    def __init__(self, config: dict, a_config: dict, _config: dict):
        self.config = config
        self.a_config = a_config
        self.b_config = b_config
        
        self.a_agents = []
        self.b_agents = []
        for i in range(config["num_team_a"]):
            self.a_agents.append(Agent(a_config))
        for i in range(config["num_team_b"]):
            self.b_agents.append(Agent(b_config))
                    
        height = config["height"]
        width = config["width"]
        self.size = height * width
        self.grid = self.generate_grid(height, width, config["density"])
        self.base_grid = self.grid
        self.turn = randint(0,1)
        self.done = False

        # Observations:
        # Each array index, HP for each agent
        self.observation_space = gym.spaces.Box(low=0, 
                                                high=max(a_config.hp, b_config.hp), 
                                                shape=(self.size + len(a_agents) + len(b_agents),), 
                                                dtype=np.int)
        # Actions:
        # Action: Attack a spot, Full Defense
        # Quick: Move to a spot, Aim
        # [Action, Quick Action]. Size is number of spots on board +1 each for Full Defense & Aim.
        # Last is whether to perform the Full Action (0) or Quick Action (1) first
        self.action_space = gym.spaces.Box(low=np.array([0,0,0]), 
                                           high=np.array([self.size+1, self.size+1, 1]), 
                                           dtype=np.int)
    
    def reset(self):
        self.turn = randint(0,1)
        self.grid = self.base_grid
        self.a_agents = []
        self.b_agents = []
        for i in range(self.config["num_team_a"]):
            self.a_agents.append(Agent(self.a_config))
        for i in range(self.config["num_team_b"]):
            self.b_agents.append(Agent(self.b_config))

        self.done = False

        testo = self.get_obs()
        return testo

    def get_obs(self):
        obs = []

        for index in self.grid:
            obs.append(index)

        for agent in self.a_agents:
            obs.append(agent.hp)
        for agent in self.b_agents:
            obs.append(agent.hp)

        return np.asarray(obs)

    def calculate_rewards(self):
        one_reward = -1
        two_reward = -1

        for agent in a_agents:
            one_reward += agent.hp
            two_rewared -= agent.hp
            
            if agent.hp <= 0:
                two_reward += 50 / self.config["num_a_agents"]

        for agent in b_agents:
            one_reward -= agent.hp
            two_reward += agent.hp

            if agent.hp <= 0:
                one_reward += 50 / self.config["num_b_agents"]        

        return one_reward, two_reward

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

        obs = self.get_obs()
        reward = self.calculate_reward()[actor[0]]
        done = self.get_dones(actor[0])
        info = {}

        return obs, reward, done, info
       
    def take_full_action(self, actor, action):
        if action >= self.size:
            if actor[0] == 0:
                self.a_agents[actor[1]] = True
            else:
                self.b_agents[actor[1]] = True
        else:
            if actor[0] == 0:
                cur_actor = self.a_agents[actor[1]]
            else:
                cur_actor = self.b_agents[actor[1]]
                            
            roll = randint(1,100)
            skill = cur_actor.skill
            if cur_actor.aiming:
                skill += 10
                cur_actor.aiming = False

            # Determine what agent is being targeted
            tar_actor
            if actor[0] == 0: # If agent is on Team A, search through team B
                for agent in self.b_agents:
                    if agent.pos == action:
                        tar_actor = agent
            else:
                for agent in self.a_agents:
                    if agent.pos == action:
                        tar_actor = agent

            if roll <= skill:
                roll = randint(1,100)
                fray = round(tar_actor.fray/2, 0)
                if tar_actor.defending:
                    fray += 30
                
                if roll > fray:
                    dmg = cur_actor.dmg
                    dmg = re.split('d|\+', dmg)
                    
                    for dice in range(dmg[0]):
                        tar_actor.hp -= randint(1, dmg[1])

                    if len(dmg) > 2:
                        tar_actor.hp -= dmg[2]
                    
    def take_quick_action(self, actor, action):
        if action > self.size:
            self.aiming[actor] = True
        else:
            if actor[0] == 0:
                cur_actor = self.a_agents[actor[1]]
            else:
                cur_actor = self.b_agents[actor[1]]

            if self.grid[action] == 0:
                self.grid[cur_actor.pos] = 0
                self.grid[action] = 2 + actor[0]
                cur_actor.pos = action
                
    def get_dones(self, team):
        if team == 0:
            for agent in self.b_agents:
                if agent.hp > 0:
                    return False        
        else:
            for agent in self.a_agents:
                if agent.hp > 0:
                    return False
        return True

    def step(self, actions: dict):
        obs, rewards, dones, infp = {}, {}, {}, {}

        if self.turn % 2 == 0:
            for i, action in actions.items():
                obs[i], rewards[i], dones[i], info[i] = self.take_action((1, i), action)
        else:
            for i, action in actions.items():
                obs[i], rewards[i], dones[i], info[i] = self.take_action((0, i), action)
                        
        self.turn += 1

        env_obs = self.get_obs()

        done = self.get_dones(0) and self.get_dones(1)

        obs = {LBL_ONE: env_obs, LBL_TWO: env_obs}
        rewards = {LBL_ONE: one_reward, LBL_TWO: two_reward}
        dones = {LBL_ONE: done, LBL_TWO: done, LBL_ALL: done}

        return obs, rewards, dones, {}

    def render(self, mode='human', close=False):
        pass

class Agent:

    def __init__(self, config):
        self.hp = config["hp"]
        self.skill = config["skill"]
        self.fray = config["fray"]
        self.dmg = config["dmg"]
        self.pos
        self.defending = False
        self.aiming = False
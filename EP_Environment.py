import gym
import numpy as np
from random import uniform

class EP_Environment:
    
    def generate_grid(self, height, width, density):
        grid = grid = np.zeros(width * height, int).reshape(height, width)
        grid[0][0] = 2
        grid[height-1][width-1] = 2

        for i in range(height):
            for j in range(width):
                if uniform(0,1) <= density:
                    grid[i,j] = 1
        return grid

    def __init__(self, config: dict):
        self.config = config

        width = config["width"]
        height = config["height"]
        self.grid = self.generate_grid(height, width, config["density"])    

        self.observation_space = gym.spaces.Box(low=0, high=2, shape=(height, width))

        # Actions:
        # Attack, Move, Aim, Full Defense
        self.action_space = gym.spaces.Discrete(height*width + 2) # One for each spot, +2 for Aiming, Full Defense
    
    def reset(self):
        self.turn = 0
        self.grid = self.generate_grid(self.config["height"], self.config["width"], self.config["density"])

    def step(self):
        yeet

    def render(self, mode='human', close=False):
        yote

config = {"width": 30, "height": 15, "density": 0.05}
env = EP_Environment(config)
print(env.grid)

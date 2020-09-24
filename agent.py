import numpy as np
from objects import Object
import random
    

class Agent(Object):
    """
    Abstract class for all agents.
    Agents use their get_movement() method to determine in what direction they
    wish to move.
    """

    def __init__(self, parent, x:int, y:int):
        super().__init__(parent, x, y)

    def __str__(self):
        return '@'

    def get_movement(self):
        raise NotImplementedError


class MeanderingAgent(Agent):
    """
    Agent that moves about randomly, one space at a time.
    """
    def __init__(self, parent, x:int, y:int):
        super().__init__(parent, x, y)
        
    def get_movement(self) -> list:
        dir = random.randint(0,3)
        if dir == 0:
            return Direction.UP
        elif dir == 1:
            return Direction.RIGHT
        elif dir == 2:
            return Direction.DOWN
        elif dir == 3:
            return Direction.LEFT


class Direction:
    UP = np.array([0,-1])
    RIGHT = np.array([1,0])
    DOWN = np.array([0,1])
    LEFT = np.array([-1,0])
import numpy as np

class Object:
    """
    Base class for all elements that can exist in an environment.

    X and Y coordinates are managed by the environment class but stored in objects
    """
    
    def __init__(self, parent, x:int, y:int):
        self.parent = parent
        self.pos = np.array([x, y])

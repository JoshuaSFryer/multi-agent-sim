import numpy as np

class Object:
    """
    Base class for all elements that can exist in an environment.

    X and Y coordinates are managed by the environment class but stored in objects
    """
    
    def __init__(self, parent, x:int, y:int):
        self.parent = parent
        # Object's current position
        self.pos = np.array([x, y])
        # Variable containing the object's last position
        self.old_pos = self.pos 

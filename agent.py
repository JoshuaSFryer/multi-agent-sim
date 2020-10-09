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

    def get_movement(self) -> np.array:
        raise NotImplementedError


class MeanderingAgent(Agent):
    """
    Agent that moves about randomly, one space at a time.
    """
    def __init__(self, parent, x:int, y:int):
        super().__init__(parent, x, y)
        
    def get_movement(self) -> np.array:
        dir = random.randint(0,3)
        if dir == 0:
            return Direction.N
        elif dir == 1:
            return Direction.E
        elif dir == 2:
            return Direction.S
        elif dir == 3:
            return Direction.W


class FocusedAgent(Agent):
    """
    Agent with two key points: Work, and Home.
    Every 12 hours (720 minutes/ticks), the agent toggles its "focus point" 
    between home and work.
    It uses a linear decay to pathfind towards, and hover around, its current
    focus point (i.e. the further away the agent is from its focus point, the
    more likely it is to move towards it).
    """
    def __init__(self, parent, x:int, y:int, home:np.array, work:np.array, slack:int):
        super().__init__(parent, x, y)
        self.home_point = home
        self.work_point = work
        self.focus_point = self.work_point # Default to work point on creation
        # "Maximum distance" in Paulo's pseudocode; essentially, the higher this
        # is, the farther the agent can be from its focus point:
        self.slack = slack 


    def get_movement(self):
        R = random.randint(0,299)
        target_vector = self.get_target_vector()
        distance_factor = self.get_distance(target_vector)/self.slack
        target_direction = self.get_compass_direction(target_vector)

        if R < 100 + 200 * distance_factor:
            # Move along the target vector directly towards focus point
            return target_direction
        elif R < 200 + 100 * distance_factor:
            # Move perpendicular to the target vector
            # 50/50 chance of moving 'right' or 'left' relative to the vector
            left_right = random.randint(0,9)
            if left_right >= 5:
                return np.dot(target_direction, Rotation.CCW_270)
            else:
                return np.dot(target_direction, Rotation.CCW_90)
        else:
            # Move along the target vector, away from the focus point
            return np.dot(target_direction, Rotation.CW_180)


    def get_distance(self, vector):
        """
        Get the distance (as crow flies, not cartesian) of a vector.
        
        The built-in numpy function to get the magnitude of a vector,
        np.linalg.norm(x), is apparently very slow. Credit to
        https://stackoverflow.com/a/9184560, which uses the fact that the dot
        product between a vector and itself is the magnitude squared, to make
        this call that returns in 1/4 the time:
        """
        return int(np.round(np.sqrt(vector.dot(vector))))


    def get_target_vector(self) -> np.array:
        """
        Get a vector pointing from the agent towards its focus point.
        """
        return self.focus_point - self.pos
    

    def get_compass_direction(self, vector):
        """
        Return the direction from the agent to its focus point, normalized to
        the eight compass directions.
        """
        # Convert from cartesian to polar coordinates
        x, y = vector.tolist()
        r = self.get_distance(vector)
        if r == 0:
            return Direction.NONE
        rad = np.arctan2(y, x)
        deg = np.degrees(rad)

        # transform from [-180,180] to [0,360]
        if deg < 0: 
            deg = 360 + deg

        # Convert degrees into compass direction, roughly.
        if deg >= 22.5 and deg < 67.5:
            return Direction.NE
        elif deg >= 67.5 and deg < 112.5:
            return Direction.N
        elif deg >= 112.5 and deg < 157.5:
            return Direction.NW
        elif deg >= 157.5 and deg < 202.5:
            return Direction.W
        elif deg >= 202.5 and deg < 247.5:
            return Direction.SW
        elif deg >= 247.5 and deg < 292.5:
            return Direction.S
        elif deg >= 292.5 and deg < 337.5:
            return Direction.SE
        else: # range between 337.5 and 22.5, looping around at 0
            return Direction.E
        

    def toggle_focus(self):
        if self.focus_point is self.work_point:
            self.focus_point = self.home_point
        elif self.focus_point is self.home_point:
            self.focus_point = self.work_point
        else:
            raise ValueError(f"Focus point set to invalid value: {self.focus_point}")



class Direction:
    # Cardinal directions
    N = np.array([0,-1])
    E = np.array([1,0])
    S = np.array([0,1])
    W = np.array([-1,0])
    # Diagonal directions
    NE = np.array([1,-1])
    SE = np.array([1,1])
    SW = np.array([-1,1])
    NW = np.array([-1,-1])

    NONE = np.array([0,0])


class Rotation:
    CCW_270 = np.array([[0, -1], [1, 0]])
    CCW_90 = np.array([[0, 1], [-1, 0]])
    CW_180 = np.array([[-1, 0], [0, -1]])

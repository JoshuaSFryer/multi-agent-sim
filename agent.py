import numpy as np
import random
import uuid

from contact import Contact
from objects import Object
from direction import Direction
from simulation_parameters import *
from sir import SIR_status as sir



class Agent(Object):
    """
    Abstract class for all agents.
    Agents use their get_movement() method to determine in what direction they
    wish to move.
    """

    def __init__(self, parent, x:int, y:int):
        super().__init__(parent, x, y)

    def get_movement(self) -> np.array:
        """
        Function that should return a vector representing the movement the agent 
        will take. 
        """
        raise NotImplementedError


class MeanderingAgent(Agent):
    """
    Agent that moves about randomly, one space at a time.
    """

    def __init__(self, parent, x:int, y:int):
        super().__init__(parent, x, y)
        

    def get_movement(self) -> np.array:
        """
        Pick a cardinal direction to step in, at random.
        """

        dirs = [Direction.N, Direction.E, Direction.S, Direction.W]
        return random.choice(dirs)


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
        """
        x:  Initial x coordiate of the agent
        y:  Initial y coordinate of the agent
        home_point: Coordinate pair representing this agent's home point
        work_point: Coordinate pair representing this agent's work point
        slack:      Integer influencing how far the agent can stray from its
                    current focus point 
        """

        super().__init__(parent, x, y)
        self.home_point = home
        self.work_point = work
        self.focus_point = self.work_point # Default to work point on creation
        # "Maximum distance" in Paulo's pseudocode; essentially, the higher this
        # is, the farther the agent can be from its focus point:
        self.slack = slack 


    def get_movement(self) -> np.array:
        """
        Move, either directly towards the focus point, or erroneously (parallel)
        or backwards). The chance of erroneous movement is inversely proportional 
        to the agent's distance from the focus point, following a linear decay. 
        Once the agent reaches its focus point, it will be randomly stepping
        in orbit around it.
        """

        target_vector = self.get_target_vector()
        target_direction = self.get_compass_direction(target_vector)   

        # If the agent is occupying its focus point, the target vector will be
        # [0,0], and so the agent will stay stuck on that point instead of 
        # orbiting around it. Let's allow it to move in any of the 8 directions,
        # with equal probability.     
        if np.array_equal(target_direction, Direction.NONE):
            return self.get_random_direction()

        distance_factor = self.get_distance(target_vector) / self.slack
        R = random.randint(0,299)
        if R < 100 + 200 * distance_factor:
            # Move along the target vector directly towards focus point
            return target_direction
        elif R < 200 + 100 * distance_factor:
            # Move perpendicular to the target vector
            # 50/50 chance of moving 'right' or 'left' relative to the vector
            rot = random.choice([Rotation.CCW_90, Rotation.CCW_270])
            return np.dot(target_direction, rot)
        else:
            # Move along the target vector, away from the focus point
            return np.dot(target_direction, Rotation.CW_180)


    def get_distance(self, vector:np.array) -> int:
        """
        Get the distance (as crow flies, not cartesian) of a vector.
        
        The built-in numpy function to get the magnitude of a vector,
        np.linalg.norm(x), is apparently very slow. Credit to
        https://stackoverflow.com/a/9184560, which uses the fact that the dot
        product between a vector and itself is the magnitude squared, to make
        this call that returns in 1/4 the time.

        vector: The vector/coordinate pair in question

        returns: The magnitude of the vector, rounded to the nearest integer
        """

        return int(np.round(np.sqrt(vector.dot(vector))))


    def get_target_vector(self) -> np.array:
        """
        Get a vector pointing from the agent towards its focus point.  
        """

        return self.focus_point - self.pos
    

    def get_compass_direction(self, vector:np.array) -> Direction:
        """
        Return the direction of a vector, normalized to one of the eight compass
        directions.
        """

        base_vector = Direction.NONE
        
        x, y = vector.tolist()
        if x > 0:
            base_vector = base_vector + Direction.E
        elif x < 0:
            base_vector = base_vector + Direction.W
        
        if y > 0:
            base_vector = base_vector + Direction.S
        elif y < 0:
            base_vector = base_vector + Direction.N

        return base_vector


    def get_random_direction(self) -> np.array:
        """
        Pick a compass direction at random.
        """
        
        return random.choice(Direction.direction_list)


    def toggle_focus(self) -> None:
        """
        Toggle this agent's focus point between work and home.
        """

        if self.focus_point is self.work_point:
            self.focus_point = self.home_point
        elif self.focus_point is self.home_point:
            self.focus_point = self.work_point
        else:
            raise ValueError(f"Something is internally buggy: \
                Focus point is somehow set to invalid value: {self.focus_point}")


class BiologicalAgent(FocusedAgent):
    """
    Agent that is susceptible to catching and spreading disease.
    """
    
    def __init__(self, parent, x:int, y:int, home:np.array, work:np.array, 
                    slack:int, diseased=sir.SUSCEPTIBLE):
        """
        x:  Initial x coordiate of the agent
        y:  Initial y coordinate of the agent
        home_point: Coordinate pair representing this agent's home point
        work_point: Coordinate pair representing this agent's work point
        slack:      Integer influencing how far the agent can stray from its
                    current focus point 
        diseased:   SIR status for the agent upon creation. Most agents should
                    be created as susceptible, but this allows for seeding 
                    an agent as infected.
        """

        super().__init__(parent, x, y, home, work, slack)
        self.disease_status = diseased
        self.infection_time = 0


    def infect(self):
        """
        Infect the agent with the disease, if it is susceptible.
        """

        if self.disease_status == sir.SUSCEPTIBLE:
            self.disease_status = sir.INCUBATING_SAFE
            self.infection_time = 0
        else:
            raise ValueError("Cannot infect agent: \
                            Agent is not susceptible to infection.")


    def progress_infection(self):
        """
        Advance the infection, ticking the infection timer forward and
        progressing to the next state of infection if sufficient time has
        passed.
        """
        
        self.infection_time += 1
        if self.disease_status == sir.INCUBATING_SAFE:
            if self.infection_time >= INCUBATION_SAFE_TIME:
                self.disease_status = sir.INCUBATING_CONTAGIOUS
                self.infection_time = 0
        
        elif self.disease_status == sir.INCUBATING_CONTAGIOUS:
            if self.infection_time >= INCUBATION_CONTAGIOUS_TIME:
                self.disease_status = sir.SYMPTOMATIC
                self.infection_time = 0
        
        elif self.disease_status == sir.SYMPTOMATIC:
            if self.infection_time >= SYMPTOMATIC_TIME:
                self.disease_status = sir.RECOVERED

        else:
            raise RuntimeError("progress_infection() called on uninfected agent")


    def is_infected(self) -> bool:
        return self.disease_status in ( sir.INCUBATING_SAFE, 
                                        sir.INCUBATING_CONTAGIOUS,
                                        sir.SYMPTOMATIC
                                        )


    def is_susceptible(self) -> bool:
        return self.disease_status == sir.SUSCEPTIBLE


    def is_contagious(self) -> bool:
        return self.disease_status in (sir.INCUBATING_CONTAGIOUS, sir.SYMPTOMATIC)


class TraceableAgent(BiologicalAgent):

    def __init__(self, parent, x:int, y:int, home:np.array, work:np.array, 
                    slack:int, diseased=sir.SUSCEPTIBLE):

        super().__init__(parent, x, y, home, work, slack, diseased)
        # Unique ID to track each agent
        self.agent_id = uuid.uuid4()
        # List of contacts with other agents
        self.contacts = list()

    def register_contact(self, time, id):
        self.contacts.append(Contact(time, id))
        
class Rotation:
    """
    Transformation matrices; multiply a vector by one of these matrices to
    effect a rotation on that vector.
    """

    CCW_270 = np.array([[0, -1], [1, 0]])
    CCW_90 = np.array([[0, 1], [-1, 0]])
    CW_180 = np.array([[-1, 0], [0, -1]])

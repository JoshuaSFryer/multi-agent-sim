import numpy as np
import random
import uuid

from contact import *
from objects import Object
from direction import Direction
from infection import Infection, TwoStageInfection
from simulation_parameters import SimConfig, SimulationMode
from sir import SIR_status as sir



class Agent(Object):
    """
    Abstract class for all agents.
    Agents use their get_movement() method to determine in what direction they
    wish to move.
    """

    def __init__(self, parent, x:int, y:int, config:SimConfig):
        super().__init__(parent, x, y)
        self.cfg = config

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

    def __init__(self, parent, x:int, y:int, home:np.array, work:np.array, 
                    slack:int, config:SimConfig):
        """
        x:  Initial x coordiate of the agent
        y:  Initial y coordinate of the agent
        home_point: Coordinate pair representing this agent's home point
        work_point: Coordinate pair representing this agent's work point
        slack:      Integer influencing how far the agent can stray from its
                    current focus point 
        """

        super().__init__(parent, x, y, config)
        self.home_point = home
        self.work_point = work
        self.focus_point = self.work_point # Default to work point on creation
        # "Maximum distance" in Paulo's pseudocode; essentially, the higher this
        # is, the farther the agent can be from its focus point:
        self.slack = slack 


    def get_movement(self) -> np.array:
        """
        Move, either directly towards the focus point, or erroneously (parallel
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
                    slack:int, config:SimConfig):
        """
        x:  Initial x coordiate of the agent
        y:  Initial y coordinate of the agent
        home_point: Coordinate pair representing this agent's home point
        work_point: Coordinate pair representing this agent's work point
        slack:      Integer influencing how far the agent can stray from its
                    current focus point
        """

        super().__init__(parent, x, y, home, work, slack, config)
        if self.cfg.RESPONSE_MODE == SimulationMode.PREEMPTIVE_ISOLATION:
            self.infection = TwoStageInfection(self, self.cfg)
        else:
            self.infection = Infection(self, self.cfg)


    def infect(self):
        """
        Infect the agent with the disease, if it is susceptible.
        """

        if not self.infection.active:
            self.infection.activate()
        else:
            pass


    def tick(self):
        """
        Update the agent for the current step.
        """
        
        self.infection.tick()


    def is_infected(self) -> bool:
        return self.infection.active


    def is_susceptible(self) -> bool:
        return self.infection.status == sir.SUSCEPTIBLE


    def is_contagious(self) -> bool:
        return self.infection.status in (sir.INCUBATING_CONTAGIOUS,
                                        sir.SYMPTOMATIC_MILD, 
                                        sir.SYMPTOMATIC_SEVERE)

    
    def is_symptomatic(self) -> bool:
        return self.infection.status in (sir.SYMPTOMATIC_MILD, 
                                        sir.SYMPTOMATIC_SEVERE)

    
    def is_recovered(self) -> bool:
        return self.infection.status == sir.RECOVERED


class BehaviorState(Enum):
    IDLE = 1
    AWAITING_TEST = 2
    SELF_ISOLATING = 3
    CAUTIOUS_ISOLATING = 4


class IsolatingAgent(BiologicalAgent):
    """
    Agent with the capability to self-isolate upon becoming symptomatic.
    Used for simulation model B.
    """
    def __init__(self, parent, x, y, home, work, slack, config):
        super().__init__(parent, x, y, home, work, slack, config)

        self.behavior = BehaviorState.IDLE
        self.testing_timer = 0

    def self_isolate(self):
        self.behavior = BehaviorState.SELF_ISOLATING
        self.focus_point = self.home_point
        self.parent.curr_self_isolating.append(self)
        self.parent.num_self_isolated += 1

    def stop_isolating(self):
        self.parent.curr_self_isolating.remove(self)
        self.behavior = BehaviorState.IDLE
        # Have the agent sync back up with the day/night cycle
        if self.parent.daytime:
            self.focus_point = self.work_point
        # else, it's night and so focus should be home_point, which it ought to
        # be if the agent was isolating, but here's the code just in case
        else:
            self.focus_point = self.home_point

    def toggle_focus(self):
        """
        Overrides FocusedAgent.toggle_focus(), disabling normal focus-toggling
        when the agent is self-isolating and should remain at home.
        """

        if not self.is_isolating():
            super().toggle_focus()


    def wait_for_test(self):
        self.testing_timer = self.cfg.SYMPTOM_TESTING_LAG
        self.behavior = BehaviorState.AWAITING_TEST

    def is_isolating(self):
        return self.behavior == BehaviorState.SELF_ISOLATING

    def tick(self):
        """
        Overrides BiologicalAgent.tick().
        Agents will now begin self-isolating upon becoming symptomatic.
        """
        # Tick the infection forward (no effect if infection is inactive)
        self.infection.tick()

        if self.behavior == BehaviorState.IDLE:
            # Get tested if symptomatic
            if self.is_symptomatic():
                self.wait_for_test()

        elif self.behavior == BehaviorState.AWAITING_TEST:
            self.testing_timer -= 1
            if self.testing_timer <= 0:
                # Go into self-isolation
                self.self_isolate()

        elif self.behavior == BehaviorState.SELF_ISOLATING:
            # Go back to normal once the infection ends
            if self.is_recovered():
                self.stop_isolating()


class TraceableAgent(IsolatingAgent):
    """
    Agent with contact-tracing and notification capability.
    Used for simulation model C.
    """

    def __init__(self, parent, x:int, y:int, home:np.array, work:np.array, 
                    slack:int, config):
        super().__init__(parent, x, y, home, work, slack, config)
        # Unique ID to track each agent
        self.agent_id = uuid.uuid4()
        # List of contacts with other agents
        self.contacts = list()


    def register_contact(self, time, contacted_agent):
        """
        Record a contact with another agent at a particular time.
        """
        if not contacted_agent.is_symptomatic():
            symptoms = SymptomLevel.NONE
        elif contacted_agent.infection.status == sir.SYMPTOMATIC_MILD:
            symptoms = SymptomLevel.MILD
        elif contacted_agent.infection.status == sir.SYMPTOMATIC_SEVERE:
            symptoms = SymptomLevel.SEVERE
        
        self.contacts.append(Contact(time, 
                                    contacted_agent.pos,
                                    contacted_agent.agent_id,
                                    symptoms
                                    ))


    def tick(self):
        """
        Overrides IsolatingAgent.tick().
        """
        # Tick the infection forward (no effect if infection is inactive)
        self.infection.tick()

        if self.behavior == BehaviorState.IDLE:
            # Get tested if symptomatic
            if self.is_symptomatic():
                self.wait_for_test()
                self.notify_contacts()

        elif self.behavior == BehaviorState.AWAITING_TEST:
            self.testing_timer -= 1
            if self.testing_timer <= 0:
                # Go into self-isolation
                self.self_isolate()

        elif self.behavior == BehaviorState.SELF_ISOLATING:
            # Go back to normal once the infection ends
            if self.is_recovered():
                self.stop_isolating()
        

    def get_contacted_agents(self, expiry:int):
        """
        Get all the unique agents that this agent has come into contact with,
        in the past {expiry} ticks.
        """

        contact_list = list()
        for c in self.contacts:
            time_delta = self.parent.current_time - c.time
            if time_delta <= expiry:
                contact_list.append(c)
        return contact_list


    def get_recent_contacts(self):
        recent_contacts = self.get_contacted_agents(self.cfg.INCUBATION_SAFE_TIME
                                                    + self.cfg.INCUBATION_CONTAGIOUS_TIME)
        if self.cfg.CONTACT_CULLING:
            self.contacts = recent_contacts
        return recent_contacts

    
    def notify_contacts(self):
        contact_list = self.get_recent_contacts()
        for c in contact_list:
            uuid = c.contact_id
            agent = self.parent.get_agent_by_uuid(uuid)
            agent.notification_reaction()


    def notification_reaction(self):
        self.self_isolate()
        self.parent.num_notified_through_tracing += 1
    

class CautiousAgent(TraceableAgent):
    """
    Agent that will preemptively isolate.
    Used for simulation model D.
    """
    def __init__(self, parent, x, y, home, work, slack, config):
        super().__init__(parent, x, y, home, work, slack, config)
        self.caution_timer = 0


    def tick(self):
        """
        Overrides BiologicalAgent.tick().
        Agents will now begin self-isolating upon becoming symptomatic.
        """
        # Tick the infection forward (no effect if infection is inactive)
        self.infection.tick()

        if self.behavior == BehaviorState.IDLE:
            # Get tested if symptomatic
            if self.is_symptomatic():
                self.wait_for_test()
                self.notify_contacts()

            # Isolate if number of symptomatic contacts exceeds threshold
            if self.get_infected_contacts() > self.cfg.CAUTION_THRESHOLD:
                self.cautious_isolate()
                self.geonotify()

        elif self.behavior == BehaviorState.AWAITING_TEST:
            self.testing_timer -= 1
            if self.testing_timer <= 0:
                # Go into self-isolation if test was prompted by symptoms
                self.self_isolate()

        elif self.behavior == BehaviorState.SELF_ISOLATING:
            # Go back to normal once the infection ends
            if self.is_recovered():
                self.stop_isolating()

        elif self.behavior == BehaviorState.CAUTIOUS_ISOLATING:
            # Go into self-isolation if symptoms develop
            if self.is_symptomatic():
                self.self_isolate()
            else:
                # Go back to normal if the caution period expires
                self.caution_timer -= 1
                if self.caution_timer <= 0:
                    self.stop_isolating()
                    self.parent.unnecessary_isolations += 1
        

    def get_infected_contacts(self):
        """
        Count all contacts with agents exhibiting mild symptoms, that occurred
        within the last {incubation period} ticks.
        """
        count = 0
        contact_list = self.get_recent_contacts()
        for c in contact_list:
            if c.symptomatic == SymptomLevel.MILD:
                count += 1
        return count

    def cautious_isolate(self):
        self.behavior = BehaviorState.CAUTIOUS_ISOLATING
        self.focus_point = self.home_point
        self.caution_timer = self.cfg.INCUBATION_SAFE_TIME + \
            self.cfg.INCUBATION_CONTAGIOUS_TIME
        self.parent.num_cautious_isolated += 1
        self.parent.curr_cautious_isolating.append(self)
    
    def stop_isolating(self):
        if self.behavior == BehaviorState.CAUTIOUS_ISOLATING:
            self.parent.curr_cautious_isolating.remove(self)
        elif self.behavior == BehaviorState.SELF_ISOLATING:
            self.parent.curr_self_isolating.remove(self)

        self.behavior = BehaviorState.IDLE
        # Have the agent sync back up with the day/night cycle
        if self.parent.daytime:
            self.focus_point = self.work_point
        # else, it's night and so focus should be home_point, which it ought to
        # be if the agent was isolating, but here's the code just in case
        else:
            self.focus_point = self.home_point

    
    def is_isolating(self):
        """
        Override IsolatingAgent.is_isolating() to include cautious isolating
        """
        return self.behavior in (BehaviorState.SELF_ISOLATING,
                                BehaviorState.CAUTIOUS_ISOLATING)


    def geonotify(self):
        
        recent_contacts = self.get_recent_contacts()
        sum_x = 0
        sum_y = 0
        n = len(recent_contacts)
        for c in recent_contacts:
            x, y = c.location.tolist()
            sum_x += x
            sum_y += y
        avg_x = sum_x / n
        avg_y = sum_y / n
        avg_point = np.array([avg_x, avg_y])
        for c in recent_contacts:
            agent = self.parent.get_agent_by_uuid(c.contact_id)
            agent.geonotification_reaction(avg_point)


    def geonotification_reaction(self, point:np.array):
        if self.check_for_local_contact(point):
            self.self_isolate
            self.parent.num_geonotified += 1
        


    def check_for_local_contact(self, notified_point:np.array):
        """
        Check to see if this agent has recently encountered contacts near 
        a given point.
        """
        recent_contacts = self.get_recent_contacts()
        for c in recent_contacts:
            vector = notified_point - c.location
            if self.get_distance(vector) <= self.cfg.GEOLOCATION_DISTANCE:
                return True
        return False
        


class Rotation:
    """
    Transformation matrices; multiply a vector by one of these matrices to
    effect a rotation on that vector.
    """

    CCW_270 = np.array([[0, -1], [1, 0]])
    CCW_90 = np.array([[0, 1], [-1, 0]])
    CW_180 = np.array([[-1, 0], [0, -1]])

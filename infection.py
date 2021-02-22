import random
import warnings

from simulation_parameters import *
from sir import SIR_status as sir

class Infection():

    def __init__(self, parent):
        self.status = sir.SUSCEPTIBLE
        self.tick_threshold = None
        self.ticks = None
        self.active = False
        self.parent = parent

    
    def activate(self):
        """
        Cover the transition between SUSCEPTIBLE and INCUBATING_SAFE states,
        i.e. trigger the infection in the agent.
        """

        self.status = sir.INCUBATING_SAFE
        self.tick_threshold = INCUBATION_SAFE_TIME
        self.ticks = 0
        self.active = True
        self.parent.parent.register_infected(self.parent)
    
    
    def tick(self):
        """
        Tick the infection timer forward, and progress to the next state of 
        infection if sufficient time has passed.
        """

        if self.active:
            self.ticks += 1
            if self.ticks >= self.tick_threshold:
                self.ticks = 0
                self.progress()


    def progress(self):
        """
        Start the infection's progress, or advance the infection one stage.
        """

        # Inelegant switch statement, but this way is more explicit and thus
        # robust than some enum iteration trick.

        # Do nothing if there is no active infection!
        if self.status == sir.SUSCEPTIBLE:
            return
        
        # activate() covers the transition from SUSCEPTIBLE to INCUBATING_SAFE

        # Become contagious
        if self.status == sir.INCUBATING_SAFE:
            self.status = sir.INCUBATING_CONTAGIOUS
            self.tick_threshold = INCUBATION_CONTAGIOUS_TIME
        # Become symptomatic
        elif self.status == sir.INCUBATING_CONTAGIOUS:
            self.status = sir.SYMPTOMATIC_SEVERE
            self.tick_threshold = SYMPTOMATIC_TIME
        # Recover, start counting down the immunity timer
        elif self.status == sir.SYMPTOMATIC_SEVERE:
            self.status = sir.RECOVERED
            self.tick_threshold = IMMUNITY_DURATION
            self.parent.parent.register_recovered(self.parent)

        # After the infection has subsided, the agent has a grace period where
        # it is immune to infection.
        # After immunity elapses, the agent has no current infection but is
        # once again susceptible to infection.
        elif self.status == sir.RECOVERED:
            self.status = sir.SUSCEPTIBLE
            self.tick_threshold = None
            self.active = False
            self.parent.parent.register_susceptible(self.parent)


class TwoStageInfection(Infection):
    """
    Infection behaviour for model D.
    """
    def __init__(self, parent):
        super().__init__(parent)

    def progress(self):
        """
        Override.
        """
        if self.status == sir.SUSCEPTIBLE:
            return
        
        # Become contagious
        if self.status == sir.INCUBATING_SAFE:
            self.status = sir.INCUBATING_CONTAGIOUS
            self.tick_threshold = MODEL_D_CONTAGIOUS_TIME
        # Become symptomatic
        elif self.status == sir.INCUBATING_CONTAGIOUS:
            self.status = sir.SYMPTOMATIC_MILD
            self.tick_threshold = MILD_SYMPTOM_TIME
        # Chance to progress from mild to severe, or to recover
        elif self.status == sir.SYMPTOMATIC_MILD:
            n = random.random()
            if n < FALSE_ALARM_PROBABILITY:
                # Recover
                self.status = sir.RECOVERED
                self.tick_threshold = IMMUNITY_DURATION
                self.parent.parent.register_recovered(self.parent)

            else:
                # Progress to severe symptoms
                self.status = sir.SYMPTOMATIC_SEVERE
                self.tick_threshold = SYMPTOMATIC_TIME
        # Recover, start counting down the immunity timer
        elif self.status == sir.SYMPTOMATIC_SEVERE:
            self.status = sir.RECOVERED
            self.tick_threshold = IMMUNITY_DURATION
            self.parent.parent.register_recovered(self.parent)
        # After the infection has subsided, the agent has a grace period where
        # it is immune to infection.
        # After immunity elapses, the agent has no current infection but is
        # once again susceptible to infection.
        elif self.status == sir.RECOVERED:
            self.status = sir.SUSCEPTIBLE
            self.tick_threshold = None
            self.active = False
            self.parent.parent.register_susceptible(self.parent)

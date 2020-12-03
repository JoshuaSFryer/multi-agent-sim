import warnings

from simulation_parameters import *
from sir import SIR_status as sir

class Infection():

    def __init__(self):
        self.status = sir.SUSCEPTIBLE
        self.tick_threshold = None
        self.ticks = None
        self.active = False

    
    def activate(self):
        self.status = sir.INCUBATING_SAFE
        self.tick_threshold = INCUBATION_SAFE_TIME
        self.ticks = 0
        self.active = True
    
    
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
            pass
        
        # activate() covers the transition from SUSCEPTIBLE to INCUBATING_SAFE

        # Become contagious
        if self.status == sir.INCUBATING_SAFE:
            self.status = sir.INCUBATING_CONTAGIOUS
            self.tick_threshold = INCUBATION_CONTAGIOUS_TIME
        # Become symptomatic
        elif self.status == sir.INCUBATING_CONTAGIOUS:
            self.status = sir.SYMPTOMATIC
            self.tick_threshold = SYMPTOMATIC_TIME
        # Recover, start counting down the immunity timer
        elif self.status == sir.SYMPTOMATIC:
            self.status = sir.RECOVERED
            self.tick_threshold = IMMUNITY_DURATION
        # After the infection has subsided, the agent has a grace period where
        # it is immune to infection.
        elif self.status == sir.RECOVERED:
            self.status = sir.SUSCEPTIBLE
            self.tick_threshold = None
            self.active = False

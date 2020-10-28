from enum import Enum

class SIR_status(Enum):
    SUSCEPTIBLE = 1
    INCUBATING_SAFE = 2
    INCUBATING_CONTAGIOUS = 3
    SYMPTOMATIC = 4
    RECOVERED = 5
from enum import Enum

class SIR_status(Enum):
    # Uninfected
    SUSCEPTIBLE = 1
    # Infected, but neither contagious nor showing symptoms
    INCUBATING_SAFE = 2
    # Infected and asymptomatic, but contagious
    INCUBATING_CONTAGIOUS = 3
    # Contagious and showing symptoms
    SYMPTOMATIC = 4
    # No longer infected, temporarily immune
    RECOVERED = 5
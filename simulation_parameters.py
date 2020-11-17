from enum import Enum
class SimulationMode(Enum):
    NO_REACTION = 1
    CONTACT_TRACING = 2
    UNDEFINED_MODE = 3

# World parameters
NUM_AGENTS = 20
AGENT_SLACK = 4
# Number of cells in the environment
WORLD_WIDTH = 30
WORLD_HEIGHT = 30

MAXIMUM_TIME = 1000


# Infection parameters
INITIAL_INFECTED_PERCENT = 0.02
INFECTION_RADIUS = 2

INCUBATION_SAFE_TIME = 50
INCUBATION_CONTAGIOUS_TIME = 50
SYMPTOMATIC_TIME = 100
IMMUNITY_DURATION = 100

INFECTION_PROBABILITY = 1


# Agent behaviour parameters
RESPONSE_MODE = SimulationMode.CONTACT_TRACING
# How long the agents wait to get tested after becoming symptomatic
SYMPTOM_TESTING_LAG = 3

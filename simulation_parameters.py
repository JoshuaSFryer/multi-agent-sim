from enum import Enum
class SimulationMode(Enum):
    NO_REACTION = 1
    CONTACT_TRACING = 2
    GEO_NOTIFICATION = 3

# World parameters
NUM_AGENTS = 100
AGENT_SLACK = 4
# Number of cells in the environment
WORLD_WIDTH = 100
WORLD_HEIGHT = 100

MAXIMUM_TIME = 3000


# Infection parameters
INITIAL_INFECTED_PERCENT = 0.02
INFECTION_RADIUS = 2
INFECTION_PROBABILITY = 0.7
REINFECTION_POSSIBLE = True

# Durations of each infection stage, in ticks
INCUBATION_SAFE_TIME = 50
INCUBATION_CONTAGIOUS_TIME = 50
SYMPTOMATIC_TIME = 100
IMMUNITY_DURATION = 100

# Agent behaviour parameters
RESPONSE_MODE = SimulationMode.CONTACT_TRACING
# How long the agents wait to "get tested" after becoming symptomatic
SYMPTOM_TESTING_LAG = 3
# How many symptomatic contacts can be registered before going into
# cautious isolation
CAUTION_THRESHOLD = 5

RNG_SEED = 5

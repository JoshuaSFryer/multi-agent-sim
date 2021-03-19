from enum import Enum
class SimulationMode(Enum):
    NO_REACTION = 1
    SELF_ISOLATION = 2
    CONTACT_TRACING = 3
    PREEMPTIVE_ISOLATION = 4

# World parameters
NUM_AGENTS = 100
AGENT_SLACK = 4
# Number of cells in the environment
WORLD_WIDTH = 300
WORLD_HEIGHT = 300

MAXIMUM_TIME = 3000


# 'safe' numbers:
# Initial percent: 0.02
# INFECTION_RADIUS = 1
# INFECTION_PROBABILITY: 0.25
# FALSE_ALARM_PROBABILITY = 0.75

# 'medium'
# INFECTION_RADIUS = 2
# INFECTION_PROBABILITY = 0.5
# FALSE_ALARM_PROBABILITY = 0.5

# 'harsh'
# INFECTION_RADIUS = 3
# INFECTION_PROBABILITY = 0.75
# FALSE_ALARM_PROBABILITY = 0.25



# Infection parameters
INITIAL_INFECTED_PERCENT = 0.02
INFECTION_RADIUS = 2
INFECTION_PROBABILITY = 0.7
REINFECTION_POSSIBLE = True
# Chance for agent to go from mild symptoms to recovered state
# (simulating common flu, etc)
FALSE_ALARM_PROBABILITY = 0.05

# Durations of each infection stage, in ticks
INCUBATION_SAFE_TIME = 50
INCUBATION_CONTAGIOUS_TIME = 50
# total time for asymptomatic in models A-C = asymptomatic + mild in D
MILD_SYMPTOM_TIME = 30
MODEL_D_CONTAGIOUS_TIME = INCUBATION_CONTAGIOUS_TIME - MILD_SYMPTOM_TIME
SYMPTOMATIC_TIME = 100
IMMUNITY_DURATION = 100

# Agent behaviour parameters
RESPONSE_MODE = SimulationMode.NO_REACTION
# How long the agents wait to "get tested" after becoming symptomatic
SYMPTOM_TESTING_LAG = 3
# How many symptomatic contacts can be registered before going into
# cautious isolation
CAUTION_THRESHOLD = 5

GEOLOCATION_DISTANCE = 5

RNG_SEED = 5

CONTACT_CULLING = True
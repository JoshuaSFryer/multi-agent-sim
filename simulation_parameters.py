from enum import Enum
class SimulationMode(Enum):
    NO_REACTION = 1
    SELF_ISOLATION = 2
    CONTACT_TRACING = 3
    PREEMPTIVE_ISOLATION = 4

class SimConfig():
    # World parameters
    # Ottawa population density: 317/km^2
    # so 317 : 1000x1000
    # or 7925 : 5000x5000
    # or 31,700 : 10000x10000
    NUM_AGENTS = 12000
    # Number of cells in the environment
    WORLD_WIDTH = 3000
    WORLD_HEIGHT = 3000
    #12000, 3500x3500 = ~980 agents/1000tile^2
    #12000, 5000x5000 = 480
    #4000x4000 = 750
    # 1440 ticks per cycle * 4 cycles = 4320
    MAXIMUM_TIME = 4320

    AGENT_SLACK = 4

    # 'safe' numbers:
    # INFECTION_RADIUS = 1
    # INFECTION_PROBABILITY = 0.25
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
    REINFECTION_POSSIBLE = True
    # Chance for agent to go from mild symptoms to recovered state
    # (simulating common flu, etc)

    # Durations of each infection stage, in ticks
    INCUBATION_SAFE_TIME = 50
    INCUBATION_CONTAGIOUS_TIME = 50
    # total time for asymptomatic in models A-C = asymptomatic + mild in D
    MILD_SYMPTOM_TIME = 30
    MODEL_D_CONTAGIOUS_TIME = INCUBATION_CONTAGIOUS_TIME - MILD_SYMPTOM_TIME
    SYMPTOMATIC_TIME = 100
    IMMUNITY_DURATION = 100

    # Agent behaviour parameters
    # RESPONSE_MODE = SimulationMode.NO_REACTION
    # How long the agents wait to "get tested" after becoming symptomatic
    SYMPTOM_TESTING_LAG = 3
    # How many symptomatic contacts can be registered before going into
    # cautious isolation
    CAUTION_THRESHOLD = 5

    GEOLOCATION_DISTANCE = 5

    RNG_SEED = 2020

    CONTACT_CULLING = True

    INFECTION_RADIUS = None
    INFECTION_PROBABILITY = None
    FALSE_ALARM_PROBABILITY = None

    RESPONSE_MODE = None

    def __init__(self, mode, severity):
        if severity == 1:
            # 'safe' numbers:
            self.INFECTION_RADIUS = 1
            self.INFECTION_PROBABILITY = 0.25
            self.FALSE_ALARM_PROBABILITY = 0.75
        elif severity == 2:
            # 'medium'
            self.INFECTION_RADIUS = 2
            self.INFECTION_PROBABILITY = 0.5
            self.FALSE_ALARM_PROBABILITY = 0.5
        elif severity == 3:
            # 'harsh'
            self.INFECTION_RADIUS = 3
            self.INFECTION_PROBABILITY = 0.75
            self.FALSE_ALARM_PROBABILITY = 0.25
        else: 
            raise ValueError


        if mode in ('A', 'a'):
            self.RESPONSE_MODE = SimulationMode.NO_REACTION
        elif mode in ('B', 'b'):
            self.RESPONSE_MODE = SimulationMode.SELF_ISOLATION
        elif mode in ('C', 'c'):
            self.RESPONSE_MODE = SimulationMode.CONTACT_TRACING
        elif mode in ('D', 'd'):
            self.RESPONSE_MODE = SimulationMode.PREEMPTIVE_ISOLATION

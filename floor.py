from enum import Enum
class Floor(Enum):
    TILE = 0
    # Further floor types may be added if necessary (e.g. floors with a movement
    # cost for pathfinding purposes or somesuch).
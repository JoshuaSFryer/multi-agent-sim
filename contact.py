from enum import Enum
class SymptomLevel(Enum):
    NONE = 0
    MILD = 1
    SEVERE = 2
class Contact:
    def __init__(self, time, loc, ID, sym):
        self.time = time
        self.contact_id = ID
        self.location = loc
        self.symptomatic = sym
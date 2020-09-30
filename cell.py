from floor import Floor
"""
Cells are individual spaces that compose an environment.
They have a floor, and should not contain more than one object at a time
(though this is currently not enforced).
"""
class Cell:
    def __init__(self, floor=Floor.TILE):
        self.floorType = floor
        self.objects = list()

    def __repr__(self):
        if not self.objects:
            if self.floorType == Floor.TILE:
                return '_'
        
        else:
            return str(self.objects[0])

    def add_object(self, obj):
        self.objects.append(obj)
    
    def remove_object(self, obj):
        self.objects.remove(obj)

    def is_occupied(self):
        return len(self.objects) > 0
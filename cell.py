from floor import Floor
from objects import Object
"""
Cells are individual spaces that compose an environment.
They have a floor, and should not contain more than one object at a time
(though this is currently not strictly enforced).
"""
class Cell:
    def __init__(self, floor=Floor.TILE):
        self.floorType = floor # Has no effect currently. May in the future.
        # List of objects placed in this cell
        self.objects = list()

    # def __repr__(self):
    #     if not self.objects:
    #         if self.floorType == Floor.TILE:
    #             return '_'
        
    #     else:
    #         return str(self.objects[0])

    def add_object(self, obj:Object) -> None:
        """
        Insert an object into this cell.

        obj: Object to place in this cell
        """

        self.objects.append(obj)
    
    def remove_object(self, obj:Object):
        """
        Remove an object from this cell.

        obj: Object to remove from this cell
        """

        self.objects.remove(obj)

    def is_occupied(self) -> bool:
        """
        Check whether there are any objects placed in this cell.
        """

        return len(self.objects) > 0
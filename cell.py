from floor import Floor
from objects import Object
"""
Cells are individual spaces that compose an environment.
They may not contain more than one object at a time.
"""
class Cell:
    def __init__(self):
        # Object placed in this cell
        self.object = None

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

        if not self.is_occupied():
            self.object = obj
        else:
            raise RuntimeError('Cell is already occupied')
    
    def remove_object(self):
        """
        Remove an object from this cell.

        obj: Object to remove from this cell
        """

        self.object = None

    def is_occupied(self) -> bool:
        """
        Check whether there are any objects placed in this cell.
        """

        return not(self.object is None)
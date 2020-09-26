"""
An environment manages a grid of Cells, which contain Objects (which can be 
agents, walls, etc). When its tick() method is called, it will execute an
update on the system, where all the agents will execute a movement based on
their own logic.
"""
from agent import MeanderingAgent
from cell import Cell
from objects import *

class Environment:

    def __init__(self, width:int, height:int):
        self.canvas_size_x = width
        self.canvas_size_y = height

        self.cells = list() # 2D list, forming a grid
        self.agents = list()

        # Build and populate a grid of Cells
        for y in range(self.canvas_size_y):
            row = list()
            for x in range(self.canvas_size_x):
                row.append(Cell())
            self.cells.append(row)

    def add_agent(self, x, y):
        new_agent = MeanderingAgent(self, x, y)
        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)

    def add_object(self, obj, x, y):
        self.cells[y][x].add_object(obj)
        obj.pos = np.array([x, y])

    def remove_object(self, obj):
        x, y = obj.pos.tolist()
        self.cells[y][x].remove_object(obj)
        self.agents.remove(obj)

    def move_object(self, obj, new_x, new_y):
        x, y = obj.pos.tolist()
        self.cells[y][x].remove_object(obj)
        obj.pos = np.array([new_x, new_y])
        self.cells[new_y][new_x].add_object(obj)
    
    def tick(self):
        """
        Tick the simulation forward one step, allowing Agents to take actions.
        """
        for agent in self.agents:
            move = agent.get_movement()
            new_pos = agent.pos + move # this is why I'm using numpy arrays.
            x, y = new_pos.tolist()
            # Check against going out of bounds, only make the move if it is
            # allowed.
            if not (x >= self.canvas_size_x or y >= self.canvas_size_y or x < 0 or y < 0):
                self.move_object(agent, x, y)



    
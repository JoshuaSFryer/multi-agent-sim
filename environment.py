"""
An environment manages a grid of Cells, which contain Objects (which can be 
agents, walls, etc). When its tick() method is called, it will execute an
update on the system, where all the agents will execute a movement based on
their own logic.
"""
from agent import MeanderingAgent, FocusedAgent
from cell import Cell
from objects import *

MAXIMUM_MOVEMENT_ATTEMPTS = 20

MINUTES_PER_DAY = 1440

class Environment:

    def __init__(self, width:int, height:int):
        self.canvas_size_x = width
        self.canvas_size_y = height

        self.cells = list() # 2D list, forming a grid
        self.agents = list()
        self.home_points = list()
        self.work_points = list()

        # Current "simulation time", in minutes. One tick advances this clock
        # by one minute. Wraps around at 1440 minutes (i.e. every 24 hours).
        self.current_time = 0

        # Build and populate a grid of Cells
        for y in range(self.canvas_size_y):
            row = list()
            for x in range(self.canvas_size_x):
                row.append(Cell())
            self.cells.append(row)


    def add_meandering_agent(self, x, y):
        new_agent = MeanderingAgent(self, x, y)
        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)


    def add_focused_agent(self, home_point, work_point):
        # Agent spawns at home
        x, y = home_point.tolist()
        new_agent = FocusedAgent(self, x, y, home_point, work_point, 10)
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
        obj.old_pos = np.array([x, y])
        obj.pos = np.array([new_x, new_y])
        self.cells[new_y][new_x].add_object(obj)

    
    def tick(self):
        """
        Tick the simulation forward one step, allowing Agents to take actions.
        """
        # Advance clock by one minute
        self.current_time += 1
        if self.current_time >= MINUTES_PER_DAY:
            self.current_time = 0
        # Upon day/night transition every 1440/2 = 720 steps (720 min = 12 hrs),
        # have agents shift from work to home or vice versa.
        if self.current_time == 0 or self.current_time == int(MINUTES_PER_DAY/2):
            for agent in self.agents:
                agent.toggle_focus()
        for agent in self.agents:
            # Generate a move repeatedly until a valid one is found
            attempts = 0 # Number of times we've tried to find a legal move
            while True: # I miss do-while loops
                attempts += 1
                move = agent.get_movement()
                new_pos = agent.pos + move
                new_x, new_y = new_pos.tolist()
                if self.validate_move(agent, new_x, new_y):
                    break
                # If we exceed the maximum number of attempts, do not move.
                if attempts >= MAXIMUM_MOVEMENT_ATTEMPTS:
                    new_x, new_y = agent.pos.tolist() # use the current coordinates
                    break
            # Execute the move
            self.move_object(agent, new_x, new_y)
                    

    def validate_move(self, agent, x, y):
        if (x >= self.canvas_size_x or y >= self.canvas_size_y 
            or x < 0 or y < 0):
            return False
        if self.cells[y][x].is_occupied(): # i.e. there is already something in that square
            return False

        return True
    
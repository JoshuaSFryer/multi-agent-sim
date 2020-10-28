"""
An environment manages a grid of Cells, which contain Objects (which can be 
agents, walls, etc). When its tick() method is called, it will execute an
update on the system, where all the agents will execute a movement based on
their own logic.
"""
from agent import *
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
        self.infected_agents = list()
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


    def add_meandering_agent(self, spawn_point:np.array) -> None:
        """
        Spawn in a MeanderingAgent.

        spawn_point:    Coordinate pair to spawn the agent at
        """
        
        x, y = spawn_point.tolist()
        new_agent = MeanderingAgent(self, x, y)
        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)


    def add_focused_agent(self, home_point:np.array, work_point:np.array) -> None:
        """
        Spawn in a FocusedAgent.

        home_point: Coordinate pair of the agent's home point
        work_point: Coordinate pair of the agent's work point
        """

        # Agent spawns at home, default focus is work
        x, y = home_point.tolist()
        new_agent = FocusedAgent(self, x, y, home_point, work_point, 10)
        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)


    def add_bio_agent(self, home_point:np.array, work_point:np.array) -> None:
        """
        Spawn in a BiologicalAgent

        home_point: Coordinate pair of the agent's home point
        work_point: Coordinate pair of the agent's work point
        """

        # Agent spawns at home, default focus is work
        x, y = home_point.tolist()
        new_agent = BiologicalAgent(self, x, y, home_point, work_point, 10)
        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)


    def add_object(self, obj:Object, x:int, y:int) -> None:
        """
        Add an object to the environment.

        TODO:   Implement collision checking so that an object cannot be placed
                where one already exists.

        obj:    The object to add
        x:      The x coordinate at which to place the object
        y:      The y coordinate at which to place the object
        """

        self.cells[y][x].add_object(obj)
        obj.pos = np.array([x, y])


    def remove_object(self, obj:Object) -> None:
        """
        Remove an object from the environment.

        obj:    The object to remove
        """

        x, y = obj.pos.tolist()
        self.cells[y][x].remove_object(obj)
        self.agents.remove(obj)


    def move_object(self, obj:Object, new_x:int, new_y:int) -> None:
        """
        Alter the position of an object in the environment.
        This method does not check against collisions (though perhaps it should),
        instead assuming that the calling code is concerned with that.

        obj:    The object to move
        new_x:  The destination x coordinate
        new_y:  The destination y coordinate
        """

        x, y = obj.pos.tolist()
        self.cells[y][x].remove_object(obj)
        obj.old_pos = np.array([x, y])
        obj.pos = np.array([new_x, new_y])
        self.cells[new_y][new_x].add_object(obj)

    
    def tick(self) -> None:
        """
        Tick the simulation forward one step, advancing the simulation clock
        and allowing Agents to take actions.
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

        # Check for infections
        for inf in self.infected_agents:
            if inf.is_infected():
                inf.progress_infection()
            else:
                self.infected_agents.remove(inf)

            # Check for disease spread
            # TODO: Optimize this to only do a local search somehow.
            for agent in self.agents:
                if not (agent is inf):
                    displacement = agent.pos - inf.pos
                    if agent.get_distance(displacement) <= INFECTION_RADIUS:
                        try:
                            if random.random() >= INFECTION_PROBABILITY:
                                self.infect_agent(agent)
                        except ValueError:
                            pass

        for agent in self.agents:
            # Generate a move repeatedly until a valid one is found
            attempts = 0 # Number of times we've tried to find a legal move
            while True: # I miss do-while loops
                attempts += 1
                if attempts < MAXIMUM_MOVEMENT_ATTEMPTS:
                    move = agent.get_movement()
                else:
                    # Pick a move at random to try to break the deadlock.
                    move = random.choice(Direction.direction_list)
                    
                new_pos = agent.pos + move
                new_x, new_y = new_pos.tolist()
                if self.validate_move(new_x, new_y):
                    break
            # Execute the move
            self.move_object(agent, new_x, new_y)
                    

    def validate_move(self, x:int, y:int) -> bool:
        """
        Check whether a position would be valid to put an object in, using the 
        following conditions:
        - The position must be within the bounds of the environment.
        - The position cannot be already occupied by another object.

        x:  The x coordinate of the space in question
        y:  The y coordinate of the space in question
        """

        if (x >= self.canvas_size_x or y >= self.canvas_size_y 
            or x < 0 or y < 0):
            return False
        if self.cells[y][x].is_occupied(): # i.e. there is already something in that square
            return False

        return True
    
    def infect_agent(self, agent:BiologicalAgent):
        try:
            agent.infect()
        except ValueError:
            # The agent could not be infected (already infected, or immune).
            return
        self.infected_agents.append(agent)

    def recover_agent(self, agent:BiologicalAgent):
        try:
            agent.recover()
        except ValueError:
            # The agent could not be cured (it wasn't infected).
            return
        self.infected_agents.remove(agent)  
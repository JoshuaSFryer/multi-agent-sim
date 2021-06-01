"""
An environment manages a grid of Cells, which contain Objects (which can be 
agents, walls, etc). When its tick() method is called, it will execute an
update on the system, where all the agents will execute a movement based on
their own logic.
"""
from agent import *
from cell import Cell
from logger import *
from objects import *
from plotter import Plotter
from simulation_parameters import SimConfig, SimulationMode

MAXIMUM_MOVEMENT_ATTEMPTS = 20
MINUTES_PER_DAY = 1440

class Environment:

    def __init__(self, width:int, height:int, config:SimConfig, run_identifier:str):
        # Flag for end of simulation
        self.complete = False

        # X and Y dimensions of the gridworld
        self.canvas_size_x = width
        self.canvas_size_y = height

        self.cells = list() # 2D list, forming a grid
        self.agents = list()

        # Lists of home and work points, used by the GUI to display
        self.home_points = list()
        self.work_points = list()

        # String that identifies the parameters this run was launched with
        # (e.g. modeA_sev1, for agent mode A and severity 1)
        self.iden = run_identifier

        # Logger that tracks the counts of susceptible, infected, and recovered
        # agents
        self.logger = Logger(self.iden)
        self.logger.create_log_file()

        self.susceptible_agents = list()
        self.infected_agents = list()
        self.recovered_agents = list()

        # Number of direct contact-tracing notifications sent
        self.num_notified_through_tracing = 0
        # Number of times any agent has gone into cautious isolation
        self.num_cautious_isolated = 0
        # Number of times any agent has gone into self-isolation
        self.num_self_isolated = 0
        # List of currently self-isolating agents
        self.curr_self_isolating = list()
        # List of currently cautiously-isolating agents
        self.curr_cautious_isolating = list()
        # Number of times any agent has received a geonotification and had
        # a recent contact in the vicinity 
        self.num_geonotified = 0
        # Number of times any agent has gone into cautious isolation, but
        # ended up not developing any symptoms (mild or severe)
        self.unnecessary_isolations = 0

        self.id_lookup = dict()

        # Current "simulation time", in minutes. One tick advances this clock
        # by one minute. Wraps to 0 at 1440 minutes (i.e. every 24 hours).
        self.current_time = 0

        # True for 'daytime', people working. False for 'nighttime', people 
        # going home.
        self.daytime = True

        self.cfg = config

        # Build and populate a grid of Cells
        for y in range(self.canvas_size_y):
            row = list()
            for x in range(self.canvas_size_x):
                row.append(Cell())
            self.cells.append(row)


    def add_agent(self, home_point:np.array, work_point:np.array) -> None:
        """
        Spawn in an agent of the appropriate type for this simulation mode.

        home_point: Coordinate pair of the agent's home point
        work_point: Coordinate pair of the agent's work point
        """

        # Agent spawns at home, default focus is work
        x, y = home_point.tolist()

        if self.cfg.RESPONSE_MODE == SimulationMode.NO_REACTION:
            new_agent = BiologicalAgent(
                self, x, y, home_point, work_point, self.cfg.AGENT_SLACK, self.cfg)
        elif self.cfg.RESPONSE_MODE == SimulationMode.SELF_ISOLATION:
            new_agent = IsolatingAgent(
                self, x, y, home_point, work_point, self.cfg.AGENT_SLACK, self.cfg)
        elif self.cfg.RESPONSE_MODE == SimulationMode.CONTACT_TRACING:
            new_agent = TraceableAgent(
                self, x, y, home_point, work_point, self.cfg.AGENT_SLACK, self.cfg)
        elif self.cfg.RESPONSE_MODE == SimulationMode.PREEMPTIVE_ISOLATION:
            new_agent = CautiousAgent(
                self, x, y, home_point, work_point, self.cfg.AGENT_SLACK, self.cfg)

        self.add_object(new_agent, x, y)
        self.agents.append(new_agent)

        self.susceptible_agents.append(new_agent)

        if self.cfg.RESPONSE_MODE in (SimulationMode.CONTACT_TRACING, 
                            SimulationMode.PREEMPTIVE_ISOLATION):
            self.id_lookup[new_agent.agent_id] = new_agent


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


    def move_object(self, obj:Object, new_x:int, new_y:int) -> None:
        """
        Alter the position of an object in the environment.
        If the new position is occupied, an exception is raised, so caller code
        should take care of avoiding this.

        obj:    The object to move
        new_x:  The destination x coordinate
        new_y:  The destination y coordinate

        raises: RuntimeError, if the destination is occupied.
        """
        try:
            x, y = obj.pos.tolist()
            self.cells[y][x].remove_object()
            obj.old_pos = np.array([x, y])
            obj.pos = np.array([new_x, new_y])
            self.cells[new_y][new_x].add_object(obj)
            
        except RuntimeError:
            print(f'Cannot place object at {x},{y}: cell occupied.')

    
    def tick(self) -> None:
        """
        Tick the simulation forward one step, advancing the simulation clock
        and allowing Agents to take actions.
        """

        # Log current state
        susceptible_count = len(self.susceptible_agents)
        infected_count = len(self.infected_agents)
        recovered_count = len(self.recovered_agents)

        infection_rate = round(infected_count / self.cfg.NUM_AGENTS, 2)
        
        self.logger.log_line(LogEntry(  self.current_time,
                                        susceptible_count,
                                        infected_count,
                                        recovered_count,
                                        infection_rate,
                                        self.num_notified_through_tracing,
                                        len(self.curr_self_isolating),
                                        self.num_self_isolated,
                                        len(self.curr_cautious_isolating),
                                        self.num_cautious_isolated,
                                        self.num_geonotified,
                                        self.unnecessary_isolations
                                        ))
           
        # Advance clock by one minute
        self.current_time += 1
        if self.current_time > self.cfg.MAXIMUM_TIME:
            self.end_simulation()
            return

        # Upon day/night transition every 1440/2 = 720 steps (720 min = 12 hrs),
        # have agents shift from work to home or vice versa.
        if self.current_time % int(MINUTES_PER_DAY/2) == 0:
            self.daytime = not self.daytime
            for agent in self.agents:
                agent.toggle_focus()

        for agent in self.agents:
            # Find all nearby agents and register contact
            nearby_agents = self.localized_search(agent, self.cfg.INFECTION_RADIUS)
            if self.cfg.RESPONSE_MODE in (SimulationMode.CONTACT_TRACING, SimulationMode.PREEMPTIVE_ISOLATION):
                for n in nearby_agents:
                    agent.register_contact(self.current_time, n)

            if agent.is_infected():
                # If the agent is contagious, roll to infect nearby agents.
                if agent.is_contagious():
                    for n in nearby_agents:
                        roll = random.random() # value between 0 and 1
                        if roll <= self.cfg.INFECTION_PROBABILITY and n.is_susceptible():
                            self.infect_agent(n)

            # Update the agent's state
            agent.tick()


            # Generate a move repeatedly until a valid one is found
            attempts = 0 # Number of times we've tried to find a legal move
            while True:
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
            or x < 0 or y < 0): # out of bounds
            return False
        if self.cells[y][x].is_occupied(): # i.e. there is already something in that square
            return False

        return True
    

    def infect_agent(self, agent:TraceableAgent):
        try:
            agent.infect()
        except ValueError as e:
            # The agent could not be infected (already infected, or immune).
            # print(f'Could not infect agent {agent.agent_id}')
            print('Could not infect agent')
            print(e)
            return

    def register_susceptible(self, agent):
        self.recovered_agents.remove(agent)
        self.susceptible_agents.append(agent)

    def register_infected(self, agent):
        self.susceptible_agents.remove(agent)
        self.infected_agents.append(agent)

    def register_recovered(self, agent):
        self.infected_agents.remove(agent)
        self.recovered_agents.append(agent)

    
    def localized_search(self, agent:Agent, radius:int):
        """
        Return a list of all Agents in the vicinity of a given Agent
        (i.e. within <radius> tiles, counting diagonals as 1).
        """

        x, y = agent.pos.tolist()
        # Get bounds of the search area, accounting for edges of the map
        min_x = max(0, x - radius)
        max_x = min(x + radius, self.canvas_size_x-1)
        min_y = max(0, y - radius)
        max_y = min(y + radius, self.canvas_size_y-1)

        local_agents = list()

        for i in range(min_x, max_x):
            for j in range(min_y, max_y):
                    cell = self.cells[j][i]
                    if cell.is_occupied():
                        # Ensure the agent does not count itself
                        if not cell.object is agent:
                            local_agents.append(cell.object)

        return local_agents

    
    def end_simulation(self):
        self.complete = True
        path = self.logger.filename
        p = Plotter(path, self.iden)

    def get_agent_by_uuid(self, id):
        return self.id_lookup[id]

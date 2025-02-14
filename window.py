# TODO: More decoupling between this view, and the model
import argparse
from environment import Environment
import math
import numpy as np
import pygame
from pygame.locals import *
import random
import sys

from logger import Logger
from plotter import Plotter
from simulation_parameters import SimConfig
from sir import SIR_status as sir

# Colour values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 128, 0)
YELLOW = (255, 255, 0)
DARK_YELLOW = (120, 120, 0)
PURPLE = (255, 0, 255)
BLUE_GRAY = (70, 70, 80)
PINK = (255, 128, 200)


HOME_COLOR = GREEN
WORK_COLOR = BLUE

agent_colors = {
    sir.SUSCEPTIBLE: DARK_YELLOW,
    sir.INCUBATING_SAFE: YELLOW,
    sir.INCUBATING_CONTAGIOUS: ORANGE,
    sir.SYMPTOMATIC_MILD: PINK,
    sir.SYMPTOMATIC_SEVERE: RED,
    sir.RECOVERED: PURPLE
}

parser = argparse.ArgumentParser()
parser.add_argument('mode')
parser.add_argument('severity', type=int)
parser.add_argument('--headless', action='store_true')
args = parser.parse_args()
headless = args.headless
if(headless):
    print("Running in headless mode")

cfg = SimConfig(args.mode, args.severity)


# Window properties
# Maximum window resolution
MAX_RES_HORIZ = 1920
MAX_RES_VERT = 1080
# Actual window resolution
WINDOW_RES_HORIZ = 1920
WINDOW_RES_VERT = 1080

# Size of each cell, in pixels
BLOCK_SIZE = 200
BLOCK_SIZE_MIN = 1
# Automatically scale BLOCK_SIZE to try to fit everything within the window
too_wide = BLOCK_SIZE * cfg.WORLD_WIDTH > MAX_RES_HORIZ
too_tall = BLOCK_SIZE * cfg.WORLD_HEIGHT > MAX_RES_VERT
while (too_wide or too_tall) and BLOCK_SIZE > BLOCK_SIZE_MIN:
    BLOCK_SIZE -= 1
    too_wide = BLOCK_SIZE * cfg.WORLD_WIDTH > MAX_RES_HORIZ
    too_tall = BLOCK_SIZE * cfg.WORLD_HEIGHT > MAX_RES_VERT

# Minimum real-time delay between simulation steps, in milliseconds
TICK_DELAY = 1

screen = None

if cfg.RNG_SEED is not None:
    random.seed(cfg.RNG_SEED)


def main():
    global screen, FPS_CLOCK
    pygame.init()
    if not headless:
        pygame.display.set_caption('Agent Simulation')
        screen = pygame.display.set_mode(
            (cfg.WORLD_WIDTH*BLOCK_SIZE, cfg.WORLD_HEIGHT*BLOCK_SIZE))
        clear_screen()

    run_identifier = f'mode{args.mode}_sev{args.severity}'

    # Build the Evironment / world
    env = Environment(cfg.WORLD_WIDTH, cfg.WORLD_HEIGHT, cfg, run_identifier)
   
    # Ensure that there are enough spaces in the gridworld to allow for one
    # work and one home point per agent.
    if not cfg.NUM_AGENTS*2 < cfg.WORLD_HEIGHT*cfg.WORLD_WIDTH:
        print('Not enough world space to spawn provided number of agents')
        sys.exit()
    spawn_agents(env)

    # Infect some of the agents
    for i in range(int(math.ceil(cfg.NUM_AGENTS * cfg.INITIAL_INFECTED_PERCENT))):
        env.infect_agent(env.agents[i])

    if not headless:
        pygame.display.update()

    # Setup time-advance event to fire every TICK_DELAY milliseconds
    TICK_EVENT = pygame.USEREVENT
    pygame.time.set_timer(TICK_EVENT, TICK_DELAY)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == TICK_EVENT:
                # Tick simulation forward
                if not env.complete:
                    env.tick()
                else:
                    running = False

            # Update the display
            if not headless:
                draw_view(env)

    sys.exit()


def draw_square(x, y, color):
    """
    Draw a square onscreen.
    """
    global screen
    rect = pygame.Rect(x*(BLOCK_SIZE), y*(BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, color, rect)


def clear_screen():
    """
    Fill the screen with white.
    """
    global screen
    screen.fill(WHITE)


def draw_view(env):
    """
    Update the screen to display agents, and their home and work points.
    """

    clear_screen()

    # Paint the background a dusky BLUE_GRAY colour at night
    if not env.daytime:
        global screen
        screen.fill(BLUE_GRAY)

    for p in env.home_points:
        x, y = p.tolist()
        draw_square(x, y, HOME_COLOR)

    for p in env.work_points:
        x, y = p.tolist()
        draw_square(x, y, WORK_COLOR)

    # Get list of agents and display them all
    for a in env.agents:
        x, y = a.pos.tolist()
        color = agent_colors[a.infection.status]
        draw_square(x, y, color)
    pygame.display.update()


def spawn_agents(env):
    """
    Spawn in agents, assigning them home and work points.
    """
    coord_list = list()

    # Generate list of all coordinate pairs (i.e. all cells)
    for x in range(cfg.WORLD_WIDTH):
        for y in range(cfg.WORLD_HEIGHT):
            coord_list.append(np.array([x,y]))

    # Shuffle the list
    random.shuffle(coord_list)

    # For each agent, pop two coordinates off the stack to use as their home
    # and work points. This avoids coordinate re-use and is much more efficient
    # than checking which coords have been used over and over.
    for n in range(cfg.NUM_AGENTS):
        home_point = coord_list.pop()
        work_point = coord_list.pop()
        # env.home_points.append(home_point)
        # env.work_points.append(work_point)
        env.add_agent(home_point, work_point)


if __name__ == '__main__':
    main()

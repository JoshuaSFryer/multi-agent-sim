# TODO: More decoupling between this view, and the model
import argparse
from environment import Environment
import math
import numpy as np
import pygame
from pygame.locals import *
import random

from simulation_parameters import *
from sir import SIR_status as sir

# Colour values
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255, 0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
ORANGE = (255,128,0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
BLUE_GRAY = (70, 70, 80)

HOME_COLOR = GREEN
WORK_COLOR = BLUE

agent_colors = {
    sir.SUSCEPTIBLE: YELLOW,
    sir.INCUBATING_SAFE: ORANGE,
    sir.INCUBATING_CONTAGIOUS: RED,
    sir.SYMPTOMATIC: RED,
    sir.RECOVERED: PURPLE
}

parser = argparse.ArgumentParser()
parser.add_argument('--headless', action='store_true')
args = parser.parse_args()
headless = args.headless
if(headless):
    print("Running in headless mode")

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
too_wide = BLOCK_SIZE * WORLD_WIDTH > MAX_RES_HORIZ
too_tall = BLOCK_SIZE * WORLD_HEIGHT > MAX_RES_VERT
while (too_wide or too_tall) and BLOCK_SIZE > BLOCK_SIZE_MIN:
    BLOCK_SIZE -= 1
    too_wide = BLOCK_SIZE * WORLD_WIDTH > MAX_RES_HORIZ
    too_tall = BLOCK_SIZE * WORLD_HEIGHT > MAX_RES_VERT


TICK_DELAY = 1

FPS_CLOCK = pygame.time.Clock()

screen = None

if RNG_SEED is not None:
    random.seed(RNG_SEED)

def main():
    global screen, FPS_CLOCK

    pygame.init()
    if not headless:
        pygame.display.set_caption('Agent Simulation')
        screen = pygame.display.set_mode((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))
        clear_screen()

    env = Environment(WORLD_WIDTH, WORLD_HEIGHT)
   
        
    spawn_agents(env)

    # Infect some of the agents
    for _ in range(int(math.ceil(NUM_AGENTS * INITIAL_INFECTED_PERCENT))):
        env.infect_agent(env.agents[0])

    if not headless:
        pygame.display.update()
    
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

            # Update the display
            if not headless:
                draw_view(env)


def draw_square(x, y, color):
    global screen
    rect = pygame.Rect(x*(BLOCK_SIZE), y*(BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, color, rect)


def clear_screen():
    global screen
    screen.fill(WHITE)


def draw_view(env):
    """
    Update the screen to display the contents of the viewport.
    NB: Viewport functionality is not yet implemented. This function just 
    updates the display.
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
    x_list = list(range(WORLD_WIDTH))
    y_list = list(range(WORLD_HEIGHT))
    random.shuffle(x_list)
    random.shuffle(y_list)
    for n in range(NUM_AGENTS):
        home_point = np.array([x_list.pop(), y_list.pop()])
        work_point = np.array([x_list.pop(), y_list.pop()])
    # while True:
    #     x = random.randint(0, WORLD_WIDTH-1)
    #     y = random.randint(0, WORLD_HEIGHT-1)
    #     focus_x = random.randint(0, WORLD_WIDTH-1)
    #     focus_y = random.randint(0, WORLD_HEIGHT-1)
    #     home_point = np.array([x, y])
    #     work_point = np.array([focus_x, focus_y])
    #     # Make sure that no two agents share the same work point or the 
    #     # same home point.
    #     valid_home = True
    #     valid_work = True
    #     for p in env.home_points:
    #         if np.array_equal(p, home_point):
    #             valid_home = False
        
    #     for p in env.work_points:
    #         if np.array_equal(p, work_point):
    #             valid_work = False

    #     if valid_home and valid_work:
    #         break

    env.home_points.append(home_point)
    env.work_points.append(work_point)
    # env.add_focused_agent(home_point, work_point)
    env.add_agent(home_point, work_point)


if __name__ == '__main__':
    main()
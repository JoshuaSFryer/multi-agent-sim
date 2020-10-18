# TODO: More decoupling between this view, and the model
from environment import Environment
import math
import numpy as np
import pygame
from pygame.locals import *
import random

# Colour values
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255, 0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

AGENT_COLOR = RED
HOME_COLOR = GREEN
WORK_COLOR = BLUE

# Window properties
# Maximum window resolution
MAX_RES_HORIZ = 1920
MAX_RES_VERT = 1080
# Actual window resolution
WINDOW_RES_HORIZ = 1920
WINDOW_RES_VERT = 1080

# Number of cells in the environment
WORLD_WIDTH = 50
WORLD_HEIGHT = 50

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

NUM_AGENTS = 3
TICK_DELAY = 500

FPS_CLOCK = pygame.time.Clock()

screen = None

def main():
    global screen, FPS_CLOCK

    is_dragging = False
    mousePos = (0, 0)
    dragStart = (0, 0)
    dragEnd = (0, 0)
    mouse_x = 0
    mouse_y = 0

    vp_curr_x = 0
    vp_curr_y = 0

    pygame.init()
    pygame.display.set_caption('Agent Simulation')
    screen = pygame.display.set_mode((WORLD_WIDTH*BLOCK_SIZE, WORLD_HEIGHT*BLOCK_SIZE))

    clear_screen()

    env = Environment(WORLD_WIDTH, WORLD_HEIGHT)
    for i in range(NUM_AGENTS):
        spawn_agent(env)

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
                env.tick()

            # Update the display
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
    
    for p in env.home_points:
        x, y = p.tolist()
        draw_square(x, y, HOME_COLOR)

    for p in env.work_points:
        x, y = p.tolist()
        draw_square(x, y, WORK_COLOR)

    # Get list of agents and display them all
    for a in env.agents:
        x, y = a.pos.tolist()
        draw_square(x, y, AGENT_COLOR)

    pygame.display.update()


def spawn_agent(env):
    while True:
        x = random.randint(0, WORLD_WIDTH-1)
        y = random.randint(0, WORLD_HEIGHT-1)
        focus_x = random.randint(0, WORLD_WIDTH-1)
        focus_y = random.randint(0, WORLD_HEIGHT-1)
        home_point = np.array([x, y])
        work_point = np.array([focus_x, focus_y])
        # Make sure that no two agents share the same work point or the 
        # same home point.
        valid_home = True
        valid_work = True
        for p in env.home_points:
            if np.array_equal(p, home_point):
                valid_home = False
        
        for p in env.work_points:
            if np.array_equal(p, work_point):
                valid_work = False

        if valid_home and valid_work:
            break

    env.home_points.append(home_point)
    env.work_points.append(work_point)
    env.add_focused_agent(home_point, work_point)

# def zoom_in():
#     global BLOCK_SIZE, screen
#     BLOCK_SIZE += 1
#     # clear_screen()

# def zoom_out():
#     global BLOCK_SIZE, screen
#     if BLOCK_SIZE > BLOCK_SIZE_MIN:
#         BLOCK_SIZE -= 1
#         # clear_screen()

# def pan_view(dx, dy):
#     global vp_curr_x, vp_curr_y, vp_max_x, vp_max_y
#     if vp_curr_x <= vp_max_x and vp_curr_x >= vp_min_x:
#         vp_curr_x = vp_curr_x - dx
#         # Constrain new coordinate within bounds
#         if vp_curr_x > vp_max_x:
#             vp_curr_x = vp_max_x
#         if vp_curr_x < vp_min_x:
#             vp_curr_x = vp_min_x # This will almost always be 0, I think...

#     if vp_curr_y <= vp_max_y and vp_curr_y >= vp_min_y:
#         vp_curr_y = vp_curr_y - dy
#         # Constrain new coordinate within bounds
#         if vp_curr_y > vp_max_y:
#             vp_curr_y = vp_max_y
#         if vp_curr_y < vp_min_y:
#             vp_curr_y = vp_min_y # This will almost always be 0, I think...

#     print(f"Viewport origin: ({vp_curr_x}, {vp_curr_y})")



if __name__ == '__main__':
    main()
from environment import Environment
import pygame
import random

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255, 0,0)

MAX_RES_HORIZ = 2200
MAX_RES_VERT = 1440

WIDTH = 250
HEIGHT = 250
BLOCK_SIZE = 5

too_wide = BLOCK_SIZE * WIDTH > MAX_RES_HORIZ
too_tall = BLOCK_SIZE * HEIGHT > MAX_RES_VERT

while (too_wide or too_tall) and BLOCK_SIZE > 1:
    BLOCK_SIZE -= 1
    too_wide = BLOCK_SIZE * WIDTH > MAX_RES_HORIZ
    too_tall = BLOCK_SIZE * HEIGHT > MAX_RES_VERT

TICK_DELAY = 200

def main():
    

    pygame.init()
    pygame.display.set_caption('Agent Simulation')
    screen = pygame.display.set_mode((WIDTH*BLOCK_SIZE, HEIGHT*BLOCK_SIZE))

    draw_grid(screen, HEIGHT, WIDTH, BLOCK_SIZE)
    
    env = Environment(WIDTH, HEIGHT)
    for i in range(6):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        env.add_agent(x, y)


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
        # Wipe the grid clean
        draw_grid(screen, HEIGHT, WIDTH, BLOCK_SIZE)
        # Draw agents
        for a in env.agents:
            x, y = a.pos.tolist()
            draw_square(screen, x, y, BLOCK_SIZE, RED)
        pygame.display.update()


def draw_square(screen, x, y, size, color):
    rect = pygame.Rect(x*(size), y*(size), size, size)
    pygame.draw.rect(screen, color, rect)



def draw_grid(screen, height, width, size):
    for y in range(height):
        for x in range(width):
            draw_square(screen, x, y, size, WHITE)

if __name__ == '__main__':
    main()
import pygame
from config import win_width, win_height, max_fps
from classes import Taz

def init():
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("TAZ")
    clock = pygame.time.Clock()

    return win, clock

def loop(win, clock):
    win.fill((0,0,0))
    taz.draw()
    pygame.display.flip()

win, clock = init()
taz = Taz(win, clock)
while True:
    clock.tick(max_fps)
    loop(win, clock)

#pygame.quit()
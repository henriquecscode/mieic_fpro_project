import pygame
from config import win_width, win_height, max_fps
from classes import Taz, GameScreen

def init():
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("TAZ")
    clock = pygame.time.Clock()

    return win, clock

def loop(win, clock):
    win.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        taz.move_left()
    if keys[pygame.K_RIGHT]:
        taz.move_right()
    if keys[pygame.K_UP]:
        taz.move_up()
    if keys[pygame.K_DOWN]:
        taz.move_down()

    taz.draw()
    screen.draw()
    pygame.display.flip()

win, clock = init()
taz = Taz(win, clock)
screen = GameScreen(win)
while True:
    clock.tick(max_fps)
    loop(win, clock)

#pygame.quit()
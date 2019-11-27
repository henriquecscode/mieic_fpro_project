import pygame
from config import line_height, line_total_height, line_width, win_height, win_width

class Taz():
    min_y = win_height /2 - line_total_height / 2
    max_y = win_height / 2 + line_total_height / 2
    min_x = win_width / 2 - line_width / 2
    max_x = win_width / 2 + line_width / 2
    line_height = line_height

    velocity = 4
    width = 30
    height = 30
    color = (255, 0, 0)

    def __init__(self, win, clock):
        self.x = win_width / 2
        self.y = win_height / 2
        self.win = win
        self.clock = clock  

    def move_up(self):
        if self.y - self.line_height >= self.min_y:
            self.y -= self.line_height

    def move_down(self):
        if self.y + self.line_height <= self.max_y:
            self.y += self.line_height
            

    def move_left(self):
        if self.x - self.velocity >= self.min_x:
            self.x -= self.velocity

    def move_right(self):
        if self.x + self.velocity <= self.max_x:
            self.x += self.velocity

    def draw(self):
        pygame.draw.rect(self.win, self.color, ((self.x - self.width/2, self.y - self.height/2), (self.width, self.height)))


import pygame
from config import line_height, line_total_height, line_width, win_height, win_width


class Taz():
    min_x = win_width / 2 - line_width / 2
    max_x = win_width / 2 + line_width / 2
    min_y = win_height / 2 - line_total_height / 2
    max_y = win_height / 2 + line_total_height / 2

    line_height = line_height

    velocity = 10
    width = 30
    height = 30
    color = (255, 0, 0)

    # So it doesn't automatically jump lines
    up_thres = 10
    down_thres = 10

    def __init__(self, win, clock):
        self.x = win_width / 2
        self.y = win_height / 2
        self.win = win
        self.clock = clock

        self.up_request = 0
        self.down_request = 0

    def move_up(self):
        self.up_request += 1
        self.down_request = 0
        if self.up_request >= self.up_thres:
            self.up_request = 0
            if self.y - self.line_height >= self.min_y:
                self.y -= self.line_height

    def move_down(self):
        self.down_request += 1
        self.up_request = 0
        if self.down_request >= self.down_thres:
            self.down_request = 0
            if self.y + self.line_height < self.max_y:
                self.y += self.line_height

    def move_left(self):
        if self.x - self.velocity >= self.min_x:
            self.x -= self.velocity

    def move_right(self):
        if self.x + self.velocity <= self.max_x:
            self.x += self.velocity

    def draw(self):
        pygame.draw.rect(self.win, self.color, ((
            self.x - self.width/2, self.y - self.height/2), (self.width, self.height)))


class GameScreen():

    lines_number = line_total_height // line_height
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width / 2 + line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / \
        2 + 16  # Shift of 18 to lay beneath taz
    line_height = line_height

    color = (255, 0, 0)

    def __init__(self, win):
        self.win = win

    def draw(self):
        for i in range(self.lines_number):
            pygame.draw.line(self.win, self.color, (self.min_x, self.min_y + i * self.line_height),
                             (self.max_x, self.min_y + i * self.line_height))

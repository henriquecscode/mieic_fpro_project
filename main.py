import pygame
from config import win_width, win_height, max_fps, line_height, line_total_height, line_width


def init():
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("TAZ")
    clock = pygame.time.Clock()

    return win, clock

class Movable:
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width /2 - line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / 2

    width = 30
    height = 30

    velocity = 10
    def __init__(self, win, x, y, color, direction=1, difficulty=1):
        self.win = win
        self.x = x
        self.y = y
        self.direction = direction
        self.difficulty = difficulty
        self.color = color

    def move(self):
        self.x += self.direction * self.velocity * self.difficulty ** 0.5

        return self.x < self.min_x or self.x > self.max_x
        # If the return value is true we can delete the object

    def draw(self):
        pygame.draw.rect(self.win, self.color, (self.x - self.width / 2, self.y - self.height / 2), (self.width, self.height))

    def loop(self):
        self.draw()
        return self.move()

class Obstacle(Movable):

    color = (100, 100, 100)

    def __init__(self, win, x, y, direction, difficulty):
        super().__init__(win, x, y, self.color, direction, difficulty)

class Reward(Movable):

    color = (0, 100, 100)
    
    def __init__(self, win, x, y, direction, difficulty):
        super().__init__(win, x, y, self.color, direction, difficulty)
    

class Taz:
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
        self.win = win
        self.x = win_width / 2
        self.y = win_height / 2
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

    def loop(self):
        self.draw()


class Game:

    lines_number = line_total_height // line_height
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width / 2 + line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / \
        2 + 16  # Shift of 18 to lay beneath taz
    line_height = line_height
    obstacles = []
    rewards = []

    color = (255, 0, 0)

    def __init__(self, win, clock):
        self.win = win
        self.clock = clock
        self.font = pygame.font.SysFont('comicsans', 30, True) #(font, size, bold, italicized)
        self.taz = Taz(win, clock)

    def draw(self):
        for i in range(self.lines_number):
            pygame.draw.line(self.win, self.color, (self.min_x, self.min_y + i * self.line_height),
                             (self.max_x, self.min_y + i * self.line_height))

    def loop(self):   
        while True:
            self.clock.tick(max_fps)
            self.win.fill((0, 0, 0))

            self.events()

            text =self.font.render(str(pygame.time.get_ticks()), 1, (255, 255, 255))
            self.win.blit(text, (0,0))
            self.loop_rewards()
            self.loop_obstacles()
            self.taz.loop()
            self.draw()

            pygame.display.flip()

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.taz.move_left()
        if keys[pygame.K_RIGHT]:
            self.taz.move_right()
        if keys[pygame.K_UP]:
            self.taz.move_up()
        if keys[pygame.K_DOWN]:
            self.taz.move_down()

    # Could probably join these two, semantically it is cleaner this way though
    def loop_rewards(self):
        self.rewards = [x for x in self.rewards if loop(x)]
    
    def loop_obstacles(self):
        self.obstacles = [x for x in self.obstacles if loop(x)]
        # Simultaneously draws, moves and deletes the object if need be



win, clock = init()
game = Game(win, clock)
game.loop()

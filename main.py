import pygame
import random
from config import win_width, win_height, max_fps, line_height, line_total_height, line_width


def init():
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("TAZ")
    clock = pygame.time.Clock()

    return win, clock


class Movable:
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width / 2 + line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / 2

    width = 30
    height = 30

    velocity = 2

    def __init__(self, win, x, y, color, direction=1, difficulty=1):
        self.win = win
        self.x = x
        self.y = y
        self.direction = direction
        self.difficulty = difficulty
        self.color = color

    def move(self):
        self.x += self.direction * self.velocity * self.difficulty ** 0.5
        return not(self.x < self.min_x or self.x > self.max_x)
        # If the return value is true we can delete the object

    def draw(self):
        pygame.draw.rect(self.win, self.color, ((
            self.x - self.width / 2, self.y - self.height / 2), (self.width, self.height)))

    def collision(self, collide):

        if not collide.running:
            return True

        if self.y != collide.y:
            return True

        if ((collide.x - collide.width / 2) < (self.x + self.width/2) < (collide.x + collide.width / 2)) or ((collide.x - collide.width / 2) < (self.x - self.width / 2) < (collide.x + collide.width / 2)):
            return False

        return True

    def loop(self, collide):
        self.draw()
        not_of_bounds = self.move()
        not_hit = self.collision(collide)
        return not_of_bounds, not_hit


class Obstacle(Movable):

    color = (255, 100, 100)

    def __init__(self, win, x, y, direction, difficulty=1):
        super().__init__(win, x, y, self.color, direction, difficulty)

    def loop(self, collide):
        not_of_bounds, not_hit = super().loop(collide)
        if not not_hit:
            collide.running = False
        return not_of_bounds and not_hit


class Reward(Movable):

    color = (255, 255, 0)
    score = 50

    def __init__(self, win, x, y, direction, difficulty=1):
        super().__init__(win, x, y, self.color, direction, difficulty)

    def loop(self, collide):
        not_of_bounds, not_hit = super().loop(collide)
        if not not_hit:
            collide.score += self.score
        return not_of_bounds and not_hit


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
        self.clock = clock
        self.reset()

    def reset(self):
        self.x = win_width / 2
        self.y = win_height / 2
        self.up_request = 0
        self.down_request = 0
        self.running = True
        self.score = 0

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
        if self.running:
            self.draw()


class Game:

    lines_number = line_total_height // line_height
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width / 2 + line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / 2
    line_min_y = min_y + 16
    line_height = line_height

    color = (255, 0, 0)

    # Deal with spawning of movable objects
    event_timer = 4000
    event_time_elapsed = 3000
    obstacle_only_chance = 0.2
    reward_only_chance = 0.6
    mixed_chance = 0.2
    type_chance = [obstacle_only_chance, reward_only_chance, mixed_chance]
    type_chance = [0, obstacle_only_chance,
                   obstacle_only_chance + reward_only_chance]  # Temporary
    #type_chance = [type_chance[:i] for i in range(len(type_chance)) ]
    mixed_obstacle_chance = 0.5
    mixed_reward_chance = 0.5
    mixed_type_chance = [mixed_obstacle_chance, mixed_reward_chance]
    mixed_type_chance = [0, mixed_obstacle_chance]
    # mixed_type_chance = [sum(mixed_type_chance[:i]) for i in range(len(mixed_type_chance))]

    def __init__(self, win, clock):
        self.win = win
        self.clock = clock
        # (font, size, bold, italicized)
        self.font = pygame.font.SysFont('comicsans', 30, True)
        self.taz = Taz(win, clock)
        self.reset()

    def reset(self):
        self.obstacles = []
        self.rewards = []
        self.event_time_elapsed = 3000
        self.taz.reset()

    def draw(self):
        for i in range(self.lines_number):
            pygame.draw.line(self.win, self.color, (self.min_x, self.line_min_y + i * self.line_height),
                             (self.max_x, self.line_min_y + i * self.line_height))

    def loop(self):
        while True:
            self.clock.tick(max_fps)
            self.event_time_elapsed += self.clock.get_time()
            self.win.fill((0, 0, 0))

            end = self.events()  # keys handling
            if end:
                return
            self.spawn()  # Movable spawning

            # Score
            score = self.font.render(str(self.taz.score), 1, (255, 255, 255))
            self.win.blit(score, (0, 0))

            self.loop_rewards()
            self.loop_obstacles()
            self.taz.loop()
            self.draw()  # Platforms draw

            pygame.display.flip()

    def spawn(self):
        if not self.taz.running:
            return
        if self.event_time_elapsed > self.event_timer:
            # We are going to create a event
            rand = random.random()
            if 0 <= rand <= self.type_chance[1]:
                # We are going to have obstacle only
                for i in range(self.lines_number):
                    direction = -1 if random.random() < 0.5 else 1
                    x = win_width / 2 + -1 * direction * line_width / 2
                    y = self.min_y + i * self.line_height

                    self.obstacles.append(Obstacle(self.win, x, y, direction))

            elif self.type_chance[1] < rand <= self.type_chance[2]:
                # We are going to have reward only
                for i in range(self.lines_number):
                    direction = -1 if random.random() < 0.5 else 1
                    x = win_width / 2 + -1 * direction * line_width / 2
                    y = self.min_y + i * self.line_height

                    self.rewards.append(Reward(self.win, x, y, direction))

            else:
                for i in range(self.lines_number):
                    direction = -1 if random.random() < 0.5 else 1
                    x = win_width / 2 + -1 * direction * line_width / 2
                    y = self.min_y + i * self.line_height
                    rand = random.random()
                    if rand < self.mixed_obstacle_chance:
                        self.obstacles.append(
                            Obstacle(self.win, x, y, direction))
                    else:
                        self.rewards.append(Reward(self.win, x, y, direction))
                # We are going to have mixed
            self.event_time_elapsed = 0

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.taz.move_left()
        if keys[pygame.K_RIGHT]:
            self.taz.move_right()
        if keys[pygame.K_UP]:
            self.taz.move_up()
        if keys[pygame.K_DOWN]:
            self.taz.move_down()

        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            if not self.taz.running:
                self.reset()

    # Could probably join these two, semantically it is cleaner this way though
    def loop_rewards(self):
        self.rewards = [x for x in self.rewards if x.loop(self.taz)]
        # The else clause needs to be another type of objects that disappears after a certain time, to replicate the original game

    def loop_obstacles(self):
        self.obstacles = [x for x in self.obstacles if x.loop(self.taz)]
        # Simultaneously draws, moves and deletes the object if need be


win, clock = init()
game = Game(win, clock)
game.loop()

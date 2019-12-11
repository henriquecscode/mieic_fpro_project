import pygame
import random
from config import win_width, win_height, max_fps, line_height, line_total_height, line_width
pygame.init()


def rescale_sprites(sprites, width, height):
    def rescale_sprite(sprite, width, height):
        return pygame.transform.scale(sprite, (width, height))
    return [rescale_sprite(x, width, height) for x in sprites]

def init():
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("TAZ")
    clock = pygame.time.Clock()
    spritesheet_taz = Spritesheet('assets/taz.png')
    sprites_taz = spritesheet_taz.load_strip(((516, 338, 388/6, 90)), 6, -1)
    sprites_obstacle = Spritesheet('assets/props.png').image_at((126, 70, 30, 30), -1)
    sprites_reward = Spritesheet('assets/props.png').image_at((162, 5, 30, 30), -1)

    return win, clock, [sprites_taz, sprites_obstacle, sprites_reward]


class Spritesheet(object):  # https://www.pygame.org/wiki/Spritesheet
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            print('Unable to load spritesheet image:' + message)
            raise SystemExit
    # Load a specific image from a specific rectangle

    def image_at(self, rectangle, colorkey=None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list

    def images_at(self, rects, colorkey=None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images

    def load_strip(self, rect, image_count, colorkey=None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class Movable:
    min_x = win_width / 2 - line_width / 2 - 20
    max_x = win_width / 2 + line_width / 2 + 20
    min_y = win_height / 2 - line_total_height / 2

    width = 30
    height = 30

    velocity = 2

    def __init__(self, win, x, y, color, sprite, direction=1, difficulty=1):
        self.win = win
        self.x = x
        self.y = y
        self.color = color
        self.sprite = rescale_sprites([sprite], self.width, self.height)[0]
        self.direction = direction
        self.difficulty = difficulty

    def move(self):
        self.x += self.direction * self.velocity * self.difficulty ** 0.5
        return not(self.x < self.min_x or self.x > self.max_x)
        # If the return value is true we can delete the object

    def draw(self):
        self.win.blit(self.sprite, (self.x - self.width/2, self.y - self.height/2))

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

    def __init__(self, win, x, y, sprite, direction, difficulty=1):
        super().__init__(win, x, y, self.color, sprite, direction, difficulty)

    def loop(self, collide):
        not_of_bounds, not_hit = super().loop(collide)
        if not not_hit:
            collide.running = False
        return not_of_bounds and not_hit


class Reward(Movable):

    color = (255, 255, 0)
    score = 50

    def __init__(self, win, x, y, sprite, direction, difficulty=1):
        super().__init__(win, x, y, self.color, sprite, direction, difficulty)

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
    width = 40
    height = 50
    color = (255, 0, 0)
    font=pygame.font.SysFont('comicsans', 30, True)
    text = font.render('Game Over', True, (255, 255, 255))
    text_width, text_height = font.size('Game Over')

    # So it doesn't automatically jump lines
    up_thres = 10
    down_thres = 10

    tick_per_sprites = 3

    def __init__(self, win, clock, sprites):
        self.win = win
        self.clock = clock
        self.reset()
        self.sprites = rescale_sprites(sprites, self.width, self.height)
        self.sprites_count = 0

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
        self.win.blit(self.sprites[self.sprites_count //
                              self.tick_per_sprites], (self.x - self.width/2, self.y - self.height/2))
        self.sprites_count = (self.sprites_count +
                              1) % (len(self.sprites) * self.tick_per_sprites)

    def loop(self):
        if self.running:
            self.draw()

        else:
            self.win.blit(self.text, ((win_width-self.text_width)/2, (win_height-self.text_height)/2))


class Game:
    scenes = {}
    scene = None
    #scenes = {'game': None, 'menu': None }

    def __init__(self, win, clock, *args):
        # *args are the sprites
        # 0 is for taz
        self.win = win
        self.clock = clock
        self.scenes['game'] = GameScene(win,clock, *args)
        def to_game():
            self.scene = self.scenes['game']
        self.scenes['menu'] = MenuScene(win,clock, to_game = to_game)
        self.scene = self.scenes['menu']

    def loop(self):
        while True:

            self.clock.tick(max_fps)
            self.scene.loop()
            # Exit condition
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

            pygame.display.flip()



class MenuScene:

    buttons = {}
    def __init__(self, win, clock, **kargs):
        play_button = Button(win, 'Play', pygame.font.SysFont('comicsans', 30, True), kargs['to_game'])
        self.buttons['game'] = play_button
        self.choose_button('game')

    def choose_button(self, name):
        self.button = self.buttons[name]
        self.highlight(name)

    def highlight(self, name):
        for key in self.buttons:
            self.buttons[key].highlight = False
        self.buttons[name].highlight = True

    def loop(self):

        self.events()

        for key in self.buttons:
            self.buttons[key].draw()

    def events(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.button.select()


class GameScene:

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

    def __init__(self, win, clock, *args):
        self.win = win
        self.clock = clock
        # (font, size, bold, italicized)
        self.font = pygame.font.SysFont('comicsans', 30, True)
        self.taz = Taz(win, clock, args[0])
        self.sprites_obstacle, self.sprites_reward = args[1], args[2]
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
        self.event_time_elapsed += self.clock.get_time()
        self.win.fill((0, 0, 0))

        self.events()  # keys handling
        self.spawn()  # Movable spawning

        # Score
        score = self.font.render(str(self.taz.score), True, (255, 255, 255))
        self.win.blit(score, (0, 0))

        self.loop_rewards()
        self.loop_obstacles()
        self.taz.loop()
        self.draw()  # Platforms draw

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

                    # To prevent all bombs from coming in the same direction
                    # Probably a slow implementation but should not affect performance too much
                    if i == self.lines_number - 1:
                        list_directions = list(map(lambda x: x.direction, self.obstacles[-self.lines_number+1:]))
                        if len(list(filter(lambda x: x == list_directions[0], list_directions))) == len(list_directions):
                            #Means that al directions are equal 
                            direction = direction if direction == self.obstacles[-1].direction else -direction # Changes the direction if it is the same as all others

                    self.create_obstacle(i, direction)

            elif self.type_chance[1] < rand <= self.type_chance[2]:
                # We are going to have reward only
                for i in range(self.lines_number):
                    direction = -1 if random.random() < 0.5 else 1
                    self.create_reward(i, direction)

            else:
                for i in range(self.lines_number):
                    direction = -1 if random.random() < 0.5 else 1
                    rand = random.random()
                    if rand < self.mixed_obstacle_chance:
                        self.create_obstacle(i, direction)
                    else:
                        self.create_obstacle(i, direction)
                # We are going to have mixed
            self.event_time_elapsed = 0

    def events(self):

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

    def create_reward(self, y, direction):
        x = win_width / 2 + -1 * direction * line_width / 2
        y = self.min_y + y * self.line_height
        self.rewards.append(Reward(self.win, x, y, self.sprites_reward, direction))

    def create_obstacle(self, y, direction):
        x = win_width / 2 + -1 * direction * line_width / 2
        y = self.min_y + y * self.line_height
        self.rewards.append(Obstacle(self.win, x, y, self.sprites_obstacle, direction))


class Button:

    def __init__(self, win, text, font=pygame.font.SysFont('comicsans', 30, True), function=None, highlight=False, x=win_width/4, y=50, width=win_width/2, height=50, text_color=(255, 255, 255), color=(0, 9, 151), high_text_color=(255, 255, 255), high_color=(100, 100, 100)):
        self.win = win
        self.function = function
        self.highlight = highlight
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.high_color = high_color
        self.highlight_text, self.lowlight_text, self.text_width, self.text_height = self.render(
            text, font, high_text_color, text_color)

    def render(self, text, font, high_text_color, text_color):
        if font:
            self.font = font
        highlight_text = self.font.render(text, True, high_text_color)
        lowlight_text = self.font.render(text, True, text_color)
        text_width, text_height = self.font.size(text)
        return highlight_text, lowlight_text, text_width, text_height

    def draw(self):

        text_x, text_y = self.x + self.width/2 - self.text_width / \
            2, self.y + self.height/2 - self.text_height/2
        if self.highlight:
            color = self.high_color
            text = self.highlight_text
        else:
            color = self.color
            text = self.lowlight_text

        pygame.draw.rect(self.win, color, ((self.x, self.y),
                                           (self.width, self.height)))
        win.blit(text, (text_x, text_y))

    def select(self):
        self.function()


win, clock, sprites = init()
game = Game(win, clock, *sprites)
game.loop()
pygame.quit()

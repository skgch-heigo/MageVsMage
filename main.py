import random
import sys
import os

import pygame

import Bullet_code


pygame.init()

size = WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode(size)

FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Move:
    def __init__(self, move_type, *args):
        self.type = move_type
        self.time = 0
        self.speed_x = 0
        self.speed_y = 0
        self.image = None
        self.image_final = None
        self.bounce = 0
        self.prep_time = 0
        self.x = 0
        self.y = 0
        self.timer = 0
        if move_type == "wait":
            self.time = args[0]
        elif move_type == "area_attack":
            self.image = args[0]
            self.image_final = args[1]
            self.x = args[2]
            self.y = args[3]
            self.speed_x = args[4]
            self.speed_y = args[5]
            self.timer = args[6]
            self.prep_time = args[7]
        else:
            self.image = args[0]
            self.x = args[1]
            self.y = args[2]
            self.speed_x = args[3]
            self.speed_y = args[4]
            self.bounce = args[5]
        self.args = args


class Player(pygame.sprite.Sprite):
    def __init__(self, speed, max_life, refill_time):
        super().__init__(characters, all_sprites)
        self.direction = "forward"
        self.move = "standing"
        self.running = False
        self.frame = 0
        self.image = player_image[self.move + "_" + self.direction][self.frame]
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.speed = speed
        self.max_life = max_life
        self.refill_time = refill_time

    def update(self, *args):
        if not self.running:
            if pygame.key.get_pressed()[pygame.K_d]:
                self.rect.x = min(self.rect.x + self.speed, FIELD_WIDTH + LEFT_F_SPACE - self.rect.width)
                self.direction = "right"
                self.move = "walking"
            if pygame.key.get_pressed()[pygame.K_w]:
                self.rect.y = max(self.rect.y - self.speed, TOP_F_SPACE)
                self.direction = "backward"
                self.move = "walking"
            if pygame.key.get_pressed()[pygame.K_a]:
                self.rect.x = max(self.rect.x - self.speed, LEFT_F_SPACE)
                self.direction = "left"
                self.move = "walking"
            if pygame.key.get_pressed()[pygame.K_s]:
                self.rect.y = min(self.rect.y + self.speed, FIELD_HEIGHT + TOP_F_SPACE - self.rect.height)
                self.direction = "forward"
                self.move = "walking"
            if not (pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_w] or
                    pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_s]):
                self.move = "standing"
        self.frame += 1
        self.image = player_image[self.move + "_" + self.direction][self.frame // 10 %
                                                                    len(player_image[self.move + "_"
                                                                                     + self.direction])]

    def spawn(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        self.rect.x = pos_x
        self.rect.y = pos_y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, max_life, refill_time, open_time, image):
        super().__init__(characters, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.open_time = open_time
        self.x = 0
        self.y = 0
        self.max_life = max_life
        self.refill_time = refill_time

    def update(self, *args):
        pass

    def spawn(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        self.rect.x = pos_x
        self.rect.y = pos_y


class Information(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(all_sprites)
        self.image = image

        self.x = pos_x
        self.y = pos_y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    # code

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def level_draw(level):
    image = pygame.Surface((1024, 768))
    image.fill(BACKGROUND_COLOR)
    field = load_image("game_sprites/background/background_game3.png")
    image.blit(field, (50, 90))
    return image


def start_level(level):
    # level start
    level_run = True
    level_back = level_draw(level)
    player = Player(*player_stats)
    player.spawn(*START_POINT)
    enemy = enemies[level]
    enemy.spawn(*ENEMY_POINT)
    timer = 0
    enemy_do = random.choice(enemy_moves[level])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
        if not level_run:
            return  # level ended
        if not enemy_do:
            enemy_do = random.choice(enemy_moves[level])
        if enemy_do[0].type == "wait":
            if timer < enemy_do[0].time:
                timer += 1
            else:
                del enemy_do[0]
                timer = 0
        elif enemy_do[0].type == "area_attack":
            pass
        else:
            Bullet_code.Bullet((all_sprites, bullets, enemy_bullets), *enemy_do[0].args, "enemy")
            del enemy_do[0]
        screen.blit(level_back, (0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def pause():
    # paused game menu
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return  # return from pause
        pygame.display.flip()
        clock.tick(FPS)


fps = 50
pygame.display.set_caption("MageVsMage")
# пикселей в секунду


BACKGROUND_COLOR = (61, 61, 61)
START_POINT = (260, 500)
ENEMY_POINT = (260, 130)
FIELD_WIDTH = 453
FIELD_HEIGHT = 588
LEFT_F_SPACE = 50
TOP_F_SPACE = 90


screen.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()
# основной персонаж

# группы спрайтов
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
characters = pygame.sprite.Group()


running = True

start_screen()
# change if other character was selected
player_image = {"standing_forward":
                    [load_image(f"game_sprites/sprites_Frossin/standing_forward/standing_forward{i}.png")
                     for i in range(1, 3)],
                "standing_backward":
                    [load_image(f"game_sprites/sprites_Frossin/standing_backward/standing_backward{i}.png")
                     for i in range(1, 3)],
                "standing_left":
                    [load_image(f"game_sprites/sprites_Frossin/standing_left/standing_left{i}.png")
                     for i in range(1, 3)],
                "standing_right":
                    [load_image(f"game_sprites/sprites_Frossin/standing_right/standing_right{i}.png")
                     for i in range(1, 3)],
                "walking_forward":
                    [load_image(f"game_sprites/sprites_Frossin/walking_forward/walking_forward{i}.png")
                     for i in range(1, 5)],
                "walking_backward":
                    [load_image(f"game_sprites/sprites_Frossin/walking_forward/walking_forward{i}.png")
                     for i in range(1, 5)],
                "walking_left":
                    [load_image(f"game_sprites/sprites_Frossin/walking_left/walking_left{i}.png")
                     for i in range(1, 10)],
                "walking_right":
                    [load_image(f"game_sprites/sprites_Frossin/walking_right/walking_right{i}.png")
                     for i in range(1, 10)],
                "run_forward":
                    [load_image(f"game_sprites/sprites_Frossin/run_forward/run_forward{i}.png")
                     for i in range(1, 9)],
                "run_backward":
                    [load_image(f"game_sprites/sprites_Frossin/run_forward/run_forward{i}.png")
                     for i in range(1, 9)],
                "run_left":
                    [load_image(f"game_sprites/sprites_Frossin/run_left/run_left{i}.png")
                     for i in range(1, 14)],
                "run_right":
                    [load_image(f"game_sprites/sprites_Frossin/run_right/run_right{i}.png")
                     for i in range(1, 14)]}

player_stats = (3, 100, 15000)
enemies = [None, None, Enemy(600, 20000, 500, load_image("game_sprites/sprites_Atanim/standing_forward1.png",
                                                    colorkey=(255, 255, 255)))]
enemy_moves = [[[], [], [], []],
               [[], [], [], []],
               [[Move("wait", 100) if i % 2 == 1 else
                 Move("bullet", load_image("game_sprites/bullets/blood_drop.png"),
                      random.randint(LEFT_F_SPACE, LEFT_F_SPACE + FIELD_WIDTH - 30), TOP_F_SPACE,
                      0, random.randint(1, 4), 0)
                 for i in range(20)]]]


while running:
    # menu
    screen.fill(BACKGROUND_COLOR)
    for event in pygame.event.get():
        # при закрытии окна
        if event.type == pygame.QUIT:
            running = False
    start_level(2)
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()

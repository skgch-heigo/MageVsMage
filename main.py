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


player_image = load_image('mario.png')


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, speed, max_life, refill_time):
        super().__init__(characters, all_sprites)
        self.image = player_image

        self.x = pos_x
        self.y = pos_y
        self.speed = speed
        self.max_life = max_life
        self.refill_time = refill_time

    def update(self, *args):
        pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, speed, max_life, refill_time, image):
        super().__init__(characters, all_sprites)
        self.image = image

        self.x = pos_x
        self.y = pos_y
        self.speed = speed
        self.max_life = max_life
        self.refill_time = refill_time

    def update(self, *args):
        pass


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


def start_level(level):
    # level start
    level_run = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
        if not level_run:
            return  # level ended
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
pygame.display.set_caption("Платформы")
# пикселей в секунду
screen.fill("black")
clock = pygame.time.Clock()
# основной персонаж

# группы спрайтов
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
characters = pygame.sprite.Group()


running = True

start_screen()
while running:
    # menu
    screen.fill("black")
    for event in pygame.event.get():
        # при закрытии окна
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()

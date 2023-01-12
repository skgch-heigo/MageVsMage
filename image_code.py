import os
import sys

import pygame


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


def player_image_load():
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
                        [load_image(f"game_sprites/sprites_Frossin/walking_backward/walking_backward{i}.png")
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
                        [load_image(f"game_sprites/sprites_Frossin/run_backward/run_backward{i}.png")
                         for i in range(1, 9)],
                    "run_left":
                        [load_image(f"game_sprites/sprites_Frossin/run_left/run_left{i}.png")
                         for i in range(1, 14)],
                    "run_right":
                        [load_image(f"game_sprites/sprites_Frossin/run_right/run_right{i}.png")
                         for i in range(1, 14)]}
    return player_image


def health_bar_load():
    nums = []
    for i in range(10):
        nums.append(load_image("game_sprites/additional/num" + str(i) + ".png"))
    nums.append(load_image("game_sprites/additional/heart.png"))
    nums.append(load_image("game_sprites/additional/energy.png"))
    nums.append(load_image("game_sprites/additional/line.png"))
    return nums


def ultra_load():
    images = []
    for i in range(1, 3):
        images.append(load_image("game_sprites/arts/fin_ultra" + str(i) + ".png"))
    return images

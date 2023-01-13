import random
import sys
import os

import pygame

import Bullet_code
import image_code
from image_code import player_image_load, load_image, health_bar_load

pygame.init()

size = WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode(size)
pygame.display.set_icon(load_image("game_sprites/icon/icon2.png"))

FPS = 50

skip = 0


def blit_text(surface, text, pos, width, the_font, color=pygame.Color((0, 0, 0))):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = the_font.size(' ')[0]  # The width of a space.
    max_width = width
    x, y = pos
    word_height = 0
    for line in words:
        for word in line:
            if len(word) >= 5 and word.startswith("<") and word.endswith(">"):
                word_surface = the_font.render(word[2:-2], 0, special_symbol[word[1]])
            else:
                word_surface = the_font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width + pos[0]:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def battle_engine(level_back, enemy, player):
    global skip
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pause()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            skip += 100
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if WIDTH - 65 < event.pos[0] <= WIDTH - 5 and 5 < event.pos[1] <= 65:
                pause()
            if WIDTH - 65 < event.pos[0] <= WIDTH - 5 and 70 < event.pos[1] <= 135:
                settings()
                pygame.mixer.music.load("data/music/battle_theme.wav")
                pygame.mixer.music.play(-1)
    if skip <= 0:
        screen.blit(level_back, (0, 0))
        screen.blit(draw_health_bar(max(enemy.life, 0)), (5, 5))
        screen.blit(draw_health_bar(max(player.life, 0)), (5, TOP_F_SPACE + FIELD_HEIGHT + 5))
        energy_bar = draw_health_bar(player.energy, player.energy_need, energy=True)
        screen.blit(energy_bar, (LEFT_F_SPACE + FIELD_WIDTH - energy_bar.get_width() - 5,
                                 TOP_F_SPACE + FIELD_HEIGHT + 5))
        all_sprites.update()
        all_sprites.draw(screen)
        shields.draw(screen)
        information.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
    else:
        skip -= 1


def blit_timed(surface, text, pos, width, the_font, level_back, enemy, player, color=pygame.Color((0, 0, 0)), wait=1):
    time = 0
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = the_font.size(' ')[0]  # The width of a space.
    max_width = width
    x, y = pos
    word_height = 0
    for line in words:
        for word in line:
            if word == "$":
                for _ in range(50):
                    battle_engine(level_back, enemy, player)
            else:
                if len(word) > 5 and word.startswith("<") and word.endswith(">"):
                    word_surface = the_font.render(word[2:-2], 0, special_symbol[word[1]])
                else:
                    word_surface = the_font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width + pos[0]:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                while time % (fps // wait) != 0:
                    time += 1
                    battle_engine(level_back, enemy, player)
                time += 1
                surface.blit(word_surface, (x, y))
                x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height + 2  # Start on new row.
    for _ in range(150):
        battle_engine(level_back, enemy, player)


def draw_health_bar(*health, energy=False):
    if not energy:
        surf = pygame.Surface(((len(str(health[0])) + 1) * 30, 30))
        surf.fill(BACKGROUND_COLOR)
        surf.blit(nums[10], (0, 0))
        for i in range(len(str(health[0]))):
            surf.blit(nums[int(str(health[0])[i])], ((i + 1) * 30, 0))
        return surf
    surf = pygame.Surface(((len(str(health[0])) + len(str(health[1])) + 2) * 30, 30))
    surf.fill(BACKGROUND_COLOR)
    surf.blit(nums[11], (0, 0))
    for i in range(len(str(health[0]))):
        surf.blit(nums[int(str(health[0])[i])], ((i + 1) * 30, 0))
    surf.blit(nums[12], ((len(str(health[0])) + 1) * 30, 0))
    for i in range(len(str(health[1]))):
        surf.blit(nums[int(str(health[1])[i])], ((len(str(health[0])) + i + 2) * 30, 0))
    return surf


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
        self.fazed = False
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
        elif move_type == "bullet":
            self.image = args[0]
            self.x = args[1]
            self.y = args[2]
            self.speed_x = args[3]
            self.speed_y = args[4]
            self.bounce = args[5]
            self.fazed = args[6]
        else:
            self.time = args[0]
        self.args = args


class PauseButton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, information)
        self.image = load_image("game_sprites/additional/pause.png")
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 65
        self.rect.y = 5


class Player(pygame.sprite.Sprite):
    def __init__(self, speed, max_life, energy_need):
        super().__init__(characters, all_sprites)
        self.direction = "forward"
        self.move = "standing"
        self.running = 0
        self.frame = 0
        self.image = player_image[self.move + "_" + self.direction][self.frame]

        self.x = 0
        self.y = 0
        self.speed = speed
        self.max_life = max_life
        self.life = max_life
        self.last_attack = 0
        self.invulnerable = 0
        self.energy_need = energy_need
        self.energy = 0

    def update(self, *args):
        self.last_attack += 1
        if self.running <= 0:
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
        else:
            self.move = "run"
            if self.direction == "right":
                self.rect.x = min(self.rect.x + self.speed * 2, FIELD_WIDTH + LEFT_F_SPACE - self.rect.width)
            elif self.direction == "left":
                self.rect.x = max(self.rect.x - self.speed * 2, LEFT_F_SPACE)
            elif self.direction == "forward":
                self.rect.y = min(self.rect.y + self.speed * 2, FIELD_HEIGHT + TOP_F_SPACE - self.rect.height)
            else:
                self.rect.y = max(self.rect.y - self.speed * 2, TOP_F_SPACE)
        self.frame += 1
        self.image = player_image[self.move + "_" + self.direction][self.frame // 10 %
                                                                    len(player_image[self.move + "_"
                                                                                     + self.direction])]
        if pygame.key.get_pressed()[pygame.K_e]:
            if self.last_attack > 15:
                self.last_attack = 0
                x_speed = 0
                y_speed = 0
                if self.direction == "backward":
                    x_speed = 0
                    y_speed = -10
                elif self.direction == "forward":
                    x_speed = 0
                    y_speed = 10
                elif self.direction == "right":
                    x_speed = 10
                    y_speed = 0
                elif self.direction == "left":
                    x_speed = -10
                    y_speed = 0
                Bullet_code.Bullet((all_sprites, player_bullets), load_image("game_sprites/bullets/player_attack.png"),
                                   self.rect.x, self.rect.y, x_speed, y_speed, 0, True, 10, "player")

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if self.running < -15:
                self.running = 15
        self.invulnerable -= 1
        self.running -= 1

        if self.running <= 0 and self.invulnerable < 0:
            for i in pygame.sprite.spritecollide(self, enemy_bullets, False):
                if not (isinstance(i, Bullet_code.AreaAttack) and i.phase == 0):
                    pygame.mixer.Sound.play(sounds["hit_sound"])
                    self.life = max(self.life - i.damage, 0)
                    self.invulnerable = 15

    def spawn(self, pos_x, pos_y):
        self.rect = self.image.get_rect()
        self.x = pos_x
        self.y = pos_y
        self.rect.x = pos_x
        self.rect.y = pos_y

    def copy(self):
        return Player(self.speed, self.max_life)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, max_life, open_time, image, player):
        super().__init__(characters, all_sprites)
        self.image = image
        self.open_time = open_time
        self.x = 0
        self.y = 0
        self.shield = True
        self.max_life = max_life
        self.life = max_life
        self.player = player

    def update(self, *args):
        if not self.shield:
            for i in pygame.sprite.spritecollide(self, player_bullets, True):
                pygame.mixer.Sound.play(sounds["enemy_hit"])
                self.life = max(self.life - i.damage, 0)
                self.player[0].energy = min(self.player[0].energy + 1, self.player[0].energy_need)

    def spawn(self, pos_x, pos_y):
        self.rect = self.image.get_rect()
        self.x = pos_x
        self.y = pos_y
        self.rect.x = pos_x
        self.rect.y = pos_y

    def copy(self):
        return Enemy(self.max_life, self.open_time, self.image)


class Information(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(all_sprites)
        self.image = image
        self.rect = self.image.get_rect()

        self.x = pos_x
        self.y = pos_y
        self.rect.x = self.x
        self.rect.y = self.y


class Shield(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(all_sprites, shields)
        self.image = image
        self.rect = self.image.get_rect()

        self.x = pos_x
        self.y = pos_y
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        if pygame.sprite.spritecollide(self, player_bullets, True):
            pygame.mixer.Sound.play(sounds["shield_crash"])

    def delete(self):
        for i in self.groups():
            i.remove(self)


def terminate():
    pygame.quit()
    sys.exit()


def ultra_move():
    ultra_group = pygame.sprite.Group()
    ultra = pygame.sprite.Sprite(ultra_group)
    timer = 150
    ultra.image = ultra_images[timer // 10 % len(ultra_images)]
    ultra.rect = ultra.image.get_rect()
    ultra.rect.x = LEFT_F_SPACE
    ultra.rect.y = HEIGHT // 2 - ultra.image.get_height() // 2
    while True:
        ultra.image = ultra_images[timer // 10 % len(ultra_images)]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if 482 < event.pos[0] <= 542 and 354 < event.pos[1] <= 414:
                    pause()
                if WIDTH - 65 < event.pos[0] <= WIDTH - 5 and 70 < event.pos[1] <= 135:
                    settings()
                    pygame.mixer.music.load("data/music/battle_theme.wav")
                    pygame.mixer.music.play(-1)
        ultra_group.draw(screen)
        pygame.display.flip()
        if timer > 0:
            timer -= 1
            clock.tick(FPS)
        else:
            return


def introduction():
    intro_now = 0
    while True:
        if intro_now >= len(introduction_images):
            start_level(0)
        if lang == EN:
            font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN)
        else:
            font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU)
        screen.fill(BACKGROUND_COLOR)
        screen.blit(introduction_images[intro_now],
                    (WIDTH // 2 - introduction_images[intro_now].get_width() // 2, 50))
        blit_text(screen, text_data[lang]["intro" + str(intro_now + 1)],
                  (WIDTH // 2 - 400, 100 if intro_now != 0 else HEIGHT // 2 + 100), 800, font, BATTLE_TEXT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                intro_now += 1
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                intro_now += 1
        pygame.display.flip()
        clock.tick(fps)


def start_screen():
    # code
    pygame.mixer.music.load("data/music/main_theme.wav")
    pygame.mixer.music.play(-1)
    btn = load_image("game_sprites/additional/button.png")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH // 2 - btn.get_width() // 2 < event.pos[0] < WIDTH // 2 + btn.get_width() // 2 and \
                        HEIGHT // 2 < event.pos[1] < HEIGHT // 2 + btn.get_height():
                    introduction()
                if WIDTH // 2 - btn.get_width() // 2 < event.pos[0] < WIDTH // 2 + btn.get_width() // 2 and \
                        HEIGHT // 2 + btn.get_height() + 10 < event.pos[1] < \
                        HEIGHT // 2 + btn.get_height() * 2 + 10:
                    settings()
                if WIDTH // 2 - btn.get_width() // 2 < event.pos[0] < WIDTH // 2 + btn.get_width() // 2 and \
                        HEIGHT // 2 + btn.get_height() * 2 + 20 < event.pos[1] < \
                        HEIGHT // 2 + btn.get_height() * 3 + 20:
                    terminate()
        if lang == EN:
            font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN)
        else:
            font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU)
        screen.fill(BACKGROUND_COLOR)
        screen.blit(btn, (WIDTH // 2 - btn.get_width() // 2, HEIGHT // 2))
        screen.blit(btn, (WIDTH // 2 - btn.get_width() // 2, HEIGHT // 2 + btn.get_height() + 10))
        screen.blit(btn, (WIDTH // 2 - btn.get_width() // 2, HEIGHT // 2 + btn.get_height() * 2 + 20))
        text = font.render(text_data[lang]["start"], False, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 45 - text.get_height() // 2))
        text = font.render(text_data[lang]["settings"], False, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + btn.get_height() * 1.5 +
                           10 - text.get_height() // 2))
        text = font.render(text_data[lang]["exit"], False, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + btn.get_height() * 2 +
                           20 + btn.get_height() // 2 - text.get_height() // 2))
        pygame.display.flip()
        clock.tick(FPS)


def level_draw(level):
    image = pygame.Surface((1024, 768))
    image.fill(BACKGROUND_COLOR)
    field = load_image("game_sprites/background/background_game3.png")
    image.blit(field, (50, 90))
    return image


def enemy_say(what_say, level_back, enemy, player, sett, enemy_do, black_sq, timer, shield, phase):
    hp_text.add(str(enemy.life) + "hp")
    for i in bullets:
        i.kill()
    if not enemy.shield:
        timer = 0
        enemy.shield = True
        shield = Shield(enemy.rect.x + enemy.rect.width // 2 - 35, enemy.rect.y + enemy.rect.height // 2 - 30,
                        load_image("game_sprites/additional/shield.png"))
    enemy_do.clear()
    enemy_do = random.choice(enemy_moves[phase]).copy()

    if lang == EN:
        font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN_MINI)
    else:
        font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU_MINI)

    enemy_do.append(Move("unshield", enemy.open_time))
    enemy_do.append(Move("wait", 250))
    blit_timed(black_sq.image, text_data[lang][what_say], (20, 100), 351, font,
               level_back, enemy, player, BATTLE_TEXT, wait=5)
    black_sq.image.fill(BLACK_SQ_COLOR)
    black_sq.image.blit(sett, (black_sq.image.get_width() - 65, 70))
    return black_sq, enemy_do, timer, shield


def start_level(level):
    global hp_times, hp_text
    phases = [400, 200]
    phase = 0

    hp_times = [50, 100, 200, 300, 400, 500]
    hp_text = set()

    # level start
    pygame.mixer.music.load("data/music/battle_theme.wav")
    pygame.mixer.music.play(-1)
    level_run = True
    level_back = level_draw(level)
    player = Player(*player_stats)
    player.spawn(*START_POINT)
    enemy = Enemy(*enemies[0], [player])
    enemy.spawn(*ENEMY_POINT)
    black_sq = pygame.sprite.Sprite(all_sprites, information)
    black_sq.image = pygame.Surface((471, 768))
    black_sq.image.fill(BLACK_SQ_COLOR)
    black_sq.rect = black_sq.image.get_rect()
    black_sq.rect.x = 553
    sett = load_image("game_sprites/additional/settings.png")
    black_sq.image.blit(sett, (black_sq.image.get_width() - 65, 70))
    timer = 0
    enemy_do = [Move("wait", 250)]
    enemy_do.extend(random.choice(enemy_moves[phase]).copy())
    enemy_do.append(Move("unshield", enemy.open_time))
    enemy_do.append(Move("wait", 250))
    shield = Shield(enemy.rect.x + enemy.rect.width // 2 - 35, enemy.rect.y + enemy.rect.height // 2 - 30,
                    load_image("game_sprites/additional/shield.png"))
    pause_btn = PauseButton()
    save_inf = (player.life, enemy.life, phase, enemy.open_time, player.energy)
    if lang == EN:
        font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN_MINI)
    else:
        font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU_MINI)
    screen.blit(level_back, (0, 0))
    screen.blit(draw_health_bar(enemy.life), (5, 5))
    screen.blit(draw_health_bar(player.life), (5, TOP_F_SPACE + FIELD_HEIGHT + 5))
    all_sprites.draw(screen)
    shields.draw(screen)
    information.draw(screen)
    pygame.display.flip()
    blit_timed(black_sq.image, text_data[lang]["tutorial"], (20, 100), 351, font,
               level_back, enemy, player, BATTLE_TEXT, wait=5)
    black_sq.image.fill(BLACK_SQ_COLOR)
    black_sq.image.blit(sett, (black_sq.image.get_width() - 65, 70))
    text = ""

    while True:
        if text == "sans":
            hp_times.clear()
            hp_text.add("first_damage_enemy")
            pygame.mixer.music.load("data/music/spider.mp3")
            pygame.mixer.music.play(-1)
            enemy.life = 50
            player.life = 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
            if event.type == pygame.KEYDOWN and event.key != pygame.K_s and event.key != pygame.K_a and \
                    event.key != pygame.K_n:
                text = ""
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                text += "s"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                text += "a"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                text += "n"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if player.energy == player.energy_need:
                    player.energy = 0
                    ultra_move()
                    pygame.mixer.Sound.play(sounds["ultra"])
                    if enemy.shield:
                        enemy.life -= 40
                    else:
                        enemy.life -= 80
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if WIDTH - 65 < event.pos[0] <= WIDTH - 5 and 5 < event.pos[1] <= 65:
                    pause()
                if WIDTH - 65 < event.pos[0] <= WIDTH - 5 and 70 < event.pos[1] <= 135:
                    settings()
                    pygame.mixer.music.load("data/music/battle_theme.wav")
                    pygame.mixer.music.play(-1)
        if not level_run:
            return  # level ended
        if not enemy_do:
            save_inf = (player.life, enemy.life, phase, enemy.open_time, player.energy)
            enemy_do = random.choice(enemy_moves[phase]).copy()
            enemy_do.append(Move("unshield", enemy.open_time))
            enemy_do.append(Move("wait", 250))
        if enemy_do[0].type == "wait":
            if timer < enemy_do[0].time:
                timer += 1
            else:
                del enemy_do[0]
                timer = 0
        elif enemy_do[0].type == "area_attack":
            Bullet_code.AreaAttack((all_sprites, bullets, enemy_bullets), *enemy_do[0].args, "enemy")
            del enemy_do[0]
        elif enemy_do[0].type == "bullet":
            Bullet_code.Bullet((all_sprites, bullets, enemy_bullets), *enemy_do[0].args, "enemy")
            del enemy_do[0]
        else:
            if enemy.shield:
                shield.delete()
            enemy.shield = False
            if timer < enemy_do[0].time:
                timer += 1
            else:
                del enemy_do[0]
                timer = 0
                enemy.shield = True
                shield = Shield(enemy.rect.x + enemy.rect.width // 2 - 35, enemy.rect.y + enemy.rect.height // 2 - 30,
                                load_image("game_sprites/additional/shield.png"))
        if enemy.life in phases and phase != phases.index(enemy.life) + 1:
            phase += 1
            enemy.open_time -= 40
        if enemy.life < enemy.max_life and "first_damage_enemy" not in hp_text:
            hp_text.add("first_damage_enemy")
            black_sq, enemy_do, timer, shield = enemy_say("first_damage_enemy", level_back, enemy, player,
                                                          sett, enemy_do, black_sq, timer, shield, phase)
        if player.life < player.max_life and "first_damage" not in hp_text:
            hp_text.add("first_damage")
            black_sq, enemy_do, timer, shield = enemy_say("first_damage", level_back, enemy, player, sett,
                                                          enemy_do, black_sq, timer, shield, phase)
        if hp_times and enemy.life <= max(hp_times):
            saying = str(max(hp_times))
            del hp_times[hp_times.index(max(hp_times))]
            save_inf = (player.life, enemy.life, phase, enemy.open_time, player.energy)
            black_sq, enemy_do, timer, shield = enemy_say(saying + "hp", level_back, enemy, player,
                                                          sett, enemy_do, black_sq, timer, shield, phase)

        if enemy.life <= 0:
            you_won()
        if player.life <= 0:
            you_lost()
            player.life, enemy.life, phase, enemy.open_time, player.energy = save_inf
            enemy_do = [Move("wait", 250)]
            enemy_do.extend(random.choice(enemy_moves[phase]).copy())
            enemy_do.append(Move("unshield", enemy.open_time))
            enemy_do.append(Move("wait", 250))

        screen.blit(level_back, (0, 0))
        screen.blit(draw_health_bar(max(enemy.life, 0)), (5, 5))
        screen.blit(draw_health_bar(max(player.life, 0)), (5, TOP_F_SPACE + FIELD_HEIGHT + 5))
        energy_bar = draw_health_bar(player.energy, player.energy_need, energy=True)
        screen.blit(energy_bar, (LEFT_F_SPACE + FIELD_WIDTH - energy_bar.get_width() - 5,
                                 TOP_F_SPACE + FIELD_HEIGHT + 5))
        all_sprites.update()
        all_sprites.draw(screen)
        shields.draw(screen)
        information.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def you_won():
    pygame.mixer.music.load("data/music/main_theme.wav")
    pygame.mixer.music.play(-1)
    art = load_image("game_sprites/arts/win2.png")
    if lang == EN:
        font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN)
    else:
        font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU)
    while True:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(art, (WIDTH // 2 - art.get_width() // 2, 100))
        blit_text(screen, text_data[lang]["you_won"], (WIDTH // 2 - 400, int(HEIGHT * 0.7)), 800, font, BATTLE_TEXT)
        text1 = pygame.Surface((100, 50))
        text1.fill(BACKGROUND_COLOR)
        blit_text(text1, text_data[lang]["yes"], (0, 0), text1.get_width(), font, BATTLE_TEXT)
        text2 = pygame.Surface((100, 50))
        text2.fill(BACKGROUND_COLOR)
        blit_text(text2, text_data[lang]["no"], (0, 0), text2.get_width(), font, BATTLE_TEXT)
        screen.blit(text1, (WIDTH // 2 - 150, int(HEIGHT * 0.9)))
        screen.blit(text2, (WIDTH // 2 + 50, int(HEIGHT * 0.9)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if WIDTH // 2 - 150 < event.pos[0] <= WIDTH // 2 - 50 and \
                        int(HEIGHT * 0.9) < event.pos[1] <= int(HEIGHT * 0.9) + 50:
                    for i in all_sprites:
                        i.kill()
                    start_screen()
                if WIDTH // 2 + 50 < event.pos[0] <= WIDTH // 2 + 150 and \
                        int(HEIGHT * 0.9) < event.pos[1] <= int(HEIGHT * 0.9) + 50:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def you_lost():
    for i in bullets:
        i.kill()
    pygame.mixer.music.load("data/music/main_theme.wav")
    pygame.mixer.music.play(-1)
    art = load_image("game_sprites/arts/lose2.png")
    if lang == EN:
        font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN)
    else:
        font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU)
    while True:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(art, (WIDTH // 2 - art.get_width() // 2, 100))
        blit_text(screen, text_data[lang]["you_lost"], (WIDTH // 2 - 400, int(HEIGHT * 0.7)), 800, font, BATTLE_TEXT)
        text1 = pygame.Surface((100, 50))
        text1.fill(BACKGROUND_COLOR)
        blit_text(text1, text_data[lang]["yes"], (0, 0), text1.get_width(), font, BATTLE_TEXT)
        text2 = pygame.Surface((100, 50))
        text2.fill(BACKGROUND_COLOR)
        blit_text(text2, text_data[lang]["no"], (0, 0), text2.get_width(), font, BATTLE_TEXT)
        screen.blit(text1, (WIDTH // 2 - 150, int(HEIGHT * 0.9)))
        screen.blit(text2, (WIDTH // 2 + 50, int(HEIGHT * 0.9)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if WIDTH // 2 - 150 < event.pos[0] <= WIDTH // 2 - 50 and \
                        int(HEIGHT * 0.9) < event.pos[1] <= int(HEIGHT * 0.9) + 50:
                    pygame.mixer.music.load("data/music/battle_theme.wav")
                    pygame.mixer.music.play(-1)
                    return
                if WIDTH // 2 + 50 < event.pos[0] <= WIDTH // 2 + 150 and \
                        int(HEIGHT * 0.9) < event.pos[1] <= int(HEIGHT * 0.9) + 50:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def pause():
    # paused game menu
    pygame.mixer.music.load("data/music/main_theme.wav")
    pygame.mixer.music.play(-1)
    screen.blit(load_image("game_sprites/additional/continue.png"), (482, 354))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.load("data/music/battle_theme.wav")
                pygame.mixer.music.play(-1)
                return  # return from pause
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if 482 < event.pos[0] <= 542 and 354 < event.pos[1] <= 414:
                    pygame.mixer.music.load("data/music/battle_theme.wav")
                    pygame.mixer.music.play(-1)
                    return
        pygame.display.flip()
        clock.tick(FPS)


def settings():
    global lang, sound, volume
    pygame.mixer.music.load("data/music/main_theme.wav")
    pygame.mixer.music.play(-1)
    en_image = load_image("game_sprites/additional/en.png")
    not_en_image = load_image("game_sprites/additional/not_en.png")
    ru_image = load_image("game_sprites/additional/ru.png")
    not_ru_image = load_image("game_sprites/additional/not_ru.png")
    exit_image = load_image("game_sprites/additional/exit.png")
    not_loud = load_image("game_sprites/additional/not_loudness.png")
    loud = load_image("game_sprites/additional/loudness.png")
    while True:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(exit_image, (20, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # return from pause
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                if 20 < event.pos[0] <= 20 + exit_image.get_width() and \
                        20 < event.pos[1] <= 20 + exit_image.get_height():
                    return
                if WIDTH // 2 - 100 - en_image.get_width() < event.pos[0] <= WIDTH // 2 - 100 and \
                        HEIGHT // 2 - 200 < event.pos[1] <= HEIGHT // 2 - 200 + en_image.get_height():
                    lang = EN
                if WIDTH // 2 + 100 < event.pos[0] <= WIDTH // 2 + 100 + en_image.get_width() and \
                        HEIGHT // 2 - 200 < event.pos[1] <= HEIGHT // 2 - 200 + en_image.get_height():
                    lang = RU
                for i in range(5):
                    if WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10) < event.pos[0] <= \
                            WIDTH // 2 + loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10) and \
                            HEIGHT // 2 < event.pos[1] <= HEIGHT // 2 + loud.get_height():
                        volume = i
                        pygame.mixer.music.set_volume(volume * 0.2)
                for i in range(5):
                    if WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10) < event.pos[0] <= \
                            WIDTH // 2 + loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10) and \
                            HEIGHT // 2 + 100 < event.pos[1] <= HEIGHT // 2 + 100 + loud.get_height():
                        sound = i
                        for j in sounds:
                            sounds[j].set_volume(sound * 0.25)
        if lang == EN:
            screen.blit(en_image, (WIDTH // 2 - 100 - en_image.get_width(), HEIGHT // 2 - 200))
            screen.blit(not_ru_image, (WIDTH // 2 + 100, HEIGHT // 2 - 200))
        else:
            screen.blit(not_en_image, (WIDTH // 2 - 100 - en_image.get_width(), HEIGHT // 2 - 200))
            screen.blit(ru_image, (WIDTH // 2 + 100, HEIGHT // 2 - 200))
        if lang == EN:
            font = pygame.font.Font('data/fonts/english.ttf', FONT_SIZE_EN)
        else:
            font = pygame.font.Font('data/fonts/russian.ttf', FONT_SIZE_RU)
        text = font.render(text_data[lang]["volume"], False, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - loud.get_width() // 2 - 2 * (loud.get_width() + 10),
                           HEIGHT // 2 - 55))
        text = font.render(text_data[lang]["sound"], False, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - loud.get_width() // 2 - 2 * (loud.get_width() + 10),
                           HEIGHT // 2 + 45))
        for i in range(5):
            if volume == i:
                screen.blit(loud, (WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10),
                                   HEIGHT // 2))
            else:
                screen.blit(not_loud, (WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10),
                                       HEIGHT // 2))
        for i in range(5):
            if sound == i:
                screen.blit(loud, (WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10),
                                   HEIGHT // 2 + 100))
            else:
                screen.blit(not_loud, (WIDTH // 2 - loud.get_width() // 2 + (i - 2) * (loud.get_width() + 10),
                                       HEIGHT // 2 + 100))
        pygame.display.flip()
        clock.tick(FPS)


fps = 50
pygame.display.set_caption("MageVsMage")
# пикселей в секунду


BACKGROUND_COLOR = (61, 61, 61)
TEXT_COLOR = (10, 10, 10)
BLACK_SQ_COLOR = (30, 30, 30)
BATTLE_TEXT = (240, 240, 240)
START_POINT = (260, 500)
ENEMY_POINT = (260, 130)
FIELD_WIDTH = 453
FIELD_HEIGHT = 588
LEFT_F_SPACE = 50
TOP_F_SPACE = 90
FONT_SIZE_EN = 40
FONT_SIZE_RU = 30
FONT_SIZE_EN_MINI = 20
FONT_SIZE_RU_MINI = 15

special_symbol = {"@": (181, 6, 0),  # bloody color
                  "!": (235, 179, 57),  # golden
                  }

text_data = []
with open("data/text/text_en.txt", "r", encoding="utf-8") as f:
    data = f.read().strip().split("###")
    temp = {}
    for i in data:
        temp[i.split(": ")[0].strip()] = i.split(": ")[1].strip()
    text_data.append(temp)
with open("data/text/text_ru.txt", "r", encoding="utf-8") as f:
    data = f.read().strip().split("###")
    temp = {}
    for i in data:
        temp[i.split(": ")[0].strip()] = i.split(": ")[1].strip()
    text_data.append(temp)
EN = 0
RU = 1
volume = 2
sound = 2
lang = EN


introduction_images = [load_image("game_sprites/arts/introduction1.png"), pygame.Surface((0, 0))]

screen.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()
# основной персонаж

# группы спрайтов
all_sprites = pygame.sprite.Group()
information = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
characters = pygame.sprite.Group()
shields = pygame.sprite.Group()

hp_times = [50, 100, 200, 300, 400, 500]
hp_text = set()

sounds = {
    "enemy_hit": pygame.mixer.Sound("data/sounds/enemy_hit.wav"),
    "hit_sound": pygame.mixer.Sound("data/sounds/hit_sound.wav"),
    "shield_crash": pygame.mixer.Sound("data/sounds/shield_crash.wav"),
    "ultra": pygame.mixer.Sound("data/sounds/ultra.wav")}

ultra_images = image_code.ultra_load()

running = True

pygame.mixer.music.set_volume(volume * 0.25)
for i in sounds:
    sounds[i].set_volume(sound * 0.25)

# change if other character was selected

player_image = player_image_load()
nums = health_bar_load()

player_stats = (3, 100, 20)
enemies = [(600, 250, load_image("game_sprites/sprites_Atanim/standing_forward1.png",
                                 colorkey=(255, 255, 255)))]

enemy_moves = [[[Move("wait", 5) if i % 2 == 1 else
                 Move("bullet", load_image("game_sprites/bullets/blood_drop.png"),
                      random.randint(LEFT_F_SPACE, LEFT_F_SPACE + FIELD_WIDTH - 30),
                      -89, 0, random.randint(5, 8), 0, False, 10)
                 for i in range(120)], [Move("wait", 50) if i % 2 == 1 else
                                        Move("area_attack", load_image("game_sprites/area/lazer_prep.png"),
                                             load_image("game_sprites/area/lazer.png"), 0,
                                             HEIGHT if i % 4 == 0 else -180,
                                             0, -8 if i % 4 == 0 else 8, 120, 50, 10)
                                        for i in range(10)]],
               [[Move("wait", 3) if i % 2 == 1 else
                 Move("bullet",
                      load_image("game_sprites/bullets/blood_drop.png"),
                      random.randint(LEFT_F_SPACE,
                                     LEFT_F_SPACE + FIELD_WIDTH - 30),
                      -89, 0, random.randint(7, 10), 0, False, 10)
                 for i in range(170)],
                [Move("wait", 40) if i % 2 == 1 else
                 Move("area_attack",
                      load_image("game_sprites/area/lazer_prep.png"),
                      load_image("game_sprites/area/lazer.png"), 0,
                      HEIGHT if i % 4 == 0 else -180,
                      0, -10 if i % 4 == 0 else 10, 120, 40, 10)
                 for i in range(12)], [Move("wait", 10) if i % 2 == 1 else
                                       Move("bullet",
                                            load_image("game_sprites/bullets/fire_ball.png"),
                                            ENEMY_POINT[0], ENEMY_POINT[1],
                                            random.choice([random.randint(-3, -1), random.randint(1, 3)]),
                                            random.choice([random.randint(-3, -1), random.randint(1, 3)]), 3, True,
                                            10)
                                       for i in range(30)
                                       ] + [Move("wait", 350)]],
               [[Move("wait", 2) if i % 2 == 1 else
                 Move("bullet",
                      load_image("game_sprites/bullets/blood_drop.png"),
                      random.randint(LEFT_F_SPACE,
                                     LEFT_F_SPACE + FIELD_WIDTH - 30),
                      -89, 0, random.randint(9, 12), 0, False, 10)
                 for i in range(200)],
                [Move("wait", 30) if i % 2 == 1 else
                 Move("area_attack",
                      load_image("game_sprites/area/lazer_prep.png"),
                      load_image("game_sprites/area/lazer.png"), 0,
                      HEIGHT if i % 4 == 0 else -180,
                      0, -12 if i % 4 == 0 else 12, 120, 30, 10)
                 for i in range(15)], [Move("wait", 8) if i % 2 == 1 else
                                       Move("bullet",
                                            load_image("game_sprites/bullets/fire_ball.png"),
                                            ENEMY_POINT[0], ENEMY_POINT[1],
                                            random.choice([random.randint(-5, -2), random.randint(2, 5)]),
                                            random.choice([random.randint(-5, -2), random.randint(2, 5)]), 3, True,
                                            10)
                                       for i in range(40)
                                       ] + [Move("wait", 350)]]
               ]

start_screen()

pygame.quit()

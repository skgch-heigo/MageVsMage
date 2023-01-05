import pygame


FIELD_WIDTH = 453
FIELD_HEIGHT = 588
LEFT_F_SPACE = 50
TOP_F_SPACE = 90


class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos_x, pos_y, speed_x, speed_y, bounce, fazed, damage, side):
        super().__init__(*[i for i in groups])
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = pos_x
        self.rect.y = pos_y
        self.fazed = fazed
        self.damage = damage

        self.x = pos_x
        self.y = pos_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.bounce = bounce
        self.side = side

    def update(self, *args):
        if self.fazed:
            if not (LEFT_F_SPACE < self.rect.x + self.speed_x < LEFT_F_SPACE + FIELD_WIDTH - self.rect.width):
                self.bounce -= 1
                self.speed_x *= -1
            if not (TOP_F_SPACE < self.rect.y + self.speed_y < TOP_F_SPACE + FIELD_HEIGHT - self.rect.height):
                self.bounce -= 1
                self.speed_y *= -1
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            if self.bounce < 0:
                self.delete()
        else:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            if not (-self.rect.width < self.rect.x < LEFT_F_SPACE * 2 + FIELD_WIDTH) or \
                    not (-self.rect.height < self.rect.y < 768):
                self.delete()

    def delete(self):
        for i in self.groups():
            i.remove(self)


class AreaAttack(pygame.sprite.Sprite):
    def __init__(self, groups, image, image_final, pos_x, pos_y, speed_x, speed_y, timer, prep_time, damage, side):
        super().__init__(*[i for i in groups])
        self.image = image
        self.image_final = image_final
        self.rect = self.image.get_rect()

        self.x = pos_x
        self.y = pos_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.timer = timer
        self.prep_time = prep_time
        self.time_now = 0
        self.side = side
        self.damage = damage
        self.phase = 0

    def update(self, *args):
        self.time_now += 1
        if self.time_now == self.prep_time:
            self.image = self.image_final
            self.phase = 1
        if self.time_now >= self.timer:
            self.delete()

    def delete(self):
        for i in self.groups():
            i.remove(self)

import pygame


FIELD_WIDTH = 453
FIELD_HEIGHT = 588
LEFT_F_SPACE = 50
TOP_F_SPACE = 90


class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups, image, pos_x, pos_y, speed_x, speed_y, bounce, side):
        super().__init__(*[i for i in groups])
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.x = pos_x
        self.rect.y = pos_y

        self.x = pos_x
        self.y = pos_y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.bounce = bounce
        self.side = side

    def update(self, *args):
       if self.rect.x + self.speed_x

    def delete(self):
        for i in self.groups():
            i.remove(self)


class AreaAttack(pygame.sprite.Sprite):
    def __init__(self, groups, image, image_final, pos_x, pos_y, speed_x, speed_y, timer, prep_time, side):
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

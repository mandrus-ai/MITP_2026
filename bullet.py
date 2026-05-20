import pygame
from pygame.sprite import Sprite
import math
import random


class Bullet(Sprite):
    def __init__(self, ai_settings, screen, Ship):
        super(Bullet, self).__init__()
        self.screen = screen

        # Создаём пулю выше корабля
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width,
                                ai_settings.bullet_height)
        self.rect.centerx = Ship.rect.centerx
        self.rect.top = Ship.rect.top - 25

        self.y = float(self.rect.y)

        self.speed_factor = ai_settings.bullet_speed_factor

        # Радужный эффект
        self.rainbow_offset = random.randint(0, 360)

    def get_rainbow_color(self):
        """Возвращает радужный цвет"""
        r = int((math.sin(self.rainbow_offset + pygame.time.get_ticks() / 200) + 1) * 127.5)
        g = int((math.sin(self.rainbow_offset + pygame.time.get_ticks() / 200 + 2.094) + 1) * 127.5)
        b = int((math.sin(self.rainbow_offset + pygame.time.get_ticks() / 200 + 4.188) + 1) * 127.5)
        return (r, g, b)

    def update(self):
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        """Рисует радужную пулю"""
        rainbow_color = self.get_rainbow_color()

        # Градиентный эффект
        for i in range(self.rect.height):
            t = i / self.rect.height
            r = int(rainbow_color[0] * (1 - t) + 255 * t)
            g = int(rainbow_color[1] * (1 - t) + 0 * t)
            b = int(rainbow_color[2] * (1 - t) + 255 * t)
            pygame.draw.line(self.screen, (r, g, b),
                             (self.rect.x, self.rect.y + i),
                             (self.rect.x + self.rect.width, self.rect.y + i))
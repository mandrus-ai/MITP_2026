import pygame
from pygame.sprite import Sprite
import random
import math


class Alien(Sprite):
    def __init__(self, ai_settings, screen):
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Загрузка изображения пончика
        self.image2 = pygame.image.load('images/donut1.png')
        self.image = pygame.transform.scale(self.image2, (55, 55))
        self.rect = self.image.get_rect()

        # Начальная позиция - сверху за пределами экрана
        self.rect.x = random.randint(50, ai_settings.screen_width - 100)
        self.rect.y = random.randint(-200, -50)

        # Скорость движения
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(2, 5)  # Основное движение ВНИЗ

        # Для небольшого покачивания
        self.wave_offset = random.uniform(0, 2 * math.pi)
        self.wave_speed = random.uniform(0.03, 0.08)

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        # Движение вниз и немного в стороны
        self.x += self.speed_x
        self.y += self.speed_y

        # Небольшое синусоидальное покачивание
        current_time = pygame.time.get_ticks()
        self.x += math.sin(current_time * self.wave_speed + self.wave_offset) * 0.3

        self.rect.x = self.x
        self.rect.y = self.y

        # Если пончик улетел за нижнюю границу - возвращаем наверх
        if self.rect.top > self.ai_settings.screen_height + 100:
            self.rect.x = random.randint(50, self.ai_settings.screen_width - 100)
            self.rect.y = random.randint(-200, -50)
            self.x = float(self.rect.x)
            self.y = float(self.rect.y)
            # Сбрасываем скорость
            self.speed_y = random.uniform(2, 5)
            self.speed_x = random.uniform(-1.5, 1.5)

        # Если улетел за левую или правую границу - возвращаем с другой стороны
        if self.rect.right < -50:
            self.rect.left = self.ai_settings.screen_width + 50
            self.x = float(self.rect.x)
        elif self.rect.left > self.ai_settings.screen_width + 50:
            self.rect.right = -50
            self.x = float(self.rect.x)

    def blitme(self):
        self.screen.blit(self.image, self.rect)
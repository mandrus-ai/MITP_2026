import pygame
from pygame.sprite import Sprite


class ship(Sprite):
    def __init__(self, ai_settings, screen):
        super(ship, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Загрузка корабля
        self.image2 = pygame.image.load('images/unic.png')
        self.image = pygame.transform.scale(self.image2, (150, 150))
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Позиционирование
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom - 30

        self.center1 = float(self.rect.centerx)

        self.moving_right = False
        self.moving_left = False

        # Для неуязвимости после попадания
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 2000  # 2 секунды неуязвимости
        self.blink = False
        self.last_blink_time = 0

    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right - 30:
            self.center1 += self.ai_settings.ship_speed_factor
        elif self.moving_left and self.rect.left > 30:
            self.center1 -= self.ai_settings.ship_speed_factor

        self.rect.centerx = self.center1

        # Обновление неуязвимости
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_start_time > self.invincible_duration:
                self.invincible = False
                self.blink = False

    def hit(self):
        """Обработка попадания в корабль"""
        if not self.invincible:
            self.invincible = True
            self.invincible_start_time = pygame.time.get_ticks()
            return True
        return False

    def blitme(self):
        # Эффект мигания при неуязвимости
        if self.invincible:
            current_time = pygame.time.get_ticks()
            # Мигаем каждые 100 мс
            if current_time - self.last_blink_time > 100:
                self.blink = not self.blink
                self.last_blink_time = current_time
            if self.blink:
                # Рисуем полупрозрачного корабля
                temp_image = self.image.copy()
                temp_image.set_alpha(128)
                self.screen.blit(temp_image, self.rect)
            else:
                self.screen.blit(self.image, self.rect)
        else:
            self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.center1 = self.screen_rect.centerx

    def center_ship(self):
        self.center1 = self.screen_rect.centerx

    def set_skin(self, skin_file):
        """Устанавливает скин корабля"""
        try:
            self.image2 = pygame.image.load(f'images/skins/{skin_file}')
            self.image = pygame.transform.scale(self.image2, (150, 150))
        except:
            try:
                self.image2 = pygame.image.load(f'images/{skin_file}')
                self.image = pygame.transform.scale(self.image2, (150, 150))
            except:
                print(f"Не удалось загрузить скин: {skin_file}")
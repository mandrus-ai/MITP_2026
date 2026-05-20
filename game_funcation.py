import sys
import pygame
from time import sleep
from bullet import Bullet
from alien import Alien
import random
from level_system import get_level_system


def fire_bullet(ai_settings, screen, Ship, bullets):
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, Ship)
        bullets.add(new_bullet)


def create_alien(ai_settings, screen):
    alien = Alien(ai_settings, screen)
    return alien


def update_bullets(ai_settings, screen, stats, sb, Ship, aliens, bullets, client=None):
    bullets.update()

    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        level_system = get_level_system()

        for aliens_hit in collisions.values():
            base_points = 10
            base_coins = 1
            base_xp = 10

            bonuses = level_system.get_level_bonus()
            points = int(base_points * bonuses['points']) * len(aliens_hit)
            coins = int(base_coins * bonuses['coins']) * len(aliens_hit)
            xp = int(base_xp) * len(aliens_hit)

            stats.score += points
            stats.currency += coins  # ДОБАВИТЬ ЭТУ СТРОКУ

            if client and coins > 0:
                client.send_command(f"addcurrency {coins}")

            level_up, old_level, new_level = level_system.add_xp(xp)

            if level_up:
                print(f"ПОЗДРАВЛЯЕМ! Уровень повышен с {old_level} до {new_level}!")

            sb.prep_score()
            print(f"Уничтожен пончик! +{points} очков, +{coins} монет, +{xp} XP")

    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)


def Ship_hit(ai_settings, stats, screen, sb, Ship, aliens, bullets):
    """Обрабатывает столкновение корабля с пончиком"""
    if stats.Ship_left > 0:
        stats.Ship_left -= 1
        print(f" Корабль повреждён! Осталось жизней: {stats.Ship_left}")

        # Очищаем экран
        aliens.empty()
        bullets.empty()

        # НЕ СБРАСЫВАЕМ УРОВЕНЬ! Просто перезапускаем текущий уровень
        # Создаём новых пончиков для ТЕКУЩЕГО уровня
        from level_system import get_level_system
        level_sys = get_level_system()
        level_stats = level_sys.get_level_stats()
        donut_count = level_stats['donut_count']
        donut_speed = level_stats['donut_speed']

        for _ in range(donut_count):
            new_alien = create_alien(ai_settings, screen)
            new_alien.rect.x = random.randint(50, ai_settings.screen_width - 100)
            new_alien.rect.y = random.randint(-200, -50)
            new_alien.x = float(new_alien.rect.x)
            new_alien.y = float(new_alien.rect.y)
            new_alien.speed_y = random.uniform(2, 4) * donut_speed
            new_alien.speed_x = random.uniform(-1.5, 1.5) * (donut_speed * 0.5)
            aliens.add(new_alien)

        Ship.center_ship()
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)
        print(" Игра окончена! ")

def update_aliens(ai_settings, stats, screen, sb, Ship, aliens, bullets):
    # Обновляем позиции всех пончиков
    for alien in aliens:
        alien.update()

    # Проверка столкновения пончиков с кораблём
    collisions = pygame.sprite.spritecollide(Ship, aliens, True)

    if collisions:
        for alien in collisions:
            if Ship.hit():
                stats.Ship_left -= 1
                print(f" Корабль повреждён! Осталось жизней: {stats.Ship_left}")

                if stats.Ship_left <= 0:
                    stats.game_active = False
                    pygame.mouse.set_visible(True)
                    print(" Игра окончена! ")
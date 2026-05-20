import pygame
from pygame.sprite import Group
import sys
import random
import math
from network import GameClient
from setting import settings
from game_stats import GameStats
from ship import ship
import game_funcation as gf
from button import Button
from scoreboard import Scoreboard
from level_system import get_level_system
from shop import ShopWindow, ShopButton

import os

def load_auth_data():
    """Загружает данные авторизации из файла (C++ -> Python)"""
    try:
        with open('auth_data.txt', 'r') as f:
            login = f.readline().strip()
            password = f.readline().strip()
        # Удаляем файл после прочтения
        os.remove('auth_data.txt')
        return login, password
    except:
        return None, None


def draw_rounded_rect(surface, color, rect, radius=20, alpha=None):
    if alpha is not None:
        temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (*color, alpha), temp_surf.get_rect(), border_radius=radius)
        surface.blit(temp_surf, rect)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_glass_panel(surface, rect, radius=25):
    draw_rounded_rect(surface, (255, 255, 255), rect, radius, 30)
    pygame.draw.rect(surface, (255, 105, 180), rect, 2, border_radius=radius)
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(surface, (255, 105, 180), inner_rect, 1, border_radius=radius - 2)


def draw_pink_background(screen, width, height):
    for i in range(height):
        t = i / height
        r = int(255 - 35 * t)
        g = int(200 - 30 * t)
        b = int(220 - 40 * t)
        pygame.draw.line(screen, (r, g, b), (0, i), (width, i))


def draw_glass_input(surface, rect, text, is_active, font):
    bg_color = (255, 255, 255) if not is_active else (255, 220, 240)
    draw_rounded_rect(surface, bg_color, rect, 15, 20 if not is_active else 40)
    pygame.draw.rect(surface, (255, 105, 180), rect, 2, border_radius=15)
    txt_surface = font.render(text, True, (200, 50, 100))
    surface.blit(txt_surface, (rect.x + 15, rect.y + rect.height // 2 - txt_surface.get_height() // 2))


def draw_glass_button(surface, rect, text, is_hover, font):
    if is_hover:
        color = (255, 120, 170)
        glow_rect = rect.inflate(8, 8)
        draw_rounded_rect(surface, (255, 120, 170), glow_rect, 20, 30)
    else:
        color = (255, 80, 140)
    draw_rounded_rect(surface, color, rect, 20)
    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=20)
    txt_surface = font.render(text, True, (255, 255, 255))
    txt_rect = txt_surface.get_rect(center=rect.center)
    surface.blit(txt_surface, txt_rect)


def draw_particle_effect(screen, particles, width, height):
    for particle in particles:
        alpha = int(255 * (1 - particle['life']))
        if alpha > 0:
            color = (255, 105, 180)
            temp_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, alpha), (particle['size'], particle['size']), particle['size'])
            screen.blit(temp_surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 0.01
        if particle['life'] <= 0 or particle['x'] < 0 or particle['x'] > width or particle['y'] < 0 or particle[
            'y'] > height:
            particle['x'] = random.randint(0, width)
            particle['y'] = random.randint(0, height)
            particle['vx'] = random.uniform(-0.5, 0.5)
            particle['vy'] = random.uniform(-0.5, 0.5)
            particle['life'] = 1.0
            particle['size'] = random.randint(2, 5)


class PauseMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.resume_button = pygame.Rect(width // 2 - 100, height // 2 - 20, 200, 50)
        self.restart_button = pygame.Rect(width // 2 - 100, height // 2 + 50, 200, 50)
        self.exit_button = pygame.Rect(width // 2 - 100, height // 2 + 120, 200, 50)

    def draw(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(self.width // 2 - 200, self.height // 2 - 150, 400, 300)
        draw_rounded_rect(self.screen, (255, 255, 255), panel_rect, 20)
        pygame.draw.rect(self.screen, (255, 105, 180), panel_rect, 3, border_radius=20)
        title = self.font_title.render("Пауза", True, (255, 105, 180))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.screen.blit(title, title_rect)
        pygame.draw.rect(self.screen, (255, 80, 140), self.resume_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 80, 140), self.restart_button, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), self.exit_button, border_radius=10)
        resume_text = self.font.render("Продолжить", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=self.resume_button.center)
        self.screen.blit(resume_text, resume_rect)
        restart_text = self.font.render("Перезапустить", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_rect)
        exit_text = self.font.render("Выйти из игры", True, (0, 0, 0))
        exit_rect = exit_text.get_rect(center=self.exit_button.center)
        self.screen.blit(exit_text, exit_rect)
        pygame.display.flip()

    def handle_click(self, pos):
        if self.resume_button.collidepoint(pos):
            return "resume"
        elif self.restart_button.collidepoint(pos):
            return "restart"
        elif self.exit_button.collidepoint(pos):
            return "exit"
        return None


class ProfileWindow:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 56)
        self.font_header = pygame.font.Font(None, 36)
        self.font_text = pygame.font.Font(None, 24)
        self.font_button = pygame.font.Font(None, 32)
        self.font_ach = pygame.font.Font(None, 20)
        self.visible = False

        self.player_name = ""
        self.player_level = 1
        self.player_score = 0
        self.player_highscore = 0
        self.player_currency = 0
        self.player_xp = 0
        self.player_xp_next = 100
        self.player_title = ""

        self.back_button = pygame.Rect(width // 2 - 100, height // 2 + 260, 200, 45)
        self.prev_button = pygame.Rect(width // 2 - 300, height // 2 + 260, 100, 40)
        self.next_button = pygame.Rect(width // 2 + 200, height // 2 + 260, 100, 40)

        self.stats_button = pygame.Rect(width // 2 - 160, height // 2 - 200, 140, 40)
        self.achievements_button = pygame.Rect(width // 2 + 20, height // 2 - 200, 140, 40)

        self.active_tab = "stats"
        self.ach_page = 0
        self.ach_per_page = 8

        self.achievements = self.generate_achievements()

    def generate_achievements(self):
        achievements = []

        kill_achievements = [
            (1, "Первый шаг", "Уничтожьте первого пончика"),
            (5, "Новичок", "Уничтожьте 5 пончиков"),
            (10, "Любитель пончиков", "Уничтожьте 10 пончиков"),
            (25, "Начинающий охотник", "Уничтожьте 25 пончиков"),
            (50, "Опытный охотник", "Уничтожьте 50 пончиков"),
            (100, "Мастер-охотник", "Уничтожьте 100 пончиков"),
            (250, "Легендарный охотник", "Уничтожьте 250 пончиков"),
            (500, "Истребитель", "Уничтожьте 500 пончиков"),
            (1000, "Пожиратель пончиков", "Уничтожьте 1000 пончиков"),
            (2500, "Бог войны", "Уничтожьте 2500 пончиков"),
        ]

        level_achievements = [
            (2, "Новичок 2 уровня", "Достигните 2 уровня"),
            (3, "Начинающий", "Достигните 3 уровня"),
            (4, "Любитель", "Достигните 4 уровня"),
            (5, "Опытный", "Достигните 5 уровня"),
            (6, "Продвинутый", "Достигните 6 уровня"),
            (7, "Мастер", "Достигните 7 уровня"),
            (8, "Эксперт", "Достигните 8 уровня"),
            (9, "Профессионал", "Достигните 9 уровня"),
            (10, "Виртуоз", "Достигните 10 уровня"),
            (15, "Легенда", "Достигните 15 уровня"),
            (20, "Миф", "Достигните 20 уровня"),
        ]

        score_achievements = [
            (100, "Сто очков", "Наберите 100 очков"),
            (500, "Пятьсот очков", "Наберите 500 очков"),
            (1000, "Тысяча очков", "Наберите 1000 очков"),
            (5000, "Пять тысяч", "Наберите 5000 очков"),
            (10000, "Десять тысяч", "Наберите 10000 очков"),
            (25000, "Двадцать пять тысяч", "Наберите 25000 очков"),
            (50000, "Пятьдесят тысяч", "Наберите 50000 очков"),
            (100000, "Сто тысяч", "Наберите 100000 очков"),
        ]

        currency_achievements = [
            (10, "Первые монеты", "Соберите 10 монет"),
            (50, "Коллекционер", "Соберите 50 монет"),
            (100, "Нумизмат", "Соберите 100 монет"),
            (500, "Богач", "Соберите 500 монет"),
            (1000, "Миллионер", "Соберите 1000 монет"),
            (5000, "Магнат", "Соберите 5000 монет"),
            (10000, "Олигарх", "Соберите 10000 монет"),
        ]

        combo_achievements = [
            (1, "Быстрый старт", "Уничтожьте 3 пончика за 5 секунд"),
            (3, "В яблочко", "Уничтожьте 5 пончиков подряд"),
            (5, "Неудержимый", "Уничтожьте 10 пончиков подряд"),
        ]

        perfect_achievements = [
            (1, "Безупречный", "Пройдите уровень без потери жизней"),
            (3, "Идеальная серия", "Пройдите 3 уровня без потери жизней"),
            (5, "Непобедимый", "Пройдите 5 уровней без потери жизней"),
        ]

        special_achievements = [
            (1, "Снайпер", "Уничтожьте пончика с первого выстрела"),
            (10, "Меткий стрелок", "Попадите 10 раз подряд"),
            (1, "Спринтер", "Уничтожьте пончика за 1 секунду"),
            (1, "Живучий", "Выживите с 1 жизнью"),
            (1, "Идеальный игрок", "Наберите 100 точности за уровень"),
            (1, "Праздник", "Уничтожьте 50 пончиков за один уровень"),
            (1, "Сверхзвуковой", "Уничтожьте пончика на максимальной скорости"),
            (1, "Эстет", "Соберите 5 разных типов пончиков"),
            (1, "Везунчик", "Найдите редкого пончика"),
            (1, "Бриллиантовый", "Наберите 50000 очков без потери жизни"),
        ]

        idx = 1

        for count, name, desc in kill_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": count,
                "category": "kills",
                "icon": "D"
            })
            idx += 1

        for level, name, desc in level_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": level,
                "category": "level",
                "icon": "L"
            })
            idx += 1

        for score, name, desc in score_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": score,
                "category": "score",
                "icon": "S"
            })
            idx += 1

        for currency, name, desc in currency_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": currency,
                "category": "currency",
                "icon": "C"
            })
            idx += 1

        for combo, name, desc in combo_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": combo,
                "category": "combo",
                "icon": "!"
            })
            idx += 1

        for perfect, name, desc in perfect_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": perfect,
                "category": "perfect",
                "icon": "*"
            })
            idx += 1

        for special, name, desc in special_achievements:
            achievements.append({
                "id": idx,
                "name": name,
                "desc": desc,
                "unlocked": False,
                "progress": 0,
                "max_progress": special,
                "category": "special",
                "icon": "T"
            })
            idx += 1

        while len(achievements) < 100:
            achievements.append({
                "id": len(achievements) + 1,
                "name": f"Секретное #{len(achievements) + 1}",
                "desc": "Секретное достижение",
                "unlocked": False,
                "progress": 0,
                "max_progress": 1,
                "category": "secret",
                "icon": "?"
            })
            idx += 1

        return achievements

    def update_achievements(self, kills, level, score, currency):
        for ach in self.achievements:
            if ach["unlocked"]:
                continue

            if ach["category"] == "kills":
                ach["progress"] = kills
                if kills >= ach["max_progress"]:
                    ach["unlocked"] = True
                    print(f"Достижение разблокировано: {ach['name']}!")

            elif ach["category"] == "level":
                ach["progress"] = level
                if level >= ach["max_progress"]:
                    ach["unlocked"] = True
                    print(f"Достижение разблокировано: {ach['name']}!")

            elif ach["category"] == "score":
                ach["progress"] = score
                if score >= ach["max_progress"]:
                    ach["unlocked"] = True
                    print(f"Достижение разблокировано: {ach['name']}!")

            elif ach["category"] == "currency":
                ach["progress"] = currency
                if currency >= ach["max_progress"]:
                    ach["unlocked"] = True
                    print(f"Достижение разблокировано: {ach['name']}!")

    def update_data(self, name, level, score, highscore, currency, xp, xp_next, title, kills=0):
        self.player_name = name
        self.player_level = level
        self.player_score = score
        self.player_highscore = highscore
        self.player_currency = currency
        self.player_xp = xp
        self.player_xp_next = xp_next if xp_next > 0 else 100
        self.player_title = title

        self.update_achievements(kills, level, score, currency)

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(self.width // 2 - 400, self.height // 2 - 280, 800, 560)
        draw_rounded_rect(self.screen, (255, 255, 255), panel_rect, 25)
        pygame.draw.rect(self.screen, (255, 105, 180), panel_rect, 3, border_radius=25)

        title = self.font_title.render("Профиль игрока", True, (255, 105, 180))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 230))
        self.screen.blit(title, title_rect)

        pygame.draw.line(self.screen, (255, 105, 180),
                         (self.width // 2 - 350, self.height // 2 - 180),
                         (self.width // 2 + 350, self.height // 2 - 180), 2)

        stats_color = (255, 120, 170) if self.active_tab == "stats" else (200, 100, 140)
        ach_color = (255, 120, 170) if self.active_tab == "achievements" else (200, 100, 140)

        draw_rounded_rect(self.screen, stats_color, self.stats_button, 10)
        stats_btn_text = self.font_text.render("Статистика", True, (255, 255, 255))
        stats_btn_rect_center = stats_btn_text.get_rect(center=self.stats_button.center)
        self.screen.blit(stats_btn_text, stats_btn_rect_center)

        draw_rounded_rect(self.screen, ach_color, self.achievements_button, 10)
        ach_btn_text = self.font_text.render("Достижения", True, (255, 255, 255))
        ach_btn_rect_center = ach_btn_text.get_rect(center=self.achievements_button.center)
        self.screen.blit(ach_btn_text, ach_btn_rect_center)

        if self.active_tab == "stats":
            info_x = self.width // 2 - 300
            info_y = self.height // 2 - 140

            name_text = self.font_header.render(f"{self.player_name}", True, (100, 50, 80))
            self.screen.blit(name_text, (info_x, info_y))

            title_text = self.font_text.render(f"{self.player_title}", True, (150, 80, 120))
            self.screen.blit(title_text, (info_x, info_y + 45))

            level_text = self.font_text.render(f"Уровень: {self.player_level}", True, (150, 80, 120))
            self.screen.blit(level_text, (info_x, info_y + 90))

            progress_width = 300
            progress_height = 15
            progress_rect = pygame.Rect(info_x + 150, info_y + 88, progress_width, progress_height)
            fill_width = int((self.player_xp / self.player_xp_next) * progress_width) if self.player_xp_next > 0 else 0

            pygame.draw.rect(self.screen, (240, 200, 220), progress_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 105, 180),
                             (progress_rect.x, progress_rect.y, fill_width, progress_height), border_radius=8)
            pygame.draw.rect(self.screen, (255, 105, 180), progress_rect, 2, border_radius=8)

            xp_text = self.font_text.render(f"XP: {self.player_xp}/{self.player_xp_next}", True, (100, 50, 80))
            self.screen.blit(xp_text, (info_x + 150 + progress_width + 15, info_y + 85))

            score_text = self.font_text.render(f"Счёт: {self.player_score}", True, (150, 80, 120))
            self.screen.blit(score_text, (info_x, info_y + 135))

            highscore_text = self.font_text.render(f"Рекорд: {self.player_highscore}", True, (150, 80, 120))
            self.screen.blit(highscore_text, (info_x, info_y + 175))

            currency_text = self.font_text.render(f"Монет: {self.player_currency}", True, (255, 150, 100))
            self.screen.blit(currency_text, (info_x, info_y + 215))

            unlocked_count = sum(1 for ach in self.achievements if ach["unlocked"])
            total_count = len(self.achievements)
            ach_progress_text = self.font_text.render(f"Достижений: {unlocked_count}/{total_count}", True,
                                                      (100, 50, 80))
            self.screen.blit(ach_progress_text, (info_x, info_y + 260))

            ach_progress_width = 300
            ach_fill_width = int((unlocked_count / total_count) * ach_progress_width)
            ach_progress_rect = pygame.Rect(info_x + 180, info_y + 258, ach_progress_width, 15)
            pygame.draw.rect(self.screen, (240, 200, 220), ach_progress_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 200, 100),
                             (ach_progress_rect.x, ach_progress_rect.y, ach_fill_width, 15), border_radius=8)
            pygame.draw.rect(self.screen, (255, 105, 180), ach_progress_rect, 2, border_radius=8)

        elif self.active_tab == "achievements":
            header_y = self.height // 2 - 160
            header_text = self.font_header.render("Список достижений", True, (255, 105, 180))
            header_rect = header_text.get_rect(center=(self.width // 2, header_y))
            self.screen.blit(header_text, header_rect)

            total_pages = (len(self.achievements) + self.ach_per_page - 1) // self.ach_per_page
            page_text = self.font_text.render(f"Страница {self.ach_page + 1} из {total_pages}", True, (150, 80, 120))
            page_rect = page_text.get_rect(center=(self.width // 2, header_y + 35))
            self.screen.blit(page_text, page_rect)

            start_idx = self.ach_page * self.ach_per_page
            end_idx = min(start_idx + self.ach_per_page, len(self.achievements))

            ach_y = self.height // 2 - 110
            for i, ach in enumerate(self.achievements[start_idx:end_idx]):
                if ach["unlocked"]:
                    color = (100, 150, 80)
                    status = "[V]"
                    bg_color = (220, 255, 220)
                else:
                    color = (180, 150, 170)
                    status = "[X]"
                    bg_color = (250, 245, 250)

                ach_rect = pygame.Rect(self.width // 2 - 350, ach_y + i * 34, 700, 32)
                draw_rounded_rect(self.screen, bg_color, ach_rect, 6)

                icon_text = self.font_ach.render(f"{status} {ach['icon']}", True, color)
                self.screen.blit(icon_text, (ach_rect.x + 10, ach_rect.y + 6))

                name_text = self.font_ach.render(f"{ach['name']}", True, color)
                self.screen.blit(name_text, (ach_rect.x + 65, ach_rect.y + 6))

                desc_text = self.font_ach.render(f"{ach['desc']}", True, (120, 100, 140))
                self.screen.blit(desc_text, (ach_rect.x + 240, ach_rect.y + 6))

                if ach["progress"] > 0 and not ach["unlocked"]:
                    prog_text = self.font_ach.render(f"({ach['progress']}/{ach['max_progress']})", True,
                                                     (150, 120, 170))
                    self.screen.blit(prog_text, (ach_rect.x + 600, ach_rect.y + 6))

            mouse_pos = pygame.mouse.get_pos()

            if self.ach_page > 0:
                prev_color = (255, 120, 170) if self.prev_button.collidepoint(mouse_pos) else (255, 80, 140)
                draw_rounded_rect(self.screen, prev_color, self.prev_button, 10)
                prev_text = self.font_text.render("Назад", True, (255, 255, 255))
                prev_rect = prev_text.get_rect(center=self.prev_button.center)
                self.screen.blit(prev_text, prev_rect)

            if self.ach_page < total_pages - 1:
                next_color = (255, 120, 170) if self.next_button.collidepoint(mouse_pos) else (255, 80, 140)
                draw_rounded_rect(self.screen, next_color, self.next_button, 10)
                next_text = self.font_text.render("Вперёд", True, (255, 255, 255))
                next_rect = next_text.get_rect(center=self.next_button.center)
                self.screen.blit(next_text, next_rect)

        mouse_pos = pygame.mouse.get_pos()
        back_color = (255, 120, 170) if self.back_button.collidepoint(mouse_pos) else (255, 80, 140)
        draw_rounded_rect(self.screen, back_color, self.back_button, 10)
        back_text = self.font_button.render("Вернуться в игру", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.active_tab == "achievements":
            if self.prev_button.collidepoint(pos) and self.ach_page > 0:
                self.ach_page -= 1
                return "refresh"
            elif self.next_button.collidepoint(pos):
                total_pages = (len(self.achievements) + self.ach_per_page - 1) // self.ach_per_page
                if self.ach_page < total_pages - 1:
                    self.ach_page += 1
                    return "refresh"

        if self.stats_button.collidepoint(pos):
            self.active_tab = "stats"
            return "refresh"
        elif self.achievements_button.collidepoint(pos):
            self.active_tab = "achievements"
            self.ach_page = 0
            return "refresh"
        elif self.back_button.collidepoint(pos):
            self.visible = False
            return "back"
        return None

class ProfileButton:
    def __init__(self, screen, x, y, width=80, height=40):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 24)
        self.is_hover = False

    def draw(self):
        color = (255, 120, 170) if self.is_hover else (255, 80, 140)
        draw_rounded_rect(self.screen, color, self.rect, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2, border_radius=10)
        text = self.font.render("PRO", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return "profile"
        return None

class AnimatedButton:
    def __init__(self, screen, x, y, width, height, text, font, normal_color, hover_color, text_color):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hover = False
        self.click_animation = 0
        self.pulse = 0
        self.pulse_direction = 1

    def update(self):
        self.pulse += 0.05 * self.pulse_direction
        if self.pulse >= 1:
            self.pulse = 1
            self.pulse_direction = -1
        elif self.pulse <= 0:
            self.pulse = 0
            self.pulse_direction = 1

        if self.click_animation > 0:
            self.click_animation -= 0.2

    def draw(self):
        current_color = self.hover_color if self.is_hover else self.normal_color

        if self.is_hover:
            pulse_scale = 1 + self.pulse * 0.05
            animated_rect = pygame.Rect(
                self.rect.centerx - self.rect.width * pulse_scale // 2,
                self.rect.centery - self.rect.height * pulse_scale // 2,
                self.rect.width * pulse_scale,
                self.rect.height * pulse_scale
            )
        else:
            animated_rect = self.rect

        draw_rounded_rect(self.screen, current_color, animated_rect, 15)
        pygame.draw.rect(self.screen, (255, 255, 255), animated_rect, 3, border_radius=15)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=animated_rect.center)
        self.screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.click_animation = 1
                return True
        return False


def run_game():
    pygame.init()
    ai_settings = settings()

    ACCENT_PINK = (255, 105, 180)
    ERROR_RED = (255, 80, 80)

    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Единобожик")

    fullscreen = False
    pygame.mouse.set_visible(True)

    game_background = None
    try:
        game_background = pygame.image.load('images/fone.png')
        game_background = pygame.transform.scale(game_background, (ai_settings.screen_width, ai_settings.screen_height))
    except:
        try:
            game_background = pygame.image.load('images/fone.jpg')
            game_background = pygame.transform.scale(game_background,
                                                     (ai_settings.screen_width, ai_settings.screen_height))
        except:
            pass

    donut_left = None
    donut_right = None
    try:
        donut_left = pygame.image.load('images/donut1.png')
        donut_left = pygame.transform.scale(donut_left, (45, 45))
        donut_right = pygame.image.load('images/donut1.png')
        donut_right = pygame.transform.scale(donut_right, (45, 45))
    except:
        pass

    client = GameClient()
    if not client.connect():
        print("Не удалось подключиться к серверу. Выход.")
        return

    auth_window = pygame.Rect(ai_settings.screen_width // 2 - 400, ai_settings.screen_height // 2 - 320, 800, 640)

    font_title = pygame.font.Font(None, 72)
    font_subtitle = pygame.font.Font(None, 32)
    font_welcome = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 28)
    font_input = pygame.font.Font(None, 32)

    input_box = pygame.Rect(auth_window.x + 180, auth_window.y + 220, 450, 65)
    password_box = pygame.Rect(auth_window.x + 180, auth_window.y + 320, 450, 65)
    login_button = pygame.Rect(auth_window.x + 200, auth_window.y + 460, 170, 60)
    register_button = pygame.Rect(auth_window.x + 430, auth_window.y + 460, 170, 60)

    active = 'login'
    login_text = ''
    password_text = ''
    error_msg = ''
    waiting_response = False
    authenticated = False
    user_role = ''
    user_score = 0
    user_currency = 0
    user_skin = 0
    user_background = 100

    login_hover = False
    register_hover = False
    time = 0
    pulse = 0

    clock = pygame.time.Clock()

    particles = []
    for i in range(100):
        particles.append({
            'x': random.randint(0, ai_settings.screen_width),
            'y': random.randint(0, ai_settings.screen_height),
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-0.5, 0.5),
            'size': random.randint(2, 6),
            'life': random.uniform(0.5, 1.0)
        })

    # АВТОРИЗАЦИЯ
    while not authenticated:
        current_page = "login"
        reg_login_text = ''
        reg_password_text = ''
        reg_confirm_text = ''
        reg_error_msg = ''
        reg_success_msg = ''
        reg_waiting_response = False

        cursor_visible = True
        cursor_timer = 0
        cursor_interval = 500
        show_password = False
        show_reg_password = False
        show_reg_confirm = False

        reg_input_box = pygame.Rect(auth_window.x + 180, auth_window.y + 200, 450, 55)
        reg_password_box = pygame.Rect(auth_window.x + 180, auth_window.y + 280, 450, 55)
        reg_confirm_box = pygame.Rect(auth_window.x + 180, auth_window.y + 360, 450, 55)

        reg_register_button = pygame.Rect(auth_window.x + 150, auth_window.y + 450, 240, 50)
        reg_back_button = pygame.Rect(auth_window.x + 430, auth_window.y + 450, 170, 50)

        eye_button = pygame.Rect(password_box.x + password_box.width + 10, password_box.y + 10, 36, 36)
        reg_eye_button = pygame.Rect(reg_password_box.x + reg_password_box.width + 10, reg_password_box.y + 10, 36, 36)
        reg_eye_confirm_button = pygame.Rect(reg_confirm_box.x + reg_confirm_box.width + 10, reg_confirm_box.y + 10, 36,
                                             36)

        font_eye = pygame.font.Font(None, 28)
        font_rainbow = pygame.font.Font(None, 28)

        rainbow_offset = 0

        def get_rainbow_color(offset):
            r = int((math.sin(offset) + 1) * 127.5)
            g = int((math.sin(offset + 2.094) + 1) * 127.5)
            b = int((math.sin(offset + 4.188) + 1) * 127.5)
            return (r, g, b)

        def draw_rainbow_text(surface, text, rect, font, offset):
            text_surf = font.render(text, True, (255, 105, 180))
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

        while not authenticated:
            current_time = pygame.time.get_ticks()
            rainbow_offset += 0.05

            if current_time - cursor_timer > cursor_interval:
                cursor_visible = not cursor_visible
                cursor_timer = current_time

            mouse_pos = pygame.mouse.get_pos()
            time += 0.02
            pulse = 0.5 + 0.3 * math.sin(time)

            login_hover = login_button.collidepoint(mouse_pos) if current_page == "login" else False
            register_hover = register_button.collidepoint(mouse_pos) if current_page == "login" else False
            reg_register_hover = reg_register_button.collidepoint(mouse_pos) if current_page == "register" else False
            reg_back_hover = reg_back_button.collidepoint(mouse_pos) if current_page == "register" else False
            eye_hover = eye_button.collidepoint(mouse_pos) if current_page == "login" else False
            reg_eye_hover = reg_eye_button.collidepoint(mouse_pos) if current_page == "register" else False
            reg_eye_confirm_hover = reg_eye_confirm_button.collidepoint(
                mouse_pos) if current_page == "register" else False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if current_page == "login":
                        if input_box.collidepoint(event.pos):
                            active = 'login'
                        elif password_box.collidepoint(event.pos):
                            active = 'password'
                        elif eye_button.collidepoint(event.pos):
                            show_password = not show_password
                        elif login_button.collidepoint(event.pos):
                            if login_text and password_text:
                                waiting_response = True
                                response = client.send_command(f"login {login_text} {password_text}")
                                waiting_response = False
                                if response and response.startswith("Login successful"):
                                    parts = response.split('|')
                                    if len(parts) == 5:
                                        user_role = parts[1]
                                        user_score = int(parts[2])
                                        user_currency = int(parts[3])
                                        user_skin = int(parts[4])
                                    authenticated = True
                                else:
                                    error_msg = "Ошибка входа. Проверьте логин и пароль."
                            else:
                                error_msg = "Введите логин и пароль"
                        elif register_button.collidepoint(event.pos):
                            current_page = "register"
                            reg_login_text = ''
                            reg_password_text = ''
                            reg_confirm_text = ''
                            reg_error_msg = ''
                            reg_success_msg = ''
                            active = 'reg_login'
                        else:
                            active = None

                    elif current_page == "register":
                        if reg_input_box.collidepoint(event.pos):
                            active = 'reg_login'
                        elif reg_password_box.collidepoint(event.pos):
                            active = 'reg_password'
                        elif reg_confirm_box.collidepoint(event.pos):
                            active = 'reg_confirm'
                        elif reg_eye_button.collidepoint(event.pos):
                            show_reg_password = not show_reg_password
                        elif reg_eye_confirm_button.collidepoint(event.pos):
                            show_reg_confirm = not show_reg_confirm
                        elif reg_register_button.collidepoint(event.pos):
                            if reg_login_text and reg_password_text and reg_confirm_text:
                                if reg_password_text != reg_confirm_text:
                                    reg_error_msg = "Пароли не совпадают!"
                                elif len(reg_password_text) < 3:
                                    reg_error_msg = "Пароль должен быть не менее 3 символов!"
                                elif len(reg_login_text) < 3:
                                    reg_error_msg = "Логин должен быть не менее 3 символов!"
                                else:
                                    reg_waiting_response = True
                                    response = client.send_command(f"register {reg_login_text} {reg_password_text}")
                                    reg_waiting_response = False
                                    if response and "successful" in response:
                                        reg_success_msg = "Регистрация успешна!"
                                        reg_error_msg = ""
                                        pygame.time.wait(2000)
                                        current_page = "login"
                                        login_text = reg_login_text
                                        password_text = reg_password_text
                                    else:
                                        reg_error_msg = response if response else "Ошибка регистрации. Пользователь уже существует."
                            else:
                                reg_error_msg = "Заполните все поля!"
                        elif reg_back_button.collidepoint(event.pos):
                            current_page = "login"
                            reg_error_msg = ''
                            reg_success_msg = ''
                        else:
                            active = None

                if event.type == pygame.KEYDOWN:
                    if current_page == "login":
                        if active == 'login':
                            if event.key == pygame.K_RETURN:
                                active = 'password'
                            elif event.key == pygame.K_BACKSPACE:
                                login_text = login_text[:-1]
                            else:
                                login_text += event.unicode
                        elif active == 'password':
                            if event.key == pygame.K_RETURN:
                                if login_text and password_text:
                                    waiting_response = True
                                    response = client.send_command(f"login {login_text} {password_text}")
                                    waiting_response = False
                                    if response and response.startswith("Login successful"):
                                        parts = response.split('|')
                                        if len(parts) == 5:
                                            user_role = parts[1]
                                            user_score = int(parts[2])
                                            user_currency = int(parts[3])
                                            user_skin = int(parts[4])
                                        authenticated = True
                                    else:
                                        error_msg = "Ошибка входа. Проверьте логин и пароль."
                            elif event.key == pygame.K_BACKSPACE:
                                password_text = password_text[:-1]
                            else:
                                password_text += event.unicode

                    elif current_page == "register":
                        if active == 'reg_login':
                            if event.key == pygame.K_RETURN:
                                active = 'reg_password'
                            elif event.key == pygame.K_BACKSPACE:
                                reg_login_text = reg_login_text[:-1]
                            else:
                                reg_login_text += event.unicode
                        elif active == 'reg_password':
                            if event.key == pygame.K_RETURN:
                                active = 'reg_confirm'
                            elif event.key == pygame.K_BACKSPACE:
                                reg_password_text = reg_password_text[:-1]
                            else:
                                reg_password_text += event.unicode
                        elif active == 'reg_confirm':
                            if event.key == pygame.K_RETURN:
                                if reg_login_text and reg_password_text and reg_confirm_text:
                                    if reg_password_text != reg_confirm_text:
                                        reg_error_msg = "Пароли не совпадают!"
                                    else:
                                        reg_waiting_response = True
                                        response = client.send_command(f"register {reg_login_text} {reg_password_text}")
                                        reg_waiting_response = False
                                        if response and "successful" in response:
                                            reg_success_msg = "Регистрация успешна!"
                                            reg_error_msg = ""
                                            pygame.time.wait(2000)
                                            current_page = "login"
                                            login_text = reg_login_text
                                            password_text = reg_password_text
                                        else:
                                            reg_error_msg = response if response else "Ошибка регистрации"
                            elif event.key == pygame.K_BACKSPACE:
                                reg_confirm_text = reg_confirm_text[:-1]
                            else:
                                reg_confirm_text += event.unicode

            # ОТРИСОВКА
            draw_pink_background(screen, ai_settings.screen_width, ai_settings.screen_height)
            for i in range(0, ai_settings.screen_width, 50):
                pygame.draw.line(screen, (255, 200, 220, 30), (i, 0), (i, ai_settings.screen_height), 1)
            for i in range(0, ai_settings.screen_height, 50):
                pygame.draw.line(screen, (255, 200, 220, 30), (0, i), (ai_settings.screen_width, i), 1)
            draw_particle_effect(screen, particles, ai_settings.screen_width, ai_settings.screen_height)
            draw_glass_panel(screen, auth_window, 30)

            title_y = auth_window.y + 60
            if donut_left:
                screen.blit(donut_left, (ai_settings.screen_width // 2 - 200, title_y - 5))
            title = font_title.render("Единобожик", True, ACCENT_PINK)
            title_rect = title.get_rect(center=(ai_settings.screen_width // 2, title_y))
            screen.blit(title, title_rect)
            if donut_right:
                screen.blit(donut_right, (ai_settings.screen_width // 2 + 155, title_y - 5))

            if current_page == "login":
                welcome_text = "Добро пожаловать!"
                welcome_surf = font_welcome.render(welcome_text, True, (200, 100, 150))
                welcome_rect = welcome_surf.get_rect(center=(ai_settings.screen_width // 2, auth_window.y + 130))
                screen.blit(welcome_surf, welcome_rect)

                login_label = font_medium.render("Логин:", True, ACCENT_PINK)
                screen.blit(login_label, (input_box.x - 85, input_box.y + 15))

                password_label = font_medium.render("Пароль:", True, ACCENT_PINK)
                screen.blit(password_label, (password_box.x - 95, password_box.y + 15))

                draw_glass_input(screen, input_box, login_text, active == 'login', font_input)
                if active == 'login' and cursor_visible:
                    text_width = font_input.size(login_text)[0]
                    cursor_x = input_box.x + 15 + text_width
                    cursor_y = input_box.y + 12
                    pygame.draw.line(screen, (200, 50, 100), (cursor_x, cursor_y), (cursor_x, cursor_y + 35), 2)

                display_text = password_text if show_password else '*' * len(password_text)
                draw_glass_input(screen, password_box, display_text, active == 'password', font_input)
                if active == 'password' and cursor_visible:
                    text_width = font_input.size(display_text)[0]
                    cursor_x = password_box.x + 15 + text_width
                    cursor_y = password_box.y + 12
                    pygame.draw.line(screen, (200, 50, 100), (cursor_x, cursor_y), (cursor_x, cursor_y + 35), 2)

                eye_icon = "O" if show_password else "*"
                eye_radius = 20 if eye_hover else 18
                eye_color = (255, 120, 170) if eye_hover else ACCENT_PINK
                pygame.draw.circle(screen, (255, 240, 245), eye_button.center, eye_radius)
                pygame.draw.circle(screen, eye_color, eye_button.center, eye_radius, 2)
                eye_surf = font_eye.render(eye_icon, True, eye_color)
                eye_rect = eye_surf.get_rect(center=eye_button.center)
                screen.blit(eye_surf, eye_rect)

                draw_glass_button(screen, login_button, "Вход", login_hover, font_medium)
                draw_glass_button(screen, register_button, "Регистрация", register_hover, font_medium)

                if error_msg:
                    err_surf = font_small.render(error_msg, True, ERROR_RED)
                    err_rect = err_surf.get_rect(center=(ai_settings.screen_width // 2, auth_window.y + 560))
                    screen.blit(err_surf, err_rect)

            elif current_page == "register":
                reg_title = font_subtitle.render("Создание аккаунта", True, ACCENT_PINK)
                reg_title_rect = reg_title.get_rect(center=(ai_settings.screen_width // 2, auth_window.y + 120))
                screen.blit(reg_title, reg_title_rect)

                reg_login_label = font_medium.render("Логин:", True, ACCENT_PINK)
                screen.blit(reg_login_label, (reg_input_box.x - 85, reg_input_box.y + 12))
                draw_glass_input(screen, reg_input_box, reg_login_text, active == 'reg_login', font_input)
                if active == 'reg_login' and cursor_visible:
                    text_width = font_input.size(reg_login_text)[0]
                    cursor_x = reg_input_box.x + 15 + text_width
                    cursor_y = reg_input_box.y + 10
                    pygame.draw.line(screen, (200, 50, 100), (cursor_x, cursor_y), (cursor_x, cursor_y + 35), 2)

                reg_pass_label = font_medium.render("Пароль:", True, ACCENT_PINK)
                screen.blit(reg_pass_label, (reg_password_box.x - 95, reg_password_box.y + 12))
                reg_display_text = reg_password_text if show_reg_password else '*' * len(reg_password_text)
                draw_glass_input(screen, reg_password_box, reg_display_text, active == 'reg_password', font_input)
                if active == 'reg_password' and cursor_visible:
                    text_width = font_input.size(reg_display_text)[0]
                    cursor_x = reg_password_box.x + 15 + text_width
                    cursor_y = reg_password_box.y + 10
                    pygame.draw.line(screen, (200, 50, 100), (cursor_x, cursor_y), (cursor_x, cursor_y + 35), 2)

                reg_eye_radius = 20 if reg_eye_hover else 18
                reg_eye_color = (255, 120, 170) if reg_eye_hover else ACCENT_PINK
                pygame.draw.circle(screen, (255, 240, 245), reg_eye_button.center, reg_eye_radius)
                pygame.draw.circle(screen, reg_eye_color, reg_eye_button.center, reg_eye_radius, 2)
                reg_eye_surf = font_eye.render("O" if show_reg_password else "*", True, reg_eye_color)
                reg_eye_rect = reg_eye_surf.get_rect(center=reg_eye_button.center)
                screen.blit(reg_eye_surf, reg_eye_rect)

                reg_confirm_label = font_medium.render("Подтвердите:", True, ACCENT_PINK)
                screen.blit(reg_confirm_label, (reg_confirm_box.x - 130, reg_confirm_box.y + 12))
                reg_confirm_display = reg_confirm_text if show_reg_confirm else '*' * len(reg_confirm_text)
                draw_glass_input(screen, reg_confirm_box, reg_confirm_display, active == 'reg_confirm', font_input)
                if active == 'reg_confirm' and cursor_visible:
                    text_width = font_input.size(reg_confirm_display)[0]
                    cursor_x = reg_confirm_box.x + 15 + text_width
                    cursor_y = reg_confirm_box.y + 10
                    pygame.draw.line(screen, (200, 50, 100), (cursor_x, cursor_y), (cursor_x, cursor_y + 35), 2)

                reg_eye_confirm_radius = 20 if reg_eye_confirm_hover else 18
                reg_eye_confirm_color = (255, 120, 170) if reg_eye_confirm_hover else ACCENT_PINK
                pygame.draw.circle(screen, (255, 240, 245), reg_eye_confirm_button.center, reg_eye_confirm_radius)
                pygame.draw.circle(screen, reg_eye_confirm_color, reg_eye_confirm_button.center, reg_eye_confirm_radius,
                                   2)
                reg_eye_confirm_surf = font_eye.render("O" if show_reg_confirm else "*", True, reg_eye_confirm_color)
                reg_eye_confirm_rect = reg_eye_confirm_surf.get_rect(center=reg_eye_confirm_button.center)
                screen.blit(reg_eye_confirm_surf, reg_eye_confirm_rect)

                draw_glass_button(screen, reg_register_button, "РЕГИСТРАЦИЯ", reg_register_hover, font_medium)
                draw_glass_button(screen, reg_back_button, "НАЗАД", reg_back_hover, font_medium)

                if reg_error_msg:
                    err_surf = font_small.render(reg_error_msg, True, ERROR_RED)
                    err_rect = err_surf.get_rect(center=(ai_settings.screen_width // 2, auth_window.y + 540))
                    screen.blit(err_surf, err_rect)

                if reg_success_msg:
                    success_rect = pygame.Rect(ai_settings.screen_width // 2 - 150, auth_window.y + 540, 300, 30)
                    draw_rainbow_text(screen, reg_success_msg, success_rect, font_small, rainbow_offset)

            if waiting_response or reg_waiting_response:
                wait_surf = font_small.render("Подключение к серверу...", True, ACCENT_PINK)
                wait_rect = wait_surf.get_rect(center=(ai_settings.screen_width // 2, auth_window.y + 600))
                screen.blit(wait_surf, wait_rect)

            pygame.display.flip()
            clock.tick(60)

    print(f"Вошли как: {login_text}")

    def restart_game():
        nonlocal current_game_level, game_paused, stats, aliens, bullets, level_sys, spawn_timer, spawn_delay
        aliens.empty()
        bullets.empty()

        stats.game_active = True
        game_paused = False
        stats.Ship_left = ai_settings.Ship_limit

        level_stats = level_sys.get_level_stats()
        donut_count = level_stats['donut_count']
        donut_speed = level_stats['donut_speed']
        spawn_delay = int(level_stats['spawn_delay'] * 1000)

        for _ in range(donut_count):
            new_alien = gf.create_alien(ai_settings, screen)
            new_alien.rect.x = random.randint(50, ai_settings.screen_width - 100)
            new_alien.rect.y = random.randint(-200, -50)
            new_alien.x = float(new_alien.rect.x)
            new_alien.y = float(new_alien.rect.y)
            new_alien.speed_y = random.uniform(2, 4) * donut_speed
            new_alien.speed_x = random.uniform(-1.5, 1.5) * (donut_speed * 0.5)
            aliens.add(new_alien)

        Ship.center_ship()
        spawn_timer = pygame.time.get_ticks()
        print(f"Уровень {current_game_level} перезапущен!")

    Ship = ship(ai_settings, screen)
    bullets = Group()
    aliens = Group()

    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    play_button = AnimatedButton(
        screen,
        ai_settings.screen_width // 2 - 100,
        ai_settings.screen_height // 2 + 100,
        200, 60,
        "START",
        pygame.font.Font(None, 36),
        (255, 80, 140),
        (255, 120, 170),
        (255, 255, 255)
    )

    restart_button = AnimatedButton(
        screen,
        ai_settings.screen_width // 2 + 120,
        ai_settings.screen_height // 2 + 100,
        160, 60,
        "RESTART",
        pygame.font.Font(None, 28),
        (200, 80, 120),
        (220, 100, 140),
        (255, 255, 255)
    )

    profile_btn = ProfileButton(screen, ai_settings.screen_width - 100, 20, 80, 40)

    shop_btn = ShopButton(screen, ai_settings.screen_width - 180, 20, 60, 40, draw_rounded_rect)

    shop_window = ShopWindow(screen, ai_settings.screen_width, ai_settings.screen_height, client, draw_rounded_rect)
    shop_window.on_currency_change = lambda new_currency: globals().update(
        {'user_currency': new_currency}) or stats.__setattr__('currency', new_currency)
    shop_window.update_currency(user_currency)
    shop_window.set_current_skin(user_skin)

    stats.score = user_score
    stats.game_active = False

    level_sys = get_level_system()
    level_sys.reset()

    current_game_level = 1
    max_game_level = 10

    spawn_timer = 0
    spawn_delay = 2500
    max_donuts_on_screen = 12

    info_font = pygame.font.Font(None, 28)
    xp_font = pygame.font.Font(None, 24)

    profile_window = ProfileWindow(screen, ai_settings.screen_width, ai_settings.screen_height)

    def create_stats_surface():
        return info_font.render(f"{login_text} | {user_role} | Счёт: {stats.score} | Монет: {user_currency}", True,
                                (200, 50, 100))

    def create_level_surface():
        return info_font.render(f"Уровень: {current_game_level}", True, (200, 50, 100))

    def create_xp_surface():
        xp_current, xp_needed = level_sys.get_current_level_xp()
        progress = level_sys.get_progress_percentage()
        title = level_sys.get_level_title()
        return xp_font.render(f"{title} | Ур.{level_sys.current_level} | XP: {xp_current}/{xp_needed} ({progress}%)",
                              True, (200, 50, 100))

    # Функция для обновления отображения статистики
    def refresh_stats_display():
        """Обновляет отображение статистики на экране"""
        nonlocal stats_surface, stats_bg, stats_rect, level_surface, level_bg, level_rect, xp_surface, xp_bg, xp_rect

        stats_surface = create_stats_surface()
        stats_bg = pygame.Rect(10, 10, stats_surface.get_width() + 20, stats_surface.get_height() + 10)
        stats_rect = stats_surface.get_rect(topleft=(20, 20))

        level_surface = create_level_surface()
        level_bg = pygame.Rect(10, 55, level_surface.get_width() + 20, level_surface.get_height() + 10)
        level_rect = level_surface.get_rect(topleft=(20, 65))

        xp_surface = create_xp_surface()
        xp_bg = pygame.Rect(10, 90, xp_surface.get_width() + 20, xp_surface.get_height() + 10)
        xp_rect = xp_surface.get_rect(topleft=(20, 100))

    # Создаем начальные поверхности
    stats_surface = create_stats_surface()
    stats_rect = stats_surface.get_rect(topleft=(20, 20))
    stats_bg = pygame.Rect(10, 10, stats_surface.get_width() + 20, stats_surface.get_height() + 10)

    level_surface = create_level_surface()
    level_rect = level_surface.get_rect(topleft=(20, 65))
    level_bg = pygame.Rect(10, 55, level_surface.get_width() + 20, level_surface.get_height() + 10)

    xp_surface = create_xp_surface()
    xp_rect = xp_surface.get_rect(topleft=(20, 100))
    xp_bg = pygame.Rect(10, 90, xp_surface.get_width() + 20, xp_surface.get_height() + 10)

    pause_menu = PauseMenu(screen, ai_settings.screen_width, ai_settings.screen_height)
    game_paused = False

    def spawn_new_donut():
        if len(aliens) < max_donuts_on_screen:
            new_alien = gf.create_alien(ai_settings, screen)

            level_stats = level_sys.get_level_stats()
            donut_speed = level_stats['donut_speed']

            new_alien.rect.x = random.randint(50, ai_settings.screen_width - 100)
            new_alien.rect.y = random.randint(-200, -50)
            new_alien.speed_y = random.uniform(2, 5) * donut_speed
            new_alien.speed_x = random.uniform(-1.5, 1.5) * (donut_speed * 0.5)

            new_alien.x = float(new_alien.rect.x)
            new_alien.y = float(new_alien.rect.y)
            aliens.add(new_alien)

    def start_level(level):
        nonlocal aliens, bullets, spawn_timer, spawn_delay, user_skin, user_background

        aliens.empty()
        bullets.empty()

        # Загружаем данные пользователя из глобальных переменных
        stats.currency = user_currency
        stats.score = user_score

        level_stats = level_sys.get_level_stats()
        donut_count = level_stats['donut_count']
        donut_speed = level_stats['donut_speed']
        spawn_delay = int(level_stats['spawn_delay'] * 1000)

        print(f"=== УРОВЕНЬ {level} ===")
        print(f"Пончиков на уровне: {donut_count}")
        print(f"Скорость пончиков: {donut_speed}")
        print(f"Задержка спавна: {level_stats['spawn_delay']} сек")
        print(f"Множитель наград: x{level_stats['bonus_multiplier']}")

        for _ in range(donut_count):
            new_alien = gf.create_alien(ai_settings, screen)
            new_alien.rect.x = random.randint(50, ai_settings.screen_width - 100)
            new_alien.rect.y = random.randint(-200, -50)
            new_alien.x = float(new_alien.rect.x)
            new_alien.y = float(new_alien.rect.y)
            new_alien.speed_y = random.uniform(2, 4) * donut_speed
            new_alien.speed_x = random.uniform(-1.5, 1.5) * (donut_speed * 0.5)
            aliens.add(new_alien)

        spawn_timer = pygame.time.get_ticks()
        Ship.center_ship()
        stats.game_active = True

    # ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height),
                                                         pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
                elif event.key == pygame.K_ESCAPE:
                    if profile_window.visible:
                        profile_window.visible = False
                    elif shop_window.visible:
                        shop_window.visible = False
                    elif stats.game_active and not game_paused:
                        game_paused = not game_paused
                    else:
                        pygame.quit()
                        sys.exit()
                elif stats.game_active and not game_paused:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        Ship.moving_right = True
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        Ship.moving_left = True
                    elif event.key == pygame.K_SPACE:
                        gf.fire_bullet(ai_settings, screen, Ship, bullets)

            if event.type == pygame.KEYUP:
                if stats.game_active and not game_paused:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        Ship.moving_right = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        Ship.moving_left = False

            if profile_window.visible:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = profile_window.handle_click(event.pos)
                    if action == "back":
                        profile_window.visible = False
                    elif action == "refresh":
                        xp_current, xp_needed = level_sys.get_current_level_xp()
                        profile_window.update_data(login_text, level_sys.current_level, stats.score, stats.high_score,
                                                   user_currency, xp_current, xp_needed, level_sys.get_level_title())
                        profile_window.draw()
                continue

            action = profile_btn.handle_event(event)
            if action == "profile" and not game_paused and not shop_window.visible:
                kills = stats.score // 10
                xp_current, xp_needed = level_sys.get_current_level_xp()
                profile_window.update_data(login_text, level_sys.current_level, stats.score, stats.high_score,
                                           user_currency, xp_current, xp_needed, level_sys.get_level_title(), kills)
                profile_window.visible = True
                if game_background:
                    screen.blit(game_background, (0, 0))
                else:
                    screen.fill((255, 255, 255))
                profile_window.draw()
                continue

            action = shop_btn.handle_event(event)
            if action == "shop" and not game_paused and not profile_window.visible:   # <-- ДОБАВЛЕНА ПРОВЕРКА
                shop_window.update_currency(user_currency)
                shop_window.visible = True
                if game_background:
                    screen.blit(game_background, (0, 0))
                else:
                    screen.fill((255, 255, 255))
                shop_window.draw()
                continue

            if shop_window.visible:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = shop_window.handle_click(event.pos)
                    if action == "back":
                        shop_window.visible = False
                    elif action == "refresh":
                        shop_window.draw()
                continue

            if game_paused and event.type == pygame.MOUSEBUTTONDOWN:
                action = pause_menu.handle_click(event.pos)
                if action == "resume":
                    game_paused = False
                elif action == "restart":
                    game_paused = False
                    restart_game()
                elif action == "exit":
                    pygame.quit()
                    sys.exit()

            if not stats.game_active and not game_paused:
                if play_button.handle_event(event):
                    current_game_level = 1
                    level_sys.reset()
                    start_level(current_game_level)
                    stats.score = user_score
                    stats.Ship_left = ai_settings.Ship_limit

                if restart_button.handle_event(event):
                    current_game_level = 1
                    level_sys.reset()
                    start_level(current_game_level)
                    stats.score = user_score
                    stats.Ship_left = ai_settings.Ship_limit

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_game_level = 1
                    level_sys.reset()
                    start_level(current_game_level)
                    stats.score = user_score
                    stats.Ship_left = ai_settings.Ship_limit

        # ОТРИСОВКА
        if not profile_window.visible and not shop_window.visible:
            if game_background:
                screen.blit(game_background, (0, 0))
            else:
                screen.fill((255, 255, 255))

            if not game_paused:
                for bullet in bullets.sprites():
                    bullet.draw_bullet()
                Ship.blitme()
                aliens.draw(screen)
                sb.show_score()

            if not stats.game_active and not game_paused:
                play_button.update()
                play_button.draw()
                restart_button.update()
                restart_button.draw()

            pygame.draw.rect(screen, (255, 240, 245), stats_bg, border_radius=12)
            pygame.draw.rect(screen, (255, 105, 180), stats_bg, 2, border_radius=12)
            screen.blit(stats_surface, stats_rect)

            level_surface = create_level_surface()
            level_bg.width = level_surface.get_width() + 20
            pygame.draw.rect(screen, (255, 240, 245), level_bg, border_radius=12)
            pygame.draw.rect(screen, (255, 105, 180), level_bg, 2, border_radius=12)
            screen.blit(level_surface, level_rect)

            xp_surface = create_xp_surface()
            xp_bg.width = xp_surface.get_width() + 20
            pygame.draw.rect(screen, (255, 240, 245), xp_bg, border_radius=12)
            pygame.draw.rect(screen, (255, 105, 180), xp_bg, 2, border_radius=12)
            screen.blit(xp_surface, xp_rect)

            profile_btn.draw()
            shop_btn.draw()

        # Отрисовка магазина поверх всего
        if shop_window.visible:
            shop_window.draw()

        if game_paused and not profile_window.visible:
            pause_menu.draw()

        pygame.display.flip()

        # ИГРОВАЯ ЛОГИКА
        if not profile_window.visible and stats.game_active and not game_paused:
            Ship.update()
            gf.update_bullets(ai_settings, screen, stats, sb, Ship, aliens, bullets, client)
            gf.update_aliens(ai_settings, stats, screen, sb, Ship, aliens, bullets)

            if current_time - spawn_timer > spawn_delay:
                spawn_new_donut()
                if current_game_level > 7:
                    spawn_delay = 2000
                elif current_game_level > 4:
                    spawn_delay = 2200
                else:
                    spawn_delay = 2500
                spawn_timer = current_time

            if level_sys.current_level > current_game_level:
                current_game_level = min(level_sys.current_level, max_game_level)
                print(f"Достигнут {current_game_level} уровень!")

            if stats.score != user_score:
                user_score = stats.score
                client.send_command(f"score {user_score}")
                refresh_stats_display()  # ВЫЗЫВАЕМ ОБНОВЛЕНИЕ

            if stats.currency != user_currency:
                user_currency = stats.currency
                shop_window.update_currency(user_currency)
                refresh_stats_display()

            # Проверяем, не сменился ли скин в магазине
            if shop_window.current_skin != user_skin:
                user_skin = shop_window.current_skin
                for skin in shop_window.skins:
                    if skin["id"] == user_skin:
                        Ship.set_skin(skin["file"])
                        print(f"Скин изменён на: {skin['name']}")
                        break

            # Проверяем, не сменился ли скин в магазине
            if shop_window.current_skin != user_skin:
                user_skin = shop_window.current_skin
                for skin in shop_window.skins:
                    if skin["id"] == user_skin:
                        Ship.set_skin(skin["file"])
                        print(f"Скин изменён на: {skin['name']}")
                        break

            # Проверяем, не сменился ли фон в магазине
            if hasattr(shop_window, 'current_background') and shop_window.current_background != user_background:
                user_background = shop_window.current_background
                try:
                    game_background = pygame.image.load(f'images/{shop_window.current_background_file}')
                    game_background = pygame.transform.scale(game_background, (ai_settings.screen_width, ai_settings.screen_height))
                    print(f"Фон изменён на: {shop_window.current_background_file}")
                except Exception as e:
                    print(f"Ошибка загрузки фона: {e}")

        clock.tick(60)


if __name__ == "__main__":
    run_game()
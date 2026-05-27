import pygame
from settings import settings


class AchievementSystem:
    def __init__(self, client, user_id):
        self.client = client
        self.user_id = user_id
        self.notifications = []
        self.achievements = {
            1: {"name": "Первый пончик", "target": 1, "progress": 0, "done": False},
            2: {"name": "Карамельный новичок", "target": 10, "progress": 0, "done": False},
            3: {"name": "Сладкий охотник", "target": 25, "progress": 0, "done": False},
            4: {"name": "Глазурный защитник", "target": 50, "progress": 0, "done": False},
            5: {"name": "Пончикоборец", "target": 100, "progress": 0, "done": False},
            6: {"name": "Маршмеллоу-воин", "target": 250, "progress": 0, "done": False},
            7: {"name": "Легенда сладостей", "target": 500, "progress": 0, "done": False},

            8: {"name": "Первые очки", "target": 100, "progress": 0, "done": False},
            9: {"name": "Сахарная тысяча", "target": 1000, "progress": 0, "done": False},
            10: {"name": "Клубничный рекорд", "target": 2500, "progress": 0, "done": False},
            11: {"name": "Золотой результат", "target": 5000, "progress": 0, "done": False},
            12: {"name": "Большой рекорд", "target": 10000, "progress": 0, "done": False},

            13: {"name": "Второй уровень", "target": 2, "progress": 0, "done": False},
            14: {"name": "Ванильный путь", "target": 5, "progress": 0, "done": False},
            15: {"name": "Карамельный герой", "target": 10, "progress": 0, "done": False},
            16: {"name": "Сливочный мастер", "target": 15, "progress": 0, "done": False},
            17: {"name": "Единобожик-профи", "target": 25, "progress": 0, "done": False},

            18: {"name": "Первые монеты", "target": 10, "progress": 0, "done": False},
            19: {"name": "Сладкий кошелёк", "target": 100, "progress": 0, "done": False},
            20: {"name": "Карамельная казна", "target": 500, "progress": 0, "done": False},
            21: {"name": "Золотой запас", "target": 1000, "progress": 0, "done": False},
            22: {"name": "Богатый единорог", "target": 2500, "progress": 0, "done": False},

            23: {"name": "Первый выстрел", "target": 1, "progress": 0, "done": False},
            24: {"name": "Меткий стрелок", "target": 50, "progress": 0, "done": False},
            25: {"name": "Сахарная очередь", "target": 100, "progress": 0, "done": False},
            26: {"name": "Глазурный снайпер", "target": 250, "progress": 0, "done": False},
            27: {"name": "Пулемёт с джемом", "target": 500, "progress": 0, "done": False},

            28: {"name": "Первая покупка", "target": 1, "progress": 0, "done": False},
            29: {"name": "Новый образ", "target": 1, "progress": 0, "done": False},
            30: {"name": "Новый фон", "target": 1, "progress": 0, "done": False},

            31: {"name": "Без промаха", "target": 1, "progress": 0, "done": False},
            32: {"name": "Три пончика подряд", "target": 3, "progress": 0, "done": False},
            33: {"name": "Комбо из пяти", "target": 5, "progress": 0, "done": False},
            34: {"name": "Десять подряд", "target": 10, "progress": 0, "done": False},

            35: {"name": "Выживший", "target": 1, "progress": 0, "done": False},
            36: {"name": "Долгая игра", "target": 300, "progress": 0, "done": False},
            37: {"name": "Упорный игрок", "target": 600, "progress": 0, "done": False},

            38: {"name": "Первый рекорд дня", "target": 1, "progress": 0, "done": False},
            39: {"name": "Почти чемпион", "target": 7500, "progress": 0, "done": False},
            40: {"name": "Чемпион Единобожика", "target": 15000, "progress": 0, "done": False},
        }
        self.load_from_server()

    def load_from_server(self):
        if not self.client:
            return False
        response = self.client.send_command(f"get_achievements&{self.user_id}")
        if not response:
            return False
        response = response.replace("\x01", "").strip()
        if not response.startswith("achievements"):
            return False
        parts = response.split("|")[1:]
        for item in parts:
            try:
                ach_id, unlocked, progress = item.split(":")
                ach_id = int(ach_id)
                if ach_id in self.achievements:
                    self.achievements[ach_id]["progress"] = int(progress)
                    self.achievements[ach_id]["done"] = int(unlocked) == 1
            except Exception:
                continue
        return True

    def save_to_server(self, ach_id):
        if not self.client or ach_id not in self.achievements:
            return False
        ach = self.achievements[ach_id]
        response = self.client.send_command(
            f"update_achievement&{self.user_id}&{ach_id}&{ach['progress']}&{1 if ach['done'] else 0}"
        )
        return response is not None and "success" in response

    def update_progress(self, ach_id, value):
        if ach_id not in self.achievements:
            return
        ach = self.achievements[ach_id]
        if ach["done"]:
            return
        old_progress = ach["progress"]
        ach["progress"] = max(old_progress, value)
        if ach["progress"] >= ach["target"]:
            ach["done"] = True
            ach["progress"] = ach["target"]
            self.notifications.append({"text": f"Открыто достижение: {ach['name']}", "time": pygame.time.get_ticks()})
        if ach["progress"] != old_progress or ach["done"]:
            self.save_to_server(ach_id)

    def draw_notifications(self, screen, font):
        current = pygame.time.get_ticks()
        start_x = screen.get_width() - 430
        start_y = 100
        for i, notif in enumerate(self.notifications[:]):
            elapsed = current - notif["time"]
            if elapsed > 4000:
                self.notifications.remove(notif)
                continue
            if elapsed < 450:
                offset = int(430 * (1 - elapsed / 450))
            else:
                offset = 0
            card = pygame.Rect(start_x + offset, start_y + i * 86, 395, 72)
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(card.x + 5, card.y + 6, card.w, card.h), border_radius=18)
            pygame.draw.rect(screen, settings.UI_PANEL, card, border_radius=18)
            pygame.draw.rect(screen, settings.UI_SUCCESS, card, 2, border_radius=18)
            badge = pygame.Rect(card.x + 18, card.y + 18, 38, 38)
            pygame.draw.rect(screen, settings.UI_SUCCESS, badge, border_radius=12)
            mark = font.render("OK", True, settings.UI_TEXT)
            screen.blit(mark, mark.get_rect(center=badge.center))
            title = font.render("ДОСТИЖЕНИЕ", True, settings.UI_SUCCESS)
            name = font.render(notif["text"].replace("Открыто достижение: ", ""), True, settings.UI_TEXT)
            screen.blit(title, (card.x + 72, card.y + 13))
            screen.blit(name, (card.x + 72, card.y + 39))


class AchievementWindow:
    def __init__(self, screen, achievement_system, font_title, font_medium, font_small):
        self.screen = screen
        self.system = achievement_system
        self.font_title = font_title
        self.font_medium = font_medium
        self.font_small = font_small
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = -740
        self.window_rect = pygame.Rect(150, 55, 900, 590)
        self.close_rect = pygame.Rect(self.window_rect.right - 58, self.window_rect.y + 22, 36, 36)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return True
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset += event.y * 42
            self.scroll_offset = min(0, self.scroll_offset)
            self.scroll_offset = max(self.max_scroll, self.scroll_offset)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.hide()
                return True
        return True

    def _draw_text(self, text, font, color, x, y):
        surf = font.render(str(text), True, color)
        self.screen.blit(surf, (x, y))
        return surf.get_rect(topleft=(x, y))

    def draw(self):
        if not self.visible:
            return
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        shadow = pygame.Surface((self.window_rect.w, self.window_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=26)
        self.screen.blit(shadow, (self.window_rect.x + 8, self.window_rect.y + 10))
        pygame.draw.rect(self.screen, settings.UI_PANEL, self.window_rect, border_radius=26)
        pygame.draw.rect(self.screen, settings.UI_BORDER, self.window_rect, 2, border_radius=26)

        title = self.font_title.render("ДОСТИЖЕНИЯ", True, settings.UI_TEXT)
        self.screen.blit(title, (self.window_rect.x + 30, self.window_rect.y + 22))

        completed = sum(1 for ach in self.system.achievements.values() if ach["done"])
        total = len(self.system.achievements)
        info = self.font_medium.render(f"Открыто: {completed}/{total}", True, settings.UI_TEXT_DARK)
        self.screen.blit(info, (self.window_rect.x + 36, self.window_rect.y + 82))

        pygame.draw.rect(self.screen, settings.UI_DANGER, self.close_rect, border_radius=12)
        close = self.font_medium.render("X", True, settings.UI_TEXT)
        self.screen.blit(close, close.get_rect(center=self.close_rect.center))

        clip = self.screen.get_clip()
        content_rect = pygame.Rect(self.window_rect.x + 28, self.window_rect.y + 120, self.window_rect.w - 56, self.window_rect.h - 150)
        self.screen.set_clip(content_rect)

        y = content_rect.y + self.scroll_offset
        for ach_id, ach in self.system.achievements.items():
            card = pygame.Rect(content_rect.x, y, content_rect.w, 86)
            if card.bottom >= content_rect.y and card.y <= content_rect.bottom:
                pygame.draw.rect(self.screen, settings.UI_CARD_HOVER if ach["done"] else settings.UI_CARD, card, border_radius=16)
                pygame.draw.rect(self.screen, settings.UI_SUCCESS if ach["done"] else settings.UI_BORDER, card, 2, border_radius=16)

                badge = pygame.Rect(card.x + 18, card.y + 20, 46, 46)
                pygame.draw.rect(self.screen, settings.UI_SUCCESS if ach["done"] else settings.DARK_GRAY, badge, border_radius=14)
                badge_text = self.font_small.render("OK" if ach["done"] else str(ach_id), True, settings.UI_TEXT)
                self.screen.blit(badge_text, badge_text.get_rect(center=badge.center))

                self._draw_text(ach["name"], self.font_medium, settings.UI_TEXT, card.x + 82, card.y + 16)
                progress_text = f"{ach['progress']}/{ach['target']}"
                self._draw_text(progress_text, self.font_small, settings.UI_TEXT_DARK, card.right - 120, card.y + 20)

                percent = 1 if ach["target"] <= 0 else min(1, ach["progress"] / ach["target"])
                bar = pygame.Rect(card.x + 82, card.y + 56, card.w - 190, 10)
                fill = pygame.Rect(bar.x, bar.y, int(bar.w * percent), bar.h)
                pygame.draw.rect(self.screen, (55, 65, 88), bar, border_radius=8)
                pygame.draw.rect(self.screen, settings.UI_SUCCESS if ach["done"] else settings.UI_ACCENT, fill, border_radius=8)
            y += 98

        self.screen.set_clip(clip)

        track = pygame.Rect(self.window_rect.right - 18, content_rect.y, 6, content_rect.h)
        pygame.draw.rect(self.screen, (55, 65, 88), track, border_radius=4)
        knob_h = max(70, int(content_rect.h * 0.55))
        knob_y = track.y + int((-self.scroll_offset / max(1, -self.max_scroll)) * (track.h - knob_h))
        pygame.draw.rect(self.screen, settings.UI_ACCENT, pygame.Rect(track.x, knob_y, track.w, knob_h), border_radius=4)

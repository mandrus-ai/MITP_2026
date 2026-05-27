import pygame


class LeaderboardWindow:
    """
    Окно таблицы лидеров.

    Поддерживает загрузку данных с сервера, отображение топа игроков
    и прокрутку списка колесом мыши.
    """

    def __init__(self, screen, client, font_title, font_medium, font_small):
        self.screen = screen
        self.client = client
        self.font_title = font_title
        self.font_medium = font_medium
        self.font_small = font_small

        self.visible = False
        self.players = []

        self.window = pygame.Rect(260, 90, 680, 520)
        self.close_rect = pygame.Rect(self.window.right - 52, self.window.y + 18, 34, 34)

        self.scroll_offset = 0
        self.scroll_speed = 45
        self.card_height = 58
        self.card_gap = 10
        self.list_top = self.window.y + 120
        self.list_bottom = self.window.bottom - 28

    def load_data(self):
        """
        Загружает таблицу лидеров с сервера.

        Ожидаемый формат ответа:
        leaderboard|place:name:score:level|place:name:score:level
        """
        self.players.clear()
        self.scroll_offset = 0

        if not self.client:
            return

        response = self.client.send_command("get_leaderboard")

        if not response:
            return

        response = response.replace("\x01", "").strip()

        if not response.startswith("leaderboard"):
            return

        parts = response.split("|")

        for item in parts[1:]:
            try:
                place, name, score, level = item.split(":")
                self.players.append({
                    "place": place,
                    "name": name,
                    "score": score,
                    "level": level
                })
            except Exception:
                continue

    def _max_scroll(self):
        visible_height = self.list_bottom - self.list_top
        content_height = len(self.players) * (self.card_height + self.card_gap)
        return max(0, content_height - visible_height)

    def _clamp_scroll(self):
        self.scroll_offset = max(0, min(self.scroll_offset, self._max_scroll()))

    def handle_event(self, event):
        """
        Обрабатывает закрытие окна и прокрутку списка.
        """
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True

            if event.key == pygame.K_UP:
                self.scroll_offset -= self.scroll_speed
                self._clamp_scroll()
                return True

            if event.key == pygame.K_DOWN:
                self.scroll_offset += self.scroll_speed
                self._clamp_scroll()
                return True

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed
            self._clamp_scroll()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.close_rect.collidepoint(event.pos):
                self.visible = False
                return True

            # Старый формат событий колесика мыши в pygame.
            if event.button == 4:
                self.scroll_offset -= self.scroll_speed
                self._clamp_scroll()
                return True

            if event.button == 5:
                self.scroll_offset += self.scroll_speed
                self._clamp_scroll()
                return True

        return True

    def draw(self):
        """
        Рисует окно рейтинга и видимую часть списка игроков.
        """
        if not self.visible:
            return

        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height()),
            pygame.SRCALPHA
        )
        overlay.fill((16, 10, 18, 190))
        self.screen.blit(overlay, (0, 0))

        shadow = pygame.Surface((self.window.w, self.window.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (8, 4, 10, 150), shadow.get_rect(), border_radius=26)
        self.screen.blit(shadow, (self.window.x + 8, self.window.y + 10))

        pygame.draw.rect(self.screen, (255, 241, 246), self.window, border_radius=26)
        pygame.draw.rect(self.screen, (190, 108, 145), self.window, 2, border_radius=26)

        title = self.font_title.render("ТОП ИГРОКОВ", True, (88, 42, 66))
        self.screen.blit(title, title.get_rect(center=(self.window.centerx, self.window.y + 55)))

        pygame.draw.rect(self.screen, (214, 92, 122), self.close_rect, border_radius=10)
        close = self.font_medium.render("X", True, (255, 255, 255))
        self.screen.blit(close, close.get_rect(center=self.close_rect.center))

        if not self.players:
            text = self.font_medium.render("Пока нет данных рейтинга", True, (88, 42, 66))
            self.screen.blit(text, text.get_rect(center=self.window.center))
            return

        # Область списка. Всё за её пределами не рисуем.
        clip_rect = pygame.Rect(
            self.window.x + 25,
            self.list_top,
            self.window.w - 50,
            self.list_bottom - self.list_top
        )

        old_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        y = self.list_top - self.scroll_offset

        for player in self.players:
            card = pygame.Rect(self.window.x + 35, y, self.window.w - 90, self.card_height)

            if card.bottom >= self.list_top and card.top <= self.list_bottom:
                pygame.draw.rect(self.screen, (255, 250, 252), card, border_radius=16)
                pygame.draw.rect(self.screen, (220, 180, 200), card, 2, border_radius=16)

                place = self.font_medium.render(f"#{player['place']}", True, (164, 68, 112))
                name = self.font_medium.render(str(player["name"]), True, (88, 42, 66))
                score = self.font_small.render(f"Очки: {player['score']}", True, (166, 122, 60))
                level = self.font_small.render(f"Уровень: {player['level']}", True, (88, 42, 66))

                self.screen.blit(place, (card.x + 18, card.y + 16))
                self.screen.blit(name, (card.x + 75, card.y + 16))
                self.screen.blit(score, (card.right - 210, card.y + 12))
                self.screen.blit(level, (card.right - 110, card.y + 12))

            y += self.card_height + self.card_gap

        self.screen.set_clip(old_clip)

        # Ползунок прокрутки.
        max_scroll = self._max_scroll()
        if max_scroll > 0:
            bar_x = self.window.right - 38
            bar_y = self.list_top
            bar_h = self.list_bottom - self.list_top
            bar_rect = pygame.Rect(bar_x, bar_y, 8, bar_h)

            pygame.draw.rect(self.screen, (235, 205, 220), bar_rect, border_radius=5)

            visible_ratio = bar_h / (bar_h + max_scroll)
            thumb_h = max(34, int(bar_h * visible_ratio))
            thumb_y = bar_y + int((bar_h - thumb_h) * (self.scroll_offset / max_scroll))

            thumb_rect = pygame.Rect(bar_x, thumb_y, 8, thumb_h)
            pygame.draw.rect(self.screen, (164, 68, 112), thumb_rect, border_radius=5)

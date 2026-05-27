import pygame
from settings import settings
from button import Button


class Menu:
    def __init__(self, screen, font_title, font_large, font_medium, font_small):
        self.screen = screen
        self.font_title = font_title
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height
        self.music_volume = 0.5
        self.effects_volume = 0.5
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass

    def _draw_background(self):
        # Светлый pastel pink gradient
        for y in range(self.screen_height):
            t = y / self.screen_height

            r = int(255 - 8 * t)
            g = int(242 - 18 * t)
            b = int(248 - 10 * t)

            pygame.draw.line(
                self.screen,
                (r, g, b),
                (0, y),
                (self.screen_width, y)
            )

        # Большое розовое свечение
        glow1 = pygame.Surface((500, 500), pygame.SRCALPHA)
        pygame.draw.circle(glow1, (255, 192, 220, 70), (250, 250), 240)
        self.screen.blit(glow1, (-120, 40))

        # Кремовое свечение
        glow2 = pygame.Surface((450, 450), pygame.SRCALPHA)
        pygame.draw.circle(glow2, (255, 228, 196, 55), (225, 225), 210)
        self.screen.blit(glow2, (self.screen_width - 320, 120))

        # Сиреневое мягкое свечение
        glow3 = pygame.Surface((420, 420), pygame.SRCALPHA)
        pygame.draw.circle(glow3, (230, 190, 255, 50), (210, 210), 190)
        self.screen.blit(glow3, (self.screen_width // 2 - 200, -80))

        # Нижнее нежное свечение
        glow4 = pygame.Surface((700, 220), pygame.SRCALPHA)
        pygame.draw.ellipse(glow4, (255, 210, 230, 45), glow4.get_rect())
        self.screen.blit(glow4, (220, self.screen_height - 120))

    def _draw_panel(self, rect):
        shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=24)
        self.screen.blit(shadow, (rect.x + 8, rect.y + 10))
        pygame.draw.rect(self.screen, settings.UI_PANEL, rect, border_radius=24)
        pygame.draw.rect(self.screen, settings.UI_BORDER, rect, 2, border_radius=24)

    def _draw_title(self, title, y):
        shadow = self.font_title.render(title, True, (0, 0, 0))
        text = self.font_title.render(title, True, settings.UI_TEXT)
        accent = self.font_title.render(title, True, settings.UI_ACCENT)
        rect = text.get_rect(center=(self.screen_width // 2, y))
        self.screen.blit(shadow, (rect.x + 4, rect.y + 5))
        self.screen.blit(accent, (rect.x, rect.y + 2))
        self.screen.blit(text, rect)

    def _draw_slider(self, label, value, rect):
        label_text = self.font_small.render(label, True, settings.UI_TEXT_DARK)
        self.screen.blit(label_text, (rect.x, rect.y - 28))

        pygame.draw.rect(self.screen, (55, 65, 88), rect, border_radius=8)
        fill = pygame.Rect(rect.x, rect.y, int(rect.w * value), rect.h)
        pygame.draw.rect(self.screen, settings.UI_ACCENT, fill, border_radius=8)
        knob_x = rect.x + int(rect.w * value)
        pygame.draw.circle(self.screen, settings.UI_TEXT, (knob_x, rect.centery), 12)
        pygame.draw.circle(self.screen, settings.UI_ACCENT, (knob_x, rect.centery), 8)

        percent = self.font_small.render(f"{int(value * 100)}%", True, settings.UI_TEXT)
        self.screen.blit(percent, (rect.right + 18, rect.y - 8))

    def _handle_slider(self, event, rect, attr_name):
        if event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEMOTION:
            return
        if event.type == pygame.MOUSEMOTION and not pygame.mouse.get_pressed()[0]:
            return

        mx, my = pygame.mouse.get_pos()
        hot_zone = rect.inflate(0, 24)
        if hot_zone.collidepoint(mx, my):
            value = (mx - rect.x) / rect.w
            value = max(0.0, min(1.0, value))
            setattr(self, attr_name, value)
            if attr_name == "music_volume":
                try:
                    pygame.mixer.music.set_volume(value)
                except Exception:
                    pass

    def _make_button(self, y, text, color):
        return Button(
            self.screen_width // 2 - 145,
            y,
            290,
            58,
            text,
            color,
            settings.UI_ACCENT,
            self.font_medium,
        )

    def show_start_menu(self):
        clock = pygame.time.Clock()
        start_btn = self._make_button(self.screen_height // 2 + 80, "ИГРАТЬ", (164, 68, 112))
        exit_btn = self._make_button(self.screen_height // 2 + 150, "ВЫЙТИ", (180, 72, 96))

        while True:
            self._draw_background()
            self._draw_title("ЕДИНОБОЖИК", 115)

            panel = pygame.Rect(self.screen_width // 2 - 330, 180, 660, 360)
            self._draw_panel(panel)

            subtitle = self.font_medium.render("УПРАВЛЕНИЕ", True, settings.UI_TEXT)
            self.screen.blit(subtitle, subtitle.get_rect(center=(self.screen_width // 2, 225)))

            controls = [("A / D или стрелки", "движение"), ("Пробел", "выстрел"), ("Esc", "пауза")]
            y = 270
            for key, text in controls:
                key_rect = pygame.Rect(self.screen_width // 2 - 230, y - 5, 185, 32)
                pygame.draw.rect(self.screen, settings.UI_CARD, key_rect, border_radius=10)
                pygame.draw.rect(self.screen, settings.UI_BORDER, key_rect, 1, border_radius=10)
                self.screen.blit(self.font_small.render(key, True, settings.UI_TEXT), (key_rect.x + 14, key_rect.y + 7))
                self.screen.blit(self.font_small.render(text, True, settings.UI_TEXT_DARK), (self.screen_width // 2 - 25, y + 2))
                y += 42

            hint = self.font_small.render("Премиальная сладкая аркада", True, settings.UI_TEXT_DARK)
            self.screen.blit(hint, hint.get_rect(center=(self.screen_width // 2, 405)))

            start_btn.draw(self.screen)
            exit_btn.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if start_btn.handle_event(event):
                    return "start"
                if exit_btn.handle_event(event):
                    return "exit"

            clock.tick(60)

    def show_game_over_menu(self, score):
        clock = pygame.time.Clock()
        restart_btn = self._make_button(self.screen_height // 2 + 105, "ЗАНОВО", settings.UI_SUCCESS)
        menu_btn = self._make_button(self.screen_height // 2 + 175, "В МЕНЮ", settings.UI_ACCENT_2)

        while True:
            self._draw_background()
            self._draw_title("ИГРА ОКОНЧЕНА", 115)

            panel = pygame.Rect(self.screen_width // 2 - 270, self.screen_height // 2 - 120, 540, 185)
            self._draw_panel(panel)

            label = self.font_medium.render("ИТОГОВЫЕ ОЧКИ", True, settings.UI_TEXT_DARK)
            self.screen.blit(label, label.get_rect(center=(self.screen_width // 2, panel.y + 50)))
            value = self.font_large.render(str(score), True, settings.UI_WARNING)
            self.screen.blit(value, value.get_rect(center=(self.screen_width // 2, panel.y + 105)))

            restart_btn.draw(self.screen)
            menu_btn.draw(self.screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if restart_btn.handle_event(event):
                    return "restart"
                if menu_btn.handle_event(event):
                    return "menu"

            clock.tick(60)

    def show_pause_menu(self):
        clock = pygame.time.Clock()

        resume_btn = self._make_button(
            self.screen_height // 2 - 10,
            "ПРОДОЛЖИТЬ",
            settings.UI_SUCCESS
        )

        menu_btn = self._make_button(
            self.screen_height // 2 + 65,
            "В ГЛАВНОЕ МЕНЮ",
            settings.UI_ACCENT
        )

        exit_btn = self._make_button(
            self.screen_height // 2 + 140,
            "ВЫЙТИ ИЗ ИГРЫ",
            settings.UI_DANGER
        )

        while True:
            overlay = pygame.Surface(
                (self.screen_width, self.screen_height),
                pygame.SRCALPHA
            )
            overlay.fill((20, 10, 18, 170))
            self.screen.blit(overlay, (0, 0))

            panel = pygame.Rect(
                self.screen_width // 2 - 250,
                self.screen_height // 2 - 170,
                500,
                340
            )

            self._draw_panel(panel)

            self._draw_title("ПАУЗА", panel.y + 55)

            subtitle = self.font_small.render(
                "Единобожик ждёт твоего возвращения",
                True,
                settings.UI_TEXT_DARK
            )

            self.screen.blit(
                subtitle,
                subtitle.get_rect(center=(self.screen_width // 2, panel.y + 120))
            )

            resume_btn.draw(self.screen)
            menu_btn.draw(self.screen)
            exit_btn.draw(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"

                if resume_btn.handle_event(event):
                    return "resume"

                if menu_btn.handle_event(event):
                    return "menu"

                if exit_btn.handle_event(event):
                    return "exit"

            clock.tick(60)

import pygame
from settings import settings


class ShopWindow:
    def __init__(self, screen, client, user_id, font_title, font_medium, font_small):
        self.screen = screen
        self.client = client
        self.user_id = user_id
        self.font_title = font_title
        self.font_medium = font_medium
        self.font_small = font_small

        self.visible = False
        self.currency = 0
        self.current_skin = 0
        self.current_background = 100
        self.on_skin_change = None
        self.on_background_change = None

        self.message = ""
        self.message_timer = 0

        self.click_zones = []
        self.current_page = "backgrounds"

        self.shop_rect = pygame.Rect(90, 35, 1020, 610)
        self.close_rect = pygame.Rect(self.shop_rect.right - 58, self.shop_rect.y + 22, 36, 36)

        self.skins = {
            0: {"name": "Обычный", "price": 0, "owned": True, "file": "unic.png"},
            1: {"name": "Розовый", "price": 100, "owned": False, "file": "unic2.png"},
            2: {"name": "Золотой", "price": 250, "owned": False, "file": "unic3.png"},
        }

        self.backgrounds = {
            100: {"name": "Стандартный", "price": 0, "owned": True, "file": "fone.jpg"},
            101: {"name": "Космос", "price": 50, "owned": False, "file": "fone2.jpg"},
            102: {"name": "Галактика", "price": 100, "owned": False, "file": "fone3.jpg"},
        }

    def update_currency(self, amount):
        self.currency = amount

    def _clean_response(self, response):
        if not response:
            return ""
        return str(response).replace("\x01", "").strip()

    def _set_message(self, text):
        self.message = text
        self.message_timer = pygame.time.get_ticks()

    def load_from_server(self):
        if not self.client:
            return False

        response = self._clean_response(
            self.client.send_command(f"get_shop_data&{self.user_id}")
        )

        if not response.startswith("shop_data"):
            return False

        parts = response.split("|")

        try:
            self.currency = int(parts[1])
            self.current_skin = int(parts[2])
            self.current_background = int(parts[3])

            owned_skins = parts[4].split(",") if len(parts) > 4 and parts[4] else []
            owned_bgs = parts[5].split(",") if len(parts) > 5 and parts[5] else []

            for skin_id in self.skins:
                self.skins[skin_id]["owned"] = str(skin_id) in owned_skins or skin_id == 0

            for bg_id in self.backgrounds:
                self.backgrounds[bg_id]["owned"] = str(bg_id) in owned_bgs or bg_id == 100

            return True
        except Exception:
            return False

    def buy_or_equip_skin(self, skin_id):
        if not self.client:
            self._set_message("Нет соединения с сервером")
            return

        skin = self.skins[skin_id]

        if skin["owned"]:
            response = self._clean_response(
                self.client.send_command(f"equip_item&{self.user_id}&{skin_id}&skin")
            )

            if "success" in response:
                self.current_skin = skin_id
                self._set_message(f"Выбран скин: {skin['name']}")

                if self.on_skin_change:
                    self.on_skin_change(skin["file"])
            else:
                self._set_message("Не удалось выбрать скин")

            return

        if self.currency < skin["price"]:
            self._set_message("Недостаточно монет")
            return

        response = self._clean_response(
            self.client.send_command(f"buy_item&{self.user_id}&{skin_id}&skin")
        )

        if "success" in response:
            self.load_from_server()
            self.buy_or_equip_skin(skin_id)
        else:
            self._set_message("Покупка не прошла")

    def buy_or_equip_background(self, bg_id):
        if not self.client:
            self._set_message("Нет соединения с сервером")
            return

        bg = self.backgrounds[bg_id]

        if bg["owned"]:
            response = self._clean_response(
                self.client.send_command(f"equip_item&{self.user_id}&{bg_id}&bg")
            )

            if "success" in response:
                self.current_background = bg_id
                self._set_message(f"Выбран фон: {bg['name']}")

                if self.on_background_change:
                    self.on_background_change(bg["file"])
            else:
                self._set_message("Не удалось выбрать фон")

            return

        if self.currency < bg["price"]:
            self._set_message("Недостаточно монет")
            return

        response = self._clean_response(
            self.client.send_command(f"buy_item&{self.user_id}&{bg_id}&bg")
        )

        if "success" in response:
            self.load_from_server()
            self.buy_or_equip_background(bg_id)
        else:
            self._set_message("Покупка не прошла")

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return True

        if self.close_rect.collidepoint(event.pos):
            self.visible = False
            return True

        bg_tab = pygame.Rect(self.shop_rect.x + 30, self.shop_rect.y + 88, 190, 44)
        skin_tab = pygame.Rect(self.shop_rect.x + 230, self.shop_rect.y + 88, 190, 44)

        if bg_tab.collidepoint(event.pos):
            self.current_page = "backgrounds"
            return True

        if skin_tab.collidepoint(event.pos):
            self.current_page = "skins"
            return True

        for rect, item_type, item_id in self.click_zones:
            if rect.collidepoint(event.pos):
                if item_type == "skin":
                    self.buy_or_equip_skin(item_id)
                else:
                    self.buy_or_equip_background(item_id)
                return True

        return True

    def _draw_text(self, text, font, color, x, y):
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))
        return surface.get_rect(topleft=(x, y))

    def _draw_button(self, rect, text, color):
        shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (20, 10, 18, 35), shadow.get_rect(), border_radius=12)
        self.screen.blit(shadow, (rect.x + 2, rect.y + 4))

        pygame.draw.rect(self.screen, color, rect, border_radius=12)

        label = self.font_small.render(text, True, (255, 250, 252))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_tab(self, rect, text, active):
        if active:
            color = (164, 68, 112)
            text_color = (255, 250, 252)
            border = (164, 68, 112)
        else:
            color = (255, 250, 252)
            text_color = (88, 42, 66)
            border = (220, 180, 200)

        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=14)

        label = self.font_small.render(text, True, text_color)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_preview(self, rect, item_type, image_file, fallback_color):
        preview = pygame.Rect(rect.x + 20, rect.y + 16, 120, 88)

        pygame.draw.rect(self.screen, (245, 230, 238), preview, border_radius=20)
        pygame.draw.rect(self.screen, (220, 180, 200), preview, 1, border_radius=20)

        try:
            image = pygame.image.load(f"images/{image_file}").convert_alpha()

            if item_type == "background":
                image = pygame.transform.scale(image, (preview.w, preview.h))
                self.screen.blit(image, preview)
            else:
                image = pygame.transform.scale(image, (90, 90))
                image_rect = image.get_rect(center=preview.center)
                self.screen.blit(image, image_rect)

        except Exception:
            pygame.draw.rect(self.screen, fallback_color, preview.inflate(-16, -16), border_radius=16)

    def _draw_item_card(self, rect, item_type, name, price, owned, selected, can_buy, preview_color, image_file):
        shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (20, 10, 18, 42), shadow.get_rect(), border_radius=24)
        self.screen.blit(shadow, (rect.x + 5, rect.y + 7))

        card_color = (255, 255, 255) if selected else (255, 252, 253)
        border_color = (196, 112, 146) if selected else (232, 205, 218)

        pygame.draw.rect(self.screen, card_color, rect, border_radius=24)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=24)

        self._draw_preview(rect, item_type, image_file, preview_color)

        text_x = rect.x + 165

        self._draw_text(name, self.font_medium, (70, 38, 56), text_x, rect.y + 28)
        self._draw_text(image_file, self.font_small, (135, 92, 112), text_x, rect.y + 62)

        if selected:
            status = "Выбрано"
            status_color = (164, 68, 112)
        elif owned:
            status = "Куплено"
            status_color = (164, 68, 112)
        else:
            status = f"Цена: {price}"
            status_color = (166, 122, 60)

        self._draw_text(status, self.font_small, status_color, text_x, rect.y + 94)

        button_rect = pygame.Rect(rect.right - 175, rect.y + 39, 135, 42)

        if selected:
            self._draw_button(button_rect, "Активно", (145, 120, 132))
        elif owned:
            self._draw_button(button_rect, "Выбрать", (164, 68, 112))
        elif can_buy:
            self._draw_button(button_rect, "Купить", (212, 164, 92))
        else:
            self._draw_button(button_rect, "Не хватает", (145, 120, 132))

    def draw(self):
        if not self.visible:
            return

        self.click_zones = []

        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((16, 10, 18, 190))
        self.screen.blit(overlay, (0, 0))

        shadow = pygame.Surface((self.shop_rect.w, self.shop_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (8, 4, 10, 150), shadow.get_rect(), border_radius=26)
        self.screen.blit(shadow, (self.shop_rect.x + 8, self.shop_rect.y + 10))

        pygame.draw.rect(self.screen, (255, 241, 246), self.shop_rect, border_radius=26)
        pygame.draw.rect(self.screen, (190, 108, 145), self.shop_rect, 2, border_radius=26)

        title = self.font_medium.render("МАГАЗИН", True, (88, 42, 66))
        self.screen.blit(title, (self.shop_rect.x + 30, self.shop_rect.y + 24))

        money_rect = pygame.Rect(self.shop_rect.right - 280, self.shop_rect.y + 26, 195, 44)
        pygame.draw.rect(self.screen, (255, 250, 252), money_rect, border_radius=14)
        pygame.draw.rect(self.screen, (212, 164, 92), money_rect, 2, border_radius=14)

        label = self.font_medium.render(f"Монеты: {self.currency}", True, (166, 122, 60))
        self.screen.blit(label, label.get_rect(center=money_rect.center))

        pygame.draw.rect(self.screen, (214, 92, 122), self.close_rect, border_radius=12)
        close = self.font_medium.render("X", True, (255, 250, 252))
        self.screen.blit(close, close.get_rect(center=self.close_rect.center))

        bg_tab = pygame.Rect(self.shop_rect.x + 30, self.shop_rect.y + 88, 190, 44)
        skin_tab = pygame.Rect(self.shop_rect.x + 230, self.shop_rect.y + 88, 190, 44)

        self._draw_tab(bg_tab, "Фоны", self.current_page == "backgrounds")
        self._draw_tab(skin_tab, "Скины", self.current_page == "skins")

        if self.message and pygame.time.get_ticks() - self.message_timer < 2500:
            msg = self.font_small.render(self.message, True, (88, 42, 66))
            self.screen.blit(msg, msg.get_rect(center=(self.shop_rect.centerx, self.shop_rect.y + 112)))

        start_x = self.shop_rect.x + 36
        start_y = self.shop_rect.y + 155

        card_w = self.shop_rect.w - 72
        card_h = 120
        gap = 12

        if self.current_page == "backgrounds":
            colors = [
                (150, 120, 145),
                (120, 140, 190),
                (150, 115, 190)
            ]

            y = start_y

            for index, (bg_id, bg) in enumerate(self.backgrounds.items()):
                rect = pygame.Rect(start_x, y, card_w, card_h)

                selected = bg_id == self.current_background
                can_buy = self.currency >= bg["price"]

                self._draw_item_card(
                    rect,
                    "background",
                    bg["name"],
                    bg["price"],
                    bg["owned"],
                    selected,
                    can_buy,
                    colors[index % len(colors)],
                    bg["file"]
                )

                self.click_zones.append((rect, "background", bg_id))
                y += card_h + gap

        else:
            y = start_y

            for skin_id, skin in self.skins.items():
                rect = pygame.Rect(start_x, y, card_w, card_h)

                selected = skin_id == self.current_skin
                can_buy = self.currency >= skin["price"]

                self._draw_item_card(
                    rect,
                    "skin",
                    skin["name"],
                    skin["price"],
                    skin["owned"],
                    selected,
                    can_buy,
                    (190, 130, 165),
                    skin["file"]
                )

                self.click_zones.append((rect, "skin", skin_id))
                y += card_h + gap
import pygame


class ShopWindow:
    def __init__(self, screen, width, height, client, draw_rounded_rect_func):
        self.screen = screen
        self.width = width
        self.height = height
        self.client = client
        self.draw_rounded_rect = draw_rounded_rect_func
        self.visible = False

        self.font_title = pygame.font.Font(None, 56)
        self.font_header = pygame.font.Font(None, 36)
        self.font_text = pygame.font.Font(None, 24)
        self.font_price = pygame.font.Font(None, 28)
        self.font_button = pygame.font.Font(None, 28)

        # Данные игрока
        self.current_skin = 0
        self.current_background = 100
        self.current_background_file = "fone.png"
        self.owned_skins = [0]
        self.owned_backgrounds = [100]
        self.currency = 0

        # Список скинов
        self.skins = [
            {"id": 0, "name": "Единорог", "price": 0, "file": "unic.png", "owned": True, "type": "skin"},
            {"id": 1, "name": "Единорог 2", "price": 100, "file": "unic2.png", "owned": False, "type": "skin"},
            {"id": 2, "name": "Единорог 3", "price": 250, "file": "unic3.png", "owned": False, "type": "skin"},
        ]

        # Список фонов
        self.backgrounds = [
            {"id": 100, "name": "Розовый фон", "price": 0, "file": "fone.jpg", "owned": True, "type": "bg"},
            {"id": 101, "name": "Фон 2", "price": 50, "file": "fone2.jpg", "owned": False, "type": "bg"},
            {"id": 102, "name": "Фон 3", "price": 100, "file": "fone3.jpg", "owned": False, "type": "bg"},
        ]

        # Кнопки
        self.back_button = pygame.Rect(width // 2 - 100, height - 80, 200, 45)
        self.prev_button = pygame.Rect(width // 2 - 250, height - 80, 100, 40)
        self.next_button = pygame.Rect(width // 2 + 150, height - 80, 100, 40)

        self.current_page = 0
        self.skins_per_page = 3

        self.selected_skin_id = 0
        self.message = ""
        self.message_timer = 0

    def update_currency(self, currency):
        self.currency = currency

    def update_owned_skins(self, owned_skins_ids):
        self.owned_skins = owned_skins_ids
        for skin in self.skins:
            skin["owned"] = skin["id"] in self.owned_skins

    def set_current_skin(self, skin_id):
        self.current_skin = skin_id

    def buy_skin(self, skin_id):
        """Покупка скина (локально, без сервера для теста)"""
        skin = self.get_skin_by_id(skin_id)
        if not skin:
            return False

        if skin["owned"]:
            self.message = "У вас уже есть этот скин!"
            self.message_timer = pygame.time.get_ticks()
            return False

        if self.currency >= skin["price"]:
            # Временно отключаем отправку на сервер
            # response = self.client.send_command(f"buyskin {skin_id}")
            # if response and "success" in response:
            if True:  # Временно всегда успешно
                self.owned_skins.append(skin_id)
                skin["owned"] = True
                self.currency -= skin["price"]  # Списываем монеты локально

                if hasattr(self, 'on_currency_change'):
                    self.on_currency_change(self.currency)

                self.message = f"Куплен скин: {skin['name']}!"
                self.message_timer = pygame.time.get_ticks()
                return True
            else:
                self.message = "Ошибка покупки!"
                self.message_timer = pygame.time.get_ticks()
                return False
        else:
            self.message = f"Не хватает монет! Нужно: {skin['price']}"
            self.message_timer = pygame.time.get_ticks()
            return False
    def buy_background(self, bg_id):
        """Покупка фона"""
        bg = self.get_background_by_id(bg_id)
        if not bg:
            return False

        if bg["owned"]:
            self.message = "У вас уже есть этот фон!"
            self.message_timer = pygame.time.get_ticks()
            return False

        if self.currency >= bg["price"]:
            self.owned_backgrounds.append(bg_id)
            bg["owned"] = True
            self.currency -= bg["price"]

            if hasattr(self, 'on_currency_change'):
                self.on_currency_change(self.currency)

            self.message = f"Куплен фон: {bg['name']}!"
            self.message_timer = pygame.time.get_ticks()
            return True
        else:
            self.message = f"Не хватает монет! Нужно: {bg['price']}"
            self.message_timer = pygame.time.get_ticks()
            return False
    def equip_skin(self, skin_id):
        """Экипировка скина"""
        print(f"equip_skin вызван с skin_id={skin_id}")
        skin = self.get_skin_by_id(skin_id)
        print(f"Найден скин: {skin}")
        if skin and skin["owned"]:
            print(f"Скин принадлежит игроку, пытаемся экипировать")
            # Временно отключаем отправку на сервер для теста
            # response = self.client.send_command(f"equipskin {skin_id}")
            # if response and "success" in response:
            if True:  # Временно всегда успешно
                self.current_skin = skin_id
                self.message = f"Скин {skin['name']} экипирован!"
                self.message_timer = pygame.time.get_ticks()
                print(f"Скин успешно экипирован! current_skin={self.current_skin}")
                return True, skin["file"]
            else:
                print("Ошибка ответа от сервера")
        else:
            print(f"Скин не принадлежит игроку или не найден. owned={skin['owned'] if skin else 'None'}")
        return False, None

    def equip_background(self, bg_id):
        """Экипировка фона"""
        bg = self.get_background_by_id(bg_id)
        if bg and bg["owned"]:
            self.current_background = bg_id
            self.current_background_file = bg["file"]
            self.message = f"Фон {bg['name']} установлен!"
            self.message_timer = pygame.time.get_ticks()
            return True, bg["file"]
        return False, None

    def get_background_by_id(self, bg_id):
        """Получить фон по ID"""
        for bg in self.backgrounds:
            if bg["id"] == bg_id:
                return bg
        return None
    def get_skin_by_id(self, skin_id):
        for skin in self.skins:
            if skin["id"] == skin_id:
                return skin
        return None

    def draw(self):
        if not self.visible:
            return

        # Полупрозрачный фон на всю область
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Главная панель
        panel_rect = pygame.Rect(50, 50, self.width - 100, self.height - 100)
        self.draw_rounded_rect(self.screen, (255, 255, 255), panel_rect, 25)
        pygame.draw.rect(self.screen, (255, 105, 180), panel_rect, 3, border_radius=25)

        # Заголовок
        title = self.font_title.render("МАГАЗИН", True, (255, 105, 180))
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)

        # Баланс монет
        currency_text = self.font_header.render(f"Ваши монеты: {self.currency}", True, (255, 150, 100))
        currency_rect = currency_text.get_rect(center=(self.width // 2, 130))
        self.screen.blit(currency_text, currency_rect)

        # Вкладки
        tab_skins = pygame.Rect(self.width // 2 - 120, 170, 100, 35)
        tab_bgs = pygame.Rect(self.width // 2 + 20, 170, 100, 35)

        # Добавляем атрибут active_tab если его нет
        if not hasattr(self, 'active_tab'):
            self.active_tab = "skins"

        skin_color = (255, 120, 170) if self.active_tab == "skins" else (200, 100, 140)
        bg_color = (255, 120, 170) if self.active_tab == "backgrounds" else (200, 100, 140)

        self.draw_rounded_rect(self.screen, skin_color, tab_skins, 10)
        skin_text = self.font_text.render("Скины", True, (255, 255, 255))
        skin_rect = skin_text.get_rect(center=tab_skins.center)
        self.screen.blit(skin_text, skin_rect)

        self.draw_rounded_rect(self.screen, bg_color, tab_bgs, 10)
        bg_text = self.font_text.render("Фоны", True, (255, 255, 255))
        bg_rect = bg_text.get_rect(center=tab_bgs.center)
        self.screen.blit(bg_text, bg_rect)

        pygame.draw.line(self.screen, (255, 105, 180),
                         (100, 210), (self.width - 100, 210), 2)

        # Выбираем какой список показывать
        if self.active_tab == "skins":
            items = self.skins
            # Для скинов показываем все на одной странице
            start_idx = 0
            end_idx = len(items)
        else:
            items = self.backgrounds
            # Для фонов оставляем пагинацию
            start_idx = self.current_page * self.skins_per_page
            end_idx = min(start_idx + self.skins_per_page, len(items))

        if len(items) == 0:
            no_items_text = self.font_text.render("Нет доступных предметов", True, (150, 80, 120))
            no_items_rect = no_items_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(no_items_text, no_items_rect)
        else:
            item_y = 240
            card_width = 300
            card_height = 250
            spacing = 40
            total_width = min(self.skins_per_page, len(items)) * card_width + (
                        min(self.skins_per_page, len(items)) - 1) * spacing
            start_x = (self.width - total_width) // 2

            mouse_pos = pygame.mouse.get_pos()

            for i, item in enumerate(items[start_idx:end_idx]):
                card_x = start_x + i * (card_width + spacing)
                card_rect = pygame.Rect(card_x, item_y, card_width, card_height)

                # Фон карточки
                if item["owned"]:
                    if self.active_tab == "skins" and item["id"] == self.current_skin:
                        bg_color_card = (200, 255, 200)
                    elif self.active_tab == "backgrounds" and item["id"] == self.current_background:
                        bg_color_card = (200, 255, 200)
                    else:
                        bg_color_card = (255, 250, 210)
                    border_color = (100, 200, 100)
                else:
                    bg_color_card = (245, 245, 245)
                    border_color = (200, 200, 200)

                self.draw_rounded_rect(self.screen, bg_color_card, card_rect, 20)
                pygame.draw.rect(self.screen, border_color, card_rect, 3, border_radius=20)

                # Название
                name_text = self.font_header.render(item["name"], True, (100, 50, 80))
                name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.y + 35))
                self.screen.blit(name_text, name_rect)

                # Изображение
                try:
                    item_image = pygame.image.load(f'images/{item["file"]}')
                    item_image = pygame.transform.scale(item_image, (100, 100))
                    img_rect = item_image.get_rect(center=(card_rect.centerx, card_rect.y + 110))
                    self.screen.blit(item_image, img_rect)
                except:
                    # Если картинки нет - рисуем прямоугольник
                    pygame.draw.rect(self.screen, (200, 150, 180),
                                     (card_rect.centerx - 50, card_rect.y + 60, 100, 100), border_radius=10)

                # Цена или статус
                if item["owned"]:
                    status_text = self.font_text.render("В СОБСТВЕННОСТИ", True, (100, 150, 100))
                    status_rect = status_text.get_rect(center=(card_rect.centerx, card_rect.y + 185))
                    self.screen.blit(status_text, status_rect)
                else:
                    price_text = self.font_price.render(f"{item['price']} монет", True, (255, 120, 100))
                    price_rect = price_text.get_rect(center=(card_rect.centerx, card_rect.y + 185))
                    self.screen.blit(price_text, price_rect)

                # Кнопка действия
                button_rect = pygame.Rect(card_rect.x + 50, card_rect.y + 210, card_width - 100, 35)

                if item["owned"]:
                    if self.active_tab == "skins" and item["id"] == self.current_skin:
                        button_text = "В ИСПОЛЬЗОВАНИИ"
                        button_color = (150, 150, 150)
                    elif self.active_tab == "backgrounds" and item["id"] == self.current_background:
                        button_text = "В ИСПОЛЬЗОВАНИИ"
                        button_color = (150, 150, 150)
                    else:
                        button_text = "ПРИМЕНИТЬ"
                        button_color = (80, 180, 80)
                else:
                    button_text = "КУПИТЬ"
                    button_color = (255, 120, 170)

                is_hover = button_rect.collidepoint(mouse_pos)
                if is_hover and (not item["owned"] or (item["owned"] and button_text == "ПРИМЕНИТЬ")):
                    if not item["owned"]:
                        button_color = (255, 80, 140)
                    else:
                        button_color = (60, 160, 60)

                self.draw_rounded_rect(self.screen, button_color, button_rect, 10)
                btn_text = self.font_button.render(button_text, True, (255, 255, 255))
                btn_rect = btn_text.get_rect(center=button_rect.center)
                self.screen.blit(btn_text, btn_rect)

                # Обработка клика
                if is_hover and pygame.mouse.get_pressed()[0]:
                    if self.active_tab == "skins":
                        if item["owned"]:
                            if item["id"] != self.current_skin:
                                self.equip_skin(item["id"])
                        else:
                            self.buy_skin(item["id"])
                    else:
                        if item["owned"]:
                            if item["id"] != self.current_background:
                                self.equip_background(item["id"])
                        else:
                            self.buy_background(item["id"])
                    pygame.time.wait(200)

        # Сообщение
        if self.message and pygame.time.get_ticks() - self.message_timer < 3000:
            msg_surf = self.font_text.render(self.message, True, (255, 80, 80))
            msg_rect = msg_surf.get_rect(center=(self.width // 2, self.height - 40))
            self.screen.blit(msg_surf, msg_rect)

        # Кнопка закрытия
        mouse_pos = pygame.mouse.get_pos()
        back_hover = self.back_button.collidepoint(mouse_pos)
        back_color = (255, 120, 170) if back_hover else (255, 80, 140)
        self.draw_rounded_rect(self.screen, back_color, self.back_button, 10)
        back_text = self.font_button.render("ЗАКРЫТЬ", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)

    def handle_click(self, pos):
        # Кнопка закрытия
        if self.back_button.collidepoint(pos):
            self.visible = False
            return "back"

        # Вкладки
        tab_skins = pygame.Rect(self.width // 2 - 120, 170, 100, 35)
        tab_bgs = pygame.Rect(self.width // 2 + 20, 170, 100, 35)

        if tab_skins.collidepoint(pos):
            self.active_tab = "skins"
            self.current_page = 0
            return "refresh"

        if tab_bgs.collidepoint(pos):
            self.active_tab = "backgrounds"
            self.current_page = 0
            return "refresh"

        # Пагинация
        if self.prev_button.collidepoint(pos) and self.current_page > 0:
            self.current_page -= 1
            return "refresh"

        if self.next_button.collidepoint(pos):
            items = self.skins if self.active_tab == "skins" else self.backgrounds
            total_pages = (len(items) + self.skins_per_page - 1) // self.skins_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
                return "refresh"

        return None


class ShopButton:
    def __init__(self, screen, x, y, width=60, height=40, draw_rounded_rect_func=None):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 24)
        self.is_hover = False
        self.draw_rounded_rect = draw_rounded_rect_func
        self.current_background = 0  # ID текущего фона
        self.current_background_file = "fone.png"


    def draw(self):
        if self.draw_rounded_rect:
            color = (255, 180, 100) if self.is_hover else (255, 140, 60)
            self.draw_rounded_rect(self.screen, color, self.rect, 10)
            pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2, border_radius=10)
        else:
            color = (255, 180, 100) if self.is_hover else (255, 140, 60)
            pygame.draw.rect(self.screen, color, self.rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2, border_radius=10)

        text = self.font.render("SHOP", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return "shop"
        return None
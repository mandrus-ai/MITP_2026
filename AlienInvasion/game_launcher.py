import pygame
import sys
import random
import os
import signal
from settings import settings
from level_system import LevelSystem
from button import Button
from menu import Menu
from achievements import AchievementSystem, AchievementWindow
from shop import ShopWindow
from leaderboard import LeaderboardWindow

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)

pygame.init()

SCREEN_WIDTH = settings.screen_width
SCREEN_HEIGHT = settings.screen_height

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Единобожик")
clock = pygame.time.Clock()

# Шрифты
font_title = pygame.font.Font(None, 72)
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

# Меню
menu = Menu(screen, font_title, font_large, font_medium, font_small)


# Загрузка картинок
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        return None


unicorn_img = load_image('images/unic.png', (100, 100))
donut_img = load_image('images/donut1.png', (50, 50))
background_img = load_image('images/fone.jpg', (SCREEN_WIDTH, SCREEN_HEIGHT))

if background_img is None:
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for i in range(SCREEN_HEIGHT):
        t = i / SCREEN_HEIGHT
        r = int(255 - 35 * t)
        g = int(200 - 30 * t)
        b = int(220 - 40 * t)
        pygame.draw.line(background_img, (r, g, b), (0, i), (SCREEN_WIDTH, i))

if donut_img is None:
    donut_img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(donut_img, (160, 100, 60), (25, 25), 25)
    pygame.draw.circle(donut_img, (255, 220, 180), (25, 25), 15)

if unicorn_img is None:
    unicorn_img = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.ellipse(unicorn_img, (255, 220, 240), (25, 45, 55, 40))
    pygame.draw.circle(unicorn_img, (255, 220, 240), (80, 48), 22)


def draw_rounded_rect(surface, color, rect, radius=15):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


# Функция сохранения всех данных
def save_all_data(client, user_id, currency, score, level_sys):
    """Сохраняет все данные игрока на сервер"""
    if client and client.connected:
        client.send_command(f"save_all&{user_id}&{score}&{currency}&{level_sys.current_level}&{level_sys.total_xp}")
        print(
            f"[СОХРАНЕНИЕ] Монеты={currency}, Очки={score}, Уровень={level_sys.current_level}, XP={level_sys.total_xp}")
        return True
    return False


# Класс корабля
class Ship:
    """
    Игровой персонаж.

    Движение рассчитано через delta time, поэтому управление остаётся
    плавным даже при небольших просадках FPS.
    """
    def __init__(self):
        self.image = unicorn_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30

        self.x = float(self.rect.centerx)
        self.velocity = 0.0

        self.max_speed = 520.0       # пикселей в секунду
        self.acceleration = 2800.0   # разгон
        self.friction = 0.88         # плавное торможение

        self.moving_left = False
        self.moving_right = False

    def update(self, dt):
        if self.moving_right and not self.moving_left:
            self.velocity += self.acceleration * dt
        elif self.moving_left and not self.moving_right:
            self.velocity -= self.acceleration * dt
        else:
            self.velocity *= self.friction

        if abs(self.velocity) < 3:
            self.velocity = 0.0

        self.velocity = max(-self.max_speed, min(self.velocity, self.max_speed))

        self.x += self.velocity * dt
        self.rect.centerx = int(self.x)

        if self.rect.left < 20:
            self.rect.left = 20
            self.x = float(self.rect.centerx)
            self.velocity = 0.0

        if self.rect.right > SCREEN_WIDTH - 20:
            self.rect.right = SCREEN_WIDTH - 20
            self.x = float(self.rect.centerx)
            self.velocity = 0.0

    def draw(self):
        screen.blit(self.image, self.rect)

    def center(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.x = float(self.rect.centerx)
        self.velocity = 0.0

    def set_skin(self, skin_file):
        try:
            new_img = pygame.image.load(f'images/{skin_file}').convert_alpha()
            self.image = pygame.transform.scale(new_img, (100, 100))
        except Exception:
            pass


# Класс пули
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 3, y - 10, 6, 15)
        self.speed = settings.bullet_speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        draw_rounded_rect(screen, settings.GOLD, self.rect, 3)

    def off_screen(self):
        return self.rect.bottom < 0


# Класс пончика
class Donut:
    def __init__(self, speed_multiplier=1.0):
        self.image = donut_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.y = random.randint(-200, -50)
        self.speed = random.uniform(1, 2.5) * speed_multiplier

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

    def off_screen(self):
        return self.rect.top > SCREEN_HEIGHT + 100


def draw_stats_panel(level_sys, score, currency, level_coins):
    # Верхняя игровая HUD-панель
    margin = 16
    avatar_size = 70

    # Аватар слева
    avatar = pygame.Rect(margin, margin, avatar_size, avatar_size)
    pygame.draw.rect(screen, (255, 241, 246), avatar, border_radius=18)
    pygame.draw.rect(screen, (190, 108, 145), avatar, 3, border_radius=18)

    if unicorn_img:
        img = pygame.transform.scale(unicorn_img, (58, 58))
        screen.blit(img, img.get_rect(center=avatar.center))

    # Имя / уровень
    name_x = avatar.right + 12
    name_bg = pygame.Rect(name_x, margin + 2, 190, 30)
    pygame.draw.rect(screen, (255, 241, 246), name_bg, border_radius=12)

    name_text = font_small.render(user_name, True, (88, 42, 66))
    screen.blit(name_text, (name_bg.x + 12, name_bg.y + 6))

    level_badge = pygame.Rect(name_x, margin + 38, 48, 28)
    pygame.draw.rect(screen, (164, 68, 112), level_badge, border_radius=14)

    level_text = font_small.render(str(level_sys.current_level), True, (255, 250, 252))
    screen.blit(level_text, level_text.get_rect(center=level_badge.center))

    # XP bar
    xp_current, xp_needed = level_sys.get_current_level_xp()
    progress = level_sys.get_progress_percentage() / 100

    xp_bar = pygame.Rect(level_badge.right + 8, margin + 42, 135, 18)
    pygame.draw.rect(screen, (220, 205, 215), xp_bar, border_radius=10)

    fill = pygame.Rect(
        xp_bar.x,
        xp_bar.y,
        int(xp_bar.w * progress),
        xp_bar.h
    )
    pygame.draw.rect(screen, (255, 92, 176), fill, border_radius=10)

    xp_text = font_small.render(f"{xp_current}/{xp_needed}", True, (255, 250, 252))
    screen.blit(xp_text, xp_text.get_rect(center=xp_bar.center))

    # Центр: уровень/локация
    center_panel = pygame.Rect(SCREEN_WIDTH // 2 - 140, 16, 280, 54)
    pygame.draw.rect(screen, (255, 250, 252), center_panel, border_radius=18)
    pygame.draw.rect(screen, (220, 180, 200), center_panel, 2, border_radius=18)

    loc_text = font_medium.render(f"Уровень {level_sys.current_level}", True, (88, 42, 66))
    screen.blit(loc_text, loc_text.get_rect(center=center_panel.center))

    # Монеты справа
    coins_panel = pygame.Rect(SCREEN_WIDTH - 235, 16, 210, 54)
    pygame.draw.rect(screen, (255, 250, 252), coins_panel, border_radius=18)
    pygame.draw.rect(screen, (212, 164, 92), coins_panel, 2, border_radius=18)

    coins_text = font_medium.render(f"Монеты: {currency}", True, (166, 122, 60))
    screen.blit(coins_text, coins_text.get_rect(center=coins_panel.center))

    # Очки под монетами
    score_panel = pygame.Rect(SCREEN_WIDTH - 235, 82, 145, 38)
    pygame.draw.rect(screen, (255, 241, 246), score_panel, border_radius=15)
    pygame.draw.rect(screen, (190, 108, 145), score_panel, 2, border_radius=15)

    score_text = font_small.render(f"Очки: {score}", True, (88, 42, 66))
    screen.blit(score_text, score_text.get_rect(center=score_panel.center))

def draw_particle_effect(particles):
    for p in particles:
        alpha = int(200 * (1 - p['life']))
        if alpha > 0:
            color = (settings.HOT_PINK[0], settings.HOT_PINK[1], settings.HOT_PINK[2], alpha)
            surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (p['size'], p['size']), p['size'])
            screen.blit(surf, (p['x'] - p['size'], p['y'] - p['size']))
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 0.02
        if p['life'] <= 0:
            p['x'] = random.randint(0, SCREEN_WIDTH)
            p['y'] = random.randint(0, SCREEN_HEIGHT)
            p['life'] = 1.0


def create_donuts_for_level(level_sys):
    donuts = []
    stats = level_sys.get_level_stats()
    donut_count = min(stats['donut_count'], 5)
    donut_speed = stats['donut_speed']

    for _ in range(donut_count):
        donuts.append(Donut(donut_speed))
    return donuts


def spawn_new_donut(level_sys, donuts):
    if len(donuts) < 12:
        stats = level_sys.get_level_stats()
        donut_speed = stats['donut_speed']
        donuts.append(Donut(donut_speed))


# Подключение к серверу
class GameClient:
    def __init__(self, host=None, port=33334):
        import socket
        import os

        if host is None:
            host = "127.0.0.1"

            config_paths = [
                os.path.join(BASE_DIR, "server_config.txt"),
                os.path.join(BASE_DIR, "..", "server_config.txt"),
            ]
            for path in config_paths:
                try:
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as file:
                            value = file.read().strip()
                            if value:
                                host = value
                                break
                except:
                    pass

        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        try:
            import socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except:
            return False

    def send_command(self, cmd):
        if not self.connected:
            return None
        try:
            self.socket.sendall((cmd + '\n').encode())
            response = self.socket.recv(4096).decode().strip()
            return response
        except:
            return None


client = GameClient()
if not client.connect():
    print("Сервер не доступен, игра в офлайн режиме")
    client = None

# ДАННЫЕ ПОЛЬЗОВАТЕЛЯ (приходят из C++ клиента через аргументы командной строки)
user_id = 1
user_name = "Player"
user_score = 0
user_currency = 0
user_level = 1
user_skin = 0
user_background = 100
user_xp = 0
socket_id = ""

# Получаем данные из аргументов командной строки
if len(sys.argv) >= 7:
    try:
        user_name = sys.argv[1]
        user_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        user_score = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        user_currency = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        user_level = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        socket_id = sys.argv[10] if len(sys.argv) > 10 else ""
        print(
            f"Загружено из аргументов: имя={user_name}, id={user_id}, очки={user_score}, монеты={user_currency}, уровень={user_level}")
    except:
        pass

# Загружаем данные с сервера при старте
if client:
    response = client.send_command(f"get_user_data&{user_id}")
    if response:
        response = response.replace('\x01', '').strip()
    if response and response.startswith("user_data"):
        parts = response.split('|')
        if len(parts) >= 6:
            user_score = int(parts[1])
            user_currency = int(parts[2])
            user_level = int(parts[3])
            user_skin = int(parts[4])
            user_background = int(parts[5])
            user_xp = int(parts[6]) if len(parts) > 6 else 0
            user_name = parts[7] if len(parts) > 7 else user_name
            print(f"[ЗАГРУЗКА С СЕРВЕРА] Очки={user_score}, Монеты={user_currency}, Уровень={user_level}, XP={user_xp}")

# Инициализация системы достижений
achievement_system = AchievementSystem(client, user_id)
achievement_window = AchievementWindow(screen, achievement_system, font_title, font_medium, font_small)

# Инициализация магазина
shop_window = ShopWindow(screen, client, user_id, font_title, font_medium, font_small)

leaderboard_window = LeaderboardWindow(
    screen,
    client,
    font_title,
    font_medium,
    font_small
)

# Функции для применения покупок
def on_skin_change(skin_file):
    ship.set_skin(skin_file)


def on_background_change(bg_file):
    global background_img
    try:
        new_bg = pygame.image.load(f'images/{bg_file}')
        background_img = pygame.transform.scale(new_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        pass


shop_window.on_skin_change = on_skin_change
shop_window.on_background_change = on_background_change

# Кнопки
shop_btn = Button(
    SCREEN_WIDTH - 150, 128, 58, 58,
    "",
    (255, 241, 246),
    (255, 220, 235),
    font_small
)

achievements_btn = Button(
    SCREEN_WIDTH - 82, 128, 58, 58,
    "",
    (255, 241, 246),
    (255, 220, 235),
    font_small
)

leaderboard_btn = Button(
    SCREEN_WIDTH - 218, 128, 58, 58,
    "",
    (255, 241, 246),
    (255, 220, 235),
    font_small
)

# Частицы
particles = []
for _ in range(30):
    particles.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(0, SCREEN_HEIGHT),
        'vx': random.uniform(-0.3, 0.3),
        'vy': random.uniform(-0.3, 0.3),
        'size': random.randint(2, 3),
        'life': random.uniform(0.5, 1.0)
    })

# Инициализация игры
ship = Ship()
bullets = []
donuts = []
score = user_score
currency = user_currency
level_coins = 0
kills = 0
bullets_fired = 0
game_active = False
game_paused = False
achievement_paused = False
spawn_timer = 0
spawn_delay = 4000
level_sys = LevelSystem()
level_sys.current_level = user_level
level_sys.total_xp = user_xp
level_sys.current_xp = user_xp

# Загрузка данных из магазина
if shop_window.load_from_server():
    currency = shop_window.currency
    user_currency = currency
    for skin_id, skin in shop_window.skins.items():
        if skin_id == shop_window.current_skin and skin["owned"]:
            ship.set_skin(skin["file"])
            break
    for bg_id, bg in shop_window.backgrounds.items():
        if bg_id == shop_window.current_background and bg["owned"]:
            try:
                new_bg = pygame.image.load(f'images/{bg["file"]}')
                background_img = pygame.transform.scale(new_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except:
                pass
            break

# Автосохранение
last_save_time = pygame.time.get_ticks()
AUTO_SAVE_INTERVAL = 30000  # 30 секунд

# Главное меню
menu_result = menu.show_start_menu()
if menu_result == "exit":
    save_all_data(client, user_id, currency, score, level_sys)
    if client:
        client.socket.close()
    pygame.quit()
    sys.exit()

# Запуск игры
game_active = True
donuts = create_donuts_for_level(level_sys)
spawn_timer = pygame.time.get_ticks()
stats = level_sys.get_level_stats()
spawn_delay = int(stats['spawn_delay'] * 1000)

# Главный игровой цикл
running = True
while running:
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 1 / 30)  # защита от рывка после паузы/подвисания
    current_time = pygame.time.get_ticks()

    # Автосохранение
    if game_active and not game_paused and not shop_window.visible:
        if current_time - last_save_time > AUTO_SAVE_INTERVAL:
            save_all_data(client, user_id, currency, score, level_sys)
            last_save_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # СОХРАНЯЕМ ВСЕ ДАННЫЕ ПЕРЕД ВЫХОДОМ
            save_all_data(client, user_id, currency, score, level_sys)
            if client:
                client.socket.close()
            running = False

        if leaderboard_window.visible:
            leaderboard_window.handle_event(event)
            continue

        # Если открыт магазин — все клики и клавиши сначала идут в магазин.
        # Игра при этом не стреляет и не двигает персонажа.
        if shop_window.visible:
            shop_window.handle_event(event)
            currency = shop_window.currency
            user_currency = currency
            continue

        if achievement_paused:
            if hasattr(achievement_window, "handle_event"):
                achievement_window.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    achievement_paused = False
                    achievement_window.hide()
                continue
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL):
                continue

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if game_active and not game_paused:
                    pause_result = menu.show_pause_menu()
                    if pause_result == "resume":
                        game_paused = False
                    elif pause_result == "menu":
                        save_all_data(client, user_id, currency, score, level_sys)
                        game_active = False
                        game_paused = False
                        menu_result = menu.show_start_menu()
                        if menu_result == "start":
                            game_active = True
                            score = user_score
                            currency = user_currency
                            level_coins = 0
                            kills = 0
                            bullets_fired = 0
                            level_sys.reset()
                            level_sys.current_level = user_level
                            level_sys.total_xp = user_xp
                            level_sys.current_xp = user_xp
                            donuts = create_donuts_for_level(level_sys)
                            bullets.clear()
                            ship.center()
                            spawn_timer = current_time
                            stats = level_sys.get_level_stats()
                            spawn_delay = int(stats['spawn_delay'] * 1000)
                            shop_window.update_currency(currency)
                        else:
                            save_all_data(client, user_id, currency, score, level_sys)
                            running = False
                    elif pause_result == "exit":
                        save_all_data(client, user_id, currency, score, level_sys)
                        running = False

            if game_active and not game_paused and not achievement_paused and not shop_window.visible:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    ship.moving_right = True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    ship.moving_left = True
                elif event.key == pygame.K_SPACE:
                    if len(bullets) < 15:
                        bullets.append(Bullet(ship.rect.centerx, ship.rect.top))
                        bullets_fired += 1
                        achievement_system.update_progress(17, bullets_fired)

        if event.type == pygame.KEYUP:
            if achievement_paused:
                continue

            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                ship.moving_right = False
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                ship.moving_left = False

        # Обработка кнопки достижений
        if achievements_btn.handle_event(event):
            if game_active and not achievement_paused:
                achievement_paused = True
                achievement_window.show()
            elif achievement_paused:
                achievement_paused = False
                achievement_window.hide()

        # Обработка кнопки рейтинга
        if leaderboard_btn.handle_event(event):
            leaderboard_window.load_data()
            leaderboard_window.visible = True

        # Обработка кнопки магазина
        if shop_btn.handle_event(event):
            if game_active and not achievement_paused:
                shop_window.load_from_server()
                currency = shop_window.currency
                user_currency = currency
                shop_window.visible = True

    if not game_active:
        break

    screen.blit(background_img, (0, 0))
    draw_particle_effect(particles)

    if game_active and not game_paused and not achievement_paused and not shop_window.visible:
        ship.update(dt)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.off_screen():
                bullets.remove(bullet)

        for donut in donuts[:]:
            donut.update()

            for bullet in bullets[:]:
                if bullet.rect.colliderect(donut.rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if donut in donuts:
                        donuts.remove(donut)

                    stats = level_sys.get_level_stats()
                    points = int(10 * stats['bonus_multiplier'])
                    coins_reward = int(1 * stats['bonus_multiplier'])
                    xp = 10

                    score += points
                    currency += coins_reward
                    level_coins += coins_reward
                    kills += 1

                    user_score = score
                    user_currency = currency

                    # СОХРАНЯЕМ МОНЕТЫ НА СЕРВЕРЕ ПРИ КАЖДОМ УБИЙСТВЕ
                    if client:
                        client.send_command(f"update_coins&{user_id}&{currency}")
                        client.send_command(f"update_score&{user_id}&{score}")

                    # Обновляем монеты в магазине
                    shop_window.update_currency(currency)

                    # Достижения
                    # 1–5, 23–40, 71–80, 86–100: достижения за убийства пончиков
                    for ach_id in list(range(1, 6)) + list(range(23, 41)) + list(range(71, 81)) + list(range(86, 101)):
                        achievement_system.update_progress(ach_id, kills)

                    # 6–10, 41–50: достижения за очки
                    for ach_id in list(range(6, 11)) + list(range(41, 51)):
                        achievement_system.update_progress(ach_id, score)

                    # 11–15, 51–60: достижения за уровень
                    for ach_id in list(range(11, 16)) + list(range(51, 61)):
                        achievement_system.update_progress(ach_id, level_sys.current_level)

                    # 16–20: достижения за монеты
                    for ach_id in range(16, 21):
                        achievement_system.update_progress(ach_id, currency)

                    # 21–22, 61–70: достижения за выстрелы
                    for ach_id in list(range(21, 23)) + list(range(61, 71)):
                        achievement_system.update_progress(ach_id, bullets_fired)

                    # 81–85: смешанные достижения, пусть идут от уровня
                    for ach_id in range(81, 86):
                        achievement_system.update_progress(ach_id, level_sys.current_level)

                    level_up, _, _ = level_sys.add_xp(xp)
                    user_level = level_sys.current_level
                    user_xp = level_sys.total_xp

                    if client:
                        client.send_command(
                            f"update_level&{user_id}&{level_sys.current_level}&{level_sys.total_xp}"
                        )

                    if level_up:
                        level_coins = 0  # Сбрасываем монеты уровня
                        donuts = create_donuts_for_level(level_sys)
                        stats = level_sys.get_level_stats()
                        spawn_delay = int(stats['spawn_delay'] * 1000)
                        if client:
                            client.send_command(
                                f"update_level&{user_id}&{level_sys.current_level}&{level_sys.total_xp}")
                    spawn_new_donut(level_sys, donuts)

            if ship.rect.colliderect(donut.rect):
                game_active = False
                save_all_data(client, user_id, currency, score, level_sys)

        if current_time - spawn_timer > spawn_delay:
            spawn_new_donut(level_sys, donuts)
            spawn_timer = current_time

        ship.draw()
        for bullet in bullets:
            bullet.draw()
        for donut in donuts:
            donut.draw()

    draw_stats_panel(level_sys, score, currency, level_coins)

    leader_icon = pygame.Rect(SCREEN_WIDTH - 218, 128, 58, 58)

    pygame.draw.rect(screen, (255, 241, 246), leader_icon, border_radius=20)
    pygame.draw.rect(screen, (190, 108, 145), leader_icon, 2, border_radius=20)

    gold = (212, 164, 92)

    pygame.draw.circle(screen, gold, (leader_icon.x + 29, leader_icon.y + 20), 10)

    pygame.draw.rect(
        screen,
        gold,
        (leader_icon.x + 24, leader_icon.y + 30, 10, 12),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        gold,
        (leader_icon.x + 18, leader_icon.y + 42, 22, 4),
        border_radius=2
    )

    # Красивая маленькая кнопка магазина
    shop_icon = pygame.Rect(SCREEN_WIDTH - 150, 128, 58, 58)
    pygame.draw.rect(screen, (255, 241, 246), shop_icon, border_radius=16)
    pygame.draw.rect(screen, (190, 108, 145), shop_icon, 2, border_radius=16)

    bag_body = pygame.Rect(shop_icon.x + 13, shop_icon.y + 21, 24, 20)

    pygame.draw.rect(
        screen,
        (164, 68, 112),
        bag_body,
        border_radius=6
    )

    pygame.draw.arc(
        screen,
        (164, 68, 112),
        (shop_icon.x + 17, shop_icon.y + 11, 16, 18),
        3.14,
        6.28,
        3
    )

    pygame.draw.circle(
        screen,
        (255, 241, 246),
        (shop_icon.x + 20, shop_icon.y + 27),
        2
    )

    pygame.draw.circle(
        screen,
        (255, 241, 246),
        (shop_icon.x + 30, shop_icon.y + 27),
        2
    )

    pygame.draw.rect(
        screen,
        (212, 164, 92),
        (shop_icon.x + 16, shop_icon.y + 34, 18, 3),
        border_radius=2
    )
    # Красивая маленькая кнопка достижений
    ach_icon = pygame.Rect(SCREEN_WIDTH - 82, 128, 58, 58)
    pygame.draw.rect(screen, (255, 241, 246), ach_icon, border_radius=16)
    pygame.draw.rect(screen, (190, 108, 145), ach_icon, 2, border_radius=16)

    cup = pygame.Rect(ach_icon.x + 19, ach_icon.y + 17, 16, 22)
    pygame.draw.rect(screen, (212, 164, 92), cup, border_radius=4)
    pygame.draw.arc(screen, (212, 164, 92), (ach_icon.x + 11, ach_icon.y + 19, 16, 16), 1.4, 4.8, 3)
    pygame.draw.arc(screen, (212, 164, 92), (ach_icon.x + 27, ach_icon.y + 19, 16, 16), -1.6, 1.7, 3)
    pygame.draw.rect(screen, (212, 164, 92), (ach_icon.x + 24, ach_icon.y + 39, 6, 7), border_radius=2)
    pygame.draw.rect(screen, (212, 164, 92), (ach_icon.x + 17, ach_icon.y + 45, 20, 4), border_radius=2)

    if not achievement_paused:
        achievement_system.draw_notifications(screen, font_small)

    if achievement_paused:
        achievement_window.draw()

    if shop_window.visible:
        shop_window.draw()

    if leaderboard_window.visible:
        leaderboard_window.draw()

    if shop_window.visible:
        shop_window.draw()

    if not game_active:
        game_over_result = menu.show_game_over_menu(score)
        save_all_data(client, user_id, currency, score, level_sys)
        user_score = score
        user_currency = currency
        user_level = level_sys.current_level
        user_xp = level_sys.total_xp
        if game_over_result == "restart":
            game_active = True
            score = user_score
            currency = user_currency
            level_coins = 0
            kills = 0
            bullets_fired = 0
            level_sys.reset()
            level_sys.current_level = user_level
            level_sys.total_xp = user_xp
            level_sys.current_xp = user_xp
            donuts = create_donuts_for_level(level_sys)
            bullets.clear()
            ship.center()
            spawn_timer = current_time
            stats = level_sys.get_level_stats()
            spawn_delay = int(stats['spawn_delay'] * 1000)
            shop_window.update_currency(currency)
        elif game_over_result == "menu":
            menu_result = menu.show_start_menu()
            if menu_result == "start":
                game_active = True
                score = user_score
                currency = user_currency
                level_coins = 0
                kills = 0
                bullets_fired = 0
                level_sys.reset()
                level_sys.current_level = user_level
                level_sys.total_xp = user_xp
                level_sys.current_xp = user_xp
                donuts = create_donuts_for_level(level_sys)
                bullets.clear()
                ship.center()
                spawn_timer = current_time
                stats = level_sys.get_level_stats()
                spawn_delay = int(stats['spawn_delay'] * 1000)
                shop_window.update_currency(currency)
            else:
                save_all_data(client, user_id, currency, score, level_sys)
                running = False
        elif game_over_result == "exit":
            save_all_data(client, user_id, currency, score, level_sys)
            running = False

    pygame.display.flip()

# Финальное сохранение перед выходом
save_all_data(client, user_id, currency, score, level_sys)
if client:
    client.socket.close()
pygame.quit()
sys.exit()
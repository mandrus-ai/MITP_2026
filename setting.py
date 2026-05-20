class settings():
    def __init__(self):
        # Настройки экрана
        self.screen_width = 1200
        self.screen_height = 700
        self.bg_color = (255, 255, 255)

        # Настройки корабля
        self.ship_speed_factor = 3.0
        self.Ship_limit = 3

        # Настройки пули
        self.bullet_speed_factor = 6
        self.bullet_width = 12
        self.bullet_height = 28
        self.bullet_color = (10, 10, 230)
        self.bullet_allowed = 40

        # Настройки пришельцев
        self.alien_speed_factor = 1.0
        self.alien_points = 10
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed_factor = 3.0
        self.bullet_speed_factor = 6
        self.alien_speed_factor = 1.0
        self.fleet_direction = 1
        self.alien_points = 10

    def increase_speed(self):
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
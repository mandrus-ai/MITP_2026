class LevelSystem:
    def __init__(self):
        self.current_level = 1
        self.current_xp = 0
        self.total_xp = 0

        # Таблица уровней (требуемый XP для каждого уровня)
        self.level_table = {
            1: (0, 100),
            2: (100, 150),
            3: (250, 200),
            4: (450, 250),
            5: (700, 300),
            6: (1000, 350),
            7: (1350, 400),
            8: (1750, 450),
            9: (2200, 500),
            10: (2700, 600),
        }

        self.max_level = 10

        # Характеристики уровней
        self.level_stats = {
            1: {"donut_count": 5, "donut_speed": 0.8, "spawn_delay": 3.5, "bonus_multiplier": 1.0},
            2: {"donut_count": 7, "donut_speed": 1.0, "spawn_delay": 3.2, "bonus_multiplier": 1.1},
            3: {"donut_count": 9, "donut_speed": 1.2, "spawn_delay": 3.0, "bonus_multiplier": 1.2},
            4: {"donut_count": 11, "donut_speed": 1.4, "spawn_delay": 2.8, "bonus_multiplier": 1.3},
            5: {"donut_count": 13, "donut_speed": 1.6, "spawn_delay": 2.6, "bonus_multiplier": 1.5},
            6: {"donut_count": 15, "donut_speed": 1.8, "spawn_delay": 2.4, "bonus_multiplier": 1.7},
            7: {"donut_count": 18, "donut_speed": 2.0, "spawn_delay": 2.2, "bonus_multiplier": 1.9},
            8: {"donut_count": 21, "donut_speed": 2.2, "spawn_delay": 2.0, "bonus_multiplier": 2.1},
            9: {"donut_count": 25, "donut_speed": 2.5, "spawn_delay": 1.8, "bonus_multiplier": 2.3},
            10: {"donut_count": 30, "donut_speed": 3.0, "spawn_delay": 1.5, "bonus_multiplier": 2.5},
        }

    def add_xp(self, amount):
        """Добавляет опыт и обновляет уровень"""
        self.current_xp += amount
        self.total_xp += amount

        level_up = False
        old_level = self.current_level

        while self.current_level < self.max_level:
            next_level_total, _ = self.level_table.get(self.current_level + 1, (0, 0))
            if self.total_xp >= next_level_total:
                self.current_level += 1
                level_up = True
            else:
                break

        if level_up:
            print(f"ПОЗДРАВЛЯЕМ! Уровень повышен с {old_level} до {self.current_level}!")

        return level_up, old_level, self.current_level

    def get_xp_for_next_level(self):
        if self.current_level >= self.max_level:
            return 0
        current_total, _ = self.level_table.get(self.current_level, (0, 0))
        next_total, _ = self.level_table.get(self.current_level + 1, (0, 0))
        return next_total - self.total_xp

    def get_current_level_xp(self):
        if self.current_level >= self.max_level:
            current_total, _ = self.level_table.get(self.max_level, (0, 0))
            return self.total_xp - current_total, 0
        current_total, _ = self.level_table.get(self.current_level, (0, 0))
        next_total, _ = self.level_table.get(self.current_level + 1, (0, 0))
        return self.total_xp - current_total, next_total - current_total

    def get_progress_percentage(self):
        current_xp, needed_xp = self.get_current_level_xp()
        if needed_xp == 0:
            return 100
        return int((current_xp / needed_xp) * 100)

    def get_level_bonus(self):
        stats = self.get_level_stats()
        return {
            'damage': 1 + (self.current_level - 1) * 0.05,
            'coins': stats['bonus_multiplier'],
            'points': stats['bonus_multiplier']
        }

    def get_level_stats(self, level=None):
        if level is None:
            level = self.current_level
        if level in self.level_stats:
            return self.level_stats[level]
        return self.level_stats[10]

    def get_level_title(self):
        titles = {
            1: "Новичок-пончик",
            2: "Сахарный разведчик",
            3: "Глазурный герой",
            4: "Посыпной воин",
            5: "Кремовый рыцарь",
            6: "Джемовый чемпион",
            7: "Шоколадный викинг",
            8: "Карамельный титан",
            9: "Мраморный легенд",
            10: "Пончижный император"
        }
        for level_max, title in sorted(titles.items(), reverse=True):
            if self.current_level >= level_max:
                return title
        return "Искатель сладостей"

    def get_level_color(self):
        if self.current_level >= 9:
            return (255, 215, 0)  # Золотой
        elif self.current_level >= 7:
            return (192, 192, 192)  # Серебряный
        elif self.current_level >= 5:
            return (205, 127, 50)  # Бронзовый
        else:
            return (255, 105, 180)  # Розовый

    def get_donut_count_for_level(self, level=None):
        stats = self.get_level_stats(level)
        return stats['donut_count']

    def get_donut_speed_for_level(self, level=None):
        stats = self.get_level_stats(level)
        return stats['donut_speed']

    def get_spawn_delay_for_level(self, level=None):
        stats = self.get_level_stats(level)
        return stats['spawn_delay'] * 1000

    def reset(self):
        """Сбрасывает систему уровней для нового игрока"""
        self.current_level = 1
        self.current_xp = 0
        self.total_xp = 0

    def load_from_db(self, level, xp, total_xp):
        """Загружает данные из базы данных"""
        self.current_level = level
        self.current_xp = xp
        self.total_xp = total_xp

    def get_data_for_db(self):
        """Возвращает данные для сохранения в базу"""
        return {
            "level": self.current_level,
            "xp": self.current_xp,
            "total_xp": self.total_xp
        }


# Глобальный экземпляр
_level_system = LevelSystem()


def get_level_system():
    return _level_system
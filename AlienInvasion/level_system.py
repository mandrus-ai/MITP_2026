class LevelSystem:
    def __init__(self):
        self.current_level = 1
        self.current_xp = 0
        self.total_xp = 0
        self.max_level = 100

        self.level_table = {}
        total_xp = 0

        for level in range(1, self.max_level + 1):
            xp_needed = 80 + level * 35
            self.level_table[level] = (total_xp, xp_needed)
            total_xp += xp_needed

        self.level_stats = {}

        for level in range(1, self.max_level + 1):
            self.level_stats[level] = {
                "donut_count": min(3 + level // 10, 12),
                "donut_speed": min(0.5 + level * 0.018, 2.5),
                "spawn_delay": max(4.0 - level * 0.018, 1.6),
                "bonus_multiplier": round(1.0 + level * 0.025, 2)
            }

    def add_xp(self, amount):
        self.total_xp += amount
        level_up = False
        old_level = self.current_level

        while self.current_level < self.max_level:
            next_level_total, _ = self.level_table[self.current_level + 1]

            if self.total_xp >= next_level_total:
                self.current_level += 1
                level_up = True
            else:
                break

        current_total, _ = self.level_table[self.current_level]
        self.current_xp = self.total_xp - current_total

        return level_up, old_level, self.current_level

    def get_current_level_xp(self):
        current_total, _ = self.level_table[self.current_level]

        if self.current_level >= self.max_level:
            return self.total_xp - current_total, 0

        next_total, _ = self.level_table[self.current_level + 1]
        return self.total_xp - current_total, next_total - current_total

    def get_progress_percentage(self):
        current_xp, needed_xp = self.get_current_level_xp()

        if needed_xp <= 0:
            return 100

        return max(0, min(100, int((current_xp / needed_xp) * 100)))

    def get_level_stats(self):
        return self.level_stats.get(self.current_level, self.level_stats[self.max_level])

    def get_level_title(self):
        titles = {
            1: "Сахарный новичок",
            5: "Ванильный искатель",
            10: "Карамельный охотник",
            15: "Клубничный герой",
            20: "Шоколадный защитник",
            25: "Марципановый рыцарь",
            30: "Зефирный маг",
            40: "Леденцовый мастер",
            50: "Пончик-сенсей",
            60: "Кремовый чемпион",
            70: "Медовый страж",
            80: "Глазурный король",
            90: "Сказочный кондитер",
            100: "Император сладостей"
        }

        for level, title in sorted(titles.items(), reverse=True):
            if self.current_level >= level:
                return title

        return "Искатель сладостей"

    def reset(self):
        self.current_level = 1
        self.current_xp = 0
        self.total_xp = 0
# Уменьшенный список достижений игры.
# Оставлено 40 достижений без сильных повторов.

ACHIEVEMENTS = {
    1: {"name": "Первый пончик", "description": "Уничтожьте первого пончика", "max_progress": 1, "category": "combat"},
    2: {"name": "Карамельный новичок", "description": "Уничтожьте 10 пончиков", "max_progress": 10, "category": "combat"},
    3: {"name": "Сладкий охотник", "description": "Уничтожьте 25 пончиков", "max_progress": 25, "category": "combat"},
    4: {"name": "Глазурный защитник", "description": "Уничтожьте 50 пончиков", "max_progress": 50, "category": "combat"},
    5: {"name": "Пончикоборец", "description": "Уничтожьте 100 пончиков", "max_progress": 100, "category": "combat"},
    6: {"name": "Маршмеллоу-воин", "description": "Уничтожьте 250 пончиков", "max_progress": 250, "category": "combat"},
    7: {"name": "Легенда сладостей", "description": "Уничтожьте 500 пончиков", "max_progress": 500, "category": "combat"},

    8: {"name": "Первые очки", "description": "Наберите 100 очков", "max_progress": 100, "category": "score"},
    9: {"name": "Сахарная тысяча", "description": "Наберите 1000 очков", "max_progress": 1000, "category": "score"},
    10: {"name": "Клубничный рекорд", "description": "Наберите 2500 очков", "max_progress": 2500, "category": "score"},
    11: {"name": "Золотой результат", "description": "Наберите 5000 очков", "max_progress": 5000, "category": "score"},
    12: {"name": "Большой рекорд", "description": "Наберите 10000 очков", "max_progress": 10000, "category": "score"},

    13: {"name": "Второй уровень", "description": "Достигните 2 уровня", "max_progress": 2, "category": "level"},
    14: {"name": "Ванильный путь", "description": "Достигните 5 уровня", "max_progress": 5, "category": "level"},
    15: {"name": "Карамельный герой", "description": "Достигните 10 уровня", "max_progress": 10, "category": "level"},
    16: {"name": "Сливочный мастер", "description": "Достигните 15 уровня", "max_progress": 15, "category": "level"},
    17: {"name": "Единобожик-профи", "description": "Достигните 25 уровня", "max_progress": 25, "category": "level"},

    18: {"name": "Первые монеты", "description": "Соберите 10 монет", "max_progress": 10, "category": "economy"},
    19: {"name": "Сладкий кошелёк", "description": "Соберите 100 монет", "max_progress": 100, "category": "economy"},
    20: {"name": "Карамельная казна", "description": "Соберите 500 монет", "max_progress": 500, "category": "economy"},
    21: {"name": "Золотой запас", "description": "Соберите 1000 монет", "max_progress": 1000, "category": "economy"},
    22: {"name": "Богатый единорог", "description": "Соберите 2500 монет", "max_progress": 2500, "category": "economy"},

    23: {"name": "Первый выстрел", "description": "Сделайте первый выстрел", "max_progress": 1, "category": "shooting"},
    24: {"name": "Меткий стрелок", "description": "Сделайте 50 выстрелов", "max_progress": 50, "category": "shooting"},
    25: {"name": "Сахарная очередь", "description": "Сделайте 100 выстрелов", "max_progress": 100, "category": "shooting"},
    26: {"name": "Глазурный снайпер", "description": "Сделайте 250 выстрелов", "max_progress": 250, "category": "shooting"},
    27: {"name": "Пулемёт с джемом", "description": "Сделайте 500 выстрелов", "max_progress": 500, "category": "shooting"},

    28: {"name": "Первая покупка", "description": "Купите первый предмет", "max_progress": 1, "category": "shop"},
    29: {"name": "Новый образ", "description": "Выберите новый скин", "max_progress": 1, "category": "shop"},
    30: {"name": "Новый фон", "description": "Выберите новый фон", "max_progress": 1, "category": "shop"},

    31: {"name": "Без промаха", "description": "Попадите по пончику без промаха", "max_progress": 1, "category": "special"},
    32: {"name": "Три пончика подряд", "description": "Уничтожьте 3 пончика подряд", "max_progress": 3, "category": "combo"},
    33: {"name": "Комбо из пяти", "description": "Уничтожьте 5 пончиков подряд", "max_progress": 5, "category": "combo"},
    34: {"name": "Десять подряд", "description": "Уничтожьте 10 пончиков подряд", "max_progress": 10, "category": "combo"},

    35: {"name": "Выживший", "description": "Продержитесь одну волну", "max_progress": 1, "category": "survival"},
    36: {"name": "Долгая игра", "description": "Играйте 5 минут", "max_progress": 300, "category": "survival"},
    37: {"name": "Упорный игрок", "description": "Играйте 10 минут", "max_progress": 600, "category": "survival"},

    38: {"name": "Первый рекорд дня", "description": "Побейте свой рекорд", "max_progress": 1, "category": "record"},
    39: {"name": "Почти чемпион", "description": "Наберите 7500 очков", "max_progress": 7500, "category": "score"},
    40: {"name": "Чемпион Единобожика", "description": "Наберите 15000 очков", "max_progress": 15000, "category": "score"},
}


def get_achievement_by_id(achievement_id):
    return ACHIEVEMENTS.get(achievement_id)


def get_all_achievements():
    return list(ACHIEVEMENTS.values())


def get_achievements_by_category(category):
    return [
        achievement
        for achievement in ACHIEVEMENTS.values()
        if achievement.get("category") == category
    ]

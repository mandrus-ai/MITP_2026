class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 700
        self.ship_speed = 5
        self.bullet_speed = 8

        # Старая палитра оставлена, чтобы существующий код не ломался
        self.PRIMARY_PINK = (255, 200, 220)
        self.SECONDARY_PINK = (255, 220, 235)
        self.DARK_PINK = (255, 150, 180)
        self.HOT_PINK = (255, 120, 160)
        self.SOFT_PINK = (255, 235, 245)
        self.LIGHT_PINK = (255, 245, 250)

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GOLD = (255, 215, 0)
        self.PURPLE = (125, 95, 255)
        self.RED = (255, 88, 88)
        self.GRAY = (145, 153, 175)
        self.DARK_GRAY = (85, 92, 112)
        self.ORANGE = (255, 173, 74)
        self.GREEN = (64, 205, 130)
        self.TEAL = (70, 210, 205)

        # PREMIUM ROSE UI
        self.UI_BG = (18, 12, 20)
        self.UI_BG_2 = (34, 20, 34)

        self.UI_PANEL = (255, 241, 246)
        self.UI_PANEL_2 = (250, 225, 236)

        self.UI_CARD = (255, 250, 252)
        self.UI_CARD_HOVER = (255, 238, 246)

        self.UI_BORDER = (190, 108, 145)

        self.UI_ACCENT = (164, 68, 112)
        self.UI_ACCENT_2 = (212, 164, 92)

        self.UI_TEXT = (62, 32, 50)
        self.UI_TEXT_DARK = (128, 82, 108)

        self.UI_SUCCESS = (164, 68, 112)
        self.UI_WARNING = (212, 164, 92)
        self.UI_DANGER = (180, 72, 96)

        self.UI_SHADOW = (18, 8, 16)

settings = Settings()

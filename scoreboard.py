import pygame.font
from pygame.sprite import Group

from ship import ship

class Scoreboard():
    "" "Класс, показывающий информацию о счете" ""

    def __init__(self,ai_settings,screen,stats):
        "" "Инициализировать атрибуты, участвующие в оценке" ""
        self.screen =screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats =stats


        # Настройки шрифта, используемые при отображении информации о счете
        self.text_color =(30,30,30)
        self.font = pygame.font.SysFont(None,48)

        # Подготовить изображение с наивысшей оценкой и текущей оценкой
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        #self.prep_Ships()

    def prep_score(self):
        "" "Преобразование партитуры в визуализированное изображение" ""
        rounded_score = int(round(self.stats.score,-1))
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.ai_settings.bg_color)

        # Поместите счет в верхнем правом углу экрана
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        "" "Преобразование наивысшего балла в отображаемое изображение" ""
        high_score = int(round(self.stats.high_score,-1))
        high_score_str =  "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str,True,self.text_color,self.ai_settings.bg_color)

        # Поместите наивысший балл в верхнем центре экрана
        self.high_score_rect =self.high_score_image.get_rect()
        self.high_score_rect.centerx =self.screen_rect.centerx
        self.high_score_rect.top =self.score_rect.top

    def prep_level(self):
        "" "Преобразовать уровень в отображаемое изображение" ""
        self.level_image =self.font.render(str(self.stats.level),True,self.text_color,self.ai_settings.bg_color)

        # Поставить уровень ниже партитуры
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10



    def show_score(self):
        "" "Показать космический корабль и набрать очки на экране" ""
        self.screen.blit(self.score_image,self.score_rect)
        self.screen.blit(self.high_score_image,self.high_score_rect)
        self.screen.blit(self.level_image,self.level_rect)
       # self.Ships.draw(self.screen)
"""
    def prep_Ships(self):
             Покажите, сколько космических кораблей осталось
        self.Ships = Group()
        for Ship_number in range(self.stats.Ship_left):
            Ship = ship(self.ai_settings,self.screen)
            Ship.rect.x =10 + Ship_number*Ship.rect.width
            Ship.rect.y = 10
            self.Ships.add(Ship)
                                           """

import pygame
from settings import settings

def draw_rounded_rect(surface, color, rect, radius=10):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.is_hover = False

    def draw(self, screen):
        color = self.hover_color if self.is_hover else self.color

        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (20, 8, 18, 90), shadow.get_rect(), border_radius=18)
        screen.blit(shadow, (self.rect.x + 4, self.rect.y + 6))

        pygame.draw.rect(screen, color, self.rect, border_radius=18)
        pygame.draw.rect(screen, (255, 205, 225), self.rect, 2, border_radius=18)

        text_surf = self.font.render(self.text, True, (255, 250, 252))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
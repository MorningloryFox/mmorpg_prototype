# ui.py
import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, callback, image=None, hover_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 36)
        self.text_surf = self.font.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        
        self.image = image
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = hover_image
        if self.hover_image:
            self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
        
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        current_image = self.image
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.hover_image:
                current_image = self.hover_image
        
        if current_image:
            screen.blit(current_image, self.rect.topleft)
        else:
            # Fallback to drawing a rectangle if no image is provided
            pygame.draw.rect(screen, GREEN, self.rect)
        
        screen.blit(self.text_surf, self.text_rect)

class InputBox:
    def __init__(self, x, y, width, height, is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = ''
        self.font = pygame.font.Font(None, 32)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        if self.is_password:
            txt_surface = self.font.render('*' * len(self.text), True, self.color)
        else:
            txt_surface = self.font.render(self.text, True, self.color)
        width = max(200, txt_surface.get_width()+10)
        self.rect.w = width
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))

class Label:
    def __init__(self, x, y, text, font_size=36, color=WHITE):
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.color = color
        self.x = x
        self.y = y

    def draw(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, text_rect)
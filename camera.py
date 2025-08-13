# camera.py
import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limitar a rolagem aos limites do mapa
        x = min(0, x)  # Limite esquerdo
        y = min(0, y)  # Limite superior
        x = max(-(self.width - SCREEN_WIDTH), x)  # Limite direito
        y = max(-(self.height - SCREEN_HEIGHT), y) # Limite inferior

        self.camera = pygame.Rect(x, y, self.width, self.height)

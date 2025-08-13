# resource.py
import pygame
from settings import *

class Resource(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (10, 10), 10)
        self.rect = self.image.get_rect(topleft=(x, y))

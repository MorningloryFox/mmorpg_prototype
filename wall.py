# wall.py
import pygame
from settings import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, image=None):
        super().__init__()
        if image:
            self.image = image
        else:
            # Default brown wall if no image is provided
            self.image = pygame.Surface((50, 50))
            self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

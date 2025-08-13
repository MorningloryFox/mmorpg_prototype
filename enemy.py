# enemy.py
import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/Bot/Bot Wheel/move with FX.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.speed = 2
        self.direction = 1 # 1 for right, -1 for left
        self.move_counter = 0
        self.move_range = 100 # Pixels to move before turning

    def update(self):
        # Move back and forth
        self.rect.x += self.speed * self.direction
        self.move_counter += self.speed
        
        if self.move_counter > self.move_range:
            self.direction *= -1 # Turn around
            self.move_counter = 0
            # Flip the image
            self.image = pygame.transform.flip(self.image, True, False)

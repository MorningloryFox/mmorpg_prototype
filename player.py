# player.py
import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Carregar sprites de animação
        self.idle_image = pygame.image.load("data/Bot/Bot Wheel/static idle.png").convert_alpha()
        self.walk_image_original = pygame.image.load("data/Bot/Bot Wheel/move with FX.png").convert_alpha()
        
        self.image = self.idle_image
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 5
        self.name = "Player"
        self.health = 100
        self.max_health = 100
        self.inventory = {}
        self.max_inventory_slots = 10
        self.moving = False
        self.direction = "right"

    def move(self, keys, walls, enemies):
        self.moving = False
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = "right"
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        if dx != 0 or dy != 0:
            self.moving = True

        # Move in x and check for collisions
        self.rect.x += dx
        for sprite in walls.sprites() + enemies.sprites():
            if self.rect.colliderect(sprite.rect):
                if dx > 0: # Moving right
                    self.rect.right = sprite.rect.left
                if dx < 0: # Moving left
                    self.rect.left = sprite.rect.right
        
        # Move in y and check for collisions
        self.rect.y += dy
        for sprite in walls.sprites() + enemies.sprites():
            if self.rect.colliderect(sprite.rect):
                if dy > 0: # Moving down
                    self.rect.bottom = sprite.rect.top
                if dy < 0: # Moving up
                    self.rect.top = sprite.rect.bottom

    def update_animation(self):
        if not self.moving:
            self.image = self.idle_image
        else:
            walk_image = self.walk_image_original
            if self.direction == 'left':
                self.image = pygame.transform.flip(walk_image, True, False)
            else:
                self.image = walk_image

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def collect_resources(self, resources):
        for resource in resources.copy():
            if self.rect.colliderect(resource.rect):
                resource.kill() # Remove from all groups
                resource_type = "alien_resource"
                if resource_type in self.inventory:
                    self.inventory[resource_type] += 1
                else:
                    if len(self.inventory) < self.max_inventory_slots:
                        self.inventory[resource_type] = 1

# enemy.py
import pygame
import random
from settings import *
from item import ITEM_DEFS

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/Bot/Bot Wheel/move with FX.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.speed = 2
        self.direction = 1 # 1 for right, -1 for left
        self.move_counter = 0
        self.move_range = 100 # Pixels to move before turning
        self.health = 50
        self.attack = 8
        self.defense = 2
        self.hit_timer = 0
        try:
            self.hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        except pygame.error:
            self.hit_sound = None
        self.drops = {"alien_resource": 0.2}

    def update(self):
        # Move back and forth
        self.rect.x += self.speed * self.direction
        self.move_counter += self.speed

        if self.move_counter > self.move_range:
            self.direction *= -1 # Turn around
            self.move_counter = 0
            # Flip the image
            self.image = pygame.transform.flip(self.image, True, False)

        if self.hit_timer > 0:
            self.hit_timer -= 1
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def take_damage(self, dmg, attacker=None):
        self.health -= dmg
        if self.hit_sound:
            self.hit_sound.play()
        self.hit_timer = 5
        if self.health <= 0:
            self.kill()
            if attacker:
                self.drop_loot(attacker)

    def drop_loot(self, player):
        for item_id, chance in self.drops.items():
            luck_bonus = 1 + player.luck * 0.5 / 100
            if random.random() < chance * luck_bonus:
                item_def = ITEM_DEFS.get(item_id)
                if item_def:
                    inv = player.inventory.setdefault(item_id, {'item': item_def, 'qty': 0})
                    inv['qty'] += 1

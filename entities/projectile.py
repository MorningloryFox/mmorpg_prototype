import pygame


class Projectile(pygame.sprite.Sprite):
    """Simple horizontal projectile that deals damage on impact."""

    def __init__(self, x, y, direction, walls, enemies, damage=10, speed=10):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed if direction == "right" else -speed
        self.damage = damage
        self.walls = walls
        self.enemies = enemies

    def update(self):
        self.rect.x += self.speed

        for wall in list(self.walls):
            if self.rect.colliderect(wall.rect):
                self.kill()
                return
        for enemy in list(self.enemies):
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(max(0, self.damage - enemy.defense))
                self.kill()
                return

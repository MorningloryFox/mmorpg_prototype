import pygame


class Projectile(pygame.sprite.Sprite):
    """Simple projectile that can animate and show an impact sprite."""

    def __init__(
        self,
        x,
        y,
        direction,
        walls,
        enemies,
        damage=10,
        speed=10,
        owner=None,
        sprites=None,
        impact_sprite=None,
    ):
        super().__init__()
        if sprites:
            self.images = [pygame.image.load(p).convert_alpha() for p in sprites]
            self.image = self.images[0]
        else:
            self.images = []
            self.image = pygame.Surface((10, 4))
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed if direction == "right" else -speed
        self.damage = damage
        self.owner = owner
        self.walls = walls
        self.enemies = enemies
        self.anim_index = 0
        self.frame_timer = 0
        self.impact_image = (
            pygame.image.load(impact_sprite).convert_alpha() if impact_sprite else None
        )
        self.collided = False
        self.collision_timer = 0

    def update(self):
        if not self.collided:
            self.rect.x += self.speed
            if self.images:
                self.frame_timer = (self.frame_timer + 1) % 10
                if self.frame_timer == 0 and len(self.images) > 1:
                    self.anim_index = (self.anim_index + 1) % len(self.images)
                    self.image = self.images[self.anim_index]
            for wall in list(self.walls):
                if self.rect.colliderect(wall.rect):
                    self._impact()
                    return
            for enemy in list(self.enemies):
                if self.rect.colliderect(enemy.rect):
                    enemy.take_damage(max(0, self.damage - enemy.defense), self.owner)
                    self._impact()
                    return
        else:
            self.collision_timer -= 1
            if self.collision_timer <= 0:
                self.kill()

    def _impact(self):
        if self.impact_image:
            self.image = self.impact_image
            self.speed = 0
            self.collided = True
            self.collision_timer = 5
        else:
            self.kill()

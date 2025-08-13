import pygame
from .common import Label


class StatusUI:
    """Display player stats and allow attribute allocation."""

    def __init__(self, player):
        self.player = player
        self.active = False
        self.panel = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel01.png").convert_alpha()
        self.panel = pygame.transform.scale(self.panel, (300, 300))

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN and self.player.attribute_points > 0:
            if event.key == pygame.K_1:
                self.player.allocate_attribute('strength')
            elif event.key == pygame.K_2:
                self.player.allocate_attribute('dexterity')
            elif event.key == pygame.K_3:
                self.player.allocate_attribute('constitution')
            elif event.key == pygame.K_4:
                self.player.allocate_attribute('intelligence')
            elif event.key == pygame.K_5:
                self.player.allocate_attribute('luck')
            elif event.key == pygame.K_6:
                self.player.allocate_attribute('crit')

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (50, 50))
        font = pygame.font.Font(None, 24)
        stats = [
            ("STR", int(self.player.strength)),
            ("DEX", int(self.player.dexterity)),
            ("CON", int(self.player.constitution)),
            ("INT", int(self.player.intelligence)),
            ("LCK", int(self.player.luck)),
            ("CRT", int(self.player.crit)),
        ]
        for i, (name, val) in enumerate(stats):
            text = font.render(f"{name}: {val}", True, (255, 255, 255))
            screen.blit(text, (80, 80 + i * 20))
        pts = font.render(f"Points: {self.player.attribute_points}", True, (255, 255, 0))
        screen.blit(pts, (80, 80 + len(stats) * 20))
        # Draw equipment icons
        for i, (slot, item) in enumerate(self.player.equipment.items()):
            try:
                icon = pygame.image.load(item.icon).convert_alpha()
                icon = pygame.transform.scale(icon, (40, 40))
                screen.blit(icon, (200, 80 + i * 45))
            except Exception:
                pass
        sprite = pygame.transform.scale(self.player.image, (64, 64))
        screen.blit(sprite, (120, 200))

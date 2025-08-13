import pygame
from .common import Button, InputBox, Label
from projectiles import PROJECTILE_DEFS, save_projectiles


class ProjectileEditor:
    """Admin tool to create or edit projectile definitions."""

    def __init__(self):
        self.active = False
        self.panel = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(self.panel, (300, 360))
        self.id_input = InputBox(120, 100, 150, 30)
        self.sprite_input = InputBox(120, 140, 150, 30)
        self.impact_input = InputBox(120, 180, 150, 30)
        self.speed_input = InputBox(120, 220, 150, 30)
        self.damage_input = InputBox(120, 260, 150, 30)
        self.save_button = Button(120, 300, 80, 30, "Save", self.save)
        self.labels = [
            Label(80, 100, "ID", font_size=20),
            Label(80, 140, "Sprites", font_size=20),
            Label(60, 180, "Impact", font_size=20),
            Label(70, 220, "Speed", font_size=20),
            Label(55, 260, "Damage", font_size=20),
        ]

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return
        for el in [
            self.id_input,
            self.sprite_input,
            self.impact_input,
            self.speed_input,
            self.damage_input,
            self.save_button,
        ]:
            if isinstance(el, (Button, InputBox)):
                el.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (250, 150))
        for label in self.labels:
            label.draw(screen)
        self.id_input.draw(screen)
        self.sprite_input.draw(screen)
        self.impact_input.draw(screen)
        self.speed_input.draw(screen)
        self.damage_input.draw(screen)
        self.save_button.draw(screen)

    def save(self):
        pid = self.id_input.text.strip()
        sprites = [s.strip() for s in self.sprite_input.text.split(',') if s.strip()]
        impact = self.impact_input.text.strip() or None
        try:
            speed = int(self.speed_input.text)
        except ValueError:
            speed = 10
        try:
            damage = int(self.damage_input.text)
        except ValueError:
            damage = 0
        if pid:
            PROJECTILE_DEFS[pid] = {
                "sprites": sprites,
                "impact": impact,
                "speed": speed,
                "damage": damage,
            }
            save_projectiles()
            self.id_input.text = ""
            self.sprite_input.text = ""
            self.impact_input.text = ""
            self.speed_input.text = ""
            self.damage_input.text = ""

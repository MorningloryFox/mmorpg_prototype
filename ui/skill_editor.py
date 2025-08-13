import pygame
from .common import Button, InputBox, Label
from skills import SKILL_DEFS, save_skills


class SkillEditor:
    """Simple admin tool to create new skills in-game."""

    def __init__(self):
        self.active = False
        self.panel = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png").convert_alpha()
        self.panel = pygame.transform.scale(self.panel, (300, 300))
        self.name_input = InputBox(120, 100, 150, 30)
        self.kind_input = InputBox(120, 140, 150, 30)
        self.power_input = InputBox(120, 180, 150, 30)
        self.save_button = Button(120, 220, 80, 30, 'Save', self.save)
        self.labels = [
            Label(80, 100, 'Name', font_size=20),
            Label(80, 140, 'Kind', font_size=20),
            Label(80, 180, 'Power', font_size=20),
        ]

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return
        for el in [self.name_input, self.kind_input, self.power_input, self.save_button]:
            if isinstance(el, (Button, InputBox)):
                el.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (250, 150))
        for label in self.labels:
            label.draw(screen)
        self.name_input.draw(screen)
        self.kind_input.draw(screen)
        self.power_input.draw(screen)
        self.save_button.draw(screen)

    def save(self):
        name = self.name_input.text
        kind = self.kind_input.text or 'damage'
        try:
            power = int(self.power_input.text)
        except ValueError:
            power = 0
        if name:
            SKILL_DEFS[name] = {"kind": kind, "power": power, "cooldown": 60}
            save_skills()
            self.name_input.text = ''
            self.kind_input.text = ''
            self.power_input.text = ''

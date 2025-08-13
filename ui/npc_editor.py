import pygame
from .common import Button, InputBox, Label
from npc import NPC_DEFS, save_npcs


class NPCEditor:
    """Admin tool to create or edit NPC definitions."""

    def __init__(self):
        self.active = False
        panel_img = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(panel_img, (400, 600))
        self.fields = [
            ("id", "ID"),
            ("name", "Name"),
            ("title", "Title"),
            ("sprite", "Sprite"),
            ("walk", "Walk"),
            ("hp", "HP"),
            ("mp", "MP"),
            ("attack", "Attack"),
            ("defense", "Defense"),
            ("speed", "Speed"),
            ("type", "Type"),
            ("vision", "Vision"),
            ("aggressive", "Aggro"),
            ("flee", "Flee"),
        ]
        self.inputs = {}
        self.labels = []
        start_y = 90
        for i, (key, label) in enumerate(self.fields):
            y = start_y + i * 30
            self.inputs[key] = InputBox(260, y, 120, 25)
            self.labels.append(Label(160, y + 10, label, font_size=20))
        self.save_button = Button(260, start_y + len(self.fields) * 30 + 20, 100, 30, "Save", self.save)

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return
        for box in self.inputs.values():
            box.handle_event(event)
        self.save_button.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (200, 60))
        for label in self.labels:
            label.draw(screen)
        for box in self.inputs.values():
            box.draw(screen)
        self.save_button.draw(screen)

    def save(self):
        npc_id = self.inputs["id"].text.strip()
        if not npc_id:
            return
        try:
            data = {
                "name": self.inputs["name"].text.strip(),
                "title": self.inputs["title"].text.strip(),
                "sprite": self.inputs["sprite"].text.strip(),
                "walk": self.inputs["walk"].text.strip(),
                "hp": int(self.inputs["hp"].text or 0),
                "mp": int(self.inputs["mp"].text or 0),
                "attack": int(self.inputs["attack"].text or 0),
                "defense": int(self.inputs["defense"].text or 0),
                "speed": int(self.inputs["speed"].text or 0),
                "type": self.inputs["type"].text.strip() or "NPC",
                "vision": int(self.inputs["vision"].text or 0),
                "aggressive": self.inputs["aggressive"].text.lower() in ("1", "true", "yes"),
                "flee": self.inputs["flee"].text.lower() in ("1", "true", "yes"),
            }
        except ValueError:
            return
        NPC_DEFS[npc_id] = data
        save_npcs()
        for box in self.inputs.values():
            box.text = ""

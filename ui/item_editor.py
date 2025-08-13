import pygame
from .common import Button, InputBox, Label
from item import ITEM_DEFS, Item, save_items
from settings import WHITE


class ItemEditor:
    """Admin tool to manage item definitions."""

    def __init__(self):
        self.active = False
        panel_img = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(panel_img, (400, 600))
        self.font = pygame.font.Font(None, 24)
        self.inputs = {}
        self.labels = []
        self.fields = [
            ("id", "ID"),
            ("name", "Name"),
            ("description", "Desc"),
            ("type", "Type"),
            ("icon", "Icon"),
            ("attack", "Atk"),
            ("defense", "Def"),
            ("strength", "Str"),
            ("agility", "Agi"),
            ("hp", "HP"),
        ]
        start_y = 220
        for i, (key, label) in enumerate(self.fields):
            y = start_y + i * 30
            self.inputs[key] = InputBox(260, y, 120, 25)
            self.labels.append(Label(160, y + 10, label, font_size=20))
        self.load_button = Button(260, 180, 120, 30, "Load", self.load)
        self.save_button = Button(260, start_y + len(self.fields) * 30 + 20, 120, 30, "Save", self.save)
        self.delete_button = Button(260, start_y + len(self.fields) * 30 + 60, 120, 30, "Delete", self.delete)

    def toggle(self):
        self.active = not self.active

    def load(self):
        item_id = self.inputs["id"].text.strip()
        item = ITEM_DEFS.get(item_id)
        if not item:
            return
        self.inputs["name"].text = item.name
        self.inputs["description"].text = item.description
        self.inputs["type"].text = item.type
        self.inputs["icon"].text = item.icon
        self.inputs["attack"].text = str(item.attack)
        self.inputs["defense"].text = str(item.defense)
        self.inputs["strength"].text = str(item.strength)
        self.inputs["agility"].text = str(item.agility)
        self.inputs["hp"].text = str(item.hp)

    def save(self):
        item_id = self.inputs["id"].text.strip()
        if not item_id:
            return
        try:
            data = {
                "name": self.inputs["name"].text.strip(),
                "description": self.inputs["description"].text.strip(),
                "type": self.inputs["type"].text.strip(),
                "icon": self.inputs["icon"].text.strip(),
                "attack": int(self.inputs["attack"].text or 0),
                "defense": int(self.inputs["defense"].text or 0),
                "strength": int(self.inputs["strength"].text or 0),
                "agility": int(self.inputs["agility"].text or 0),
                "hp": int(self.inputs["hp"].text or 0),
            }
        except ValueError:
            return
        ITEM_DEFS[item_id] = Item(id=item_id, **data)
        save_items()

    def delete(self):
        item_id = self.inputs["id"].text.strip()
        if item_id in ITEM_DEFS:
            del ITEM_DEFS[item_id]
            save_items()

    def handle_event(self, event):
        if not self.active:
            return
        for box in self.inputs.values():
            box.handle_event(event)
        for btn in [self.load_button, self.save_button, self.delete_button]:
            btn.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (200, 60))
        # catalog
        y = 100
        for item_id, item in ITEM_DEFS.items():
            text = self.font.render(f"{item_id}: {item.name}", True, WHITE)
            screen.blit(text, (220, y))
            y += 20
            if y > 170:
                break
        for label in self.labels:
            label.draw(screen)
        for box in self.inputs.values():
            box.draw(screen)
        for btn in [self.load_button, self.save_button, self.delete_button]:
            btn.draw(screen)

import pygame
from .common import Button
from dialogue import DIALOGUES
from settings import WHITE


class DialogueUI:
    """Display dialogue with NPCs."""

    def __init__(self):
        self.active = False
        panel_img = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(panel_img, (400, 200))
        self.font = pygame.font.Font(None, 24)
        self.npc_id = None
        self.node_id = None
        self.buttons = []

    def start(self, npc_id):
        data = DIALOGUES.get(npc_id)
        if not data:
            return
        self.npc_id = npc_id
        self.node_id = data.get("start")
        self.active = True
        self._build_buttons()

    def _build_buttons(self):
        self.buttons.clear()
        if not self.active:
            return
        node = DIALOGUES[self.npc_id]["nodes"][self.node_id]
        for i, opt in enumerate(node.get("options", [])):
            btn = Button(220, 360 + i * 40, 360, 30, opt["text"], lambda o=opt: self._choose(o))
            self.buttons.append(btn)

    def _choose(self, option):
        next_id = option.get("next")
        if next_id:
            self.node_id = next_id
            self._build_buttons()
        else:
            self.active = False

    def handle_event(self, event):
        if not self.active:
            return
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (200, 320))
        node = DIALOGUES[self.npc_id]["nodes"].get(self.node_id, {})
        text = node.get("text", "")
        surf = self.font.render(text, True, WHITE)
        screen.blit(surf, (220, 340))
        for btn in self.buttons:
            btn.draw(screen)

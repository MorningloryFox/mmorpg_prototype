import pygame
from .common import Button, InputBox, Label
from dialogue import DIALOGUES, save_dialogues
from settings import WHITE


class DialogueEditor:
    """Admin tool to manage NPC dialogue trees."""

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
            ("npc", "NPC ID"),
            ("node", "Node ID"),
            ("text", "Text"),
            ("options", "Options"),
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
        npc_id = self.inputs["npc"].text.strip()
        node_id = self.inputs["node"].text.strip()
        npc = DIALOGUES.get(npc_id, {})
        node = npc.get("nodes", {}).get(node_id)
        if not node:
            return
        self.inputs["text"].text = node.get("text", "")
        opts = []
        for opt in node.get("options", []):
            nxt = opt.get("next") or ""
            opts.append(f"{opt.get('text', '')}>{nxt}")
        self.inputs["options"].text = ";".join(opts)

    def save(self):
        npc_id = self.inputs["npc"].text.strip()
        node_id = self.inputs["node"].text.strip()
        if not npc_id or not node_id:
            return
        npc = DIALOGUES.setdefault(npc_id, {"start": node_id, "nodes": {}})
        text = self.inputs["text"].text.strip()
        options_str = self.inputs["options"].text.strip()
        options = []
        if options_str:
            for part in options_str.split(";"):
                if ">" in part:
                    t, n = part.split(">", 1)
                    options.append({"text": t.strip(), "next": n.strip() or None})
        npc["nodes"][node_id] = {"text": text, "options": options}
        save_dialogues()

    def delete(self):
        npc_id = self.inputs["npc"].text.strip()
        node_id = self.inputs["node"].text.strip()
        npc = DIALOGUES.get(npc_id)
        if npc and node_id in npc.get("nodes", {}):
            del npc["nodes"][node_id]
            save_dialogues()

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
        npc_id = self.inputs["npc"].text.strip()
        y = 100
        npc = DIALOGUES.get(npc_id)
        if npc:
            for nid in npc["nodes"].keys():
                text = self.font.render(nid, True, WHITE)
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

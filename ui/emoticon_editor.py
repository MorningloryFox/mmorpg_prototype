import pygame
from .common import Button, InputBox, Label
from emoticons import EMOTICON_DEFS, save_emoticons


class EmoticonEditor:
    """Simple admin tool to map chat codes to images."""

    def __init__(self, chat):
        self.chat = chat
        self.active = False
        self.panel = pygame.image.load(
            "data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png"
        ).convert_alpha()
        self.panel = pygame.transform.scale(self.panel, (320, 320))
        self.code_input = InputBox(160, 120, 140, 30)
        self.path_input = InputBox(160, 160, 140, 30)
        self.save_button = Button(160, 200, 80, 30, "Save", self.save)
        self.font = pygame.font.Font(None, 20)
        self.labels = [
            Label(120, 120, "Code", font_size=20),
            Label(120, 160, "Image", font_size=20),
        ]

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return
        for el in [self.code_input, self.path_input, self.save_button]:
            el.handle_event(event)

    def draw(self, screen):
        if not self.active:
            return
        screen.blit(self.panel, (230, 130))
        for label in self.labels:
            label.draw(screen)
        self.code_input.draw(screen)
        self.path_input.draw(screen)
        self.save_button.draw(screen)
        y = 240
        for code, path in EMOTICON_DEFS.items():
            txt = self.font.render(f"{code}: {path}", True, (255, 255, 255))
            screen.blit(txt, (240, y))
            y += 20

    def save(self):
        code = self.code_input.text.strip()
        path = self.path_input.text.strip()
        if code and path:
            EMOTICON_DEFS[code] = path
            save_emoticons()
            self.chat.load_emoticons()
            self.code_input.text = ""
            self.path_input.text = ""

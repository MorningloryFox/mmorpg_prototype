import pygame
from .common import InputBox
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from emoticons import load_surfaces


class Chat:
    """Simple chat box for displaying and sending messages."""

    def __init__(self, max_messages: int = 6):
        self.font = pygame.font.Font(None, 24)
        # each message is a list of ('text', str) or ('img', Surface)
        self.messages: list[list[tuple[str, object]]] = []
        self.max_messages = max_messages
        self.emotes = load_surfaces()
        # input box positioned at bottom-left
        self.input_box = InputBox(10, SCREEN_HEIGHT - 30, 300, 20)
        self.active = False

    def load_emoticons(self) -> None:
        """Reload emoticon surfaces from definitions."""
        self.emotes = load_surfaces()

    def handle_event(self, event: pygame.event.Event, send_callback) -> None:
        """Process pygame events. When a message is submitted it calls send_callback."""
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    text = self.input_box.text.strip()
                    if text:
                        send_callback(text)
                    self.input_box.text = ""
                    self.active = False
                    self.input_box.active = False
                else:
                    self.input_box.handle_event(event)
            elif event.key == pygame.K_RETURN:
                self.active = True
                self.input_box.active = True
        elif self.active:
            self.input_box.handle_event(event)

    def add_message(self, message: str) -> None:
        parts: list[tuple[str, object]] = []
        for token in message.split(' '):
            if token in self.emotes:
                parts.append(("img", self.emotes[token]))
            else:
                parts.append(("text", token))
            parts.append(("text", " "))
        if parts:
            parts.pop()  # remove trailing space
        self.messages.append(parts)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self, screen: pygame.Surface) -> None:
        y = SCREEN_HEIGHT - 50
        for msg in reversed(self.messages):
            x = 10
            for kind, value in msg:
                if kind == "text":
                    surf = self.font.render(str(value), True, WHITE)
                    screen.blit(surf, (x, y))
                    x += surf.get_width()
                else:
                    screen.blit(value, (x, y - 4))
                    x += value.get_width()
            y -= 20
        if self.active:
            self.input_box.draw(screen)

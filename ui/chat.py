import pygame
from .common import InputBox
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class Chat:
    """Simple chat box for displaying and sending messages."""

    def __init__(self, max_messages: int = 6):
        self.font = pygame.font.Font(None, 24)
        self.messages: list[str] = []
        self.max_messages = max_messages
        # input box positioned at bottom-left
        self.input_box = InputBox(10, SCREEN_HEIGHT - 30, 300, 20)
        self.active = False

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
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self, screen: pygame.Surface) -> None:
        y = SCREEN_HEIGHT - 50
        for msg in reversed(self.messages):
            surf = self.font.render(msg, True, WHITE)
            screen.blit(surf, (10, y))
            y -= 20
        if self.active:
            self.input_box.draw(screen)

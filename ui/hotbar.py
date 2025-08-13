import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

GREY = (100, 100, 100)


class Hotbar:
    """Simple action bar with numbered slots."""

    def __init__(self, slots: int = 5):
        self.slots = [None] * slots
        self.selected = 0
        self.slot_size = 40
        self.margin = 5
        self.font = pygame.font.Font(None, 24)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
            index = event.key - pygame.K_1
            if index < len(self.slots):
                self.selected = index
                # Slot activation logic would go here

    def draw(self, screen: pygame.Surface) -> None:
        total_width = self.slot_size * len(self.slots) + self.margin * (len(self.slots) - 1)
        x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - self.slot_size - 10
        for i in range(len(self.slots)):
            rect = pygame.Rect(x + i * (self.slot_size + self.margin), y, self.slot_size, self.slot_size)
            color = WHITE if i == self.selected else GREY
            pygame.draw.rect(screen, color, rect, 2)
            num_surf = self.font.render(str(i + 1), True, WHITE)
            screen.blit(num_surf, (rect.x + 5, rect.y + 5))

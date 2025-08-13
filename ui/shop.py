import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class ShopUI:
    """Basic shop interface listing items for purchase."""

    def __init__(self, shop):
        self.shop = shop
        self.font = pygame.font.Font(None, 24)
        self.active = False

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event, player):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                item_ids = list(self.shop.stock.keys())
                if index < len(item_ids):
                    self.shop.buy(player, item_ids[index])
            elif event.key == pygame.K_ESCAPE:
                self.toggle()

    def draw(self, screen):
        if not self.active:
            return
        panel = pygame.Surface((300, 200))
        panel.fill((0, 0, 0))
        panel.set_alpha(200)
        screen.blit(panel, ((SCREEN_WIDTH - 300) // 2, (SCREEN_HEIGHT - 200) // 2))
        y = (SCREEN_HEIGHT - 160) // 2
        for i, (item_id, data) in enumerate(self.shop.stock.items(), start=1):
            text = self.font.render(f"{i}. {item_id} - {data['price']}g", True, WHITE)
            screen.blit(text, ((SCREEN_WIDTH - 280) // 2, y))
            y += 20

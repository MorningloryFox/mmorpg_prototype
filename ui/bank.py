import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class BankUI:
    """Simple bank interface for depositing and withdrawing."""

    def __init__(self, bank):
        self.bank = bank
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
                inv_ids = list(player.inventory.keys())
                if index < len(inv_ids):
                    self.bank.deposit_item(player, inv_ids[index])
            elif event.key == pygame.K_q:
                self.bank.deposit_gold(player, 10)
            elif event.key == pygame.K_w:
                self.bank.withdraw_gold(player, 10)
            elif event.key == pygame.K_a:
                bank_items = list(self.bank.items.keys())
                if bank_items:
                    self.bank.withdraw_item(player, bank_items[0])
            elif event.key == pygame.K_ESCAPE:
                self.toggle()

    def draw(self, screen):
        if not self.active:
            return
        panel = pygame.Surface((300, 200))
        panel.fill((0, 0, 50))
        panel.set_alpha(200)
        screen.blit(panel, ((SCREEN_WIDTH - 300) // 2, (SCREEN_HEIGHT - 200) // 2))
        y = (SCREEN_HEIGHT - 160) // 2
        text = self.font.render(f"Gold in bank: {self.bank.gold}", True, WHITE)
        screen.blit(text, ((SCREEN_WIDTH - 280) // 2, y))
        y += 20
        for item_id, data in self.bank.items.items():
            txt = self.font.render(f"{item_id} x{data['qty']}", True, WHITE)
            screen.blit(txt, ((SCREEN_WIDTH - 280) // 2, y))
            y += 20

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class CraftingUI:
    """Simple interface to craft items from recipes."""

    def __init__(self, crafting):
        self.crafting = crafting
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
                recipe_ids = list(self.crafting.recipes.keys())
                if index < len(recipe_ids):
                    self.crafting.craft(player, recipe_ids[index])
            elif event.key == pygame.K_ESCAPE:
                self.toggle()

    def draw(self, screen):
        if not self.active:
            return
        panel = pygame.Surface((300, 200))
        panel.fill((50, 0, 0))
        panel.set_alpha(200)
        screen.blit(panel, ((SCREEN_WIDTH - 300) // 2, (SCREEN_HEIGHT - 200) // 2))
        y = (SCREEN_HEIGHT - 160) // 2
        for i, (rid, recipe) in enumerate(self.crafting.recipes.items(), start=1):
            inputs = ", ".join(f"{k}x{v}" for k, v in recipe.get("inputs", {}).items())
            outputs = ", ".join(f"{k}x{v}" for k, v in recipe.get("output", {}).items())
            text = self.font.render(f"{i}. {outputs} <- {inputs}", True, WHITE)
            screen.blit(text, ((SCREEN_WIDTH - 280) // 2, y))
            y += 20

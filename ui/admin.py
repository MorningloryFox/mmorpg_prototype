import pygame
from .common import Button

class AdminPanel:
    """Simple admin tools panel with basic commands."""

    def __init__(self, net_client, player):
        self.net_client = net_client
        self.player = player
        self.visible = False
        self.width = 300
        self.height = 200
        self.x = 20
        self.y = 100
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_alpha(220)
        self.surface.fill((50, 50, 50))
        self.buttons = []
        self._build_buttons()

    def _build_buttons(self):
        # Button to give the player a potion item
        self.buttons.append(
            Button(self.x + 10, self.y + 10, 130, 40, "Give Potion", self._give_potion)
        )
        # Button to spawn an enemy at the player's position
        self.buttons.append(
            Button(self.x + 10, self.y + 60, 130, 40, "Spawn Enemy", self._spawn_enemy)
        )
        # Button to toggle day/night
        self.buttons.append(
            Button(self.x + 10, self.y + 110, 130, 40, "Toggle Day", self._toggle_day)
        )

    # --- Admin Commands ---
    def _give_potion(self):
        if not self.net_client:
            return
        self.net_client.send_admin(
            command="give_item",
            target=self.player.name,
            item_id="potion",
            qty=1,
        )

    def _spawn_enemy(self):
        if not self.net_client:
            return
        self.net_client.send_admin(
            command="spawn_enemy",
            x=self.player.rect.x,
            y=self.player.rect.y,
        )

    def _toggle_day(self):
        if not self.net_client:
            return
        # The actual mode will be toggled server-side; client just requests
        self.net_client.send_admin(command="toggle_weather")

    # --- UI Handling ---
    def handle_event(self, event):
        if not self.visible:
            return
        for btn in self.buttons:
            btn.handle_event(event)

    def draw(self, screen):
        if not self.visible:
            return
        panel_rect = self.surface.get_rect()
        panel_rect.topleft = (self.x, self.y)
        screen.blit(self.surface, panel_rect)
        for btn in self.buttons:
            btn.draw(screen)

    def toggle(self):
        self.visible = not self.visible

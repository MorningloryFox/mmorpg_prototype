# editor.py
import pygame
import json
from settings import *
from wall import Wall

TILE_SIZE = 32  # Assuming 32x32 tiles in the tileset
MAP_WIDTH_TILES = 40
MAP_HEIGHT_TILES = 30

class Editor:
    def __init__(self):
        self.tileset = pygame.image.load('tileset1.png').convert_alpha()
        self.tiles = []
        self.load_tiles()
        self.selected_tile_index = 0

        # Palette dimensions and position
        self.palette_width = 4 * TILE_SIZE
        self.palette_height = SCREEN_HEIGHT
        self.palette_x = SCREEN_WIDTH - self.palette_width
        self.palette_y = 0

        # Layer data: -1 means empty
        self.layers = {
            'ground': [[-1 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'objects': [[-1 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'collision': [[0 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
        }
        self.current_layer = 'ground'

        # Simple metadata defaults
        self.metadata = {
            'climate': 'day',
            'events': []
        }

    def load_tiles(self):
        width, height = self.tileset.get_size()
        for y in range(0, height, TILE_SIZE):
            for x in range(0, width, TILE_SIZE):
                tile = self.tileset.subsurface(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                self.tiles.append(tile)

    def handle_event(self, event, all_sprites, wall_sprites, camera):
        # Switch editing layer with number keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.current_layer = 'ground'
            elif event.key == pygame.K_2:
                self.current_layer = 'objects'
            elif event.key == pygame.K_3:
                self.current_layer = 'collision'
            elif event.key == pygame.K_c:
                # cycle climate metadata for demonstration
                modes = ['day', 'night', 'rain']
                idx = modes.index(self.metadata['climate'])
                self.metadata['climate'] = modes[(idx + 1) % len(modes)]
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Selecting tile from palette
            if mouse_pos[0] > self.palette_x:
                palette_x = mouse_pos[0] - self.palette_x
                palette_y = mouse_pos[1] - self.palette_y
                col = palette_x // TILE_SIZE
                row = palette_y // TILE_SIZE
                index = row * (self.palette_width // TILE_SIZE) + col
                if index < len(self.tiles):
                    self.selected_tile_index = index
            else:
                # placing tile into world
                world_x = mouse_pos[0] - camera.camera.x
                world_y = mouse_pos[1] - camera.camera.y
                grid_x = world_x // TILE_SIZE
                grid_y = world_y // TILE_SIZE
                if not (0 <= grid_x < MAP_WIDTH_TILES and 0 <= grid_y < MAP_HEIGHT_TILES):
                    return

                if self.current_layer in ('ground', 'objects'):
                    if event.button == 1:
                        self.layers[self.current_layer][grid_y][grid_x] = self.selected_tile_index
                        if self.current_layer == 'ground':
                            self.update_autotiles(grid_x, grid_y)
                    elif event.button == 3:
                        self.layers[self.current_layer][grid_y][grid_x] = -1
                        if self.current_layer == 'ground':
                            self.update_autotiles(grid_x, grid_y)
                elif self.current_layer == 'collision':
                    # toggle collision tile
                    if event.button == 1:
                        self.layers['collision'][grid_y][grid_x] = 1
                        # create visual wall sprite
                        selected_image = self.tiles[self.selected_tile_index]
                        wall = Wall(grid_x * TILE_SIZE, grid_y * TILE_SIZE, selected_image)
                        all_sprites.add(wall)
                        wall_sprites.add(wall)
                    elif event.button == 3:
                        self.layers['collision'][grid_y][grid_x] = 0
                        for wall in wall_sprites:
                            if wall.rect.x == grid_x * TILE_SIZE and wall.rect.y == grid_y * TILE_SIZE:
                                wall.kill()

    def update_autotiles(self, x, y):
        """Simple bitmask-based autotiling for the ground layer."""
        def autotile(cx, cy):
            base = self.layers['ground'][cy][cx]
            if base < 0:
                return
            mask = 0
            # up, right, down, left bitmask
            if cy > 0 and self.layers['ground'][cy - 1][cx] >= 0:
                mask |= 1
            if cx < MAP_WIDTH_TILES - 1 and self.layers['ground'][cy][cx + 1] >= 0:
                mask |= 2
            if cy < MAP_HEIGHT_TILES - 1 and self.layers['ground'][cy + 1][cx] >= 0:
                mask |= 4
            if cx > 0 and self.layers['ground'][cy][cx - 1] >= 0:
                mask |= 8
            self.layers['ground'][cy][cx] = base + mask

        # update this tile and neighbors for transitions
        for nx in range(max(0, x - 1), min(MAP_WIDTH_TILES, x + 2)):
            for ny in range(max(0, y - 1), min(MAP_HEIGHT_TILES, y + 2)):
                autotile(nx, ny)

    def save_map(self):
        data = {
            'layers': self.layers,
            'metadata': self.metadata
        }
        with open('map.json', 'w') as f:
            json.dump(data, f)
        print('Map saved to map.json')

    def draw(self, screen, camera):
        # Draw map layers
        offset_x = -camera.camera.x
        offset_y = -camera.camera.y
        for layer_name in ('ground', 'objects'):
            layer = self.layers[layer_name]
            for y, row in enumerate(layer):
                for x, tile_index in enumerate(row):
                    if tile_index >= 0:
                        screen.blit(self.tiles[tile_index], (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y))

        # Palette panel
        pygame.draw.rect(screen, (50, 50, 50), (self.palette_x, self.palette_y, self.palette_width, self.palette_height))

        for i, tile_img in enumerate(self.tiles):
            col = i % (self.palette_width // TILE_SIZE)
            row = i // (self.palette_width // TILE_SIZE)
            x = self.palette_x + col * TILE_SIZE
            y = self.palette_y + row * TILE_SIZE
            screen.blit(tile_img, (x, y))

        selected_col = self.selected_tile_index % (self.palette_width // TILE_SIZE)
        selected_row = self.selected_tile_index // (self.palette_width // TILE_SIZE)
        pygame.draw.rect(screen, RED, (self.palette_x + selected_col * TILE_SIZE, self.palette_y + selected_row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

        # Current layer indicator
        layer_surf = pygame.font.Font(None, 24).render(f'Layer: {self.current_layer}', True, WHITE)
        screen.blit(layer_surf, (10, 10))
        climate_surf = pygame.font.Font(None, 24).render(f'Climate: {self.metadata["climate"]}', True, WHITE)
        screen.blit(climate_surf, (10, 30))

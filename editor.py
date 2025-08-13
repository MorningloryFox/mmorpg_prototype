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
        self.palette_margin = TILE_SIZE * 2  # preview space

        # vertical toolbar on the left
        self.tools = ["pencil", "eraser", "rect", "fill", "eyedropper"]
        self.current_tool = "pencil"
        self.toolbar_width = TILE_SIZE
        self.toolbar_x = 0
        self.toolbar_y = 0

        # Layer data: -1 means empty
        self.layers = {
            'ground': [[-1 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'mask': [[-1 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'fringe': [[-1 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'events': [[None for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
            'collision': [[0 for _ in range(MAP_WIDTH_TILES)] for _ in range(MAP_HEIGHT_TILES)],
        }
        self.layer_visible = {k: True for k in self.layers}
        self.current_layer = 'ground'

        # Simple metadata defaults
        self.metadata = {
            'climate': 'day',
            'events': []
        }

        # helper state for rect tool
        self.rect_start = None

    def load_tiles(self):
        width, height = self.tileset.get_size()
        for y in range(0, height, TILE_SIZE):
            for x in range(0, width, TILE_SIZE):
                tile = self.tileset.subsurface(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                self.tiles.append(tile)

    def handle_event(self, event, all_sprites, wall_sprites, camera):
        # Switch editing layer with number keys
        if event.type == pygame.KEYDOWN:
            # layer switching
            if event.key == pygame.K_1:
                self.current_layer = 'ground'
            elif event.key == pygame.K_2:
                self.current_layer = 'mask'
            elif event.key == pygame.K_3:
                self.current_layer = 'fringe'
            elif event.key == pygame.K_4:
                self.current_layer = 'events'
            elif event.key == pygame.K_5:
                self.current_layer = 'collision'
            elif event.key == pygame.K_s:
                self.save_map()
            elif event.key == pygame.K_l:
                self.load_map()
            elif event.key == pygame.K_r:
                self.resize_map(MAP_WIDTH_TILES, MAP_HEIGHT_TILES)
            elif event.key == pygame.K_v:
                self.layer_visible[self.current_layer] = not self.layer_visible[
                    self.current_layer
                ]
            elif event.key == pygame.K_c:
                modes = ['day', 'night', 'rain']
                idx = modes.index(self.metadata['climate'])
                self.metadata['climate'] = modes[(idx + 1) % len(modes)]
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # toolbar selection
            if mouse_pos[0] < self.toolbar_width:
                idx = mouse_pos[1] // TILE_SIZE
                if idx < len(self.tools):
                    self.current_tool = self.tools[idx]
                return

            # Selecting tile from palette
            if mouse_pos[0] > self.palette_x:
                palette_x = mouse_pos[0] - self.palette_x
                palette_y = mouse_pos[1] - self.palette_y - self.palette_margin
                if palette_y < 0:
                    return
                col = palette_x // TILE_SIZE
                row = palette_y // TILE_SIZE
                index = row * (self.palette_width // TILE_SIZE) + col
                if index < len(self.tiles):
                    self.selected_tile_index = index
            else:
                world_x = mouse_pos[0] - camera.camera.x
                world_y = mouse_pos[1] - camera.camera.y
                grid_x = world_x // TILE_SIZE
                grid_y = world_y // TILE_SIZE
                if not (0 <= grid_x < MAP_WIDTH_TILES and 0 <= grid_y < MAP_HEIGHT_TILES):
                    return

                if self.current_layer == 'collision':
                    if event.button == 1:
                        self.layers['collision'][grid_y][grid_x] = 1
                        selected_image = self.tiles[self.selected_tile_index]
                        wall = Wall(grid_x * TILE_SIZE, grid_y * TILE_SIZE, selected_image)
                        all_sprites.add(wall)
                        wall_sprites.add(wall)
                    elif event.button == 3 or self.current_tool == 'eraser':
                        self.layers['collision'][grid_y][grid_x] = 0
                        for wall in wall_sprites:
                            if wall.rect.x == grid_x * TILE_SIZE and wall.rect.y == grid_y * TILE_SIZE:
                                wall.kill()
                    return

                if self.current_layer == 'events':
                    if event.button == 1 and self.current_tool != 'eraser':
                        self.layers['events'][grid_y][grid_x] = {'id': 1}
                    else:
                        self.layers['events'][grid_y][grid_x] = None
                    return

                if self.current_tool == 'pencil':
                    if event.button == 1:
                        self.layers[self.current_layer][grid_y][grid_x] = self.selected_tile_index
                        if self.current_layer == 'ground':
                            self.update_autotiles(grid_x, grid_y)
                    elif event.button == 3:
                        self.layers[self.current_layer][grid_y][grid_x] = -1
                        if self.current_layer == 'ground':
                            self.update_autotiles(grid_x, grid_y)
                elif self.current_tool == 'eraser':
                    self.layers[self.current_layer][grid_y][grid_x] = -1
                elif self.current_tool == 'eyedropper':
                    tile = self.layers[self.current_layer][grid_y][grid_x]
                    if tile is not None and tile >= 0:
                        self.selected_tile_index = tile
                elif self.current_tool == 'fill':
                    target = self.layers[self.current_layer][grid_y][grid_x]
                    self.flood_fill(self.current_layer, grid_x, grid_y, target, self.selected_tile_index)
                elif self.current_tool == 'rect':
                    if self.rect_start is None:
                        self.rect_start = (grid_x, grid_y)
                    else:
                        x0, y0 = self.rect_start
                        for ry in range(min(y0, grid_y), max(y0, grid_y) + 1):
                            for rx in range(min(x0, grid_x), max(x0, grid_x) + 1):
                                if 0 <= rx < MAP_WIDTH_TILES and 0 <= ry < MAP_HEIGHT_TILES:
                                    self.layers[self.current_layer][ry][rx] = self.selected_tile_index
                        self.rect_start = None

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

    def flood_fill(self, layer: str, x: int, y: int, target, replacement):
        if target == replacement:
            return
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not (0 <= cx < MAP_WIDTH_TILES and 0 <= cy < MAP_HEIGHT_TILES):
                continue
            if self.layers[layer][cy][cx] != target:
                continue
            self.layers[layer][cy][cx] = replacement
            stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

    def save_map(self):
        data = {
            'layers': self.layers,
            'metadata': self.metadata
        }
        with open('map.json', 'w') as f:
            json.dump(data, f)
        print('Map saved to map.json')

    def load_map(self):
        try:
            with open('map.json') as f:
                data = json.load(f)
            self.layers = data.get('layers', self.layers)
            self.metadata = data.get('metadata', self.metadata)
        except FileNotFoundError:
            print('map.json not found')

    def resize_map(self, new_w, new_h):
        for layer, grid in self.layers.items():
            if layer == 'events':
                fill = None
            elif layer == 'collision':
                fill = 0
            else:
                fill = -1
            new_grid = [[fill for _ in range(new_w)] for _ in range(new_h)]
            for y in range(min(new_h, len(grid))):
                for x in range(min(new_w, len(grid[0]))):
                    new_grid[y][x] = grid[y][x]
            self.layers[layer] = new_grid

    def draw(self, screen, camera):
        # Draw map layers in order
        offset_x = -camera.camera.x
        offset_y = -camera.camera.y
        for layer_name in ('ground', 'mask', 'fringe'):
            if not self.layer_visible.get(layer_name, True):
                continue
            layer = self.layers[layer_name]
            for y, row in enumerate(layer):
                for x, tile_index in enumerate(row):
                    if tile_index >= 0:
                        screen.blit(self.tiles[tile_index], (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y))

        # event markers
        if self.layer_visible.get('events', True):
            for y, row in enumerate(self.layers['events']):
                for x, ev in enumerate(row):
                    if ev:
                        pygame.draw.rect(
                            screen,
                            (255, 0, 255),
                            pygame.Rect(x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE),
                            2,
                        )

        # Palette panel
        pygame.draw.rect(screen, (50, 50, 50), (self.palette_x, self.palette_y, self.palette_width, self.palette_height))
        # preview of selected tile
        screen.blit(self.tiles[self.selected_tile_index], (self.palette_x, self.palette_y))
        pygame.draw.rect(
            screen,
            WHITE,
            (self.palette_x, self.palette_y, TILE_SIZE, TILE_SIZE),
            1,
        )

        for i, tile_img in enumerate(self.tiles):
            col = i % (self.palette_width // TILE_SIZE)
            row = i // (self.palette_width // TILE_SIZE)
            x = self.palette_x + col * TILE_SIZE
            y = self.palette_y + self.palette_margin + row * TILE_SIZE
            screen.blit(tile_img, (x, y))

        selected_col = self.selected_tile_index % (self.palette_width // TILE_SIZE)
        selected_row = self.selected_tile_index // (self.palette_width // TILE_SIZE)
        pygame.draw.rect(
            screen,
            RED,
            (
                self.palette_x + selected_col * TILE_SIZE,
                self.palette_y + self.palette_margin + selected_row * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            ),
            2,
        )

        # toolbar draw
        pygame.draw.rect(
            screen, (60, 60, 60), (self.toolbar_x, self.toolbar_y, self.toolbar_width, SCREEN_HEIGHT)
        )
        font = pygame.font.Font(None, 24)
        for i, tool in enumerate(self.tools):
            rect = pygame.Rect(self.toolbar_x, i * TILE_SIZE, self.toolbar_width, TILE_SIZE)
            pygame.draw.rect(screen, (80, 80, 80), rect)
            text = font.render(tool[0].upper(), True, WHITE)
            screen.blit(text, (rect.x + 8, rect.y + 8))
            if self.current_tool == tool:
                pygame.draw.rect(screen, RED, rect, 2)

        # Current layer and climate indicator
        layer_surf = pygame.font.Font(None, 24).render(
            f'Layer: {self.current_layer}', True, WHITE
        )
        screen.blit(layer_surf, (self.toolbar_width + 10, 10))
        climate_surf = pygame.font.Font(None, 24).render(
            f'Climate: {self.metadata["climate"]}', True, WHITE
        )
        screen.blit(climate_surf, (self.toolbar_width + 10, 30))

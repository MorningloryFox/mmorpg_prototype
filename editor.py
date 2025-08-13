# editor.py
import pygame
from settings import *
from wall import Wall

TILE_SIZE = 32 # Assuming 32x32 tiles in the tileset

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

    def load_tiles(self):
        width, height = self.tileset.get_size()
        for y in range(0, height, TILE_SIZE):
            for x in range(0, width, TILE_SIZE):
                tile = self.tileset.subsurface(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                self.tiles.append(tile)

    def handle_event(self, event, all_sprites, wall_sprites, camera):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if mouse_pos[0] > self.palette_x:
                palette_x = mouse_pos[0] - self.palette_x
                palette_y = mouse_pos[1] - self.palette_y
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
                
                selected_image = self.tiles[self.selected_tile_index]
                
                for wall in wall_sprites:
                    if wall.rect.x == grid_x * TILE_SIZE and wall.rect.y == grid_y * TILE_SIZE:
                        wall.kill()

                if event.button == 1:
                    wall = Wall(grid_x * TILE_SIZE, grid_y * TILE_SIZE, selected_image)
                    all_sprites.add(wall)
                    wall_sprites.add(wall)

    def save_map(self, wall_sprites):
        # Assuming a fixed map size for now. This should be more robust in a real game.
        map_width_tiles = 40
        map_height_tiles = 30
        
        grid = [['.' for _ in range(map_width_tiles)] for _ in range(map_height_tiles)]

        for wall in wall_sprites:
            grid_x = wall.rect.x // TILE_SIZE
            grid_y = wall.rect.y // TILE_SIZE
            if 0 <= grid_x < map_width_tiles and 0 <= grid_y < map_height_tiles:
                grid[grid_y][grid_x] = 'W'
        
        with open('map.txt', 'w') as f:
            for row in grid:
                f.write(''.join(row) + '\n')
        print("Map saved to map.txt")

    def draw(self, screen):
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

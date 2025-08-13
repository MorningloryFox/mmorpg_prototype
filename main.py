# main.py
import pygame
import sys
import random
import json

from settings import *
from player import Player
from resource import Resource
from quest import QuestManager, Quest
from item import ITEM_DEFS
import events

with open('classes.json', 'r') as f:
    CLASS_DEFS = json.load(f)
from wall import Wall
from camera import Camera
from enemy import Enemy
from entities.projectile import Projectile
from ui import Button, InputBox, Label
from ui.chat import Chat
from ui.hotbar import Hotbar
from shop import Shop
from bank import Bank
from crafting import Crafting
from ui.shop import ShopUI
from ui.bank import BankUI
from ui.crafting import CraftingUI
from editor import Editor
import database as db
from network.client import NetworkClient

# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MMORPG 2D Prototype")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Game State Variables ---
game_state = 'login'
current_user = None
message = ''
net_client = None
other_players = {}
chat_ui = Chat()
hotbar = Hotbar()
quest_manager = QuestManager()
shop = Shop()
bank = Bank()
crafting = Crafting()
shop_ui = ShopUI(shop)
bank_ui = BankUI(bank)
crafting_ui = CraftingUI(crafting)

# --- Load UI Assets ---
login_panel_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel02.png").convert_alpha()
login_panel_img = pygame.transform.scale(login_panel_img, (400, 500))
button_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Btn01.png").convert_alpha()

# HUD Assets
health_bar_bg_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/ProgressBar_01/BarV1_ProgressBar.png").convert_alpha()
health_bar_fill_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/ProgressBar_01/BarV1_Bar.png").convert_alpha()

# --- UI Elements ---
panel_x = (SCREEN_WIDTH - 400) // 2
panel_y = (SCREEN_HEIGHT - 500) // 2

# Login Screen
login_title = Label(panel_x + 200, panel_y + 80, "Login", font_size=50)
username_input = InputBox(panel_x + 100, panel_y + 150, 200, 40)
password_input = InputBox(panel_x + 100, panel_y + 210, 200, 40, is_password=True)
login_button = Button(panel_x + 125, panel_y + 280, 150, 50, 'Login', lambda: login(), image=button_img)
create_account_button = Button(panel_x + 100, panel_y + 340, 200, 50, 'Create Account', lambda: set_state('create_account'), image=button_img)
login_elements = [login_title, username_input, password_input, login_button, create_account_button]

# Create Account Screen
create_account_title = Label(panel_x + 200, panel_y + 80, "Create Account", font_size=40)
new_username_input = InputBox(panel_x + 100, panel_y + 150, 200, 40)
new_password_input = InputBox(panel_x + 100, panel_y + 210, 200, 40, is_password=True)
class_input = InputBox(panel_x + 100, panel_y + 270, 200, 40)
create_button = Button(panel_x + 125, panel_y + 330, 150, 50, 'Create', lambda: create_account(), image=button_img)
back_to_login_button = Button(panel_x + 100, panel_y + 340, 200, 50, 'Back to Login', lambda: set_state('login'), image=button_img)
create_account_elements = [create_account_title, new_username_input, new_password_input, class_input, create_button, back_to_login_button]

# Options Menu
options_title = Label(panel_x + 200, panel_y + 80, "Options", font_size=50)
resume_button = Button(panel_x + 125, panel_y + 200, 150, 50, 'Resume', lambda: set_state('playing'), image=button_img)
logout_button = Button(panel_x + 125, panel_y + 280, 150, 50, 'Logout', lambda: set_state('login'), image=button_img)
options_elements = [options_title, resume_button, logout_button]

# --- Game World Variables ---
all_sprites = None
player = None
camera = None
wall_sprites = None
enemy_sprites = None
resource_sprites = None
projectile_sprites = None
inventory_panel_img = None
resource_icon_img = None
editor = Editor()

def set_state(new_state):
    global game_state, message
    game_state = new_state
    message = ''

def login():
    """Authenticate the user through the network server."""
    global current_user, message, net_client, other_players
    username = username_input.text
    password = password_input.text
    try:
        if not net_client:
            net_client = NetworkClient()
        success, players, is_admin = net_client.login(username, password)
    except Exception:
        message = 'Connection failed'
        return

    if success:
        user_data = db.get_user(username)
        current_user = {
            'username': username,
            'is_admin': is_admin,
            'class': user_data['characters'][0].get('class') if user_data else None,
            'quests': user_data['characters'][0].get('quests', {}) if user_data else {}
        }
        load_game_world()
        other_players = {}
        for uname, pos in players.items():
            if uname != username:
                op = Player(pos['x'], pos['y'])
                op.name = uname
                all_sprites.add(op)
                other_players[uname] = op
        set_state('playing')
        # send initial position to server
        net_client.update_position(player.rect.x, player.rect.y)
    else:
        message = 'Invalid username or password'

def create_account():
    global message
    username = new_username_input.text
    password = new_password_input.text
    char_class = class_input.text or 'Warrior'
    if db.create_user(username, password, char_class):
        message = 'Account created successfully! Please login.'
        set_state('login')
    else:
        message = 'Username already exists.'

def load_game_world():
    global all_sprites, player, camera, wall_sprites, enemy_sprites, resource_sprites, projectile_sprites, inventory_panel_img, resource_icon_img, quest_manager
    
    inventory_panel_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel01.png").convert_alpha()
    inventory_panel_img = pygame.transform.scale(inventory_panel_img, (250, 180))
    resource_icon_img = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Icons/Icon01.png").convert_alpha()
    resource_icon_img = pygame.transform.scale(resource_icon_img, (40, 40))

    all_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()
    resource_sprites = pygame.sprite.Group()
    projectile_sprites = pygame.sprite.Group()

    with open("map.txt", 'r') as f:
        map_data = f.readlines()

    TILE_SIZE = 32
    map_width = len(map_data[0].strip()) * TILE_SIZE
    map_height = len(map_data) * TILE_SIZE

    for row, tiles in enumerate(map_data):
        for col, tile in enumerate(tiles):
            if tile == 'W':
                wall = Wall(col * TILE_SIZE, row * TILE_SIZE, editor.tiles[0])
                all_sprites.add(wall)
                wall_sprites.add(wall)

    player = Player(100, 100)
    class_name = current_user.get('class', 'Warrior')
    class_def = CLASS_DEFS.get(class_name, {})
    stats = class_def.get('base_stats', {})
    player.max_health = stats.get('health', player.max_health)
    player.health = player.max_health
    player.attack = stats.get('attack', player.attack)
    player.defense = stats.get('defense', player.defense)
    player.character_class = class_name
    quest_manager = QuestManager()
    quest_manager.load_from_dict(current_user.get('quests', {}))
    all_sprites.add(player)

    camera = Camera(map_width, map_height)


def send_chat_message(text: str) -> None:
    """Send a chat message to the server and display locally."""
    chat_ui.add_message(f"{current_user['username']}: {text}")
    if net_client:
        net_client.send_chat(text)

def display_inventory(inventory):
    screen.blit(inventory_panel_img, (10, 10))
    font = pygame.font.Font(None, 36)
    y_offset = 50

    for item_id, data in inventory.items():
        icon = pygame.image.load(data['item'].icon).convert_alpha()
        icon = pygame.transform.scale(icon, (40, 40))
        screen.blit(icon, (35, y_offset - 5))
        text = font.render(f"x {data['qty']}", True, WHITE)
        screen.blit(text, (85, y_offset))
        y_offset += 50

def display_hud(player):
    # Player Name
    name_surf = font.render(player.name, True, WHITE)
    screen.blit(name_surf, (10, 10))

    # Health Bar
    bar_width = 200
    bar_height = 30
    bar_x = 10
    bar_y = 40

    # Background of health bar
    screen.blit(pygame.transform.scale(health_bar_bg_img, (bar_width, bar_height)), (bar_x, bar_y))

    # Fill of health bar
    health_percentage = player.health / player.max_health
    fill_width = int(bar_width * health_percentage)
    screen.blit(pygame.transform.scale(health_bar_fill_img, (fill_width, bar_height)), (bar_x, bar_y))

    # Health text
    health_text = font.render(f"{player.health}/{player.max_health}", True, WHITE)
    screen.blit(health_text, (bar_x + bar_width // 2 - health_text.get_width() // 2, bar_y + bar_height // 2 - health_text.get_height() // 2))

    # Level and XP
    level_text = font.render(f"Lv {player.level}", True, WHITE)
    screen.blit(level_text, (10, 80))
    xp_text = font.render(f"XP: {player.xp}/{player.required_xp}", True, WHITE)
    screen.blit(xp_text, (10, 110))
    gold_text = font.render(f"Gold: {player.gold}", True, WHITE)
    screen.blit(gold_text, (10, 140))

    # Inventory
    display_inventory(player.inventory)

    # Hotbar
    hotbar.draw(screen)

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if game_state == 'login':
            for el in login_elements:
                if isinstance(el, (Button, InputBox)):
                    el.handle_event(event)
        elif game_state == 'create_account':
            for el in create_account_elements:
                if isinstance(el, (Button, InputBox)):
                    el.handle_event(event)
        elif game_state == 'playing':
            chat_ui.handle_event(event, lambda text: send_chat_message(text))
            hotbar.handle_event(event)
            shop_ui.handle_event(event, player)
            bank_ui.handle_event(event, player)
            crafting_ui.handle_event(event, player)
            if event.type == pygame.KEYDOWN and not chat_ui.active:
                if event.key == pygame.K_F1 and current_user['is_admin']:
                    set_state('editor')
                elif event.key == pygame.K_ESCAPE:
                    set_state('options')
                elif event.key == pygame.K_p:
                    shop_ui.toggle()
                elif event.key == pygame.K_b:
                    bank_ui.toggle()
                elif event.key == pygame.K_c:
                    crafting_ui.toggle()
                elif event.key == pygame.K_t and other_players and net_client:
                    target = next(iter(other_players.keys()))
                    for item_id, data in list(player.inventory.items()):
                        if data['qty'] > 0:
                            net_client.send_trade(target, item_id, 1)
                            data['qty'] -= 1
                            if data['qty'] <= 0:
                                del player.inventory[item_id]
                            break
                elif event.key == pygame.K_SPACE:
                    player.melee_attack(enemy_sprites)
                elif event.key == pygame.K_f:
                    proj = Projectile(player.rect.centerx, player.rect.centery, player.direction, wall_sprites, enemy_sprites, player.attack)
                    all_sprites.add(proj)
                    projectile_sprites.add(proj)
        elif game_state == 'editor':
            editor.handle_event(event, all_sprites, wall_sprites, camera)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    set_state('playing')
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    editor.save_map(wall_sprites)
                    message = "Map Saved!"
        elif game_state == 'options':
            for el in options_elements:
                if isinstance(el, Button):
                    el.handle_event(event)

    screen.fill(BLACK)

    if game_state == 'login':
        screen.blit(login_panel_img, (panel_x, panel_y))
        for el in login_elements:
            el.draw(screen)
        msg_surf = font.render(message, True, RED)
        screen.blit(msg_surf, (panel_x + 50, panel_y + 420))

    elif game_state == 'create_account':
        screen.blit(login_panel_img, (panel_x, panel_y))
        for el in create_account_elements:
            el.draw(screen)
        msg_surf = font.render(message, True, RED)
        screen.blit(msg_surf, (panel_x + 50, panel_y + 420))

    elif game_state == 'playing' or game_state == 'options' or game_state == 'editor':
        # Draw the game world in the background for these states
        all_sprites.update()
        if game_state != 'options' and not chat_ui.active:  # Don't move player in options menu or while chatting
            keys = pygame.key.get_pressed()
            player.move(keys, wall_sprites, enemy_sprites)
        camera.update(player)
        player.collect_resources(resource_sprites)
        events.check_events(player, quest_manager)
        db.save_user_quests(current_user['username'], quest_manager.to_dict())
        for enemy in enemy_sprites:
            if player.rect.colliderect(enemy.rect):
                player.take_damage(max(0, enemy.attack - player.defense))

        if game_state == 'playing' and net_client:
            net_client.update_position(player.rect.x, player.rect.y)
            for msg in net_client.get_messages():
                action = msg.get('action')
                if action == 'pos':
                    uname = msg.get('username')
                    if uname != current_user['username']:
                        if uname not in other_players:
                            op = Player(msg.get('x', 0), msg.get('y', 0))
                            op.name = uname
                            all_sprites.add(op)
                            other_players[uname] = op
                        else:
                            other_players[uname].rect.x = msg.get('x', 0)
                            other_players[uname].rect.y = msg.get('y', 0)
                elif action == 'join':
                    uname = msg.get('username')
                    if uname != current_user['username'] and uname not in other_players:
                        op = Player(msg.get('x', 0), msg.get('y', 0))
                        op.name = uname
                        all_sprites.add(op)
                        other_players[uname] = op
                elif action == 'leave':
                    uname = msg.get('username')
                    if uname in other_players:
                        other_players[uname].kill()
                        del other_players[uname]
                elif action == 'chat':
                    chat_ui.add_message(f"{msg.get('username')}: {msg.get('text', '')}")
                elif action == 'trade':
                    if msg.get('to') == current_user['username']:
                        item_id = msg.get('item_id')
                        qty = msg.get('qty', 1)
                        item_def = ITEM_DEFS.get(item_id)
                        if item_def:
                            player.inventory.setdefault(item_id, {'item': item_def, 'qty': 0})
                            player.inventory[item_id]['qty'] += qty

        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        display_hud(player)
        chat_ui.draw(screen)
        shop_ui.draw(screen)
        bank_ui.draw(screen)
        crafting_ui.draw(screen)

        if game_state == 'options':
            screen.blit(login_panel_img, (panel_x, panel_y))
            for el in options_elements:
                el.draw(screen)
        elif game_state == 'editor':
            editor.draw(screen)
            msg_surf = font.render(message, True, GREEN)
            screen.blit(msg_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

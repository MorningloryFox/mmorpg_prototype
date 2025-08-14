import pygame
import sys
import json
from settings import *
from ui import Button, InputBox, Label
import database as db
from network.client import NetworkClient

class LoginScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Cores modernas
        self.colors = {
            'bg': (20, 20, 30),
            'panel': (40, 40, 50),
            'accent': (100, 150, 255),
            'text': (255, 255, 255),
            'text_dark': (180, 180, 180),
            'error': (255, 100, 100),
            'success': (100, 255, 100)
        }
        
        # Carregar imagens de fundo
        try:
            self.bg_image = pygame.image.load("data/Wenrexa/Wenrexa Interface UI KIT #4/PNG/Panel03.png")
            self.bg_image = pygame.transform.scale(self.bg_image, (500, 600))
        except:
            self.bg_image = None
            
        # Elementos UI
        self.setup_ui()
        self.message = ""
        self.message_timer = 0
        
    def setup_ui(self):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Título
        self.title = Label(center_x, center_y - 200, "MMORPG 2D", font_size=56)
        self.subtitle = Label(center_x, center_y - 160, "Enter the Adventure", font_size=24)
        
        # Campos de entrada
        self.username_label = Label(center_x - 150, center_y - 80, "Username", font_size=20)
        self.username_input = InputBox(center_x - 150, center_y - 50, 300, 40)
        
        self.password_label = Label(center_x - 150, center_y + 10, "Password", font_size=20)
        self.password_input = InputBox(center_x - 150, center_y + 40, 300, 40, is_password=True)
        
        # Botões
        self.login_button = Button(center_x - 100, center_y + 120, 200, 50, 'LOGIN', lambda: self.login())
        self.register_button = Button(center_x - 100, center_y + 180, 200, 50, 'CREATE ACCOUNT', lambda: self.show_register())
        
        # Tela de registro
        self.register_title = Label(center_x, center_y - 200, "Create Account", font_size=48)
        self.class_label = Label(center_x - 150, center_y + 100, "Class (Warrior/Mage/Archer)", font_size=20)
        self.class_input = InputBox(center_x - 150, center_y + 130, 300, 40)
        
        self.create_button = Button(center_x - 100, center_y + 200, 200, 50, 'CREATE', lambda: self.create_account())
        self.back_button = Button(center_x - 100, center_y + 260, 200, 50, 'BACK', lambda: self.show_login())
        
        self.current_screen = 'login'
        
    def draw_gradient_background(self):
        """Desenha um fundo gradiente moderno"""
        for y in range(SCREEN_HEIGHT):
            color_value = int(20 + (y / SCREEN_HEIGHT) * 20)
            color = (color_value, color_value, color_value + 10)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
    def draw_panel(self, x, y, width, height):
        """Desenha um painel com bordas arredondadas"""
        # Sombra
        shadow_rect = pygame.Rect(x + 5, y + 5, width, height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # Painel principal
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect, border_radius=15)
        
        # Borda
        pygame.draw.rect(self.screen, self.colors['accent'], panel_rect, 2, border_radius=15)
        
    def handle_events(self, event):
        if self.current_screen == 'login':
            for element in [self.username_input, self.password_input, self.login_button, self.register_button]:
                if hasattr(element, 'handle_event'):
                    element.handle_event(event)
        else:
            for element in [self.username_input, self.password_input, self.class_input, 
                           self.create_button, self.back_button]:
                if hasattr(element, 'handle_event'):
                    element.handle_event(event)
                    
    def login(self):
        username = self.username_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.show_message("Please fill all fields", error=True)
            return
            
        try:
            net_client = NetworkClient()
            success, players, is_admin = net_client.login(username, password)
            
            if success:
                self.show_message("Login successful!", error=False)
                return True
            else:
                self.show_message("Invalid credentials", error=True)
                
        except Exception as e:
            self.show_message("Connection failed", error=True)
            
        return False
        
    def create_account(self):
        username = self.username_input.text
        password = self.password_input.text
        char_class = self.class_input.text or 'Warrior'
        
        if not username or not password:
            self.show_message("Please fill all fields", error=True)
            return
            
        if db.create_user(username, password, char_class):
            self.show_message("Account created! Please login.", error=False)
            self.show_login()
        else:
            self.show_message("Username already exists", error=True)
            
    def show_login(self):
        self.current_screen = 'login'
        self.message = ""
        
    def show_register(self):
        self.current_screen = 'register'
        self.message = ""
        
    def show_message(self, text, error=True):
        self.message = text
        self.message_timer = 180  # 3 segundos a 60 FPS
        
    def draw(self):
        self.draw_gradient_background()
        
        # Desenhar painel central
        panel_x = SCREEN_WIDTH // 2 - 250
        panel_y = SCREEN_HEIGHT // 2 - 300
        
        if self.bg_image:
            self.screen.blit(self.bg_image, (panel_x, panel_y))
        else:
            self.draw_panel(panel_x, panel_y, 500, 600)
        
        if self.current_screen == 'login':
            self.draw_login_screen()
        else:
            self.draw_register_screen()
            
        # Desenhar mensagem
        if self.message:
            color = self.colors['error'] if "failed" in self.message.lower() or "invalid" in self.message.lower() else self.colors['success']
            msg_surface = self.font_medium.render(self.message, True, color)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(msg_surface, msg_rect)
            
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
                
    def draw_login_screen(self):
        center_x = SCREEN_WIDTH // 2
        
        # Título
        title_surface = self.font_large.render("MMORPG 2D", True, self.colors['accent'])
        title_rect = title_surface.get_rect(center=(center_x, 150))
        self.screen.blit(title_surface, title_rect)
        
        subtitle_surface = self.font_small.render("Enter the Adventure", True, self.colors['text_dark'])
        subtitle_rect = subtitle_surface.get_rect(center=(center_x, 190))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Labels e inputs
        self.username_label.draw(self.screen)
        self.username_input.draw(self.screen)
        
        self.password_label.draw(self.screen)
        self.password_input.draw(self.screen)
        
        # Botões
        self.login_button.draw(self.screen)
        self.register_button.draw(self.screen)
        
    def draw_register_screen(self):
        center_x = SCREEN_WIDTH // 2
        
        # Título
        title_surface = self.font_large.render("Create Account", True, self.colors['accent'])
        title_rect = title_surface.get_rect(center=(center_x, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Labels e inputs
        self.username_label.draw(self.screen)
        self.username_input.draw(self.screen)
        
        self.password_label.draw(self.screen)
        self.password_input.draw(self.screen)
        
        self.class_label.draw(self.screen)
        self.class_input.draw(self.screen)
        
        # Botões
        self.create_button.draw(self.screen)
        self.back_button.draw(self.screen)

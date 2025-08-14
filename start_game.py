import subprocess
import os
import sys
import time
import pygame
from login_screen import LoginScreen
from settings import *

def start_server():
    """Inicia o servidor em uma nova janela"""
    if os.name == 'nt':  # Windows
        subprocess.Popen(['start', 'cmd', '/k', 'python', 'network/server.py'], shell=True)
    else:  # Linux/Mac
        subprocess.Popen(['gnome-terminal', '--', 'python3', 'network/server.py'])
    print("Servidor iniciado na porta 5000")

def main():
    # Iniciar servidor
    print("Iniciando servidor...")
    start_server()
    time.sleep(2)  # Aguardar servidor iniciar
    
    # Iniciar Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MMORPG 2D - Login")
    clock = pygame.time.Clock()
    
    # Criar tela de login
    login_screen = LoginScreen(screen)
    
    print("Cliente iniciado. Aguardando login...")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            login_screen.handle_events(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if login_screen.login():
                        print("Login bem-sucedido! Iniciando jogo...")
                        # Aqui você pode iniciar o jogo principal
                        running = False
        
        # Desenhar
        login_screen.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()

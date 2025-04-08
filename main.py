# Importando bibliotecas necessárias
import pygame
import random

# Inicializando o Pygame
pygame.init()

# Definindo constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Cor para recursos alienígenas
BROWN = (139, 69, 19)  # Cor para o solo

# Configurando a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MMORPG 2D Prototype")

# Definindo variáveis do jogador
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5

# Lista de recursos alienígenas
alien_resources = []
inventory = {}  # Dicionário para armazenar recursos e suas quantidades
max_inventory_slots = 10  # Número máximo de slots no inventário

# Carregar sprites de animação
player_idle = pygame.image.load("data/Bot Wheel/static idle.png")  # Sprite de idle
player_walk_left = pygame.image.load("data/Bot Wheel/move with FX.png")  # Sprite de andar para a esquerda
player_walk_right = pygame.image.load("data/Bot Wheel/move with FX.png")  # Sprite de andar para a direita

# Função para gerar recursos alienígenas
def generate_alien_resources():
    for _ in range(5):  # Gerar 5 recursos
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        alien_resources.append((x, y))

# Função para coletar recursos
def collect_resources():
    global player_pos, inventory
    for resource in alien_resources[:]:  # Iterar sobre uma cópia da lista
        if (player_pos[0] < resource[0] + 10 and player_pos[0] > resource[0] - 10 and
            player_pos[1] < resource[1] + 10 and player_pos[1] > resource[1] - 10):
            alien_resources.remove(resource)  # Remover recurso coletado
            resource_type = "alien_resource"  # Tipo de recurso coletado
            if resource_type in inventory:
                inventory[resource_type] += 1  # Incrementar contador
            else:
                inventory[resource_type] = 1  # Adicionar novo recurso ao inventário

# Função para exibir o inventário
def display_inventory():
    font = pygame.font.Font(None, 36)
    y_offset = 10
    for resource, count in inventory.items():
        text = font.render(f"{resource}: {count}", True, BLACK)
        screen.blit(text, (10, y_offset))
        y_offset += 30

# Função para desenhar o mapa
def draw_map():
    for x in range(0, SCREEN_WIDTH, 50):  # Desenhar linhas horizontais
        for y in range(0, SCREEN_HEIGHT, 50):  # Desenhar linhas verticais
            if random.random() < 0.1:  # 10% de chance de desenhar um obstáculo
                pygame.draw.rect(screen, BROWN, (x, y, 50, 50))  # Desenhar solo

# Função para exibir a tela de início
def display_start_screen():
    font = pygame.font.Font(None, 74)
    title_text = font.render("MMORPG 2D", True, BLACK)
    start_text = font.render("Pressione ENTER para Iniciar", True, BLACK)
    
    screen.fill(WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

# Função principal do jogo
def main():
    generate_alien_resources()  # Gerar recursos no início
    clock = pygame.time.Clock()
    running = True
    game_started = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Iniciar o jogo ao pressionar ENTER
                    game_started = True

        if not game_started:
            display_start_screen()  # Exibir tela de início
        else:
            # Capturando teclas pressionadas
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_pos[0] -= player_speed
            if keys[pygame.K_RIGHT]:
                player_pos[0] += player_speed
            if keys[pygame.K_UP]:
                player_pos[1] -= player_speed
            if keys[pygame.K_DOWN]:
                player_pos[1] += player_speed

            # Coletar recursos
            collect_resources()

            # Preenchendo a tela com a cor branca
            screen.fill(WHITE)

            # Desenhar o mapa
            draw_map()

            # Desenhando o jogador com o sprite atual
            screen.blit(player_idle, (player_pos[0], player_pos[1]))  # Usar sprite de idle

            # Desenhando recursos alienígenas
            for resource in alien_resources:
                pygame.draw.circle(screen, GREEN, resource, 10)  # Desenhar recursos como círculos

            # Exibir inventário
            display_inventory()

            # Atualizando a tela
            pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

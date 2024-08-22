import pygame
import math
import time

# Inicialização do Pygame
pygame.init()

# Definindo o tamanho da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Birds no Espaço")

# Carregando texturas e sons
background_texture = pygame.image.load("background.png").convert()
cannon_texture = pygame.image.load("cannon.png").convert_alpha()
projectile_texture = pygame.image.load("projectile.png").convert_alpha()
target_texture = pygame.image.load("target.png").convert_alpha()
celestial_texture = pygame.image.load("celestial.png").convert_alpha()

# Redimensionando texturas
cannon_texture = pygame.transform.scale(cannon_texture, (50, 50))
projectile_texture = pygame.transform.scale(projectile_texture, (30, 30))  # Aumentado
target_texture = pygame.transform.scale(target_texture, (60, 60))  # Mantido
celestial_texture = pygame.transform.scale(celestial_texture, (60, 60))
background_texture = pygame.transform.scale(background_texture, (WIDTH, HEIGHT))

# Carregando e configurando a trilha sonora e efeitos sonoros
pygame.mixer.music.load("satriani.mp3")
pygame.mixer.music.set_volume(0.5)  # Volume da música (0.0 a 1.0)
pygame.mixer.music.play(-1)  # Toca a música em loop

shot_sound = pygame.mixer.Sound("shot_sound.wav")
hit_sound = pygame.mixer.Sound("hit_sound.wav")

# Configurações do canhão
cannon_pos = (100, HEIGHT - 100)
cannon_angle = 0
cannon_power = 100
gravity = 3.8  # gravidade simulada
max_power = 100  # Potência máxima

# Inicializa a pontuação
score = 0
font = pygame.font.SysFont(None, 36)  # Fonte para a pontuação

# Função para desenhar texto
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def menu_screen():
    global gravity, cannon_power
    menu_running = True
    while menu_running:
        screen.blit(background_texture, (0, 0))
        draw_text('Menu', font, (255, 255, 255), screen, WIDTH // 2, 50)
        draw_text(f'Gravidade: {gravity:.1f}', font, (255, 255, 255), screen, WIDTH // 2, 150)
        draw_text(f'Potência do Canhão: {cannon_power}', font, (255, 255, 255), screen, WIDTH // 2, 200)
        draw_text('Pressione UP/DOWN para ajustar a gravidade', font, (255, 255, 255), screen, WIDTH // 2, 300)
        draw_text('Pressione LEFT/RIGHT para ajustar a potência', font, (255, 255, 255), screen, WIDTH // 2, 350)
        draw_text('Pressione ENTER para iniciar', font, (255, 255, 255), screen, WIDTH // 2, 400)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    gravity += 0.1
                if event.key == pygame.K_DOWN:
                    gravity -= 0.1
                if event.key == pygame.K_LEFT:
                    cannon_power = max(0, cannon_power - 1)
                if event.key == pygame.K_RIGHT:
                    cannon_power = min(max_power, cannon_power + 1)
                if event.key == pygame.K_RETURN:
                    menu_running = False
    return True


# Classe para representar o objeto lançado
class Projectile:
    def __init__(self, pos, angle, power):
        self.x, self.y = pos
        self.angle = angle
        self.power = power
        self.vx = power * math.cos(math.radians(angle))
        self.vy = -power * math.sin(math.radians(angle))
        self.radius = 15  # Aumentado
        self.image = projectile_texture

    def update(self, celestial_bodies):
        # Atualiza a posição do projétil com movimento
        self.x += self.vx
        self.y += self.vy

        # Adiciona o efeito da gravidade global
        self.vy += gravity * 0.1  # ajuste para o intervalo de tempo
        
        # Calcula o efeito de cada corpo celeste
        for body in celestial_bodies:
            dx = body.x - self.x
            dy = body.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                force = body.mass / (distance ** 2)
                angle = math.atan2(dy, dx)
                self.vx += math.cos(angle) * force
                self.vy += math.sin(angle) * force

    def draw(self, screen):
        screen.blit(self.image, (int(self.x) - self.radius, int(self.y) - self.radius))

    def check_collision(self, target):
        # Verifica colisão simples entre o projétil e o alvo
        distance = math.hypot(self.x - target.x, self.y - target.y)
        return distance <= self.radius + target.radius

# Classe para representar o alvo
class Target:
    def __init__(self, pos, radius=30, speed=(2, 0)):
        self.x, self.y = pos
        self.radius = radius
        self.vx, self.vy = speed
        self.image = target_texture

    def update(self, celestial_bodies):
        # Calcula a força gravitacional de cada corpo celeste
        for body in celestial_bodies:
            dx = body.x - self.x
            dy = body.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                force = body.mass / ((distance ** 2) + math.pow(10, -5))
                angle = math.atan2(dy, dx)
                self.vx += math.cos(angle) * force
                self.vy += math.sin(angle) * force

        # Atualiza a posição do alvo com movimento uniforme
        self.x += self.vx
        self.y += self.vy

        # Verifica colisão com as bordas da tela e inverte a direção
        if self.x - self.radius < 0 or self.x + self.radius > WIDTH:
            self.vx = -self.vx
        if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
            self.vy = -self.vy

    def draw(self, screen):
        screen.blit(self.image, (int(self.x) - self.radius, int(self.y) - self.radius))

# Classe para representar um corpo celeste que exerce atração gravitacional
class CelestialBody:
    def __init__(self, pos, mass, radius=30):
        self.x, self.y = pos
        self.mass = mass
        self.radius = radius
        self.image = celestial_texture

    def draw(self, screen):
        screen.blit(self.image, (int(self.x) - self.radius, int(self.y) - self.radius))

def draw_cannon(screen, pos, angle):
    rotated_image = pygame.transform.rotate(cannon_texture, angle)
    new_rect = rotated_image.get_rect(center=cannon_texture.get_rect(topleft=(pos[0] - 25, pos[1] - 25)).center)
    screen.blit(rotated_image, new_rect.topleft)
##############################################################################################################
def game_loop():
    global gravity, cannon_power, max_power, score

    cannon_angle = 0
    # Configurações do alvo e corpos celestes
    target_pos = (WIDTH - 100, HEIGHT // 2)
    target = Target(target_pos, radius=30, speed=(2, 1))  # Mantido o raio do alvo

    # Configuração dos corpos celestes para diferentes níveis
    levels = [
        [CelestialBody((WIDTH // 2, HEIGHT // 2), mass=2000)],  # Nível 1: um corpo celeste
        [CelestialBody((WIDTH // 2, HEIGHT // 2), mass=2000),
        CelestialBody((200, 200), mass=1500)],  # Nível 2: dois corpos celestes
        [CelestialBody((WIDTH // 2, HEIGHT // 2), mass=2000),
        CelestialBody((200, 200), mass=1500),
        CelestialBody((600, 400), mass=1000)],  # Nível 3: três corpos celestes
    ]

    current_level = 0
    celestial_bodies = levels[current_level]

    # Loop principal do jogo
    running = True
    projectiles = []
    is_mouse_held = False
    mouse_hold_start = None  # Tempo em que o mouse foi pressionado
    while running:
        # Desenha a imagem de fundo
        screen.blit(background_texture, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Inicia o ajuste do ângulo e da potência quando o mouse é pressionado
                is_mouse_held = True
                mouse_hold_start = time.time()  # Registra o tempo em que o mouse foi pressionado
            elif event.type == pygame.MOUSEBUTTONUP:
                # Lança o projétil quando o botão do mouse é solto
                if is_mouse_held:
                    hold_duration = time.time() - mouse_hold_start  # Calcula o tempo em que o mouse foi segurado
                    cannon_power = min(max_power, hold_duration * 50)  # Ajusta a potência com base no tempo de pressão
                    projectile = Projectile(cannon_pos, cannon_angle, cannon_power)
                    projectiles.append(projectile)
                    shot_sound.play()  # Toca o som do disparo
                is_mouse_held = False
                mouse_hold_start = None
            elif event.type == pygame.MOUSEMOTION:
                if is_mouse_held:
                    # Ajusta o ângulo do canhão baseado na posição do mouse
                    mouse_x, mouse_y = event.pos
                    cannon_angle = math.degrees(math.atan2(cannon_pos[1] - mouse_y, mouse_x - cannon_pos[0]))

        # Atualiza e desenha os projéteis
        for projectile in projectiles:
            projectile.update(celestial_bodies)
            projectile.draw(screen)
            if projectile.check_collision(target):
                hit_sound.play()  # Toca o som do acerto no alvo
                print("Alvo atingido!")
                score += 10  # Adiciona pontos à pontuação
                # Avança para o próximo nível se o alvo for atingido
                current_level += 1
                if current_level >= len(levels):
                    print("Você venceu!")
                    running = False
                else:
                    celestial_bodies = levels[current_level]
                projectiles.clear()  # Limpa projéteis existentes após acertar o alvo
                break
            # Penaliza o jogador se o projétil sair da tela sem atingir o alvo
            if projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT:
                projectiles.remove(projectile)
                score -= 3  # Penaliza com 3 pontos
                break

        # Atualiza e desenha o alvo
        target.update(celestial_bodies)
        target.draw(screen)
        
        # Desenha os corpos celestes
        for body in celestial_bodies:
            body.draw(screen)
        
        # Desenha o canhão
        draw_cannon(screen, cannon_pos, cannon_angle)
        
        # Desenha a pontuação
        score_text = font.render(f"Pontos: {score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH - 150, 10))
        
        pygame.display.flip()
        pygame.time.delay(30)

    # Executa a tela de menu
if menu_screen():
    try:
        game_loop()
    except Exception as e:
        print(f"Erro no loop do jogo: {e}")

pygame.quit()

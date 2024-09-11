import pygame
import random

# Inicializar PyGame
pygame.init()

# Configuración de la ventana
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Frames por segundo
FPS = 60

# Fuente de texto
font = pygame.font.SysFont("comicsans", 40)
font_large = pygame.font.SysFont("comicsans", 60)
font_small = pygame.font.SysFont("comicsans", 30)

# Variables globales
score = 0
high_score = 0

# Función para cargar y escalar imágenes con manejo de errores
def cargar_imagen(nombre_archivo, ancho, alto):
    try:
        imagen = pygame.image.load(nombre_archivo)
        imagen = pygame.transform.scale(imagen, (ancho, alto))
        return imagen
    except pygame.error as e:
        print(f"Error al cargar la imagen {nombre_archivo}: {e}")
        return None

# Cargar imágenes
PLAYER_SHIP = cargar_imagen("player_ship.png", 64, 64)
ENEMY_SHIP = cargar_imagen("enemy_ship.png", 50, 50)
BOSS_SHIP = cargar_imagen("boss_ship.png", 160, 160)
BULLET = cargar_imagen("bullet.png", 8, 16)
BOSS_BULLET = cargar_imagen("boss_bullet.png", 12, 24)
POWERUP_SHIELD = cargar_imagen("shield_powerup.png", 32, 32)
POWERUP_TRIPLE_SHOT = cargar_imagen("triple_shot_powerup.png", 32, 32)
POWERUP_EXTRA_LIFE = cargar_imagen("extra_life_powerup.png", 32, 32)
BACKGROUND = cargar_imagen("galaxy_background.jpg", WIDTH, HEIGHT)

# Clase para la Nave del Jugador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship_img = PLAYER_SHIP
        self.bullets = []
        self.cooldown = 0
        self.lives = 3
        self.shield = False
        self.triple_shot = False

    def draw(self, window):
        if self.ship_img:
            window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            pygame.draw.rect(window, WHITE, bullet)

    def move(self, vel):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x - vel > 0:
            self.x -= vel
        if keys[pygame.K_RIGHT] and self.x + vel + 64 < WIDTH:
            self.x += vel
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            self.shoot()

    def shoot(self):
        if len(self.bullets) < 5:
            if self.triple_shot:
                bullet1 = pygame.Rect(self.x + 64//2 - 2, self.y, 4, 10)
                bullet2 = pygame.Rect(self.x + 64//2 - 15, self.y, 4, 10)
                bullet3 = pygame.Rect(self.x + 64//2 + 10, self.y, 4, 10)
                self.bullets.extend([bullet1, bullet2, bullet3])
            else:
                bullet = pygame.Rect(self.x + 64//2 - 2, self.y, 4, 10)
                self.bullets.append(bullet)
        self.cooldown = 20

    def handle_bullets(self, vel, enemies, boss, powerups):
        global score
        for bullet in self.bullets:
            bullet.y -= vel
            if bullet.y < 0:
                self.bullets.remove(bullet)
            else:
                for enemy in enemies:
                    if enemy.ship_img and bullet.colliderect(pygame.Rect(enemy.x, enemy.y, 50, 50)):
                        enemies.remove(enemy)
                        score += 100
                        if random.random() < 0.3:  # 30% de probabilidad de generar un power-up
                            powerup_type = random.choice(['shield', 'triple_shot', 'extra_life'])
                            powerup = PowerUp(enemy.x, enemy.y, powerup_type)
                            powerups.append(powerup)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

                if boss and bullet.colliderect(pygame.Rect(boss.x, boss.y, 160, 160)):
                    boss.lives -= 1
                    score += 200
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

    def cooldown_tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

# Clase para los Enemigos
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship_img = ENEMY_SHIP
        self.bullets = []

    def move(self, vel):
        self.y += vel
        if random.randint(0, 100) < 2:  # Ajusta la probabilidad para disparar
            self.shoot()

    def shoot(self):
        bullet = pygame.Rect(self.x + 50//2 - 2, self.y + 50, 4, 10)
        self.bullets.append(bullet)

    def handle_bullets(self, vel, player):
        for bullet in self.bullets:
            bullet.y += vel
            if bullet.y > HEIGHT:
                self.bullets.remove(bullet)
            elif bullet.colliderect(pygame.Rect(player.x, player.y, 64, 64)):
                if player.shield:
                    player.shield = False
                else:
                    player.lives -= 1
                self.bullets.remove(bullet)

    def draw(self, window):
        if self.ship_img:
            window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            pygame.draw.rect(window, RED, bullet)

# Clase para el Jefe (Boss)
class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ship_img = BOSS_SHIP
        self.bullets = []
        self.lives = 20
        self.direction = random.choice([-1, 1])

    def move(self, vel):
        self.x += vel * self.direction
        if self.x <= 0 or self.x + 160 >= WIDTH:
            self.direction *= -1

        if random.randint(0, 500) < 5:
            self.y += 10

        if self.y >= HEIGHT // 2:
            self.y -= 20

    def shoot(self):
        if len(self.bullets) < 3:
            bullet = pygame.Rect(self.x + 160//2 - 6, self.y + 160, 12, 24)
            self.bullets.append(bullet)

    def handle_bullets(self, vel, player):
        for bullet in self.bullets:
            bullet.y += vel
            if bullet.colliderect(pygame.Rect(player.x, player.y, 64, 64)):
                if player.shield:
                    player.shield = False
                else:
                    player.lives -= 1
                self.bullets.remove(bullet)

    def draw(self, window):
        if self.ship_img:
            window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            pygame.draw.rect(window, RED, bullet)

# Clase para los PowerUps
class PowerUp:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.img = {
            'shield': POWERUP_SHIELD,
            'triple_shot': POWERUP_TRIPLE_SHOT,
            'extra_life': POWERUP_EXTRA_LIFE
        }[tipo]
        self.rect = pygame.Rect(x, y, 32, 32)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def fall(self, vel):
        self.y += vel
        self.rect.y = self.y

# Función para mostrar el menú principal
def main_menu():
    global high_score
    while True:
        win.fill(BLACK)
        title = font_large.render("Space Invaders", 1, WHITE)
        win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        play_text = font_small.render("Presione ENTER para jugar", 1, WHITE)
        win.blit(play_text, (WIDTH//2 - play_text.get_width()//2, HEIGHT//2))
        instructions_text = font_small.render("Presione I para instrucciones", 1, WHITE)
        win.blit(instructions_text, (WIDTH//2 - instructions_text.get_width()//2, HEIGHT//2 + 50))
        exit_text = font_small.render("Presione ESC para salir", 1, WHITE)
        win.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 100))

        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if keys[pygame.K_RETURN]:
                game_loop()
            if keys[pygame.K_i]:
                instructions_menu()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                quit()

# Función para mostrar el menú de instrucciones
def instructions_menu():
    while True:
        win.fill(BLACK)
        instructions = [
            "Instrucciones:",
            "1. Usa las flechas izquierda y derecha para mover la nave.",
            "2. Presiona ESPACIO para disparar.",
            "3. El objetivo es destruir a los enemigos y al jefe.",
            "4. Recoge power-ups para obtener ventajas.",
            "5. El juego termina cuando pierdes todas las vidas."
        ]
        y_offset = 50
        for line in instructions:
            text = font_small.render(line, 1, WHITE)
            win.blit(text, (50, y_offset))
            y_offset += 40

        back_text = font_small.render("Presione ESC para volver", 1, WHITE)
        win.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 50))

        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if keys[pygame.K_ESCAPE]:
                return

# Función para mostrar el menú de Game Over
def game_over_menu(final_score):
    global score
    while True:
        win.fill(BLACK)
        game_over_text = font_large.render("Game Over", 1, WHITE)
        win.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        score_text = font_small.render(f"Tu puntuación: {final_score}", 1, WHITE)
        win.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        high_score_text = font_small.render(f"Puntuación más alta: {high_score}", 1, WHITE)
        win.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 50))
        restart_text = font_small.render("Presione ENTER para reiniciar", 1, WHITE)
        win.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 100))
        exit_text = font_small.render("Presione ESC para salir", 1, WHITE)
        win.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 150))

        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if keys[pygame.K_RETURN]:
                score = 0  # Reiniciar el puntaje
                return
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                quit()

# Función para mostrar el menú de pausa
def pause_menu():
    while True:
        win.fill(BLACK)
        pause_text = font_large.render("PAUSA", 1, WHITE)
        win.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 100))
        resume_text = font_small.render("Presione ENTER para reanudar", 1, WHITE)
        win.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2))
        exit_text = font_small.render("Presione ESC para salir", 1, WHITE)
        win.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 50))

        pygame.display.update()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if keys[pygame.K_RETURN]:
                return
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                quit()

# Función principal del juego
def game_loop():
    global score, high_score
    score = 0  # Reiniciar el puntaje al comenzar una nueva partida
    clock = pygame.time.Clock()
    run = True

    # Crear jugador y enemigos
    player = Player(WIDTH // 2 - 32, HEIGHT - 100)
    enemies = [Enemy(random.randint(0, WIDTH - 50), random.randint(-1500, -50)) for _ in range(10)]
    boss = None
    powerups = []

    while run:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_menu()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

        # Lógica del juego
        player.move(5)
        player.cooldown_tick()

        if boss:
            boss.move(3)
            boss.handle_bullets(5, player)
            if boss.lives <= 0:
                boss = None  # Destruir al boss si tiene 0 vidas
                score += 1000  # Bonificación por destruir al boss
        else:
            if random.random() < 0.01:
                boss = Boss(WIDTH // 2 - 80, -160)

        for enemy in enemies:
            enemy.move(2)
            enemy.handle_bullets(5, player)
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                enemies.append(Enemy(random.randint(0, WIDTH - 50), random.randint(-1500, -50)))

        for powerup in powerups:
            powerup.fall(3)
            if powerup.rect.colliderect(pygame.Rect(player.x, player.y, 64, 64)):
                if powerup.tipo == 'shield':
                    player.shield = True
                elif powerup.tipo == 'triple_shot':
                    player.triple_shot = True
                elif powerup.tipo == 'extra_life':
                    player.lives += 1
                powerups.remove(powerup)

        player.handle_bullets(10, enemies, boss, powerups)

        if player.lives <= 0:
            high_score = max(score, high_score)
            game_over_menu(score)
            return

        # Dibujar en la pantalla
        win.blit(BACKGROUND, (0, 0))
        player.draw(win)
        for enemy in enemies:
            enemy.draw(win)
        if boss:
            boss.draw(win)
        for powerup in powerups:
            powerup.draw(win)

        # Mostrar puntuación
        score_text = font.render(f"Score: {score}", 1, WHITE)
        win.blit(score_text, (10, 10))

        lives_text = font.render(f"Lives: {player.lives}", 1, WHITE)
        win.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))

        pygame.display.update()

# Menú principal
main_menu()
    
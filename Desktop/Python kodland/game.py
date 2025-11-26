import pgzrun
import math
import random
from pygame import Rect

# --- CONFIGURAÇÕES & CONSTANTES ---
WIDTH = 800
HEIGHT = 600
TITLE = "Rabbit Adventure"

TILE_SIZE = 48
GRAVITY = 1
JUMP_STRENGTH = -16
MOVE_SPEED = 5
BULLET_SPEED = 12

# Estados do Jogo
GAME_STATE = "MENU" # MENU, GAME, GAMEOVER
SOUND_ENABLED = True

# --- MAPA DO NÍVEL ---
# W = Grama, T = Terra, C = Caixa, P = Player
# A = Inimigo Azul, B = Inimigo Abelha, G = Arma
level_map = [
    "..................................................",
    "..................................................",
    "..................................................",
    "........................B.........................",
    "W...CC..B..............CCC..C...B................W",
    "T.......CC..A..C.....B..........C...C............T",
    "T.........C.......CCC..............A....CCC......T",
    "T...............................A................T",
    "T...G...............B......B...WWWWWWW..........WT",
    "TP......A........A.............TTTTTTT..........TT",
    "TWWWWWWWWWWW...WWWWWWWWWW...WWWTTTTTTTWWWWWWWWWWTT",
    "TTTTTTTTTTTT...TTTTTTTTTT...TTTTTTTTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTT...TTTTTTTTTT...TTTTTTTTTTTTTTTTTTTTTT"
]

# --- VARIÁVEIS GLOBAIS ---
camera_x = 0
walls = []
enemies = []
bullets = []
impacts = [] 
items = []
player = None

# --- BOTÕES DO MENU (Classe Rect permitida) ---
btn_start = Rect(300, 200, 200, 50)
btn_sound = Rect(300, 300, 200, 50)
btn_exit = Rect(300, 400, 200, 50)

# --- CLASSES ---

class GameSprite(Actor):
    """ Classe base para gerenciar animação de sprites automaticamente """
    def __init__(self, img_idle_list, img_move_list, x, y):
        super().__init__(img_idle_list[0], pos=(x, y))
        self.img_idle_list = img_idle_list # Lista de imagens parado
        self.img_move_list = img_move_list # Lista de imagens movendo
        self.anim_timer = 0
        self.current_frame = 0
        self.is_moving = False
        self.facing_left = False

    def animate(self):
        # Avança o frame a cada 10 ticks (ajuste velocidade aqui)
        self.anim_timer += 1
        if self.anim_timer > 8:
            self.anim_timer = 0
            self.current_frame += 1
        
        # Escolhe a lista correta
        if self.is_moving:
            lst = self.img_move_list
        else:
            lst = self.img_idle_list
            
        # Pega a imagem correta (usando módulo para loop infinito)
        img_name = lst[self.current_frame % len(lst)]
        
        # Aplica a imagem e direção
        self.image = img_name
        
        # Espelhamento manual (se a imagem original olha para a direita)
        if self.facing_left:
             # Nota: PgZero não tem flip fácil nativo sem Pygame Surface, 
             if not img_name.endswith("_left"):
                 self.image = img_name + "_left"
        else:
             if img_name.endswith("_left"):
                 self.image = img_name.replace("_left", "")

class Hero(GameSprite):
    def __init__(self, x, y):
        # Define as listas de animação. Certifique-se que estes arquivos existem!
        # Ex: heroi1.png, heroi2.png
        idle_imgs = ["heroi1"] 
        move_imgs = ["heroi1", "heroi2"]
        super().__init__(idle_imgs, move_imgs, x, y)
        self.anchor = ('center', 'bottom')
        
        # Física
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.has_gun = False
        self.recoil_timer = 0

        # Respiração
        self.breath_counter = 0

    def update_hero(self):
        # 1. Checa morte (buraco)
        if self.y > 800:
            setup_level()
            return

        # 2. Respiração
        self.breath_counter += 1

        # 3. Recuo
        if self.recoil_timer > 0:
            self.recoil_timer -= 1

        # 4. Controles
        if keyboard.left:
            self.vx = -MOVE_SPEED
            self.is_moving = True
            self.facing_left = True
        elif keyboard.right:
            self.vx = MOVE_SPEED
            self.is_moving = True
            self.facing_left = False
        else:
            self.vx = 0
            self.is_moving = False

        # Pulo
        if keyboard.space and self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False
            if SOUND_ENABLED:
                # sounds.jump.play() # Descomente se tiver o som
                pass

        # 5. Física Vertical
        self.vy += GRAVITY
        if self.vy > 12: self.vy = 12

        # 6. Movimento e Colisão
        self.apply_movement()
        
        # 7. Coleta de Arma
        self.check_item_collision()

        # 8. Atualiza Animação
        # Se estiver atirando, sobrescreve a animação padrão
        if self.has_gun and self.recoil_timer > 0:
            self.image = "heroiatirando"
            if self.facing_left: self.image += "_left"
        elif self.has_gun:
             # Atualiza as listas base para usar versão com arma
             self.img_idle_list = ["heroiarma1"]
             self.img_move_list = ["heroiarma1", "heroiarma2"]
             self.animate()
        else:
             self.animate()

    def apply_movement(self):
        # Eixo X
        self.x += self.vx
        if self.collidelist(walls) != -1:
            self.x -= self.vx
        
        # Eixo Y
        self.y += self.vy
        index = self.collidelist(walls)
        if index != -1:
            wall = walls[index]
            if self.vy > 0: 
                self.bottom = wall.top
                self.on_ground = True
                self.vy = 0
            elif self.vy < 0: 
                self.top = wall.bottom
                self.vy = 0
        else:
            self.on_ground = False

    def check_item_collision(self):
        for item in items[:]:
            if self.colliderect(item):
                if "arma" in item.image: 
                    self.has_gun = True
                    items.remove(item)
                    if SOUND_ENABLED:
                        # sounds.pickup.play()
                        pass

    def shoot(self):
        if self.has_gun:
            self.recoil_timer = 10 
            if SOUND_ENABLED:
                # sounds.shoot.play()
                pass
            
            b_y = self.y - 25
            offset_x = 25 if not self.facing_left else -25
            b_x = self.x + offset_x
            b_speed = BULLET_SPEED if not self.facing_left else -BULLET_SPEED
            img_bala = "bala" if not self.facing_left else "bala_left"
            
            bullet = Bullet(b_x, b_y, b_speed, img_bala)
            bullets.append(bullet)

    def draw(self):
        # 1. Calcula animação
        breath_offset = 0
        if self.on_ground and not self.is_moving:
            breath_offset = math.sin(self.breath_counter * 0.1) * 2

        # 2. Modifica a posição TEMPORARIAMENTE
        self.x -= camera_x      # Aplica câmera
        self.y += breath_offset # Aplica respiração

        # 3. Desenha
        super().draw()

        # 4. RESTAURA a posição (CRUCIAL!)
        # Se esquecer isso aqui, ele cai do mapa mesmo!
        self.y -= breath_offset 
        self.x += camera_x        

class Enemy(GameSprite):
    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        base = f"inimigo{enemy_type}" # ex: inimigoazul
        # Define listas de animação
        idles = [f"{base}1"]
        moves = [f"{base}1", f"{base}2"]
        
        super().__init__(idles, moves, x, y)
        self.anchor = ('left', 'bottom')
        self.start_y = y

        # --- LÓGICA DE DESINCRONIZAÇÃO (ASSÍNCRONA) ---
        
        # 1. Velocidade Variável (Opcional, mas ajuda muito)
        # Alguns são um pouco mais rápidos (ex: entre 1.5 e 2.5)
        # Usamos round() para não quebrar muito o pixel art
        speed_variation = random.choice([1.5, 2, 2.5])

        # 2. Direção Inicial Aleatória
        # Escolhe aleatoriamente 1 (direita) ou -1 (esquerda)
        initial_direction = random.choice([-1, 1])

        self.vx = speed_variation * initial_direction
        
        # 3. Fase da Patrulha ("Já andei um pouco")
        # Define que o inimigo já "caminhou" uma parte aleatória da rota
        # Isso garante que eles não cheguem na parede todos juntos
        self.max_dist = 200
        self.dist_traveled = random.randint(0, int(self.max_dist / 2))
        
        # 4. Desincronizar Animação
        # Inicia o timer em um número aleatório para não trocarem sprites juntos
        self.anim_timer = random.randint(0, 8)
        
        self.is_moving = True
        self.facing_left = (self.vx < 0)

    # O método update_enemy permanece o mesmo, 
    # mas agora ele obedece aos valores aleatórios definidos acima.

    def update_enemy(self):
        self.animate()
        
        # Movimento de Patrulha
        self.x += self.vx
        self.dist_traveled += abs(self.vx)
        
        # Inverte direção por distância
        if self.dist_traveled > self.max_dist:
            self.vx *= -1
            self.dist_traveled = 0
            
        if self.enemy_type == "azul" or self.enemy_type == "abelha":
            # math.sin cria uma onda entre -1 e 1
            # Multiplicamos por 5 para a onda ter 5 pixels de altura (amplitude)
            # O self.anim_timer faz a onda se mover com o tempo
            oscillation = math.sin(self.anim_timer * 0.05) * 5
            self.y = self.start_y + oscillation

        if self.collidelist(walls) != -1:
            self.vx *= -1
        
        self.facing_left = (self.vx < 0)

class Bullet(Actor):
    def __init__(self, x, y, speed, image_name):
        super().__init__(image_name, pos=(x, y))
        self.vx = speed
        
    def update(self):
        self.x += self.vx

class ImpactEffect(Actor):
    def __init__(self, x, y, direction):
        img = "balaacertando"
        if direction == "left": img += "_left"
        super().__init__(img, pos=(x, y))
        self.life_time = 10 

    def update(self):
        self.life_time -= 1

# --- FUNÇÕES DE GERENCIAMENTO ---

def setup_level():
    global player
    walls.clear()
    enemies.clear()
    items.clear()
    bullets.clear()
    impacts.clear()
    
    for row_index, row in enumerate(level_map):
        for col_index, char in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            
            if char == "W":
                walls.append(Actor("chaoreto", anchor=('left', 'top'), pos=(x, y)))
            elif char == "T":
                walls.append(Actor("terra", anchor=('left', 'top'), pos=(x, y)))
            elif char == "C":
                walls.append(Actor("chaoreto2", anchor=('left', 'top'), pos=(x, y)))
            elif char == "P":
                player = Hero(x + TILE_SIZE/2, y + TILE_SIZE)
            elif char == "A":
                enemies.append(Enemy(x, y + TILE_SIZE/2, "azul"))
            elif char == "B":
                enemies.append(Enemy(x, y + TILE_SIZE/2, "abelha"))
            elif char == "G":
                items.append(Actor("arma", anchor=('center', 'center'), pos=(x + TILE_SIZE/2, y + TILE_SIZE/2)))

def create_impact(x, y, direction):
    impact = ImpactEffect(x, y, direction)
    impacts.append(impact)

# --- LOOP PRINCIPAL (UPDATE) ---

def update():
    if GAME_STATE == "GAME":
        update_game()
    # No Menu não precisa de update complexo

def update_game():
    global camera_x
    
    if player:
        player.update_hero()
        
        # Câmera
        target_camera = player.x - WIDTH / 2
        camera_x = target_camera
        map_width = len(level_map[0]) * TILE_SIZE
        if camera_x < 0: camera_x = 0
        if camera_x > map_width - WIDTH: camera_x = map_width - WIDTH

    # Atualiza inimigos
    for enemy in enemies:
        enemy.update_enemy()
        if player.colliderect(enemy):
            setup_level() 

    # Atualiza balas
    for bullet in bullets[:]:
        bullet.update()
        bullet_direction = "left" if bullet.vx < 0 else "right"
        bullet_removed = False

        # Colisão Bala -> Inimigo
        index = bullet.collidelist(enemies)
        if index != -1:
            enemy = enemies[index]
            create_impact(bullet.x, bullet.y, bullet_direction)
            enemies.pop(index)
            bullet_removed = True

        # Colisão Bala -> Parede
        if not bullet_removed and bullet.collidelist(walls) != -1:
            create_impact(bullet.x, bullet.y, bullet_direction)
            bullet_removed = True
            
        if bullet_removed or abs(bullet.x - player.x) > WIDTH:
            if bullet in bullets:
                bullets.remove(bullet)

    # Atualiza efeitos
    for impact in impacts[:]:
        impact.update()
        if impact.life_time <= 0:
            impacts.remove(impact)

# --- LOOP DE DESENHO (DRAW) ---

def draw():
    screen.clear()
    
    if GAME_STATE == "MENU":
        draw_menu()
    elif GAME_STATE == "GAME":
        draw_game()

def draw_menu():
    # Fundo simples
    screen.fill((50, 50, 100))
    screen.draw.text("Rabbit Adventure", center=(WIDTH/2, 100), fontsize=60, color="yellow")
    
    # Botão Iniciar
    screen.draw.filled_rect(btn_start, "green")
    screen.draw.text("JOGAR", center=btn_start.center, fontsize=30, color="white")
    
    # Botão Som
    color_sound = "blue" if SOUND_ENABLED else "red"
    text_sound = "SOM: ON" if SOUND_ENABLED else "SOM: OFF"
    screen.draw.filled_rect(btn_sound, color_sound)
    screen.draw.text(text_sound, center=btn_sound.center, fontsize=30, color="white")
    
    # Botão Sair
    screen.draw.filled_rect(btn_exit, "gray")
    screen.draw.text("SAIR", center=btn_exit.center, fontsize=30, color="white")

def draw_game():
    screen.fill((100, 170, 255))
    
    # Desenha objetos com ajuste da câmera
    # Método: mover temporariamente para desenhar (padrão em PgZero simples)
    
    # Paredes
    for wall in walls:
        wall.x -= camera_x
        wall.draw()
        wall.x += camera_x
        
    # Itens
    for item in items:
        item.x -= camera_x
        item.draw()
        item.x += camera_x
        
    # Inimigos
    for enemy in enemies:
        enemy.x -= camera_x
        enemy.draw()
        enemy.x += camera_x
        
    # Balas
    for bullet in bullets:
        bullet.x -= camera_x
        bullet.draw()
        bullet.x += camera_x
        
    # Efeitos
    for impact in impacts:
        impact.x -= camera_x
        impact.draw()
        impact.x += camera_x
        
    # Jogador
    if player:
        player.draw()

# --- ENTRADAS (INPUTS) ---

def on_key_down(key):
    if GAME_STATE == "GAME" and player:
        if key == keys.Z:
            player.shoot()

def on_mouse_down(pos):
    global GAME_STATE, SOUND_ENABLED
    
    if GAME_STATE == "MENU":
        if btn_start.collidepoint(pos):
            setup_level()
            GAME_STATE = "GAME"
            if SOUND_ENABLED:
                music.play("musiclostwoods.mp3") 
                pass
        
        elif btn_sound.collidepoint(pos):
            SOUND_ENABLED = not SOUND_ENABLED
            if SOUND_ENABLED:
                music.unpause()
                pass
            else:
                music.pause()
                pass
                
        elif btn_exit.collidepoint(pos):
            quit()
pgzrun.go()
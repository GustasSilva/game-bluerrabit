import pgzrun
from pygame import Rect

# --- CONFIGURAÇÕES ---
WIDTH = 800
HEIGHT = 600
TITLE = "Alien Adventure"

TILE_SIZE = 48
GRAVITY = 1
JUMP_STRENGTH = -16
MOVE_SPEED = 5
BULLET_SPEED = 12

# --- MAPA DO NÍVEL ---
# W = Grama (chaoreto)
# T = Terra (terra)
# C = Caixa/Plataforma
# P = Player
# A = Inimigo Azul (Chão)
# B = Inimigo Abelha (Voador)
# G = Arma (Gun)
level_map = [
    "..................................................",
    "..................................................",
    "..................................................",
    "........................B.........................",
    "....CC..B..............CCC..C...B.................",
    "........CC..A..C.....B..........C...C.............",
    "..........C.......CCC..............A....CCC.......",
    "................................A.................",
    "....G...............B......B...WWWWWWW............",
    "P.......A........A.............T.....T............",
    "WWWWWWWWWWWW...WWWWWWWWWW...WWWT.....TWWWWWWWWWWWW",
    "TTTTTTTTTTTT...TTTTTTTTTT...TTTT.....TTTTTTTTTTTTT" 
]

# --- VARIÁVEIS GLOBAIS ---
camera_x = 0
walls = []
enemies = []
bullets = []
impacts = [] 
items = []
hero = None

# --- CLASSES ---

class Hero:
    def __init__(self, x, y):
        self.actor = Actor("heroi1", anchor=('center', 'bottom'))
        self.actor.pos = (x, y)
        
        # Física
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.direction = "right"
        self.has_gun = False
        
        # Estado de Animação
        self.anim_timer = 0
        self.walk_frame = 1 
        self.recoil_timer = 0 

    def update(self):
        # 1. Resetar Jogo se cair no buraco
        # (Mapa tem 12 linhas * 48px = 576px. Se passar de 700, caiu)
        if self.actor.y > 800:
            setup_level()
            return

        # 2. Recuo do tiro
        if self.recoil_timer > 0:
            self.recoil_timer -= 1

        # 3. Controles
        if keyboard.left:
            self.vx = -MOVE_SPEED
            self.direction = "left"
        elif keyboard.right:
            self.vx = MOVE_SPEED
            self.direction = "right"
        else:
            self.vx = 0

        # Pulo
        if keyboard.space and self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False

        # 4. Física Vertical
        self.vy += GRAVITY
        if self.vy > 12: self.vy = 12

        # 5. Movimento e Colisão
        self.apply_movement()

        # 6. Coleta de Arma
        self.check_item_collision()

        # 7. Atualiza Sprite
        self.animate()

    def apply_movement(self):
        # Eixo X
        self.actor.x += self.vx
        if self.actor.collidelist(walls) != -1:
            self.actor.x -= self.vx
        
        # Eixo Y
        self.actor.y += self.vy
        index = self.actor.collidelist(walls)
        if index != -1:
            wall = walls[index]
            if self.vy > 0: 
                self.actor.bottom = wall.top
                self.on_ground = True
                self.vy = 0
            elif self.vy < 0: 
                self.actor.top = wall.bottom
                self.vy = 0
        else:
            self.on_ground = False

    def check_item_collision(self):
        for item in items[:]:
            if self.actor.colliderect(item):
                if "arma" in item.image: 
                    self.has_gun = True
                    items.remove(item)

    def shoot(self):
        if self.has_gun:
            self.recoil_timer = 10 
            
            # CORREÇÃO 1: Ajuste de Spawn da Bala
            # Sobe mais (perto da cabeça/ombro) para não bater no chão
            b_y = self.actor.y - 25
            
            # Empurra a bala para frente para não nascer dentro da parede de trás
            offset_x = 25 if self.direction == "right" else -25
            b_x = self.actor.x + offset_x

            b_speed = BULLET_SPEED if self.direction == "right" else -BULLET_SPEED
            img_bala = "bala" if self.direction == "right" else "bala_left"
            
            bullet = Bullet(b_x, b_y, b_speed, img_bala)
            bullets.append(bullet)

    def animate(self):
        # 1. Base do nome
        if self.has_gun:
            if self.recoil_timer > 0:
                img_name = "heroiatirando"
            else:
                img_name = "heroiarma"
        else:
            img_name = "heroi"

        # 2. Lógica de frames (Andando vs Parado)
        # CORREÇÃO 4: Lógica estrita para IDLE
        if img_name != "heroiatirando":
            if self.vx != 0 and self.on_ground:
                # Se está movendo E no chão -> Animação 1 e 2
                self.anim_timer += 1
                if self.anim_timer > 8:
                    self.anim_timer = 0
                    self.walk_frame = 1 if self.walk_frame == 2 else 2
                img_name += str(self.walk_frame)
            else:
                # Se parou OU está pulando -> Trava no frame 1 (Idle)
                self.walk_frame = 1 
                img_name += "1"

        # 3. Direção
        if self.direction == "left":
            img_name += "_left"

        self.actor.image = img_name
        
    def draw(self):
        self.actor.x -= camera_x
        self.actor.draw()
        self.actor.x += camera_x

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.type = enemy_type
        self.base_name = f"inimigo{enemy_type}"
        self.actor = Actor(f"{self.base_name}1", anchor=('left', 'bottom'))
        self.actor.pos = (x, y)
        self.vx = 2
        self.dist_traveled = 0
        self.max_dist = 200
        self.direction = "right"
        self.anim_timer = 0
        self.frame = 1

    def update(self):
        self.actor.x += self.vx
        self.dist_traveled += abs(self.vx)
        
        if self.dist_traveled > self.max_dist:
            self.vx *= -1
            self.dist_traveled = 0
            
        if self.type == "azul":
            if self.actor.collidelist(walls) != -1:
                self.vx *= -1
                
        self.direction = "right" if self.vx > 0 else "left"
        
        self.anim_timer += 1
        if self.anim_timer > 10:
            self.anim_timer = 0
            self.frame = 1 if self.frame == 2 else 2
            
        img_name = f"{self.base_name}{self.frame}"
        if self.direction == "left":
            img_name += "_left"
            
        self.actor.image = img_name

    def draw(self):
        self.actor.x -= camera_x
        self.actor.draw()
        self.actor.x += camera_x

class Bullet:
    def __init__(self, x, y, speed, image_name):
        self.actor = Actor(image_name)
        self.actor.pos = (x, y)
        self.vx = speed
        
    def update(self):
        self.actor.x += self.vx

    def draw(self):
        self.actor.x -= camera_x
        self.actor.draw()
        self.actor.x += camera_x

class ImpactEffect:
    def __init__(self, x, y, direction):
        img = "balaacertando"
        if direction == "left":
            img += "_left"
        self.actor = Actor(img)
        self.actor.pos = (x, y)
        self.life_time = 10 

    def update(self):
        self.life_time -= 1

    def draw(self):
        self.actor.x -= camera_x
        self.actor.draw()
        self.actor.x += camera_x

# --- FUNÇÕES ---

def setup_level():
    global hero
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
                hero = Hero(x + TILE_SIZE/2, y + TILE_SIZE)
            elif char == "A":
                enemies.append(Enemy(x, y + TILE_SIZE, "azul"))
            elif char == "B":
                enemies.append(Enemy(x, y + TILE_SIZE/2, "abelha"))
            elif char == "G":
                items.append(Actor("arma", anchor=('center', 'center'), pos=(x + TILE_SIZE/2, y + TILE_SIZE/2)))

def create_impact(x, y, direction):
    impact = ImpactEffect(x, y, direction)
    impacts.append(impact)

def update():
    global camera_x
    
    if hero:
        hero.update()
        
        target_camera = hero.actor.x - WIDTH / 2
        camera_x = target_camera
        
        map_width = len(level_map[0]) * TILE_SIZE
        if camera_x < 0: camera_x = 0
        if camera_x > map_width - WIDTH: camera_x = map_width - WIDTH

    for enemy in enemies:
        enemy.update()
        if hero.actor.colliderect(enemy.actor):
            setup_level() 

    # --- LÓGICA DE TIRO ATUALIZADA ---
    for bullet in bullets[:]:
        bullet.update()
        
        bullet_direction = "left" if bullet.vx < 0 else "right"
        bullet_removed = False

        # 1. Colisão com Inimigos
        index = bullet.actor.collidelist([e.actor for e in enemies])
        if index != -1:
            enemy = enemies[index]
            
            # CORREÇÃO 2: Impacto na posição da BALA, não do inimigo
            create_impact(bullet.actor.x, bullet.actor.y, bullet_direction)
            
            enemies.pop(index)
            bullet_removed = True

        # 2. Colisão com Paredes
        if not bullet_removed and bullet.actor.collidelist(walls) != -1:
            create_impact(bullet.actor.x, bullet.actor.y, bullet_direction)
            bullet_removed = True
            
        if bullet_removed or abs(bullet.actor.x - hero.actor.x) > WIDTH:
            if bullet in bullets:
                bullets.remove(bullet)

    for impact in impacts[:]:
        impact.update()
        if impact.life_time <= 0:
            impacts.remove(impact)

def on_key_down(key):
    if key == keys.Z and hero:
        hero.shoot()

def draw():
    screen.clear()
    screen.fill((100, 170, 255))
    
    for wall in walls:
        wall.x -= camera_x
        wall.draw()
        wall.x += camera_x
        
    for item in items:
        item.x -= camera_x
        item.draw()
        item.x += camera_x
        
    for enemy in enemies:
        enemy.draw()
        
    for bullet in bullets:
        bullet.draw()
        
    for impact in impacts:
        impact.draw()
        
    if hero:
        hero.draw()

setup_level()
pgzrun.go()
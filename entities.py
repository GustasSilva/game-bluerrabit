"""Sprites do jogo: herói, inimigos, balas e efeitos de impacto."""
import math
import random

from pgzero.builtins import Actor, keyboard, sounds

import state
from settings import GRAVITY, JUMP_STRENGTH, MOVE_SPEED, BULLET_SPEED


class GameSprite(Actor):
    """Classe base que gerencia a animação de sprites automaticamente."""

    def __init__(self, img_idle_list, img_move_list, x, y):
        super().__init__(img_idle_list[0], pos=(x, y))
        self.img_idle_list = img_idle_list   # imagens parado
        self.img_move_list = img_move_list   # imagens movendo
        self.anim_timer = 0
        self.current_frame = 0
        self.is_moving = False
        self.facing_left = False

    def animate(self):
        # Avança o frame a cada 8 ticks
        self.anim_timer += 1
        if self.anim_timer > 8:
            self.anim_timer = 0
            self.current_frame += 1

        lst = self.img_move_list if self.is_moving else self.img_idle_list

        # Pega a imagem correta (módulo para loop infinito)
        img_name = lst[self.current_frame % len(lst)]
        self.image = img_name

        # Espelhamento manual (imagens originais olham para a direita)
        if self.facing_left:
            if not img_name.endswith("_left"):
                self.image = img_name + "_left"
        else:
            if img_name.endswith("_left"):
                self.image = img_name.replace("_left", "")


class Hero(GameSprite):
    def __init__(self, x, y):
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
        # 1. Checa morte (buraco) -> pede reinício do nível
        if self.y > 800:
            state.request_restart = True
            return

        # 2. Respiração
        self.breath_counter += 1

        # 3. Recuo do tiro
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
            if state.SOUND_ENABLED:
                sounds.jump.play()

        # 5. Física vertical
        self.vy += GRAVITY
        if self.vy > 12:
            self.vy = 12

        # 6. Movimento e colisão
        self.apply_movement()

        # 7. Coleta de arma
        self.check_item_collision()

        # 8. Animação (se estiver atirando, sobrescreve a animação padrão)
        if self.has_gun and self.recoil_timer > 0:
            self.image = "heroiatirando"
            if self.facing_left:
                self.image += "_left"
        elif self.has_gun:
            self.img_idle_list = ["heroiarma1"]
            self.img_move_list = ["heroiarma1", "heroiarma2"]
            self.animate()
        else:
            self.animate()

    def apply_movement(self):
        # Eixo X
        self.x += self.vx
        if self.collidelist(state.walls) != -1:
            self.x -= self.vx

        # Eixo Y
        self.y += self.vy
        index = self.collidelist(state.walls)
        if index != -1:
            wall = state.walls[index]
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
        for item in state.items[:]:
            if self.colliderect(item):
                if "arma" in item.image:
                    self.has_gun = True
                    state.items.remove(item)

    def shoot(self):
        if self.has_gun:
            self.recoil_timer = 10
            if state.SOUND_ENABLED:
                sounds.gun.play()

            b_y = self.y - 25
            offset_x = 25 if not self.facing_left else -25
            b_x = self.x + offset_x
            b_speed = BULLET_SPEED if not self.facing_left else -BULLET_SPEED
            img_bala = "bala" if not self.facing_left else "bala_left"

            state.bullets.append(Bullet(b_x, b_y, b_speed, img_bala))

    def draw(self):
        # Animação de respiração
        breath_offset = 0
        if self.on_ground and not self.is_moving:
            breath_offset = math.sin(self.breath_counter * 0.1) * 2

        # Aplica câmera e respiração temporariamente
        self.x -= state.camera_x
        self.y += breath_offset

        super().draw()

        # Restaura a posição
        self.y -= breath_offset
        self.x += state.camera_x


class Enemy(GameSprite):
    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        base = f"inimigo{enemy_type}"
        idles = [f"{base}1"]
        moves = [f"{base}1", f"{base}2"]

        super().__init__(idles, moves, x, y)
        self.anchor = ('left', 'bottom')
        self.start_y = y

        # --- Desincronização (movimento/animação assíncronos) ---
        speed_variation = random.choice([1.5, 2, 2.5])
        initial_direction = random.choice([-1, 1])
        self.vx = speed_variation * initial_direction

        # Fase da patrulha
        self.max_dist = 200
        self.dist_traveled = random.randint(0, int(self.max_dist / 2))

        # Desincroniza a animação para não trocarem sprites juntos
        self.anim_timer = random.randint(0, 8)

        self.is_moving = True
        self.facing_left = (self.vx < 0)

    def update_enemy(self):
        self.animate()

        # Movimento de patrulha
        self.x += self.vx
        self.dist_traveled += abs(self.vx)

        # Inverte direção por distância
        if self.dist_traveled > self.max_dist:
            self.vx *= -1
            self.dist_traveled = 0

        if self.enemy_type in ("azul", "abelha"):
            # Onda senoidal de 5px de amplitude para um voo "flutuante"
            oscillation = math.sin(self.anim_timer * 0.05) * 5
            self.y = self.start_y + oscillation

        if self.collidelist(state.walls) != -1:
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
        if direction == "left":
            img += "_left"
        super().__init__(img, pos=(x, y))
        self.life_time = 10

    def update(self):
        self.life_time -= 1

"""Rabbit Adventure — ponto de entrada (Pygame Zero).

Este arquivo concentra os hooks que o Pygame Zero procura no módulo principal
(`update`, `draw`, `on_key_down`, `on_mouse_down`) e a tela de menu. A lógica do
jogo está dividida em:
    settings.py  -> constantes e mapa do nível
    state.py     -> estado compartilhado (player, câmera, listas)
    entities.py  -> sprites (herói, inimigos, balas, efeitos)
    level.py     -> construção do nível

Execute a partir da raiz do projeto:  pgzrun game.py
"""
import pgzrun
from pygame import Rect

import state
from settings import WIDTH, HEIGHT, TITLE, TILE_SIZE, level_map
from entities import ImpactEffect
from level import setup_level

# WIDTH, HEIGHT e TITLE precisam existir no namespace deste módulo: o Pygame Zero
# os lê daqui para dimensionar e nomear a janela.

# --- Botões do menu ---
btn_start = Rect(300, 200, 200, 50)
btn_sound = Rect(300, 300, 200, 50)
btn_exit = Rect(300, 400, 200, 50)


def create_impact(x, y, direction):
    state.impacts.append(ImpactEffect(x, y, direction))


# --- LOOP PRINCIPAL (UPDATE) ---

def update():
    if state.GAME_STATE == "GAME":
        update_game()


def update_game():
    # Reinício solicitado pelo herói (queda no buraco)
    if state.request_restart:
        setup_level()
        state.request_restart = False
        return

    player = state.player
    if player:
        player.update_hero()

        # Câmera segue o jogador, respeitando os limites do mapa
        state.camera_x = player.x - WIDTH / 2
        map_width = len(level_map[0]) * TILE_SIZE
        if state.camera_x < 0:
            state.camera_x = 0
        if state.camera_x > map_width - WIDTH:
            state.camera_x = map_width - WIDTH

    # Inimigos
    for enemy in state.enemies:
        enemy.update_enemy()
        if player.colliderect(enemy):
            setup_level()
            return

    # Balas
    for bullet in state.bullets[:]:
        bullet.update()
        bullet_direction = "left" if bullet.vx < 0 else "right"
        bullet_removed = False

        # Colisão bala -> inimigo
        index = bullet.collidelist(state.enemies)
        if index != -1:
            create_impact(bullet.x, bullet.y, bullet_direction)
            state.enemies.pop(index)
            bullet_removed = True

        # Colisão bala -> parede
        if not bullet_removed and bullet.collidelist(state.walls) != -1:
            create_impact(bullet.x, bullet.y, bullet_direction)
            bullet_removed = True

        if bullet_removed or abs(bullet.x - player.x) > WIDTH:
            if bullet in state.bullets:
                state.bullets.remove(bullet)

    # Efeitos de impacto
    for impact in state.impacts[:]:
        impact.update()
        if impact.life_time <= 0:
            state.impacts.remove(impact)


# --- LOOP DE DESENHO (DRAW) ---

def draw():
    screen.clear()
    if state.GAME_STATE == "MENU":
        draw_menu()
    elif state.GAME_STATE == "GAME":
        draw_game()


def draw_menu():
    screen.fill((50, 50, 100))
    screen.draw.text("Rabbit Adventure", center=(WIDTH / 2, 100), fontsize=60, color="yellow")

    # Botão Iniciar
    screen.draw.filled_rect(btn_start, "green")
    screen.draw.text("JOGAR", center=btn_start.center, fontsize=30, color="white")

    # Botão Som
    color_sound = "blue" if state.SOUND_ENABLED else "red"
    text_sound = "SOM: ON" if state.SOUND_ENABLED else "SOM: OFF"
    screen.draw.filled_rect(btn_sound, color_sound)
    screen.draw.text(text_sound, center=btn_sound.center, fontsize=30, color="white")

    # Botão Sair
    screen.draw.filled_rect(btn_exit, "gray")
    screen.draw.text("SAIR", center=btn_exit.center, fontsize=30, color="white")

    # Instruções
    screen.draw.text("CONTROLES:", center=(WIDTH / 2, 480), fontsize=25, color="cyan")
    screen.draw.text("Setas: Mover  |  Espaço: Pular  |  Z: Atirar",
                     center=(WIDTH / 2, 520), fontsize=25, color="white")


def draw_game():
    screen.fill((100, 170, 255))

    # Desenha cada objeto deslocado pela câmera (e restaura a posição depois)
    for wall in state.walls:
        wall.x -= state.camera_x
        wall.draw()
        wall.x += state.camera_x

    for item in state.items:
        item.x -= state.camera_x
        item.draw()
        item.x += state.camera_x

    for enemy in state.enemies:
        enemy.x -= state.camera_x
        enemy.draw()
        enemy.x += state.camera_x

    for bullet in state.bullets:
        bullet.x -= state.camera_x
        bullet.draw()
        bullet.x += state.camera_x

    for impact in state.impacts:
        impact.x -= state.camera_x
        impact.draw()
        impact.x += state.camera_x

    if state.player:
        state.player.draw()


# --- ENTRADAS (INPUTS) ---

def on_key_down(key):
    if state.GAME_STATE == "GAME" and state.player:
        if key == keys.Z:
            state.player.shoot()


def on_mouse_down(pos):
    if state.GAME_STATE == "MENU":
        if btn_start.collidepoint(pos):
            setup_level()
            state.GAME_STATE = "GAME"
            if state.SOUND_ENABLED:
                music.play("musiclostwoods")

        elif btn_sound.collidepoint(pos):
            state.SOUND_ENABLED = not state.SOUND_ENABLED
            if state.SOUND_ENABLED:
                music.unpause()
            else:
                music.pause()

        elif btn_exit.collidepoint(pos):
            quit()


pgzrun.go()

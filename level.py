"""Construção do nível a partir do mapa de tiles."""
from pgzero.builtins import Actor

import state
from settings import TILE_SIZE, level_map
from entities import Hero, Enemy


def setup_level():
    """(Re)constrói o nível: paredes, inimigos, itens e o jogador."""
    state.walls.clear()
    state.enemies.clear()
    state.items.clear()
    state.bullets.clear()
    state.impacts.clear()

    for row_index, row in enumerate(level_map):
        for col_index, char in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            if char == "W":
                state.walls.append(Actor("chaoreto", anchor=('left', 'top'), pos=(x, y)))
            elif char == "T":
                state.walls.append(Actor("terra", anchor=('left', 'top'), pos=(x, y)))
            elif char == "C":
                state.walls.append(Actor("chaoreto2", anchor=('left', 'top'), pos=(x, y)))
            elif char == "P":
                state.player = Hero(x + TILE_SIZE / 2, y + TILE_SIZE)
            elif char == "A":
                state.enemies.append(Enemy(x, y + TILE_SIZE / 2, "azul"))
            elif char == "B":
                state.enemies.append(Enemy(x, y + TILE_SIZE / 2, "abelha"))
            elif char == "G":
                state.items.append(
                    Actor("arma", anchor=('center', 'center'),
                          pos=(x + TILE_SIZE / 2, y + TILE_SIZE / 2))
                )

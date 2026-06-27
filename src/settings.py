"""Constantes de configuração e o mapa do nível."""

# --- Janela ---
WIDTH = 800
HEIGHT = 600
TITLE = "Rabbit Adventure"

# --- Física e jogo ---
TILE_SIZE = 48
GRAVITY = 1
JUMP_STRENGTH = -16
MOVE_SPEED = 5
BULLET_SPEED = 12

# --- Mapa do nível ---
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
    "T...G...............B........B.WWWWWWW..........WT",
    "TP......A........A.............TTTTTTT..........TT",
    "TWWWWWWWWWWW...WWWWWWWWWW...WWWTTTTTTTWWWWWWWWWWTT",
    "TTTTTTTTTTTT...TTTTTTTTTT...TTTTTTTTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTT...TTTTTTTTTT...TTTTTTTTTTTTTTTTTTTTTT",
]

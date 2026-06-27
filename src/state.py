"""Estado compartilhado do jogo, mutável em tempo de execução.

Centralizar aqui evita o uso de `global` espalhado entre os módulos: cada módulo
importa `state` e lê/escreve via `state.<nome>`.
"""

# --- Objetos do mundo ---
walls = []
enemies = []
bullets = []
impacts = []
items = []
player = None

# --- Câmera ---
camera_x = 0

# --- Fluxo do jogo ---
GAME_STATE = "MENU"        # MENU, GAME, GAMEOVER
SOUND_ENABLED = True
request_restart = False    # sinaliza reinício do nível (ex.: herói caiu no buraco)

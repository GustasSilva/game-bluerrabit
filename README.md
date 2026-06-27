# Rabbit Adventure

Plataforma 2D feito em **Python** com **Pygame Zero** (`pgzero`). Você controla um
coelho que percorre a fase, pula entre plataformas, pega uma arma e atira nos
inimigos que patrulham o cenário, enquanto a câmera acompanha o personagem.

---

## 🎮 Controles

| Tecla        | Ação      |
|--------------|-----------|
| ← / →        | Mover      |
| Espaço       | Pular      |
| Z            | Atirar (após pegar a arma) |
| Mouse        | Navegar no menu |

No menu é possível **Jogar**, ligar/desligar o **Som** e **Sair**.

---

## ✨ Destaques técnicos

- **Pygame Zero** — loop de jogo com `update()` / `draw()` e `Actor`s.
- **Animação por frames** — classe base `GameSprite` que alterna sprites de
  parado/andando e espelha automaticamente conforme a direção.
- **Física simples** — gravidade, pulo e colisão com o cenário em dois eixos.
- **Fase em tiles** — o mapa é desenhado a partir de uma matriz de caracteres
  (`W` grama, `T` terra, `C` caixa, `P` player, `A`/`B` inimigos, `G` arma).
- **Câmera lateral** que segue o jogador respeitando os limites do mapa.
- **Inimigos dessincronizados** — velocidade, direção e fase de animação
  sorteadas para que não se movam todos juntos.

---

## 🚀 Como executar

Pré-requisito: **Python 3.10+**.

```bash
# 1. (opcional) criar e ativar um ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. instalar as dependências
pip install -r requirements.txt

# 3. rodar o jogo (a partir da pasta do projeto)
pgzrun game.py
```

> O `pgzrun game.py` deve ser executado **a partir da raiz do projeto**, pois o
> Pygame Zero procura os recursos nas pastas `images/`, `music/` e `sounds/`.

---

## 📁 Estrutura

```
game-bluerrabit/
├── game.py              # Entrada: hooks do Pygame Zero (update/draw/inputs) e menu
├── settings.py          # Constantes e o mapa do nível
├── state.py             # Estado compartilhado (player, câmera, listas)
├── entities.py          # Sprites: GameSprite, Hero, Enemy, Bullet, ImpactEffect
├── level.py             # Construção do nível a partir do mapa de tiles
├── aumentarsprites.py   # Utilitário: padroniza os PNGs de images/ para 48x48
├── images/              # Sprites (herói, inimigos, bala, arma, cenário)
├── music/               # Trilha sonora
├── sounds/              # Efeitos sonoros (pulo, tiro)
└── requirements.txt
```

### Organização do código
O jogo é executado pelo `game.py` (`pgzrun game.py`), que contém apenas os
*hooks* que o Pygame Zero procura no módulo principal e a tela de menu. A lógica
foi separada em módulos: `settings` (configuração), `state` (estado compartilhado
em tempo de execução), `entities` (classes de sprite) e `level` (montagem da
fase). Como o Pygame Zero injeta seus objetos (`Actor`, `keyboard`, `sounds`…)
apenas no módulo principal, os submódulos os importam de `pgzero.builtins`.

### Sobre o `aumentarsprites.py`
Script auxiliar de uso único: redimensiona **todos** os `.png` da pasta `images/`
para 48×48 (o tamanho de tile do jogo), sobrescrevendo os arquivos. Rode apenas
se precisar repadronizar os sprites.

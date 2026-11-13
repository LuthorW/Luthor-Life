"""Assentos virados para o lugar certo: cadeiras olham para a mesa, sofás e poltronas para a TV, a mesinha de centro
ou o tapete, e as poltronas do cinema para a tela.

Cada assento ganha uma direção (`face`):
- "down": de frente para a tela (o desenho de sempre);
- "up": de costas para a tela. O encosto fica na frente e cobre quem está sentada (só aparecem a cabeça e os ombros,
  como no Stardew);
- "left"/"right": de lado, com o encosto atrás das costas (na poltrona, o braço do lado de cá cobre as pernas).

Os desenhos virados têm duas camadas: "base" (desenhada no lugar do objeto) e "front" (encosto ou braço), que entra
na lista de desenho logo depois de quem está sentada (`world_items`, `FRONT_BIAS`); quem senta usa `sitter_sort`.

A direção é calculada pelo que há em volta (`_compute`), guardada no próprio objeto (`o.face`) e refeita sozinha
quando a lista de objetos do mapa muda (decoração, festas, Fundação). Sofás (3x1) só viram para cima ou para baixo.
"""
import pygame

from . import art
from .art import new, R, P, shade, mix, up, cached
from .config import TILE

TABLE_WORDS = ("table", "desk", "dining", "island", "counter", "bar", "kitchen", "mesa")
CHAIRS = ("chair", "chair_blue", "hchair", "stool", "cadeira_ceo", "cadeira_reuniao", "cadeira_vittoria", "cadeira_sam")        # 1 tile: olham para a mesa do lado
LOUNGE = ("sofa", "sofa_grey", "armchair", "poltrona_roxa")  # olham para a TV, a mesinha ou o tapete
WIDE = ("sofa", "sofa_grey")                                 # 3x1: só para cima ou para baixo
FIXED = {"bench_l": "left", "bench_r": "right", "bench": "down", "seat": "up"}   # "seat" = poltrona do cinema
KINDS = CHAIRS + LOUNGE + tuple(FIXED)
TVS = ("tv", "tv_big", "tv_wall")
DIRS = (("up", (0, -1)), ("right", (1, 0)), ("left", (-1, 0)), ("down", (0, 1)))
WALLS = ("wall", "glass")


# ---------------------------------------------------------------------------
# Para onde cada assento olha
# ---------------------------------------------------------------------------
def prepare(m):
    """Garante que os assentos do mapa sabem para onde olham (refaz se a lista de objetos mudou)."""
    sig = (id(m.objects), len(m.objects))
    if getattr(m, "_faces_sig", None) == sig:
        return
    m._faces_sig = sig
    fronts = []
    for o in m.objects:
        if o.kind in KINDS:
            o.face = _compute(m, o)
            if o.face != "down" and front_image(o) is not None:
                fronts.append(o)
    m._seat_fronts = fronts


def invalidate(m):
    m._faces_sig = None


def face(m, o):
    prepare(m)
    return getattr(o, "face", "down")


def _is_wall(m, x, y):
    return not m.in_bounds(x, y) or m.tiles[y][x] in WALLS


def _is_table(n, o):
    return n is not None and n is not o and n.kind not in KINDS and any(w in n.kind for w in TABLE_WORDS)


def _clear_line(m, ax, ay, bx, by):
    """Nenhuma parede entre os dois pontos (em tiles): a TV do outro cômodo não conta."""
    steps = int(max(abs(bx - ax), abs(by - ay)) * 3) + 1
    for i in range(1, steps):
        t = i / steps
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        if _is_wall(m, int(x), int(y)):
            return False
    return True


def _towards(vx, vy, wide):
    if wide:
        if abs(vy) < 0.3:
            return None
        return "down" if vy > 0 else "up"
    if abs(vx) >= abs(vy):
        return "right" if vx > 0 else "left"
    return "down" if vy > 0 else "up"


def _focus(m, o):
    """Sofá/poltrona: a TV ou a mesinha de centro mais perto (sem parede no meio); senão, o tapete."""
    cx, cy = o.x + o.w / 2, o.y + o.h / 2
    best = None
    for n in m.objects:
        if n is o:
            continue
        if n.kind in TVS:
            pri, rng = 0, 7
        elif n.kind == "coffee_table":
            pri, rng = 0, 4
        elif "rug" in n.kind and n.layer == "decal":
            pri, rng = 1, 2.5
        else:
            continue
        if o.kind in WIDE and not (n.x < o.x + o.w and o.x < n.x + n.w):
            continue                                  # sofá: só o que está bem na frente ou atrás dele
        nx, ny = min(max(cx, n.x), n.x + n.w), min(max(cy, n.y), n.y + n.h)   # ponto do objeto mais perto
        dist = max(abs(nx - cx), abs(ny - cy))
        if dist > rng or not _clear_line(m, cx, cy, nx, ny):
            continue
        vx, vy = nx - cx, ny - cy
        if pri == 1 or dist < 0.01:                   # tapete (ou em cima dele): para o meio
            vx, vy = n.x + n.w / 2 - cx, n.y + n.h / 2 - cy
        d = _towards(vx, vy, o.kind in WIDE)
        if d and (best is None or (pri, dist) < best[0]):
            best = ((pri, dist), d)
    return best[1] if best else None


def _run(m, o, dy, limit=6):
    """Quantos tiles livres há em cima (dy=-1) ou embaixo (dy=1) do assento (média das colunas)."""
    total = 0
    for x in range(o.x, o.x + o.w):
        y = o.y - 1 if dy < 0 else o.y + o.h
        n = 0
        while n < limit and m.in_bounds(x, y) and not _is_wall(m, x, y) and not m.solid[y][x]:
            n += 1
            y += dy
        total += n
    return total / o.w


def _compute(m, o):
    if o.kind in FIXED:
        return FIXED[o.kind]
    if o.kind in CHAIRS or o.kind not in WIDE:       # cadeira/banqueta/poltrona: mesa encostada
        for d, (dx, dy) in DIRS:
            if _is_table(m.object_at(o.x + dx, o.y + dy), o):
                return d
    if o.kind in LOUNGE:
        d = _focus(m, o)
        if d:
            return d
        # sem TV nem mesinha: se a frente está apertada (parede logo ali), vira para o lado aberto da sala
        down, upr = _run(m, o, 1), _run(m, o, -1)
        if down <= 2 and upr > down:
            return "up"
    # de frente para a parede de baixo (sem espaço para as pernas): vira para dentro da sala
    below = all(_is_wall(m, x, o.y + o.h) for x in range(o.x, o.x + o.w))
    above = any(not _is_wall(m, x, o.y - 1) for x in range(o.x, o.x + o.w))
    if o.kind != "stool" and below and above:
        return "up"
    return "down"


def sort_key(o):
    """A mesma chave de ordem de desenho que Game.draw_world usa para os objetos."""
    return o.base_y - (14 if not o.solid else 0)


def sitter_sort(o):
    """Quem está sentada é desenhada logo depois do assento e antes da camada da frente (`FRONT_BIAS`)."""
    return sort_key(o) + 1


FRONT_BIAS = 2          # a camada da frente (encosto visto de trás, braço da poltrona de lado) vem por cima


# ---------------------------------------------------------------------------
# Desenhos (px de arte; "down" é o desenho original de art.py / hospital.py / activities.py)
# Cada desenho tem duas camadas: "base" (o que fica atrás de quem senta) e "front" (o que fica na frente).
# ---------------------------------------------------------------------------
def _chair_up(part, c, leg=(60, 40, 40)):
    s = new(16, 18)
    if part == "base":
        R(s, shade(leg, 0.8), 5, 12, 1, 4); R(s, shade(leg, 0.8), 10, 12, 1, 4)    # pernas da frente (lá atrás)
        R(s, shade(c, 1.18), 4, 10, 8, 2)                                         # assento
        return s
    R(s, leg, 4, 12, 1, 6); R(s, leg, 11, 12, 1, 6)                               # pernas de trás (aqui na frente)
    R(s, shade(c, 0.78), 4, 5, 8, 7)                                              # costas do encosto
    R(s, shade(c, 0.9), 5, 6, 6, 4)
    R(s, shade(c, 1.12), 4, 5, 8, 1)                                              # topo do encosto
    R(s, shade(c, 0.62), 4, 11, 8, 1)
    return s


def _chair_side(part, c, leg=(60, 40, 40)):
    """Virada para a direita: encosto à esquerda, assento para a frente."""
    s = new(16, 18)
    if part == "front":
        return None
    R(s, shade(c, 0.85), 3, 2, 2, 10)                                             # encosto (de perfil)
    R(s, shade(c, 1.1), 3, 2, 2, 1)
    R(s, shade(c, 0.95), 3, 10, 10, 2)                                            # assento
    R(s, shade(c, 1.18), 3, 10, 10, 1)
    R(s, shade(leg, 0.8), 5, 12, 1, 5); R(s, shade(leg, 0.8), 11, 12, 1, 5)       # pernas do outro lado
    R(s, leg, 3, 12, 1, 6); R(s, leg, 12, 12, 1, 6)
    return s


H_COLOR, H_LEG = (40, 130, 110), (150, 150, 160)


def _hchair_up(part):
    c, leg = H_COLOR, H_LEG
    s = new(16, 18)
    if part == "base":
        R(s, shade(leg, 0.8), 5, 13, 1, 4); R(s, shade(leg, 0.8), 10, 13, 1, 4)
        R(s, (50, 146, 122), 3, 11, 10, 2)
        return s
    R(s, leg, 4, 13, 1, 5); R(s, leg, 11, 13, 1, 5)
    R(s, shade(c, 0.8), 3, 5, 10, 8)
    R(s, shade(c, 0.92), 4, 6, 8, 5)
    R(s, (60, 160, 136), 3, 5, 10, 1)
    R(s, shade(c, 0.62), 3, 12, 10, 1)
    return s


def _hchair_side(part):
    c, leg = H_COLOR, H_LEG
    if part == "front":
        return None
    s = new(16, 18)
    R(s, shade(c, 0.88), 3, 3, 3, 9)
    R(s, (60, 160, 136), 3, 3, 3, 1)
    R(s, (50, 146, 122), 3, 10, 10, 3)
    R(s, (60, 160, 136), 3, 10, 10, 1)
    R(s, shade(leg, 0.8), 5, 13, 1, 4); R(s, shade(leg, 0.8), 11, 13, 1, 4)
    R(s, leg, 3, 13, 1, 5); R(s, leg, 12, 13, 1, 5)
    return s


def _armchair_up(part, c):
    s = new(16, 20)
    if part == "base":
        R(s, shade(c, 1.2), 3, 5, 10, 3)                                          # almofada do assento, lá atrás
        R(s, shade(c, 0.8), 0, 4, 3, 13); R(s, shade(c, 0.8), 13, 4, 3, 13)       # braços
        R(s, shade(c, 1.02), 0, 4, 3, 1); R(s, shade(c, 1.02), 13, 4, 3, 1)
        return s
    R(s, (40, 30, 30), 2, 17, 2, 3); R(s, (40, 30, 30), 12, 17, 2, 3)            # pés
    R(s, shade(c, 0.74), 1, 7, 14, 10)                                            # costas da poltrona
    R(s, shade(c, 0.84), 2, 8, 12, 7)
    R(s, shade(c, 1.08), 1, 7, 14, 1)                                             # topo do encosto
    R(s, shade(c, 0.6), 1, 16, 14, 1)
    for x in (5, 10):                                                              # pespontos
        P(s, shade(c, 0.66), x, 11)
    return s


def _armchair_side(part, c):
    """Virada para a direita: encosto alto atrás (à esquerda); o braço do lado de cá cobre as pernas."""
    s = new(16, 20)
    if part == "base":
        R(s, (40, 30, 30), 2, 17, 2, 3); R(s, (40, 30, 30), 12, 17, 2, 3)
        R(s, c, 1, 2, 4, 15)                                                      # encosto
        R(s, shade(c, 1.1), 1, 2, 4, 1)
        R(s, shade(c, 0.85), 1, 3, 1, 14)
        R(s, shade(c, 0.9), 4, 6, 11, 2)                                          # braço do outro lado
        R(s, shade(c, 1.2), 4, 9, 10, 3)                                          # almofada do assento
        R(s, shade(c, 0.88), 4, 12, 11, 5)                                        # frente da base
        return s
    R(s, shade(c, 0.86), 3, 10, 12, 3)                                            # braço do lado de cá (rolinho)
    R(s, shade(c, 1.06), 3, 10, 12, 1)
    R(s, shade(c, 0.72), 13, 10, 3, 7)                                            # ponta do braço
    R(s, shade(c, 0.92), 13, 10, 3, 1)
    R(s, shade(c, 0.62), 3, 13, 10, 1)
    return s


def _sofa_up(part, c, w=3):
    W = 16 * w
    s = new(W, 22)
    if part == "base":
        R(s, shade(c, 1.22), 3, 5, W - 6, 3)                                      # almofadas do assento, lá atrás
        for i in range(1, w):
            R(s, shade(c, 1.05), i * 16, 5, 1, 3)
        R(s, shade(c, 0.82), 0, 4, 3, 15); R(s, shade(c, 0.82), W - 3, 4, 3, 15)  # braços
        R(s, shade(c, 1.0), 0, 4, 3, 1); R(s, shade(c, 1.0), W - 3, 4, 3, 1)
        return s
    R(s, (40, 30, 40), 2, 19, 2, 3); R(s, (40, 30, 40), W - 4, 19, 2, 3)         # pés
    R(s, shade(c, 0.74), 0, 8, W, 11)                                             # costas do sofá
    R(s, shade(c, 0.84), 2, 9, W - 4, 7)
    R(s, shade(c, 1.08), 0, 8, W, 1)                                              # topo do encosto
    R(s, shade(c, 0.6), 0, 18, W, 1)
    for i in range(1, w):                                                         # costura entre os lugares
        R(s, shade(c, 0.7), i * 16, 10, 1, 6)
    return s


def _seat_up(part):
    """Poltrona do cinema vista de trás (o público olha para a tela)."""
    s = new(16, 18)
    if part == "base":
        R(s, (170, 40, 60), 3, 5, 10, 3)                                          # assento, lá atrás
        R(s, (90, 20, 30), 1, 6, 2, 8); R(s, (90, 20, 30), 13, 6, 2, 8)           # braços
        R(s, (110, 26, 40), 1, 6, 2, 1); R(s, (110, 26, 40), 13, 6, 2, 1)
        return s
    R(s, (60, 40, 50), 4, 14, 1, 4); R(s, (60, 40, 50), 11, 14, 1, 4)
    R(s, (118, 22, 40), 3, 7, 10, 8)                                              # costas do encosto
    R(s, (136, 28, 48), 4, 8, 8, 5)
    R(s, (160, 40, 58), 3, 7, 10, 1)
    R(s, (80, 16, 28), 3, 14, 10, 1)
    return s


BUILDERS = {
    ("chair", "up"): lambda p: _chair_up(p, (120, 40, 60)),
    ("chair", "right"): lambda p: _chair_side(p, (120, 40, 60)),
    ("chair_blue", "up"): lambda p: _chair_up(p, (50, 70, 120)),
    ("chair_blue", "right"): lambda p: _chair_side(p, (50, 70, 120)),
    ("hchair", "up"): _hchair_up,
    ("hchair", "right"): _hchair_side,
    ("armchair", "up"): lambda p: _armchair_up(p, (150, 60, 70)),
    ("armchair", "right"): lambda p: _armchair_side(p, (150, 60, 70)),
    ("poltrona_roxa", "up"): lambda p: _armchair_up(p, (118, 52, 176)),
    ("poltrona_roxa", "right"): lambda p: _armchair_side(p, (118, 52, 176)),
    ("sofa", "up"): lambda p: _sofa_up(p, (96, 40, 140)),
    ("sofa_grey", "up"): lambda p: _sofa_up(p, (90, 96, 110)),
    ("seat", "up"): _seat_up,
}


def sprite(kind, d, part="base"):
    """Camada do assento virado para d (part: "base", "front" ou "all"). None se não houver."""
    if part == "all":
        def both():
            b, f = sprite(kind, d, "base"), sprite(kind, d, "front")
            if b is None or f is None:
                return b or f
            s = b.copy()
            s.blit(f, (0, 0))
            return s
        return cached(("seat_dir", kind, d, "all"), both)
    if d == "left":
        if (kind, "right") not in BUILDERS:
            return None
        return cached(("seat_dir", kind, "left", part), lambda: _flip(sprite(kind, "right", part)))
    if (kind, d) not in BUILDERS:
        return None
    return cached(("seat_dir", kind, d, part), lambda: _up(BUILDERS[(kind, d)](part)))


def _up(s):
    return None if s is None else up(s)


def _flip(s):
    return None if s is None else pygame.transform.flip(s, True, False)


def object_image(g, o):
    """Gancho de Game.object_image: a camada de trás do assento virado (None = desenho de sempre)."""
    d = getattr(o, "face", None)
    if d is None or d == "down" or o.kind not in KINDS:
        return None
    return sprite(o.kind, d, "base")


def front_image(o):
    """A camada da frente (desenhada depois de quem está sentada), ou None."""
    d = getattr(o, "face", None)
    if d is None or d == "down" or o.kind not in KINDS:
        return None
    return sprite(o.kind, d, "front")


def world_items(g, m):
    """Itens extras para a lista de desenho de Game.draw_world: a camada da frente de cada assento virado."""
    prepare(m)
    return [(sort_key(o) + FRONT_BIAS, 0, "seatfront", o) for o in m._seat_fronts]

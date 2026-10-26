"""Natureza e cenário no estilo Stardew Valley.

- Árvores grandes com copa em "tufos" iluminados de cima à esquerda (a copa fica
  transparente quando a jogadora passa atrás dela).
- Grama e terra mais ricas, cantos arredondados nos caminhos e detalhes espalhados
  pelo chão (tufos, florzinhas, pedrinhas).
- Objetos novos: pinheiro, capim alto, pedras, toco, tronco, cerca de madeira, mesa de
  piquenique, vaso de flores, gazebo, farol, toalha e castelinho de areia.
"""
import math
import random

import pygame

from . import art
from .art import new, up, R, P, shade, mix, cached
from .config import TS, TILE, SCALE

# ---------------------------------------------------------------------------
# Paletas
# ---------------------------------------------------------------------------
GRASS = (104, 176, 78)
GRASS_DK = (78, 142, 62)
GRASS_LT = (146, 206, 98)

LEAF = {
    #        contorno        escuro          médio           base            claro
    "oak": [(30, 70, 46), (44, 104, 58), (60, 132, 66), (82, 160, 74), (130, 196, 92)],
    "cherry": [(118, 56, 92), (172, 86, 128), (208, 118, 160), (236, 154, 190), (252, 204, 222)],
    "orange": [(28, 66, 44), (40, 98, 56), (56, 126, 62), (76, 150, 70), (122, 188, 88)],
    "pine": [(18, 52, 44), (28, 78, 58), (40, 100, 66), (56, 124, 74), (96, 160, 92)],
}
TRUNK = [(70, 46, 32), (98, 66, 42), (126, 86, 54), (156, 112, 72)]


def _lit_blobs(s, blobs, pal, seed, light=(-0.55, -0.83)):
    """Desenha uma copa feita de tufos redondos, cada um iluminado de cima à esquerda."""
    w, h = s.get_size()
    rnd = random.Random(seed)
    owner = {}
    for y in range(h):
        for x in range(w):
            # entre os tufos que cobrem o pixel, o mais baixo fica na frente
            inside = [i for i, (bx, by, r) in enumerate(blobs) if math.hypot(x + 0.5 - bx, y + 0.5 - by) < r]
            if inside:
                owner[(x, y)] = max(inside, key=lambda i: blobs[i][1])
    cy = sum(b[1] for b in blobs) / len(blobs)
    span = max(b[1] + b[2] for b in blobs) - min(b[1] - b[2] for b in blobs)
    for (x, y), i in owner.items():
        bx, by, r = blobs[i]
        nx, ny = (x + 0.5 - bx) / r, (y + 0.5 - by) / r
        lum = -(nx * light[0] + ny * light[1]) * 0.9 - (y - cy) / span * 0.9 + rnd.uniform(-0.18, 0.18)
        if lum > 0.62:
            c = pal[4]
        elif lum > 0.05:
            c = pal[3]
        elif lum > -0.55:
            c = pal[2]
        else:
            c = pal[1]
        s.set_at((x, y), c)
    # contorno escuro e linha entre tufos
    for (x, y), i in owner.items():
        edge = False
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in owner:
                edge = True
                break
        if edge:
            s.set_at((x, y), pal[0])
        elif owner.get((x, y - 1), i) != i and blobs[owner[(x, y - 1)]][1] < blobs[i][1]:
            s.set_at((x, y), pal[1])
    return owner


def _trunk(s, cx, top, bottom, wdt=8):
    x0 = cx - wdt // 2
    R(s, TRUNK[1], x0, top, wdt, bottom - top)
    R(s, TRUNK[2], x0 + 2, top, wdt - 4, bottom - top)
    R(s, TRUNK[3], x0 + 3, top + 2, 1, bottom - top - 5)
    R(s, TRUNK[0], x0, top, 1, bottom - top)
    R(s, TRUNK[0], x0 + wdt - 1, top, 1, bottom - top)
    # raízes
    for dx, ln in ((-3, 3), (-2, 2), (wdt + 1, 3), (wdt, 2)):
        R(s, TRUNK[1], x0 + dx, bottom - 2, ln if dx < 0 else 3, 2)
    R(s, TRUNK[0], x0 - 3, bottom - 1, wdt + 6, 1)
    for y in range(top + 3, bottom - 3, 4):
        P(s, TRUNK[0], x0 + 2 + (y // 4) % 3, y)


def _big_tree(kind="oak"):
    s = new(48, 64)
    _trunk(s, 24, 34, 62)
    blobs = [(24, 30, 12), (12, 30, 9), (36, 30, 9), (16, 19, 10), (32, 19, 10), (24, 11, 9),
             (8, 22, 6), (40, 22, 6), (24, 38, 9), (14, 39, 6), (34, 39, 6)]
    owner = _lit_blobs(s, blobs, LEAF[kind], hash(kind) & 0xFFFF)
    rnd = random.Random(kind)
    pts = [p for p in owner if 2 < p[0] < 45 and 3 < p[1] < 44]
    if kind == "orange":
        for _ in range(11):
            x, y = rnd.choice(pts)
            pygame.draw.circle(s, (232, 128, 40), (x, y), 2)
            P(s, (255, 196, 110), x - 1, y - 1)
            P(s, (150, 74, 30), x + 1, y + 1)
    elif kind == "cherry":
        for _ in range(26):
            x, y = rnd.choice(pts)
            P(s, (255, 250, 252), x, y)
            P(s, (255, 226, 238), x + 1, y)
    else:
        for _ in range(16):
            x, y = rnd.choice(pts)
            if s.get_at((x, y))[:3] == LEAF[kind][3]:
                P(s, LEAF[kind][4], x, y)
                P(s, LEAF[kind][4], x + 1, y - 1)
    return s


def _pine():
    s = new(48, 64)
    _trunk(s, 24, 46, 62, 6)
    pal = LEAF["pine"]
    tiers = [(2, 10), (10, 15), (19, 19), (28, 22)]   # (topo, meia largura da base)
    mask = {}
    for i, (top, hw) in enumerate(tiers):
        bot = top + 20
        for y in range(top, bot):
            t = (y - top) / (bot - top)
            half = int(2 + (hw - 2) * t)
            for x in range(24 - half, 24 + half):
                # borda de baixo serrilhada
                if y >= bot - 2 and (x // 3) % 2 == (y - bot) % 2:
                    continue
                mask[(x, y)] = i
    rnd = random.Random(7)
    for (x, y), i in mask.items():
        top, hw = tiers[i]
        nx = (x - 24) / max(1, hw)
        t = (y - top) / 20
        lum = -nx * 0.9 - t * 0.6 + 0.35 + rnd.uniform(-0.15, 0.15)
        c = pal[4] if lum > 0.85 else pal[3] if lum > 0.2 else pal[2] if lum > -0.45 else pal[1]
        s.set_at((x, y), c)
    for (x, y), i in mask.items():
        if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            s.set_at((x, y), pal[0])
        elif mask.get((x, y - 1), i) < i:
            s.set_at((x, y), pal[1])
    return s


def _bush_big(flower=(255, 140, 180), seed=0):
    s = new(22, 20)
    blobs = [(11, 11, 8), (5, 13, 5), (17, 13, 5), (8, 7, 5), (14, 7, 5)]
    owner = _lit_blobs(s, blobs, LEAF["oak"], 31 + seed)
    rnd = random.Random(seed + 5)
    pts = [p for p in owner if 2 < p[0] < 20 and 2 < p[1] < 17]
    for _ in range(7):
        x, y = rnd.choice(pts)
        P(s, flower, x, y); P(s, flower, x + 1, y); P(s, flower, x, y + 1)
        P(s, mix(flower, (255, 255, 200), 0.6), x + 1, y + 1)
    return s


def _tallgrass(frame=0):
    s = new(16, 16)
    rnd = random.Random(11)
    blades = [(rnd.randrange(1, 15), rnd.randrange(6, 12), rnd.choice((GRASS_DK, (92, 160, 70), GRASS_LT, (70, 128, 56))))
              for _ in range(14)]
    blades.sort(key=lambda b: b[2] == GRASS_LT)
    for (x, hgt, c) in blades:
        lean = (1 if frame else -1) * (1 if x > 7 else 0) + (1 if frame and x < 8 else 0)
        for k in range(hgt):
            xx = x + (lean if k > hgt // 2 else 0)
            P(s, c, xx, 15 - k)
        P(s, mix(c, (230, 250, 170), 0.5), x + lean, 15 - hgt)
    R(s, (60, 116, 52), 1, 15, 14, 1)
    return s


def _rock(big=False):
    s = new(16, 16)
    base, dk, lt, out = (150, 146, 156), (112, 108, 122), (190, 188, 196), (74, 70, 84)
    if big:
        pygame.draw.ellipse(s, out, (0, 3, 16, 13))
        pygame.draw.ellipse(s, base, (1, 4, 14, 11))
        pygame.draw.ellipse(s, dk, (2, 10, 13, 5))
        pygame.draw.ellipse(s, lt, (3, 5, 7, 4))
        P(s, (108, 156, 86), 11, 5); P(s, (108, 156, 86), 12, 5); P(s, (90, 140, 74), 12, 6)
    else:
        pygame.draw.ellipse(s, out, (2, 7, 12, 9))
        pygame.draw.ellipse(s, base, (3, 8, 10, 7))
        pygame.draw.ellipse(s, dk, (4, 11, 9, 4))
        R(s, lt, 5, 9, 3, 2)
    return s


def _stump():
    s = new(16, 16)
    R(s, TRUNK[1], 3, 7, 10, 8)
    R(s, TRUNK[2], 5, 7, 6, 8)
    R(s, TRUNK[0], 3, 14, 10, 1)
    R(s, TRUNK[1], 1, 13, 3, 2); R(s, TRUNK[1], 12, 13, 3, 2)
    pygame.draw.ellipse(s, (206, 164, 112), (3, 4, 10, 6))
    pygame.draw.ellipse(s, (176, 132, 86), (5, 5, 6, 4), 1)
    P(s, (150, 108, 68), 8, 7)
    pygame.draw.ellipse(s, TRUNK[0], (3, 4, 10, 6), 1)
    return s


def _log():
    s = new(32, 16)
    R(s, TRUNK[1], 4, 6, 25, 8)
    R(s, TRUNK[2], 4, 7, 25, 3)
    R(s, TRUNK[3], 6, 7, 20, 1)
    R(s, TRUNK[0], 4, 13, 25, 1)
    for x in (9, 15, 21):
        R(s, TRUNK[0], x, 9, 3, 1)
    pygame.draw.ellipse(s, (206, 164, 112), (1, 5, 7, 10))
    pygame.draw.ellipse(s, (170, 128, 84), (3, 7, 3, 6), 1)
    pygame.draw.ellipse(s, TRUNK[0], (1, 5, 7, 10), 1)
    P(s, (110, 160, 80), 20, 6); P(s, (110, 160, 80), 21, 6); P(s, (110, 160, 80), 12, 6)
    return s


def _fence(vertical=False):
    s = new(16, 20)
    wood, dk, lt = (170, 120, 74), (112, 74, 44), (204, 160, 108)
    if vertical:
        R(s, dk, 6, 0, 4, 20)
        R(s, wood, 7, 0, 2, 19)
        R(s, lt, 7, 0, 1, 19)
        R(s, dk, 5, 4, 6, 3); R(s, wood, 6, 4, 4, 2)
        return s
    for y in (8, 13):
        R(s, dk, 0, y, 16, 3)
        R(s, wood, 0, y, 16, 2)
        R(s, lt, 0, y, 16, 1)
    R(s, dk, 1, 4, 5, 15)
    R(s, wood, 2, 4, 3, 14)
    R(s, lt, 2, 5, 1, 12)
    R(s, (90, 58, 34), 1, 18, 5, 1)
    R(s, lt, 2, 4, 3, 1)
    return s


def _picnic():
    s = new(32, 24)
    wood, dk, lt = (176, 122, 72), (116, 76, 44), (210, 164, 110)
    R(s, dk, 2, 15, 28, 4); R(s, wood, 2, 15, 28, 2)          # banco da frente
    R(s, dk, 1, 5, 30, 8); R(s, wood, 1, 5, 30, 6)            # tampo
    for x in (1, 8, 15, 22, 29):
        R(s, dk, x, 5, 1, 6)
    R(s, lt, 1, 5, 30, 1)
    R(s, (220, 70, 80), 6, 6, 20, 4)                          # toalha xadrez
    for x in range(6, 26, 4):
        R(s, (250, 240, 240), x, 6, 2, 2); R(s, (250, 240, 240), x + 2, 8, 2, 2)
    R(s, dk, 4, 19, 2, 5); R(s, dk, 26, 19, 2, 5)
    R(s, (250, 230, 150), 22, 3, 4, 3)                        # cestinha
    R(s, (180, 120, 60), 22, 4, 4, 1)
    return s


def _flowerpot(c=(255, 120, 160)):
    s = new(16, 18)
    pygame.draw.circle(s, LEAF["oak"][2], (8, 8), 6)
    pygame.draw.circle(s, LEAF["oak"][3], (7, 7), 4)
    for (x, y) in ((5, 5), (10, 6), (7, 9), (11, 10), (4, 9)):
        P(s, c, x, y); P(s, c, x + 1, y); P(s, (255, 236, 150), x, y + 1)
    R(s, (150, 74, 50), 3, 11, 10, 7)
    R(s, (196, 108, 72), 4, 11, 8, 5)
    R(s, (214, 128, 88), 2, 10, 12, 2)
    R(s, (120, 60, 40), 3, 17, 10, 1)
    return s


def _gazebo():
    s = new(64, 84)
    stone, stone_dk, stone_lt = (196, 190, 204), (150, 144, 160), (226, 222, 232)
    R(s, stone_dk, 2, 66, 60, 18)
    R(s, stone, 2, 66, 60, 14)
    R(s, stone_lt, 2, 66, 60, 2)
    for x in range(6, 60, 10):
        R(s, stone_dk, x, 70, 1, 10)
    R(s, (120, 112, 132), 26, 80, 12, 4)                     # degrau
    R(s, (210, 204, 218), 24, 78, 16, 3)
    # pilares
    for x in (6, 22, 39, 55):
        R(s, (232, 228, 238), x, 34, 4, 34)
        R(s, (190, 184, 200), x + 3, 34, 1, 34)
    # grade baixa
    for x in range(8, 58, 3):
        if 24 <= x <= 38:
            continue
        R(s, (220, 214, 228), x, 56, 1, 10)
    R(s, (236, 232, 242), 6, 55, 20, 2); R(s, (236, 232, 242), 38, 55, 20, 2)
    # telhado (roxo Luthor)
    roof, roof_dk, roof_lt = (110, 44, 170), (74, 26, 120), (160, 92, 220)
    pygame.draw.polygon(s, roof_dk, [(32, 2), (63, 30), (63, 36), (0, 36), (0, 30)])
    pygame.draw.polygon(s, roof, [(32, 4), (60, 29), (4, 29)])
    pygame.draw.polygon(s, roof_lt, [(32, 4), (32, 29), (4, 29)])
    for i in range(1, 6):
        y = 4 + i * 5
        pygame.draw.line(s, roof_dk, (32 - i * 5, y), (32 + i * 5, y))
    R(s, (240, 236, 246), 0, 30, 64, 3)
    R(s, (200, 192, 214), 0, 33, 64, 2)
    R(s, (255, 214, 102), 31, 0, 2, 4)
    return s


def _lighthouse():
    s = new(48, 124)
    # rochas da base
    for (x, y, r, c) in [(10, 112, 10, (120, 116, 128)), (36, 113, 10, (128, 124, 136)), (24, 116, 11, (140, 136, 148)),
                         (6, 118, 6, (110, 106, 118)), (42, 118, 6, (110, 106, 118))]:
        pygame.draw.circle(s, c, (x, y), r)
        pygame.draw.circle(s, mix(c, (255, 255, 255), 0.25), (x - 3, y - 4), max(2, r // 3))
    # torre afunilada com listras
    top, bot = 30, 110
    for y in range(top, bot):
        t = (y - top) / (bot - top)
        half = int(8 + 6 * t)
        band = ((y - top) // 12) % 2 == 1
        base = (214, 52, 64) if band else (244, 242, 248)
        dk = shade(base, 0.78)
        R(s, base, 24 - half, y, half * 2, 1)
        R(s, dk, 24 + half - 4, y, 4, 1)
        P(s, shade(base, 0.6), 24 - half, y); P(s, shade(base, 0.6), 24 + half - 1, y)
    R(s, (60, 70, 90), 21, 96, 6, 14)                         # porta
    R(s, (90, 100, 124), 22, 97, 4, 12)
    R(s, (120, 170, 210), 22, 70, 4, 6)                       # janelinha
    # varanda e lanterna
    R(s, (40, 40, 52), 10, 26, 28, 4)
    for x in range(11, 38, 3):
        R(s, (40, 40, 52), x, 20, 1, 6)
    R(s, (40, 40, 52), 10, 20, 28, 1)
    R(s, (255, 236, 150), 16, 12, 16, 12)
    R(s, (255, 250, 210), 18, 14, 6, 8)
    for x in (16, 23, 31):
        R(s, (40, 40, 52), x, 12, 1, 12)
    pygame.draw.polygon(s, (190, 40, 54), [(24, 1), (36, 12), (12, 12)])
    pygame.draw.polygon(s, (230, 70, 80), [(24, 1), (24, 12), (12, 12)])
    R(s, (40, 40, 52), 23, 0, 2, 2)
    return s


def _towel(c=(80, 160, 220)):
    s = new(32, 16)
    R(s, shade(c, 0.75), 3, 4, 26, 10)
    R(s, c, 3, 4, 26, 9)
    for x in range(5, 28, 6):
        R(s, (250, 250, 250), x, 4, 3, 9)
    R(s, (250, 250, 250), 3, 4, 26, 1)
    return s


def _sandcastle():
    s = new(16, 16)
    sand, dk, lt = (236, 206, 140), (204, 170, 106), (252, 230, 176)
    R(s, dk, 2, 8, 12, 7); R(s, sand, 2, 8, 12, 6)
    R(s, sand, 5, 4, 6, 5); R(s, lt, 5, 4, 2, 5)
    for x in (2, 6, 10):
        R(s, sand, x, 6, 2, 2)
    R(s, (40, 30, 30), 7, 11, 2, 3)
    R(s, (220, 60, 70), 8, 0, 1, 4); R(s, (220, 60, 70), 9, 0, 3, 2)
    return s


def _bench_side(facing="right"):
    """Banco visto de lado (encosto junto à parede, assento virado para o corredor)."""
    s = new(16, 18)
    wood, dk, lt, iron = (160, 106, 62), (112, 72, 42), (194, 140, 90), (50, 44, 56)
    R(s, iron, 3, 3, 2, 14)                     # encosto (pés de ferro)
    R(s, dk, 4, 2, 3, 10)
    R(s, wood, 5, 2, 2, 9)
    R(s, lt, 5, 2, 1, 9)
    R(s, dk, 4, 10, 10, 4)                      # assento
    R(s, wood, 4, 10, 10, 2)
    R(s, lt, 4, 10, 10, 1)
    R(s, iron, 12, 13, 2, 4)
    R(s, iron, 4, 13, 2, 4)
    return s if facing == "right" else pygame.transform.flip(s, True, False)


art.OBJECT_BUILDERS.update({
    "bench_r": lambda: _bench_side("right"), "bench_l": lambda: _bench_side("left"),
    "tree": lambda: _big_tree("oak"), "tree2": lambda: _big_tree("cherry"), "tree3": lambda: _big_tree("orange"),
    "pine": _pine,
    "bush": lambda: _bush_big((255, 140, 180), 0), "bush2": lambda: _bush_big((255, 226, 110), 1),
    "bush3": lambda: _bush_big((196, 160, 255), 2),
    "tallgrass": lambda: _tallgrass(0), "tallgrass_b": lambda: _tallgrass(1),
    "rock": _rock, "rock_big": lambda: _rock(True), "stump": _stump, "log": _log,
    "fence": _fence, "fence_v": lambda: _fence(True), "picnic": _picnic,
    "flowerpot": _flowerpot, "flowerpot2": lambda: _flowerpot((255, 220, 90)),
    "gazebo": _gazebo, "lighthouse": _lighthouse,
    "towel": _towel, "towel2": lambda: _towel((236, 110, 150)), "sandcastle": _sandcastle,
})

TREE_KINDS = {"tree", "tree2", "tree3", "pine", "palm"}
# largura das sombras no chão (pixels de tela / 3, como em game.SHADOW_KINDS)
SHADOWS = {"tree": 80, "tree2": 80, "tree3": 80, "pine": 64, "bush": 30, "bush2": 30, "bush3": 30, "rock": 26,
           "rock_big": 36, "stump": 28, "log": 60, "picnic": 84, "flowerpot": 22, "flowerpot2": 22,
           "bench_r": 26, "bench_l": 26, "gazebo": 170, "lighthouse": 110, "sandcastle": 24, "palm": 34}


def object_image(g, o):
    """Capim alto balança com o vento (dois quadros, defasados pela posição)."""
    if o.kind == "tallgrass":
        k = int(g.t * 1.6 + o.x * 0.37 + o.y * 0.61) % 2
        return art.object_sprite("tallgrass_b" if k else "tallgrass")
    return None


def faded(kind):
    """Versão translúcida da copa (quando a jogadora está atrás da árvore)."""
    def make():
        s = art.object_sprite(kind).copy()
        s.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_MULT)
        return s
    return cached(("faded", kind), make)


# ---------------------------------------------------------------------------
# Chão: grama, terra, bordas arredondadas e detalhes espalhados
# ---------------------------------------------------------------------------
_orig_make_tile = art._make_tile


def _make_tile(name, v):
    if name in ("grass", "flowers"):
        s = new(TS, TS)
        base = [GRASS, (100, 172, 76), (108, 180, 82), (102, 174, 78)][v % 4]
        s.fill(base)
        r = random.Random(v * 97 + 5)
        for _ in range(22):
            P(s, r.choice((shade(base, 0.93), shade(base, 1.05))), r.randrange(16), r.randrange(16))
        for _ in range(4):
            x, y = r.randrange(1, 14), r.randrange(3, 15)
            P(s, GRASS_DK, x, y); P(s, GRASS_DK, x + 2, y); P(s, GRASS_DK, x + 1, y + 1)
            P(s, GRASS_LT, x, y - 1); P(s, GRASS_LT, x + 2, y - 1)
        if name == "flowers":
            for _ in range(5):
                x, y = r.randrange(2, 14), r.randrange(2, 14)
                c = r.choice([(255, 150, 190), (255, 236, 130), (205, 165, 255), (255, 255, 255), (255, 170, 120),
                              (150, 210, 255)])
                for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    P(s, c, x + dx, y + dy)
                P(s, (255, 226, 120), x, y)
                P(s, GRASS_DK, x, y + 2)
        return s
    if name == "dirt":
        s = new(TS, TS)
        base = (204, 158, 104)
        s.fill(base)
        r = random.Random(v * 31 + 9)
        for _ in range(26):
            P(s, r.choice(((192, 146, 96), (214, 170, 116), (184, 138, 90))), r.randrange(16), r.randrange(16))
        for _ in range(2):
            x, y = r.randrange(1, 14), r.randrange(1, 14)
            P(s, (232, 200, 152), x, y); P(s, (150, 112, 74), x + 1, y + 1); P(s, (222, 186, 138), x + 1, y)
        return s
    return _orig_make_tile(name, v)


art._make_tile = _make_tile


def _grass_edge(side):
    def make():
        s = new(TS, TS)
        rr = random.Random(side)
        for i in range(TS):
            h = 2 + rr.choice((0, 1, 1, 2))
            for k in range(h + 1):
                c = GRASS_DK if k == h else (GRASS_LT if k == 0 and i % 3 == 0 else GRASS)
                if side == "up":
                    P(s, c, i, k)
                elif side == "down":
                    P(s, c, i, TS - 1 - k)
                elif side == "left":
                    P(s, c, k, i)
                else:
                    P(s, c, TS - 1 - k, i)
        return up(s)
    return cached(("gedge2", side), make)


art.grass_edge = _grass_edge


def _corner(which, convex):
    """Canto arredondado de grama sobre caminhos.

    convex: grama nos dois lados do canto (arredonda a quina do caminho);
    senão: grama só na diagonal (um pequeno arremate).
    """
    def make():
        s = new(TS, TS)
        cx = 0 if "l" in which else TS - 1
        cy = 0 if "t" in which else TS - 1
        for y in range(TS):
            for x in range(TS):
                ax, ay = abs(x - cx), abs(y - cy)
                if convex:
                    rad = 7
                    if ax < rad and ay < rad:
                        d = math.hypot(rad - ax, rad - ay)
                        if d > rad:
                            P(s, GRASS, x, y)
                        elif d > rad - 1:
                            P(s, GRASS_DK, x, y)
                else:
                    d = math.hypot(ax, ay)
                    if d < 3:
                        P(s, GRASS, x, y)
                    elif d < 4:
                        P(s, GRASS_DK, x, y)
        return up(s)
    return cached(("gcorner", which, convex), make)


_DECOR = {}


def _decor_sprite(kind, v):
    key = (kind, v)
    if key in _DECOR:
        return _DECOR[key]
    s = new(TS, TS)
    r = random.Random(v * 13 + len(kind))
    ox, oy = r.randrange(2, 10), r.randrange(5, 12)
    if kind == "tuft":
        for i in range(r.randint(3, 5)):
            x = ox + i * 2 - 1 + r.choice((0, 1))
            hgt = r.randint(2, 4)
            for k in range(hgt):
                P(s, GRASS_DK if k < hgt - 1 else GRASS_LT, x + (1 if k == hgt - 1 and i % 2 else 0), oy - k)
    elif kind == "flower":
        c = r.choice([(255, 255, 255), (255, 230, 120), (250, 160, 200), (190, 170, 255)])
        for i in range(r.randint(2, 3)):
            x, y = ox + r.randrange(0, 5), oy + r.randrange(-2, 2)
            P(s, GRASS_DK, x, y + 1)
            P(s, c, x, y)
            P(s, c, x - 1, y); P(s, c, x + 1, y); P(s, c, x, y - 1)
            P(s, (255, 214, 90), x, y)
    elif kind == "pebble":
        R(s, (110, 106, 118), ox, oy, 3, 2)
        R(s, (176, 172, 184), ox, oy, 2, 1)
        P(s, (120, 116, 128), ox + 4, oy + 1)
    elif kind == "ripple":
        for i in range(2):
            R(s, (232, 210, 156), ox + i * 3, oy + i * 3, 5, 1)
            R(s, (255, 246, 214), ox + i * 3 + 1, oy + i * 3 - 1, 3, 1)
    elif kind == "sandpebble":
        P(s, (200, 180, 150), ox, oy); P(s, (170, 150, 126), ox + 1, oy)
        P(s, (250, 250, 246), ox + 4, oy + 2); P(s, (236, 220, 200), ox + 5, oy + 2)
    elif kind == "clover":
        for (dx, dy) in ((0, 0), (1, -1), (2, 0), (1, 1)):
            P(s, (70, 150, 70), ox + dx, oy + dy)
        P(s, (130, 200, 100), ox + 1, oy)
    sp = up(s)
    _DECOR[key] = sp
    return sp


def decorate_floor(m, surf):
    """Detalhes do chão ao ar livre: cantos de grama arredondados e enfeites na grama."""
    if not m.outdoor:
        return
    grassy = ("grass", "flowers")
    skip = grassy + ("wall", "wall_top", "glass", "void", "door", "water", "sea", "sea_foam", "fountain")
    taken = set()
    for o in m.objects:
        for yy in range(o.y, o.y + o.h):
            for xx in range(o.x, o.x + o.w):
                taken.add((xx, yy))

    def g(x, y):
        return m.tile_at(x, y) in grassy

    for y in range(m.h):
        for x in range(m.w):
            t = m.tiles[y][x]
            if t in skip:
                continue
            for which, (dx, dy) in (("tl", (-1, -1)), ("tr", (1, -1)), ("bl", (-1, 1)), ("br", (1, 1))):
                a, b = g(x + dx, y), g(x, y + dy)
                if a and b:
                    surf.blit(_corner(which, True), (x * TILE, y * TILE))
                elif not a and not b and g(x + dx, y + dy):
                    surf.blit(_corner(which, False), (x * TILE, y * TILE))
    rnd = random.Random(m.name + "-decor")
    for y in range(m.h):
        for x in range(m.w):
            if m.tiles[y][x] == "sand" and (x, y) not in taken:
                k = rnd.random()
                if k < 0.12:
                    surf.blit(_decor_sprite("ripple", rnd.randrange(4)), (x * TILE, y * TILE))
                elif k < 0.15:
                    surf.blit(_decor_sprite("sandpebble", rnd.randrange(4)), (x * TILE, y * TILE))
                continue
            if m.tiles[y][x] != "grass" or (x, y) in taken:
                continue
            k = rnd.random()
            if k < 0.16:
                kind = "tuft"
            elif k < 0.21:
                kind = "flower"
            elif k < 0.24:
                kind = "clover"
            elif k < 0.265:
                kind = "pebble"
            else:
                continue
            surf.blit(_decor_sprite(kind, rnd.randrange(6)), (x * TILE, y * TILE))


# Borda da água: barranco de terra em cima, espuma nas laterais (estilo lago do Stardew)
def _water_edge(side, frame=0):
    if side.startswith("c_"):
        return _water_corner(side[2:])

    def make():
        s = new(TS, TS)
        if side == "up":
            R(s, (92, 70, 50), 0, 0, TS, 2)
            R(s, (64, 50, 40), 0, 2, TS, 1)
            R(s, (44, 100, 150), 0, 3, TS, 1)
            y0 = 4
        else:
            y0 = 0
        for i in range(TS):
            if (i + frame * 3) % 4 == 0:
                continue
            h = 1 + ((i + frame * 5) % 7 == 0)
            for k in range(h):
                c = (190, 228, 248) if k == 0 else (150, 206, 240)
                if side == "up":
                    P(s, c, i, y0 + k)
                elif side == "down":
                    P(s, c, i, TS - 1 - k)
                elif side == "left":
                    P(s, (60, 116, 160) if k == 0 and i % 5 == 0 else c, k, i)
                else:
                    P(s, c, TS - 1 - k, i)
        return up(s)
    return cached(("wedge2", side, frame), make)


art.water_edge = _water_edge


def _water_corner(which):
    """Canto arredondado do lago (grama dos dois lados)."""
    def make():
        s = new(TS, TS)
        cx = 0 if "l" in which else TS - 1
        cy = 0 if "t" in which else TS - 1
        rad = 6
        for y in range(TS):
            for x in range(TS):
                ax, ay = abs(x - cx), abs(y - cy)
                if ax < rad and ay < rad:
                    d = math.hypot(rad - ax, rad - ay)
                    if d > rad + 0.5:
                        P(s, GRASS, x, y)
                    elif d > rad - 0.7:
                        P(s, (64, 50, 40), x, y)
                    elif d > rad - 1.7:
                        P(s, (150, 206, 240), x, y)
        return up(s)
    return cached(("wcorner", which), make)

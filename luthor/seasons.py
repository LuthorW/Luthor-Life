"""Estações do ano: cada trimestre é uma estação (Q1 primavera, Q2 verão, Q3 outono, Q4 inverno).

A estação muda o cenário (cor da grama, árvores floridas, folhas laranja, árvores peladas com neve), os efeitos
do ar (pétalas, vagalumes, folhas caindo, neve), a chuva (vira neve no inverno), os coletáveis e as roupas de
todo mundo (characters.dress). Game.apply_season() chama set_season() ao começar o dia e ao carregar o jogo.
"""
import random

import pygame

from . import art, scenery, effects
from .art import new, P, R, shade, mix

SEASONS = ["spring", "summer", "autumn", "winter"]
NAMES = {"spring": "Primavera", "summer": "Verão", "autumn": "Outono", "winter": "Inverno"}
CURRENT = {"season": "spring"}


def of_quarter(q):
    return SEASONS[(q - 1) % 4]


# grama: (base, escura, clara)
GRASS = {
    "spring": ((104, 176, 78), (78, 142, 62), (146, 206, 98)),
    "summer": ((92, 168, 64), (66, 132, 50), (140, 200, 84)),
    "autumn": ((150, 156, 74), (118, 120, 58), (190, 182, 98)),
    "winter": ((226, 234, 242), (186, 200, 220), (250, 252, 255)),
}
# copa das árvores: contorno, escuro, médio, base, claro
LEAVES = {
    "spring": dict(scenery.LEAF),
    "summer": {**scenery.LEAF,
               "oak": [(24, 62, 40), (36, 94, 50), (50, 122, 58), (70, 150, 64), (118, 186, 80)],
               "cherry": [(24, 62, 40), (36, 94, 50), (52, 124, 60), (72, 152, 66), (122, 190, 84)]},
    "autumn": {**scenery.LEAF,
               "oak": [(92, 40, 24), (150, 66, 30), (196, 98, 38), (226, 136, 52), (246, 186, 92)],
               "cherry": [(96, 30, 30), (152, 46, 40), (192, 70, 46), (220, 104, 60), (240, 156, 96)],
               "orange": [(74, 60, 30), (110, 90, 40), (140, 116, 50), (166, 140, 62), (206, 180, 96)]},
    "winter": dict(scenery.LEAF),
}
SNOW = [(150, 166, 196), (196, 210, 230), (220, 230, 242), (238, 244, 250), (255, 255, 255)]

_orig_big_tree = scenery._big_tree
_orig_pine = scenery._pine
_orig_bush = scenery._bush_big
_orig_tallgrass = scenery._tallgrass
_orig_make_tile = art._make_tile


def _bare_tree(kind):
    """Inverno: árvore pelada, galhos com neve por cima."""
    s = new(48, 64)
    scenery._trunk(s, 24, 34, 62)
    trunk = scenery.TRUNK
    rnd = random.Random(kind)
    branches = [((24, 36), (10, 20)), ((24, 34), (38, 18)), ((24, 30), (24, 8)), ((17, 27), (7, 30)),
                ((31, 26), (42, 30)), ((14, 22), (16, 12)), ((33, 21), (31, 11)), ((24, 18), (17, 10)),
                ((24, 16), (31, 9))]
    for (a, b) in branches:
        pygame.draw.line(s, trunk[0], a, b, 3)
        pygame.draw.line(s, trunk[1], a, b, 1)
        # neve em cima do galho
        steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for k in range(0, steps, 2):
            x = a[0] + (b[0] - a[0]) * k // max(1, steps)
            y = a[1] + (b[1] - a[1]) * k // max(1, steps)
            if rnd.random() < 0.7:
                P(s, SNOW[4], x, y - 2)
                P(s, SNOW[3], x + 1, y - 2)
    for _ in range(10):
        b = rnd.choice(branches)[1]
        P(s, SNOW[4], b[0], b[1] - 1)
    return s


def _big_tree(kind="oak"):
    season = CURRENT["season"]
    if season == "winter" and kind in ("oak", "cherry"):
        return _bare_tree(kind)
    saved = scenery.LEAF
    scenery.LEAF = LEAVES[season]
    try:
        if kind == "cherry" and season != "spring":
            # fora da primavera a cerejeira perde as flores brancas: copa comum com a cor da estação
            scenery.LEAF = {**LEAVES[season], "oak": LEAVES[season]["cherry"]}
            s = _orig_big_tree("oak")
        else:
            s = _orig_big_tree(kind)
    finally:
        scenery.LEAF = saved
    if season == "winter":
        _snow_cap(s)
    return s


def _snow_cap(s, rows=3):
    """Neve na parte de cima da copa (só onde tem folha)."""
    w, h = s.get_size()
    for x in range(w):
        seen = 0
        for y in range(h):
            if s.get_at((x, y)).a > 0:
                if seen < rows:
                    s.set_at((x, y), SNOW[4] if seen else SNOW[3])
                seen += 1
                if seen >= rows:
                    break


def _pine():
    s = _orig_pine()
    if CURRENT["season"] == "winter":
        # neve em cima de cada andar do pinheiro
        w, h = s.get_size()
        for y in range(1, h):
            for x in range(w):
                c = s.get_at((x, y))
                if c.a and s.get_at((x, y - 1)).a == 0 and y < 50:
                    s.set_at((x, y), SNOW[4])
                    if y + 1 < h and s.get_at((x, y + 1)).a:
                        s.set_at((x, y + 1), SNOW[2])
    return s


def _bush_big(flower=(255, 140, 180), seed=0):
    season = CURRENT["season"]
    saved = scenery.LEAF
    scenery.LEAF = LEAVES[season]
    try:
        if season == "autumn":
            s = _orig_bush((236, 120, 40), seed)
        elif season == "winter":
            scenery.LEAF = {**LEAVES[season], "oak": [(40, 70, 56), (56, 96, 70), (70, 116, 80), (90, 136, 92),
                                                      (130, 170, 120)]}
            s = _orig_bush((255, 255, 255), seed)
            _snow_cap(s, 2)
        else:
            s = _orig_bush(flower, seed)
    finally:
        scenery.LEAF = saved
    return s


def _tallgrass(frame=0):
    s = _orig_tallgrass(frame)
    season = CURRENT["season"]
    if season in ("autumn", "winter"):
        tint = (214, 184, 100) if season == "autumn" else (232, 238, 246)
        w, h = s.get_size()
        for y in range(h):
            for x in range(w):
                c = s.get_at((x, y))
                if c.a:
                    s.set_at((x, y), (*mix(c[:3], tint, 0.55 if season == "autumn" else 0.75), c.a))
    return s


def _make_tile(name, v):
    season = CURRENT["season"]
    if name in ("grass", "flowers"):
        base_c, dk, lt = GRASS[season]
        s = new(16, 16)
        base = [base_c, shade(base_c, 0.97), shade(base_c, 1.03), shade(base_c, 0.99)][v % 4]
        s.fill(base)
        r = random.Random(v * 97 + 5)
        for _ in range(22):
            P(s, r.choice((shade(base, 0.93), shade(base, 1.05))), r.randrange(16), r.randrange(16))
        for _ in range(4):
            x, y = r.randrange(1, 14), r.randrange(3, 15)
            P(s, dk, x, y); P(s, dk, x + 2, y); P(s, dk, x + 1, y + 1)
            P(s, lt, x, y - 1); P(s, lt, x + 2, y - 1)
        for _ in range(7):                  # folhinhas de grama: risquinhos claros com a base escura
            x, y = r.randrange(0, 16), r.randrange(2, 16)
            P(s, mix(base, lt, 0.7), x, y - 1)
            P(s, mix(base, lt, 0.35), x, y)
            P(s, shade(base, 0.86), x, y + 1)
        if name == "flowers" and season != "winter":
            cols = {"spring": [(255, 150, 190), (255, 236, 130), (205, 165, 255), (255, 255, 255), (255, 170, 120),
                               (150, 210, 255)],
                    "summer": [(255, 220, 80), (255, 120, 90), (255, 255, 255), (250, 150, 200)],
                    "autumn": [(230, 120, 50), (200, 70, 50), (240, 190, 80)]}[season]
            for _ in range(5 if season != "autumn" else 3):
                x, y = r.randrange(2, 14), r.randrange(2, 14)
                c = r.choice(cols)
                for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    P(s, c, x + dx, y + dy)
                P(s, (255, 226, 120), x, y)
                P(s, dk, x, y + 2)
        return s
    return _orig_make_tile(name, v)


# troca os construtores do cenário pelos que conhecem a estação
art._make_tile = _make_tile
art.OBJECT_BUILDERS.update({
    "tree": lambda: _big_tree("oak"), "tree2": lambda: _big_tree("cherry"), "tree3": lambda: _big_tree("orange"),
    "pine": _pine,
    "bush": lambda: _bush_big((255, 140, 180), 0), "bush2": lambda: _bush_big((255, 226, 110), 1),
    "bush3": lambda: _bush_big((196, 160, 255), 2),
    "tallgrass": lambda: _tallgrass(0), "tallgrass_b": lambda: _tallgrass(1),
})

SEASONAL_KEYS = ("tile", "obj", "faded", "gedge2", "gcorner")


def set_season(season, world=None):
    """Aplica a estação: cores, árvores, efeitos e o chão já desenhado dos mapas ao ar livre."""
    if season == CURRENT["season"] and CURRENT.get("applied"):
        return False
    CURRENT["season"] = season
    CURRENT["applied"] = True
    scenery.GRASS, scenery.GRASS_DK, scenery.GRASS_LT = GRASS[season]
    effects.SEASON = season
    for k in [k for k in art._cache if isinstance(k, tuple) and k and k[0] in SEASONAL_KEYS]:
        del art._cache[k]
    if hasattr(scenery, "_DECOR"):
        scenery._DECOR.clear()
    if world:
        for m in world.values():
            if any(t in ("grass", "flowers") for row in m.tiles for t in row):
                m._build_floor()
    return True


# coletáveis de cada estação (os que não aparecem aqui saem o ano todo)
FORAGE_SEASONS = {
    "estrela_mar": ("spring", "summer"), "coral": ("summer",), "flor_silvestre": ("spring", "summer"),
    "amora": ("summer", "autumn"), "trevo4": ("spring",), "dente_leao": ("spring", "summer"),
    "pinha": ("autumn", "winter"),
}
FORAGE_EXTRA_WEIGHT = {"autumn": 3.0}      # cogumelos: muito mais comuns no outono


def forage_ok(item):
    return CURRENT["season"] in FORAGE_SEASONS.get(item, SEASONS)


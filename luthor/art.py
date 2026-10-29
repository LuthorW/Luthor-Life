"""Arte procedural em pixel art. Tudo é desenhado em 16 px e ampliado 3x."""
import os
import random
import pygame

from .config import TS, SCALE, TILE, ASSETS

_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def new(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def up(surf, k=SCALE):
    return pygame.transform.scale(surf, (surf.get_width() * k, surf.get_height() * k))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def R(s, color, x, y, w, h):
    pygame.draw.rect(s, color, (x, y, w, h))


def P(s, color, x, y):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), color)


def _speckle(s, colors, seed, n):
    r = random.Random(seed)
    w, h = s.get_size()
    for _ in range(n):
        P(s, r.choice(colors), r.randrange(w), r.randrange(h))


# ---------------------------------------------------------------------------
# Tiles de chão
# ---------------------------------------------------------------------------

def _make_tile(name, v):
    s = new(TS, TS)
    r = random.Random(hash((name, v)) & 0xFFFFF)
    if name in ("grass", "flowers"):
        base = [(112, 184, 92), (106, 178, 88), (116, 188, 96), (110, 182, 90)][v % 4]
        s.fill(base)
        _speckle(s, [shade(base, 0.9), shade(base, 1.07), shade(base, 0.94)], v * 13 + 3, 26)
        for _ in range(3):
            x, y = r.randrange(1, 14), r.randrange(4, 15)
            dk, lt = shade(base, 0.76), mix(base, (220, 250, 170), 0.45)
            P(s, dk, x, y); P(s, dk, x + 2, y); P(s, lt, x + 1, y - 1); P(s, lt, x, y - 1); P(s, lt, x + 2, y - 1)
        if name == "flowers":
            for _ in range(5):
                x, y = r.randrange(2, 14), r.randrange(2, 14)
                c = r.choice([(255, 150, 190), (255, 236, 130), (205, 165, 255), (255, 255, 255), (255, 170, 120),
                              (150, 210, 255)])
                for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    P(s, c, x + dx, y + dy)
                P(s, (255, 226, 120), x, y)
                P(s, shade(base, 0.7), x, y + 2)
    elif name == "pavement":
        s.fill((184, 178, 190))
        _speckle(s, [(172, 166, 180), (194, 188, 200)], v + 5, 14)
        R(s, (156, 150, 166), 0, 0, 16, 1); R(s, (156, 150, 166), 0, 0, 1, 16)
        R(s, (204, 198, 210), 1, 1, 15, 1); R(s, (204, 198, 210), 1, 1, 1, 15)
        if v % 3 == 0:
            P(s, (130, 126, 140), 9, 6); P(s, (130, 126, 140), 10, 7); P(s, (130, 126, 140), 10, 8)
    elif name == "plaza":
        s.fill((222, 204, 178))
        R(s, (198, 180, 154), 0, 7, 16, 1); R(s, (198, 180, 154), 0, 15, 16, 1)
        off = 0 if v % 2 == 0 else 4
        R(s, (176, 162, 142), 4 + off, 0, 1, 7); R(s, (176, 162, 142), 12 - off, 8, 1, 7)
        _speckle(s, [(206, 192, 172), (186, 172, 152)], v + 11, 10)
    elif name.startswith("road") or name.startswith("cross"):
        s.fill((86, 84, 100))
        _speckle(s, [(78, 76, 92), (94, 92, 108), (100, 98, 114)], v + 9, 22)
        if name == "road_line_b":
            R(s, (236, 200, 84), 3, 15, 10, 1)
        elif name == "road_line_t":
            R(s, (236, 200, 84), 3, 0, 10, 1)
        elif name == "road_line_r":
            R(s, (236, 200, 84), 15, 3, 1, 10)
        elif name == "road_line_l":
            R(s, (236, 200, 84), 0, 3, 1, 10)
        elif name == "cross":
            for x in (1, 5, 9, 13):
                R(s, (232, 232, 238), x, 1, 2, 14)
        elif name == "cross_v":
            for y in (1, 5, 9, 13):
                R(s, (232, 232, 238), 1, y, 14, 2)
    elif name == "dirt":
        s.fill((218, 176, 126))
        _speckle(s, [(204, 162, 114), (228, 190, 140), (196, 154, 108), (236, 200, 152)], v + 21, 26)
        if v % 3 == 0:
            P(s, (170, 140, 110), 5, 9); P(s, (240, 220, 190), 5, 8)
    elif name == "sand":
        s.fill((248, 230, 178))
        _speckle(s, [(238, 218, 164), (252, 240, 196), (230, 206, 154)], v + 31, 28)
        if v % 4 == 1:
            P(s, (250, 250, 250), 6, 9); P(s, (240, 220, 200), 7, 9)
    elif name in ("water", "sea", "sea_foam"):
        deep = (84, 170, 226) if name == "water" else (64, 146, 214)
        s.fill(deep)
        for i in range(4):
            y = (i * 4 + v * 2) % 16
            x = (i * 7 + v * 3) % 12
            R(s, mix(deep, (255, 255, 255), 0.35), x, y, 4, 1)
            R(s, mix(deep, (255, 255, 255), 0.18), (x + 6) % 14, (y + 2) % 16, 2, 1)
        if name == "sea_foam":
            for x in range(16):
                h = 2 + ((x + v) % 4 == 0)
                R(s, (232, 244, 250), x, 0, 1, h)
            R(s, (180, 214, 236), 0, 3, 16, 1)
    elif name in ("boardwalk", "pier"):
        s.fill((156, 112, 72))
        if name == "boardwalk":
            for y in (0, 4, 8, 12):
                R(s, (128, 88, 56), 0, y + 3, 16, 1)
                R(s, (172, 126, 84), 0, y, 16, 1)
        else:
            for x in (0, 4, 8, 12):
                R(s, (128, 88, 56), x + 3, 0, 1, 16)
                R(s, (172, 126, 84), x, 0, 1, 16)
        _speckle(s, [(140, 98, 62)], v + 41, 6)
    elif name in ("wood", "wood_dark"):
        base = (154, 104, 66) if name == "wood" else (96, 62, 46)
        s.fill(base)
        for y in (3, 7, 11, 15):
            R(s, shade(base, 0.8), 0, y, 16, 1)
        off = (v % 2) * 6
        for y, x in ((0, 5 + off), (4, 11 - off), (8, 2 + off), (12, 9)):
            R(s, shade(base, 0.8), x % 16, y, 1, 3)
        _speckle(s, [shade(base, 1.08)], v + 2, 8)
    elif name == "marble":
        s.fill((230, 226, 236))
        R(s, (208, 202, 218), 0, 0, 16, 1); R(s, (208, 202, 218), 0, 0, 1, 16)
        for _ in range(3):
            x, y = r.randrange(14), r.randrange(14)
            P(s, (214, 208, 224), x, y); P(s, (214, 208, 224), x + 1, y + 1)
    elif name in ("lab", "tile_white"):
        s.fill((216, 222, 232) if name == "lab" else (236, 238, 242))
        c = (192, 198, 212) if name == "lab" else (210, 214, 222)
        R(s, c, 0, 0, 16, 1); R(s, c, 0, 0, 1, 16); R(s, c, 0, 8, 16, 1); R(s, c, 8, 0, 1, 16)
    elif name in ("carpet", "carpet_blue", "office"):
        base = {"carpet": (82, 44, 114), "carpet_blue": (54, 72, 112), "office": (104, 110, 126)}[name]
        s.fill(base)
        _speckle(s, [shade(base, 1.1), shade(base, 0.9)], v + 4, 24)
    elif name == "checker":
        a, b = (216, 200, 174), (72, 54, 48)
        s.fill(a)
        R(s, b, 0, 0, 8, 8); R(s, b, 8, 8, 8, 8)
    elif name == "terracotta":
        s.fill((196, 112, 78))
        R(s, (168, 92, 62), 0, 0, 16, 1); R(s, (168, 92, 62), 0, 0, 1, 16)
        R(s, (168, 92, 62), 0, 8, 16, 1); R(s, (168, 92, 62), 8, 0, 1, 16)
        _speckle(s, [(206, 124, 88), (184, 102, 70)], v + 7, 10)
    elif name == "wall":
        s.fill((100, 86, 130))
        R(s, (116, 102, 148), 0, 0, 16, 7)
        R(s, (124, 110, 158), 0, 0, 16, 1)
        R(s, (74, 62, 98), 0, 11, 16, 5)
        R(s, (132, 116, 166), 0, 10, 16, 1)
        R(s, (54, 44, 74), 0, 15, 16, 1)
    elif name == "wall_top":
        s.fill((40, 32, 56))
        R(s, (52, 42, 70), 0, 0, 16, 2)
    elif name == "glass":
        s.fill((170, 208, 232))
        R(s, (120, 130, 150), 0, 0, 16, 2)
        R(s, (120, 130, 150), 0, 14, 16, 2)
        R(s, (214, 238, 250), 3, 4, 1, 6); R(s, (214, 238, 250), 5, 3, 1, 4)
    elif name == "door":
        s.fill((44, 34, 52))
        R(s, (130, 64, 72), 2, 10, 12, 6)
        R(s, (150, 80, 88), 3, 11, 10, 1)
    else:
        s.fill((255, 0, 255))
    return s


def tile(name, v=0):
    return cached(("tile", name, v), lambda: up(_make_tile(name, v)))


def grass_edge(side):
    """Franja de grama desenhada sobre o tile vizinho (side = lado onde está a grama)."""
    def make():
        s = new(TS, TS)
        g, dk, lt = (110, 182, 90), (78, 140, 66), (150, 214, 118)
        rr = random.Random(side)
        for i in range(TS):
            h = 2 + rr.choice((0, 0, 1, 1, 2))
            for k in range(h):
                c = lt if k == 0 else g
                if side == "up":
                    P(s, c, i, k)
                elif side == "down":
                    P(s, c, i, TS - 1 - k)
                elif side == "left":
                    P(s, c, k, i)
                else:
                    P(s, c, TS - 1 - k, i)
            if side == "up":
                P(s, dk, i, h)
            elif side == "down":
                P(s, dk, i, TS - 1 - h)
            elif side == "left":
                P(s, dk, h, i)
            else:
                P(s, dk, TS - 1 - h, i)
        return up(s)
    return cached(("gedge", side), make)


def water_edge(side, frame=0):
    def make():
        s = new(TS, TS)
        for i in range(TS):
            if (i + frame * 3) % 4 == 0:
                continue
            h = 1 + ((i + frame * 5) % 7 == 0)
            for k in range(h):
                c = (190, 228, 248) if k == 0 else (150, 206, 240)
                if side == "up":
                    P(s, c, i, k)
                elif side == "down":
                    P(s, c, i, TS - 1 - k)
                elif side == "left":
                    P(s, c, k, i)
                else:
                    P(s, c, TS - 1 - k, i)
        return up(s)
    return cached(("wedge", side, frame), make)


# ---------------------------------------------------------------------------
# Objetos
# ---------------------------------------------------------------------------

def _tree(kind=0):
    s = new(32, 46)
    R(s, (120, 80, 52), 13, 30, 6, 15)
    R(s, (96, 62, 40), 13, 30, 2, 15)
    R(s, (146, 102, 66), 17, 31, 1, 12)
    R(s, (96, 62, 40), 11, 43, 10, 2)
    base = [(70, 160, 86), (236, 150, 186), (62, 150, 96)][kind % 3]
    out = shade(base, 0.62)
    blobs = [(16, 18, 12), (8, 22, 8), (24, 22, 8), (16, 10, 9), (10, 14, 6), (22, 13, 6), (16, 26, 8)]
    for (x, y, rad) in blobs:
        pygame.draw.circle(s, out, (x, y), rad + 1)
    for (x, y, rad) in blobs:
        pygame.draw.circle(s, base, (x, y), rad)
    for (x, y, rad) in [(13, 12, 5), (20, 9, 3), (8, 19, 3), (24, 18, 3)]:
        pygame.draw.circle(s, mix(base, (255, 255, 230), 0.3), (x, y), rad)
    for (x, y, rad) in [(10, 27, 5), (22, 27, 5), (16, 29, 5)]:
        pygame.draw.circle(s, shade(base, 0.82), (x, y), rad)
    for (x, y) in ((11, 9), (19, 6), (6, 17), (25, 15), (15, 16)):
        P(s, mix(base, (255, 255, 255), 0.65), x, y)
    if kind == 2:
        for (x, y) in ((9, 16), (21, 12), (14, 22), (24, 22), (17, 14)):
            pygame.draw.circle(s, (255, 170, 60), (x, y), 2)
            P(s, (255, 230, 160), x - 1, y - 1)
    if kind == 1:
        for (x, y) in ((9, 14), (21, 11), (14, 22), (25, 20), (17, 8)):
            P(s, (255, 255, 255), x, y); P(s, (255, 220, 236), x + 1, y)
    return s


def _bush(color=(255, 140, 180)):
    s = new(16, 18)
    base = (80, 170, 92)
    for (x, y, rad) in [(8, 10, 7), (4, 12, 4), (12, 12, 4)]:
        pygame.draw.circle(s, shade(base, 0.62), (x, y), rad + 1)
    for (x, y, rad) in [(8, 10, 7), (4, 12, 4), (12, 12, 4)]:
        pygame.draw.circle(s, base, (x, y), rad)
    pygame.draw.circle(s, mix(base, (255, 255, 220), 0.3), (6, 7), 3)
    for (x, y) in ((5, 9), (10, 6), (11, 12), (7, 13), (3, 12)):
        P(s, color, x, y); P(s, color, x + 1, y); P(s, color, x, y + 1); P(s, (255, 236, 150), x + 1, y + 1)
    return s


def _palm():
    s = new(32, 52)
    for i in range(30):
        x = 15 + int((i / 30) ** 2 * 3)
        R(s, (150, 112, 70) if i % 3 else (124, 90, 56), x, 50 - i, 3, 1)
    for ang, ln in ((-60, 14), (-20, 15), (20, 15), (60, 14), (-100, 10), (100, 10)):
        v = pygame.math.Vector2(0, -1).rotate(ang)
        for k in range(ln):
            px, py = 17 + v.x * k, 20 + v.y * k + (k * k) / 28
            pygame.draw.circle(s, (54, 140, 70) if k % 2 else (70, 160, 84), (int(px), int(py)), 2)
    pygame.draw.circle(s, (120, 80, 40), (16, 22), 2); pygame.draw.circle(s, (120, 80, 40), (19, 22), 2)
    return s


def _hedge():
    s = new(16, 20)
    base = (74, 160, 84)
    R(s, shade(base, 0.85), 0, 8, 16, 12)
    pygame.draw.ellipse(s, base, (-2, 2, 20, 14))
    R(s, shade(base, 0.7), 0, 17, 16, 3)
    for x in (2, 7, 12):
        pygame.draw.circle(s, mix(base, (255, 255, 220), 0.25), (x + 1, 6), 2)
    return s


def _planter():
    s = new(20, 40)
    R(s, (150, 140, 150), 1, 30, 18, 10)
    R(s, (176, 166, 178), 1, 30, 18, 2)
    R(s, (90, 64, 44), 9, 18, 3, 12)
    for (x, y, rad, c) in [(10, 13, 8, (56, 130, 70)), (6, 16, 5, (64, 142, 76)), (14, 16, 5, (64, 142, 76)),
                           (10, 9, 5, (84, 166, 92))]:
        pygame.draw.circle(s, c, (x, y), rad)
    return s


def _lamp():
    s = new(16, 42)
    R(s, (40, 38, 52), 7, 9, 2, 31)
    R(s, (40, 38, 52), 5, 38, 6, 3)
    R(s, (54, 50, 70), 4, 4, 8, 5)
    R(s, (255, 230, 150), 5, 8, 6, 2)
    return s


def _bench():
    s = new(16, 16)
    R(s, (146, 96, 56), 1, 4, 14, 2)
    R(s, (146, 96, 56), 1, 8, 14, 3)
    R(s, (112, 72, 42), 1, 11, 14, 1)
    R(s, (50, 44, 56), 2, 12, 2, 4); R(s, (50, 44, 56), 12, 12, 2, 4)
    return s


def _statue():
    s = new(16, 36)
    R(s, (140, 136, 150), 2, 26, 12, 9)
    R(s, (170, 166, 180), 2, 26, 12, 2)
    R(s, (120, 40, 190), 5, 6, 3, 18)
    R(s, (120, 40, 190), 5, 21, 8, 3)
    R(s, (184, 100, 255), 5, 6, 1, 18)
    return s


def _hydrant():
    s = new(16, 16)
    R(s, (200, 50, 50), 5, 4, 6, 10)
    R(s, (230, 80, 70), 4, 3, 8, 3)
    R(s, (170, 40, 40), 3, 7, 10, 2)
    R(s, (90, 80, 80), 4, 14, 8, 2)
    return s


def _busstop():
    s = new(32, 40)
    R(s, (60, 60, 72), 2, 8, 2, 32); R(s, (60, 60, 72), 28, 8, 2, 32)
    R(s, (120, 40, 190), 0, 4, 32, 5)
    R(s, (180, 210, 230, 160), 4, 10, 24, 18)
    R(s, (140, 100, 60), 6, 30, 20, 3)
    R(s, (250, 250, 250), 26, 0, 6, 6); R(s, (40, 90, 160), 27, 1, 4, 4)
    return s


def _umbrella(color=(220, 60, 70)):
    s = new(32, 40)
    pygame.draw.ellipse(s, color, (0, 4, 32, 14))
    for i in range(0, 32, 8):
        pygame.draw.polygon(s, (250, 250, 250), [(16, 4), (i, 12), (i + 4, 12)])
    R(s, (220, 220, 220), 15, 14, 2, 26)
    R(s, (240, 230, 200), 4, 34, 14, 4)
    return s


def _lifeguard():
    s = new(32, 52)
    R(s, (230, 230, 236), 4, 10, 24, 14)
    R(s, (220, 60, 60), 2, 4, 28, 7)
    R(s, (250, 250, 250), 10, 13, 12, 6)
    for x in (6, 24):
        R(s, (190, 150, 100), x, 24, 3, 28)
    R(s, (190, 150, 100), 6, 36, 21, 2)
    return s


def _boat():
    s = new(48, 28)
    pygame.draw.polygon(s, (240, 240, 244), [(2, 12), (46, 12), (40, 24), (8, 24)])
    R(s, (40, 90, 160), 6, 18, 36, 2)
    R(s, (200, 200, 210), 18, 4, 14, 8)
    R(s, (120, 170, 220), 20, 6, 4, 3); R(s, (120, 170, 220), 26, 6, 4, 3)
    return s


def _kiosk():
    s = new(48, 44)
    R(s, (150, 104, 66), 2, 18, 44, 26)
    R(s, (120, 80, 50), 2, 18, 44, 3)
    for i in range(0, 48, 8):
        R(s, (40, 110, 170) if (i // 8) % 2 == 0 else (250, 250, 250), i, 8, 8, 10)
    R(s, (60, 60, 70), 4, 4, 2, 6); R(s, (60, 60, 70), 42, 4, 2, 6)
    R(s, (230, 220, 190), 8, 24, 32, 6)
    R(s, (200, 120, 90), 10, 26, 6, 3); R(s, (90, 160, 200), 20, 26, 8, 3)
    return s


def _bed(w=2):
    W = 16 * w
    s = new(W, 40)
    R(s, (92, 60, 40), 0, 0, W, 12)
    R(s, (112, 76, 50), 1, 1, W - 2, 9)
    R(s, (92, 60, 40), 0, 12, W, 28)
    R(s, (246, 242, 250), 2, 12, W - 4, 9)
    for px in range(4, W - 6, 14):
        R(s, (255, 255, 255), px, 13, 11, 6)
        R(s, (230, 226, 240), px, 18, 11, 1)
    R(s, (118, 44, 176), 2, 21, W - 4, 17)
    R(s, (142, 66, 202), 2, 21, W - 4, 2)
    R(s, (96, 34, 150), 2, 36, W - 4, 2)
    R(s, (230, 200, 120), 2, 26, W - 4, 1)
    return s


def _nightstand():
    s = new(16, 24)
    R(s, (110, 74, 48), 1, 10, 14, 14)
    R(s, (130, 90, 60), 1, 10, 14, 2)
    R(s, (90, 60, 40), 3, 16, 10, 1)
    R(s, (240, 220, 160), 5, 2, 6, 5)
    R(s, (60, 50, 60), 7, 7, 2, 3)
    return s


def _wardrobe():
    s = new(32, 40)
    R(s, (100, 66, 44), 0, 2, 32, 38)
    R(s, (122, 84, 56), 1, 3, 14, 36); R(s, (122, 84, 56), 17, 3, 14, 36)
    R(s, (220, 190, 110), 13, 20, 1, 4); R(s, (220, 190, 110), 18, 20, 1, 4)
    return s


def _tv(big=False):
    W = 32 if not big else 48
    s = new(W, 28)
    R(s, (30, 28, 38), 1, 2, W - 2, 18)
    R(s, (60, 30, 100), 3, 4, W - 6, 14)
    R(s, (120, 70, 190), 4, 5, 10, 2)
    R(s, (90, 50, 150), 4, 9, W - 10, 1)
    R(s, (40, 36, 50), 2, 22, W - 4, 6)
    R(s, (70, 64, 84), 2, 22, W - 4, 1)
    return s


def _tv_wall():
    s = new(64, 16)
    for i in range(4):
        R(s, (30, 30, 40), i * 16 + 1, 2, 14, 11)
        c = [(200, 60, 60), (60, 120, 200), (230, 180, 60), (120, 200, 120)][i]
        R(s, c, i * 16 + 2, 3, 12, 9)
        R(s, (250, 250, 250), i * 16 + 3, 9, 8, 1)
    return s


def _sofa(w=3, color=(96, 40, 140)):
    s = new(16 * w, 22)
    R(s, color, 0, 2, 16 * w, 12)
    R(s, shade(color, 1.22), 0, 10, 16 * w, 9)
    R(s, shade(color, 0.82), 0, 2, 3, 18); R(s, shade(color, 0.82), 16 * w - 3, 2, 3, 18)
    for i in range(1, w):
        R(s, shade(color, 1.05), i * 16, 10, 1, 8)
    R(s, (40, 30, 40), 2, 19, 2, 3); R(s, (40, 30, 40), 16 * w - 4, 19, 2, 3)
    return s


def _armchair(color=(150, 60, 70)):
    s = new(16, 20)
    R(s, color, 1, 2, 14, 10)
    R(s, shade(color, 1.2), 2, 8, 12, 8)
    R(s, shade(color, 0.8), 0, 4, 3, 13); R(s, shade(color, 0.8), 13, 4, 3, 13)
    R(s, (40, 30, 30), 2, 17, 2, 3); R(s, (40, 30, 30), 12, 17, 2, 3)
    return s


def _coffee_table():
    s = new(32, 14)
    R(s, (60, 40, 34), 2, 2, 28, 6)
    R(s, (90, 64, 50), 2, 2, 28, 2)
    R(s, (50, 34, 28), 4, 8, 2, 6); R(s, (50, 34, 28), 26, 8, 2, 6)
    R(s, (240, 240, 240), 8, 1, 5, 2); R(s, (120, 40, 190), 20, 0, 3, 3)
    return s


def _counter(w, top=(232, 226, 236), front=(150, 102, 64)):
    s = new(16 * w, 22)
    R(s, front, 0, 6, 16 * w, 16)
    R(s, shade(front, 0.8), 0, 20, 16 * w, 2)
    for i in range(w):
        R(s, shade(front, 0.88), i * 16 + 3, 10, 10, 8)
    R(s, top, 0, 2, 16 * w, 5)
    R(s, shade(top, 1.08), 0, 2, 16 * w, 1)
    return s


def _stove():
    s = new(16, 24)
    R(s, (60, 60, 70), 0, 6, 16, 18)
    R(s, (30, 30, 36), 0, 4, 16, 4)
    for x in (3, 9):
        pygame.draw.circle(s, (90, 90, 100), (x + 2, 6), 2)
    R(s, (40, 40, 48), 2, 12, 12, 8)
    R(s, (255, 150, 60), 3, 18, 10, 1)
    R(s, (200, 200, 210), 3, 10, 10, 1)
    return s


def _fridge(w=1):
    W = 16 * w
    s = new(W, 32)
    R(s, (226, 230, 238), 1, 2, W - 2, 30)
    R(s, (200, 204, 214), 1, 13, W - 2, 1)
    R(s, (150, 154, 166), W - 5, 5, 1, 5); R(s, (150, 154, 166), W - 5, 16, 1, 8)
    if w > 1:
        R(s, (200, 204, 214), W // 2, 2, 1, 30)
        R(s, (170, 220, 250), 3, 4, W // 2 - 5, 8)
        R(s, (170, 220, 250), W // 2 + 2, 4, W // 2 - 5, 8)
    return s


def _plant(big=False):
    s = new(16, 32 if big else 28)
    off = 4 if big else 0
    R(s, (170, 96, 70), 4, 20 + off, 8, 8)
    R(s, (190, 112, 84), 3, 19 + off, 10, 2)
    for (x, y, rad, c) in [(8, 12, 6, (52, 132, 70)), (5, 9, 4, (64, 150, 80)), (11, 8, 4, (64, 150, 80)),
                           (8, 5, 3, (84, 172, 96))]:
        pygame.draw.circle(s, c, (x, y + off), rad)
    if big:
        pygame.draw.circle(s, (64, 150, 80), (8, 4), 4)
    return s


def _bookshelf(seed=0):
    s = new(32, 32)
    R(s, (96, 62, 40), 0, 0, 32, 32)
    for y in (2, 12, 22):
        R(s, (70, 44, 28), 2, y, 28, 8)
        x = 3
        rr = random.Random(y + seed * 7)
        while x < 28:
            w = rr.randint(2, 3)
            c = rr.choice([(170, 60, 70), (60, 100, 170), (200, 170, 70), (120, 60, 170), (70, 150, 110), (220, 220, 210)])
            h = rr.randint(5, 7)
            R(s, c, x, y + 8 - h, w, h)
            x += w + 1
    return s


def _desk(color=(70, 44, 40), with_pc=True, w=3):
    s = new(16 * w, 30)
    R(s, color, 0, 12, 16 * w, 18)
    R(s, shade(color, 1.3), 0, 12, 16 * w, 3)
    R(s, shade(color, 0.75), 3, 18, 16 * w - 6, 12)
    if with_pc:
        cx = 16 * w // 2 - 8 + (2 if w == 3 else 0)
        R(s, (30, 30, 40), cx, 1, 16, 11)
        R(s, (70, 150, 230), cx + 1, 2, 14, 8)
        R(s, (150, 210, 255), cx + 2, 3, 6, 1)
        R(s, (40, 40, 52), cx + 6, 11, 4, 2)
        R(s, (240, 240, 246), 3, 9, 7, 4)
        R(s, (120, 40, 190), 16 * w - 7, 8, 3, 5)
    return s


def _reception():
    s = new(48, 26)
    R(s, (240, 238, 246), 0, 6, 48, 20)
    R(s, (255, 255, 255), 0, 4, 48, 4)
    R(s, (120, 40, 190), 0, 14, 48, 3)
    R(s, (120, 40, 190), 20, 8, 3, 10); R(s, (120, 40, 190), 20, 16, 8, 2)
    R(s, (210, 206, 220), 0, 24, 48, 2)
    return s


def _station(state, color=(150, 150, 150), worked=False, progress=0.0):
    s = new(16, 28)
    if state == "locked":
        R(s, (120, 116, 130), 1, 12, 14, 16)
        R(s, (150, 146, 160), 0, 10, 16, 6)
        R(s, (100, 96, 110), 2, 18, 12, 1)
        R(s, (232, 196, 80), 3, 20, 10, 2)
        for x in (3, 7, 11):
            R(s, (40, 36, 44), x, 20, 2, 2)
        return s
    R(s, (172, 178, 192), 1, 14, 14, 14)
    R(s, (150, 156, 170), 1, 26, 14, 2)
    R(s, (228, 232, 240), 0, 11, 16, 4)
    R(s, (90, 96, 110), 3, 18, 10, 6)
    R(s, (60, 64, 76), 6, 8, 4, 4)
    if state == "empty":
        R(s, (60, 64, 76), 4, 1, 8, 8)
        R(s, (90, 96, 110), 5, 2, 6, 6)
        return s
    glow = color if worked else shade(color, 0.45)
    R(s, (36, 34, 46), 3, 0, 10, 9)
    R(s, glow, 4, 1, 8, 7)
    R(s, shade(glow, 1.25), 5, 2, 3, 2)
    bw = max(1, int(8 * progress))
    R(s, (40, 40, 52), 4, 20, 8, 2)
    R(s, (120, 240, 140) if state == "ready" else color, 4, 20, bw, 2)
    if state == "ready":
        R(s, (255, 230, 120), 7, 2, 2, 3); R(s, (255, 230, 120), 7, 6, 2, 1)
    return s


def _terminal():
    s = new(16, 30)
    R(s, (50, 46, 64), 3, 12, 10, 18)
    R(s, (36, 32, 48), 1, 2, 14, 12)
    R(s, (120, 40, 190), 2, 3, 12, 10)
    R(s, (200, 150, 255), 3, 4, 5, 1); R(s, (200, 150, 255), 3, 6, 8, 1); R(s, (200, 150, 255), 3, 8, 6, 1)
    R(s, (80, 76, 96), 4, 18, 8, 2)
    return s


def _shipbox(pier=False):
    s = new(32, 26)
    if pier:
        R(s, (120, 84, 54), 0, 8, 32, 18)
        R(s, (150, 106, 70), 0, 8, 32, 3)
        R(s, (90, 62, 40), 4, 14, 24, 1); R(s, (90, 62, 40), 4, 19, 24, 1)
        R(s, (40, 110, 170), 10, 2, 12, 6)
        return s
    R(s, (40, 36, 52), 0, 6, 32, 20)
    R(s, (60, 54, 76), 0, 6, 32, 3)
    R(s, (24, 20, 32), 4, 10, 24, 4)
    R(s, (184, 76, 255), 4, 18, 24, 2)
    R(s, (240, 220, 140), 13, 1, 6, 6)
    R(s, (200, 170, 90), 13, 3, 6, 1)
    return s


def _coffee():
    s = new(16, 28)
    R(s, (100, 70, 50), 0, 18, 16, 10)
    R(s, (60, 60, 70), 3, 4, 10, 14)
    R(s, (90, 90, 104), 3, 4, 10, 2)
    R(s, (30, 30, 36), 5, 10, 6, 2)
    R(s, (240, 240, 240), 6, 14, 4, 4)
    R(s, (255, 90, 90), 11, 7, 1, 1)
    return s


def _table(cloth=None):
    s = new(16, 20)
    if cloth:
        R(s, cloth, 1, 2, 14, 10)
        for x in range(1, 15, 4):
            for y in range(2, 12, 4):
                R(s, (250, 250, 250), x, y, 2, 2)
        R(s, shade(cloth, 0.8), 1, 10, 14, 3)
        R(s, (240, 200, 120), 7, 0, 2, 4)
        R(s, (90, 60, 40), 7, 13, 2, 6)
        return s
    pygame.draw.ellipse(s, (130, 86, 54), (1, 4, 14, 8))
    pygame.draw.ellipse(s, (154, 104, 68), (2, 4, 12, 6))
    R(s, (90, 60, 40), 7, 11, 2, 7)
    R(s, (90, 60, 40), 4, 18, 8, 2)
    R(s, (255, 255, 255), 6, 5, 3, 2)
    return s


def _dining():
    s = new(32, 24)
    R(s, (120, 80, 52), 0, 4, 32, 12)
    R(s, (146, 100, 66), 0, 4, 32, 3)
    R(s, (100, 66, 44), 2, 16, 2, 8); R(s, (100, 66, 44), 28, 16, 2, 8)
    R(s, (250, 250, 250), 6, 6, 5, 3); R(s, (250, 250, 250), 20, 6, 5, 3)
    R(s, (200, 60, 90), 14, 2, 4, 5)
    return s


def _chair(color=(120, 40, 60)):
    s = new(16, 18)
    R(s, color, 4, 2, 8, 9)
    R(s, shade(color, 1.18), 4, 9, 8, 3)
    R(s, (60, 40, 40), 4, 12, 1, 6); R(s, (60, 40, 40), 11, 12, 1, 6)
    return s


def _stool():
    s = new(16, 18)
    pygame.draw.ellipse(s, (170, 40, 50), (3, 4, 10, 5))
    R(s, (70, 70, 80), 7, 8, 2, 8)
    R(s, (70, 70, 80), 4, 16, 8, 2)
    return s


def _shelf_cafe():
    s = new(48, 30)
    R(s, (96, 62, 40), 0, 2, 48, 28)
    R(s, (70, 44, 28), 2, 4, 44, 10); R(s, (70, 44, 28), 2, 17, 44, 10)
    for i in range(7):
        R(s, (220, 210, 190), 4 + i * 6, 8, 4, 6)
        R(s, (120, 80, 50), 4 + i * 6, 8, 4, 2)
    for i in range(5):
        R(s, (200, 120, 60), 5 + i * 9, 21, 6, 6)
    return s


def _bottle_shelf():
    s = new(48, 32)
    R(s, (60, 40, 34), 0, 0, 48, 32)
    for y in (4, 18):
        R(s, (40, 26, 22), 2, y, 44, 12)
        rr = random.Random(y)
        for x in range(4, 44, 5):
            c = rr.choice([(60, 140, 70), (150, 40, 50), (200, 170, 70), (120, 160, 200)])
            R(s, c, x, y + 4, 3, 8)
            R(s, c, x + 1, y + 1, 1, 3)
    return s


def _wine_shelf():
    s = new(48, 32)
    R(s, (110, 70, 44), 0, 0, 48, 32)
    for y in range(3, 30, 6):
        for x in range(3, 45, 6):
            pygame.draw.circle(s, (70, 20, 34), (x + 2, y + 2), 2)
            P(s, (160, 60, 80), x + 1, y + 1)
    return s


def _oven():
    s = new(32, 36)
    pygame.draw.ellipse(s, (170, 90, 60), (0, 4, 32, 26))
    R(s, (170, 90, 60), 0, 18, 32, 18)
    for y in range(8, 34, 5):
        R(s, (150, 76, 50), 0, y, 32, 1)
    pygame.draw.ellipse(s, (40, 24, 20), (8, 16, 16, 12))
    R(s, (40, 24, 20), 8, 22, 16, 8)
    R(s, (255, 150, 60), 11, 25, 10, 3)
    R(s, (255, 220, 100), 14, 26, 4, 2)
    return s


def _produce(seed=0):
    s = new(32, 24)
    R(s, (140, 100, 64), 0, 10, 32, 14)
    R(s, (120, 84, 54), 0, 10, 32, 2)
    rr = random.Random(seed)
    for i in range(2):
        c = rr.choice([(230, 60, 50), (250, 160, 40), (120, 200, 80), (240, 220, 80), (150, 60, 160)])
        for k in range(10):
            pygame.draw.circle(s, c, (2 + i * 16 + rr.randrange(12), 6 + rr.randrange(5)), 2)
    return s


def _flowerstand():
    s = new(32, 28)
    R(s, (90, 140, 90), 0, 14, 32, 14)
    R(s, (70, 110, 70), 0, 14, 32, 2)
    rr = random.Random(5)
    for k in range(18):
        x, y = rr.randrange(2, 30), rr.randrange(2, 13)
        c = rr.choice([(255, 120, 170), (255, 210, 60), (220, 30, 60), (250, 250, 250), (200, 150, 255)])
        R(s, (60, 130, 60), x, y + 2, 1, 4)
        pygame.draw.circle(s, c, (x, y), 2)
    return s


def _desk_news():
    s = new(32, 28)
    R(s, (200, 200, 210), 0, 12, 32, 16)
    R(s, (230, 230, 236), 0, 12, 32, 3)
    R(s, (150, 150, 160), 2, 18, 28, 1)
    R(s, (30, 30, 40), 4, 2, 12, 9); R(s, (90, 160, 220), 5, 3, 10, 6)
    R(s, (240, 240, 246), 20, 8, 8, 5); R(s, (200, 60, 60), 21, 9, 6, 1)
    return s


def _printer():
    s = new(16, 24)
    R(s, (90, 90, 100), 1, 10, 14, 14)
    R(s, (210, 210, 218), 1, 6, 14, 6)
    R(s, (250, 250, 250), 4, 2, 8, 6)
    R(s, (60, 200, 90), 11, 14, 2, 1)
    return s


def _cooler():
    s = new(16, 30)
    R(s, (220, 224, 232), 3, 12, 10, 18)
    R(s, (150, 200, 240), 4, 0, 8, 12)
    R(s, (120, 180, 230), 4, 0, 8, 2)
    R(s, (80, 80, 90), 6, 18, 4, 2)
    return s


def _bathtub():
    s = new(48, 28)
    R(s, (240, 242, 248), 0, 6, 48, 22)
    R(s, (200, 206, 216), 0, 26, 48, 2)
    R(s, (170, 210, 236), 3, 8, 42, 8)
    R(s, (210, 230, 246), 6, 9, 10, 2)
    R(s, (190, 190, 200), 40, 2, 4, 6)
    return s


def _sink():
    s = new(16, 28)
    R(s, (240, 242, 248), 1, 12, 14, 16)
    R(s, (200, 206, 216), 3, 13, 10, 4)
    R(s, (190, 190, 200), 7, 9, 2, 4)
    R(s, (170, 210, 236), 3, 0, 10, 8)
    R(s, (120, 130, 150), 2, 0, 12, 1)
    return s


def _aquarium():
    s = new(48, 32)
    R(s, (40, 40, 52), 0, 22, 48, 10)
    R(s, (60, 140, 200), 1, 2, 46, 20)
    R(s, (100, 180, 230), 1, 2, 46, 3)
    R(s, (200, 180, 120), 1, 18, 46, 4)
    R(s, (60, 160, 80), 6, 10, 2, 8); R(s, (60, 160, 80), 38, 8, 2, 10)
    R(s, (30, 30, 40), 0, 1, 48, 1)
    return s


def _arcade():
    s = new(16, 36)
    R(s, (40, 20, 70), 1, 4, 14, 32)
    R(s, (120, 40, 190), 1, 4, 14, 3)
    R(s, (20, 20, 30), 3, 9, 10, 9)
    R(s, (90, 255, 120), 6, 12, 2, 2); R(s, (255, 200, 60), 9, 15, 2, 2)
    R(s, (60, 30, 90), 2, 20, 12, 4)
    R(s, (255, 60, 60), 4, 21, 2, 2); R(s, (60, 160, 255), 9, 21, 2, 2)
    R(s, (255, 230, 120), 3, 0, 10, 4)
    return s


def _pool():
    s = new(32, 32)
    R(s, (90, 56, 40), 0, 4, 32, 26)
    R(s, (40, 120, 70), 3, 7, 26, 20)
    for (x, y, c) in ((10, 12, (250, 250, 250)), (16, 16, (230, 60, 50)), (20, 13, (240, 200, 60)), (14, 20, (40, 40, 40))):
        pygame.draw.circle(s, c, (x, y), 2)
    R(s, (60, 40, 30), 2, 28, 3, 4); R(s, (60, 40, 30), 27, 28, 3, 4)
    return s


def _jukebox():
    s = new(16, 32)
    pygame.draw.ellipse(s, (180, 60, 60), (0, 0, 16, 14))
    R(s, (180, 60, 60), 0, 7, 16, 25)
    R(s, (255, 210, 120), 3, 4, 10, 10)
    R(s, (90, 40, 40), 3, 18, 10, 10)
    for y in (19, 22, 25):
        R(s, (255, 230, 160), 4, y, 8, 1)
    return s


def _window_big(night=False):
    s = new(32, 16)
    R(s, (60, 50, 80), 0, 1, 32, 13)
    c = (36, 44, 100) if night else (150, 200, 240)
    R(s, c, 1, 2, 30, 11)
    R(s, (60, 50, 80), 15, 2, 2, 11)
    sky = (80, 90, 140) if not night else (30, 30, 60)
    for x in (3, 8, 20, 26):
        R(s, shade(sky, 0.9), x, 7, 3, 6)
    R(s, (210, 236, 250), 3, 3, 3, 1)
    return s


def _window_decor(night=False):
    s = new(16, 16)
    R(s, (60, 50, 80), 1, 2, 14, 11)
    c = (40, 50, 110) if night else (150, 200, 240)
    R(s, c, 2, 3, 12, 9)
    R(s, (60, 50, 80), 7, 3, 1, 9)
    R(s, (200, 230, 250), 3, 4, 2, 1)
    return s


def _painting(c=(184, 76, 255)):
    s = new(16, 16)
    R(s, (200, 170, 80), 2, 2, 12, 10)
    R(s, (60, 40, 90), 3, 3, 10, 8)
    R(s, c, 5, 4, 2, 6); R(s, c, 5, 9, 6, 1)
    return s


def _poster(c=(230, 60, 60)):
    s = new(16, 16)
    R(s, (240, 236, 226), 3, 1, 10, 13)
    R(s, c, 4, 2, 8, 6)
    R(s, (40, 40, 40), 4, 9, 8, 1); R(s, (40, 40, 40), 4, 11, 6, 1)
    return s


def _menuboard():
    s = new(32, 16)
    R(s, (30, 32, 30), 1, 1, 30, 13)
    R(s, (120, 90, 60), 0, 0, 32, 1); R(s, (120, 90, 60), 0, 14, 32, 1)
    for y in (4, 7, 10):
        R(s, (230, 230, 220), 4, y, 14, 1); R(s, (240, 200, 120), 22, y, 5, 1)
    return s


def _neon(text_color=(255, 80, 140)):
    s = new(32, 16)
    R(s, (20, 14, 24), 0, 2, 32, 11)
    for i, x in enumerate(range(3, 29, 5)):
        R(s, text_color if i % 2 == 0 else (120, 220, 255), x, 5, 3, 5)
    return s


def _rug(w, h, base=(110, 50, 150), border=(200, 160, 240), logo=False):
    s = new(16 * w, 16 * h)
    R(s, border, 0, 0, 16 * w, 16 * h)
    R(s, base, 2, 2, 16 * w - 4, 16 * h - 4)
    R(s, shade(base, 1.2), 4, 4, 16 * w - 8, 1)
    R(s, shade(base, 1.2), 4, 16 * h - 5, 16 * w - 8, 1)
    if logo:
        cx, cy = 8 * w, 8 * h
        R(s, border, cx - 5, cy - 8, 3, 15)
        R(s, border, cx - 5, cy + 5, 11, 3)
    return s


def _sign_board():
    s = new(16, 24)
    R(s, (110, 76, 48), 7, 10, 2, 14)
    R(s, (230, 220, 190), 1, 2, 14, 9)
    R(s, (110, 76, 48), 1, 2, 14, 1)
    R(s, (40, 110, 170), 3, 5, 10, 1); R(s, (40, 110, 170), 3, 7, 7, 1)
    return s


OBJECT_BUILDERS = {
    "tree": _tree, "tree2": lambda: _tree(1), "tree3": lambda: _tree(2), "palm": _palm, "hedge": _hedge,
    "bush": _bush, "bush2": lambda: _bush((255, 230, 110)), "bush3": lambda: _bush((190, 160, 255)),
    "planter": _planter, "lamp": _lamp, "bench": _bench, "statue": _statue, "hydrant": _hydrant,
    "busstop": _busstop, "umbrella": _umbrella, "umbrella2": lambda: _umbrella((40, 120, 200)),
    "lifeguard": _lifeguard, "boat": _boat, "kiosk": _kiosk, "signboard": _sign_board,
    "bed": _bed, "bed2": lambda: _bed(3), "nightstand": _nightstand, "wardrobe": _wardrobe,
    "tv": _tv, "tv_big": lambda: _tv(True), "tv_wall": _tv_wall,
    "sofa": lambda: _sofa(3), "sofa_grey": lambda: _sofa(3, (90, 96, 110)), "armchair": _armchair,
    "coffee_table": _coffee_table,
    "kitchen": lambda: _counter(3, (236, 236, 242), (200, 200, 214)),
    "kitchen2": lambda: _counter(2, (236, 236, 242), (200, 200, 214)),
    "island": lambda: _counter(3, (240, 240, 246), (80, 60, 90)),
    "stove": _stove, "fridge": _fridge, "fridge2": lambda: _fridge(2),
    "plant": _plant, "plant_big": lambda: _plant(True),
    "bookshelf": _bookshelf, "bookshelf2": lambda: _bookshelf(1), "bookshelf3": lambda: _bookshelf(2),
    "ceo_desk": lambda: _desk((58, 34, 44)), "desk": lambda: _desk((120, 84, 56)),
    "desk_home": lambda: _desk((70, 50, 80)), "desk_editor": lambda: _desk((50, 50, 60)),
    "desk_news": _desk_news, "reception": _reception, "terminal": _terminal,
    "shipbox": _shipbox, "shipbox_pier": lambda: _shipbox(True), "coffee": _coffee,
    "table": _table, "table_it": lambda: _table((200, 40, 50)), "dining": _dining,
    "chair": _chair, "chair_blue": lambda: _chair((50, 70, 120)), "stool": _stool,
    "cafe_counter": lambda: _counter(6, (232, 216, 190), (110, 70, 44)),
    "shop_counter": lambda: _counter(4, (236, 230, 216), (90, 120, 90)),
    "counter_it": lambda: _counter(6, (240, 236, 228), (150, 60, 50)),
    "bar_counter": lambda: _counter(6, (120, 80, 50), (60, 36, 30)),
    "cafe_shelf": _shelf_cafe, "bottle_shelf": _bottle_shelf, "wine_shelf": _wine_shelf, "oven": _oven,
    "produce": _produce, "produce2": lambda: _produce(3), "flowerstand": _flowerstand,
    "printer": _printer, "cooler": _cooler, "bathtub": _bathtub, "sink": _sink, "aquarium": _aquarium,
    "arcade": _arcade, "pool": _pool, "jukebox": _jukebox,
    "rug": lambda: _rug(4, 3), "rug_big": lambda: _rug(5, 3, (70, 60, 110), (210, 200, 240)),
    "logo_rug": lambda: _rug(6, 3, (90, 30, 140), (220, 190, 255), True),
    "rug_red": lambda: _rug(3, 2, (150, 50, 60), (230, 190, 120)),
    "rug_bed": lambda: _rug(3, 2, (60, 90, 130), (200, 210, 230)),
    "rug_green": lambda: _rug(4, 3, (60, 110, 80), (220, 210, 170)),
    "catco_rug": lambda: _rug(6, 2, (40, 60, 110), (240, 240, 250)),
    "window": _window_decor, "window_big": _window_big, "painting": _painting,
    "painting2": lambda: _painting((90, 200, 255)), "poster": _poster, "poster2": lambda: _poster((60, 120, 220)),
    "menuboard": _menuboard, "neon": _neon,
}


def object_sprite(kind, night=False):
    if kind in ("window", "window_big") and night:
        fn = _window_decor if kind == "window" else _window_big
        return cached(("obj", kind, "night"), lambda: up(fn(True)))
    return cached(("obj", kind), lambda: up(OBJECT_BUILDERS[kind]()))


def station_sprite(state, color=(150, 150, 150), worked=False, progress=0.0):
    key = ("station", state, tuple(color), worked, round(progress, 2))
    return cached(key, lambda: up(_station(state, color, worked, progress)))


# ---------------------------------------------------------------------------
# Carros
# ---------------------------------------------------------------------------

def car_sprite(color, facing_right=True):
    def make():
        s = new(32, 18)
        R(s, (20, 20, 26), 4, 13, 6, 5); R(s, (20, 20, 26), 22, 13, 6, 5)
        R(s, color, 1, 7, 30, 8)
        R(s, shade(color, 1.2), 1, 7, 30, 2)
        R(s, shade(color, 0.85), 8, 1, 15, 7)
        R(s, (150, 200, 230), 10, 2, 5, 5); R(s, (150, 200, 230), 17, 2, 5, 5)
        R(s, (255, 240, 170), 29, 9, 2, 2)
        R(s, (220, 40, 40), 1, 9, 1, 2)
        R(s, (40, 40, 50), 0, 13, 32, 1)
        if not facing_right:
            s = pygame.transform.flip(s, True, False)
        return up(s)
    return cached(("car", tuple(color), facing_right), make)


# ---------------------------------------------------------------------------
# Prédios da cidade
# ---------------------------------------------------------------------------

def _windows(s, x0, y0, x1, y1, step_x, step_y, ww, wh, glass, frame, night, r, lit_chance=0.55):
    for y in range(y0, y1, step_y):
        for x in range(x0, x1, step_x):
            lit = night and r.random() < lit_chance
            R(s, frame, x - 1, y - 1, ww + 2, wh + 2)
            c = (252, 222, 136) if lit else glass
            R(s, c, x, y, ww, wh)
            if not lit:
                R(s, shade(glass, 1.25), x, y, max(1, ww // 3), wh)
                P(s, shade(glass, 1.5), x, y)


def building_sprite(style, w, h, extra, night=False):
    def make():
        W, H = w * TS, (h + extra) * TS
        s = new(W, H)
        r = random.Random(style)
        if style == "tower":
            body, frame, glass = (52, 38, 84), (32, 24, 54), (86, 96, 172)
            R(s, body, 0, 8, W, H - 8)
            R(s, shade(body, 1.2), 0, 8, 3, H - 8)
            R(s, shade(body, 0.75), W - 3, 8, 3, H - 8)
            R(s, frame, 0, 8, W, 3)
            R(s, (120, 40, 190), W // 2 - 12, 0, 24, 9)
            R(s, (184, 76, 255), W // 2 - 1, 0, 2, 4)
            _windows(s, 5, 15, W - 6, H - 52, 6, 7, 4, 5, glass, frame, night, r)
            R(s, (22, 16, 38), 6, H - 48, W - 12, 13)
            R(s, (30, 24, 46), W // 2 - 16, H - 26, 32, 26)
            R(s, (140, 180, 232), W // 2 - 14, H - 23, 28, 23)
            R(s, (100, 130, 180), W // 2 - 1, H - 23, 2, 23)
            R(s, (120, 40, 190), W // 2 - 20, H - 30, 40, 4)
            R(s, (90, 86, 100), W // 2 - 18, H - 3, 36, 3)
        elif style == "catco":
            body, frame, glass = (30, 60, 104), (20, 36, 66), (120, 170, 220)
            R(s, body, 0, 10, W, H - 10)
            R(s, shade(body, 1.25), 0, 10, 3, H - 10)
            R(s, frame, 0, 10, W, 3)
            R(s, (220, 230, 240), 4, 2, W - 8, 9)
            _windows(s, 5, 18, W - 6, H - 46, 6, 6, 4, 4, glass, frame, night, r, 0.5)
            R(s, (240, 244, 250), 6, H - 44, W - 12, 12)
            R(s, (20, 36, 66), W // 2 - 14, H - 24, 28, 24)
            R(s, (160, 200, 236), W // 2 - 12, H - 21, 24, 21)
            R(s, (240, 244, 250), W // 2 - 18, H - 28, 36, 3)
        elif style == "home":
            wall = (178, 122, 98)
            R(s, wall, 0, 10, W, H - 10)
            R(s, (92, 66, 82), 0, 5, W, 7)
            R(s, (72, 52, 66), 0, 5, W, 2)
            R(s, (200, 200, 210), 6, 0, 10, 6); R(s, (120, 120, 130), 8, 2, 6, 3)
            for y in range(12, H, 4):
                R(s, shade(wall, 0.94), 0, y, W, 1)
            for y in range(16, H - 26, 15):
                for x in range(6, W - 10, 14):
                    lit = night and r.random() < 0.6
                    R(s, (60, 46, 50), x - 1, y - 1, 10, 11)
                    R(s, (252, 222, 136) if lit else (150, 196, 228), x, y, 8, 9)
                    R(s, (60, 46, 50), x + 3, y, 1, 9)
                    R(s, (90, 70, 74), x - 2, y + 10, 12, 2)
            dx = (W // 2) - 9
            R(s, (130, 84, 70), dx - 2, H - 24, 22, 24)
            R(s, (90, 56, 40), dx, H - 22, 18, 22)
            R(s, (210, 180, 90), dx + 14, H - 12, 2, 2)
            R(s, (120, 40, 190), dx - 5, H - 27, 28, 3)
        elif style == "cafe":
            wall = (234, 222, 198)
            R(s, wall, 0, 12, W, H - 12)
            R(s, (112, 72, 46), 0, 8, W, 6)
            for i in range(0, W, 8):
                R(s, (120, 40, 190) if (i // 8) % 2 == 0 else (250, 246, 255), i, H - 42, 8, 10)
            R(s, shade(wall, 0.85), 0, H - 32, W, 2)
            R(s, (62, 46, 42), 6, H - 28, 32, 20)
            R(s, (252, 222, 150) if night else (172, 212, 238), 7, H - 27, 30, 18)
            R(s, (62, 46, 42), 22, H - 27, 1, 18)
            dx = W // 2 + 6
            R(s, (90, 56, 40), dx, H - 24, 14, 24)
            R(s, (170, 210, 236), dx + 3, H - 21, 8, 9)
            R(s, (62, 46, 42), 0, H - 2, W, 2)
        elif style == "bank":
            wall = (214, 208, 196)
            R(s, wall, 0, 10, W, H - 10)
            pygame.draw.polygon(s, (190, 184, 172), [(0, 12), (W // 2, 0), (W, 12)])
            R(s, (170, 164, 152), 0, 12, W, 3)
            for x in range(6, W - 4, 12):
                R(s, (240, 236, 228), x, 18, 5, H - 24)
                R(s, (190, 184, 172), x + 4, 18, 1, H - 24)
            R(s, (160, 154, 142), 0, H - 6, W, 6)
            R(s, (120, 100, 60), W // 2 - 6, H - 22, 12, 16)
        elif style == "hospital":
            # Conti Moretti Hospitais: papel, verde profundo e cobre
            paper, green, green2, copper = (246, 243, 236), (18, 63, 53), (29, 89, 74), (183, 123, 101)
            R(s, paper, 0, 14, W, H - 14)
            R(s, shade(paper, 0.9), W - 4, 14, 4, H - 14)
            R(s, green, 0, 2, W, 13)
            R(s, shade(green, 1.3), 0, 2, W, 1)
            R(s, copper, 0, 15, W, 2)
            # torre central de vidro verde
            R(s, green2, W // 2 - 26, 20, 52, H - 56)
            for yy in range(23, H - 70, 7):
                for xx in range(W // 2 - 23, W // 2 + 22, 7):
                    lit = night and r.random() < 0.55
                    R(s, (252, 226, 160) if lit else (120, 178, 160), xx, yy, 5, 5)
            # alas laterais
            _windows(s, 4, 22, W // 2 - 32, H - 40, 8, 9, 6, 6, (176, 210, 226), (210, 200, 190), night, r, 0.6)
            _windows(s, W // 2 + 32, 22, W - 6, H - 40, 8, 9, 6, 6, (176, 210, 226), (210, 200, 190), night, r, 0.6)
            # medalhão do logo na torre
            pygame.draw.circle(s, paper, (W // 2, H - 56), 11)
            pygame.draw.circle(s, copper, (W // 2, H - 56), 11, 1)
            # marquise e entrada
            R(s, green, 4, H - 40, W - 8, 12)
            R(s, shade(green, 1.3), 4, H - 40, W - 8, 1)
            R(s, copper, 4, H - 28, W - 8, 2)
            R(s, (30, 46, 40), W // 2 - 16, H - 24, 32, 24)
            R(s, (170, 214, 210) if not night else (250, 230, 170), W // 2 - 14, H - 22, 13, 22)
            R(s, (170, 214, 210) if not night else (250, 230, 170), W // 2 + 1, H - 22, 13, 22)
            for x in (10, W - 22):
                R(s, (90, 150, 90), x, H - 14, 12, 12)
                R(s, (120, 180, 110), x + 2, H - 16, 8, 6)
        elif style == "books":
            wall = (150, 70, 56)
            R(s, wall, 0, 10, W, H - 10)
            for y in range(12, H, 3):
                for x in range((y % 6) * 2, W, 8):
                    R(s, shade(wall, 0.86), x, y, 1, 3)
                R(s, shade(wall, 0.9), 0, y, W, 1)
            R(s, (60, 40, 36), 0, 6, W, 6)
            _windows(s, 6, 18, W - 8, H - 46, 12, 12, 8, 8, (172, 212, 238), (60, 40, 36), night, r)
            for i in range(0, W, 8):
                R(s, (40, 110, 80) if (i // 8) % 2 == 0 else (240, 230, 200), i, H - 40, 8, 9)
            R(s, (50, 36, 30), 6, H - 28, 30, 20)
            R(s, (252, 222, 150) if night else (172, 212, 238), 7, H - 27, 28, 18)
            for x in range(9, 34, 4):
                R(s, r.choice([(200, 60, 60), (60, 100, 170), (230, 200, 80)]), x, H - 14, 3, 5)
            dx = W - 22
            R(s, (60, 40, 30), dx, H - 24, 14, 24)
            R(s, (170, 210, 236), dx + 3, H - 21, 8, 9)
        elif style == "market":
            wall = (244, 230, 196)
            R(s, wall, 0, 10, W, H - 10)
            R(s, (70, 120, 70), 0, 6, W, 6)
            for i in range(0, W, 8):
                R(s, (250, 196, 60) if (i // 8) % 2 == 0 else (250, 250, 240), i, H - 40, 8, 10)
            R(s, (90, 70, 50), 4, H - 28, W - 8, 20)
            R(s, (252, 222, 150) if night else (180, 216, 236), 5, H - 27, W - 10, 10)
            for x in range(6, W - 8, 6):
                c = r.choice([(230, 60, 50), (250, 160, 40), (120, 200, 80), (240, 220, 80)])
                R(s, (140, 100, 64), x, H - 12, 5, 4)
                R(s, c, x + 1, H - 14, 3, 2)
            dx = W // 2 - 7
            R(s, (60, 46, 36), dx, H - 26, 14, 26)
            R(s, (170, 210, 236), dx + 2, H - 24, 10, 12)
        elif style == "trattoria":
            wall = (236, 200, 160)
            R(s, wall, 0, 10, W, H - 10)
            R(s, (180, 90, 60), 0, 4, W, 8)
            for x in range(0, W, 4):
                R(s, (160, 76, 50), x, 4, 2, 8)
            for i in range(0, W, 6):
                R(s, [(40, 150, 70), (250, 250, 250), (210, 40, 50)][(i // 6) % 3], i, H - 40, 6, 9)
            _windows(s, 6, 16, W - 8, H - 46, 14, 12, 8, 9, (172, 212, 238), (120, 70, 50), night, r)
            R(s, (100, 60, 40), 6, H - 28, 34, 20)
            R(s, (252, 214, 140) if night else (190, 220, 238), 7, H - 27, 32, 18)
            R(s, (200, 40, 50), 7, H - 27, 32, 2)
            dx = W - 26
            R(s, (100, 60, 40), dx, H - 26, 16, 26)
            R(s, (90, 50, 30), dx + 2, H - 24, 12, 24)
            R(s, (60, 140, 60), 2, H - 8, 4, 8); R(s, (60, 140, 60), W - 6, H - 8, 4, 8)
        elif style == "bar":
            wall = (70, 50, 52)
            R(s, wall, 0, 10, W, H - 10)
            for y in range(12, H, 3):
                for x in range((y % 6) * 2, W, 8):
                    R(s, shade(wall, 0.8), x, y, 1, 3)
            R(s, (30, 22, 26), 0, 6, W, 6)
            R(s, (24, 16, 20), 6, H - 44, W - 12, 12)
            R(s, (40, 30, 30), 6, H - 28, 30, 18)
            R(s, (255, 190, 110) if night else (120, 140, 160), 7, H - 27, 28, 16)
            dx = W - 22
            R(s, (30, 20, 20), dx, H - 26, 14, 26)
            R(s, (120, 40, 50), dx + 2, H - 24, 10, 24)
        elif style == "cinema":
            wall = (60, 40, 90)
            R(s, wall, 0, 10, W, H - 10)
            R(s, (40, 26, 60), 0, 6, W, 6)
            for x in range(4, W - 4, 10):
                R(s, shade(wall, 1.18), x, 14, 6, H - 72)
                R(s, shade(wall, 0.85), x + 5, 14, 1, H - 72)
            for x in (8, W - 20):
                R(s, (90, 90, 100), x, 1, 12, 6)
            R(s, (240, 220, 140), 4, H - 52, W - 8, 16)
            R(s, (30, 20, 40), 6, H - 50, W - 12, 12)
            for x in range(6, W - 6, 4):
                R(s, (255, 230, 140) if (x // 4) % 2 == 0 or night else (200, 180, 100), x, H - 54, 2, 2)
            R(s, (40, 26, 60), W // 2 - 16, H - 28, 32, 28)
            R(s, (170, 140, 210), W // 2 - 14, H - 26, 12, 26); R(s, (170, 140, 210), W // 2 + 2, H - 26, 12, 26)
            for x in (6, W - 20):
                R(s, (240, 236, 226), x, H - 30, 14, 20); R(s, (200, 60, 60), x + 2, H - 28, 10, 10)
        elif style == "apartments":
            wall = (190, 176, 150)
            R(s, wall, 0, 8, W, H - 8)
            R(s, (130, 116, 100), 0, 8, W, 3)
            for y in range(16, H - 24, 14):
                for x in range(5, W - 9, 12):
                    lit = night and r.random() < 0.5
                    R(s, (90, 80, 70), x - 1, y - 1, 9, 10)
                    R(s, (252, 222, 136) if lit else (160, 200, 226), x, y, 7, 8)
                    R(s, (120, 110, 100), x - 2, y + 9, 11, 2)
                    if r.random() < 0.4:
                        R(s, (80, 150, 80), x, y + 7, 7, 2)
            R(s, (90, 70, 50), W // 2 - 7, H - 22, 14, 22)
        return up(s)
    return cached(("bld", style, w, h, extra, night), make)


# ---------------------------------------------------------------------------
# Personagens (16x32)
# ---------------------------------------------------------------------------

# H cabelo h brilho | S pele s sombra N pescoço | W brilho do olho I íris L cílio | B bochecha M boca
# C roupa c sombra A detalhe | P calça p sombra | O sapato | K boné k aba
FRONT = [
    "................",
    "................",
    "......HHHH......",
    "....HHHhhHHH....",
    "...HHHhhHHHHH...",
    "...HHHHHHHHHH...",
    "...HHSSHHHSSH...",
    "...HSSSSSSSSH...",
    "...HLLSSSSLLH...",
    "...HSWISSWISH...",
    "...HSIISSIISH...",
    "...HSBSSSSBSH...",
    "....SSSMMSSS....",
    ".....sSSSSs.....",
    "......NNNN......",
    ".....CCAACc.....",
    "....CCCAACCc....",
    "...CCCCAACCcc...",
    "...CCCCCCCCcc...",
    "...CCCCCCCCcc...",
    "...SCCCCCCCcS...",
    "...S.CCCCCc.S...",
    ".....PPPPPp.....",
]
BACK = [
    "................",
    "................",
    "......HHHH......",
    "....HHHhhHHH....",
    "...HHHhhHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "....HHHHHHHH....",
    ".....HHHHHH.....",
    "......NNNN......",
    ".....CCCCCc.....",
    "....CCCCCCCc....",
    "...CCCCCCCCcc...",
    "...CCCCCCCCcc...",
    "...CCCCCCCCcc...",
    "...SCCCCCCCcS...",
    "...S.CCCCCc.S...",
    ".....PPPPPp.....",
]
SIDE = [
    "................",
    "................",
    "......HHHHH.....",
    ".....HHHhhHH....",
    "....HHHhhHHHH...",
    "....HHHHHHHHHH..",
    "....HHHHHHHSSH..",
    "....HHHHHSSSSS..",
    "....HHHHSSSLLS..",
    "....HHHHSSSWIS..",
    "....HHHHSSSIIS..",
    "....HHHHSSBSSS..",
    ".....HHHSSSSM...",
    "......HHsSSS....",
    ".......NNN......",
    "......CCAc......",
    ".....CCCCCc.....",
    ".....CCCCCc.....",
    ".....CCSSCc.....",
    ".....CCSSCc.....",
    ".....CCCSCc.....",
    "......CCCc......",
    "......PPPp......",
]
LEGS_FRONT = {
    0: [".....PPpPPp....."] * 6 + [".....OOOOOO.....", "................", "................"],
    1: [".....PPpPPp....."] * 5 + [".....OOOPPp.....", "........OOO.....", "................", "................"],
    2: [".....PPpPPp....."] * 5 + [".....PPpOOO.....", ".....OOO........", "................", "................"],
}
LEGS_SIDE = {
    0: ["......PPPp......"] * 6 + ["......OOOOO.....", "................", "................"],
    1: ["......PPPp......", ".....PPp.Pp.....", ".....PP...Pp....", "....PPp...PPp...",
        "....PP.....Pp...", "....PP.....PP...", "...OOO.....OOO..", "................", "................"],
}


def _apply_style(rows, style, view):
    rows = [list(r) for r in rows]
    if style == "long":
        if view == "front":
            for y in range(12, 21):
                rows[y][3] = "H" if rows[y][3] in ".C" else rows[y][3]
                rows[y][12] = "H" if rows[y][12] in ".c" else rows[y][12]
            for y in range(12, 17):
                rows[y][2] = "H"; rows[y][13] = "H"
        elif view == "back":
            for y in range(12, 20):
                for x in range(4, 12):
                    rows[y][x] = "H"
            for y in range(12, 18):
                rows[y][3] = "H"; rows[y][12] = "H"
            rows[19][4] = "C"; rows[19][11] = "c"
        else:
            for y in range(12, 19):
                for x in (4, 5, 6):
                    rows[y][x] = "H"
    elif style in ("short", "cap"):
        if view == "front":
            rows[12] = list("....sSSMMSSs....")
            for y in (6, 7, 8, 9, 10, 11):
                rows[y][3] = "H" if y < 10 else "s"
                rows[y][12] = "H" if y < 10 else "s"
        elif view == "side":
            rows[12] = list("......HSSSSM....")
            rows[13] = list(".......sSSS.....")
        elif view == "back":
            rows[12] = list(".....HHHHHH.....")
            rows[13] = list("......sNNs......")
    elif style == "bun":
        if view in ("front", "back"):
            rows[0] = list("......HHHH......")
            rows[1] = list(".....HHhhHH.....")
            if view == "front":
                rows[12] = list("....sSSMMSSs....")
        else:
            rows[1] = list("...HHH..........")
            rows[2] = list("..HHhHHHHHH.....")
            rows[12] = list("......HSSSSM....")
    elif style == "wavy":
        if view == "front":
            for y in range(12, 22):
                for x in (2, 3, 12, 13):
                    if y < 20 or x in (3, 12):
                        rows[y][x] = "H" if rows[y][x] in ".Cc" else rows[y][x]
        elif view == "back":
            for y in range(12, 21):
                for x in range(3, 13):
                    rows[y][x] = "H"
        else:
            for y in range(12, 20):
                for x in (3, 4, 5, 6):
                    rows[y][x] = "H"
    if style == "cap":
        if view == "side":
            rows[2] = list("......KKKKK.....")
            rows[3] = list(".....KKKKKKK....")
            rows[4] = list("....KKKKKKKKkkk.")
        else:
            rows[2] = list("......KKKK......")
            rows[3] = list("....KKKKKKKK....")
            rows[4] = list("...kkkkkkkkkk...")
    return rows


def _render(rows, pal):
    W, H = 16, 32
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for y, row in enumerate(rows[:H]):
        for x, ch in enumerate(row):
            if ch in pal:
                s.set_at((x, y), pal[ch])
    out = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(H):
        for x in range(W):
            if s.get_at((x, y)).a:
                continue
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and s.get_at((nx, ny)).a:
                    out.set_at((x, y), (*mix(shade(s.get_at((nx, ny)), 0.4), (40, 20, 50), 0.35), 255))
                    break
    out.blit(s, (0, 0))
    return out


def _palette(look):
    hair, skin, cloth = look["hair"], look["skin"], look["cloth"]
    eyes = look.get("eyes", (70, 46, 40))
    return {"H": hair, "h": mix(hair, (255, 255, 255), 0.4 if sum(hair) > 200 else 0.28), "S": skin,
            "s": shade(skin, 0.87), "N": shade(skin, 0.8), "W": (255, 255, 255), "I": eyes,
            "L": mix(hair, (30, 16, 30), 0.6), "B": mix(skin, (255, 120, 140), 0.38),
            "M": mix(skin, (180, 60, 80), 0.5), "C": cloth, "c": shade(cloth, 0.78), "A": look["accent"],
            "P": look["pants"], "p": shade(look["pants"], 0.74), "O": look["shoes"],
            "K": look["accent"], "k": shade(look["accent"], 0.72)}


def _frames(look, blink=False):
    pal = _palette(look)
    style = look.get("style", "short")
    out = {}
    for d, base, legs, seq, view in (("down", FRONT, LEGS_FRONT, [0, 1, 0, 2], "front"),
                                      ("up", BACK, LEGS_FRONT, [0, 2, 0, 1], "back"),
                                      ("right", SIDE, LEGS_SIDE, [0, 1, 0, 1], "side")):
        body = _apply_style(base, style, view)
        for i, leg in enumerate(seq):
            rows = [r[:] for r in body] + [list(r) for r in legs[leg]]
            if blink and view != "back":
                for y in (8, 9, 10):
                    rows[y] = [("L" if y == 10 else "S") if c in "WIL" else c for c in rows[y]]
            img = up(_render(rows, pal))
            out[(d, i)] = img
            if d == "right":
                out[("left", i)] = pygame.transform.flip(img, True, False)
    return out


def character_frames(look):
    """dict {(direção, frame): Surface}; piscadas em {("blink", direção): Surface}."""
    key = ("char",) + tuple(sorted((k, tuple(v) if isinstance(v, tuple) else v) for k, v in look.items()))

    def make():
        fr = _frames(look)
        bl = _frames(look, blink=True)
        for d in ("down", "left", "right", "up"):
            fr[("blink", d)] = bl[(d, 0)]
        return fr
    return cached(key, make)


# ---------------------------------------------------------------------------
# Ícones de itens (16x16)
# ---------------------------------------------------------------------------

def _icon(kind, color):
    s = new(16, 16)
    c = color
    d = shade(c, 0.7)
    if kind == "folder":
        R(s, d, 2, 3, 6, 2)
        R(s, c, 1, 4, 14, 10)
        R(s, shade(c, 1.2), 1, 4, 14, 2)
        R(s, (250, 250, 255), 4, 7, 8, 1); R(s, (250, 250, 255), 4, 9, 6, 1)
    elif kind == "doc":
        R(s, (240, 240, 248), 3, 1, 10, 14)
        R(s, (200, 200, 214), 3, 14, 10, 1)
        for y in (4, 6, 8):
            R(s, (140, 140, 160), 5, y, 6, 1)
        R(s, c, 5, 10, 2, 3); R(s, c, 8, 11, 2, 2); R(s, shade(c, 0.8), 11, 9, 1, 4)
    elif kind == "paper":
        R(s, (200, 200, 190), 2, 3, 12, 10)
        R(s, (120, 120, 130), 4, 5, 8, 2)
        R(s, (150, 150, 160), 4, 8, 8, 1); R(s, (150, 150, 160), 4, 10, 6, 1)
        R(s, (120, 170, 220), 2, 11, 12, 2)
    elif kind == "disk":
        R(s, c, 2, 2, 12, 12)
        R(s, (240, 240, 248), 4, 2, 8, 5)
        R(s, d, 5, 10, 6, 4)
    elif kind == "dna":
        R(s, (220, 236, 240), 6, 1, 4, 14)
        R(s, c, 6, 7, 4, 7)
        R(s, (250, 250, 255), 7, 2, 1, 4)
        R(s, (120, 120, 140), 5, 1, 6, 1)
    elif kind == "chip":
        R(s, (40, 36, 52), 3, 3, 10, 10)
        R(s, c, 5, 5, 6, 6)
        for i in (4, 7, 10):
            R(s, (200, 200, 210), i, 1, 1, 2); R(s, (200, 200, 210), i, 13, 1, 2)
            R(s, (200, 200, 210), 1, i, 2, 1); R(s, (200, 200, 210), 13, i, 2, 1)
    elif kind == "shield":
        pygame.draw.polygon(s, c, [(2, 2), (14, 2), (14, 8), (8, 14), (2, 8)])
        pygame.draw.polygon(s, shade(c, 1.2), [(4, 4), (8, 4), (8, 11), (4, 7)])
    elif kind == "robot":
        R(s, (180, 184, 196), 4, 2, 8, 6)
        R(s, c, 5, 4, 2, 2); R(s, c, 9, 4, 2, 2)
        R(s, (150, 154, 166), 3, 8, 10, 6)
        R(s, c, 6, 10, 4, 2)
    elif kind == "satellite":
        R(s, c, 1, 6, 4, 4); R(s, c, 11, 6, 4, 4)
        R(s, (200, 200, 214), 5, 7, 6, 2)
        R(s, (230, 230, 240), 6, 4, 4, 8)
        R(s, (255, 230, 120), 7, 2, 2, 2)
    elif kind == "orb":
        pygame.draw.circle(s, d, (8, 8), 7)
        pygame.draw.circle(s, c, (8, 8), 5)
        pygame.draw.circle(s, (255, 230, 250), (6, 6), 2)
    elif kind == "fish":
        pygame.draw.ellipse(s, c, (2, 5, 10, 7))
        pygame.draw.polygon(s, d, [(11, 8), (15, 4), (15, 12)])
        R(s, shade(c, 1.25), 4, 6, 5, 1)
        P(s, (20, 20, 30), 4, 7)
        R(s, d, 6, 11, 3, 1)
    elif kind == "can":
        R(s, (170, 170, 180), 4, 3, 8, 11)
        R(s, (200, 60, 60), 4, 6, 8, 4)
        R(s, (120, 120, 130), 4, 3, 8, 1); R(s, (120, 120, 130), 5, 12, 6, 2)
    elif kind == "rod":
        for i in range(12):
            P(s, c, 2 + i, 14 - i); P(s, shade(c, 1.3), 3 + i, 14 - i)
        R(s, (60, 60, 70), 3, 11, 3, 3)
        R(s, (230, 230, 240), 14, 2, 1, 9)
        R(s, (240, 60, 60), 13, 10, 3, 2)
    elif kind == "bait":
        R(s, (120, 90, 60), 3, 6, 10, 8)
        R(s, (150, 112, 76), 3, 6, 10, 2)
        for x in (5, 8, 11):
            R(s, (210, 120, 110), x, 4, 2, 4)
    elif kind == "pendant":
        pygame.draw.circle(s, (230, 200, 120), (8, 6), 6, 1)
        pygame.draw.polygon(s, c, [(8, 8), (11, 11), (8, 15), (5, 11)])
        P(s, (250, 220, 255), 7, 10)
    elif kind == "cup":
        R(s, (240, 240, 244), 3, 6, 8, 8)
        R(s, (240, 240, 244), 11, 8, 2, 3)
        R(s, c, 4, 6, 6, 2)
        R(s, (200, 200, 210), 2, 14, 12, 1)
        R(s, (220, 220, 230), 5, 2, 1, 2); R(s, (220, 220, 230), 8, 1, 1, 3)
    elif kind == "soda":
        R(s, (230, 240, 250), 5, 3, 6, 11)
        R(s, c, 5, 7, 6, 6)
        R(s, (250, 250, 250), 9, 1, 1, 4)
    elif kind == "drink":
        pygame.draw.polygon(s, (230, 240, 250), [(3, 3), (13, 3), (8, 9)])
        pygame.draw.polygon(s, c, [(5, 4), (11, 4), (8, 8)])
        R(s, (230, 240, 250), 7, 9, 2, 5); R(s, (230, 240, 250), 5, 14, 6, 1)
        R(s, (120, 220, 90), 11, 2, 3, 2)
    elif kind == "sandwich":
        R(s, (230, 190, 110), 2, 4, 12, 3)
        R(s, (110, 190, 90), 2, 7, 12, 2)
        R(s, (230, 110, 90), 3, 9, 10, 1)
        R(s, (230, 190, 110), 2, 10, 12, 3)
    elif kind == "croissant":
        pygame.draw.ellipse(s, c, (1, 5, 14, 8))
        for x in (4, 8, 11):
            R(s, d, x, 6, 1, 6)
    elif kind == "donut":
        pygame.draw.circle(s, (210, 160, 100), (8, 8), 7)
        pygame.draw.circle(s, c, (8, 7), 6)
        pygame.draw.circle(s, (0, 0, 0, 0), (8, 8), 2)
        for (x, y, cc) in ((5, 5, (255, 255, 255)), (10, 4, (120, 200, 255)), (11, 9, (255, 230, 120))):
            P(s, cc, x, y)
    elif kind == "pizza":
        pygame.draw.polygon(s, (230, 180, 100), [(8, 14), (1, 2), (15, 2)])
        pygame.draw.polygon(s, (240, 210, 120), [(8, 12), (3, 4), (13, 4)])
        for (x, y) in ((6, 5), (10, 6), (8, 9)):
            pygame.draw.circle(s, c, (x, y), 1)
    elif kind in ("lasagna", "cake"):
        R(s, (250, 250, 250), 1, 12, 14, 2)
        layers = [c, (240, 220, 160), c, (240, 220, 160)] if kind == "lasagna" else [c, (250, 240, 230), c]
        for i, lc in enumerate(layers):
            R(s, lc, 3, 4 + i * 2, 10, 2)
        if kind == "cake":
            R(s, (230, 60, 80), 7, 2, 2, 2)
    elif kind == "fries":
        R(s, (220, 50, 50), 4, 8, 8, 7)
        for x in (4, 6, 8, 10):
            R(s, c, x, 3 + (x % 3), 2, 6)
    elif kind == "flower":
        R(s, (70, 150, 80), 7, 8, 2, 7)
        for (x, y) in ((4, 3), (9, 2), (6, 6), (10, 6)):
            pygame.draw.circle(s, c, (x + 1, y + 1), 2)
            P(s, (255, 240, 150), x + 1, y + 1)
    elif kind == "wine":
        R(s, (40, 60, 40), 6, 5, 4, 10)
        R(s, (40, 60, 40), 7, 1, 2, 4)
        R(s, c, 6, 8, 4, 4)
        R(s, (230, 220, 200), 6, 8, 4, 1)
    elif kind == "book":
        R(s, c, 3, 2, 10, 12)
        R(s, shade(c, 0.7), 3, 2, 2, 12)
        R(s, (240, 220, 140), 6, 5, 5, 1); R(s, (240, 220, 140), 6, 7, 4, 1)
    elif kind == "sack":
        R(s, (210, 190, 150), 3, 4, 10, 11)
        R(s, (180, 160, 120), 3, 4, 10, 2)
        R(s, (160, 140, 100), 6, 2, 4, 3)
        R(s, c, 5, 8, 6, 4)
        R(s, shade(c, 0.8), 5, 11, 6, 1)
    elif kind == "egg":
        for (x, y) in ((5, 8), (10, 9), (7, 4)):
            pygame.draw.ellipse(s, (246, 236, 214), (x - 3, y - 4, 7, 9))
            P(s, (255, 255, 255), x - 1, y - 2)
    elif kind == "milk":
        R(s, (240, 244, 250), 4, 5, 8, 10)
        pygame.draw.polygon(s, (240, 244, 250), [(4, 5), (8, 1), (12, 5)])
        R(s, (90, 150, 220), 4, 8, 8, 4)
        R(s, (200, 210, 230), 11, 5, 1, 10)
    elif kind == "cheese":
        pygame.draw.polygon(s, c, [(2, 12), (14, 12), (14, 6), (4, 5)])
        pygame.draw.polygon(s, shade(c, 1.15), [(4, 5), (14, 6), (11, 3)])
        for (x, y) in ((6, 9), (10, 8), (12, 10)):
            pygame.draw.circle(s, shade(c, 0.75), (x, y), 1)
    elif kind == "pasta":
        for i in range(5):
            pygame.draw.line(s, c, (3 + i * 2, 3), (5 + i * 2, 14), 1)
        R(s, (200, 60, 50), 3, 7, 11, 2)
    elif kind == "leaf":
        pygame.draw.ellipse(s, c, (2, 3, 8, 11))
        pygame.draw.ellipse(s, shade(c, 1.15), (7, 2, 7, 10))
        pygame.draw.line(s, shade(c, 0.7), (6, 13), (6, 5))
    elif kind == "mushroom":
        pygame.draw.ellipse(s, c, (2, 3, 12, 8))
        R(s, (240, 230, 210), 6, 9, 4, 6)
        P(s, (250, 240, 220), 5, 5); P(s, (250, 240, 220), 9, 4)
    elif kind == "chocbar":
        R(s, c, 2, 4, 12, 9)
        for x in (5, 8, 11):
            R(s, shade(c, 0.75), x, 4, 1, 9)
        R(s, shade(c, 0.75), 2, 8, 12, 1)
        R(s, (200, 40, 50), 2, 10, 12, 3)
    elif kind == "ingredient":
        pygame.draw.circle(s, c, (8, 9), 5)
        pygame.draw.circle(s, shade(c, 1.15), (7, 8), 2)
        R(s, (80, 150, 80), 7, 2, 2, 3)
        pygame.draw.circle(s, shade(c, 0.75), (8, 9), 5, 1)
    elif kind == "pancake":
        for i in range(3):
            pygame.draw.ellipse(s, shade(c, 1 - i * 0.08), (2, 9 - i * 3, 12, 5))
        R(s, (250, 240, 200), 6, 2, 4, 2)
        R(s, (150, 80, 40), 4, 4, 8, 1)
    elif kind == "sushi":
        for x in (2, 9):
            R(s, (250, 250, 250), x, 7, 6, 6)
            R(s, c, x, 5, 6, 3)
            R(s, (30, 40, 30), x, 9, 6, 2)
    elif kind == "dish":
        pygame.draw.ellipse(s, (240, 240, 246), (1, 6, 14, 8))
        pygame.draw.ellipse(s, c, (4, 6, 8, 5))
        P(s, shade(c, 1.3), 6, 7); P(s, (80, 160, 80), 9, 7)
    else:
        R(s, c, 3, 3, 10, 10)
    return s


def item_icon(item, k=3):
    from .data import ITEMS
    it = ITEMS[item]
    return cached(("icon", item, k), lambda: up(_icon(it["icon"], it["color"]), k))


def heart(full=True, k=3, color=(240, 80, 130)):
    def make():
        s = new(7, 6)
        rows = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "X":
                    P(s, color if full else (80, 60, 90), x, y)
        return up(s, k)
    return cached(("heart", full, k, color), make)


# ---------------------------------------------------------------------------
# Retratos e imagens
# ---------------------------------------------------------------------------

PORTRAIT_BG = ((70, 46, 104), (34, 22, 54))     # fundo do quadro do retrato (degradê roxo)
PORTRAIT_SIZE = 236                              # tamanho do retrato na caixa de fala (igual ao ui.Dialog)
PORTRAIT_SRC = {}                                # id da imagem do retrato -> arquivo (para redesenhar em alta)


def _portrait_bg(size):
    s = pygame.Surface((size, size))
    top, bottom = PORTRAIT_BG
    for y in range(size):
        pygame.draw.line(s, mix(top, bottom, y / size), (0, y), (size, y))
    return s


def _clear_fake_bg(img):
    """Apaga o fundo "de mentira" que encosta nas bordas: branco liso ou o xadrez cinza de
    transparência desenhado na imagem. Só some o que está ligado às bordas, então o branco
    dentro do desenho (olhos, roupa) fica intacto."""
    w, h = img.get_size()
    # sementes nas bordas de cima e dos lados (embaixo costuma encostar a roupa, que pode ser clara)
    seeds = [(0, 0), (w - 1, 0), (w // 4, 0), (w // 2, 0), (3 * w // 4, 0),
             (0, h // 4), (w - 1, h // 4), (0, h // 2), (w - 1, h // 2)]
    if all(img.get_at(c).a < 20 for c in seeds[:2]):
        return img                                      # já tem transparência de verdade
    # tons claros e acinzentados (branco liso ou as duas cores do xadrez, com as bordas suavizadas)
    bg = pygame.mask.from_threshold(img, (226, 226, 226, 255), (30, 30, 30, 255))
    hole = pygame.mask.Mask((w, h))
    for c in seeds:
        col = img.get_at(c)
        if bg.get_at(c) and max(col[:3]) - min(col[:3]) < 20:
            hole.draw(bg.connected_component(c), (0, 0))
    if hole.count() == 0:
        return img
    # sobras do xadrez: pontinhos soltos que não fazem parte do desenho principal
    fig = hole.copy()
    fig.invert()
    keep = pygame.mask.Mask((w, h))
    for comp in fig.connected_components(minimum=max(200, w * h // 2000)):
        keep.draw(comp, (0, 0))
    hole = keep
    hole.invert()
    out = img.copy()
    out.blit(hole.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)), (0, 0),
             special_flags=pygame.BLEND_RGBA_SUB)
    return out


def portrait(filename, look, size=120):
    def make():
        if filename:
            path = os.path.join(ASSETS, "portraits", filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    w, h = img.get_size()
                    side = min(w, h)
                    crop = img.subsurface((max(0, (w - side) // 2), 0, side, side)).copy()
                    if filename.lower().endswith(".png"):
                        # retrato: só o desenho, com transparência (sem quadrado de fundo)
                        crop = _clear_fake_bg(crop.convert_alpha())
                        out = pygame.transform.smoothscale(crop, (size, size))
                    else:
                        out = pygame.transform.smoothscale(crop.convert(), (size, size))
                    PORTRAIT_SRC[id(out)] = filename
                    return out
                except Exception:
                    pass
        frames = character_frames(look)
        small = pygame.transform.scale(frames[("down", 0)], (16, 32))
        head = new(16, 14)
        head.blit(small, (0, -1))
        s = pygame.Surface((size, size))
        top, bottom = (70, 46, 104), (34, 22, 54)
        for y in range(size):
            pygame.draw.line(s, mix(top, bottom, y / size), (0, y), (size, y))
        big = pygame.transform.scale(head, (size, int(size * 14 / 16)))
        s.blit(big, (0, size - big.get_height()))
        return s
    return cached(("portrait", filename, tuple(sorted((k, str(v)) for k, v in look.items())), size), make)


# humor -> sufixos procurados em assets/portraits (nome.png, nome_feliz.png, nome_ruim.png, nome_timido.png)
MOOD_SUFFIXES = {"happy": ("feliz",), "smile": ("feliz",), "bad": ("ruim", "bravo", "brava"),
                 "shy": ("timido", "timida"), "love": ("timido", "timida", "feliz")}


def portrait_hd(filename, size):
    """O mesmo retrato, mas no tamanho real da tela (tela cheia maior que 1280x720).

    Usa o original de assets/portraits_hd quando ele existe (melhor qualidade); senão, o de assets/portraits.
    """
    def make():
        path = os.path.join(ASSETS, "portraits", filename)
        hd = os.path.join(ASSETS, "portraits_hd", filename)
        img = pygame.image.load(hd if os.path.exists(hd) else path)
        w, h = img.get_size()
        side = min(w, h)
        crop = img.subsurface((max(0, (w - side) // 2), 0, side, side)).copy()
        if filename.lower().endswith(".png"):
            crop = _clear_fake_bg(crop.convert_alpha())
        else:
            crop = crop.convert()
        # reduz em etapas (metade por vez) para não serrilhar
        while crop.get_width() > size[0] * 2:
            crop = pygame.transform.smoothscale(crop, (crop.get_width() // 2, crop.get_height() // 2))
        return pygame.transform.smoothscale(crop, size)
    return cached(("portrait_hd", filename, size), make)


def portrait_file(base, mood=None):
    """Arquivo do retrato de uma personagem (pelo padrão de nomes), ou None se não houver."""
    if not base:
        return None
    if mood:
        for suf in MOOD_SUFFIXES.get(mood, (mood,)):
            f = f"{base}_{suf}.png"
            if portrait_exists(f):
                return f
    for f in (f"{base}.png",):
        if portrait_exists(f):
            return f
    return None


def resolve_photo(name):
    """Foto de cutscene: usa o arquivo pedido; se ele não existir mais, tenta o retrato equivalente
    (ex.: lucy_apaixonada.jpg -> lucy_timido.png)."""
    if portrait_exists(name):
        return name
    stem = os.path.splitext(name)[0]
    base, _, suf = stem.partition("_")
    alias = {"apaixonada": "love", "apaixonado": "love", "feliz": "happy", "sorridente": "smile", "ruim": "bad",
             "timido": "shy", "timida": "shy"}.get(suf)
    if portrait_exists(stem + ".png"):
        return stem + ".png"
    return portrait_file(base, alias)


def portrait_exists(filename):
    return bool(filename) and os.path.exists(os.path.join(ASSETS, "portraits", filename))


def load_image(name, size):
    def make():
        path = os.path.join(ASSETS, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            except Exception:
                pass
        return None
    return cached(("img", name, size), make)


def load_logo(size=96):
    img = load_image("lexcorp.png", (size, size))
    if img:
        return img
    s = new(16, 16)
    R(s, (120, 40, 190), 4, 2, 3, 12); R(s, (120, 40, 190), 4, 11, 9, 3)
    return pygame.transform.scale(s, (size, size))

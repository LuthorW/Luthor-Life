"""Arte da Marina Luthor (clube náutico da Luthor Corp): prédio, iate, veleiro, cais e o convés do alto-mar."""
import random

import pygame

from . import art
from .art import new, up, R, P, shade, mix, cached
from .config import TS

NAVY = (28, 44, 84)
NAVY_LT = (60, 84, 140)
WHITE = (240, 242, 246)
WHITE_DK = (204, 208, 218)
TEAK = (176, 122, 74)
TEAK_DK = (132, 88, 52)
ROPE = (214, 190, 140)
PURPLE = (138, 0, 230)


# ---------------------------------------------------------------------------
# Tiles: mar profundo (alto-mar) e convés de madeira
# ---------------------------------------------------------------------------
_prev_make_tile = art._make_tile


def _make_tile(name, v):
    if name == "deep":
        s = new(TS, TS)
        base = (34, 86, 156)
        s.fill(base)
        for i in range(4):
            y = (i * 4 + v * 2) % 16
            x = (i * 7 + v * 3) % 12
            R(s, mix(base, (255, 255, 255), 0.28), x, y, 4, 1)
            R(s, mix(base, (255, 255, 255), 0.12), (x + 6) % 14, (y + 2) % 16, 2, 1)
        return s
    if name == "deck":
        s = new(TS, TS)
        s.fill(TEAK)
        for y in (0, 4, 8, 12):
            R(s, TEAK_DK, 0, y + 3, 16, 1)
            R(s, mix(TEAK, (255, 230, 190), 0.25), 0, y, 16, 1)
        r = random.Random(v)
        for _ in range(3):
            P(s, (60, 40, 30), r.randrange(16), r.randrange(16))
        return s
    return _prev_make_tile(name, v)


art._make_tile = _make_tile


# ---------------------------------------------------------------------------
# Prédio do clube
# ---------------------------------------------------------------------------
def _marina_building(w, h, extra, night):
    W, H = w * TS, (h + extra) * TS
    s = new(W, H)
    top = 16
    # telhado azul-marinho com borda branca
    pygame.draw.polygon(s, NAVY, [(0, top + 4), (10, top - 10), (W - 10, top - 10), (W, top + 4)])
    R(s, NAVY_LT, 10, top - 10, W - 20, 3)
    R(s, WHITE, 0, top + 2, W, 3)
    # mastro com bandeiras
    cx = W // 2
    R(s, (90, 90, 100), cx - 1, 0, 2, top - 8)
    R(s, PURPLE, cx + 1, 1, 9, 6)
    R(s, (184, 76, 255), cx + 1, 1, 9, 2)
    # paredes brancas com faixa azul
    R(s, WHITE, 0, top + 5, W, H - top - 5)
    R(s, WHITE_DK, W - 3, top + 5, 3, H - top - 5)
    R(s, NAVY, 0, top + 18, W, 3)
    # janelas redondas (escotilhas) no andar de cima
    glass = (250, 214, 140) if night else (150, 200, 230)
    for x in range(14, W - 8, 22):
        pygame.draw.circle(s, NAVY, (x, top + 11), 5)
        pygame.draw.circle(s, glass, (x, top + 11), 3)
        P(s, (255, 255, 255), x - 1, top + 10)
    # placa (o nome é escrito pelo jogo)
    R(s, NAVY, 8, top + 24, W - 16, 10)
    R(s, (214, 172, 84), 8, top + 24, W - 16, 1); R(s, (214, 172, 84), 8, top + 33, W - 16, 1)
    # vidraças do térreo e porta dupla de vidro no centro
    for x in list(range(6, cx - 14, 14)) + list(range(cx + 16, W - 8, 14)):
        R(s, NAVY, x - 1, H - 26, 12, 20)
        R(s, glass, x, H - 25, 10, 18)
        R(s, mix(glass, (255, 255, 255), 0.4), x + 2, H - 23, 2, 10)
    R(s, NAVY, cx - 10, H - 28, 20, 28)
    R(s, glass, cx - 8, H - 26, 7, 26); R(s, glass, cx + 1, H - 26, 7, 26)
    # toldo listrado azul e branco sobre a porta
    for i in range(6):
        R(s, NAVY_LT if i % 2 == 0 else WHITE, cx - 15 + i * 5, H - 34, 5, 5)
    R(s, NAVY, cx - 15, H - 29, 30, 1)
    # boias salva-vidas penduradas
    for x in (cx - 24, cx + 22):
        pygame.draw.circle(s, (230, 70, 60), (x, H - 18), 5)
        pygame.draw.circle(s, WHITE, (x, H - 18), 5, 2)
        pygame.draw.circle(s, WHITE, (x, H - 18), 2)
    R(s, (190, 190, 200), 0, H - 3, W, 3)
    return s


_prev_building_sprite = art.building_sprite


def _building_sprite(style, w, h, extra, night=False):
    if style == "marina":
        return cached(("bld", style, w, h, extra, night), lambda: up(_marina_building(w, h, extra, night)))
    return _prev_building_sprite(style, w, h, extra, night)


art.building_sprite = _building_sprite


# ---------------------------------------------------------------------------
# Barcos e cais
# ---------------------------------------------------------------------------
def _yacht():
    """Iate de luxo atracado (5x2 tiles), visto de lado, proa para a direita."""
    s = new(80, 52)
    hull_y = 30
    pygame.draw.polygon(s, WHITE, [(2, hull_y), (76, hull_y), (66, hull_y + 16), (8, hull_y + 16)])
    pygame.draw.polygon(s, NAVY, [(6, hull_y + 10), (72, hull_y + 10), (66, hull_y + 16), (8, hull_y + 16)])
    R(s, PURPLE, 4, hull_y + 3, 68, 2)
    # cabine em dois níveis
    pygame.draw.polygon(s, WHITE, [(14, hull_y), (18, 16), (54, 16), (64, hull_y)])
    pygame.draw.polygon(s, WHITE_DK, [(24, 16), (28, 6), (48, 6), (52, 16)])
    R(s, (40, 60, 90), 20, 20, 32, 6)
    R(s, (40, 60, 90), 30, 9, 14, 4)
    for x in (22, 30, 38, 46):
        R(s, (120, 170, 220), x, 21, 6, 4)
    R(s, (90, 90, 100), 38, 0, 2, 7)
    R(s, (220, 60, 60), 39, 1, 4, 3)
    # nome no casco
    for x in range(14, 40, 3):
        P(s, (214, 172, 84), x, hull_y + 7)
    return s


def _sailboat():
    s = new(32, 44)
    pygame.draw.polygon(s, WHITE, [(2, 32), (30, 32), (25, 40), (7, 40)])
    R(s, NAVY, 5, 37, 22, 3)
    R(s, (90, 80, 70), 15, 2, 2, 31)
    pygame.draw.polygon(s, (246, 246, 250), [(17, 3), (17, 30), (29, 30)])
    pygame.draw.polygon(s, (190, 120, 255), [(14, 6), (14, 30), (4, 30)])
    return s


def _buoy():
    s = new(16, 16)
    pygame.draw.ellipse(s, (240, 120, 40), (3, 5, 10, 9))
    R(s, WHITE, 3, 8, 10, 2)
    R(s, (60, 60, 70), 7, 1, 2, 5)
    return s


def _bollard():
    s = new(16, 16)
    R(s, (60, 64, 76), 5, 6, 6, 8)
    R(s, (96, 100, 114), 4, 5, 8, 2)
    R(s, ROPE, 3, 9, 10, 2)
    return s


def _charter():
    """Balcão de passeios do clube (3x1)."""
    s = new(48, 28)
    R(s, NAVY, 0, 10, 48, 18)
    R(s, WHITE, 0, 8, 48, 4)
    R(s, (214, 172, 84), 0, 12, 48, 1)
    for i, c in enumerate(((240, 120, 40), (120, 180, 230), (190, 120, 255))):
        R(s, c, 6 + i * 14, 16, 8, 6)
        R(s, WHITE, 7 + i * 14, 17, 6, 1)
    R(s, (230, 220, 190), 34, 0, 10, 9)
    R(s, NAVY, 35, 2, 8, 1); R(s, NAVY, 35, 4, 6, 1)
    return s


def _trophy():
    """Estante de troféus de regata (2x1)."""
    s = new(32, 30)
    R(s, TEAK_DK, 0, 4, 32, 26)
    R(s, TEAK, 2, 6, 28, 22)
    R(s, TEAK_DK, 2, 16, 28, 2)
    for (x, y, c) in ((5, 8, (230, 190, 70)), (13, 9, (200, 200, 210)), (22, 8, (230, 190, 70)),
                      (7, 19, (200, 140, 80)), (18, 19, (230, 190, 70))):
        R(s, c, x, y + 4, 4, 3)
        R(s, c, x + 1, y + 2, 2, 2)
        R(s, mix(c, (255, 255, 255), 0.5), x, y, 4, 2)
    return s


def _ship_wheel():
    s = new(16, 16)
    pygame.draw.circle(s, TEAK_DK, (8, 8), 6, 2)
    for a in range(0, 360, 45):
        v = pygame.math.Vector2(0, -8).rotate(a)
        pygame.draw.line(s, TEAK, (8, 8), (8 + v.x, 8 + v.y))
    pygame.draw.circle(s, (214, 172, 84), (8, 8), 2)
    return s


def _chart():
    s = new(32, 16)
    R(s, TEAK_DK, 0, 1, 32, 14)
    R(s, (226, 218, 190), 1, 2, 30, 12)
    for (x, y, w, h) in ((3, 4, 9, 6), (20, 6, 8, 5)):
        R(s, (190, 200, 150), x, y, w, h)
    for x in range(4, 29, 3):
        P(s, (60, 90, 160), x, 12)
    pygame.draw.circle(s, (220, 60, 60), (16, 7), 1)
    return s


def _helm():
    """Timão no convés do barco (volta para a marina)."""
    s = new(16, 28)
    R(s, TEAK_DK, 6, 12, 4, 16)
    pygame.draw.circle(s, TEAK_DK, (8, 10), 7, 2)
    for a in range(0, 360, 45):
        v = pygame.math.Vector2(0, -9).rotate(a)
        pygame.draw.line(s, TEAK, (8, 10), (8 + v.x, 10 + v.y))
    pygame.draw.circle(s, (214, 172, 84), (8, 10), 2)
    return s


def _deck_cabin():
    """Cabine do barco no alto-mar (4x2)."""
    s = new(64, 52)
    R(s, WHITE, 2, 14, 60, 38)
    R(s, WHITE_DK, 58, 14, 4, 38)
    R(s, NAVY, 0, 8, 64, 8)
    R(s, NAVY_LT, 0, 8, 64, 2)
    for x in (8, 26, 44):
        R(s, (120, 170, 220), x, 22, 12, 9)
        R(s, (200, 230, 250), x + 2, 23, 3, 4)
    R(s, NAVY, 26, 36, 12, 16)
    R(s, (90, 90, 100), 30, 0, 2, 8)
    R(s, PURPLE, 32, 1, 7, 4)
    return s


def _cooler_box():
    s = new(16, 16)
    R(s, (60, 130, 200), 2, 6, 12, 9)
    R(s, WHITE, 2, 5, 12, 3)
    R(s, (40, 90, 150), 2, 13, 12, 2)
    return s


art.OBJECT_BUILDERS.update({
    "yacht": _yacht, "sailboat": _sailboat, "buoy": _buoy, "bollard": _bollard, "charter": _charter,
    "trophy": _trophy, "ship_wheel": _ship_wheel, "nautical_chart": _chart, "helm": _helm,
    "deck_cabin": _deck_cabin, "cooler_box": _cooler_box,
})

def decorate_floor(m, surf):
    """Borda do casco (amurada branca) em volta do convés do barco do alto-mar."""
    from .config import TILE, SCALE
    if m.name != "altomar":
        return
    t = 3 * SCALE
    for y in range(m.h):
        for x in range(m.w):
            if m.tiles[y][x] != "deck":
                continue
            for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                if m.tile_at(x + dx, y + dy) != "deep":
                    continue
                px, py = x * TILE, y * TILE
                if dy == -1:
                    rects = [((px, py, TILE, t), WHITE), ((px, py + t, TILE, SCALE), NAVY)]
                elif dy == 1:
                    rects = [((px, py + TILE - t - SCALE * 2, TILE, t + SCALE * 2), WHITE),
                             ((px, py + TILE - SCALE * 2, TILE, SCALE * 2), NAVY)]
                elif dx == -1:
                    rects = [((px, py, t, TILE), WHITE), ((px + t, py, SCALE, TILE), NAVY)]
                else:
                    rects = [((px + TILE - t, py, t, TILE), WHITE), ((px + TILE - t - SCALE, py, SCALE, TILE), NAVY)]
                for r, c in rects:
                    pygame.draw.rect(surf, c, r)


OBJECT_DEFS = {
    "yacht": (5, 2, True, "obj"), "sailboat": (2, 1, True, "obj"), "buoy": (1, 1, True, "obj"),
    "bollard": (1, 1, True, "obj"), "charter": (3, 1, True, "obj"), "trophy": (2, 1, True, "obj"),
    "ship_wheel": (1, 1, False, "wall"), "nautical_chart": (2, 1, False, "wall"), "helm": (1, 1, True, "obj"),
    "deck_cabin": (4, 2, True, "obj"), "cooler_box": (1, 1, True, "obj"),
}
HITBOXES = {"bollard": (4, 7, 8, 8), "buoy": (3, 5, 10, 9), "cooler_box": (2, 5, 12, 10), "helm": (4, 10, 8, 6)}

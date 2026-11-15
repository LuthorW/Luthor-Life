"""Praça do chafariz, no meio do Parque Central (caprichada).

- chão de pedras (tile "plaza", o mesmo do calçadão) no lugar da terra, com meio-fio de pedra onde encontra a grama;
- mosaico no chão: anel de pedras cor de terracota e uma rosa dos ventos em volta do chafariz (decorate_floor);
- chafariz redondo de pedra (objeto "chafariz", 6x3 tiles, sólido): bacia, coluna, bacia de cima, água caindo,
  jatinho no topo e ondinhas, animado (object_image).
As trilhas de terra do parque (norte, leste, sul) continuam de terra.
"""
import math

import pygame

from . import art
from .art import new, up, R, P, mix
from .config import TILE, SCALE

AREA = (14, 29, 25, 39)                 # x0, y0, x1, y1 da praça (inclusive)
FOUNTAIN = (17, 33)                     # canto de cima à esquerda do chafariz (6x3 tiles)
CENTER = (20.0, 34.5)                   # centro do chafariz e da praça, em tiles (eixos de simetria)
FRAMES, FPS = 8, 7.0

STONE_LT, STONE, STONE_DK, STONE_LINE = (224, 220, 230), (196, 190, 206), (150, 142, 164), (98, 90, 112)
WATER, WATER_DK, WATER_LT, FOAM = (86, 166, 224), (58, 128, 196), (150, 210, 244), (236, 248, 255)


def _ellipse(s, col, cx, cy, rx, ry):
    pygame.draw.ellipse(s, col, (round(cx - rx), round(cy - ry), round(2 * rx), round(2 * ry)))


def _fountain(f):
    """Quadro f do chafariz: 96x78 px de arte (6 tiles de largura; a base de 3 tiles fica embaixo)."""
    W, H = 96, 78
    s = new(W, H)
    cx, cy = 48, 52                                     # centro da bacia grande
    # sombra no chão
    _ellipse(s, (0, 0, 0, 50), cx, cy + 9, 47, 15)
    # parede da bacia (espessura na frente) e borda
    for k in range(7, 0, -1):
        _ellipse(s, mix(STONE_DK, STONE_LINE, k / 9), cx, cy + k, 46, 18)
    _ellipse(s, STONE_LINE, cx, cy, 46, 18)
    _ellipse(s, STONE, cx, cy, 45, 17)
    _ellipse(s, STONE_LT, cx, cy - 1, 44, 16)
    def mirror(col, x, y):                              # pinta x e o espelho de x (o desenho fica simétrico)
        P(s, col, x, y)
        P(s, col, W - 1 - x, y)

    for a in range(-90, 91, 24):                        # juntas das pedras da borda
        x = cx + math.cos(math.radians(a)) * 42.5
        y = cy + math.sin(math.radians(a)) * 15.5 - 1
        mirror(STONE_DK, int(x), int(y))
    # água da bacia
    _ellipse(s, WATER_DK, cx, cy, 40, 13)
    _ellipse(s, WATER, cx, cy + 1, 39, 11)
    for i in range(3):                                  # ondinhas saindo da coluna
        t = ((f / FRAMES) + i / 3) % 1.0
        rx, ry = round(7 + t * 30), 2.5 + t * 8
        col = (*mix(WATER, FOAM, 0.6 * (1 - t)), int(200 * (1 - t)))
        pygame.draw.ellipse(s, col, (round(cx - rx), round(cy + 2 - ry), round(2 * rx), round(2 * ry)), 1)
    for (bx, by, ph) in ((18, 51, 0), (75, 51, 0), (30, 57, 5), (63, 57, 5), (40, 47, 2), (53, 47, 2)):    # brilhinhos
        if (f + ph) % 8 < 4:
            R(s, WATER_LT, bx, by, 3, 1)
    # cortina de água caindo da bacia de cima
    for y in range(30, 50):
        if (y - 30 + f * 3) % 6 < 4:
            mirror((*mix(WATER_LT, FOAM, 0.4), 200), cx + 11 + (y - 30) // 8, y)
    for x in range(cx + 11, cx + 16):                   # respingo onde cai
        mirror((*FOAM, 220), x, 49)
    # coluna
    R(s, STONE_LINE, cx - 5, 26, 10, 27)
    R(s, STONE, cx - 4, 26, 8, 27)
    R(s, STONE_LT, cx - 4, 26, 2, 27)
    R(s, STONE_DK, cx + 2, 26, 2, 27)
    for y in (34, 44):                                  # aneis da coluna
        R(s, STONE_LINE, cx - 6, y, 12, 3)
        R(s, STONE_LT, cx - 5, y, 10, 1)
    # bacia de cima
    for k in range(3, 0, -1):
        _ellipse(s, mix(STONE_DK, STONE_LINE, k / 4), cx, 27 + k, 13, 4.5)
    _ellipse(s, STONE_LINE, cx, 27, 13, 4.5)
    _ellipse(s, STONE_LT, cx, 26.5, 12, 3.8)
    _ellipse(s, WATER, cx, 26.5, 10, 2.6)
    # haste e a tacinha do topo, com o jatinho
    R(s, STONE_LINE, cx - 2, 19, 4, 8)
    R(s, STONE_LT, cx - 1, 19, 2, 8)
    _ellipse(s, STONE_LINE, cx, 19, 6, 2.2)
    _ellipse(s, STONE_LT, cx, 18.6, 5, 1.6)
    _ellipse(s, WATER_LT, cx, 18.6, 3, 1)
    for i in range(6):                                  # gotinhas subindo e caindo na bacia de cima (dos dois lados)
        t = ((f / FRAMES) + i / 6) % 1.0
        x = cx + round(t * (10 if i % 3 else 6))
        y = 15 - math.sin(t * math.pi) * 6 + t * 11
        mirror((*FOAM, int(255 * (1 - 0.5 * t))), x, int(y))
    R(s, (*FOAM, 230), cx - 1, 12 - f % 2, 2, 6 + f % 2)   # o jatinho no meio
    R(s, (*WATER_LT, 220), cx - 1, 11 - f % 2, 2, 1)
    return s


def frame_image(f):
    return art.cached(("chafariz", f), lambda: up(_fountain(f)))


def object_image(g, o):
    if o.kind != "chafariz":
        return None
    return frame_image(int(g.t * FPS) % FRAMES)


art.OBJECT_BUILDERS["chafariz"] = lambda: _fountain(0)


# ---------------------------------------------------------------------------
# Chão: mosaico e meio-fio
# ---------------------------------------------------------------------------
TERRA, TERRA_DK = (196, 120, 92), (150, 84, 66)
CLARA, ESCURA = (236, 226, 210), (128, 118, 138)


def _mosaic():
    """Desenho do chão da praça em px de arte (sobreposto às pedras)."""
    x0, y0, x1, y1 = AREA
    w, h = (x1 - x0 + 1) * 16, (y1 - y0 + 1) * 16
    s = new(w, h)
    cx, cy = (CENTER[0] - x0) * 16, (CENTER[1] - y0) * 16
    r_out, r_in = 4.25 * 16, 3.7 * 16
    for y in range(h):
        for x in range(w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if r_in <= d <= r_out:                      # anel de pedras de terracota com juntas
                a = math.atan2(dy, dx)
                seg = int((a + math.pi) / (2 * math.pi) * 64)
                edge = d < r_in + 1 or d > r_out - 1
                col = TERRA_DK if edge or (seg % 2 == 0 and int(d) % 4 == 0) else TERRA
                P(s, (*col, 255), x, y)
            elif r_out < d <= r_out + 1:
                P(s, (*ESCURA, 160), x, y)
            elif 2.0 * 16 < d < r_in:                   # rosa dos ventos: 8 pontas
                ang = math.degrees(math.atan2(dy, abs(dx)))     # espelhado: os dois lados iguais
                a = ang % 45
                off = min(a, 45 - a)                    # distância angular até a ponta mais perto
                main = round(ang / 45) % 2 == 0    # N, L, S, O mais compridas
                reach = r_in if main else r_in - 10
                width = 7.0 * (1 - (d - 2 * 16) / (reach - 2 * 16)) if d < reach else -1
                if off < width and abs(dx) >= 12:    # sem as pontas norte e sul (atrás e embaixo do chafariz)
                    left = a < 22.5
                    P(s, (*(CLARA if left else ESCURA), 230 if main else 190), x, y)
    return s


def decorate_floor(m, surf):
    """Chamado por GameMap ao montar o chão da cidade."""
    if m.name != "city":
        return
    x0, y0, x1, y1 = AREA
    img = art.cached("praca_mosaico", lambda: up(_mosaic()))
    surf.blit(img, (x0 * TILE, y0 * TILE))
    k = SCALE
    for y in range(y0, y1 + 1):                         # meio-fio de pedra onde a praça encontra a grama
        for x in range(x0, x1 + 1):
            if m.tiles[y][x] != "plaza":
                continue
            px, py = x * TILE, y * TILE
            for (dx, dy) in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                if m.tile_at(x + dx, y + dy) in ("grass", "flowers"):
                    if dy == -1:
                        pygame.draw.rect(surf, STONE_LINE, (px, py, TILE, k))
                        pygame.draw.rect(surf, STONE_LT, (px, py + k, TILE, k))
                    elif dy == 1:
                        pygame.draw.rect(surf, STONE_LT, (px, py + TILE - 3 * k, TILE, k))
                        pygame.draw.rect(surf, STONE_DK, (px, py + TILE - 2 * k, TILE, k))
                        pygame.draw.rect(surf, STONE_LINE, (px, py + TILE - k, TILE, k))
                    elif dx == -1:
                        pygame.draw.rect(surf, STONE_LINE, (px, py, k, TILE))
                        pygame.draw.rect(surf, STONE_LT, (px + k, py, k, TILE))
                    else:
                        pygame.draw.rect(surf, STONE_LT, (px + TILE - 2 * k, py, k, TILE))
                        pygame.draw.rect(surf, STONE_LINE, (px + TILE - k, py, k, TILE))

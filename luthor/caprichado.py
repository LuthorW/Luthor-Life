"""Cidade caprichada (pedido da dona, com a imagem de referência "Cidade caprichada, bonecos de sempre").

O que muda (os personagens continuam exatamente iguais):
- chão: calçada de pedras em amarração, meio-fio, asfalto com textura, faixas e faixa de pedestres novas;
- todos os prédios redesenhados com cornija, janelas com moldura e floreira, toldos, vitrines e portas
  (Luthor Corp, Grão Nobre, CatCo, Bayside Books, Mercado Central, Ricci Trattoria, Noonan's, Cine National,
  Residencial Luthor, Apartamentos Bayside, Gruppo Ricci, Conti Moretti e Marina Luthor);
- objetos de rua: poste de lanterna, mesinhas com guarda-sol, lousa de cardápio, floreiras e pombos.

Tudo é desenhado em pixels de arte (16 px por tile) e ampliado por art.up, como o resto do jogo.
Janelas acesas usam a cor LIT: é por ela que lighting.py acha as janelas e faz elas brilharem à noite.
Os letreiros (texto) são escritos por `draw_label`, chamado por Game.draw_building.
"""
import math
import random

import pygame

from . import art, ui
from .art import new, R, P, shade, mix
from .config import SCALE, TILE, TS

LIT = (252, 222, 136)          # vidro aceso (a mesma cor que lighting.py procura)
ROXO, ROXO_2 = (120, 40, 190), (184, 76, 255)


# ---------------------------------------------------------------------------
# Chão: calçada de pedra, asfalto e meio-fio
# ---------------------------------------------------------------------------
PEDRA = (182, 176, 192)
PEDRA_JUNTA = (148, 142, 160)
PEDRA_LUZ = (204, 199, 214)
PLAZA = (206, 186, 160)
PLAZA_JUNTA = (176, 156, 132)
ASFALTO = (74, 72, 86)
FAIXA = (240, 198, 72)
BRANCO = (236, 236, 242)


def _pedras(v, base, junta, luz, seed):
    """Pedras retangulares assentadas em amarração (8x4), cada uma com um tom levemente diferente."""
    s = new(TS, TS)
    s.fill(junta)
    r = random.Random(v * 41 + seed)
    for row in range(4):
        y = row * 4
        off = 4 if row % 2 else 0
        for bx in range(-8, TS, 8):
            x = bx + off
            tom = shade(base, r.choice((0.95, 1.0, 1.0, 1.03, 0.98)))
            x0, x1 = max(0, x), min(TS, x + 7)
            if x1 <= x0:
                continue
            R(s, tom, x0, y, x1 - x0, 3)
            R(s, mix(tom, luz, 0.6), x0, y, x1 - x0, 1)             # luz em cima de cada pedra
            if r.random() < 0.25:
                P(s, shade(tom, 0.88), r.randrange(x0, x1), y + 2)
    return s


def _asfalto(name, v):
    s = new(TS, TS)
    s.fill(ASFALTO)
    r = random.Random(v * 17 + 3)
    for _ in range(30):
        P(s, r.choice((shade(ASFALTO, 0.9), shade(ASFALTO, 1.1), shade(ASFALTO, 1.18))), r.randrange(TS), r.randrange(TS))
    if v == 3:                                                      # remendo/rachadura de vez em quando
        for i in range(4):
            P(s, shade(ASFALTO, 0.78), 4 + i, 9 + (i % 2))
    if name == "road_line_b":
        R(s, FAIXA, 2, 14, 12, 2)
    elif name == "road_line_t":
        R(s, FAIXA, 2, 0, 12, 2)
    elif name == "road_line_r":
        R(s, FAIXA, 14, 2, 2, 12)
    elif name == "road_line_l":
        R(s, FAIXA, 0, 2, 2, 12)
    elif name == "cross":
        for x in (1, 6, 11):
            R(s, BRANCO, x, 1, 3, 14)
            R(s, shade(BRANCO, 0.85), x, 14, 3, 1)
    elif name == "cross_v":
        for y in (1, 6, 11):
            R(s, BRANCO, 1, y, 14, 3)
            R(s, shade(BRANCO, 0.85), 1, y + 2, 14, 1)
    return s


_prev_make_tile = art._make_tile


def _make_tile(name, v):
    if name == "pavement":
        return _pedras(v, PEDRA, PEDRA_JUNTA, PEDRA_LUZ, 7)
    if name == "plaza":
        return _pedras(v, PLAZA, PLAZA_JUNTA, (226, 210, 188), 11)
    if name.startswith("road") or name.startswith("cross"):
        return _asfalto(name, v)
    return _prev_make_tile(name, v)


art._make_tile = _make_tile


def _rua(t):
    return t.startswith("road") or t.startswith("cross")


def decorate_floor(m, surf):
    """Meio-fio onde a calçada encontra o asfalto (chamado por GameMap ao montar o chão)."""
    if not m.outdoor:
        return
    k = SCALE
    top, face, dark = (216, 210, 224), (196, 190, 206), (106, 100, 118)
    for y in range(m.h):
        for x in range(m.w):
            if m.tiles[y][x] not in ("pavement", "plaza"):
                continue
            px, py = x * TILE, y * TILE
            if _rua(m.tile_at(x, y + 1)):                    # rua embaixo: topo do meio-fio + face na sombra
                pygame.draw.rect(surf, top, (px, py + 13 * k, TILE, k))
                pygame.draw.rect(surf, face, (px, py + 14 * k, TILE, k))
                pygame.draw.rect(surf, dark, (px, py + 15 * k, TILE, k))
            if _rua(m.tile_at(x, y - 1)):                    # rua em cima: borda clara
                pygame.draw.rect(surf, (122, 116, 134), (px, py, TILE, k))
                pygame.draw.rect(surf, top, (px, py + k, TILE, k))
            if _rua(m.tile_at(x + 1, y)):
                pygame.draw.rect(surf, top, (px + 14 * k, py, k, TILE))
                pygame.draw.rect(surf, dark, (px + 15 * k, py, k, TILE))
            if _rua(m.tile_at(x - 1, y)):
                pygame.draw.rect(surf, dark, (px, py, k, TILE))
                pygame.draw.rect(surf, top, (px + k, py, k, TILE))


def building_shadows(m, surf):
    """Sombra dos prédios no chão: o sol vem de cima à esquerda, a sombra cai à direita e um pouco embaixo."""
    for b in m.buildings:
        x0, y0 = b.x * TILE, b.y * TILE
        x1, y1 = (b.x + b.w) * TILE, (b.y + b.h) * TILE
        side = pygame.Surface((TILE, y1 - y0 + TILE // 2), pygame.SRCALPHA)
        for i in range(TILE):                                # mais escura junto da parede, some aos poucos
            a = int(70 * (1 - i / TILE) ** 1.4)
            pygame.draw.line(side, (20, 14, 40, a), (i, i // 2 + TILE // 3), (i, side.get_height()))
        surf.blit(side, (x1, y0))
        front = pygame.Surface((x1 - x0 + TILE // 2, TILE // 2), pygame.SRCALPHA)
        for j in range(TILE // 2):
            a = int(64 * (1 - j / (TILE / 2)) ** 1.5)
            pygame.draw.line(front, (20, 14, 40, a), (0, j), (front.get_width(), j))
        surf.blit(front, (x0, y1))


# ---------------------------------------------------------------------------
# Peças das fachadas
# ---------------------------------------------------------------------------
def window(s, x, y, w, h, frame, glass, lit, sill=None, box=None, shutter=None, cross=True):
    """Janela com moldura, reflexo, cruzeta; opcional: peitoril, floreira (cor das flores) e venezianas."""
    if shutter:
        for sx in (x - 5, x + w + 2):
            R(s, shutter, sx, y - 1, 3, h + 2)
            for yy in range(y, y + h, 2):
                R(s, shade(shutter, 0.8), sx, yy, 3, 1)
    R(s, frame, x - 1, y - 1, w + 2, h + 2)
    if lit:
        R(s, LIT, x, y, w, h)
        R(s, (255, 240, 190), x, y, w, 1)
    else:
        R(s, glass, x, y, w, h)
        R(s, shade(glass, 0.84), x, y + h - 2, w, 2)
        R(s, shade(glass, 1.22), x, y, w, 1)
        for i in range(min(w, h) - 2):                      # reflexo na diagonal
            if 1 < i < w - 1:
                P(s, shade(glass, 1.18), x + w - 2 - i, y + 1 + i)
    if cross:
        if w >= 8:
            R(s, frame, x + w // 2, y, 1, h)
        if h >= 10:
            R(s, frame, x, y + h // 2, w, 1)
    if sill:
        R(s, sill, x - 2, y + h + 1, w + 4, 2)
        R(s, shade(sill, 1.2), x - 2, y + h + 1, w + 4, 1)
    if box:
        R(s, (110, 70, 46), x - 2, y + h + 2, w + 4, 3)
        R(s, (138, 90, 60), x - 2, y + h + 2, w + 4, 1)
        R(s, (64, 138, 70), x - 2, y + h - 1, w + 4, 3)
        R(s, (92, 168, 84), x - 1, y + h - 1, w + 2, 1)
        for fx in range(x - 1, x + w + 2, 3):
            P(s, box if (fx // 3) % 2 else (255, 236, 140), fx, y + h)


def awning(s, x, y, w, c1, c2, depth=10, stripe=8, wall=None):
    """Toldo listrado com a borda recortada e uma faixa de sombra embaixo (na cor da parede)."""
    for i in range(x, x + w, stripe):
        col = c1 if ((i - x) // stripe) % 2 == 0 else c2
        sw = min(stripe, x + w - i)
        R(s, col, i, y, sw, depth)
        R(s, shade(col, 0.8), i, y, sw, 2)
        R(s, shade(col, 1.08), i, y + 2, sw, 1)
        R(s, col, i + 1, y + depth, max(1, sw - 2), 2)
        R(s, shade(col, 0.72), i + 1, y + depth + 1, max(1, sw - 2), 1)
    if wall:
        R(s, shade(wall, 0.78), x, y + depth + 2, w, 2)
        R(s, shade(wall, 0.9), x, y + depth + 4, w, 1)


def bricks(s, x, y, w, h, base, mortar):
    R(s, base, x, y, w, h)
    for row, yy in enumerate(range(y, y + h, 4)):
        R(s, mortar, x, yy + 3, w, 1)
        off = 0 if row % 2 else 4
        for xx in range(x + off, x + w, 8):
            R(s, mortar, xx, yy, 1, 3)
        for xx in range(x + (row * 3) % 7, x + w, 11):
            R(s, shade(base, 1.07), xx, yy, 3, 1)


def cornice(s, y, W, c, h=6):
    R(s, c, 0, y, W, h)
    R(s, shade(c, 1.25), 0, y, W, 1)
    R(s, shade(c, 0.7), 0, y + h - 1, W, 1)
    for x in range(2, W, 5):
        R(s, shade(c, 1.12), x, y + 2, 2, h - 3)


def door(s, x, y, w, h, frame, wood, lit, glass=(170, 210, 236)):
    """Porta de madeira com vidro em cima, maçaneta e soleira."""
    R(s, frame, x - 1, y - 1, w + 2, h + 1)
    R(s, wood, x, y, w, h)
    R(s, shade(wood, 1.15), x + 1, y + 1, 1, h - 2)
    R(s, LIT if lit else glass, x + 2, y + 2, w - 4, h // 2 - 2)
    R(s, shade(wood, 0.82), x + 2, y + h // 2 + 2, w - 4, 1)
    R(s, shade(wood, 0.82), x + 2, y + h - 5, w - 4, 1)
    P(s, (226, 190, 100), x + w - 3, y + h // 2 + 4)
    R(s, (110, 104, 120), x - 2, y + h - 1, w + 4, 1)


def shopfront(s, x, y, w, h, frame, lit, glass=(168, 206, 232), goods=None, seed=0):
    """Vitrine com caixilhos e mercadoria aparecendo atrás do vidro."""
    R(s, frame, x - 1, y - 1, w + 2, h + 2)
    R(s, LIT if lit else glass, x, y, w, h)
    if not lit:
        R(s, shade(glass, 1.2), x, y, w, 2)
        for i in range(0, min(w, h) - 2, 1):
            P(s, shade(glass, 1.14), x + 3 + i, y + h - 3 - i)
    r = random.Random(seed)
    if goods:
        for gx in range(x + 2, x + w - 3, 4):
            c = r.choice(goods)
            gh = r.randrange(4, 8)
            R(s, c, gx, y + h - gh - 1, 3, gh)
            R(s, shade(c, 1.2), gx, y + h - gh - 1, 3, 1)
    for k in range(x + 12, x + w - 2, 13):
        R(s, frame, k, y, 1, h)
    R(s, shade(frame, 1.2), x - 2, y + h + 1, w + 4, 2)


def vaso(s, x, y, flor=(255, 130, 170)):
    """Vasinho de 8 px com planta (enfeite das fachadas)."""
    R(s, (150, 92, 64), x + 1, y + 5, 6, 4)
    R(s, (176, 112, 78), x, y + 4, 8, 2)
    R(s, (70, 140, 76), x + 1, y, 6, 4)
    R(s, (96, 170, 92), x + 2, y, 3, 2)
    P(s, flor, x + 2, y + 1); P(s, flor, x + 5, y + 2)


def lantern(s, x, y, lit):
    """Arandela de parede (acende à noite)."""
    R(s, (40, 34, 40), x, y, 4, 1)
    R(s, (40, 34, 40), x, y + 1, 1, 5); R(s, (40, 34, 40), x + 3, y + 1, 1, 5)
    R(s, LIT if lit else (230, 214, 170), x + 1, y + 1, 2, 4)
    R(s, (40, 34, 40), x, y + 6, 4, 1)


def side_light(s, W, H, top, light=1.18, dark=0.74, base=None):
    """Quina iluminada à esquerda e sombra à direita (volume do prédio)."""
    for y in range(top, H):
        c = s.get_at((0, y))
        if c.a:
            P(s, shade(c, light), 0, y); P(s, shade(c, light * 0.95), 1, y)
        c = s.get_at((W - 1, y))
        if c.a:
            P(s, shade(c, dark), W - 1, y); P(s, shade(c, dark * 1.1), W - 2, y)


# ---------------------------------------------------------------------------
# Prédios (W, H em pixels de arte; a porta fica no tile da porta de world.Building)
# ---------------------------------------------------------------------------
def _janelas(s, x0, y0, x1, y1, sx, sy, ww, wh, vidro, moldura, acesa, r):
    for y in range(y0, y1, sy):
        for x in range(x0, x1, sx):
            R(s, moldura, x - 1, y - 1, ww + 2, wh + 2)
            if r.random() < acesa:
                R(s, LIT, x, y, ww, wh)
            else:
                R(s, vidro, x, y, ww, wh)
                R(s, shade(vidro, 1.18), x, y, max(1, ww // 2), 1)
                P(s, shade(vidro, 1.3), x, y)
                R(s, shade(vidro, 0.85), x, y + wh - 1, ww, 1)


def _torre(W, H, night):
    r = random.Random("torre-luthor")
    corpo, moldura = (82, 58, 112), (54, 38, 78)
    vidro = (186, 160, 210)
    s = new(W, H)
    R(s, corpo, 0, 6, W, H - 6)
    R(s, shade(corpo, 0.8), 0, 4, W, 4)                     # platibanda
    R(s, shade(corpo, 1.25), 0, 4, W, 1)
    R(s, ROXO, W // 2 - 10, 0, 20, 5)                        # casa de máquinas com o roxo da marca
    R(s, ROXO_2, W // 2 - 1, 0, 2, 2)
    _janelas(s, 6, 12, W - 7, H - 58, 8, 8, 5, 5, vidro, moldura, 0.6 if night else 0.14, r)
    for x in range(0, W, 16):                               # pilares entre as colunas de janelas
        R(s, shade(corpo, 1.08), x + 3, 8, 1, H - 64)
    R(s, shade(corpo, 1.22), 0, 6, 2, H - 6)
    R(s, shade(corpo, 0.72), W - 2, 6, 2, H - 6)
    base = (40, 28, 58)
    R(s, base, 0, H - 54, W, 54)
    R(s, (24, 16, 38), 6, H - 49, W - 12, 15)               # painel do letreiro
    R(s, (60, 44, 84), 6, H - 49, W - 12, 1)
    R(s, ROXO, W // 2 - 26, H - 33, 52, 3)                  # neon
    R(s, (200, 120, 255), W // 2 - 24, H - 32, 48, 1)
    for lado in (-1, 1):                                    # vitrines do saguão
        x = W // 2 + (14 if lado > 0 else -14 - 40)
        R(s, (30, 22, 44), x, H - 26, 40, 22)
        R(s, LIT if night else (120, 132, 176), x + 1, H - 25, 38, 20)
        R(s, (150, 164, 206) if not night else (255, 238, 190), x + 1, H - 25, 38, 2)
        for k in range(1, 4):
            R(s, (30, 22, 44), x + k * 10, H - 25, 1, 20)
        vaso(s, x + 2, H - 12, (200, 140, 255))
        vaso(s, x + 30, H - 12, (200, 140, 255))
    R(s, (30, 24, 46), W // 2 - 12, H - 28, 24, 28)        # porta dupla (centro do tile da porta)
    R(s, LIT if night else (150, 190, 236), W // 2 - 10, H - 26, 20, 26)
    R(s, (200, 222, 246) if not night else (255, 248, 220), W // 2 - 10, H - 26, 4, 26)
    R(s, (30, 24, 46), W // 2 - 1, H - 26, 2, 26)
    R(s, ROXO, W // 2 - 16, H - 31, 32, 3)                  # marquise roxa
    R(s, ROXO_2, W // 2 - 16, H - 31, 32, 1)
    R(s, (96, 90, 110), W // 2 - 18, H - 3, 36, 3)          # degrau
    return s


def _cafe(W, H, night):
    s = new(W, H)
    parede, sombra = (240, 228, 204), (214, 198, 172)
    madeira, madeira_dk = (122, 76, 46), (86, 52, 32)
    vinho = (150, 50, 60)
    R(s, parede, 0, 8, W, H - 8)
    for y in range(12, H - 40, 4):                           # reboco com linhas leves
        R(s, shade(parede, 0.97), 0, y, W, 1)
    R(s, madeira, 0, 0, W, 9)                               # cornija com dentículos
    R(s, madeira_dk, 0, 8, W, 2)
    for x in range(2, W, 6):
        R(s, shade(madeira, 1.2), x, 2, 3, 3)
    R(s, shade(parede, 1.03), 0, 10, 2, H - 10)
    R(s, sombra, W - 2, 10, 2, H - 10)
    for x in (10, 46, 82):                                  # andar de cima: janelas com floreira
        R(s, vinho, x - 1, 16, 22, 24)
        R(s, LIT if night else (172, 210, 238), x + 1, 18, 18, 20)
        R(s, (210, 234, 250) if not night else (255, 236, 170), x + 1, 18, 6, 2)
        R(s, vinho, x + 9, 18, 2, 20)
        R(s, vinho, x + 1, 27, 18, 1)
        R(s, madeira_dk, x - 2, 40, 24, 4)
        R(s, (70, 146, 74), x - 1, 37, 22, 4)
        for fx in range(x, x + 20, 4):
            P(s, (255, 130, 170) if fx % 8 else (255, 230, 120), fx + 1, 38)
    R(s, madeira_dk, 24, 46, 64, 13)                        # placa de madeira (texto em draw_label)
    R(s, madeira, 25, 47, 62, 11)
    R(s, (214, 170, 96), 25, 47, 62, 1)
    lantern(s, 17, 48, night); lantern(s, 91, 48, night)
    awning(s, 0, 61, W, ROXO, (250, 246, 255), 10, 8, parede)
    for (x, w) in ((6, 52), (84, 24)):                      # vitrines com plantas
        R(s, madeira_dk, x - 1, 78, w + 2, 24)
        R(s, LIT if night else (168, 206, 232), x, 79, w, 20)
        R(s, (220, 238, 250) if not night else (255, 240, 190), x, 79, w, 2)
        for k in range(x + 12, x + w - 2, 13):
            R(s, madeira_dk, k, 79, 1, 20)
        R(s, madeira, x - 2, 99, w + 4, 3)
        for k in range(x, x + w - 6, 9):
            vaso(s, k, 92)
    R(s, madeira_dk, 63, 80, 18, 32)                         # porta (coluna 4 = 64..80)
    R(s, madeira, 65, 82, 14, 30)
    R(s, LIT if night else (176, 214, 236), 67, 85, 10, 11)
    R(s, (214, 170, 96), 76, 99, 2, 2)
    R(s, (98, 90, 96), 0, H - 2, W, 2)
    return s


def _catco(W, H, night):
    r = random.Random("catco")
    corpo, moldura = (34, 56, 98), (22, 38, 70)
    vidro = (62, 92, 140)
    s = new(W, H)
    R(s, corpo, 0, 10, W, H - 10)
    R(s, shade(corpo, 0.8), 0, 8, W, 3)
    R(s, (220, 230, 240), 4, 2, W - 8, 7)                    # coroa branca (o logo vem por cima)
    R(s, shade(corpo, 1.25), 0, 10, 2, H - 10)
    R(s, shade(corpo, 0.72), W - 2, 10, 2, H - 10)
    _janelas(s, 6, 16, W - 6, H - 52, 6, 7, 4, 4, vidro, moldura, 0.55 if night else 0.06, r)
    R(s, (28, 46, 82), 0, H - 50, W, 50)
    R(s, (236, 242, 250), 4, H - 45, W - 8, 13)              # faixa branca do letreiro CATCO
    R(s, (200, 214, 232), 4, H - 33, W - 8, 1)
    for lado in (-1, 1):
        x = 72 + (14 if lado > 0 else -14 - 34)
        R(s, (18, 30, 56), x, H - 26, 34, 22)
        R(s, LIT if night else (90, 128, 178), x + 1, H - 25, 32, 20)
        R(s, (130, 166, 210) if not night else (255, 246, 210), x + 1, H - 25, 32, 2)
        for k in range(1, 3):
            R(s, (18, 30, 56), x + k * 11, H - 25, 1, 20)
    R(s, (18, 30, 56), 61, H - 27, 22, 27)                   # porta (tile da porta = 64..80)
    R(s, LIT if night else (160, 200, 236), 63, H - 25, 18, 25)
    R(s, (220, 236, 250), 63, H - 25, 3, 25)
    R(s, (18, 30, 56), 71, H - 25, 2, 25)
    R(s, (236, 242, 250), 58, H - 30, 28, 2)
    R(s, (96, 90, 110), 58, H - 3, 28, 3)
    return s


def _books(W, H, night):
    """Bayside Books: sobrado de tijolinho, janelas brancas com floreira, toldo verde e vitrine de livros."""
    r = random.Random("books")
    tijolo, argamassa = (156, 72, 56), (122, 58, 48)
    verde, creme, madeira = (36, 96, 70), (240, 230, 200), (70, 46, 34)
    s = new(W, H)
    bricks(s, 0, 8, W, H - 8, tijolo, argamassa)
    cornice(s, 2, W, (78, 56, 46), 7)
    R(s, (60, 42, 34), 0, 0, W, 3)
    for y in (16, 42):                                      # dois andares de janelas com arco reto
        for x in (10, 40, 70, 100):
            R(s, (214, 200, 180), x - 3, y - 4, 24, 3)       # verga de pedra
            window(s, x, y, 18, 18, (238, 234, 226), (150, 196, 226), night and r.random() < 0.6,
                   sill=(214, 200, 180), box=(255, 120, 150) if y == 42 else None)
    R(s, verde, 4, 68, W - 8, 13)                           # placa verde (texto em draw_label)
    R(s, (214, 172, 84), 4, 68, W - 8, 1); R(s, (214, 172, 84), 4, 80, W - 8, 1)
    lantern(s, 2, 70, night)
    awning(s, 0, 83, W, verde, creme, 9, 8, tijolo)
    shopfront(s, 6, 98, 96, 24, madeira, night, goods=[(200, 60, 60), (60, 100, 170), (230, 200, 80),
                                                         (90, 150, 90), (150, 90, 160)], seed=3)
    door(s, 112, 98, 14, 30, madeira, (96, 64, 44), night)
    vaso(s, 104, 119)
    side_light(s, W, H, 8)
    return s


def _market(W, H, night):
    """Mercado Central: fachada creme, venezianas verdes, toldo amarelo e caixotes de frutas na vitrine."""
    r = random.Random("market")
    parede, verde = (246, 234, 204), (70, 122, 72)
    madeira = (110, 78, 50)
    s = new(W, H)
    R(s, parede, 0, 8, W, H - 8)
    for y in range(12, H - 40, 4):
        R(s, shade(parede, 0.97), 0, y, W, 1)
    cornice(s, 2, W, verde, 7)
    R(s, shade(verde, 0.7), 0, 0, W, 3)
    for x in (14, 54, 94):
        window(s, x, 18, 18, 22, (236, 232, 220), (160, 204, 230), night and r.random() < 0.6,
               sill=(220, 210, 190), shutter=verde, box=(255, 200, 80))
    R(s, verde, 6, 52, W - 12, 13)                          # placa (texto em draw_label)
    R(s, (240, 210, 110), 6, 52, W - 12, 1); R(s, (240, 210, 110), 6, 64, W - 12, 1)
    awning(s, 0, 70, W, (250, 196, 60), (250, 250, 240), 10, 8, parede)
    for (x, w) in ((4, 40), (68, 56)):                      # vitrines com bancada de frutas
        shopfront(s, x, 88, w, 20, madeira, night)
        R(s, madeira, x - 1, 108, w + 2, 12)
        R(s, shade(madeira, 1.2), x - 1, 108, w + 2, 1)
        for fx in range(x, x + w - 4, 5):
            c = r.choice([(230, 60, 50), (250, 160, 40), (120, 200, 80), (240, 220, 80), (160, 80, 170)])
            R(s, (150, 108, 70), fx, 111, 5, 6)
            R(s, c, fx + 1, 109, 3, 3)
            P(s, shade(c, 1.3), fx + 1, 109)
    door(s, 49, 92, 14, 36, (60, 46, 36), (90, 66, 46), night)
    side_light(s, W, H, 8)
    return s


def _trattoria(W, H, night):
    """Ricci Trattoria: telhado de telha, reboco quente, venezianas verdes com gerânios e toldo tricolor."""
    r = random.Random("trattoria")
    parede, telha = (238, 204, 164), (186, 92, 60)
    verde, vermelho = (40, 120, 70), (196, 46, 54)
    madeira = (104, 62, 40)
    s = new(W, H)
    R(s, parede, 0, 14, W, H - 14)
    for y in range(16, H - 40, 5):                           # reboco irregular
        for x in range(r.randrange(0, 9), W, 13):
            R(s, shade(parede, 0.95), x, y, r.randrange(3, 7), 1)
    for y in range(0, 14, 3):                               # telhas em escama
        for x in range(-(y % 6), W, 6):
            R(s, telha, x, y, 6, 3)
            R(s, shade(telha, 1.18), x + 1, y, 4, 1)
            R(s, shade(telha, 0.75), x + 5, y, 1, 3)
    R(s, shade(telha, 0.6), 0, 14, W, 2)
    for yy in range(18, H - 6, 6):
        R(s, (220, 206, 186), 0, yy, 5, 4); R(s, (220, 206, 186), W - 5, yy, 5, 4)
    for x in (14, 62, 110):
        window(s, x, 22, 18, 20, (232, 222, 200), (170, 206, 230), night and r.random() < 0.7,
               shutter=verde, box=vermelho)
    R(s, (246, 238, 220), 16, 54, W - 32, 13)               # placa creme (texto em draw_label)
    R(s, verde, 16, 54, (W - 32) // 3, 2)
    R(s, (250, 250, 250), 16 + (W - 32) // 3, 54, (W - 32) // 3, 2)
    R(s, vermelho, 16 + 2 * (W - 32) // 3, 54, W - 32 - 2 * ((W - 32) // 3), 2)
    lantern(s, 8, 56, night); lantern(s, W - 12, 56, night)
    for i, x in enumerate(range(0, W, 6)):                  # toldo verde-branco-vermelho
        col = (verde, (250, 250, 250), vermelho)[i % 3]
        R(s, col, x, 72, 6, 9)
        R(s, shade(col, 0.8), x, 72, 6, 2)
        R(s, col, x + 1, 81, 4, 2)
    R(s, shade(parede, 0.78), 0, 84, W, 2)
    # janelão em arco com mesas aparecendo
    R(s, madeira, 7, 90, 96, 32)
    R(s, LIT if night else (180, 212, 232), 9, 92, 92, 28)
    for k in range(9, 101, 23):
        R(s, madeira, k + 22, 92, 1, 28)
    for tx in (16, 40, 64, 88):
        R(s, (246, 240, 236), tx, 110, 10, 3)
        R(s, vermelho, tx + 1, 111, 8, 1)
        R(s, (90, 56, 40), tx + 4, 113, 2, 6)
    R(s, shade(madeira, 1.3), 6, 122, 98, 2)
    door(s, 112, 94, 16, 34, (80, 48, 32), madeira, night)
    R(s, madeira, 110, 92, 20, 2)
    vaso(s, 0, 119, (230, 60, 60)); vaso(s, 134, 119, (230, 60, 60))
    side_light(s, W, H, 14)
    return s


def _bar(W, H, night):
    """Noonan's: tijolo escuro, letreiro neon (texto em draw_label), janelas âmbar e porta vermelha."""
    r = random.Random("bar")
    tijolo, argamassa = (82, 52, 54), (58, 38, 42)
    s = new(W, H)
    bricks(s, 0, 8, W, H - 8, tijolo, argamassa)
    cornice(s, 2, W, (40, 30, 34), 7)
    R(s, (28, 20, 24), 0, 0, W, 3)
    for x in (10, 44, 78, 108):
        window(s, x, 18, 12, 18, (40, 30, 30), (100, 120, 150), night and r.random() < 0.7,
               sill=(120, 100, 96))
    for x in (10, 44, 78, 108):
        window(s, x, 50, 12, 14, (40, 30, 30), (100, 120, 150), night and r.random() < 0.5)
    R(s, (24, 16, 20), 6, H - 46, W - 12, 15)               # painel do neon
    R(s, (60, 40, 50), 6, H - 46, W - 12, 1)
    R(s, (36, 26, 30), 0, H - 30, W, 30)
    shopfront(s, 6, H - 26, 40, 18, (30, 20, 20), True, glass=(255, 190, 110))
    shopfront(s, 52, H - 26, 40, 18, (30, 20, 20), True, glass=(255, 190, 110))
    R(s, (255, 90, 150), 58, H - 22, 14, 4)                 # "OPEN" em neon (barrinhas)
    R(s, (255, 170, 200), 59, H - 21, 12, 2)
    door(s, 112, H - 28, 14, 28, (30, 20, 20), (130, 40, 52), night)
    lantern(s, 104, H - 26, True)
    side_light(s, W, H, 8)
    return s


def _cinema(W, H, night, t=0):
    """Cine National: fachada art déco roxa, frisos dourados, marquise com lâmpadas e cartazes."""
    corpo, frisos = (66, 42, 98), (222, 186, 96)
    s = new(W, H)
    R(s, corpo, 0, 10, W, H - 10)
    R(s, (44, 28, 66), 0, 4, W, 7)
    R(s, frisos, 0, 4, W, 1); R(s, frisos, 0, 10, W, 1)
    for x in (W // 2 - 16, W // 2 + 8):                      # torrezinhas em degrau
        R(s, (44, 28, 66), x, 0, 8, 5); R(s, frisos, x, 0, 8, 1)
    for x in range(6, W - 6, 12):                           # pilastras com frisos
        R(s, shade(corpo, 1.18), x, 14, 6, H - 72)
        R(s, shade(corpo, 0.8), x + 5, 14, 1, H - 72)
        R(s, frisos, x, 14, 6, 1)
    for x in range(12, W - 12, 12):                         # janelinhas entre as pilastras
        window(s, x + 1, 22, 4, 30, (40, 26, 60), (120, 100, 170), night, cross=False)
    # marquise iluminada
    R(s, (40, 26, 60), 2, H - 58, W - 4, 24)
    R(s, (240, 220, 140), 4, H - 56, W - 8, 20)
    R(s, (30, 20, 40), 6, H - 53, W - 12, 14)
    for x in range(5, W - 5, 4):
        on = night or (x // 4) % 2 == 0
        P(s, (255, 244, 180) if on else (200, 176, 100), x, H - 57)
        P(s, (255, 244, 180) if on else (200, 176, 100), x, H - 36)
    R(s, shade(corpo, 0.7), 0, H - 33, W, 3)
    for x in (6, W - 26):                                   # cartazes
        R(s, frisos, x - 1, H - 31, 22, 26)
        R(s, (240, 236, 226), x, H - 30, 20, 24)
        R(s, (200, 60, 60) if x < 40 else (60, 110, 190), x + 2, H - 28, 16, 14)
        R(s, (40, 30, 40), x + 3, H - 12, 14, 2)
    R(s, (40, 26, 60), 61, H - 30, 38, 30)                  # porta dupla (tile da porta = 64..80)
    for dx in (63, 81):
        R(s, LIT if night else (170, 140, 210), dx, H - 28, 16, 28)
        R(s, (210, 190, 240) if not night else (255, 240, 200), dx, H - 28, 3, 28)
    R(s, frisos, 61, H - 31, 38, 1)
    side_light(s, W, H, 10)
    return s


def _apartments(W, H, night):
    """Apartamentos Bayside: reboco bege, sacadas com grade e plantas, marquise na entrada."""
    r = random.Random("apartments")
    parede = (214, 196, 166)
    s = new(W, H)
    R(s, parede, 0, 8, W, H - 8)
    for y in range(10, H, 4):
        R(s, shade(parede, 0.97), 0, y, W, 1)
    cornice(s, 2, W, (150, 128, 104), 7)
    for y in range(18, H - 34, 22):
        for x in (8, 46, 86):
            window(s, x, y, 14, 14, (110, 96, 84), (160, 200, 226), night and r.random() < 0.55)
            R(s, (90, 80, 76), x - 3, y + 15, 20, 2)               # sacada
            for gx in range(x - 3, x + 17, 3):
                R(s, (90, 80, 76), gx, y + 11, 1, 4)
            R(s, (90, 80, 76), x - 3, y + 11, 20, 1)
            if r.random() < 0.6:
                R(s, (70, 146, 74), x - 2, y + 12, 5, 3)
                P(s, r.choice([(255, 130, 170), (255, 220, 110), (200, 150, 255)]), x - 1, y + 12)
    R(s, (120, 100, 80), 54, H - 32, 36, 4)                  # marquise
    R(s, shade((120, 100, 80), 1.3), 54, H - 32, 36, 1)
    door(s, 64, H - 28, 16, 28, (80, 64, 50), (110, 84, 60), night)
    lantern(s, 56, H - 24, night); lantern(s, 84, H - 24, night)
    vaso(s, 4, H - 10); vaso(s, W - 12, H - 10)
    side_light(s, W, H, 8)
    return s


def _home(W, H, night):
    """Residencial Luthor: prédio elegante de tijolo com base de pedra, sacadas e marquise roxa."""
    r = random.Random("home")
    tijolo, argamassa = (176, 120, 96), (146, 98, 80)
    pedra = (214, 206, 196)
    s = new(W, H)
    bricks(s, 0, 12, W, H - 12, tijolo, argamassa)
    R(s, (92, 66, 82), 0, 4, W, 9)                          # faixa do nome (texto em draw_label)
    R(s, (120, 90, 108), 0, 4, W, 1)
    R(s, (72, 52, 66), 0, 12, W, 2)
    R(s, (200, 200, 210), 6, 0, 10, 5); R(s, (120, 120, 130), 8, 1, 6, 3)
    for y in range(20, H - 40, 18):
        for x in (8, 36, 64, 92, 120):
            if x + 16 > W:
                continue
            window(s, x, y, 14, 12, (238, 232, 226), (150, 196, 228), night and r.random() < 0.6,
                   sill=pedra, box=(255, 130, 170) if (x + y) % 3 == 0 else None)
    R(s, pedra, 0, H - 34, W, 34)                           # base de pedra
    for yy in range(H - 34, H, 6):
        R(s, shade(pedra, 0.9), 0, yy, W, 1)
        for xx in range((yy // 6) % 2 * 8, W, 16):
            R(s, shade(pedra, 0.9), xx, yy, 1, 6)
    R(s, ROXO, 56, H - 34, 32, 4)                           # marquise roxa da Luthor
    R(s, ROXO_2, 56, H - 34, 32, 1)
    door(s, 64, H - 29, 16, 29, (60, 46, 50), (96, 64, 52), night)
    for x in (10, 100):
        window(s, x, H - 26, 26, 16, (90, 80, 84), (150, 196, 228), night, sill=pedra)
    lantern(s, 58, H - 26, night); lantern(s, 82, H - 26, night)
    vaso(s, 44, H - 10, (200, 140, 255)); vaso(s, 92, H - 10, (200, 140, 255))
    side_light(s, W, H, 12)
    return s


def _arched(s, x, y, w, h, frame, glass, lit, shutter=None, box=None):
    """Janela em arco (alta), com venezianas e floreira opcionais."""
    if shutter:
        for sx in (x - 5, x + w + 2):
            R(s, shutter, sx, y + 2, 3, h - 2)
            for yy in range(y + 3, y + h, 2):
                R(s, shade(shutter, 0.8), sx, yy, 3, 1)
    r = w // 2
    pygame.draw.circle(s, frame, (x + r, y + r), r + 1, draw_top_left=True, draw_top_right=True)
    R(s, frame, x - 1, y + r, w + 2, h - r + 1)
    g = LIT if lit else glass
    pygame.draw.circle(s, g, (x + r, y + r), r, draw_top_left=True, draw_top_right=True)
    R(s, g, x, y + r, w, h - r)
    if not lit:
        R(s, shade(glass, 0.84), x, y + h - 2, w, 2)
        for i in range(2, min(w, h) - 2):
            P(s, shade(glass, 1.18), x + w - 2 - i // 2, y + r + i)
    R(s, frame, x + r, y + 1, 1, h - 1)
    R(s, frame, x, y + r + 2, w, 1)
    R(s, (226, 214, 190), x - 2, y + h, w + 4, 2)           # peitoril de pedra
    if box:
        R(s, (110, 70, 46), x - 2, y + h + 1, w + 4, 3)
        R(s, (64, 138, 70), x - 2, y + h - 1, w + 4, 2)
        for fx in range(x - 1, x + w + 2, 3):
            P(s, box if (fx // 3) % 2 else (255, 236, 140), fx, y + h - 1)


def _ricci(W, H, night):
    """Gruppo Ricci: palácio italiano de reboco creme, telhado de telha, frontão com brasão dourado,
    janelas em arco com venezianas verdes, sacada com bandeiras e portão em arco na base de pedra."""
    r = random.Random("ricci")
    reboco, reboco_dk, reboco_lt = (240, 226, 200), (208, 190, 162), (252, 244, 226)
    telha, telha_dk = (186, 96, 64), (138, 70, 48)
    verde, ouro = (58, 108, 72), (214, 172, 84)
    pedra = (200, 186, 162)
    s = new(W, H)
    top = 16
    R(s, reboco, 0, top, W, H - top)
    for y in range(top + 4, H - 36, 6):                     # reboco com juntas leves
        R(s, shade(reboco, 0.97), 0, y, W, 1)
    for y in range(0, top - 4, 3):                          # telhas em escama
        for x in range(-(y % 6), W, 6):
            R(s, telha, x, y + 2, 6, 3)
            R(s, shade(telha, 1.2), x + 1, y + 2, 4, 1)
            R(s, telha_dk, x + 5, y + 2, 1, 3)
    R(s, reboco_lt, 0, top - 4, W, 3)                       # cornija com mísulas
    R(s, reboco_dk, 0, top - 1, W, 2)
    for x in range(3, W, 8):
        R(s, reboco_dk, x, top + 1, 3, 3)
        P(s, reboco_lt, x, top + 1)
    cx = W // 2
    pygame.draw.polygon(s, reboco_lt, [(cx - 22, top - 2), (cx, top - 16), (cx + 22, top - 2)])   # frontão
    pygame.draw.polygon(s, reboco_dk, [(cx - 22, top - 2), (cx, top - 16), (cx + 22, top - 2)], 1)
    pygame.draw.circle(s, ouro, (cx, top - 7), 4)
    pygame.draw.circle(s, verde, (cx, top - 7), 2)
    P(s, (255, 236, 170), cx - 2, top - 9)
    for x in (0, W - 6):                                    # cunhais de pedra nas quinas
        for yy in range(top + 2, H - 32, 6):
            R(s, pedra, x, yy, 6, 5)
            R(s, shade(pedra, 1.1), x, yy, 6, 1)
    cols = [12, 36, W - 48, W - 24]
    for row_y in (top + 10, top + 44, top + 78):
        if row_y + 26 > H - 50:
            continue
        for x in cols:
            _arched(s, x, row_y, 12, 22, reboco_dk, (150, 196, 222), night and r.random() < 0.65,
                    shutter=verde, box=(230, 70, 80) if row_y != top + 10 else None)
    by = top + 44                                           # sacada central com bandeirinhas da Itália
    _arched(s, cx - 9, by - 2, 18, 26, reboco_dk, (150, 196, 222), night)
    R(s, reboco_dk, cx - 16, by + 24, 32, 3)
    R(s, shade(reboco_dk, 0.8), cx - 16, by + 27, 32, 1)
    for x in range(cx - 15, cx + 16, 3):
        R(s, (52, 48, 56), x, by + 17, 1, 7)
    R(s, (52, 48, 56), cx - 16, by + 16, 32, 1)
    for k, c in enumerate(((60, 140, 80), (244, 244, 240), (200, 50, 56))):
        R(s, c, cx - 20 + k * 3, by - 10, 3, 7)
        R(s, c, cx + 11 + k * 3, by - 10, 3, 7)
    R(s, (90, 80, 70), cx - 21, by - 12, 1, 13); R(s, (90, 80, 70), cx + 20, by - 12, 1, 13)
    _arched(s, cx - 9, top + 10, 18, 22, reboco_dk, (150, 196, 222), night and r.random() < 0.65)
    sy = H - 48                                             # faixa verde do nome com filetes dourados
    R(s, verde, 6, sy, W - 12, 13)
    R(s, ouro, 6, sy, W - 12, 1); R(s, ouro, 6, sy + 12, W - 12, 1)
    R(s, shade(verde, 0.7), 6, sy + 13, W - 12, 1)
    R(s, pedra, 0, H - 34, W, 34)                           # base de pedra rústica
    for yy in range(H - 34, H, 6):
        R(s, shade(pedra, 0.86), 0, yy, W, 1)
        for xx in range((yy // 6) % 2 * 9, W, 18):
            R(s, shade(pedra, 0.86), xx, yy, 1, 6)
            R(s, shade(pedra, 1.08), xx + 1, yy + 1, 16, 1)
    dw = 18                                                 # portão em arco (tile da porta = 64..80)
    dx0 = cx - dw // 2
    pygame.draw.circle(s, (80, 54, 38), (cx, H - 24), dw // 2 + 3, draw_top_left=True, draw_top_right=True)
    R(s, (80, 54, 38), dx0 - 3, H - 24, dw + 6, 24)
    pygame.draw.circle(s, (134, 88, 56), (cx, H - 24), dw // 2, draw_top_left=True, draw_top_right=True)
    R(s, (134, 88, 56), dx0, H - 24, dw, 24)
    if night:
        pygame.draw.circle(s, LIT, (cx, H - 24), dw // 2 - 3, draw_top_left=True, draw_top_right=True)
    R(s, (92, 60, 40), cx, H - 32, 1, 32)
    for yy in (H - 20, H - 10):
        R(s, shade((134, 88, 56), 0.8), dx0, yy, dw, 1)
    P(s, ouro, cx - 3, H - 13); P(s, ouro, cx + 2, H - 13)
    R(s, ouro, cx - 1, H - 35, 3, 3)                        # chave do arco
    lantern(s, cx - 18, H - 30, night); lantern(s, cx + 14, H - 30, night)
    for x in (12, W - 24):                                  # janelas gradeadas do térreo
        window(s, x, H - 26, 12, 14, (80, 54, 38), (150, 196, 222), night, sill=(226, 214, 190))
        for gx in range(x + 2, x + 12, 3):
            R(s, (52, 48, 56), gx, H - 26, 1, 14)
    for x in (cx - 34, cx + 26):                            # limoeiros em vasos de terracota
        R(s, (166, 92, 62), x, H - 10, 8, 9)
        R(s, (196, 112, 76), x - 1, H - 11, 10, 2)
        R(s, (110, 70, 46), x + 3, H - 18, 2, 8)
        pygame.draw.circle(s, (64, 128, 66), (x + 4, H - 21), 6)
        pygame.draw.circle(s, (96, 160, 84), (x + 2, H - 23), 3)
        for (lx, ly) in ((x + 1, H - 20), (x + 6, H - 24), (x + 5, H - 18), (x + 2, H - 25)):
            P(s, (250, 220, 70), lx, ly)
    side_light(s, W, H, top)
    return s


def _hospital(W, H, night):
    """Conti Moretti Hospitais (papel, verde #123f35 e cobre #b77b65): alas com faixas de janelas e brises
    de cobre, torre de vidro verde no meio, heliponto e marquise verde na entrada."""
    r = random.Random("hospital")
    papel, verde, verde2, cobre = (246, 243, 236), (18, 63, 53), (29, 89, 74), (183, 123, 101)
    vidro = (176, 210, 226)
    s = new(W, H)
    R(s, papel, 0, 16, W, H - 16)
    for y in range(18, H - 40, 9):                          # placas da fachada
        R(s, shade(papel, 0.96), 0, y, W, 1)
    R(s, verde, 0, 2, W, 13)                                # faixa do nome no topo
    R(s, shade(verde, 1.35), 0, 2, W, 1)
    R(s, cobre, 0, 15, W, 2)
    R(s, (200, 200, 206), 6, 0, 22, 2)                      # heliponto e antena no telhado
    R(s, (230, 70, 60), 14, 0, 1, 2)
    R(s, (150, 150, 160), W - 16, 0, 2, 2)
    for y in range(24, H - 46, 14):                         # alas: faixas de janela e brises de cobre
        for (x0, x1) in ((4, W // 2 - 30), (W // 2 + 30, W - 4)):
            R(s, (200, 196, 190), x0 - 1, y - 1, x1 - x0 + 2, 10)
            for x in range(x0, x1 - 5, 7):
                lit = night and r.random() < 0.6
                R(s, LIT if lit else vidro, x, y, 6, 8)
                if not lit:
                    R(s, shade(vidro, 1.18), x, y, 6, 1)
                    P(s, shade(vidro, 1.3), x + 4, y + 2)
                    R(s, shade(vidro, 0.86), x, y + 7, 6, 1)
            R(s, cobre, x0 - 1, y + 9, x1 - x0 + 2, 2)
            R(s, shade(cobre, 1.2), x0 - 1, y + 9, x1 - x0 + 2, 1)
    tx0, tx1 = W // 2 - 26, W // 2 + 26                     # torre central de vidro verde
    R(s, verde2, tx0, 18, tx1 - tx0, H - 54)
    R(s, shade(verde2, 1.25), tx0, 18, 2, H - 54)
    R(s, shade(verde2, 0.7), tx1 - 2, 18, 2, H - 54)
    for yy in range(21, H - 72, 7):
        for xx in range(tx0 + 3, tx1 - 4, 7):
            lit = night and r.random() < 0.55
            R(s, LIT if lit else (120, 178, 160), xx, yy, 5, 5)
            if not lit:
                P(s, (170, 214, 196), xx, yy)
    for xx in range(tx0 + 2, tx1, 7):
        R(s, shade(verde2, 0.8), xx, 18, 1, H - 72)
    pygame.draw.circle(s, papel, (W // 2, H - 56), 12)      # medalhão do logo
    pygame.draw.circle(s, cobre, (W // 2, H - 56), 12, 1)
    R(s, verde, 2, H - 42, W - 4, 13)                       # marquise verde com o nome e colunas
    R(s, shade(verde, 1.35), 2, H - 42, W - 4, 1)
    R(s, cobre, 2, H - 29, W - 4, 2)
    R(s, shade(papel, 0.8), 2, H - 27, W - 4, 2)
    for x in (10, 44, W - 48, W - 14):
        R(s, papel, x, H - 27, 4, 27)
        R(s, shade(papel, 0.85), x + 3, H - 27, 1, 27)
    for (x, w) in ((16, 26), (W - 42, 26)):                 # vidraças
        shopfront(s, x, H - 24, w, 20, verde2, night, glass=(176, 214, 210))
    R(s, (30, 46, 40), W // 2 - 16, H - 25, 32, 25)         # porta automática (tile 64..80)
    for dx in (W // 2 - 14, W // 2 + 1):
        R(s, LIT if night else (170, 214, 210), dx, H - 23, 13, 23)
        R(s, (220, 240, 236) if not night else (255, 244, 210), dx, H - 23, 2, 23)
    R(s, (230, 70, 60), W // 2 - 2, H - 27, 4, 1)
    for x in (46, W - 58):                                  # canteiros com arbusto
        R(s, (190, 186, 180), x, H - 8, 12, 8)
        pygame.draw.circle(s, (70, 132, 82), (x + 6, H - 10), 6)
        pygame.draw.circle(s, (100, 162, 100), (x + 4, H - 12), 3)
    side_light(s, W, H, 16)
    return s


def _marina(W, H, night):
    """Marina Luthor: clube náutico de tábuas brancas, telhado azul-marinho com bandeira roxa, escotilhas,
    placa azul com filete dourado, toldo listrado, boias, lanternas de navio e âncora."""
    navy, navy_lt = (26, 44, 84), (52, 82, 140)
    branco, branco_dk = (244, 246, 250), (208, 214, 226)
    ouro = (214, 172, 84)
    s = new(W, H)
    top = 16
    roof = [(0, top + 4), (12, top - 10), (W - 12, top - 10), (W, top + 4)]
    pygame.draw.polygon(s, navy, roof)
    for y in range(top - 8, top + 3, 3):                    # fiadas do telhado
        pygame.draw.line(s, shade(navy, 1.2), (14 - (y - top + 10), y), (W - 14 + (y - top + 10), y))
    R(s, navy_lt, 12, top - 10, W - 24, 2)
    R(s, branco, 0, top + 2, W, 3)
    cx = W // 2
    R(s, (90, 90, 100), cx - 1, 0, 2, top - 8)              # mastro com a bandeira roxa da Luthor
    R(s, ROXO, cx + 1, 1, 10, 6)
    R(s, ROXO_2, cx + 1, 1, 10, 2)
    R(s, branco, 0, top + 5, W, H - top - 5)                # tábuas brancas
    for y in range(top + 7, H - 30, 3):
        R(s, branco_dk, 0, y, W, 1)
    for k in range(6, W - 10, 22):                          # escotilhas no andar de cima
        x = k + 5
        pygame.draw.circle(s, navy, (x, top + 13), 6)
        pygame.draw.circle(s, ouro, (x, top + 13), 6, 1)
        pygame.draw.circle(s, LIT if night else (150, 200, 230), (x, top + 13), 4)
        if not night:
            P(s, (255, 255, 255), x - 1, top + 11)
    R(s, navy, 6, top + 24, W - 12, 12)                     # placa (texto em draw_label)
    R(s, ouro, 6, top + 24, W - 12, 1); R(s, ouro, 6, top + 35, W - 12, 1)
    R(s, navy, 0, H - 34, W, 3)                             # faixa azul
    R(s, navy_lt, 0, H - 34, W, 1)
    for i in range(0, W, 8):                                # toldo azul e branco na fachada toda
        col = navy_lt if (i // 8) % 2 == 0 else branco
        R(s, col, i, H - 31, 8, 6)
        R(s, shade(col, 0.8), i, H - 31, 8, 1)
        R(s, col, i + 1, H - 25, 6, 2)
    for x in list(range(6, cx - 16, 13)) + list(range(cx + 18, W - 8, 13)):   # vidraças
        R(s, navy, x - 1, H - 22, 12, 18)
        R(s, LIT if night else (150, 200, 230), x, H - 21, 10, 16)
        if not night:
            R(s, (200, 228, 244), x + 2, H - 20, 2, 10)
    R(s, navy, cx - 11, H - 23, 22, 23)                     # porta dupla de vidro (tile 64..80)
    for dx in (cx - 9, cx + 1):
        R(s, LIT if night else (150, 200, 230), dx, H - 21, 8, 21)
    R(s, ouro, cx - 2, H - 12, 1, 2); R(s, ouro, cx + 1, H - 12, 1, 2)
    for x in (cx - 26, cx + 22):                            # boias salva-vidas
        pygame.draw.circle(s, (230, 70, 60), (x, H - 41), 5)
        pygame.draw.circle(s, branco, (x, H - 41), 5, 2)
        pygame.draw.circle(s, branco, (x, H - 41), 2)
    for x in (cx - 17, cx + 14):                            # lanternas de navio
        R(s, (40, 40, 50), x, H - 22, 4, 1)
        R(s, LIT if night else (230, 214, 170), x, H - 21, 4, 4)
        R(s, (40, 40, 50), x, H - 17, 4, 1)
    ax = W - 14                                             # âncora encostada na parede
    R(s, (60, 64, 76), ax + 3, H - 18, 2, 14)
    R(s, (60, 64, 76), ax, H - 15, 8, 1)
    pygame.draw.circle(s, (60, 64, 76), (ax + 4, H - 19), 2, 1)
    R(s, (60, 64, 76), ax, H - 6, 8, 2)
    P(s, (60, 64, 76), ax - 1, H - 7); P(s, (60, 64, 76), ax + 8, H - 7)
    for x in range(0, W, 6):                                # corda náutica na base
        R(s, (196, 166, 116), x, H - 3, 4, 2)
        P(s, shade((196, 166, 116), 0.8), x + 4, H - 2)
    side_light(s, W, H, top + 5)
    return s


BUILDERS = {"tower": _torre, "cafe": _cafe, "catco": _catco, "books": _books, "market": _market,
            "trattoria": _trattoria, "bar": _bar, "cinema": _cinema, "apartments": _apartments, "home": _home,
            "ricci": _ricci, "hospital": _hospital, "marina": _marina}
_prev_building_sprite = art.building_sprite


def building_sprite(style, w, h, extra, night=False):
    fn = BUILDERS.get(style)
    if fn is None:
        return _prev_building_sprite(style, w, h, extra, night)
    return art.cached(("bld+", style, w, h, extra, night), lambda: art.up(fn(w * TS, (h + extra) * TS, night)))


art.building_sprite = building_sprite


def draw_label(g, surf, b, spr, x, y, night):
    """Letreiros dos prédios novos. Devolve True se escreveu (senão o Game usa os letreiros antigos)."""
    if b.style not in BUILDERS:
        return False
    cx = x + spr.get_width() // 2
    H = spr.get_height()
    S = SCALE
    if b.style == "tower":
        ui.text(surf, "LUTHOR CORP", (cx, y + H - 49 * S + 4), 26, (223, 197, 255), bold=True, center=True)
    elif b.style == "catco":
        logo = art.load_image("catco.png", (28 * S, 28 * S))
        if logo:
            surf.blit(logo, (cx - 14 * S, y - 6 * S))
        ui.text(surf, "CATCO", (cx, y + H - 45 * S + 3), 24, (30, 60, 104), bold=True, center=True, shadow=False)
    elif b.style == "cafe":
        ui.text(surf, "GRÃO NOBRE", (cx, y + 47 * S - 3), 19, (255, 226, 150), bold=True, center=True)
    elif b.style == "books":
        ui.text(surf, "BAYSIDE BOOKS", (cx, y + 68 * S - 1), 17, (250, 226, 150), bold=True, center=True)
    elif b.style == "market":
        ui.text(surf, "MERCADO CENTRAL", (cx, y + 52 * S - 1), 17, (255, 240, 190), bold=True, center=True)
    elif b.style == "trattoria":
        ui.text(surf, "RICCI TRATTORIA", (cx, y + 56 * S - 2), 17, (150, 40, 46), bold=True, center=True, shadow=False)
    elif b.style == "bar":
        col = (255, 90, 150) if night or int(g.t * 2) % 7 else (120, 60, 90)
        ui.text(surf, "NOONAN'S", (cx, y + H - 46 * S + 3), 24, col, bold=True, center=True)
    elif b.style == "cinema":
        ui.text(surf, "CINE NATIONAL", (cx, y + H - 53 * S + 3), 20, (255, 230, 140), bold=True, center=True)
    elif b.style == "home":
        ui.text(surf, "RESIDENCIAL LUTHOR", (cx, y + 5 * S - 1), 15, (250, 230, 220), bold=True, center=True)
    elif b.style == "ricci":
        ui.text(surf, "GRUPPO RICCI", (cx, y + H - 48 * S + 1), 18, (240, 214, 140), bold=True, center=True)
    elif b.style == "hospital":
        logo = art.load_image("cmh.png", (18 * S, 18 * S))
        if logo:
            surf.blit(logo, (cx - 9 * S, y + H - 56 * S - 9 * S))
        ui.text(surf, "CONTI MORETTI HOSPITAIS", (cx, y + 3 * S + 3), 17, (246, 243, 236), bold=True, center=True)
        ui.text(surf, "CONTI MORETTI", (cx, y + H - 42 * S + 2), 19, (246, 243, 236), bold=True, center=True)
    elif b.style == "marina":
        ui.text(surf, "MARINA LUTHOR", (cx, y + 40 * S + 1), 17, (240, 214, 140), bold=True, center=True)
    return True


# ---------------------------------------------------------------------------
# Objetos da rua
# ---------------------------------------------------------------------------
def _poste():
    """Poste de lanterna: haste fina, cúpula com vidro quente."""
    s = new(16, 44)
    ferro, luz = (34, 32, 44), (60, 56, 76)
    R(s, ferro, 7, 10, 2, 31)
    R(s, luz, 7, 10, 1, 31)
    R(s, ferro, 5, 39, 6, 2); R(s, ferro, 4, 41, 8, 3)
    R(s, luz, 4, 41, 8, 1)
    R(s, ferro, 6, 24, 4, 2)                                 # anel no meio da haste
    R(s, ferro, 4, 2, 8, 2)                                  # cúpula
    R(s, ferro, 6, 0, 4, 2)
    R(s, ferro, 4, 4, 1, 6); R(s, ferro, 11, 4, 1, 6)
    R(s, (255, 226, 150), 5, 4, 6, 6)
    R(s, (255, 246, 210), 6, 5, 2, 3)
    R(s, ferro, 4, 10, 8, 1)
    return s


def _mesa(c1=ROXO, c2=(250, 246, 255), toalha=(246, 244, 250), detalhe=(200, 60, 70)):
    """Mesinha redonda com toalha, duas cadeiras e guarda-sol listrado."""
    def make():
        s = new(32, 36)
        for i in range(6):
            cor = c1 if i % 2 == 0 else c2
            R(s, cor, 4 + i * 4, 6 - min(i, 5 - i), 4, 4 + min(i, 5 - i))
        R(s, shade(c1, 0.75), 4, 9, 24, 1)
        R(s, (210, 200, 220), 15, 0, 2, 3)
        R(s, (60, 52, 60), 15, 10, 2, 16)
        madeira = (120, 76, 46)
        R(s, madeira, 2, 22, 6, 2); R(s, madeira, 2, 24, 1, 8); R(s, madeira, 7, 24, 1, 8)
        R(s, madeira, 24, 22, 6, 2); R(s, madeira, 24, 24, 1, 8); R(s, madeira, 29, 24, 1, 8)
        R(s, shade(madeira, 0.8), 2, 18, 1, 5); R(s, shade(madeira, 0.8), 29, 18, 1, 5)
        R(s, toalha, 9, 21, 14, 4)
        R(s, shade(toalha, 0.86), 9, 24, 14, 1)
        R(s, detalhe, 13, 20, 2, 1)
        P(s, (255, 255, 255), 18, 20)
        R(s, (60, 52, 60), 15, 25, 2, 8)
        R(s, (60, 52, 60), 12, 33, 8, 2)
        return s
    return make


def _cavalete():
    """Cavalete com quadro-negro do cardápio."""
    s = new(16, 20)
    madeira = (122, 76, 46)
    R(s, madeira, 3, 2, 10, 15)
    R(s, (40, 46, 44), 4, 3, 8, 12)
    for y, w in ((5, 6), (8, 5), (11, 6)):
        R(s, (230, 230, 220), 5, y, w, 1)
    P(s, (255, 140, 180), 10, 8)
    R(s, shade(madeira, 0.8), 2, 16, 2, 4); R(s, shade(madeira, 0.8), 12, 16, 2, 4)
    R(s, shade(madeira, 1.2), 3, 2, 10, 1)
    return s


def _floreira(flores=((255, 130, 170), (255, 236, 140))):
    """Floreira comprida de madeira, cheia de folhas e flores."""
    def make():
        s = new(16, 16)
        madeira = (126, 84, 56)
        R(s, madeira, 1, 9, 14, 6)
        R(s, shade(madeira, 1.25), 1, 9, 14, 1)
        R(s, shade(madeira, 0.75), 1, 14, 14, 1)
        R(s, shade(madeira, 0.85), 5, 10, 1, 4); R(s, shade(madeira, 0.85), 10, 10, 1, 4)
        r = random.Random(sum(flores[0]))
        for x in range(1, 15):
            hgt = r.randrange(3, 6)
            R(s, (64, 138, 70), x, 9 - hgt, 1, hgt)
            P(s, (96, 172, 88), x, 9 - hgt)
        for x in range(2, 14, 2):
            c = flores[(x // 2) % len(flores)]
            y = r.randrange(4, 7)
            P(s, c, x, y); P(s, c, x + 1, y); P(s, c, x, y - 1); P(s, shade(c, 1.2), x + 1, y - 1)
        return s
    return make


OBJECT_BUILDERS = {
    "lamp": _poste, "cafe_mesa": _mesa(), "mesa_ricci": _mesa((40, 120, 70), (246, 240, 230), (246, 240, 236), (196, 46, 54)),
    "cavalete": _cavalete, "floreira": _floreira(), "floreira2": _floreira(((200, 140, 255), (255, 255, 255))),
    "floreira3": _floreira(((255, 120, 90), (255, 220, 90))),
}
art.OBJECT_BUILDERS.update(OBJECT_BUILDERS)

OBJECT_DEFS = {"cafe_mesa": (1, 1, True, "obj"), "mesa_ricci": (1, 1, True, "obj"), "cavalete": (1, 1, True, "obj"),
               "floreira": (1, 1, True, "obj"), "floreira2": (1, 1, True, "obj"), "floreira3": (1, 1, True, "obj")}
HITBOXES = {"cafe_mesa": (0, 6, 16, 10), "mesa_ricci": (0, 6, 16, 10), "cavalete": (3, 9, 10, 7),
            "floreira": (1, 9, 14, 7), "floreira2": (1, 9, 14, 7), "floreira3": (1, 9, 14, 7)}
SHADOWS = {"cafe_mesa": 40, "mesa_ricci": 40, "cavalete": 18, "floreira": 26, "floreira2": 26, "floreira3": 26}

# enfeites na calçada de cada fachada (da ponta longe da porta para perto dela)
FACADE_DECOR = {
    "cafe": ["cafe_mesa", "cavalete"], "trattoria": ["mesa_ricci", "mesa_ricci", "floreira3"],
    "books": ["cavalete", "floreira"], "market": ["floreira3", "floreira"], "bar": ["cavalete"],
    "tower": ["floreira2", "floreira2"], "catco": ["floreira", "floreira"], "cinema": ["cavalete"],
    "home": ["floreira2", "floreira2"], "ricci": ["floreira", "floreira"], "hospital": ["floreira", "floreira"],
}


def street_decor(m):
    """Mesas, lousas e floreiras na calçada em frente às fachadas (só onde sobra calçada para passar).
    Chamado por world.build_city antes de finalize()."""
    taken = set()
    for o in m.objects:
        if o.layer == "obj":
            for yy in range(o.y, o.y + o.h):
                for xx in range(o.x, o.x + o.w):
                    taken.add((xx, yy))
    floor = ("pavement", "plaza")
    placed = set()
    for b in m.buildings:
        kinds = list(FACADE_DECOR.get(b.style, []))
        if not kinds:
            continue
        row = b.y + b.h
        door_x = b.door[0]
        # colunas da fachada, começando pela ponta mais longe da porta
        cols = sorted(range(b.x, b.x + b.w), key=lambda c: -abs(c - door_x))
        for c in cols:
            if not kinds:
                break
            if abs(c - door_x) <= 1 or (c, row) in taken:
                continue
            if m.tile_at(c, row) not in floor or m.tile_at(c, row + 1) not in floor:
                continue
            if (c, row + 1) in taken or (c - 1, row) in placed or (c + 1, row) in placed:
                continue                                    # um tile livre entre um enfeite e outro
            m.add(kinds.pop(0), c, row)
            taken.add((c, row))
            placed.add((c, row))


# ---------------------------------------------------------------------------
# Pombos: ciscam pela calçada e voam quando a Letícia chega perto
# ---------------------------------------------------------------------------
def _pombo(frame, flying=False):
    def make():
        s = new(8, 7)
        corpo, asa, pescoco = (150, 150, 168), (118, 118 , 136), (110, 160, 150)
        if flying:
            up_ = frame % 2 == 0
            R(s, corpo, 2, 3, 4, 2)
            R(s, asa, 0, 1 if up_ else 4, 3, 2); R(s, asa, 5, 1 if up_ else 4, 3, 2)
            P(s, pescoco, 6, 3); P(s, (60, 60, 70), 7, 3)
            return art.up(s)
        peck = frame == 1
        R(s, corpo, 1, 3, 5, 3)
        R(s, asa, 2, 3, 3, 2)
        R(s, shade(corpo, 0.8), 0, 4, 2, 1)                  # rabo
        hy = 3 if peck else 1
        R(s, pescoco, 5, hy, 2, 2)
        P(s, (40, 40, 50), 6, hy)
        P(s, (230, 160, 110), 7, hy + 1)                    # bico
        P(s, (210, 110, 90), 3, 6); P(s, (210, 110, 90), 5, 6)
        return art.up(s)
    return art.cached(("pombo", frame, flying), make)


def _sombra_pombo():
    def make():
        s = pygame.Surface((6 * SCALE, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 60), s.get_rect())
        return s
    return art.cached(("pombo_sombra",), make)


class Pigeons:
    """Bandinhos de pombos na calçada e no calçadão (só de dia, só na cidade)."""

    def __init__(self):
        self.birds = []
        self.t = 0.0
        self.spawn_t = 2.0

    def reset(self):
        self.birds.clear()

    def _spawn(self, g, m, cam):
        rnd = random
        for _ in range(12):
            tx = int((cam[0] + rnd.randrange(0, 1280)) // TILE)
            ty = int((cam[1] + rnd.randrange(0, 720)) // TILE)
            if m.tile_at(tx, ty) not in ("pavement", "plaza") or m.is_solid(tx, ty):
                continue
            if math.hypot(g.player.x - (tx + 0.5) * TILE, g.player.y - (ty + 0.5) * TILE) < 5 * TILE:
                continue
            for _ in range(rnd.randrange(2, 5)):
                self.birds.append({"x": (tx + rnd.uniform(0.1, 0.9)) * TILE, "y": (ty + rnd.uniform(0.3, 0.9)) * TILE,
                                   "dir": rnd.choice((-1, 1)), "peck": rnd.uniform(0, 3), "hop": rnd.uniform(0.5, 3),
                                   "fly": None})
            return

    def update(self, dt, g):
        self.t += dt
        if g.map_name != "city":
            self.reset()
            return
        m = g.current_map
        cam = g.camera(m)
        if g.darkness(g.minutes) > 0.3 or g.weather == "chuva":
            for b in self.birds:                            # escureceu ou choveu: vão embora voando
                if b["fly"] is None:
                    b["fly"] = [random.uniform(-1, 1) * 60, -random.uniform(90, 140)]
        else:
            self.spawn_t -= dt
            if self.spawn_t <= 0 and len(self.birds) < 9:
                self.spawn_t = random.uniform(6, 14)
                self._spawn(g, m, cam)
        px, py = g.player.x, g.player.y
        keep = []
        for b in self.birds:
            if b["fly"] is None:
                if math.hypot(px - b["x"], py - b["y"]) < 2.2 * TILE:   # susto: todos levantam voo
                    away = 1 if b["x"] > px else -1
                    b["fly"] = [away * random.uniform(80, 130), -random.uniform(90, 150)]
                    b["dir"] = away
                b["hop"] -= dt
                if b["fly"] is None and b["hop"] <= 0:                           # pulinho para o lado
                    b["hop"] = random.uniform(0.8, 3.5)
                    b["dir"] = random.choice((-1, 1))
                    nx = b["x"] + b["dir"] * random.uniform(3, 8) * SCALE
                    if m.tile_at(int(nx // TILE), int(b["y"] // TILE)) in ("pavement", "plaza"):
                        b["x"] = nx
            else:
                b["x"] += b["fly"][0] * dt * SCALE
                b["y"] += b["fly"][1] * dt * SCALE
                b["fly"][1] -= 20 * dt
            sx, sy = b["x"] - cam[0], b["y"] - cam[1]
            if -200 < sx < 1480 and -300 < sy < 920:
                keep.append(b)
        self.birds = keep

    def draw(self, surf, cam, flying):
        for b in self.birds:
            if (b["fly"] is not None) != flying:
                continue
            if flying:
                img = _pombo(int(self.t * 12) % 2, True)
            else:
                img = _pombo(1 if (self.t + b["peck"]) % 2.4 < 0.35 else 0)
            if b["dir"] < 0:
                img = pygame.transform.flip(img, True, False)
            x, y = int(b["x"] - cam[0] - img.get_width() / 2), int(b["y"] - cam[1] - img.get_height())
            if not flying:
                surf.blit(_sombra_pombo(), (x + 2, y + img.get_height() - 3))
            surf.blit(img, (x, y))

"""Atividades da vida fora do escritório: horta no terraço, coletáveis, bichinho de estimação,
karaokê no Noonan's e sessões no Cine National.

O jogo principal (game.py) chama as funções deste módulo em pontos bem definidos:
init_state / save_state / load_state, update, night, resolve, use_object, labels e desenho.
"""
import math
import random

import pygame

from . import art, ui
from .art import new, up, R, P, shade, mix, cached
from .config import (SCALE, TILE, SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_RED, C_PINK,
                     C_ACCENT, C_ACCENT_2, C_PANEL_2)
from .data import ITEMS, CROPS, FORAGE, FORAGE_EXTRA
from .characters import NPCS
from .world import PLOT_SLOTS, in_area

# ---------------------------------------------------------------------------
# Arte: objetos novos
# ---------------------------------------------------------------------------


def _telescope():
    s = new(16, 26)
    for (x0, x1) in ((8, 3), (8, 13), (8, 8)):
        pygame.draw.line(s, (70, 64, 80), (x0, 14), (x1, 25), 1)
    pygame.draw.line(s, (60, 52, 90), (4, 12), (13, 5), 3)
    pygame.draw.line(s, (120, 100, 180), (4, 11), (13, 4), 1)
    R(s, (230, 220, 250), 13, 3, 2, 3)
    R(s, (40, 36, 50), 7, 12, 3, 3)
    return s


def _petbed():
    s = new(16, 12)
    pygame.draw.ellipse(s, (110, 60, 150), (0, 2, 16, 10))
    pygame.draw.ellipse(s, (160, 110, 210), (2, 3, 12, 7))
    pygame.draw.ellipse(s, (230, 210, 245), (4, 5, 8, 4))
    return s


def _lounger():
    s = new(16, 32)
    R(s, (230, 230, 236), 2, 4, 12, 24)
    R(s, (200, 200, 210), 2, 26, 12, 2)
    R(s, (120, 190, 220), 3, 9, 10, 17)
    for y in range(11, 26, 4):
        R(s, (240, 250, 255), 3, y, 10, 1)
    R(s, (250, 250, 250), 3, 4, 10, 5)
    R(s, (90, 90, 100), 2, 28, 2, 4); R(s, (90, 90, 100), 12, 28, 2, 4)
    return s


def _string_lights():
    s = new(96, 16)
    cols = [(255, 220, 120), (255, 150, 190), (150, 220, 255), (190, 255, 160)]
    pts = []
    for i in range(0, 97, 2):
        y = 3 + int(5 * math.sin(i / 96 * math.pi * 3) ** 2)
        pts.append((i, y))
    pygame.draw.lines(s, (60, 50, 70), False, pts, 1)
    for k, (x, y) in enumerate(pts[3::6]):
        c = cols[k % 4]
        R(s, c, x - 1, y + 1, 3, 3)
        P(s, (255, 255, 255), x, y + 1)
    return s


def _railing_plant():
    s = new(16, 22)
    R(s, (200, 120, 80), 3, 14, 10, 8)
    R(s, (230, 150, 100), 3, 14, 10, 2)
    for (x, y, rad, c) in [(8, 9, 6, (60, 150, 80)), (4, 11, 4, (70, 160, 90)), (12, 11, 4, (70, 160, 90)),
                           (8, 5, 4, (90, 180, 100))]:
        pygame.draw.circle(s, c, (x, y), rad)
    for (x, y) in ((5, 8), (11, 6), (8, 11)):
        P(s, (255, 200, 230), x, y)
    return s


def _watering():
    s = new(16, 16)
    R(s, (90, 150, 210), 4, 6, 8, 8)
    R(s, (130, 190, 240), 4, 6, 8, 2)
    pygame.draw.line(s, (90, 150, 210), (11, 9), (15, 5), 2)
    pygame.draw.arc(s, (70, 120, 180), (2, 2, 9, 9), 0.5, 2.7, 2)
    R(s, (60, 100, 150), 4, 14, 8, 1)
    return s


def _petstand():
    s = new(32, 30)
    for i in range(8):
        R(s, (255, 140, 180) if i % 2 == 0 else (255, 250, 250), i * 4, 2, 4, 6)
    for i in range(8):
        pygame.draw.circle(s, (255, 140, 180) if i % 2 == 0 else (255, 250, 250), (i * 4 + 2, 8), 2)
    R(s, (150, 100, 60), 1, 8, 2, 20); R(s, (150, 100, 60), 29, 8, 2, 20)
    R(s, (170, 120, 76), 0, 20, 32, 4)
    R(s, (130, 90, 56), 0, 24, 32, 6)
    R(s, (240, 220, 180), 10, 24, 12, 4)
    # pata no letreiro
    pygame.draw.circle(s, (200, 90, 130), (16, 26), 1)
    # caixinhas com filhotes
    R(s, (210, 170, 110), 4, 15, 9, 5); R(s, (210, 170, 110), 19, 15, 9, 5)
    pygame.draw.circle(s, (240, 160, 80), (8, 14), 3)
    P(s, (240, 160, 80), 6, 11); P(s, (240, 160, 80), 10, 11)
    P(s, (30, 30, 30), 7, 14); P(s, (30, 30, 30), 9, 14)
    pygame.draw.circle(s, (200, 150, 90), (23, 14), 3)
    R(s, (150, 100, 60), 20, 12, 2, 4); R(s, (150, 100, 60), 25, 12, 2, 4)
    P(s, (30, 30, 30), 22, 14); P(s, (30, 30, 30), 24, 14)
    return s


def _glass_door():
    s = new(16, 30)
    R(s, (60, 54, 74), 0, 0, 16, 30)
    R(s, (200, 200, 214), 1, 1, 14, 29)
    R(s, (150, 210, 240), 3, 3, 10, 26)
    R(s, (190, 235, 255), 3, 3, 10, 2)
    pygame.draw.line(s, (230, 250, 255), (4, 10), (8, 6))
    pygame.draw.line(s, (230, 250, 255), (5, 16), (11, 10))
    R(s, (120, 190, 110), 4, 22, 8, 7)
    pygame.draw.circle(s, (90, 170, 90), (6, 22), 3); pygame.draw.circle(s, (110, 190, 100), (10, 21), 3)
    R(s, (230, 200, 90), 12, 15, 2, 3)
    return s


def _cine_screen():
    s = new(160, 34)
    R(s, (150, 30, 50), 0, 0, 160, 34)
    for x in range(0, 160, 6):
        R(s, (120, 20, 40), x, 0, 2, 34)
    R(s, (20, 16, 26), 12, 3, 136, 28)
    R(s, (232, 232, 244), 14, 5, 132, 24)
    R(s, (210, 210, 228), 14, 25, 132, 4)
    R(s, (200, 160, 60), 0, 0, 160, 2)
    return s


def _seat():
    s = new(16, 18)
    R(s, (150, 30, 50), 3, 2, 10, 9)
    R(s, (190, 50, 70), 4, 3, 8, 3)
    R(s, (170, 40, 60), 3, 10, 10, 4)
    R(s, (90, 20, 30), 2, 5, 1, 9); R(s, (90, 20, 30), 13, 5, 1, 9)
    R(s, (60, 40, 50), 4, 14, 1, 4); R(s, (60, 40, 50), 11, 14, 1, 4)
    return s


def _ticket():
    s = new(48, 28)
    R(s, (90, 40, 110), 0, 10, 48, 18)
    R(s, (130, 70, 160), 0, 10, 48, 3)
    R(s, (160, 200, 230), 4, 0, 40, 11)
    R(s, (200, 230, 250), 6, 1, 6, 9)
    R(s, (250, 210, 100), 6, 16, 36, 6)
    for x in range(8, 40, 5):
        R(s, (180, 60, 60), x, 18, 3, 2)
    return s


def _popcorn():
    s = new(16, 28)
    R(s, (200, 40, 50), 2, 6, 12, 20)
    R(s, (240, 240, 250), 3, 8, 10, 10)
    for (x, y) in ((5, 14), (8, 13), (11, 15), (6, 16), (9, 16), (4, 17), (11, 17), (7, 11)):
        pygame.draw.circle(s, (255, 236, 160), (x, y), 2)
    R(s, (160, 30, 40), 1, 3, 14, 4)
    R(s, (250, 210, 90), 5, 0, 6, 3)
    R(s, (80, 30, 40), 3, 26, 2, 2); R(s, (80, 30, 40), 11, 26, 2, 2)
    return s


def _film_poster(kind=0):
    s = new(16, 16)
    bg = [(30, 30, 70), (240, 120, 160)][kind]
    R(s, (230, 200, 120), 2, 0, 12, 15)
    R(s, bg, 3, 1, 10, 13)
    if kind == 0:
        for (x, y) in ((5, 3), (10, 4), (7, 6), (11, 9), (4, 9)):
            P(s, (255, 255, 255), x, y)
        pygame.draw.polygon(s, (220, 60, 60), [(8, 5), (6, 11), (10, 11)])
    else:
        pygame.draw.circle(s, (255, 255, 255), (7, 6), 2); pygame.draw.circle(s, (255, 255, 255), (10, 6), 2)
        pygame.draw.polygon(s, (255, 255, 255), [(5, 7), (12, 7), (8, 11)])
    R(s, (255, 255, 255), 4, 12, 8, 1)
    return s


def _rope():
    s = new(16, 16)
    R(s, (210, 170, 70), 2, 4, 2, 11); R(s, (210, 170, 70), 12, 4, 2, 11)
    pygame.draw.circle(s, (240, 210, 110), (3, 3), 2); pygame.draw.circle(s, (240, 210, 110), (13, 3), 2)
    pygame.draw.arc(s, (190, 30, 50), (3, 2, 10, 8), math.pi, 2 * math.pi, 2)
    R(s, (150, 120, 60), 1, 14, 4, 2); R(s, (150, 120, 60), 11, 14, 4, 2)
    return s


art.OBJECT_BUILDERS.update({
    "telescope": _telescope, "petbed": _petbed, "lounger": _lounger, "string_lights": _string_lights,
    "railing_plant": _railing_plant, "watering": _watering, "petstand": _petstand, "cine_screen": _cine_screen,
    "seat": _seat, "ticket": _ticket, "popcorn": _popcorn, "film_poster": _film_poster,
    "film_poster2": lambda: _film_poster(1), "rope": _rope,
    "plot": lambda: _plot_art(None, 0, False), "glass_door": _glass_door,
})


# --- canteiros -------------------------------------------------------------

def _plot_art(crop, stage, wet, ready=False):
    s = new(16, 26)
    R(s, (120, 80, 50), 0, 14, 16, 12)
    R(s, (150, 104, 66), 0, 14, 16, 2)
    R(s, (96, 62, 40), 0, 24, 16, 2)
    soil = (66, 42, 30) if wet else (112, 74, 48)
    R(s, soil, 2, 16, 12, 7)
    rnd = random.Random(7)
    for _ in range(8):
        P(s, shade(soil, 1.25 if not wet else 0.8), rnd.randrange(2, 14), rnd.randrange(16, 23))
    if wet:
        P(s, (150, 190, 230), 4, 17); P(s, (150, 190, 230), 11, 20)
    if crop is None:
        return s
    c = CROPS[crop]["color"]
    leaf, leaf2 = (70, 160, 80), (100, 190, 100)
    if stage == 0:
        for x in (5, 8, 11):
            P(s, (200, 170, 110), x, 19)
        return s
    if stage == 1:
        R(s, leaf, 7, 14, 2, 4)
        R(s, leaf2, 5, 13, 2, 2); R(s, leaf2, 9, 13, 2, 2)
        return s
    if stage == 2:
        R(s, leaf, 7, 10, 2, 8)
        for (x, y) in ((4, 11), (10, 9), (4, 14), (10, 13)):
            R(s, leaf2, x, y, 3, 2)
        return s
    # pronta
    if crop == "girassol":
        R(s, leaf, 7, 4, 2, 14)
        R(s, leaf2, 4, 12, 3, 2); R(s, leaf2, 9, 9, 3, 2)
        pygame.draw.circle(s, c, (8, 4), 4)
        pygame.draw.circle(s, (120, 70, 30), (8, 4), 2)
    elif crop == "abobora":
        R(s, leaf, 2, 12, 4, 3); R(s, leaf, 10, 11, 4, 3)
        pygame.draw.ellipse(s, c, (3, 13, 10, 8))
        pygame.draw.ellipse(s, shade(c, 1.15), (5, 14, 4, 5))
        R(s, (90, 120, 50), 7, 11, 2, 3)
    elif crop == "morango":
        for (x, y) in ((3, 14), (9, 13), (6, 12)):
            R(s, leaf, x, y, 4, 3)
        for (x, y) in ((4, 17), (11, 16), (8, 18)):
            pygame.draw.circle(s, c, (x, y), 2)
            P(s, (255, 230, 120), x, y - 1)
    elif crop == "manjericao":
        for (x, y, rad) in ((8, 10, 4), (5, 13, 3), (11, 13, 3), (8, 7, 3)):
            pygame.draw.circle(s, c, (x, y), rad)
        for (x, y) in ((7, 8), (10, 12), (5, 12)):
            P(s, (160, 230, 150), x, y)
    elif crop == "tomate":
        R(s, (90, 140, 60), 7, 4, 2, 14)
        for (x, y) in ((4, 7), (10, 6), (4, 11), (10, 11)):
            R(s, leaf2, x, y, 3, 2)
        for (x, y) in ((5, 9), (11, 9), (8, 13), (6, 15)):
            pygame.draw.circle(s, c, (x, y), 2)
            P(s, (255, 200, 190), x - 1, y - 1)
    elif crop == "rosa":
        for (x, y, rad) in ((8, 11, 5), (4, 13, 3), (12, 13, 3)):
            pygame.draw.circle(s, (60, 130, 70), (x, y), rad)
        for (x, y) in ((6, 8), (11, 10), (5, 13), (9, 13)):
            pygame.draw.circle(s, c, (x, y), 2)
            P(s, shade(c, 1.25), x, y)
    if ready:
        R(s, (255, 250, 200), 14, 1, 1, 3); R(s, (255, 250, 200), 13, 2, 3, 1)
    return s


def plot_sprite(crop, stage, wet, ready):
    return cached(("plot", crop, stage, wet, ready), lambda: up(_plot_art(crop, stage, wet, ready)))


# --- coletáveis no chão (8x8 de arte) ------------------------------------------

def _mini(kind, c):
    s = new(10, 10)
    d = shade(c, 0.7)
    if kind == "shell":
        pygame.draw.polygon(s, c, [(5, 8), (1, 4), (3, 1), (7, 1), (9, 4)])
        for x in (3, 5, 7):
            pygame.draw.line(s, d, (5, 8), (x, 2))
    elif kind == "seaglass":
        pygame.draw.polygon(s, c, [(2, 5), (4, 2), (8, 3), (8, 7), (4, 8)])
        P(s, (240, 255, 255), 4, 4)
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 4.5 if i % 2 == 0 else 2
            pts.append((5 + math.cos(a) * r, 5 + math.sin(a) * r))
        pygame.draw.polygon(s, c, pts)
        P(s, (255, 230, 200), 5, 4)
    elif kind == "coral":
        for (x0, y0, x1, y1) in ((5, 9, 5, 2), (5, 6, 2, 3), (5, 5, 8, 2), (2, 3, 2, 1), (8, 2, 9, 1)):
            pygame.draw.line(s, c, (x0, y0), (x1, y1), 2)
    elif kind == "wildflower":
        R(s, (70, 150, 80), 4, 5, 1, 5); R(s, (70, 150, 80), 7, 6, 1, 4)
        for (x, y, cc) in ((4, 3, c), (7, 4, (255, 240, 140)), (2, 6, (255, 170, 200))):
            pygame.draw.circle(s, cc, (x, y), 1)
            P(s, (255, 255, 255), x, y)
    elif kind == "berry":
        R(s, (70, 150, 80), 3, 1, 4, 2)
        for (x, y) in ((3, 5), (6, 5), (4, 7), (7, 7)):
            pygame.draw.circle(s, c, (x, y), 1)
        P(s, shade(c, 1.6), 3, 4)
    elif kind == "clover":
        for (x, y) in ((3, 3), (6, 3), (3, 6), (6, 6)):
            pygame.draw.circle(s, c, (x, y), 2)
        P(s, (150, 230, 150), 3, 2)
        R(s, shade(c, 0.7), 5, 7, 1, 3)
    elif kind == "mushroom":
        pygame.draw.ellipse(s, (200, 80, 70), (1, 2, 8, 5))
        R(s, (240, 230, 210), 4, 6, 2, 3)
        P(s, (255, 255, 255), 3, 3); P(s, (255, 255, 255), 6, 4)
    else:
        pygame.draw.circle(s, c, (5, 5), 3)
    return s


def forage_sprite(item):
    icon = "mushroom" if item == "cogumelos" else ITEMS[item]["icon"]
    return cached(("forage", item), lambda: up(_mini(icon, ITEMS[item]["color"])))


# --- ícones de itens novos (16x16), plugados no desenhista de ícones ------------

_orig_icon = art._icon


def _icon_extra(kind, color):
    c = color
    s = new(16, 16)
    if kind == "seed":
        R(s, (240, 226, 196), 3, 2, 10, 12)
        R(s, (210, 190, 150), 3, 2, 10, 2)
        pygame.draw.circle(s, c, (8, 8), 3)
        R(s, (90, 160, 80), 7, 10, 2, 3)
        R(s, (180, 160, 120), 3, 13, 10, 1)
    elif kind == "berry":
        R(s, (70, 150, 80), 6, 2, 4, 2)
        for (x, y) in ((5, 8), (10, 8), (7, 11), (8, 6)):
            pygame.draw.circle(s, c, (x, y), 3)
            P(s, shade(c, 1.5), x - 1, y - 1)
    elif kind == "rose":
        R(s, (60, 130, 70), 7, 7, 2, 8)
        R(s, (80, 160, 90), 4, 10, 3, 2)
        pygame.draw.circle(s, c, (8, 5), 4)
        pygame.draw.circle(s, shade(c, 0.8), (8, 5), 2)
        P(s, shade(c, 1.3), 7, 3)
    elif kind == "pumpkin":
        pygame.draw.ellipse(s, c, (1, 4, 14, 11))
        pygame.draw.ellipse(s, shade(c, 1.15), (5, 5, 6, 9))
        pygame.draw.line(s, shade(c, 0.75), (8, 5), (8, 14))
        R(s, (90, 120, 50), 7, 1, 2, 4)
    elif kind == "popcorn":
        pygame.draw.polygon(s, (220, 40, 50), [(3, 6), (13, 6), (11, 15), (5, 15)])
        for x in (5, 9):
            pygame.draw.line(s, (250, 250, 250), (x, 6), (x + 1, 15), 2)
        for (x, y) in ((4, 5), (7, 3), (10, 4), (12, 6), (6, 6), (9, 6)):
            pygame.draw.circle(s, (255, 236, 160), (x, y), 2)
    elif kind == "bone":
        R(s, c, 4, 7, 8, 3)
        for (x, y) in ((3, 6), (3, 10), (12, 6), (12, 10)):
            pygame.draw.circle(s, c, (x, y), 2)
    elif kind in ("shell", "seaglass", "star", "coral", "wildflower", "clover"):
        m = _mini(kind, c)
        s.blit(pygame.transform.scale(m, (15, 15)), (0, 0))
    else:
        return _orig_icon(kind, color)
    return s


art._icon = _icon_extra


# --- bichinhos -----------------------------------------------------------------

PET_COATS = {
    "gato": [("Laranjinha", (240, 160, 80)), ("Cinza", (150, 150, 164)), ("Pretinho", (56, 50, 64)),
             ("Branquinho", (244, 240, 234))],
    "cachorro": [("Caramelo", (204, 144, 82)), ("Chocolate", (116, 76, 54)), ("Branco com manchas", (244, 238, 230))],
}
PET_NAMES = {"gato": ["Kiwi", "Mel", "Fumaça", "Pandora", "Biscoito", "Lex"],
             "cachorro": ["Krypto", "Pipoca", "Paçoca", "Thor", "Luna", "Bolinha"]}


def _pet_art(kind, coat, frame, sleeping=False):
    s = new(16, 14)
    c = coat
    d = shade(c, 0.72)
    if sum(c) > 650:
        d = (200, 190, 180)
    out = shade(c, 0.45) if sum(c) > 200 else (20, 18, 24)
    eye = (40, 30, 30) if sum(c) > 200 else (120, 230, 120)
    if sleeping:
        pygame.draw.ellipse(s, out, (1, 5, 14, 9))
        pygame.draw.ellipse(s, c, (2, 6, 12, 7))
        pygame.draw.circle(s, c, (11, 8), 3)
        R(s, d, 3, 11, 9, 1)
        if kind == "gato":
            P(s, c, 10, 5); P(s, c, 13, 5)
        P(s, out, 10, 8); P(s, out, 12, 8)
        return s
    legs = [(4, 6), (5, 7), (3, 5)][frame % 3]
    # corpo
    pygame.draw.ellipse(s, out, (1, 5, 11, 7))
    pygame.draw.ellipse(s, c, (2, 6, 9, 5))
    R(s, out, legs[0], 10, 2, 4); R(s, out, legs[1] + 4, 10, 2, 4)
    R(s, c, legs[0], 10, 1, 3); R(s, c, legs[1] + 4, 10, 1, 3)
    # cauda
    if kind == "gato":
        wag = frame % 2
        pygame.draw.line(s, out, (2, 7), (0, 2 + wag), 2)
        P(s, c, 1, 4 + wag)
    else:
        pygame.draw.line(s, out, (2, 7), (0, 4 + (frame % 2) * 2), 2)
    # cabeça
    pygame.draw.circle(s, out, (12, 5), 4)
    pygame.draw.circle(s, c, (12, 5), 3)
    if kind == "gato":
        pygame.draw.polygon(s, out, [(9, 3), (10, 0), (11, 2)])
        pygame.draw.polygon(s, out, [(13, 2), (14, 0), (15, 3)])
        P(s, (255, 170, 190), 10, 1); P(s, (255, 170, 190), 14, 1)
    else:
        R(s, d if d != c else out, 9, 3, 2, 4)
        R(s, d if d != c else out, 14, 3, 2, 4)
        R(s, mix(c, (255, 255, 255), 0.3), 12, 6, 3, 2)
        P(s, (30, 20, 20), 14, 6)
    P(s, eye, 11, 4); P(s, eye, 13, 4)
    P(s, (255, 150, 170), 12, 6)
    if sum(c) > 650 and kind == "cachorro":
        R(s, (120, 90, 70), 4, 6, 3, 2)
        P(s, (120, 90, 70), 8, 8)
    return s


def pet_frames(kind, coat):
    def make():
        fr = {}
        for f in range(3):
            img = up(_pet_art(kind, coat, f))
            fr[("right", f)] = img
            fr[("left", f)] = pygame.transform.flip(img, True, False)
        img = up(_pet_art(kind, coat, 0, True))
        fr[("sleep", 0)] = img
        return fr
    return cached(("pet", kind, tuple(coat)), make)


class Pet:
    def __init__(self, kind, name, coat):
        self.kind, self.name, self.coat = kind, name, tuple(coat)
        self.map = "home"
        self.x, self.y = 0.0, 0.0
        self.path = []
        self.wait = 1.0
        self.dir = "right"
        self.anim = 0.0
        self.petted = False
        self.love = 0
        self.emote = None
        self.emote_t = 0.0
        self.sleeping = False
        self.near = False

    # posição em tiles
    @property
    def tile(self):
        return int(self.x // TILE), int((self.y - 1) // TILE)

    @property
    def base_y(self):
        return self.y

    def place(self, tx, ty):
        self.x, self.y = (tx + 0.5) * TILE, (ty + 1) * TILE - 4
        self.path = []

    def to_save(self):
        return dict(kind=self.kind, name=self.name, coat=list(self.coat), love=self.love, petted=self.petted,
                    map=self.map)

    @classmethod
    def from_save(cls, d):
        p = cls(d["kind"], d["name"], d["coat"])
        p.love = d.get("love", 0)
        p.petted = d.get("petted", False)
        p.map = d.get("map", "home")
        return p

    def update(self, dt, g):
        self.anim += dt
        if self.emote_t > 0:
            self.emote_t -= dt
            if self.emote_t <= 0:
                self.emote = None
        m = g.world[self.map]
        night = g.minutes >= 22 * 60 or g.minutes < 7 * 60
        if self.sleeping and not night:
            self.sleeping = False
        if self.sleeping:
            if random.random() < dt * 0.15:
                self.emote, self.emote_t = "zzz", 2.0
            return
        if self.path:
            tx, ty = self.path[0]
            cx, cy = (tx + 0.5) * TILE, (ty + 1) * TILE - 4
            dx, dy = cx - self.x, cy - self.y
            dist = math.hypot(dx, dy)
            sp = 1.8 * TILE * dt
            if dx:
                self.dir = "right" if dx > 0 else "left"
            if dist <= sp:
                self.x, self.y = cx, cy
                self.path.pop(0)
                if not self.path and night and self.map == "home" and (tx, ty) == (16, 12):
                    self.sleeping = True
            else:
                self.x += dx / dist * sp
                self.y += dy / dist * sp
            return
        self.wait -= dt
        if self.wait > 0:
            return
        self.wait = random.uniform(1.5, 5.0)
        here = self.tile
        if night and self.map == "home":
            goal = (16, 12)
        elif self.map == g.map_name and random.random() < 0.35:
            goal = g.player.tile          # vem ficar pertinho
            goal = (goal[0] + random.choice((-1, 1)), goal[1])
        else:
            goal = (here[0] + random.randint(-4, 4), here[1] + random.randint(-3, 3))
        if m.is_solid(*goal) or goal in m.doors:
            return
        path = m.find_path(here, goal, 900)
        if path and len(path) <= 14 and not any(p in m.doors for p in path):
            self.path = path

    def draw(self, surf, cam):
        fr = pet_frames(self.kind, self.coat)
        if self.sleeping:
            img = fr[("sleep", 0)]
        else:
            f = int(self.anim * 8) % 3 if self.path else 0
            img = fr[(self.dir, f)]
        x = int(self.x - img.get_width() // 2 - cam[0])
        y = int(self.y - img.get_height() - cam[1])
        sh = pygame.Surface((12 * SCALE, 4 * SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 60), sh.get_rect())
        surf.blit(sh, (int(self.x - 6 * SCALE - cam[0]), int(self.y - 2 * SCALE - cam[1])))
        surf.blit(img, (x, y))
        if self.emote:
            from .cutscenes import draw_emote
            draw_emote(surf, int(self.x - cam[0]), y - 2, self.emote, 1 - max(0, self.emote_t - 1.4))


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------

def init_state(g):
    g.garden = {}
    g.forage = []
    g.forage_found = set()
    g.pet = None
    g.rested = False
    for k in ("harvest", "karaoke_best", "karaoke_s", "movies", "forage"):
        g.stats.setdefault(k, 0)


def save_state(g):
    return dict(garden=g.garden, forage=g.forage, forage_found=sorted(g.forage_found),
                pet=g.pet.to_save() if g.pet else None, rested=g.rested)


def load_state(g, d):
    g.garden = {str(k): v for k, v in d.get("garden", {}).items() if v.get("crop") in CROPS}
    g.forage = [f for f in d.get("forage", []) if f[3] in ITEMS]
    g.forage_found = set(d.get("forage_found", []))
    g.pet = Pet.from_save(d["pet"]) if d.get("pet") else None
    g.rested = d.get("rested", False)
    if g.pet:
        place_pet(g)
    if not g.forage:
        spawn_forage(g)


def place_pet(g):
    p = g.pet
    p.map = "terrace" if (g.weather != "chuva" and random.random() < 0.3) else "home"
    m = g.world[p.map]
    spots = [(x, y) for y in range(2, m.h - 1) for x in range(1, m.w - 1)
             if not m.is_solid(x, y) and (x, y) not in m.doors and m.tile_at(x, y) not in ("void", "door")]
    if p.map == "home":
        spots = [s for s in spots if s[0] >= 9] or spots
    p.place(*random.choice(spots))
    p.sleeping = False


# ---------------------------------------------------------------------------
# Coletáveis
# ---------------------------------------------------------------------------

def spawn_forage(g):
    city = g.world["city"]
    rnd = random.Random()
    out = []

    def free(x, y):
        return (not city.is_solid(x, y) and city.object_at(x, y) is None
                and all((f[1], f[2]) != (x, y) for f in out))

    beach = [k for k, f in FORAGE.items() if f["where"] == "beach"]
    park = [k for k, f in FORAGE.items() if f["where"] == "park"]
    sand = [(x, y) for y in range(city.h) for x in range(1, city.w - 1)
            if city.tile_at(x, y) == "sand" and in_area("beach", x, y)]
    grass = [(x, y) for y in range(city.h) for x in range(1, city.w - 1)
             if city.tile_at(x, y) in ("grass", "flowers")
             and (in_area("park", x, y) or in_area("woods", x, y) or in_area("garden", x, y))]
    n_beach = rnd.randint(6, 8) + (2 if g.weather == "chuva" else 0)
    n_park = rnd.randint(6, 9)
    for pool, kinds, n in ((sand, beach, n_beach), (grass, park, n_park)):
        weights = [FORAGE[k]["weight"] for k in kinds]
        extra = FORAGE_EXTRA.get("park", []) if kinds is park else []
        items = kinds + [e[0] for e in extra]
        weights = weights + [e[1] * (2 if g.weather == "chuva" else 1) for e in extra]
        for _ in range(n):
            for _try in range(20):
                x, y = rnd.choice(pool)
                if free(x, y):
                    out.append(["city", x, y, rnd.choices(items, weights)[0]])
                    break
    g.forage = out


def pickup_forage(g):
    tile = g.player.tile
    for f in g.forage:
        if f[0] == g.map_name and (f[1], f[2]) == tile:
            item = f[3]
            if not g.add_item(item):
                if "forage_full" not in g.warned:
                    g.warned.add("forage_full")
                    g.toasts.push("Mochila cheia! Não dá para pegar.", C_RED)
                return
            g.forage.remove(f)
            first = item not in g.forage_found
            g.forage_found.add(item)
            g.stats["forage"] = g.stats.get("forage", 0) + 1
            g.toasts.push(f"Achou: {ITEMS[item]['name']}" + (" (novo!)" if first else ""),
                          C_GOLD if first else C_GREEN, item)
            g.burst_at(tile, (255, 240, 180))
            return


def draw_ground(g, surf, m, cam):
    """Coletáveis brilhando no chão."""
    for f in g.forage:
        if f[0] != m.name:
            continue
        x, y = f[1] * TILE - cam[0], f[2] * TILE - cam[1]
        if x < -TILE or y < -TILE or x > surf.get_width() or y > surf.get_height():
            continue
        spr = forage_sprite(f[3])
        bob = int(math.sin(g.t * 3 + f[1]) * 1.5)
        sh = pygame.Surface((8 * SCALE, 3 * SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 50), sh.get_rect())
        surf.blit(sh, (x + TILE // 2 - 4 * SCALE, y + TILE - 6 * SCALE))
        surf.blit(spr, (x + (TILE - spr.get_width()) // 2, y + TILE - spr.get_height() - 3 * SCALE + bob))
        ph = (g.t * 0.7 + f[1] * 0.37 + f[2] * 0.11) % 1.0
        if ph < 0.12:
            k = int(3 + 4 * math.sin(ph / 0.12 * math.pi))
            cx, cy = x + TILE // 2 + 6, y + TILE // 2 - 2
            pygame.draw.line(surf, (255, 255, 255), (cx - k, cy), (cx + k, cy))
            pygame.draw.line(surf, (255, 255, 255), (cx, cy - k), (cx, cy + k))


# ---------------------------------------------------------------------------
# Horta
# ---------------------------------------------------------------------------

def plot_state(g, idx):
    return g.garden.get(str(idx))


def plot_stage(st):
    c = CROPS[st["crop"]]
    if st["growth"] >= c["days"]:
        return 3
    if st["growth"] == 0:
        return 0
    return 1 if st["growth"] / c["days"] < 0.5 else 2


def plot_image(g, o):
    st = plot_state(g, o.data)
    if not st:
        return plot_sprite(None, 0, False, False)
    stage = plot_stage(st)
    return plot_sprite(st["crop"], stage, st["watered"], stage == 3)


def plot_label(g, o):
    st = plot_state(g, o.data)
    if not st:
        sel = g.selected_item()
        if sel and ITEMS[sel]["kind"] == "seed":
            return f"Plantar {CROPS[ITEMS[sel]['crop']]['name']}"
        return "Canteiro vazio"
    c = CROPS[st["crop"]]
    if st["growth"] >= c["days"]:
        return f"Colher {c['name']}!"
    if not st["watered"]:
        return f"Regar {c['name']}"
    left = c["days"] - st["growth"]
    return f"{c['name']}: pronto em {left} dia(s)"


def use_plot(g, o):
    key = str(o.data)
    st = g.garden.get(key)
    tile = (o.x, o.y)
    if not st:
        sel = g.selected_item()
        if sel and ITEMS[sel]["kind"] == "seed":
            crop = ITEMS[sel]["crop"]
            g.remove_item(sel)
            g.garden[key] = dict(crop=crop, growth=0, watered=g.weather == "chuva")
            msg = f"Plantou {CROPS[crop]['name']}!"
            if g.weather == "chuva":
                msg += " A chuva já regou."
            g.toasts.push(msg, C_GREEN, sel)
            g.burst_at(tile, (170, 120, 80))
        else:
            g.toasts.push("Canteiro vazio: selecione sementes na barra (Mercado Central vende).", C_MUTED)
        return
    c = CROPS[st["crop"]]
    if st["growth"] >= c["days"]:
        if not g.add_item(c["item"], c["qty"]):
            g.toasts.push("Mochila cheia!", C_RED)
            return
        g.stats["harvest"] = g.stats.get("harvest", 0) + 1
        g.toasts.push(f"Colheu {c['qty']}x {ITEMS[c['item']]['name']}!", C_GOLD, c["item"])
        g.burst_at(tile, c["color"])
        if c["regrow"]:
            st["growth"] = c["days"] - c["regrow"]
            st["watered"] = False
        else:
            del g.garden[key]
        return
    if st["watered"]:
        g.toasts.push(f"{c['name']} já foi regado hoje.", C_MUTED)
        return
    st["watered"] = True
    g.toasts.push(f"Regou {c['name']}.", (150, 200, 255))
    g.burst_at(tile, (120, 180, 255))


def water_all(g):
    dry = [st for st in g.garden.values() if not st["watered"]]
    if not dry:
        g.toasts.push("Todos os canteiros já estão regados." if g.garden else "Nada plantado ainda.", C_MUTED)
        return
    if g.energy < 4:
        g.toasts.push("Sem energia nem para segurar o regador.", C_RED)
        return
    g.energy -= 4
    for st in dry:
        st["watered"] = True
    g.toasts.push(f"Regou {len(dry)} canteiro(s) com o regador.", (150, 200, 255))
    for i, (x, y) in enumerate(PLOT_SLOTS):
        if g.garden.get(str(i)):
            g.burst_at((x, y), (120, 180, 255))


# ---------------------------------------------------------------------------
# Bichinho
# ---------------------------------------------------------------------------

def open_adoption(g):
    if not (9 * 60 <= g.minutes < 18 * 60):
        g.say("Abrigo Patinhas: 'Voltamos amanhã às 9h! Adote, não compre.'")
        return
    if g.pet:
        p = g.pet
        g.push(ui.Choice(f"Abrigo Patinhas — 'Como está {'a' if p.name in ('Mel', 'Pandora', 'Luna', 'Fumaça') else 'o'} "
                         f"{p.name}?'", ["Comprar Petisco de Pet ($12)", "Só passando"],
                         lambda i: buy_treat(g) if i == 0 else None))
        return

    def pick_kind(i):
        if i > 1:
            return
        kind = ["gato", "cachorro"][i]
        coats = PET_COATS[kind]

        def pick_coat(j):
            if j >= len(coats):
                return
            coat = coats[j][1]
            names = PET_NAMES[kind]

            def pick_name(n):
                if n >= len(names):
                    return
                if g.money < 100:
                    g.say("O abrigo pede uma doação de $100 para a adoção. Você não tem o suficiente agora.")
                    return
                g.money -= 100
                g.pet = Pet(kind, names[n], coat)
                place_pet(g)
                g.pet.map = "home"
                g.pet.place(13, 12)
                g.toasts.push(f"{names[n]} agora é da família! Está te esperando na cobertura.", C_PINK)
                g.push(ui.Dialog("Abrigo Patinhas", [
                    f"Que lindo! {names[n]} vai adorar a cobertura.",
                    "Faça carinho todo dia (E) e, de vez em quando, traga um petisco. "
                    "Bichinhos felizes deixam presentinhos pela casa!"]))
            g.push(ui.Choice("Qual nome?", names + ["Voltar"], pick_name))
        g.push(ui.Choice(f"Qual {kind} você quer adotar?", [c[0] for c in coats] + ["Voltar"], pick_coat))
    g.push(ui.Choice("Abrigo Patinhas de National City. Adoção com doação de $100.",
                     ["Adotar um gato", "Adotar um cachorro", "Só olhando"], pick_kind))


def buy_treat(g):
    if g.money < 12:
        g.toasts.push("Dinheiro insuficiente.", C_RED)
        return
    if not g.add_item("petisco_pet"):
        g.toasts.push("Mochila cheia.", C_RED)
        return
    g.money -= 12
    g.toasts.push("Comprou Petisco de Pet.", C_GREEN, "petisco_pet")


def pet_at(g, tx, ty):
    p = g.pet
    if p and p.map == g.map_name:
        px, py = p.tile
        if abs(px - tx) <= 0 and abs(py - ty) <= 0:
            return p
        if math.hypot((tx + 0.5) * TILE - p.x, (ty + 1) * TILE - 4 - p.y) < TILE * 0.7:
            return p
    return None


def pet_label(g, p):
    if g.selected_item() == "petisco_pet":
        return f"Dar petisco para {p.name}"
    if p.petted:
        return f"Brincar com {p.name}"
    return f"Fazer carinho em {p.name}"


PET_REACT = {
    "gato": ["{n} ronrona e se esfrega na sua perna.", "{n} pisca devagar pra você. Isso é um 'eu te amo' felino.",
             "{n} deita de barriga pra cima. É uma armadilha, mas você cai.",
             "{n} mia como quem reclama do atendimento. Depois ronrona."],
    "cachorro": ["{n} abana o rabo tão forte que quase cai.", "{n} te dá a patinha sem você pedir.",
                 "{n} pula, gira e lambe sua mão.", "{n} traz um brinquedo e espera, cheio de esperança."],
}


def pet_interact(g, p):
    p.sleeping = False
    p.dir = "left" if g.player.x < p.x else "right"
    p.path = []
    p.wait = 2.5
    if g.selected_item() == "petisco_pet":
        g.remove_item("petisco_pet")
        p.love += 3
        p.emote, p.emote_t = "coracao", 2.4
        g.toasts.push(f"{p.name} amou o petisco!", C_PINK, "petisco_pet")
        if not p.petted:
            p.petted = True
            g.energy = min(g.max_energy, g.energy + 10)
        return
    if p.petted:
        p.emote, p.emote_t = "musica", 1.8
        g.toasts.push(random.choice(PET_REACT[p.kind]).format(n=p.name), C_LILAC)
        return
    p.petted = True
    bonus = "pediatria" in getattr(g, "buffs", ())
    p.love += 2 if bonus else 1
    p.emote, p.emote_t = "coracao", 2.4
    gain = 20 if bonus else 10
    g.energy = min(g.max_energy, g.energy + gain)
    g.toasts.push(random.choice(PET_REACT[p.kind]).format(n=p.name) + f" (+{gain} energia)", C_PINK)


# ---------------------------------------------------------------------------
# Karaokê (Noonan's)
# ---------------------------------------------------------------------------

SONGS = [
    dict(title="Luzes do Píer", bpm=96, color=(255, 140, 190), lyrics=[
        "As luzes do píer piscam pra mim", "o mar conta segredos sem fim",
        "e se a noite deixar, eu vou ficar", "até o sol voltar a brilhar"]),
    dict(title="Manchete de Primeira Página", bpm=112, color=(120, 200, 255), lyrics=[
        "Eu li seu nome no jornal da manhã", "uma notícia que ninguém viu",
        "você é a manchete do meu coração", "edição extra, ninguém resistiu"]),
    dict(title="Coração de Kryptonita", bpm=124, color=(110, 255, 140), lyrics=[
        "Você brilha verde no escuro", "me deixa fraca, eu juro",
        "coração de kryptonita", "que coisa mais bonita"]),
    dict(title="Garota de National City", bpm=134, color=(255, 214, 102), lyrics=[
        "Ela anda pela Siegel de salto alto", "dona da cidade, dona do asfalto",
        "garota de National City", "ninguém segura, é a verdade"]),
]
LANES = [((pygame.K_LEFT, pygame.K_d), "left", (255, 120, 170)), ((pygame.K_DOWN, pygame.K_f), "down", (120, 210, 255)),
         ((pygame.K_UP, pygame.K_j), "up", (255, 220, 110)), ((pygame.K_RIGHT, pygame.K_k), "right", (130, 240, 150))]


def _arrow(surf, cx, cy, d, color, size=13, outline=(30, 20, 40)):
    pts = {"up": [(0, -1), (1, 0.1), (0.4, 0.1), (0.4, 1), (-0.4, 1), (-0.4, 0.1), (-1, 0.1)]}
    base = pts["up"]
    rot = {"up": 0, "right": 90, "down": 180, "left": 270}[d]
    poly = []
    for (x, y) in base:
        v = pygame.math.Vector2(x, y).rotate(rot)
        poly.append((cx + v.x * size, cy + v.y * size))
    pygame.draw.polygon(surf, outline, [(x + 1, y + 2) for x, y in poly])
    pygame.draw.polygon(surf, color, poly)
    pygame.draw.polygon(surf, shade(color, 1.25), poly, 2)


class Karaoke(ui.Modal):
    W, H = 640, 520
    LEAD = 1.6         # segundos que a nota leva para cair até a linha

    def __init__(self, song, on_done, audience=()):
        self.song = song
        self.on_done = on_done
        self.audience = audience
        self.t = -3.0
        beat = 60.0 / song["bpm"]
        rnd = random.Random(song["title"])
        self.notes = []
        t = 0.6
        last = -1
        dur = 34.0
        while t < dur:
            dens = 0.55 + 0.35 * (t / dur)
            if rnd.random() < dens:
                lane = rnd.randrange(4)
                if lane == last and rnd.random() < 0.6:
                    lane = (lane + rnd.choice((1, 2, 3))) % 4
                self.notes.append(dict(t=t, lane=lane, hit=None))
                last = lane
                if t > dur * 0.5 and rnd.random() < 0.12:
                    self.notes.append(dict(t=t, lane=(lane + 2) % 4, hit=None))
            t += beat * (0.5 if rnd.random() < 0.25 + 0.2 * (t / dur) else 1.0)
        self.end_t = dur + 2.0
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.judge = ("", 0.0, C_TEXT)
        self.flash = [0.0] * 4
        self.over = False
        self.reported = False
        self.counts = dict(perfect=0, good=0, miss=0)
        self.hype = 0.5

    @property
    def accuracy(self):
        n = len(self.notes)
        return 0 if not n else (self.counts["perfect"] * 100 + self.counts["good"] * 60) / n

    def rank(self):
        a = self.accuracy
        return "S" if a >= 90 else "A" if a >= 75 else "B" if a >= 55 else "C" if a >= 35 else "D"

    def finish(self):
        self.over = True

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        if self.over:
            if ev.key in ui.CONFIRM + ui.CANCEL:
                self.done = True
                if not self.reported:
                    self.reported = True
                    self.on_done(self)
            return
        if ev.key == pygame.K_ESCAPE:
            for n in self.notes:
                if n["hit"] is None:
                    n["hit"] = "miss"
                    self.counts["miss"] += 1
            self.over = True
            return
        for i, (keys, _, _) in enumerate(LANES):
            if ev.key in keys:
                self.flash[i] = 0.12
                self.press(i)

    def press(self, lane):
        best, bd = None, 9
        for n in self.notes:
            if n["hit"] is None and n["lane"] == lane:
                d = abs(n["t"] - self.t)
                if d < bd:
                    best, bd = n, d
        if best is None or bd > 0.2:
            return
        if bd <= 0.07:
            best["hit"] = "perfect"
            self.counts["perfect"] += 1
            self.score += 100 + self.combo * 2
            self.judge = ("PERFEITO!", 0.6, (255, 230, 120))
        else:
            best["hit"] = "good"
            self.counts["good"] += 1
            self.score += 60 + self.combo
            self.judge = ("BOM", 0.6, (150, 220, 255))
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        self.hype = min(1.0, self.hype + 0.03)

    def update(self, dt):
        self.flash = [max(0.0, f - dt) for f in self.flash]
        j, jt, jc = self.judge
        self.judge = (j, max(0.0, jt - dt), jc)
        if self.over:
            return
        self.t += dt
        for n in self.notes:
            if n["hit"] is None and self.t - n["t"] > 0.2:
                n["hit"] = "miss"
                self.counts["miss"] += 1
                self.combo = 0
                self.hype = max(0.0, self.hype - 0.06)
                self.judge = ("ERROU", 0.5, C_RED)
        if self.t >= self.end_t:
            self.over = True

    def lyric(self):
        lines = self.song["lyrics"]
        if self.t < 0:
            return ""
        return lines[int(self.t / 8.5) % len(lines)]

    def draw(self, surf):
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((6, 2, 14, 200))
        surf.blit(veil, (0, 0))
        r = pygame.Rect(0, 0, self.W, self.H)
        r.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, r, border=self.song["color"])
        ui.text(surf, "KARAOKÊ  ·  NOONAN'S", (r.x + 24, r.y + 14), 22, self.song["color"], bold=True)
        ui.text(surf, f"Música: {self.song['title']}", (r.x + 24, r.y + 42), 18, C_TEXT)
        ui.text(surf, f"Pontos: {self.score}", (r.right - 24, r.y + 16), 20, C_GOLD, bold=True, right=True)
        ui.text(surf, f"Combo: {self.combo}", (r.right - 24, r.y + 42), 17, C_LILAC, right=True)
        lane_w = 82
        x0 = r.centerx - lane_w * 2
        top, hit_y = r.y + 80, r.bottom - 132
        # palco: holofotes
        for i in range(3):
            a = math.sin(pygame.time.get_ticks() / 900 + i * 2) * 60
            beam = pygame.Surface((r.w, hit_y - top + 30), pygame.SRCALPHA)
            cx = r.w // 2 + int(a) + (i - 1) * 160
            pygame.draw.polygon(beam, (*self.song["color"], 18), [(cx - 10, 0), (cx + 10, 0), (cx + 90, beam.get_height()),
                                                                   (cx - 90, beam.get_height())])
            surf.blit(beam, (r.x, top - 10))
        for i, (_, d, col) in enumerate(LANES):
            lr = pygame.Rect(x0 + i * lane_w + 4, top, lane_w - 8, hit_y - top + 40)
            s = pygame.Surface(lr.size, pygame.SRCALPHA)
            s.fill((*col, 26 + int(self.flash[i] * 500)))
            surf.blit(s, lr)
            cx = lr.centerx
            _arrow(surf, cx, hit_y, d, shade(col, 0.55) if self.flash[i] <= 0 else col, 17)
            pygame.draw.circle(surf, (255, 255, 255), (cx, hit_y), 24, 2)
        for n in self.notes:
            if n["hit"] in ("perfect", "good"):
                continue
            dy = (n["t"] - self.t) / self.LEAD
            if dy > 1.05 or dy < -0.25:
                continue
            y = hit_y - dy * (hit_y - top)
            _, d, col = LANES[n["lane"]]
            cx = x0 + n["lane"] * lane_w + lane_w // 2
            _arrow(surf, cx, int(y), d, col if n["hit"] is None else (90, 80, 100), 15)
        j, jt, jc = self.judge
        if jt > 0:
            ui.text(surf, j, (r.centerx, hit_y - 80 - int((0.6 - jt) * 30)), 30, jc, bold=True, center=True)
        if self.t < 0:
            ui.text(surf, str(int(-self.t) + 1), (r.centerx, r.centery - 60), 64, C_TEXT, bold=True, center=True)
            ui.text(surf, "Setas (ou D F J K) quando a seta encostar no círculo", (r.centerx, r.centery + 16), 18,
                    C_MUTED, center=True)
        ui.text(surf, self.lyric(), (r.centerx, r.bottom - 88), 22, C_TEXT, center=True)
        # plateia
        bar = pygame.Rect(r.x + 24, r.bottom - 28, r.w - 48, 10)
        pygame.draw.rect(surf, (40, 30, 56), bar, border_radius=5)
        pygame.draw.rect(surf, mix((248, 113, 113), (110, 231, 140), self.hype),
                         (bar.x, bar.y, int(bar.w * self.hype), bar.h), border_radius=5)
        ui.text(surf, "Animação da plateia", (bar.x, bar.y - 22), 14, C_MUTED)
        if self.over:
            box = pygame.Rect(0, 0, 420, 220)
            box.center = r.center
            ui.panel(surf, box, border=self.song["color"])
            ui.text(surf, f"Nota {self.rank()}", (box.centerx, box.y + 22), 44, C_GOLD, bold=True, center=True)
            ui.text(surf, f"{self.accuracy:.0f}% de precisão · combo máximo {self.best_combo}",
                    (box.centerx, box.y + 92), 18, C_TEXT, center=True)
            c = self.counts
            ui.text(surf, f"Perfeitos {c['perfect']}  ·  Bons {c['good']}  ·  Erros {c['miss']}",
                    (box.centerx, box.y + 122), 17, C_MUTED, center=True)
            ui.text(surf, "E: continuar", (box.centerx, box.bottom - 40), 17, C_LILAC, center=True)


def open_karaoke(g):
    if not (g.minutes >= 18 * 60 or g.minutes < 2 * 60):
        g.say("A jukebox toca rock dos anos 80. O karaokê começa às 18h.")
        return
    if g.energy < 8:
        g.toasts.push("Você está cansada demais para cantar.", C_RED)
        return
    audience = [k for k, n in g.npcs.items() if n.map == "bar"]

    def pick(i):
        if i >= len(SONGS):
            return
        g.energy -= 8

        def done(k):
            acc = k.accuracy
            rank = k.rank()
            tips = int(acc * 1.6) + (40 if rank == "S" else 0) + 5 * len(audience)
            if "dermatologia" in getattr(g, "buffs", ()):
                tips = int(tips * 1.5)
            g.money += tips
            if acc > g.stats.get("karaoke_best", 0):
                g.stats["karaoke_best"] = int(acc)
            if rank == "S":
                g.stats["karaoke_s"] = 1
            g.toasts.push(f"Karaokê: nota {rank}! A plateia deixou ${tips} de gorjeta.", C_GOLD)
            for key in audience:
                if rank in ("S", "A", "B"):
                    g.add_friendship(key, 25 if key in ("lucy", "vittoria") else 12)
                    g.npc_emote(g.npcs[key], "coracao" if key in (g.dating, g.partner) else "musica")
            if "lucy" in audience and rank in ("S", "A"):
                g.toasts.push("A Lucy assobiou e gritou 'Bis!'", C_PINK)
            g.minutes += 30
        g.push(Karaoke(SONGS[i], done, audience))
    who = ", ".join(NPCS[k]["short"] for k in audience) if audience else "uns desconhecidos"
    g.push(ui.Choice(f"Karaokê! Na plateia: {who}. Escolha a música:",
                     [f"{s['title']}  ({['fácil', 'médio', 'médio', 'difícil'][i]})" for i, s in enumerate(SONGS)]
                     + ["Agora não"], pick))


# ---------------------------------------------------------------------------
# Cinema
# ---------------------------------------------------------------------------

MOVIES = [
    dict(title="O Último Kryptoniano", genre="ficção científica", kind="space",
         caps=["Um planeta distante explode em luz verde...", "Uma nave minúscula atravessa as estrelas.",
               "'Ele não é daqui', diz a narradora. 'Mas escolheu ficar.'"]),
    dict(title="Amor em Midvale", genre="romance", kind="romance",
         caps=["Duas garotas, um farol e um verão inteiro.", "'Você volta no ano que vem?'",
               "A plateia inteira suspira ao mesmo tempo."]),
    dict(title="A Mansão da Rua Siegel", genre="terror", kind="horror",
         caps=["Um trovão. Uma porta que range sozinha.", "Alguém na fileira de trás grita antes da hora.",
               "...era só o gato. Era SÓ o gato. Né?"]),
    dict(title="Velozes em National City", genre="ação", kind="action",
         caps=["Perseguição pela Avenida Siegel!", "Um caminhão, uma ponte e zero respeito pela física.",
               "Explosão em câmera lenta. Óculos escuros. Aplausos."]),
    dict(title="O Gato Detetive", genre="animação", kind="cat",
         caps=["Inspetor Bigode está de volta!", "Ele segue pegadas de leite derramado até o vilão.",
               "Final feliz e uma música grudenta. Você vai cantar isso amanhã."]),
    dict(title="Marés de Gotham", genre="drama", kind="rain",
         caps=["Chuva no porto de Gotham.", "Uma carta que nunca foi enviada.",
               "Você não chorou. Foi a pipoca. Estava salgada."]),
]


def movies_today(g):
    n = g.abs_day()
    return [MOVIES[(n + i * 2) % len(MOVIES)] for i in range(3)]


class MovieScene(ui.Modal):
    DUR = 9.0

    def __init__(self, movie, companion, on_done):
        self.m = movie
        self.companion = companion
        self.on_done = on_done
        self.t = 0.0
        rnd = random.Random(movie["title"])
        self.stars = [(rnd.random(), rnd.random(), rnd.random()) for _ in range(70)]
        self.heads = [(rnd.randrange(0, SCREEN_W), rnd.choice((0, 1, 2)), rnd.choice(
            [(40, 30, 40), (60, 40, 30), (30, 26, 34), (90, 60, 40)])) for _ in range(26)]

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and (ev.key in ui.CONFIRM or ev.key in ui.CANCEL) and self.t > 1.0:
            self.t = self.DUR

    def update(self, dt):
        self.t += dt
        if self.t >= self.DUR and not self.done:
            self.done = True
            self.on_done()

    def draw(self, surf):
        surf.fill((8, 4, 12))
        scr = pygame.Rect(140, 50, SCREEN_W - 280, 400)
        pygame.draw.rect(surf, (150, 30, 50), scr.inflate(40, 30))
        view = pygame.Surface(scr.size)
        self.draw_film(view)
        k = min(1.0, self.t / 0.8, max(0.0, (self.DUR - self.t) / 0.8))
        dim = pygame.Surface(scr.size, pygame.SRCALPHA)
        dim.fill((0, 0, 0, int(255 * (1 - k))))
        view.blit(dim, (0, 0))
        surf.blit(view, scr.topleft)
        # plateia em silhueta
        for (x, row, col) in self.heads:
            y = SCREEN_H - 150 + row * 50
            pygame.draw.circle(surf, col, (x, y), 22)
            pygame.draw.rect(surf, col, (x - 30, y + 14, 60, 80), border_radius=14)
        for row in range(3):
            pygame.draw.rect(surf, (70, 14, 26), (0, SCREEN_H - 110 + row * 50, SCREEN_W, 18))
        cx = SCREEN_W // 2
        for (dx, col) in ((-34, (40, 34, 48)), (34, (60, 40, 50))):
            pygame.draw.circle(surf, col, (cx + dx, SCREEN_H - 120), 26)
            pygame.draw.rect(surf, col, (cx + dx - 34, SCREEN_H - 104, 68, 110), border_radius=16)
        if self.companion and self.t > self.DUR * 0.55:
            from .cutscenes import draw_emote
            draw_emote(surf, cx + 34, SCREEN_H - 156, "coracao", min(1.0, (self.t - self.DUR * 0.55) * 2))
        caps = self.m["caps"]
        i = min(len(caps) - 1, int(self.t / (self.DUR / len(caps))))
        ui.text(surf, caps[i], (cx, scr.bottom + 26), 20, C_TEXT, center=True)
        ui.text(surf, f"{self.m['title']}  ·  {self.m['genre']}", (cx, 16), 16, C_MUTED, center=True)

    def draw_film(self, s):
        w, h = s.get_size()
        t = self.t
        kind = self.m["kind"]
        if kind == "space":
            s.fill((6, 8, 26))
            for (x, y, z) in self.stars:
                xx = (x * w - t * 40 * (0.3 + z)) % w
                pygame.draw.circle(s, (255, 255, 255), (int(xx), int(y * h)), 1 + int(z * 1.5))
            pygame.draw.circle(s, (90, 255, 140), (int(w * 0.25), int(h * 0.45)), int(40 + 30 * min(1, t / 3)))
            sx = int(w * 0.2 + t * 70) % w
            pygame.draw.polygon(s, (220, 220, 240), [(sx, h // 2), (sx - 30, h // 2 - 10), (sx - 30, h // 2 + 10)])
            pygame.draw.line(s, (120, 180, 255), (sx - 30, h // 2), (sx - 70, h // 2), 3)
        elif kind == "romance":
            s.fill(mix((255, 170, 120), (120, 80, 160), min(1, t / self.DUR)))
            pygame.draw.circle(s, (255, 220, 150), (w // 2, int(h * 0.75)), 90)
            pygame.draw.rect(s, (60, 70, 120), (0, int(h * 0.75), w, h))
            pygame.draw.rect(s, (250, 250, 250), (w - 140, int(h * 0.3), 24, int(h * 0.45)))
            pygame.draw.rect(s, (220, 60, 60), (w - 140, int(h * 0.3), 24, 16))
            for (dx, c) in ((-28, (40, 30, 50)), (28, (50, 30, 40))):
                gap = max(0, 60 - t * 8)
                x = w // 2 + (dx // abs(dx)) * int(gap / 2 + 14)
                pygame.draw.circle(s, c, (x, int(h * 0.58)), 14)
                pygame.draw.rect(s, c, (x - 12, int(h * 0.58) + 10, 24, 50), border_radius=6)
            if t > 5:
                for i in range(5):
                    y = h * 0.5 - (t - 5) * 40 - i * 30
                    art_h = art.heart(True, 3)
                    s.blit(art_h, (w // 2 - 10 + int(math.sin(t * 2 + i) * 30), int(y)))
        elif kind == "horror":
            flash = (int(t * 10) % 37) < 2
            s.fill((200, 200, 230) if flash else (16, 14, 24))
            pygame.draw.polygon(s, (30, 26, 40), [(w // 2 - 140, h), (w // 2 - 140, 150), (w // 2, 60),
                                                  (w // 2 + 140, 150), (w // 2 + 140, h)])
            for (x, y) in ((w // 2 - 80, 190), (w // 2 + 50, 190), (w // 2 - 15, 120)):
                pygame.draw.rect(s, (240, 220, 120) if int(t * 3 + x) % 4 else (40, 30, 30), (x, y, 30, 40))
            if t > 4:
                gx = int(w * 0.75 + math.sin(t * 2) * 20)
                pygame.draw.circle(s, (240, 240, 250), (gx, int(h * 0.55)), 30)
                pygame.draw.rect(s, (240, 240, 250), (gx - 30, int(h * 0.55), 60, 60))
                for i in range(4):
                    pygame.draw.circle(s, (16, 14, 24), (gx - 22 + i * 15, int(h * 0.55) + 60), 8)
                pygame.draw.circle(s, (10, 10, 10), (gx - 10, int(h * 0.53)), 5)
                pygame.draw.circle(s, (10, 10, 10), (gx + 10, int(h * 0.53)), 5)
        elif kind == "action":
            s.fill((255, 170, 90))
            pygame.draw.rect(s, (80, 70, 90), (0, int(h * 0.7), w, h))
            for i in range(8):
                x = (i * 150 - t * 400) % (w + 150) - 100
                pygame.draw.rect(s, (110, 80, 120), (x, int(h * 0.3) - (i % 3) * 30, 90, 200))
            cx = int(w * 0.35 + math.sin(t * 3) * 30)
            pygame.draw.rect(s, (200, 30, 40), (cx, int(h * 0.7) - 30, 110, 30), border_radius=8)
            pygame.draw.circle(s, (20, 20, 20), (cx + 22, int(h * 0.7)), 12)
            pygame.draw.circle(s, (20, 20, 20), (cx + 88, int(h * 0.7)), 12)
            if t > 4:
                r = int((t - 4) * 70) % 200
                for rr, c in ((r, (255, 230, 120)), (r * 0.7, (255, 140, 60)), (r * 0.4, (255, 255, 255))):
                    pygame.draw.circle(s, c, (int(w * 0.8), int(h * 0.55)), int(rr))
        elif kind == "cat":
            s.fill((150, 210, 240))
            pygame.draw.rect(s, (110, 200, 120), (0, int(h * 0.72), w, h))
            cx = int(w * 0.2 + t * 50) % w
            cy = int(h * 0.62)
            pygame.draw.ellipse(s, (240, 160, 80), (cx - 40, cy - 10, 80, 40))
            pygame.draw.circle(s, (240, 160, 80), (cx + 40, cy - 14), 22)
            pygame.draw.polygon(s, (240, 160, 80), [(cx + 24, cy - 28), (cx + 30, cy - 50), (cx + 40, cy - 32)])
            pygame.draw.polygon(s, (240, 160, 80), [(cx + 44, cy - 32), (cx + 54, cy - 50), (cx + 58, cy - 26)])
            pygame.draw.rect(s, (60, 40, 30), (cx + 20, cy - 52, 44, 8))
            pygame.draw.rect(s, (60, 40, 30), (cx + 28, cy - 70, 28, 20))
            pygame.draw.circle(s, (30, 30, 30), (cx + 34, cy - 18), 3)
            pygame.draw.circle(s, (30, 30, 30), (cx + 48, cy - 18), 3)
            pygame.draw.circle(s, (230, 230, 240), (cx + 80, cy - 4), 14, 3)
            pygame.draw.line(s, (120, 90, 60), (cx + 70, cy + 6), (cx + 60, cy + 18), 4)
            for i in range(6):
                pygame.draw.ellipse(s, (250, 250, 250), (cx - 60 - i * 40, cy + 34, 12, 8))
        else:
            s.fill((40, 50, 70))
            for i in range(140):
                x = (i * 37 + int(t * 260)) % w
                y = (i * 53 + int(t * 600)) % h
                pygame.draw.line(s, (150, 170, 220), (x, y), (x - 4, y + 12))
            pygame.draw.rect(s, (30, 30, 40), (0, int(h * 0.75), w, h))
            pygame.draw.circle(s, (240, 220, 160), (int(w * 0.7), int(h * 0.3)), 30)
            for i in range(3):
                pygame.draw.rect(s, (20, 20, 30), (100 + i * 220, int(h * 0.45), 70, int(h * 0.3)))
            pygame.draw.circle(s, (30, 26, 36), (w // 2, int(h * 0.65)), 16)
            pygame.draw.rect(s, (30, 26, 36), (w // 2 - 14, int(h * 0.65) + 12, 28, 60), border_radius=6)


def open_cinema(g):
    if not (12 * 60 <= g.minutes < 24 * 60):
        g.say("Bilheteria: 'Sessões das 12h à meia-noite. Volte mais tarde!'")
        return
    films = movies_today(g)
    companion = None
    for key in (g.partner, g.dating):
        if key and g.npcs[key].map == "cinema":
            companion = key
            break
    price = 25 * (2 if companion else 1)

    def pick(i):
        if i >= len(films):
            return
        if g.money < price:
            g.say("Dinheiro insuficiente para o ingresso.")
            return
        g.money -= price
        movie = films[i]

        def after():
            g.stats["movies"] = g.stats.get("movies", 0) + 1
            g.minutes = min(g.minutes + 120, 25 * 60)
            for n in g.npcs.values():
                n.check_schedule(g.minutes)
            g.energy = min(g.max_energy, g.energy + 15)
            msg = {"horror": "Você pulou da cadeira duas vezes. (+15 energia, de susto)",
                   "romance": "Que filme lindo. Seu coração está quentinho. (+15 energia)",
                   "action": "Adrenalina pura! (+15 energia)", "cat": "Você saiu cantarolando a música do gato. (+15 energia)",
                   "space": "Você ficou olhando para o céu na saída. (+15 energia)",
                   "rain": "Um drama daqueles. Você está bem. Está sim. (+15 energia)"}[movie["kind"]]
            g.toasts.push(f"{movie['title']}: {msg}", C_LILAC)
            if companion:
                g.add_friendship(companion, 60 if movie["kind"] == "romance" else 40)
                g.npc_emote(g.npcs[companion], "coracao")
                g.toasts.push(f"{NPCS[companion]['short']} segurou sua mão no meio do filme.", C_PINK)
        g.push(MovieScene(movie, companion, after))
    opts = [f"{f['title']}  ({f['genre']})" for f in films]
    sub = f"Ingresso ${price}" + (f" (você e {NPCS[companion]['short']})" if companion else "")
    g.push(ui.Choice(f"Cine National — em cartaz hoje. {sub}. A sessão dura 2h.", opts + ["Agora não"], pick))


def buy_popcorn(g):
    if g.money < 15:
        g.toasts.push("Dinheiro insuficiente.", C_RED)
        return
    if g.add_item("pipoca"):
        g.money -= 15
        g.toasts.push("Comprou Pipoca. Cheirinho de cinema!", C_GREEN, "pipoca")
    else:
        g.toasts.push("Mochila cheia.", C_RED)


# ---------------------------------------------------------------------------
# Terraço: céu de fundo
# ---------------------------------------------------------------------------

def _sky_colors(minutes):
    keys = [(5 * 60, (30, 26, 70), (90, 60, 110)), (7 * 60, (120, 170, 230), (255, 200, 170)),
            (12 * 60, (90, 160, 240), (190, 225, 255)), (17 * 60, (110, 150, 220), (255, 190, 140)),
            (18 * 60 + 40, (90, 70, 150), (255, 130, 90)), (20 * 60, (24, 20, 60), (70, 50, 110)),
            (26 * 60, (12, 10, 34), (34, 26, 70))]
    m = minutes if minutes >= 5 * 60 else minutes + 24 * 60
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a[0] <= m <= b[0]:
            k = (m - a[0]) / (b[0] - a[0])
            return mix(a[1], b[1], k), mix(a[2], b[2], k)
    return keys[-1][1], keys[-1][2]


def draw_backdrop(g, surf, m, minutes):
    w, h = surf.get_size()
    bucket = (minutes // 10) * 10
    night = minutes >= 19 * 60 + 30 or minutes < 6 * 60

    def make():
        top, bot = _sky_colors(bucket)
        s = pygame.Surface((w, h))
        for y in range(h):
            pygame.draw.line(s, mix(top, bot, y / h), (0, y), (w, y))
        rnd = random.Random(3)
        if night:
            for _ in range(80):
                P(s, (255, 255, 255) if rnd.random() < 0.5 else (200, 200, 255), rnd.randrange(w), rnd.randrange(h // 2))
        # silhueta da cidade
        x = 0
        col = mix(bot, (20, 16, 40), 0.65)
        while x < w:
            bw = rnd.randint(30, 80)
            bh = rnd.randint(60, 220)
            R(s, col, x, h - bh, bw - 4, bh)
            for yy in range(h - bh + 8, h - 6, 12):
                for xx in range(x + 5, x + bw - 10, 9):
                    if rnd.random() < (0.45 if night else 0.08):
                        R(s, (255, 220, 140), xx, yy, 4, 5)
            x += bw
        return s
    surf.blit(cached(("sky", w, h, bucket, night), make), (0, 0))


# ---------------------------------------------------------------------------
# Integração com o jogo
# ---------------------------------------------------------------------------

def update(g, dt):
    if g.pet:
        p = g.pet
        if p.map == g.map_name:
            p.near = math.hypot(p.x - g.player.x, p.y - g.player.y) < TILE * 6
        last = getattr(g, "_act_last_map", g.map_name)
        if last != g.map_name and p.map == last and p.near and g.map_name in ("home", "terrace") and \
                last in ("home", "terrace"):
            p.map = g.map_name
            tx, ty = g.player.tile
            p.place(tx, ty)
            p.wait = 0.4
            p.sleeping = False
        p.update(dt, g)
    g._act_last_map = g.map_name
    if g.map_name == "city" and g.forage:
        pickup_forage(g)


def world_items(g, m):
    if g.pet and g.pet.map == m.name:
        return [(g.pet.base_y, 1, "pet", g.pet)]
    return []


def resolve(g, fx, fy):
    p = pet_at(g, fx, fy)
    if p:
        return ("pet", p)
    return None


OBJ_LABELS = {"telescope": "Olhar pelo telescópio", "watering": "Regar tudo (regador)", "petstand": "Abrigo Patinhas",
              "ticket": "Bilheteria", "popcorn": "Pipoca ($15)", "lounger": "Descansar na espreguiçadeira",
              "petbed": "Caminha do pet"}


def object_label(g, o):
    k = o.kind
    if k == "plot":
        return plot_label(g, o)
    if k == "jukebox":
        return "Karaokê!" if (g.minutes >= 18 * 60 or g.minutes < 2 * 60) else "Jukebox"
    if k == "seat":
        return "Poltrona"
    return OBJ_LABELS.get(k)


TELESCOPE_DAY = ["Você vê a sacada da CatCo. A Lucy está digitando furiosamente.",
                 "O letreiro da Luthor Corp brilha lá embaixo. Bonito, né? Foi você que aprovou.",
                 "Um barco do Seu Joca está voltando para o píer. Parece que pescou bem.",
                 "Dá para ver a fila no Grão Nobre daqui. O Rafa está correndo de um lado pro outro."]
TELESCOPE_NIGHT = ["Uma estrela cadente! ...Espera. Estrelas fazem curva?",
                   "A Lua está enorme hoje. Dá para ver as crateras.",
                   "As luzes de National City parecem um segundo céu.",
                   "Um ponto vermelho e azul cruza o céu muito rápido. Deve ser um avião. Deve."]


def use_object(g, o):
    """Retorna True se o objeto foi tratado aqui."""
    k = o.kind
    if k == "plot":
        use_plot(g, o)
    elif k == "watering":
        water_all(g)
    elif k == "petstand":
        open_adoption(g)
    elif k == "telescope":
        night = g.minutes >= 19 * 60 or g.minutes < 6 * 60
        g.say(random.choice(TELESCOPE_NIGHT if night else TELESCOPE_DAY))
    elif k == "lounger":
        if g.rested:
            g.toasts.push("Você já descansou aqui hoje. Bom demais, né?", C_MUTED)
        elif g.minutes >= 23 * 60:
            g.toasts.push("Está tarde. Melhor ir para a cama.", C_MUTED)
        else:
            def pick(i):
                if i == 0:
                    g.rested = True
                    g.minutes += 60
                    for n in g.npcs.values():
                        n.check_schedule(g.minutes)
                    g.energy = min(g.max_energy, g.energy + 25)
                    view = "o pôr do sol" if 17 * 60 <= g.minutes <= 19 * 60 + 30 else (
                        "as estrelas" if g.minutes > 19 * 60 else "as nuvens passando")
                    g.toasts.push(f"Você ficou uma hora olhando {view}. (+25 energia)", C_GREEN)
            g.push(ui.Choice("Relaxar uma hora na espreguiçadeira?", ["Relaxar", "Agora não"], pick))
    elif k == "petbed":
        if g.pet:
            g.say(f"A caminha de {g.pet.name}. Tem pelo por todo lado e um brinquedo meio mordido.")
        else:
            g.say("Uma caminha de pet vazia. O Abrigo Patinhas, no calçadão, tem bichinhos esperando um lar.")
    elif k == "jukebox":
        open_karaoke(g)
    elif k == "ticket":
        open_cinema(g)
    elif k == "popcorn":
        buy_popcorn(g)
    elif k == "seat":
        g.say("Poltronas vermelhas de veludo. Para ver um filme, compre o ingresso na bilheteria.")
    elif k in ("cine_screen", "rope", "railing_plant", "string_lights", "film_poster", "film_poster2"):
        g.say({"rope": "Fila para a sala 1. Hoje está tranquila.",
               "railing_plant": "Um vaso de flores. Alguém precisa regar isso também.",
               }.get(k, "O Cine National existe desde 1952. As poltronas são originais. Infelizmente."))
    else:
        return False
    return True


def night(g, notes):
    grown = 0
    for st in g.garden.values():
        if st["watered"]:
            st["growth"] += 1
            grown += 1
        st["watered"] = False
    ready = sum(1 for st in g.garden.values() if st["growth"] >= CROPS[st["crop"]]["days"])
    if ready:
        notes.append((f"Horta: {ready} canteiro(s) prontos para colher no terraço!", C_GREEN))
    if g.weather == "chuva" and g.garden:
        for st in g.garden.values():
            st["watered"] = True
        notes.append(("Vai chover: a horta vai ser regada sozinha hoje.", (150, 200, 255)))
    g.rested = False
    if g.pet:
        p = g.pet
        chance = (0.25 + min(0.4, p.love * 0.02)) if p.petted else 0.05
        if random.random() < chance:
            gift = random.choice(["concha", "flor_silvestre", "amora", "vidro_mar"] + (["trevo4"] if p.love > 15 else []))
            if g.add_item(gift):
                notes.append((f"{p.name} deixou {ITEMS[gift]['name']} ao lado da sua cama!", C_PINK))
        if not p.petted:
            p.love = max(0, p.love - 1)
        p.petted = False
        place_pet(g)
    spawn_forage(g)

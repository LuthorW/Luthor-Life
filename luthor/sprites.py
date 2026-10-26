"""Personagens no estilo Stardew Valley (16x32 px de arte, mesmo tamanho de pixel do cenário).

Cabeça grande (12 px) e redonda, olhos grandes com brilho e nariz, cabelo em mechas com três tons, roupa com luz e
sombra, braços de 2 px com mãos, sapatos com sola e contorno escuro na cor de cada parte.
Cada personagem pode ter uma roupa ("outfit" no look): shirt, blazer, coat (jaleco), chef, apron
(avental), vest (colete), cardigan, fisher (colete de pesca) e blouse. O corpo continua magrinho.

Letras da grade:
  H/h/D cabelo (base, brilho, sombra)   S/s/N pele (base, sombra, pescoço)   L/I/i/W olhos   B blush  M boca
  C/Q/c roupa (base, luz, sombra)   A/a detalhe   Z/z camisa branca   T estetoscópio
  P/R/p calça (base, luz, sombra)   O/o/U sapato (base, brilho, sola)   K/k boné
Substitui art._frames; quem chama continua usando art.character_frames(look).
"""
import pygame

from . import art
from .art import up, mix, shade

W, H = 16, 32

# cabeça: (y, x0, x1) — de frente/de costas (12 px de largura) e de perfil (virada para a direita)
HEAD_FRONT = [(2, 5, 10), (3, 4, 11), (4, 3, 12), (5, 2, 13), (6, 2, 13), (7, 2, 13), (8, 2, 13), (9, 2, 13),
              (10, 2, 13), (11, 2, 13), (12, 2, 13), (13, 2, 13), (14, 3, 12), (15, 4, 11)]
HEAD_SIDE = [(2, 6, 10), (3, 5, 11), (4, 4, 12), (5, 3, 13), (6, 3, 13), (7, 3, 13), (8, 3, 13), (9, 3, 13),
             (10, 3, 13), (11, 3, 14), (12, 3, 13), (13, 3, 13), (14, 4, 12), (15, 5, 11)]

# ---------------------------------------------------------------------------
# Cabelos (máscaras 16 colunas; "." = sem cabelo). De frente/perfil, linhas >= 16 ficam atrás do corpo.
# ---------------------------------------------------------------------------
_TOP = [
    "................",
    ".....HHHHHD.....",
    "....HhhhHHHD....",
    "...HhhHHHHHHD...",
    "..HhhHHHHHHHHD..",
    ".HhhHHHHHHHHHHD.",
    ".HhHHHHHHDHHHHD.",
    ".HHHHHHHDHHHHHD.",
    ".HHHHDHHHHHDHHD.",              # franja (linha 8)
]
_TIPS = ".HHD..H..D..DHD."            # pontas da franja, sem cobrir os olhos
HAIR = {
    ("long", "front"): _TOP + [_TIPS] + [".HH..........HD."] * 4 + [".HD..........DD."] * 3 + [
        ".HD..........DD.", ".HD..........DD.", ".HD..........DD.", ".HD..........DD.", ".HD..........DD.",
        "..D..........D.."],
    ("wavy", "front"): _TOP[:5] + [
        "HHhhHHHHHHHHHHDD",
        "HHhHHHHHHDHHHHDD",
        "HHHHHHHHDHHHHHDD",
        ".HHHHDHHHHHDHHD.",
        "HHHD..H..D..DHDD",
        "HHH..........HDD",
        ".HH..........DHD",
        "HHD..........HDD",
        ".HH..........DHD",
        "HHD..........HDD",
        ".HH..........DHD",
        "HHD..........HDD",
        ".HH..........DHD",
        "HHD..........HDD",
        ".HD..........DD.",
        "HHD..........HDD",
        ".HD..........DD.",
    ],
    ("short", "front"): _TOP + [_TIPS, "..D..........D.."],
    ("bun", "front"): [
        "......HhHD......",
        ".....HhHHHD.....",
        "....HhhhHHHD....",
        "...HhhHHHHHHD...",
        "..HhhHHHHHHHHD..",
        ".HhhHHHHHHHHHHD.",
        ".HhHHHHHHHHHHHD.",
        ".HHHHHHHHHHHHDD.",
        ".HHHD......DHHD.",
        ".HD..........DD.",
        "..D..........D..",
    ],
    ("cap", "front"): [
        "................",
        ".....KKKKKk.....",
        "....KKAAKKKk....",
        "...KKKKKKKKKk...",
        "..KKKKKKKKKKKk..",
        ".KKKKKKKKKKKKKk.",
        ".kkkkkkkkkkkkkk.",
        "kkkkkkkkkkkkkkkk",
        ".HD..........DH.",
        ".H............D.",
        ".H............D.",
    ],
}
_BACK_TOP = [
    "................",
    ".....HHHHHD.....",
    "....HhhhHHHD....",
    "...HhhHHHHHHD...",
    "..HhhHHHHHHHHD..",
    ".HhHHHDHHHDHHHD.",
    ".HHHHHDHHHDHHHD.",
    ".HHHHDHHHHDHHHD.",
    ".HHHHDHHHDHHHHD.",
    ".HHHHDHHHDHHHHD.",
    ".HHHHDHHHDHHHDD.",
    ".HHHDHHHHDHHHDD.",
    ".HHHDHHHHDHHHDD.",
    "..HHDHHHHDHHDD..",
    "..HHHDHHHDHHHD..",
    "...HHDHHHDHHD...",
]
HAIR.update({
    ("long", "back"): _BACK_TOP + [
        "...HHDHHHDHHD...",
        "...HHDHHHDHHD...",
        "....HDHHHDHH....",
        "....HDHHHDHH....",
        "....HDHHHDHD....",
        "....HDHHHDHD....",
        "....HHDHHHDD....",
        ".....DHHHHD.....",
    ],
    ("wavy", "back"): _BACK_TOP + [
        "..HHHDHHHDHHHD..",
        "...HHDHHHDHHD...",
        "..HHHDHHHDHHHD..",
        "...HHDHHHDHHD...",
        "....HDHHHDHH....",
        "...HHDHHHDHHD...",
        "....HHDHHDHD....",
    ],
    ("short", "back"): _BACK_TOP[:-1] + ["...HHHHHHHHHD..."],
    ("bun", "back"): ["......HhHD......", ".....HhHHHD....."] + _BACK_TOP[2:-1] + ["...HHHHHHHHHD..."],
    ("cap", "back"): ["................", ".....KKKKKk.....", "....KKKKKKKk....", "...KKKKKKKKKk...",
                      "..KKKKKKKKKKKk..", ".KKKKKKKKKKKKKk.", ".kkkkkkkkkkkkkk."] + _BACK_TOP[7:-1] + [
                      "...HHHHHHHHHD..."],
})
_SIDE_TOP = [
    "................",
    "......HHHHD.....",
    ".....HhhHHHD....",
    "....HhhHHHHHD...",
    "...HhHHHHHHHHD..",
    "..HHHHHHHHHHHHD.",
    "..HHHHHHHHHHHHD.",
    "..HHHHHHHDHHHHD.",
    "..HHHHHHHD.HHD..",
    "..HHHHHHD.......",
    "..HHHHHH........",
]
HAIR.update({
    ("long", "side"): _SIDE_TOP + [
        "..HHHHH.........", "..HHHHD.........", "..HHHD..........", "..HHHD..........", "..HHHD..........",
        "..HHD...........", "..HHD...........", "..HHD...........", "..HHD...........", "..HD............",
        "..HD............", "...D............"],
    ("wavy", "side"): _SIDE_TOP + [
        ".HHHHHH.........", "..HHHHD.........", ".HHHHD..........", "..HHHD..........", ".HHHD...........",
        "..HHHD..........", ".HHHD...........", "..HHD...........", ".HHHD...........", "..HD............"],
    ("short", "side"): _SIDE_TOP[:10] + ["..HHHHH.........", "..HHHHD.........", "...HHD..........",
                                         "....D..........."],
    ("bun", "side"): ["..HHH...........", ".HhHHDHHHD......"] + _SIDE_TOP[2:10] + [
        "..HHHHH.........", "..HHHHD.........", "...HHD..........", "....D..........."],
    ("cap", "side"): ["................", "......KKKKk.....", ".....KKKKKKk....", "....KKKKKKKKk...",
                      "...KKAKKKKKKKk..", "..KKKKKKKKKKKKk.", "..kkkkkkkkkkkkkk", "..HHHHHD........",
                      "..HHHHD.........", "..HHHHD.........", "..HHHHH.........", "..HHHD..........",
                      "...HD..........."],
})


def _palette(look):
    hair, skin, cloth, acc = look["hair"], look["skin"], look["cloth"], look["accent"]
    eyes = look.get("eyes", (70, 46, 40))
    light = sum(hair) > 300
    pants = look["pants"]
    return {
        "H": hair, "h": mix(hair, (255, 250, 235), 0.42 if light else 0.32), "D": shade(hair, 0.66),
        "S": skin, "s": shade(skin, 0.86), "N": shade(skin, 0.74),
        "L": mix(eyes, (16, 10, 18), 0.78), "I": eyes, "i": shade(eyes, 0.62), "W": (250, 250, 255),
        "B": mix(skin, (255, 110, 130), 0.4), "M": mix(skin, (160, 46, 66), 0.6),
        "C": cloth, "Q": mix(cloth, (255, 255, 255), 0.24), "c": shade(cloth, 0.74),
        "A": acc, "a": shade(acc, 0.74), "Z": (238, 238, 244), "z": (196, 196, 210), "T": (70, 74, 86),
        "P": pants, "R": mix(pants, (255, 255, 255), 0.16), "p": shade(pants, 0.7),
        "O": look["shoes"], "o": mix(look["shoes"], (255, 255, 255), 0.35), "U": shade(look["shoes"], 0.6),
        "K": acc, "k": shade(acc, 0.7),
    }


class Grid:
    def __init__(self):
        self.px = {}

    def set(self, x, y, k):
        if 0 <= x < W and 0 <= y < H:
            self.px[(x, y)] = k

    def row(self, y, x0, x1, k):
        for x in range(x0, x1 + 1):
            self.set(x, y, k)

    def mask(self, rows, behind=None):
        """behind=True: só linhas >= 16; False: só < 16; None: todas."""
        for y, line in enumerate(rows):
            if behind is True and y < 16 or behind is False and y >= 16:
                continue
            for x, ch in enumerate(line):
                if ch != ".":
                    self.set(x, y, ch)


def _hair(style, view):
    return HAIR.get((style, view)) or HAIR[("short", view)]


# ---------------------------------------------------------------------------
# Cabeça e rosto
# ---------------------------------------------------------------------------

def _head(g, view, style, blink):
    """Rosto no estilo original do jogo (olhos grandes com brilho), agora maior e com nariz."""
    if view == "back":
        g.row(16, 6, 9, "N")
        return
    if view == "front":
        for (y, x0, x1) in HEAD_FRONT:
            g.row(y, x0, x1, "S")
        for y in range(7, 14):                  # sombra do lado direito do rosto
            g.set(13, y, "s")
        g.set(12, 14, "s"); g.set(11, 15, "s")
        g.row(15, 5, 10, "s")
        if style in ("short", "bun", "cap"):    # orelhas
            for y in (10, 11):
                g.set(1, y, "S"); g.set(14, y, "s")
            g.set(1, 11, "s")
        if blink:
            g.row(11, 4, 5, "L"); g.row(11, 10, 11, "L")
            g.set(3, 10, "L"); g.set(12, 10, "L")
        else:
            g.row(9, 4, 5, "L"); g.row(9, 10, 11, "L")          # cílios
            g.set(3, 10, "L"); g.set(12, 10, "L")               # cantinho dos cílios
            g.set(4, 10, "W"); g.set(5, 10, "I")                # brilho + íris
            g.set(10, 10, "W"); g.set(11, 10, "I")
            g.set(4, 11, "I"); g.set(5, 11, "i")
            g.set(10, 11, "I"); g.set(11, 11, "i")
        g.set(3, 12, "B"); g.set(4, 12, "B"); g.set(11, 12, "B"); g.set(12, 12, "B")
        g.set(7, 11, "s"); g.set(7, 12, "s"); g.set(8, 12, "N")   # nariz
        g.set(7, 14, "M"); g.set(8, 14, "M")
    else:
        for (y, x0, x1) in HEAD_SIDE:
            g.row(y, x0, x1, "S")
        g.row(15, 5, 11, "s"); g.set(12, 14, "s")
        g.set(8, 10, "s"); g.set(8, 11, "s"); g.set(9, 11, "N")   # orelha
        if blink:
            g.row(11, 11, 12, "L")
        else:
            g.row(9, 11, 12, "L")
            g.set(11, 10, "W"); g.set(12, 10, "I")
            g.set(11, 11, "I"); g.set(12, 11, "i")
        g.set(10, 12, "B"); g.set(11, 12, "B")
        g.set(14, 11, "S"); g.set(14, 12, "s"); g.set(13, 12, "N")   # nariz
        g.set(13, 14, "M")


# ---------------------------------------------------------------------------
# Corpo e roupas
# ---------------------------------------------------------------------------

def _legs_front(g, frame, view, long_top=False):
    lift_l = 1 if frame == 2 else 0
    lift_r = 1 if frame == 1 else 0
    if view == "back":
        lift_l, lift_r = lift_r, lift_l
    g.row(23, 5, 10, "P")
    g.set(10, 23, "p")
    for (x0, lift) in ((5, lift_l), (8, lift_r)):
        end = 27 - lift
        for y in range(24, end + 1):
            g.row(y, x0, x0 + 2, "P")
            g.set(x0 + 2, y, "p")
        g.set(x0, 24, "R"); g.set(x0, 25, "R")
        g.row(end + 1, x0, x0 + 2, "O")
        g.set(x0 if view == "front" else x0 + 1, end + 1, "o")
        g.row(end + 2, x0, x0 + 2, "U")


def _legs_side(g, frame):
    g.row(23, 5, 9, "P")
    if frame == 0:
        for y in range(24, 28):
            g.row(y, 6, 8, "P"); g.set(6, y, "p"); g.set(8, y, "R")
        g.row(28, 6, 9, "O"); g.set(9, 28, "o")
        g.row(29, 6, 9, "U")
        return
    big = frame == 1
    back = [(24, 5, 6), (25, 5, 6), (26, 4, 5), (27, 4 - big, 5 - big)]
    front = [(24, 8, 9), (25, 8, 9), (26, 9, 10), (27, 9 + big, 10 + big)]
    for (y, a, b) in back:
        g.row(y, a, b, "p")
    for (y, a, b) in front:
        g.row(y, a, b, "P"); g.set(b, y, "R")
    g.row(28, 3 - big, 5 - big, "O"); g.row(29, 3 - big, 5 - big, "U")
    g.row(28, 9 + big, 11 + big, "O"); g.set(11 + big, 28, "o"); g.row(29, 9 + big, 11 + big, "U")


def _arm(g, x, top, d, col_out, col_in, sleeve_end=None, hand=True):
    """Braço de 2 px (x, x+1) do ombro até a mão. d desloca a mão (balanço ao andar)."""
    end = 21 + d
    for y in range(top, end + 1):
        g.set(x, y, col_out); g.set(x + 1, y, col_in)
    if sleeve_end is not None:          # manga curta/dobrada: antebraço de pele
        for y in range(sleeve_end + 1, end + 1):
            g.set(x, y, "S"); g.set(x + 1, y, "s")
    if hand:
        g.set(x, end + 1, "S"); g.set(x + 1, end + 1, "s")
        g.set(x, end + 2, "s")


def _torso_front(g, outfit, view):
    for y in range(17, 23):
        g.row(y, 5, 10, "C")
        g.set(10, y, "c")
    g.row(17, 4, 11, "C")
    g.set(11, 17, "c")
    if view == "front":
        g.set(6, 18, "Q"); g.set(6, 19, "Q"); g.set(5, 18, "Q")
    else:
        g.set(9, 18, "Q"); g.set(9, 19, "Q")
    if outfit == "coat":
        for y in range(23, 26):
            g.row(y, 4, 11, "C"); g.set(11, y, "c")
        g.row(26, 4, 11, "c")
    if view == "back":
        if outfit == "apron":
            for (x, y) in ((6, 18), (9, 18), (7, 19), (8, 19), (6, 20), (9, 20)):
                g.set(x, y, "A")
            g.row(22, 6, 9, "A"); g.set(7, 23, "A"); g.set(8, 23, "a")
        elif outfit == "blazer":
            g.set(7, 21, "c"); g.set(7, 22, "c")
        elif outfit == "coat":
            g.set(7, 23, "c"); g.set(7, 24, "c"); g.set(7, 25, "c")
            g.row(21, 6, 9, "c")
        elif outfit == "vest":
            g.row(17, 4, 11, "Z")
        return
    # frente
    if outfit == "shirt":
        g.set(6, 17, "A"); g.set(9, 17, "A"); g.set(7, 17, "N"); g.set(8, 17, "N")
        g.set(7, 19, "c"); g.set(7, 21, "c")
    elif outfit == "blouse":
        g.row(17, 5, 10, "Q"); g.set(7, 17, "N"); g.set(8, 17, "N")
        g.set(7, 18, "Q"); g.set(8, 18, "Q")
        g.row(22, 5, 10, "A")
    elif outfit == "blazer":
        for y in (17, 18, 19):
            g.set(7, y, "A"); g.set(8, y, "A")
        g.set(7, 17, "N"); g.set(8, 17, "N")
        g.set(6, 17, "Q"); g.set(6, 18, "Q"); g.set(9, 17, "Q"); g.set(9, 18, "Q")
        g.set(8, 19, "a")
        g.set(8, 20, "c"); g.set(8, 21, "k" if False else "c")
        g.set(9, 19, "A")                                 # lencinho no bolso
        g.row(22, 5, 10, "c")
    elif outfit == "coat":
        for y in range(17, 26):
            g.set(7, y, "A"); g.set(8, y, "a")
        g.set(7, 17, "N"); g.set(8, 17, "N")
        g.set(6, 17, "T"); g.set(9, 17, "T"); g.set(6, 18, "T"); g.set(9, 18, "T")
        g.set(9, 19, "T"); g.set(9, 20, "T")
        g.set(5, 21, "c"); g.set(10, 21, "c"); g.set(10, 20, "A")
        g.set(5, 24, "c"); g.set(10, 24, "c")
    elif outfit == "chef":
        g.row(17, 6, 9, "A"); g.set(7, 18, "A"); g.set(8, 18, "a")
        for y in (19, 21):
            g.set(6, y, "c"); g.set(9, y, "c")
        g.row(22, 5, 10, "z")
    elif outfit == "apron":
        g.set(6, 17, "A"); g.set(9, 17, "A"); g.set(7, 17, "N"); g.set(8, 17, "N")
        g.row(18, 6, 9, "A")
        for y in range(19, 26):
            g.row(y, 5, 10, "A"); g.set(10, y, "a")
        g.row(22, 7, 8, "a")
    elif outfit == "vest":
        g.row(17, 6, 9, "Z"); g.set(7, 17, "A"); g.set(8, 17, "A")
        g.set(7, 18, "Z"); g.set(8, 18, "Z"); g.set(7, 19, "Z"); g.set(8, 19, "z")
        g.set(7, 20, "c"); g.set(7, 22, "c")
    elif outfit == "cardigan":
        for y in range(17, 23):
            g.set(7, y, "A"); g.set(8, y, "a")
        g.set(7, 17, "N"); g.set(8, 17, "N")
        g.set(6, 19, "c"); g.set(6, 21, "c")
    elif outfit == "fisher":
        g.row(17, 6, 9, "A"); g.set(7, 17, "N"); g.set(8, 17, "N")
        for (x, y) in ((5, 20), (6, 20), (5, 21), (9, 20), (10, 20), (10, 21)):
            g.set(x, y, "c")
        g.set(6, 19, "Q")


def _body_front(g, outfit, view, frame):
    g.row(16, 6, 9, "N")
    _torso_front(g, outfit, view)
    la, ra = {0: (0, 0), 1: (1, -1), 2: (-1, 1)}[frame]
    if view == "back":
        la, ra = ra, la
    sleeve = {"vest": 19, "apron": 20, "fisher": 19}.get(outfit)
    arm_out, arm_in = ("Z", "z") if outfit == "vest" else ("A", "a") if outfit == "fisher" else ("Q", "C")
    _arm(g, 3, 18, la, arm_out, arm_in, sleeve)
    _arm(g, 11, 18, ra, "C" if outfit not in ("vest", "fisher") else arm_in, "c" if outfit != "vest" else "z",
         sleeve)
    _legs_front(g, frame, view)
    if outfit in ("coat",):
        for y in range(23, 26):              # o jaleco cobre o alto das pernas
            g.row(y, 4, 11, "C"); g.set(11, y, "c")
            if view == "front":
                g.set(7, y, "A"); g.set(8, y, "a")
        g.row(26, 4, 6, "c"); g.row(26, 9, 11, "c")
        if view == "back":
            g.set(7, 24, "c"); g.set(7, 25, "c")
    if outfit == "apron" and view == "front":
        for y in range(23, 26):
            g.row(y, 5, 10, "A"); g.set(10, y, "a")
        g.row(26, 5, 10, "a")


def _body_side(g, outfit, frame):
    g.row(16, 7, 8, "N")
    for y in range(17, 23):
        g.row(y, 5, 9, "C")
        g.set(5, y, "c")
    g.set(9, 17, "Q"); g.set(9, 18, "Q")
    if outfit == "blazer":
        g.set(9, 17, "A"); g.set(9, 18, "A"); g.set(8, 17, "Q")
    elif outfit in ("chef", "shirt", "fisher", "blouse"):
        g.set(9, 17, "A")
    elif outfit == "vest":
        g.set(9, 17, "Z"); g.set(9, 18, "Z"); g.set(10, 17, "A")
    _legs_side(g, frame)
    if outfit == "coat":
        for y in range(23, 26):
            g.row(y, 4, 9, "C"); g.set(4, y, "c")
        g.row(26, 4, 9, "c")
        g.set(9, 17, "A"); g.set(9, 18, "T")
    if outfit == "apron":
        for y in range(18, 26):
            g.set(9, y, "A"); g.set(10, y, "a")
    # braço: balança para frente (frame 1) e para trás (frame 2)
    sleeve = {"vest": 19, "apron": 20, "fisher": 19}.get(outfit)
    out, inn = ("Z", "z") if outfit == "vest" else ("A", "a") if outfit == "fisher" else ("C", "c")
    if frame == 0:
        _arm(g, 6, 18, 0, out, inn, sleeve)
    else:
        dx = 1 if frame == 1 else -1
        for y in range(18, 21):
            g.set(6, y, out); g.set(7, y, inn)
        g.set(6 + dx, 21, out); g.set(7 + dx, 21, inn)
        g.set(6 + 2 * dx, 22, "S"); g.set(7 + 2 * dx, 22, "s")
        if sleeve is not None:
            g.set(6 + dx, 21, "S"); g.set(7 + dx, 21, "s")


def _render(g, pal):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for (x, y), k in g.px.items():
        s.set_at((x, y), pal.get(k, (255, 0, 255)))
    out = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(H):
        for x in range(W):
            if (x, y) in g.px:
                continue
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                n = g.px.get((x + dx, y + dy))
                if n:
                    c = pal.get(n, (0, 0, 0))
                    out.set_at((x, y), (*mix(shade(c, 0.36), (34, 18, 30), 0.45), 255))
                    break
    out.blit(s, (0, 0))
    return out


def _frames(look, blink=False):
    pal = _palette(look)
    style = look.get("style", "short")
    outfit = look.get("outfit", "shirt")
    out = {}
    for d, view in (("down", "front"), ("up", "back"), ("right", "side")):
        hair = _hair(style, view)
        for i, fr in enumerate([0, 1, 0, 2]):
            g = Grid()
            if view != "back":
                g.mask(hair, behind=True)          # cabelo comprido atrás do corpo
            if view == "side":
                _body_side(g, outfit, fr)
            else:
                _body_front(g, outfit, view, fr)
            _head(g, view, style, blink)
            g.mask(hair, behind=False if view != "back" else None)
            img = up(_render(g, pal))
            out[(d, i)] = img
            if d == "right":
                out[("left", i)] = pygame.transform.flip(img, True, False)
    return out


art._frames = _frames

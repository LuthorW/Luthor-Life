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
_TIPS = ".HHD........DHD."            # pontas da franja só nos cantos: a testa e os olhos ficam livres
_FRINGE = ".HHHHD....DHHHD."          # franja aberta no meio: aparece um pedaço da testa
HAIR = {
    # mechas laterais por fora do rosto (colunas 0-1 e 14-15), para o rosto inteiro aparecer
    ("long", "front"): _TOP[:8] + [_FRINGE, "HHD..........DHD"] + ["HH............HD"] * 3 + ["HD............DD"] * 3 + [
        "HD............DD", "HD............DD", ".H............D.", ".H............D.", ".D............D.",
        "................"],
    ("wavy", "front"): _TOP[:5] + [
        "HHhhHHHHHHHHHHDD",
        "HHhHHHHHHDHHHHDD",
        "HHHHHHHHDHHHHHDD",
        "HHHHHD....DHHHDD",
        "HHD..........DHD",
        "HHD..........DHD",
        "HH............DH",
        ".HH..........HD.",
        "HH............DH",
        ".HH..........HD.",
        "HH............DH",
        ".H............D.",
        "HH............DH",
        ".H............D.",
        "HD............DD",
        ".H............D.",
        "HD............DD",
    ],
    ("short", "front"): _TOP[:8] + [_FRINGE, ".HD..........DD.", "..D..........D.."],
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
        "K": acc, "k": shade(acc, 0.7), "J": (222, 180, 84), "E": (90, 230, 240),
        # barba, óculos e chapéu
        "Y": shade(look.get("beard_color", hair), 0.85), "y": mix(skin, look.get("beard_color", hair), 0.45),
        "X": look.get("glasses_color", (34, 28, 34)),
        "V": look.get("hat", (110, 90, 64)), "v": shade(look.get("hat", (110, 90, 64)), 0.68),
        "F": look.get("scarf", (180, 40, 60)), "f": shade(look.get("scarf", (180, 40, 60)), 0.72),
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


# black power (Dona Graça)
HAIR.update({
    ("afro", "front"): [
        "....HHhHHHH.....",
        "..HHhhhHHHHHH...",
        ".HHhhHHHhHHHHD..",
        ".HhHHhHHHHHhHHD.",
        "HHhHHHHhHHHHHHDD",
        "HHHHhHHHHHhHHHDD",
        "HhHHHHHhHHHHHDHD",
        "HHHHHDHHHHDHHHDD",
        "HHHD........DHDD",
        "HHH..........HDD",
        "HhH..........HDD",
        ".HH..........HD.",
        ".HD..........DD.",
        "..D..........D..",
    ],
    ("afro", "back"): [
        "....HHhHHHH.....",
        "..HHhhhHHHHHH...",
        ".HHhhHHHhHHHHD..",
        "HHhHHhHHHHHhHHDD",
        "HHHHHHHhHHHHHHDD",
        "HhHHHHHHHHhHHHDD",
        "HHHHhHHHHHHHHDHD",
        "HHHHHHHHhHHHHHDD",
        "HhHHHHHHHHHHhHDD",
        "HHHHHhHHHHHHHHDD",
        "HHHHHHHHHHhHHHDD",
        "HHhHHHHHHHHHHDHD",
        ".HHHHHHhHHHHHDD.",
        "..HHHHHHHHHHDD..",
        "....HHHHHHHD....",
    ],
    ("afro", "side"): [
        "...HHHhHHH......",
        "..HHhhHHHHHH....",
        ".HHhHHHhHHHHH...",
        "HHHHhHHHHHHHHD..",
        "HhHHHHHhHHHHHD..",
        "HHHHHhHHHHHHHD..",
        "HHhHHHHHHhHHHD..",
        "HHHHHHHHHDHHD...",
        "HHHHHhHHHD......",
        "HhHHHHHH........",
        "HHHHHHH.........",
        ".HhHHHH.........",
        ".HHHHD..........",
        "..HHD...........",
    ],
})


# cabelo médio (até o queixo): Brainy, Ian
HAIR.update({
    ("medium", "front"): HAIR[("long", "front")][:13] + ["..HD........DD..", "..D..........D.."],
    ("medium", "back"): _BACK_TOP + ["...HHDHHHDHHD...", "....HDHHHDHH...."],
    ("medium", "side"): HAIR[("long", "side")][:14] + ["..HD............"],
})


def _extras(g, look, view):
    """Barba, óculos, óculos de proteção na testa, chapéu de aba larga e cachecol, por cima do rosto e do cabelo."""
    if look.get("scarf"):
        if view == "side":
            g.row(15, 6, 10, "F"); g.row(16, 5, 10, "F"); g.row(17, 6, 9, "f")
            g.set(5, 17, "F"); g.set(5, 18, "f"); g.set(4, 19, "f")       # ponta solta para trás
        else:
            g.row(15, 5, 10, "F"); g.row(16, 4, 11, "F"); g.row(17, 5, 10, "f")
            if view == "front":
                for y in (18, 19, 20):
                    g.set(9, y, "F"); g.set(10, y, "f")                  # ponta caindo na frente
                g.set(9, 21, "f")
            else:
                g.row(15, 5, 10, "f")
    if look.get("goggles"):
        if view == "side":
            g.row(6, 3, 12, "T"); g.set(10, 5, "E"); g.set(11, 5, "E"); g.set(10, 6, "E"); g.set(11, 6, "E")
        else:
            g.row(6, 2, 13, "T")
            if view == "front":
                for x in (4, 5, 10, 11):
                    g.set(x, 5, "E"); g.set(x, 6, "E")
                g.set(4, 5, "W")
    beard = look.get("beard")
    if beard and view != "back":
        k = "Y" if beard == "full" else "y"
        if view == "front":
            for (x, y) in ((3, 11), (12, 11), (3, 12), (4, 12), (11, 12), (12, 12)):
                g.set(x, y, k)
            g.row(13, 3, 12, k)
            g.row(14, 3, 6, k); g.row(14, 9, 12, k)
            g.row(15, 4, 11, k)
            if beard == "full":
                g.row(16, 6, 9, k)
        else:
            for y in range(12, 16):
                g.row(y, 9, 12, k)
            g.set(13, 13, k)
            g.set(13, 14, "M")
    if look.get("glasses") and view != "back":
        # armação fina: linha de baixo das lentes, cantinhos e ponte (os olhos continuam à mostra)
        if view == "front":
            for x0 in (3, 9):
                g.row(12, x0 + 1, x0 + 2, "X")
                g.set(x0, 11, "X"); g.set(x0 + 3, 11, "X")
                g.set(x0, 10, "X"); g.set(x0 + 3, 10, "X")
            g.set(7, 10, "X"); g.set(8, 10, "X")
        else:
            g.row(12, 11, 12, "X")
            g.set(13, 10, "X"); g.set(13, 11, "X")
            g.row(10, 8, 10, "X")
    if look.get("hat"):
        if view == "side":
            g.row(0, 5, 10, "V"); g.row(1, 4, 11, "V"); g.row(2, 4, 11, "v"); g.row(3, 4, 11, "V")
            g.row(4, 0, 15, "V"); g.row(5, 1, 14, "v")
        else:
            g.row(0, 4, 11, "V"); g.row(1, 3, 12, "V"); g.row(2, 3, 12, "v"); g.row(3, 3, 12, "V")
            g.row(4, 0, 15, "V"); g.row(5, 1, 14, "v")
            g.set(5, 0, "v"); g.set(10, 0, "v")


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


_SHORT_SLEEVES = {"on": False}       # ligado em _frames quando look["sleeves"] == "short"


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
    if _SHORT_SLEEVES["on"] and sleeve is None:
        sleeve = 19                                   # manga curta (verão)
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
    if _SHORT_SLEEVES["on"] and sleeve is None:
        sleeve = 19                                   # manga curta (verão)
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


# roupas especiais desenhadas por cima do corpo básico (base -> roupa usada para o tronco e os braços)
OUTFIT_BASE = {"trench": "plain", "peacoat": "plain", "skirt_suit": "blazer", "patterned": "blazer",
               "breton": "plain", "bartender": "vest", "tech": "plain", "labcoat": "coat",
               "leather": "plain", "captain": "blazer"}


def _outfit_overlay(g, outfit, view, frame):
    side = view == "side"
    if outfit == "trench":
        # sobretudo comprido com cinto e cachecol (Vittoria)
        x0, x1 = (4, 9) if side else (4, 11)
        for y in range(23, 27):
            g.row(y, x0, x1, "C")
            g.set(x1 if not side else x0, y, "c")
        g.row(27, x0 + 1, x1 - 1, "c") if not side else g.row(27, x0, x1 - 1, "c")
        if side:
            g.row(21, 5, 9, "c"); g.set(9, 21, "J")
            g.row(16, 7, 9, "A"); g.row(17, 7, 9, "A")
            g.set(9, 18, "A"); g.set(9, 19, "a"); g.set(10, 18, "a")
        else:
            g.row(21, 4, 11, "c")
            if view == "front":
                g.set(7, 21, "J"); g.set(8, 21, "J")
                for y in range(22, 27):
                    g.set(7, y, "c")                     # abertura do casaco
                g.row(16, 6, 9, "A"); g.row(17, 5, 10, "A")
                g.set(6, 18, "A"); g.set(6, 19, "A"); g.set(6, 20, "a")
                g.set(9, 17, "a")
                g.set(9, 19, "Q"); g.set(5, 23, "Q")
            else:
                g.row(16, 6, 9, "A"); g.row(17, 5, 10, "A")
                g.set(7, 22, "c"); g.set(7, 23, "c"); g.set(7, 24, "c")
    elif outfit == "peacoat":
        # casaco de lã trespassado, gola larga e botões dourados (Lucy)
        x0, x1 = (4, 9) if side else (4, 11)
        for y in range(23, 25):
            g.row(y, x0, x1, "C")
        g.row(25, x0, x1, "c")
        if side:
            g.set(8, 17, "Q"); g.set(9, 17, "Q"); g.set(9, 18, "Q")
            g.set(9, 20, "J"); g.set(9, 22, "J")
        elif view == "front":
            g.row(17, 4, 11, "Q"); g.set(7, 17, "N"); g.set(8, 17, "N")
            g.set(5, 18, "Q"); g.set(10, 18, "Q"); g.set(6, 18, "A"); g.set(9, 18, "A")
            for y in (19, 21, 23):
                g.set(6, y, "J"); g.set(9, y, "J")
            g.set(8, 20, "c"); g.set(8, 22, "c")
        else:
            g.row(17, 4, 11, "Q"); g.row(21, 5, 10, "c")
            g.set(6, 21, "J"); g.set(9, 21, "J")
    elif outfit == "skirt_suit":
        # blazer + saia + meia-calça (Jess)
        if side:
            for y in range(23, 26):
                g.row(y, 5, 9, "P")
            g.set(5, 25, "p")
        else:
            for y in range(23, 26):
                g.row(y, 4 if y == 25 else 5, 11 if y == 25 else 10, "P")
                g.set(11 if y == 25 else 10, y, "p")
            g.set(5, 23, "R")
            if view == "front":
                g.set(7, 18, "A"); g.set(8, 18, "A"); g.set(7, 19, "A"); g.set(8, 19, "a")
        # meia-calça escura no lugar da calça
        for (x, y), k in list(g.px.items()):
            if y >= 26 and k in ("P", "R"):
                g.px[(x, y)] = "p"
    elif outfit == "labcoat":
        # jaleco de cientista: sem estetoscópio, camisa escura por dentro e canetas no bolso (Brainy)
        for (x, y), k in list(g.px.items()):
            if k == "T":
                g.px[(x, y)] = "A" if 6 <= x <= 9 and view == "front" else "C"
        if view == "front":
            g.set(10, 19, "E"); g.set(10, 20, "J"); g.set(10, 21, "c")
            g.set(5, 23, "c"); g.set(5, 24, "c")
        elif side:
            g.set(8, 19, "E")
    elif outfit == "breton":
        # camiseta listrada de marinheiro, mangas listradas (Ian)
        for (x, y), k in list(g.px.items()):
            if 17 <= y <= 22 and k in ("C", "c", "Q"):
                g.px[(x, y)] = ("Z" if k != "c" else "z") if y % 2 == 1 else ("C" if k != "c" else "c")
        if view == "front":
            g.row(17, 6, 9, "C"); g.set(7, 17, "N"); g.set(8, 17, "N")
        elif side:
            g.set(9, 17, "C")
    elif outfit == "bartender":
        # colete de barman: pano no ombro, corrente de relógio, gravata-borboleta (Marco)
        if side:
            g.set(9, 20, "J"); g.set(8, 21, "J")
            g.set(6, 17, "Z"); g.set(6, 18, "Z"); g.set(5, 18, "z")
        elif view == "front":
            g.set(3, 17, "Z"); g.set(4, 17, "Z"); g.set(3, 18, "Z"); g.set(4, 18, "Z"); g.set(3, 19, "z")
            g.set(4, 19, "A")
            g.set(9, 20, "J"); g.set(10, 21, "J"); g.set(10, 20, "J")
            g.set(6, 20, "c"); g.set(6, 22, "c")
        else:
            g.set(11, 17, "Z"); g.set(12, 17, "Z"); g.set(11, 18, "Z"); g.set(12, 18, "Z")
            g.row(20, 6, 9, "c")
    elif outfit == "tech":
        # jaqueta tech preta: dragonas douradas e linhas de circuito brilhando (Brainy)
        if side:
            g.set(7, 17, "J"); g.set(8, 17, "J"); g.set(6, 17, "J")
            for y in (19, 20, 21):
                g.set(8, y, "E")
            g.set(9, 21, "E")
        elif view == "front":
            g.row(17, 3, 5, "J"); g.row(17, 10, 12, "J")
            g.set(3, 18, "J"); g.set(12, 18, "J")
            for (x, y) in ((6, 19), (6, 20), (6, 21), (5, 21), (9, 18), (9, 19), (10, 19), (10, 21)):
                g.set(x, y, "E")
            g.set(7, 17, "N"); g.set(8, 17, "N"); g.set(7, 18, "A")
        else:
            g.row(17, 3, 5, "J"); g.row(17, 10, 12, "J")
            for (x, y) in ((7, 19), (8, 19), (7, 20), (7, 21), (8, 21)):
                g.set(x, y, "E")
    elif outfit == "leather":
        # jaqueta de couro curta e aberta, camiseta por baixo, zíper prateado e gola larga (Lucy)
        if side:
            g.set(8, 17, "Q"); g.set(9, 17, "Q"); g.set(9, 18, "A")
            for y in (19, 20, 21):
                g.set(9, y, "z")
            g.row(22, 5, 9, "c")
        elif view == "front":
            for y in range(17, 22):
                g.set(7, y, "A"); g.set(8, y, "A")
            g.set(7, 17, "N"); g.set(8, 17, "N")
            g.set(6, 17, "Q"); g.set(9, 17, "Q"); g.set(5, 17, "Q"); g.set(10, 17, "Q")
            g.set(6, 18, "Q"); g.set(9, 18, "Q")
            for y in (19, 20, 21):
                g.set(6, y, "z")
            g.set(10, 20, "z")                                # zíper do bolso
            g.row(22, 5, 10, "c")
        else:
            g.row(17, 4, 11, "Q")
            g.set(6, 20, "c"); g.set(9, 20, "c")
            g.row(22, 5, 10, "c")
    elif outfit == "captain":
        # casaco de capitão trespassado: dragonas e botões dourados, galão nos punhos (Ian)
        if side:
            g.row(17, 6, 8, "J")
            g.set(9, 19, "J"); g.set(9, 21, "J")
        else:
            g.row(17, 3, 5, "J"); g.row(17, 10, 12, "J")
            if view == "front":
                for y in (19, 21):
                    g.set(6, y, "J"); g.set(9, y, "J")
                g.set(9, 19, "J")
        for (x, y), k in list(g.px.items()):
            if y == 21 and (x <= 4 or x >= 11) and k in ("C", "c", "Q"):
                g.px[(x, y)] = "J"
    elif outfit == "patterned":
        # blazer preto estampado com flores vermelhas e colar dourado (Dona Graça)
        if side:
            for (x, y) in ((6, 18), (8, 20), (5, 21), (7, 22)):
                g.set(x, y, "A")
            g.set(9, 17, "J")
        else:
            flowers = [(5, 18), (10, 19), (6, 21), (9, 22), (11, 20), (4, 22)] if view == "front" else \
                      [(5, 19), (9, 18), (7, 21), (10, 22), (6, 22)]
            for (x, y) in flowers:
                g.set(x, y, "A")
                if g.px.get((x + 1, y)) in ("C", "c"):
                    g.set(x + 1, y, "a")
            if view == "front":
                g.row(17, 6, 9, "J"); g.set(7, 17, "N"); g.set(8, 17, "N")
                g.set(6, 18, "J"); g.set(9, 18, "J"); g.set(7, 18, "J"); g.set(8, 18, "J")
                g.set(7, 19, "N"); g.set(8, 19, "N")


def _broaden(g):
    """Ombros largos: o tronco (e o que desce dos ombros, como mãos e jaleco) ganha 1 px de cada lado.

    Divide a linha ao meio e repete a coluna central de cada metade; as pernas (x 5..10) não mudam.
    """
    px = {}
    rows = {}
    for (x, y), k in g.px.items():
        rows.setdefault(y, []).append(x)
    for (x, y), k in g.px.items():
        xs = rows[y]
        if 17 <= y <= 27 and (y <= 22 or min(xs) <= 4 or max(xs) >= 11):
            if x <= 7:
                px[(x - 1, y)] = k
                if x == 7:
                    px[(7, y)] = k
            else:
                px[(x + 1, y)] = k
                if x == 8:
                    px[(8, y)] = k
        else:
            px[(x, y)] = k
    g.px = px


TALL_ROWS = [25, 19, 26]         # linhas repetidas para quem é mais alta (meio da perna, meio do tronco)
SHORT_ROWS = [25, 19]            # linhas tiradas de quem é mais baixa


def _resize(g, dh):
    """Altura própria de cada personagem (como no Stardew): dh pixels a mais ou a menos.

    A figura cresce para cima (os pés continuam no chão); retorna a nova altura do quadro.
    """
    if not dh:
        return H
    px = {}
    if dh > 0:
        dups = TALL_ROWS[:dh]
        for (x, y), k in g.px.items():
            ny = y + sum(1 for r in dups if r < y)
            px[(x, ny)] = k
            if y in dups:
                px[(x, ny + 1)] = k
    else:
        rem = SHORT_ROWS[:-dh]
        for (x, y), k in g.px.items():
            if y in rem:
                continue
            px[(x, y - sum(1 for r in rem if r < y) - dh)] = k
    g.px = px
    return H + max(0, dh)


def _render(g, pal, h=H):
    s = pygame.Surface((W, h), pygame.SRCALPHA)
    for (x, y), k in g.px.items():
        s.set_at((x, y), pal.get(k, (255, 0, 255)))
    out = pygame.Surface((W, h), pygame.SRCALPHA)
    for y in range(h):
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
    outfit_full = look.get("outfit", "shirt")
    outfit = OUTFIT_BASE.get(outfit_full, outfit_full)
    out = {}
    _SHORT_SLEEVES["on"] = look.get("sleeves") == "short"
    for d, view in (("down", "front"), ("up", "back"), ("right", "side")):
        hair = _hair(style, view)
        for i, fr in enumerate([0, 1, 0, 2]):
            g = Grid()
            if view != "back":
                g.mask(hair, behind=True)          # cabelo comprido atrás do corpo
            body = Grid()                          # corpo à parte, para alargar os ombros sem mexer no cabelo
            if view == "side":
                _body_side(body, outfit, fr)
            else:
                _body_front(body, outfit, view, fr)
            if outfit_full != outfit:
                _outfit_overlay(body, outfit_full, view, fr)
            if look.get("broad") and view != "side":
                _broaden(body)
            g.px.update(body.px)
            _head(g, view, style, blink)
            g.mask(hair, behind=False if view != "back" else None)
            _extras(g, look, view)
            h = _resize(g, look.get("height", 0))
            img = up(_render(g, pal, h))
            out[(d, i)] = img
            if d == "right":
                out[("left", i)] = pygame.transform.flip(img, True, False)
    return out


art._frames = _frames

"""Camas dos apartamentos: cada morador tem a sua (cabeceira, colcha e estampa com a cara da pessoa).

Todas têm o mesmo tamanho da cama de casal da cobertura (3x2 tiles, 48x40 px de arte), menos a do Brainy,
que é de solteiro (2x2). Registradas em art.OBJECT_BUILDERS; os tamanhos ficam em world.OBJECT_DEFS.
"""
from . import art
from .art import new, P, R, shade


def _frame(s, W, wood, style):
    """Cabeceira e pé da cama. style: 'plain', 'tall' (estofada alta), 'metal', 'round', 'slats', 'anchor'."""
    dk, lt = shade(wood, 0.78), shade(wood, 1.18)
    if style == "tall":                               # estofada, com botões (capitonê)
        R(s, dk, 0, 0, W, 12)
        R(s, wood, 1, 1, W - 2, 10)
        R(s, lt, 1, 1, W - 2, 1)
        for y in (4, 8):
            for x in range(4 + (y // 4 % 2) * 3, W - 3, 6):
                P(s, dk, x, y)
    elif style == "metal":                            # grade de metal
        R(s, dk, 0, 1, W, 2)
        R(s, dk, 0, 10, W, 2)
        for x in range(0, W, 4):
            R(s, wood, x, 1, 1, 11)
        R(s, lt, 0, 1, W, 1)
        R(s, dk, 0, 1, 2, 11); R(s, dk, W - 2, 1, 2, 11)
    elif style == "round":                            # cabeceira arredondada
        R(s, dk, 2, 0, W - 4, 1)
        R(s, dk, 0, 2, W, 10)
        R(s, dk, 1, 1, W - 2, 1)
        R(s, wood, 2, 2, W - 4, 9)
        R(s, wood, 3, 1, W - 6, 1)
        R(s, lt, 3, 2, W - 6, 1)
    elif style == "slats":                            # ripas de madeira
        R(s, dk, 0, 0, W, 12)
        for x in range(1, W - 1, 4):
            R(s, wood, x, 1, 3, 10)
            R(s, lt, x, 1, 1, 10)
    elif style == "anchor":                           # madeira escura com âncora no meio
        R(s, dk, 0, 0, W, 12)
        R(s, wood, 1, 1, W - 2, 9)
        R(s, lt, 1, 1, W - 2, 1)
        cx = W // 2
        gold = (226, 190, 96)
        R(s, gold, cx, 2, 1, 7)
        R(s, gold, cx - 2, 3, 5, 1)
        P(s, gold, cx - 3, 7); P(s, gold, cx + 3, 7)
        R(s, gold, cx - 2, 8, 5, 1)
    else:
        R(s, dk, 0, 0, W, 12)
        R(s, wood, 1, 1, W - 2, 9)
        R(s, lt, 1, 1, W - 2, 1)
    # laterais e pé
    R(s, dk, 0, 12, W, 28)
    R(s, shade(dk, 0.85), 0, 38, W, 2)


def _pillows(s, W, color, n=None):
    edge = shade(color, 0.9)
    R(s, shade(color, 0.96), 2, 12, W - 4, 9)
    n = n or (2 if W >= 40 else 1)
    pw = (W - 4 - 3 * (n - 1)) // n - 2
    for i in range(n):
        px = 3 + i * (pw + 3)
        R(s, color, px, 13, pw, 6)
        R(s, shade(color, 1.05), px, 13, pw, 1)
        R(s, edge, px, 18, pw, 1)


def _quilt(s, W, base, pattern, accent, accent2=None):
    """Colcha de y=21 a y=38 com a estampa escolhida."""
    x0, y0, w, h = 2, 21, W - 4, 17
    R(s, base, x0, y0, w, h)
    R(s, shade(base, 1.15), x0, y0, w, 2)            # dobra de cima
    R(s, shade(base, 0.8), x0, y0 + h - 2, w, 2)     # borda de baixo
    a2 = accent2 or shade(accent, 0.8)
    if pattern == "plaid":                            # xadrez de flanela
        for x in range(x0 + 2, x0 + w, 6):
            R(s, accent, x, y0 + 2, 2, h - 4)
        for y in range(y0 + 4, y0 + h - 2, 6):
            R(s, accent, x0, y, w, 2)
        for x in range(x0 + 5, x0 + w, 6):
            R(s, a2, x, y0 + 2, 1, h - 4)
    elif pattern == "trim":                           # veludo liso com barra dourada
        R(s, accent, x0, y0 + 3, w, 1)
        R(s, accent, x0, y0 + h - 4, w, 1)
        for x in range(x0 + 3, x0 + w - 2, 5):
            P(s, shade(base, 1.25), x, y0 + 8 + (x % 3))
    elif pattern == "stripes":                        # listras verticais
        for x in range(x0 + 3, x0 + w, 7):
            R(s, accent, x, y0 + 2, 2, h - 4)
    elif pattern == "hstripes":                       # listras de marinheiro
        for y in range(y0 + 4, y0 + h - 2, 4):
            R(s, accent, x0, y, w, 2)
    elif pattern == "circuit":                        # trilhas de circuito
        for i, y in enumerate(range(y0 + 4, y0 + h - 3, 5)):
            xa = x0 + 2 + (i * 5) % 9
            R(s, accent, xa, y, w - 8, 1)
            R(s, accent, xa, y, 1, 3)
            P(s, a2, xa + w - 9, y); P(s, a2, xa, y + 3)
    elif pattern == "flowers":                        # florzinhas
        for i, (fx, fy) in enumerate([(5, 6), (13, 11), (21, 5), (29, 12), (37, 7), (9, 14), (33, 3), (25, 9)]):
            x, y = x0 + fx, y0 + fy
            if x >= x0 + w - 1 or y >= y0 + h - 2:
                continue
            c = accent if i % 2 else a2
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                P(s, c, x + dx, y + dy)
            P(s, (255, 230, 120), x, y)
    elif pattern == "stars":                          # estrelinhas e uma lua
        for (fx, fy) in [(4, 5), (12, 11), (19, 4), (27, 9), (35, 5), (8, 13), (31, 13), (23, 14)]:
            x, y = x0 + fx, y0 + fy
            if x >= x0 + w - 1 or y >= y0 + h - 2:
                continue
            P(s, accent, x, y); P(s, accent, x - 1, y); P(s, accent, x + 1, y)
            P(s, accent, x, y - 1); P(s, accent, x, y + 1)
        mx = x0 + w - 7
        R(s, a2, mx, y0 + 5, 3, 5); P(s, a2, mx + 3, y0 + 5); P(s, a2, mx + 3, y0 + 9)
    elif pattern == "bolt":                           # raio no meio (o Barry ama)
        cx, cy = x0 + w // 2, y0 + 3
        for i, (dx, ln) in enumerate([(2, 1), (1, 1), (0, 1), (-1, 1), (-2, 1)]):
            R(s, accent, cx + dx - 1, cy + i, 3, 1)
        R(s, accent, cx - 3, cy + 5, 7, 1)
        for i, dx in enumerate((1, 0, -1, -2, -3)):
            R(s, accent, cx + dx, cy + 6 + i, 3, 1)
        R(s, a2, x0, y0 + 3, w, 1)
    elif pattern == "diamonds":                       # losangos (colcha de matelassê)
        for y in range(y0 + 3, y0 + h - 2, 6):
            for x in range(x0 + 3 + ((y - y0) // 6 % 2) * 4, x0 + w - 2, 8):
                P(s, accent, x, y - 2); P(s, accent, x - 1, y - 1); P(s, accent, x + 1, y - 1)
                P(s, accent, x - 2, y); P(s, accent, x + 2, y)
                P(s, accent, x - 1, y + 1); P(s, accent, x + 1, y + 1); P(s, accent, x, y + 2)


def _make(w, wood, frame, pillow, base, pattern, accent, accent2=None, extra=None):
    W = 16 * w
    s = new(W, 40)
    _frame(s, W, wood, frame)
    _pillows(s, W, pillow)
    _quilt(s, W, base, pattern, accent, accent2)
    if extra:
        extra(s, W)
    return s


def _throw(color):
    """Mantinha dobrada no pé da cama."""
    def f(s, W):
        R(s, color, 2, 31, W - 4, 4)
        R(s, shade(color, 1.15), 2, 31, W - 4, 1)
        R(s, shade(color, 0.8), 2, 34, W - 4, 1)
    return f


def _plush(color):
    """Bichinho de pelúcia em cima do travesseiro."""
    def f(s, W):
        x = W - 12
        R(s, color, x, 14, 5, 4); P(s, color, x, 13); P(s, color, x + 4, 13)
        P(s, (40, 30, 30), x + 1, 15); P(s, (40, 30, 30), x + 3, 15)
    return f


BEDS = {
    # Lucy: couro marrom e flanela xadrez vermelha e azul (a repórter da jaqueta de couro)
    "bed_lucy": lambda: _make(3, (110, 70, 44), "plain", (242, 236, 226), (54, 70, 120), "plaid",
                              (176, 48, 52), (30, 40, 76), _throw((200, 170, 120))),
    # Vittoria: cabeceira alta estofada creme, veludo vinho com barra dourada
    "bed_vittoria": lambda: _make(3, (226, 210, 186), "tall", (252, 246, 236), (122, 26, 46), "trim",
                                  (226, 186, 96)),
    # Sam: moderna, cinza, colcha azul-petróleo com listras brancas
    "bed_sam": lambda: _make(3, (120, 124, 134), "plain", (236, 240, 246), (36, 102, 120), "stripes",
                             (226, 236, 240), None, _throw((240, 200, 90))),
    # Brainy: solteiro, grade de metal, colcha verde-escura com trilhas de circuito
    "bed_brainy": lambda: _make(2, (176, 184, 198), "metal", (230, 236, 244), (30, 64, 58), "circuit",
                                (90, 230, 160), (180, 255, 210)),
    # Jess: branca arredondada, colcha rosa com florzinhas e um ursinho
    "bed_jess": lambda: _make(3, (244, 240, 236), "round", (255, 250, 252), (240, 160, 186), "flowers",
                              (255, 255, 255), (200, 110, 170), _plush((196, 150, 110))),
    # Nia: ripas de madeira clara, colcha mostarda com estrelas e lua (a sonhadora)
    "bed_nia": lambda: _make(3, (196, 150, 98), "slats", (248, 240, 222), (60, 56, 120), "stars",
                             (250, 216, 110), (250, 236, 190), _throw((214, 150, 60))),
    # Barry: madeira escura, colcha vermelha com o raio amarelo
    "bed_barry": lambda: _make(3, (86, 58, 40), "plain", (240, 236, 228), (178, 34, 38), "bolt",
                               (250, 210, 70), (140, 24, 30)),
    # Ian: cabeceira com âncora, listras de marinheiro azul e branco
    "bed_ian": lambda: _make(3, (64, 44, 34), "anchor", (240, 242, 246), (236, 240, 246), "hstripes",
                             (34, 56, 104), None, _throw((178, 140, 92))),
    # Milany: madeira clara arredondada, colcha lilás de matelassê
    "bed_milany": lambda: _make(3, (214, 178, 136), "round", (250, 248, 252), (168, 140, 206), "diamonds",
                                (214, 198, 240), None, _throw((140, 180, 160))),
}
art.OBJECT_BUILDERS.update(BEDS)

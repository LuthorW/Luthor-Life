"""Emotes em estilo emoji (pixel art 20x20, ampliada), que aparecem em cima da cabeça das personagens.

Rostos amarelos com contorno escuro, como os emojis do celular:
  coracao 😍  feliz 😄  vergonha 😊  gota 😅  raiva 😠  triste 😢  zzz 😴  surpresa 😮  beijo 😘
  estrela 🤩  pergunta ❓  exclamacao ❗  musica 🎶  brilho ✨  reticencias 💬

Uso: draw_emote(surf, x, y, kind, k) — x = centro, y = base do emote, k = 0..1 (animação de entrada).
"""
import math

import pygame

N = 20                        # tamanho do desenho em pixels de arte
ZOOM = 2                      # ampliação na tela
OUT = (52, 30, 34)            # contorno
FACE, FACE_D, FACE_L = (255, 206, 62), (238, 160, 36), (255, 238, 150)
RED_FACE, RED_FACE_D = (244, 120, 66), (220, 76, 50)
EYE = (70, 40, 24)
MOUTH = (150, 36, 46)
TONGUE = (250, 120, 130)
HEART, HEART_L = (236, 42, 74), (255, 150, 170)
BLUSH = (255, 128, 150)
BLUE, BLUE_L = (96, 170, 250), (196, 230, 255)
WHITE = (255, 255, 255)
GREY = (150, 150, 170)
PURPLE, PURPLE_L = (176, 72, 250), (226, 176, 255)
GOLD, GOLD_L = (255, 200, 40), (255, 244, 170)

_CACHE = {}


def _canvas():
    return pygame.Surface((N, N), pygame.SRCALPHA)


def _px(s, pts, c):
    for x, y in pts:
        if 0 <= x < N and 0 <= y < N:
            s.set_at((x, y), c)


def _grid(s, rows, ox, oy, colors):
    """Desenha linhas de texto: cada letra é uma cor de `colors` (ponto = vazio)."""
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in colors:
                _px(s, [(ox + x, oy + y)], colors[ch])


def _face(s, fill=FACE, shade=FACE_D, oy=3):
    """Rosto redondo de 16 px (com sombra embaixo e brilho em cima) a partir de (2, oy)."""
    cx, cy = 2 + 7.5, oy + 7.5
    for y in range(oy, oy + 16):
        for x in range(2, 18):
            d = math.hypot(x - cx, y - cy)
            if d <= 7.6:
                c = fill
                if y - cy > 3.2 and d > 4.5:
                    c = shade
                s.set_at((x, y), c)
    _px(s, [(5, oy + 3), (6, oy + 2), (7, oy + 2), (5, oy + 4)], FACE_L if fill == FACE else (255, 190, 150))
    return oy


def _smile_open(s, oy):
    _grid(s, ["EEEEEE",
              "EMMMME",
              ".ETTE.",
              "..EE.."], 7, oy + 9, {"E": EYE, "M": MOUTH, "T": TONGUE})


def _smile(s, oy):
    _px(s, [(6, oy + 10), (13, oy + 10)], EYE)
    _px(s, [(7, oy + 11), (8, oy + 11), (9, oy + 11), (10, oy + 11), (11, oy + 11), (12, oy + 11)], EYE)


def _happy_eyes(s, oy):
    """Olhos fechados de alegria (^ ^)."""
    for ex in (6, 12):
        _px(s, [(ex - 1, oy + 7), (ex, oy + 6), (ex + 1, oy + 6), (ex + 2, oy + 7)], EYE)


def _dot_eyes(s, oy, big=False):
    for ex in (6, 12):
        pts = [(ex, oy + 6), (ex, oy + 7)] + ([(ex + 1, oy + 6), (ex + 1, oy + 7)] if big else [])
        _px(s, pts, EYE)
        if big:
            _px(s, [(ex, oy + 6)], WHITE)


def _heart(s, ox, oy, c=HEART, hi=HEART_L):
    _grid(s, [".X.X.",
              "XXXXX",
              "XXXXX",
              ".XXX.",
              "..X.."], ox, oy, {"X": c})
    _px(s, [(ox + 1, oy + 1)], hi)


def _star(s, ox, oy, c=GOLD, hi=GOLD_L):
    _grid(s, ["..X..",
              ".XXX.",
              "XXXXX",
              ".XXX.",
              ".X.X."], ox, oy, {"X": c})
    _px(s, [(ox + 2, oy + 1)], hi)


def _sparkle(s, ox, oy, r, c=GOLD, hi=GOLD_L):
    for i in range(-r, r + 1):
        _px(s, [(ox + i, oy), (ox, oy + i)], c)
    if r >= 2:
        _px(s, [(ox - 1, oy - 1), (ox + 1, oy - 1), (ox - 1, oy + 1), (ox + 1, oy + 1)], c)
    _px(s, [(ox, oy)], hi)


# --- cada emote ---------------------------------------------------------------

def _e_coracao(s):
    oy = _face(s)
    _heart(s, 4, oy + 4)
    _heart(s, 11, oy + 4)
    _smile_open(s, oy + 1)


def _e_feliz(s):
    oy = _face(s)
    _happy_eyes(s, oy)
    _smile_open(s, oy)


def _e_vergonha(s):
    oy = _face(s)
    _happy_eyes(s, oy)
    for bx in (4, 13):
        _px(s, [(bx, oy + 9), (bx + 1, oy + 9), (bx - 0, oy + 10), (bx + 1, oy + 10)], BLUSH)
    _smile(s, oy)


def _e_gota(s):
    oy = _face(s)
    _happy_eyes(s, oy)
    _smile_open(s, oy)
    _grid(s, ["..B..",
              ".BBB.",
              "BBLBB",
              "BBBBB",
              ".BBB."], 14, 0, {"B": BLUE, "L": BLUE_L})


def _e_raiva(s):
    oy = _face(s, RED_FACE, RED_FACE_D)
    _px(s, [(4, oy + 4), (5, oy + 4), (6, oy + 5), (7, oy + 5)], EYE)       # sobrancelhas franzidas
    _px(s, [(12, oy + 5), (13, oy + 5), (14, oy + 4), (15, oy + 4)], EYE)
    _px(s, [(6, oy + 7), (6, oy + 8), (13, oy + 7), (13, oy + 8)], EYE)
    _px(s, [(7, oy + 11), (8, oy + 11), (9, oy + 11), (10, oy + 11), (11, oy + 11), (12, oy + 11)], EYE)
    _px(s, [(6, oy + 12), (13, oy + 12)], EYE)
    _grid(s, ["X.X",
              ".X.",
              "X.X"], 15, 0, {"X": (230, 40, 50)})                          # veinha de raiva


def _e_triste(s):
    oy = _face(s)
    _px(s, [(5, oy + 5), (6, oy + 4), (13, oy + 4), (14, oy + 5)], EYE)     # sobrancelhas tristes
    _dot_eyes(s, oy)
    _px(s, [(8, oy + 11), (9, oy + 11), (10, oy + 11), (11, oy + 11)], EYE)
    _px(s, [(7, oy + 12), (12, oy + 12)], EYE)
    _grid(s, [".B.",
              "BBB",
              "BLB",
              ".B."], 5, oy + 8, {"B": BLUE, "L": BLUE_L})                    # lágrima


def _e_zzz(s):
    oy = _face(s, oy=4)
    for ex in (6, 12):
        _px(s, [(ex - 1, oy + 7), (ex, oy + 8), (ex + 1, oy + 8), (ex + 2, oy + 7)], EYE)
    _px(s, [(9, oy + 11), (10, oy + 11), (9, oy + 12), (10, oy + 12)], EYE)
    _grid(s, ["ZZZ",
              "..Z",
              ".Z.",
              "ZZZ"], 13, 0, {"Z": (110, 120, 230)})
    _grid(s, ["ZZ",
              ".Z",
              "ZZ"], 17, 3, {"Z": (150, 160, 240)})


def _e_surpresa(s):
    oy = _face(s)
    _px(s, [(5, oy + 3), (6, oy + 3), (13, oy + 3), (14, oy + 3)], EYE)     # sobrancelhas para cima
    _dot_eyes(s, oy, big=True)
    _grid(s, [".EE.",
              "EMME",
              "EMME",
              ".EE."], 8, oy + 10, {"E": EYE, "M": MOUTH})


def _e_beijo(s):
    oy = _face(s)
    _px(s, [(6, oy + 6), (6, oy + 7)], EYE)                                # um olho aberto
    _px(s, [(11, oy + 7), (12, oy + 6), (13, oy + 6), (14, oy + 7)], EYE)   # piscadinha
    _grid(s, ["EE.",
              "..E",
              "EE.",
              "..E",
              "EE."], 9, oy + 9, {"E": EYE})                                 # biquinho
    _heart(s, 14, oy + 9)


def _e_estrela(s):
    oy = _face(s)
    _star(s, 4, oy + 4, (236, 92, 24), (255, 200, 90))
    _star(s, 11, oy + 4, (236, 92, 24), (255, 200, 90))
    _smile_open(s, oy + 1)


def _e_pergunta(s):
    _grid(s, ["..RRRRR..",
              ".RRLLRRR.",
              "RRR...RRR",
              "RRR...RRR",
              "......RRR",
              ".....RRR.",
              "....RRR..",
              "....RRR..",
              "....RRR..",
              ".........",
              "....RRR..",
              "....RRR.."], 5, 4, {"R": (220, 44, 58), "L": (255, 140, 140)})


def _e_exclamacao(s):
    _grid(s, ["RRRR",
              "RLRR",
              "RLRR",
              "RRRR",
              "RRRR",
              ".RR.",
              ".RR.",
              ".RR.",
              "....",
              ".RR.",
              ".RR."], 8, 5, {"R": (220, 44, 58), "L": (255, 140, 140)})


def _e_musica(s):
    _grid(s, ["......PPPPPPP",
              "....PPPPPPPPP",
              "....PPPP...PP",
              "....P......P.",
              "....P......P.",
              "....P......P.",
              "....P......P.",
              "..PPP....PPP.",
              ".PLPP...PLPP.",
              ".PPPP...PPPP.",
              "..PP.....PP.."], 3, 5, {"P": PURPLE, "L": PURPLE_L})


def _e_brilho(s):
    _sparkle(s, 7, 11, 5)
    _sparkle(s, 15, 5, 3)
    _sparkle(s, 15, 15, 2, (255, 230, 120))


def _e_reticencias(s):
    _grid(s, ["..WWWWWWWWWWWWW..",
              ".WWWWWWWWWWWWWWW.",
              "WWWWWWWWWWWWWWWWW",
              "WWWWWWWWWWWWWWWWW",
              "WWWWWWWWWWWWWWWWW",
              "WWWWWWWWWWWWWWWWW",
              "WWWWWWWWWWWWWWWWW",
              ".WWWWWWWWWWWWWWW.",
              "..WWWWWWWWWWWWW..",
              "...WW............",
              "..W.............."], 1, 4, {"W": WHITE})
    for x in (5, 9, 13):
        _px(s, [(x, 8), (x + 1, 8), (x, 9), (x + 1, 9)], GREY)


BUILDERS = {
    "coracao": _e_coracao, "feliz": _e_feliz, "vergonha": _e_vergonha, "gota": _e_gota, "raiva": _e_raiva,
    "triste": _e_triste, "zzz": _e_zzz, "surpresa": _e_surpresa, "beijo": _e_beijo, "estrela": _e_estrela,
    "pergunta": _e_pergunta, "exclamacao": _e_exclamacao, "musica": _e_musica, "brilho": _e_brilho,
    "reticencias": _e_reticencias,
}


def _outline(s):
    """Contorno escuro de 1 px em volta de tudo o que foi desenhado."""
    out = pygame.Surface((N + 2, N + 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(s)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(mask.to_surface(setcolor=OUT, unsetcolor=(0, 0, 0, 0)), (dx, dy))
    out.blit(s, (1, 1))
    return out


def image(kind):
    img = _CACHE.get(kind)
    if img is None:
        s = _canvas()
        BUILDERS.get(kind, _e_reticencias)(s)
        img = pygame.transform.scale_by(_outline(s), ZOOM)
        _CACHE[kind] = img
    return img


def draw_emote(surf, x, y, kind, k=1.0):
    """Emote entrando com um "pulo" (cresce passando um pouco do tamanho e volta)."""
    pop = min(1.0, max(0.0, k) * 1.6)
    if pop <= 0.05:
        return
    img = image(kind)
    scale = pop * (1 + 0.28 * math.sin(pop * math.pi))
    if abs(scale - 1) > 0.01:
        w, h = max(1, int(img.get_width() * scale)), max(1, int(img.get_height() * scale))
        img = pygame.transform.scale(img, (w, h))
    bob = int(math.sin(pygame.time.get_ticks() / 180.0) * 2) if pop >= 1 else 0
    surf.blit(img, (x - img.get_width() // 2, y - img.get_height() + 4 + bob))


HEART_PX = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]


def heart_img(k):
    """Coração rosa com contorno (o do beijo), k = tamanho do pixel."""
    key = ("heart", k)
    img = _CACHE.get(key)
    if img is None:
        img = pygame.Surface((9 * k, 8 * k), pygame.SRCALPHA)
        for yy, row in enumerate(HEART_PX):
            for xx, c in enumerate(row):
                if c == "X":
                    img.fill((120, 30, 70), (xx * k, yy * k, 3 * k, 3 * k))
        for yy, row in enumerate(HEART_PX):
            for xx, c in enumerate(row):
                if c == "X":
                    img.fill((255, 96, 150), ((xx + 1) * k, (yy + 1) * k, k, k))
        img.fill((255, 214, 228), (2 * k, 2 * k, k, k))
        _CACHE[key] = img
    return img

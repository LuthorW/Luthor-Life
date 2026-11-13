"""Interiores caprichados (como a cidade de caprichado.py, mas dentro dos prédios).

- Chão com textura contínua: tábuas compridas com emendas desencontradas e veios, mármore em placas grandes com
  veios, azulejo com rejunte e brilho, carpete trançado, xadrez e terracota com relevo (`paint`, chamado por
  GameMap._build_floor antes dos tapetes).
- Paredes no estilo de cada lugar (`STYLES`): sanca em cima, papel de parede com desenho, roda-meio, lambri e rodapé;
  o topo das paredes ganha beirada e o chão escurece de leve perto delas (sombra de canto).
- Sombra embaixo dos móveis (`draw_shadows`, chamado por Game.draw_world antes dos objetos).
- Quadros, relógios, arandelas, prateleiras e vasos nas paredes dos lugares públicos (`decorate`, no fim do
  build_world), só onde não tapam porta, janela, letreiro nem móvel alto. A cobertura (decoração da jogadora),
  os apartamentos, o terraço e o barco não ganham enfeites automáticos.
"""
import random

import pygame

from . import art
from .art import new, R, P, shade, mix, up
from .config import TS, TILE, SCALE

SKIP_MAPS = ("terrace", "altomar")                  # sem paredes (céu aberto / barco)
NO_DECOR = ("home", "terrace", "altomar")            # a cobertura tem a decoração da própria jogadora

# ---------------------------------------------------------------------------
# Estilos das paredes
# paper: papel de parede; ink: cor do desenho; pattern: stripes | dots | damask | panel | brick | band | plain
# wains: lambri (metade de baixo) ou None; wpat: panel | tile | wood | plain; trim: sanca, roda-meio e rodapé
# ---------------------------------------------------------------------------
STYLES = {
    "_": dict(paper=(166, 150, 200), ink=(152, 136, 188), pattern="damask", wains=(104, 86, 136), wpat="panel",
              trim=(226, 214, 240)),
    "home": dict(paper=(222, 210, 236), ink=(208, 194, 226), pattern="stripes", wains=(246, 242, 250), wpat="panel",
                 trim=(252, 248, 254)),
    "hq": dict(paper=(74, 50, 110), ink=(96, 66, 138), pattern="panel", wains=(46, 32, 70), wpat="panel",
               trim=(214, 172, 84)),
    "cafe": dict(paper=(240, 226, 200), ink=(226, 206, 174), pattern="damask", wains=(74, 112, 86), wpat="panel",
                 trim=(250, 242, 226)),
    "catco": dict(paper=(226, 232, 242), ink=(84, 132, 204), pattern="band", wains=None, wpat="plain",
                  trim=(246, 248, 252), ink2=(196, 210, 232)),
    "books": dict(paper=(56, 94, 74), ink=(200, 172, 98), pattern="dots", wains=(112, 74, 48), wpat="wood",
                  trim=(200, 164, 100)),
    "market": dict(paper=(246, 236, 204), ink=(234, 222, 186), pattern="plain", wains=(232, 238, 242), wpat="tile",
                   trim=(250, 250, 250)),
    "trattoria": dict(paper=(180, 100, 72), ink=(214, 196, 178), pattern="brick", wains=(118, 74, 48), wpat="wood",
                      trim=(236, 214, 180)),
    "bar": dict(paper=(110, 52, 48), ink=(70, 40, 40), pattern="brick", wains=(64, 42, 36), wpat="wood",
                trim=(172, 122, 72)),
    "cinema": dict(paper=(124, 28, 44), ink=(150, 44, 60), pattern="panel", wains=(72, 18, 28), wpat="panel",
                   trim=(214, 172, 84)),
    "hospital": dict(paper=(244, 247, 246), ink=(18, 63, 53), pattern="band", wains=(226, 236, 233), wpat="plain",
                     trim=(250, 250, 248), ink2=(183, 123, 101), base=(18, 63, 53)),
    "ricci": dict(paper=(134, 42, 58), ink=(160, 62, 76), pattern="damask", wains=(66, 30, 36), wpat="panel",
                  trim=(214, 172, 84)),
    "marina": dict(paper=(236, 241, 247), ink=(206, 220, 236), pattern="stripes", wains=(40, 66, 112), wpat="wood",
                   trim=(250, 250, 252)),
    "boutique": dict(paper=(240, 214, 216), ink=(250, 236, 236), pattern="stripes", wains=(250, 246, 242),
                     wpat="panel", trim=(214, 172, 82)),
    "bayside": dict(paper=(234, 216, 192), ink=(222, 200, 174), pattern="stripes", wains=(132, 94, 62), wpat="wood",
                    trim=(246, 234, 216)),
    "residencial": dict(paper=(208, 198, 228), ink=(224, 216, 240), pattern="panel", wains=(94, 76, 124),
                        wpat="panel", trim=(214, 172, 84)),
    "apt_lucy": dict(paper=(198, 216, 234), ink=(186, 206, 228), pattern="stripes", wains=(242, 244, 248),
                     wpat="panel", trim=(250, 250, 252)),
    "apt_vittoria": dict(paper=(242, 224, 202), ink=(228, 206, 182), pattern="damask", wains=(152, 72, 62),
                         wpat="panel", trim=(250, 240, 226)),
    "apt_brainy": dict(paper=(198, 228, 216), ink=(180, 216, 200), pattern="plain", wains=(72, 92, 112),
                       wpat="panel", trim=(232, 238, 242)),
    "apt_jess": dict(paper=(246, 214, 224), ink=(236, 194, 210), pattern="dots", wains=(250, 244, 246),
                     wpat="panel", trim=(252, 250, 252)),
    "apt_nia": dict(paper=(216, 202, 238), ink=(250, 236, 172), pattern="dots", wains=(112, 88, 152), wpat="panel",
                    trim=(242, 234, 250)),
    "apt_barry": dict(paper=(238, 208, 178), ink=(224, 188, 152), pattern="stripes", wains=(152, 62, 52),
                      wpat="wood", trim=(246, 236, 220)),
    "apt_sam": dict(paper=(192, 226, 224), ink=(178, 214, 212), pattern="panel", wains=(62, 92, 102), wpat="panel",
                    trim=(236, 244, 244)),
    "apt_ian": dict(paper=(222, 232, 242), ink=(202, 216, 232), pattern="stripes", wains=(38, 58, 98), wpat="wood",
                    trim=(250, 250, 252)),
    "apt_milany": dict(paper=(210, 238, 222), ink=(196, 228, 210), pattern="damask", wains=(246, 250, 248),
                       wpat="panel", trim=(252, 252, 252)),
}

WALLS = ("wall", "wall_top")
NOT_FLOOR = ("wall", "wall_top", "void", "glass", "door")


def _style(m):
    return STYLES.get(m.name, STYLES["_"])


# ---------------------------------------------------------------------------
# Chão (padrões do tamanho do mapa, em pixels de arte; cada tile copia o seu pedaço)
# ---------------------------------------------------------------------------
def _wood(s, base, rnd):
    W, H = s.get_size()
    tones = (0.88, 0.93, 0.97, 1.0, 1.0, 1.04, 1.08)
    for j in range(H // 4 + 1):
        y = j * 4
        x = -rnd.randrange(6, 40)
        while x < W:
            L = rnd.randrange(22, 46)
            tone = shade(base, rnd.choice(tones))
            R(s, tone, x, y, L, 4)
            R(s, shade(tone, 1.1), x, y, L, 1)              # brilho na beira da tábua
            R(s, shade(base, 0.68), x, y + 3, L, 1)         # junta entre as tábuas
            R(s, shade(base, 0.64), x, y, 1, 3)             # emenda (desencontrada de uma fileira para a outra)
            P(s, shade(tone, 1.16), x + 1, y + 1)
            for _ in range(rnd.randrange(1, 3)):            # veios
                gx = x + rnd.randrange(3, max(4, L - 6))
                R(s, shade(tone, 0.87), gx, y + 1 + rnd.randrange(2), rnd.randrange(3, 8), 1)
            if rnd.random() < 0.07:                         # nó da madeira
                kx = x + rnd.randrange(4, max(5, L - 4))
                P(s, shade(tone, 0.7), kx, y + 1); P(s, shade(tone, 0.8), kx + 1, y + 1)
                P(s, shade(tone, 0.8), kx, y + 2)
            x += L


def _marble(s, rnd):
    W, H = s.get_size()
    base = (236, 232, 242)
    S = 32
    for sy in range(0, H, S):
        for sx in range(0, W, S):
            tone = shade(base, rnd.choice((0.975, 0.99, 1.0, 1.0, 1.01)))
            R(s, tone, sx, sy, S, S)
            for _ in range(rnd.randrange(1, 3)):            # veios tortinhos
                x, y = sx + rnd.randrange(S), sy
                dx = rnd.choice((-1, 1))
                vein = (214, 206, 228) if rnd.random() < 0.6 else (204, 196, 222)
                while y < sy + S:
                    P(s, vein, x, y)
                    if rnd.random() < 0.45:
                        P(s, (250, 248, 254), x + 1, y)
                    y += 1
                    if rnd.random() < 0.45:
                        x += dx
                    if rnd.random() < 0.12:
                        dx = -dx
                    x = max(sx + 1, min(sx + S - 2, x))
            R(s, (252, 250, 255), sx, sy, S, 1); R(s, (252, 250, 255), sx, sy, 1, S)
            R(s, (206, 200, 218), sx, sy + S - 1, S, 1); R(s, (206, 200, 218), sx + S - 1, sy, 1, S)
            R(s, shade(tone, 1.025), sx + 2, sy + 2, 7, 1); R(s, shade(tone, 1.025), sx + 2, sy + 3, 3, 1)


def _ceramic(s, base, grout, rnd):
    W, H = s.get_size()
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            tone = shade(base, rnd.choice((0.985, 1.0, 1.0, 1.012)))
            R(s, tone, x, y, 8, 8)
            R(s, grout, x, y, 8, 1); R(s, grout, x, y, 1, 8)
            R(s, mix(tone, (255, 255, 255), 0.45), x + 1, y + 1, 6, 1)
            R(s, mix(tone, (255, 255, 255), 0.3), x + 1, y + 2, 1, 5)
            R(s, shade(tone, 0.965), x + 2, y + 7, 6, 1); R(s, shade(tone, 0.965), x + 7, y + 2, 1, 5)
            if rnd.random() < 0.08:
                P(s, (255, 255, 255), x + 3, y + 3)


def _checker(s, rnd):
    W, H = s.get_size()
    light, dark = (222, 206, 180), (74, 56, 52)
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            is_dark = ((x // 8) + (y // 8)) % 2 == 0          # mesma fase do xadrez antigo
            c = shade(dark if is_dark else light, rnd.choice((0.97, 1.0, 1.02)))
            R(s, c, x, y, 8, 8)
            hi = shade(c, 1.22) if is_dark else mix(c, (255, 255, 255), 0.35)
            lo = shade(c, 0.78) if is_dark else shade(c, 0.9)
            R(s, hi, x, y, 8, 1); R(s, hi, x, y, 1, 8)
            R(s, lo, x, y + 7, 8, 1); R(s, lo, x + 7, y, 1, 8)
            if not is_dark and rnd.random() < 0.25:            # reflexo de chão encerado
                P(s, (246, 236, 216), x + 2, y + 2); P(s, (246, 236, 216), x + 3, y + 2)


def _terracotta(s, rnd):
    W, H = s.get_size()
    base = (198, 114, 80)
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            c = shade(base, rnd.choice((0.9, 0.95, 1.0, 1.0, 1.05, 1.09)))
            R(s, c, x, y, 8, 8)
            R(s, (150, 82, 58), x, y, 8, 1); R(s, (150, 82, 58), x, y, 1, 8)
            R(s, shade(c, 1.1), x + 1, y + 1, 6, 1); R(s, shade(c, 1.1), x + 1, y + 1, 1, 6)
            R(s, shade(c, 0.9), x + 1, y + 7, 7, 1); R(s, shade(c, 0.9), x + 7, y + 1, 1, 7)
            if rnd.random() < 0.18:
                P(s, shade(c, 0.84), x + rnd.randrange(2, 6), y + rnd.randrange(2, 6))


def _carpet(s, base, rnd):
    W, H = s.get_size()
    t = pygame.Surface((8, 8))
    t.fill(base)
    hi, lo = shade(base, 1.06), shade(base, 0.94)
    for yy in range(8):
        for xx in range(8):
            k = (xx + yy) % 4
            if k == 0:
                t.set_at((xx, yy), hi)
            elif k == 2:
                t.set_at((xx, yy), lo)
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            s.blit(t, (x, y))
    for _ in range(W * H // 70):
        P(s, rnd.choice((shade(base, 1.14), shade(base, 0.86))), rnd.randrange(W), rnd.randrange(H))


MATERIALS = {"wood": lambda s, r: _wood(s, (156, 106, 68), r), "wood_dark": lambda s, r: _wood(s, (98, 64, 48), r),
             "marble": _marble, "tile_white": lambda s, r: _ceramic(s, (238, 240, 244), (208, 212, 222), r),
             "lab": lambda s, r: _ceramic(s, (216, 222, 232), (190, 196, 210), r), "checker": _checker,
             "terracotta": _terracotta, "carpet": lambda s, r: _carpet(s, (84, 46, 116), r),
             "carpet_blue": lambda s, r: _carpet(s, (56, 74, 114), r),
             "office": lambda s, r: _carpet(s, (104, 110, 128), r)}


# ---------------------------------------------------------------------------
# Paredes
# ---------------------------------------------------------------------------
def _paper(s, X0, Y, h, st):
    """Papel de parede na faixa (X0..X0+16, Y..Y+h). O desenho segue a posição no mapa, então emenda entre os tiles
    e serve para parede de 1 ou 2 tiles de altura."""
    pat, ink = st["pattern"], st["ink"]
    old = s.get_clip()
    s.set_clip(pygame.Rect(X0, Y, 16, h).clip(old))
    if pat == "stripes":
        for xx in range(16):
            if (X0 + xx) % 6 in (0, 1):
                R(s, ink, X0 + xx, Y, 1, h)
    elif pat == "dots":
        for xx in range(16):
            X = X0 + xx
            if X % 6 == 3:
                for yy in range(Y + 1 + (X // 6) % 2 * 2, Y + h, 4):
                    P(s, ink, X, yy)
    elif pat == "damask":
        for X in range(X0 - 4, X0 + 20):
            if X % 8 != 4:
                continue
            off = 0 if (X // 8) % 2 == 0 else 6               # florzinhas desencontradas
            for cy in range(((Y - 8) // 12) * 12 + off, Y + h + 6, 12):
                for dx, dy in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2)):
                    P(s, ink, X + dx, cy + dy)
                P(s, ink, X, cy)
    elif pat == "panel":
        hi = mix(st["paper"], (255, 255, 255), 0.12)
        R(s, ink, X0 + 2, Y + 1, 12, 1); R(s, ink, X0 + 2, Y + 1, 1, h - 2)
        R(s, hi, X0 + 3, Y + h - 2, 11, 1); R(s, hi, X0 + 13, Y + 2, 1, h - 3)
    elif pat == "brick":
        mortar = ink
        for r in range(h):
            yy = Y + r
            if yy % 4 == 3:
                R(s, mortar, X0, yy, 16, 1)
        for br in range((Y - 1) // 4, (Y + h) // 4 + 1):
            off = 4 if br % 2 else 0
            by = br * 4
            bx = ((X0 - off) // 8) * 8 + off - 8
            while bx < X0 + 16:
                k = random.Random(bx * 131 + br * 7).choice((0.9, 0.96, 1.0, 1.05, 1.1))
                c = shade(st["paper"], k)
                y0, y1 = max(by, Y), min(by + 3, Y + h)
                if y1 > y0:
                    R(s, c, bx, y0, 7, y1 - y0)
                    R(s, mortar, bx + 7, y0, 1, y1 - y0)
                    if by >= Y:
                        R(s, shade(c, 1.12), bx, by, 7, 1)
                bx += 8
    elif pat == "band":
        mid = Y + h // 2
        R(s, ink, X0, mid - 1, 16, 2)
        R(s, st.get("ink2", shade(ink, 1.3)), X0, mid + 2, 16, 1)
    else:                                            # liso, com um leve granulado
        for xx in range(0, 16, 5):
            for yy in range(Y + (xx * 3) % 7, Y + h, 7):
                P(s, shade(st["paper"], 0.97), X0 + xx, yy)
    s.set_clip(old)


def _wainscot(s, X0, Y, h, st):
    w, pat = st["wains"], st.get("wpat", "panel")
    R(s, w, X0, Y, 16, h)
    if pat == "panel":
        for xx in range(16):
            if (X0 + xx) % 8 == 0:
                R(s, shade(w, 0.8), X0 + xx, Y, 1, h)
                R(s, mix(w, (255, 255, 255), 0.18), X0 + xx + 1, Y, 1, h)
        R(s, mix(w, (255, 255, 255), 0.15), X0, Y, 16, 1)
    elif pat == "tile":
        grout = shade(w, 0.86)
        for xx in range(16):
            if (X0 + xx) % 4 == 0:
                R(s, grout, X0 + xx, Y, 1, h)
        R(s, grout, X0, Y + 1, 16, 1)
        R(s, (255, 255, 255), X0 + 1, Y, 2, 1)
    elif pat == "wood":
        for xx in range(16):
            if (X0 + xx) % 4 == 0:
                R(s, shade(w, 0.78), X0 + xx, Y, 1, h)
            elif (X0 + xx) % 4 == 1:
                R(s, shade(w, 1.1), X0 + xx, Y, 1, h)


LIFT, CROWN = 8, 5          # enfeites sobem até 8 px de arte numa parede alta; a sanca tem 5 px


def _column(s, X0, Y0, H, st, clip=None):
    """Face da parede com H px de altura (16 ou 32): sanca, papel de parede, roda-meio, lambri e rodapé."""
    s.set_clip(clip or pygame.Rect(X0, Y0, 16, H))
    paper, trim, wains = st["paper"], st["trim"], st.get("wains")
    base = st.get("base") or shade(wains or paper, 0.55)
    R(s, paper, X0, Y0, 16, H)
    if H >= 32:                                      # parede de 2 tiles (como no Stardew)
        rail = 22 if wains else 28
        _paper(s, X0, Y0 + CROWN, rail - CROWN, st)
        R(s, shade(trim, 0.45), X0, Y0, 16, 1)        # beirada de cima
        R(s, shade(trim, 0.74), X0, Y0 + 1, 16, 1)    # sanca
        R(s, trim, X0, Y0 + 2, 16, 1)
        R(s, mix(trim, (255, 255, 255), 0.3), X0, Y0 + 3, 16, 1)
        R(s, shade(paper, 0.78), X0, Y0 + 4, 16, 1)   # sombrinha embaixo da sanca
        R(s, shade(paper, 0.9), X0, Y0 + 5, 16, 1)
        if wains:
            R(s, mix(trim, (255, 255, 255), 0.2), X0, Y0 + 22, 16, 1)   # roda-meio
            R(s, shade(trim, 0.74), X0, Y0 + 23, 16, 1)
            _wainscot(s, X0, Y0 + 24, 6, st)
        else:
            R(s, shade(paper, 0.9), X0, Y0 + 28, 16, 1)
            R(s, trim, X0, Y0 + 29, 16, 1)
        R(s, base, X0, Y0 + 30, 16, 1)               # rodapé
        R(s, shade(base, 0.78), X0, Y0 + 31, 16, 1)
    else:
        bottom = 10 if wains else 14
        _paper(s, X0, Y0 + 3, bottom - 3, st)
        R(s, shade(trim, 0.72), X0, Y0, 16, 1)      # sanca
        R(s, trim, X0, Y0 + 1, 16, 1)
        R(s, shade(paper, 0.8), X0, Y0 + 2, 16, 1)  # sombrinha embaixo da sanca
        if wains:
            R(s, trim, X0, Y0 + 10, 16, 1)           # roda-meio
            R(s, shade(trim, 0.74), X0, Y0 + 11, 16, 1)
            _wainscot(s, X0, Y0 + 12, 3, st)
        else:
            R(s, shade(paper, 0.9), X0, Y0 + 13, 16, 1)
            R(s, trim, X0, Y0 + 14, 16, 1)
        R(s, base, X0, Y0 + 15, 16, 1)               # rodapé
    s.set_clip(None)


def _face(s, X0, Y0, st):
    _column(s, X0, Y0, 16, st)


def _is_face(m, x, y):
    return m.tile_at(x, y) == "wall" and m.tile_at(x, y + 1) not in WALLS + ("void", "glass", "door")


def _is_upper(m, x, y):
    """Parte de cima de uma parede de 2 tiles: parede com face (ou porta) embaixo e parede (ou o fim do mapa) em
    cima. Divisórias finas (com chão do lado) continuam com 1 tile e topo escuro."""
    if m.tile_at(x, y) != "wall" or (y > 0 and m.tile_at(x, y - 1) not in WALLS):
        return False
    if not (_is_face(m, x, y + 1) or (m.tile_at(x, y + 1) == "door" and _is_floor(m, x, y + 2))):
        return False
    return not (_is_floor(m, x - 1, y) or _is_floor(m, x + 1, y))


def lift(m, o, h):
    """Quanto (px de tela) um enfeite de parede sobe numa parede de 2 tiles, para ficar no meio dela e não no lambri.
    h = altura do desenho em px de tela."""
    if m.outdoor:
        return 0
    yb = o.y + o.h - 1
    if not (_is_face(m, o.x, yb) and _is_upper(m, o.x, yb - 1)):
        return 0
    return max(0, min(LIFT, 2 * TS - CROWN - h // SCALE)) * SCALE


def _is_floor(m, x, y):
    return m.in_bounds(x, y) and m.tiles[y][x] not in NOT_FLOOR


def paint(m, surf):
    """Chão com textura e paredes no estilo do lugar (antes dos tapetes; só interiores)."""
    if m.outdoor:
        return
    W, H = m.w * TS, m.h * TS
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    present = {}
    for y in range(m.h):
        for x in range(m.w):
            t = m.tiles[y][x]
            if t in MATERIALS:
                present.setdefault(t, []).append((x, y))
    for mat, cells in present.items():
        pat = pygame.Surface((W, H))
        MATERIALS[mat](pat, random.Random(f"{m.name}:{mat}"))
        for (x, y) in cells:
            layer.blit(pat, (x * TS, y * TS), (x * TS, y * TS, TS, TS))
    if m.name not in SKIP_MAPS:
        st = _style(m)
        dark = mix(st.get("wains") or st["paper"], (22, 14, 32), 0.82)
        edge = mix(dark, st["trim"], 0.3)
        done = set()
        for y in range(m.h):
            for x in range(m.w):
                t = m.tiles[y][x]
                if t != "wall" or (x, y) in done:
                    continue
                X0, Y0 = x * TS, y * TS
                if _is_upper(m, x, y):
                    if m.tile_at(x, y + 1) == "door":       # em cima da porta: só a parte de cima da parede
                        _column(layer, X0, Y0, 32, st, clip=pygame.Rect(X0, Y0, 16, 16))
                        R(layer, shade(st["trim"], 0.6), X0, Y0 + 15, 16, 1)
                    else:
                        _column(layer, X0, Y0, 32, st)
                        done.add((x, y + 1))
                    continue
                if _is_face(m, x, y):
                    _face(layer, X0, Y0, st)
                    continue
                # topo da parede: massa escura com beirada voltada para o chão
                R(layer, dark, X0, Y0, 16, 16)
                R(layer, shade(dark, 1.15), X0, Y0, 16, 1)
                if _is_face(m, x, y + 1) or _is_floor(m, x, y + 1) or m.tile_at(x, y + 1) == "door":
                    R(layer, edge, X0, Y0 + 15, 16, 1)
                if _is_floor(m, x, y - 1):
                    R(layer, edge, X0, Y0, 16, 2)
                    R(layer, shade(edge, 1.2), X0, Y0, 16, 1)
                for dx, x1 in ((1, X0 + 14), (-1, X0)):
                    nx = x + dx
                    if (_is_floor(m, nx, y) or _is_face(m, nx, y) or _is_upper(m, nx, y)
                            or _is_upper(m, nx, y - 1)):
                        R(layer, edge, x1, Y0, 2, 16)
        # sombra de canto no chão, perto das paredes
        ao = pygame.Surface((W, H), pygame.SRCALPHA)
        col = (24, 12, 36)
        for y in range(m.h):
            for x in range(m.w):
                if not _is_floor(m, x, y):
                    continue
                X0, Y0 = x * TS, y * TS
                if m.tile_at(x, y - 1) in WALLS:
                    for i, a in enumerate((84, 54, 32, 18, 9, 4)):
                        R(ao, (*col, a), X0, Y0 + i, 16, 1)
                for side, dx in (("l", -1), ("r", 1)):
                    if m.tile_at(x + dx, y) in WALLS:
                        for i, a in enumerate((58, 32, 15, 6)):
                            R(ao, (*col, a), X0 + i if side == "l" else X0 + 15 - i, Y0, 1, 16)
        layer.blit(ao, (0, 0))
    surf.blit(up(layer), (0, 0))


# ---------------------------------------------------------------------------
# Sombra dos móveis
# ---------------------------------------------------------------------------
SEATS = ("chair", "chair_blue", "stool", "hchair", "seat")
NO_SHADOW = ("plot", "petbed", "rope", "watering", "railing_plant")
_shadow_cache = {}


def _shadow(w, h):
    k = (w, h)
    img = _shadow_cache.get(k)
    if img is None:
        img = pygame.Surface((w + 8, h + 6), pygame.SRCALPHA)
        pygame.draw.rect(img, (14, 6, 24, 26), (0, 0, w + 8, h + 6), border_radius=(h + 6) // 2)
        pygame.draw.rect(img, (14, 6, 24, 34), (3, 2, w + 2, h + 2), border_radius=(h + 2) // 2)
        pygame.draw.rect(img, (14, 6, 24, 30), (5, 3, w - 2, h), border_radius=h // 2)
        _shadow_cache[k] = img
    return img


def draw_shadows(surf, m, cam, skip=()):
    """Sombra suave no pé de cada móvel (os que já têm sombra própria ficam de fora)."""
    if m.outdoor:
        return
    SW, SH = surf.get_size()
    for o in m.objects:
        if o.layer != "obj" or o.kind in skip or o.kind in NO_SHADOW:
            continue
        seat = o.kind in SEATS
        if not o.solid and not seat:
            continue
        inset = 4 * SCALE if seat else 2 * SCALE
        w = o.w * TILE - inset * 2
        h = (3 if seat else 4) * SCALE
        x = o.x * TILE + inset + SCALE - cam[0] - 4
        y = o.base_y - h - 2 * SCALE - cam[1]
        if x > SW or y > SH or x + w < -8 or y + h < -8 or w <= 0:
            continue
        surf.blit(_shadow(w, h), (x, y))


# ---------------------------------------------------------------------------
# Enfeites de parede (pixel art 16x16, presos na face da parede)
# ---------------------------------------------------------------------------
FRAME_D, GOLD, GOLD_L = (88, 58, 30), (214, 172, 84), (244, 214, 132)


def _frame(s, x, y, w, h, outer=FRAME_D, mid=GOLD, inner=GOLD_L):
    R(s, (20, 10, 26, 90), x + 1, y + 1, w, h)        # sombra na parede
    R(s, outer, x, y, w, h)
    R(s, mid, x + 1, y + 1, w - 2, h - 2)
    R(s, inner, x + 1, y + 1, w - 2, 1)


def _quadro_paisagem():
    s = new(16, 16)
    _frame(s, 2, 2, 12, 9)
    for i in range(5):
        R(s, mix((150, 196, 238), (226, 232, 248), i / 4), 3, 3 + i, 10, 1)
    R(s, (255, 236, 150), 10, 4, 2, 2)
    R(s, (112, 172, 102), 3, 7, 10, 2); R(s, (86, 146, 84), 3, 8, 6, 1)
    R(s, (96, 156, 92), 6, 6, 4, 1); R(s, (80, 150, 200), 3, 9, 10, 1)
    return s


def _quadro_abstrato():
    s = new(16, 16)
    _frame(s, 3, 1, 10, 11, outer=(32, 24, 40), mid=(196, 196, 210), inner=(240, 240, 248))
    R(s, (244, 240, 236), 4, 2, 8, 9)
    R(s, (138, 0, 230), 5, 3, 3, 4); R(s, (110, 231, 140), 8, 6, 3, 3)
    R(s, (240, 196, 72), 6, 8, 2, 2); R(s, (184, 76, 255), 9, 3, 2, 2)
    R(s, (40, 30, 50), 4, 7, 8, 1)
    return s


def _quadro_flores():
    s = new(16, 16)
    _frame(s, 3, 2, 10, 10, outer=(150, 140, 150), mid=(246, 244, 240), inner=(255, 255, 255))
    R(s, (250, 226, 230), 4, 3, 8, 8)
    R(s, (90, 150, 200), 7, 8, 2, 3)
    for (fx, fy, c) in ((6, 5, (240, 90, 120)), (8, 4, (250, 200, 90)), (10, 6, (200, 120, 230)), (7, 7, (240, 140, 160))):
        P(s, c, fx, fy); P(s, shade(c, 0.8), fx + 1, fy); P(s, c, fx, fy + 1)
    R(s, (90, 150, 80), 7, 6, 1, 2); R(s, (90, 150, 80), 9, 6, 1, 2)
    return s


def _relogio():
    s = new(16, 16)
    pygame.draw.circle(s, (20, 10, 26, 90), (9, 7), 5)
    pygame.draw.circle(s, (64, 50, 70), (8, 6), 5)
    pygame.draw.circle(s, (248, 244, 236), (8, 6), 4)
    for (dx, dy) in ((0, -3), (3, 0), (0, 3), (-3, 0)):
        P(s, (120, 110, 130), 8 + dx, 6 + dy)
    R(s, (40, 30, 50), 8, 3, 1, 3); R(s, (40, 30, 50), 8, 6, 3, 1)
    P(s, (220, 60, 70), 8, 6)
    return s


def _arandela():
    s = new(16, 16)
    R(s, (150, 110, 56), 7, 7, 2, 4)                  # base de latão
    R(s, (200, 160, 80), 7, 7, 1, 4)
    R(s, (150, 110, 56), 8, 5, 1, 2)
    pygame.draw.polygon(s, (250, 236, 200), [(5, 1), (11, 1), (12, 5), (4, 5)])   # cúpula
    R(s, (255, 248, 226), 6, 2, 4, 1)
    R(s, (226, 200, 150), 4, 5, 9, 1)
    return s


def _prateleira():
    s = new(16, 16)
    R(s, (20, 10, 26, 80), 2, 10, 13, 1)
    R(s, (120, 80, 50), 1, 8, 14, 2); R(s, (154, 106, 66), 1, 8, 14, 1)
    R(s, (90, 60, 40), 3, 10, 1, 2); R(s, (90, 60, 40), 12, 10, 1, 2)
    R(s, (196, 110, 76), 2, 5, 4, 3); R(s, (220, 136, 96), 2, 5, 4, 1)          # vasinho
    for (lx, ly) in ((2, 3), (4, 2), (5, 4), (3, 4), (1, 4)):
        P(s, (90, 168, 90), lx, ly); P(s, (120, 196, 110), lx, ly - 1)
    for i, c in enumerate(((138, 0, 230), (70, 130, 200), (230, 180, 70))):     # livrinhos
        R(s, c, 8 + i * 2, 3 + (i == 1), 2, 5 - (i == 1))
    return s


def _vaso_parede():
    s = new(16, 16)
    R(s, (120, 110, 100), 8, 0, 1, 2)
    for i in range(3):
        P(s, (210, 196, 170), 7 - i, 2 + i); P(s, (210, 196, 170), 9 + i, 2 + i)
    R(s, (196, 110, 76), 5, 5, 6, 3); R(s, (224, 140, 100), 5, 5, 6, 1)
    for (lx, ly, ln) in ((5, 8, 4), (7, 8, 3), (9, 8, 5), (10, 8, 2), (6, 8, 2)):
        for k in range(ln):
            P(s, (86, 160, 86) if k % 2 else (120, 196, 110), lx + (k % 2), ly + k)
    for (lx, ly) in ((4, 5), (11, 5), (6, 4), (10, 4)):
        P(s, (120, 196, 110), lx, ly)
    return s


def _diploma():
    s = new(16, 16)
    _frame(s, 3, 2, 10, 8, outer=(30, 22, 36), mid=(60, 46, 70), inner=(90, 76, 100))
    R(s, (250, 246, 232), 4, 3, 8, 6)
    R(s, (120, 110, 130), 5, 4, 6, 1); R(s, (170, 160, 176), 5, 6, 5, 1)
    R(s, (210, 60, 70), 9, 7, 2, 2); P(s, (240, 196, 72), 9, 7)
    return s


def _capa_jornal():
    s = new(16, 16)
    _frame(s, 2, 1, 12, 11, outer=(30, 22, 36), mid=(54, 44, 60), inner=(80, 70, 90))
    R(s, (244, 238, 222), 3, 2, 10, 9)
    R(s, (30, 26, 34), 4, 3, 8, 2)
    R(s, (150, 170, 196), 4, 6, 4, 4)
    for yy in (6, 8, 10):
        R(s, (150, 144, 140), 9, yy, 3, 1)
    return s


def _quadro_cmh():
    s = new(16, 16)
    _frame(s, 3, 2, 10, 9, outer=(18, 63, 53), mid=(183, 123, 101), inner=(214, 160, 136))
    R(s, (251, 250, 248), 4, 3, 8, 7)
    for (hx, hy) in ((6, 5), (7, 5), (9, 5), (10, 5), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (7, 7), (8, 7), (9, 7),
                     (8, 8)):
        P(s, (18, 63, 53), hx, hy)
    P(s, (183, 123, 101), 7, 5)
    return s


def _boia():
    s = new(16, 16)
    pygame.draw.circle(s, (20, 10, 26, 90), (9, 7), 6)
    pygame.draw.circle(s, (240, 240, 244), (8, 6), 6)
    pygame.draw.circle(s, (0, 0, 0, 0), (8, 6), 3)
    for (a, b) in (((3, 2), (5, 4)), ((11, 2), (13, 4)), ((3, 8), (5, 10)), ((11, 8), (13, 10))):
        R(s, (220, 60, 60), a[0], a[1], b[0] - a[0], b[1] - a[1])
    pygame.draw.circle(s, (0, 0, 0, 0), (8, 6), 3)
    pygame.draw.circle(s, (150, 130, 100), (8, 6), 6, 1)
    return s


OBJECT_BUILDERS = {"quadro_paisagem": _quadro_paisagem, "quadro_abstrato": _quadro_abstrato,
                   "quadro_flores": _quadro_flores, "relogio": _relogio, "arandela": _arandela,
                   "prateleira": _prateleira, "vaso_parede": _vaso_parede, "diploma": _diploma,
                   "capa_jornal": _capa_jornal, "quadro_cmh": _quadro_cmh, "boia": _boia}
OBJECT_DEFS = {k: (1, 1, False, "wall") for k in OBJECT_BUILDERS}
art.OBJECT_BUILDERS.update(OBJECT_BUILDERS)

# o que cada lugar ganha nas paredes (na ordem; repete se faltar)
THEMES = {
    "hq": ["quadro_abstrato", "arandela", "diploma", "relogio", "arandela", "quadro_paisagem"],
    "cafe": ["quadro_paisagem", "vaso_parede", "prateleira", "arandela", "quadro_flores"],
    "catco": ["capa_jornal", "relogio", "quadro_abstrato", "capa_jornal", "vaso_parede"],
    "books": ["prateleira", "quadro_paisagem", "arandela", "relogio", "prateleira"],
    "market": ["vaso_parede", "relogio", "quadro_flores", "vaso_parede"],
    "trattoria": ["quadro_paisagem", "vaso_parede", "arandela", "prateleira", "quadro_flores", "arandela"],
    "bar": ["arandela", "quadro_abstrato", "arandela", "relogio"],
    "cinema": ["arandela", "arandela"],
    "hospital": ["quadro_cmh", "relogio", "diploma", "quadro_flores", "vaso_parede", "quadro_paisagem"],
    "ricci": ["quadro_paisagem", "arandela", "quadro_flores", "arandela", "relogio"],
    "marina": ["boia", "quadro_paisagem", "relogio", "boia"],
    "bayside": ["quadro_flores", "arandela", "vaso_parede", "arandela", "quadro_paisagem"],
    "residencial": ["quadro_abstrato", "arandela", "quadro_paisagem", "arandela", "vaso_parede"],
}


def _tall(o):
    """Móvel alto encostado na parede (o desenho sobe por cima da face da parede)."""
    try:
        return art.object_sprite(o.kind).get_height() > TILE * 1.15
    except Exception:
        return True


def decorate(maps):
    """Põe os enfeites de parede de THEMES onde a parede está livre (2 tiles vazios entre um enfeite novo e outro)."""
    from .world import Obj
    for name, kinds in THEMES.items():
        m = maps.get(name)
        if m is None or m.outdoor or any(o.kind in OBJECT_BUILDERS for o in m.objects):
            continue
        taken = set()
        for o in m.objects:
            if o.layer in ("wall", "decal"):
                for yy in range(o.y, o.y + o.h):
                    for xx in range(o.x, o.x + o.w):
                        taken.add((xx, yy))
            elif o.layer == "obj" and _tall(o):
                for xx in range(o.x, o.x + o.w):
                    taken.add((xx, o.y - 1))
        doors = {(x, y) for y in range(m.h) for x in range(m.w) if m.tiles[y][x] == "door"} | set(m.doors)
        rnd = random.Random("enfeites-" + name)
        i = rnd.randrange(len(kinds))
        placed = 0
        limit = max(3, sum(1 for y in range(m.h) for x in range(m.w) if _is_face(m, x, y)) // 6)
        for y in range(m.h):
            last = -99
            for x in range(m.w):
                if not _is_face(m, x, y) or (x, y) in taken:
                    continue
                if any((x + dx, y + dy) in doors for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    continue
                if not (_is_face(m, x - 1, y) and _is_face(m, x + 1, y)):      # nada colado no canto
                    continue
                if x - last < 3:
                    continue
                o = Obj(kinds[i % len(kinds)], x, y)
                m.objects.append(o)
                m.wall_decor.append(o)
                taken.add((x, y))
                last = x
                i += 1
                placed += 1
                if placed >= limit:
                    break
            if placed >= limit:
                break

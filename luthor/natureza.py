"""Mar e natureza com vida.

- Mar: fica mais escuro conforme se afasta da areia, com ondulações que andam devagar em direção à praia e
  brilhinhos que acendem e apagam (`draw_sea`, no lugar dos tiles "sea"/"sea_foam").
- Ondas na areia: a água sobe pela areia, deixa espuma e volta, com a areia molhada marcando até onde ela chega
  (`draw_shore`); o píer fica de fora.
- Reflexos no mar depois do escurecimento: dourados no pôr do sol e um caminho prateado de luar à noite
  (`draw_glints`, depois da iluminação; chovendo, nada).
- Vento: árvores e arbustos balançam (a copa entorta 1 ou 2 px de arte, mais na chuva e na tempestade) e rajadas
  passam pela cidade como uma onda; tufinhos de grama balançam junto (`object_image`, `faded`, `draw_ground`).
"""
import math
import random

import pygame

from . import art
from .art import new, R, P, shade, mix, up, cached
from .config import TS, TILE, SCALE

SEA = ("sea", "sea_foam")

# ---------------------------------------------------------------------------
# Mar
# ---------------------------------------------------------------------------
SHALLOW, MID, DEEP = (96, 190, 214), (56, 146, 208), (36, 100, 172)
SEA_FRAMES, SEA_FPS = 24, 4.0          # ondulação anda 1 px de arte por quadro e repete a cada 24 px
DUSK_NEAR, DUSK_FAR = (240, 176, 150), (190, 118, 168)   # céu do pôr do sol refletido (pêssego -> lilás)


def _depth_color(d):
    """Cor do mar a d tiles da areia."""
    t = min(1.0, max(0.0, d / 8.0))
    if t < 0.4:
        return mix(SHALLOW, MID, t / 0.4)
    return mix(MID, DEEP, (t - 0.4) / 0.6)


def _sea_strip(d, f, dusk=0):
    """Faixa de 4 tiles de largura (repete) do mar na fileira d (0 = encostada na areia), quadro f.
    dusk (0..4): quanto do céu do pôr do sol o mar reflete."""
    key = d if d < 9 else 9 + d % 3

    def color(dd):
        c = _depth_color(dd)
        if dusk:
            c = mix(c, mix(DUSK_NEAR, DUSK_FAR, min(1.0, dd / 8.0)), 0.5 * dusk / 4)
        return c

    def make():
        W = 64
        s = new(W, TS)
        for yy in range(TS):
            R(s, color(key + yy / TS), 0, yy, W, 1)
        Y = key * TS
        near = max(0.35, 1.0 - key / 10)                 # cristas mais marcadas perto da praia
        for x in range(W):
            wob = round(1.4 * math.sin(2 * math.pi * x / 32) + 0.8 * math.sin(2 * math.pi * x / 64 + 1.0))
            for yy in range(TS):
                v = Y + yy + wob + f
                k = v % 8
                if k > 1:
                    continue
                ci = (v // 8) % 3
                if (x + ci * 21 + wob * 3) % 32 >= 20:     # crista quebrada em pedaços
                    continue
                base = color(key + yy / TS)
                if k == 0:
                    P(s, mix(base, (255, 255, 255), 0.2 * near), x, yy)
                else:
                    P(s, shade(base, 1 - 0.06 * near), x, yy)
        rnd = random.Random(f"brilho{key}")
        for _ in range(3):                               # brilhinhos que acendem e apagam
            gx, gy, ph = rnd.randrange(W - 4), rnd.randrange(TS), rnd.random()
            b = math.sin(2 * math.pi * (f / SEA_FRAMES + ph))
            if b > 0.2:
                L = 1 + int(b * 2.5)
                R(s, mix(color(key + gy / TS), (255, 255, 255), 0.45 + 0.3 * b), gx, gy, L, 1)
        return up(s)
    return cached(("mar", key, f, dusk), make)


def _sea_info(m):
    """Primeira fileira de mar de cada coluna (para a profundidade) e trechos de praia com areia em cima."""
    info = getattr(m, "_natureza", None)
    if info is None:
        top = {}
        for (x, y, t) in m.anim_tiles:
            if t in SEA and (x not in top or y < top[x]):
                top[x] = y
        runs = []
        cur = None
        for x in range(m.w):
            y = top.get(x)
            ok = y is not None and m.tile_at(x, y) in SEA and m.tile_at(x, y - 1) == "sand"
            if ok and cur and cur[2] == y and cur[1] == x - 1:
                cur[1] = x
            elif ok:
                cur = [x, x, y]
                runs.append(cur)
            else:
                cur = None
        info = m._natureza = dict(top=top, runs=[tuple(r) for r in runs])
    return info


def draw_sea(g, surf, m, cam, x0, y0, x1, y1, sun=0.0):
    """Desenha os tiles de mar visíveis. Devolve False se o mapa não tem mar (aí o jogo usa os tiles antigos)."""
    info = _sea_info(m)
    if not info["top"]:
        return False
    f = int(g.t * SEA_FPS) % SEA_FRAMES
    dusk = int(round(min(1.0, sun * 1.4) * 4))
    top = info["top"]
    for (x, y, t) in m.anim_tiles:
        if t in SEA and x0 <= x <= x1 and y0 <= y <= y1:
            strip = _sea_strip(y - top.get(x, y), f, dusk)
            surf.blit(strip, (x * TILE - cam[0], y * TILE - cam[1]), ((x % 4) * TILE, 0, TILE, TILE))
    return True


# ---------------------------------------------------------------------------
# Ondas na areia
# ---------------------------------------------------------------------------
SW_W, SW_UP, SW_DN = 128, 16, 7        # faixa: 128 px de arte (repete), 16 acima da linha da praia, 7 abaixo
SW_FRAMES, SW_PERIOD = 36, 5.5


def _swash(f):
    def make():
        s = new(SW_W, SW_UP + SW_DN)
        y0 = SW_UP
        p = f / SW_FRAMES
        for x in range(SW_W):
            ph = (p + 0.07 * math.sin(2 * math.pi * x / 128) + 0.03 * math.sin(2 * math.pi * x / 32 + 0.7)) % 1.0
            reach = 9.5 + 2.5 * math.sin(2 * math.pi * x / 64 + 1.1) + 1.5 * math.sin(2 * math.pi * x * 3 / 128 + 0.4)
            if ph < 0.32:                                # a onda sobe pela areia
                a = reach * (1 - (1 - ph / 0.32) ** 2)
            else:                                        # e volta devagar
                a = reach * (1 - (ph - 0.32) / 0.68) ** 1.5
            wet = int(reach + 1.5)
            for k in range(wet):                         # areia molhada até onde a água chega
                P(s, (92, 70, 44, 22 + int(34 * (1 - k / wet))), x, y0 - 1 - k)
            top = y0 - int(round(a))
            for yy in range(top, y0):                    # lâmina de água por cima da areia
                frac = (y0 - yy) / max(1.0, a)
                P(s, (150, 222, 232, int(175 - 95 * frac)), x, yy)
            back = ph > 0.32
            if not back or (x * 7 + int(ph * 23)) % 5:   # espuma na frente da água (rendada quando volta)
                P(s, (246, 252, 252, 150 if back else 235), x, top)
                if not back:
                    P(s, (214, 240, 246, 170), x, top + 1)
            # arrebentação: espuma branca logo depois da linha da praia, mais forte antes da onda subir
            bk = max(0.0, math.cos(2 * math.pi * (ph - 0.97))) ** 4
            by = y0 + 2 + int(round(1.3 * math.sin(2 * math.pi * x / 32 + f * 0.17)))
            if bk > 0.05:
                P(s, (248, 252, 252, int(220 * bk)), x, by)
                if (x + f) % 3:
                    P(s, (220, 242, 248, int(150 * bk)), x, by + 1)
            P(s, (236, 248, 250, 110), x, y0)            # linha fina onde a água encontra a areia
        return up(s)
    return cached(("onda", f), make)


def draw_shore(g, surf, m, cam):
    info = _sea_info(m)
    if not info["runs"]:
        return
    SWd, SHd = surf.get_size()
    f = int((g.t % SW_PERIOD) / SW_PERIOD * SW_FRAMES) % SW_FRAMES
    strip = _swash(f)
    sw = SW_W * SCALE
    old = surf.get_clip()
    for (xa, xb, y) in info["runs"]:
        top = y * TILE - SW_UP * SCALE - cam[1]
        if top > SHd or top + strip.get_height() < 0:
            continue
        clip = pygame.Rect(xa * TILE - cam[0], top, (xb - xa + 1) * TILE, strip.get_height()).clip(old)
        if clip.w <= 0:
            continue
        surf.set_clip(clip)
        k0 = (clip.x + cam[0]) // sw
        X = k0 * sw - cam[0]
        while X < clip.right:
            surf.blit(strip, (X, top))
            X += sw
    surf.set_clip(old)


# ---------------------------------------------------------------------------
# Reflexos (pôr do sol e luar), depois da iluminação
# ---------------------------------------------------------------------------
def _path_glow(kind, q):
    """Faixa de luz suave no mar (o caminho do sol ou da lua), mais larga e forte para longe da praia."""
    def make():
        W, H = 560, 480
        s = pygame.Surface((W // 4, H // 4))
        col = (110, 54, 18) if kind == "sol" else (40, 48, 70)
        k = q / 6
        for y in range(H // 4):
            fy = 0.35 + 0.65 * (y / (H // 4))
            half = (W // 8) * (0.45 + 0.55 * y / (H // 4))
            for x in range(W // 4):
                dx = (x - W // 8) / max(1.0, half)
                v = math.exp(-dx * dx * 2.2) * fy * k
                s.set_at((x, y), tuple(int(c * v) for c in col))
        return pygame.transform.smoothscale(s, (W, H))
    return cached(("caminho", kind, q), make)


def draw_glints(g, surf, m, cam, minutes, sun, dark, weather):
    if weather == "chuva" or not m.outdoor:
        return
    info = _sea_info(m)
    if not info["top"]:
        return
    SWd, SHd = surf.get_size()
    top = min(info["top"].values()) * TILE - cam[1] + 6 * SCALE
    if top >= SHd:
        return
    top = max(0, top)
    night = max(0.0, min(1.0, (dark - 0.3) / 0.3))
    old = surf.get_clip()
    surf.set_clip(pygame.Rect(0, top, SWd, SHd - top).clip(old))
    for kind, amount in (("sol", sun), ("lua", night)):
        q = int(round(amount * 6))
        if q:
            glow = _path_glow(kind, q)
            surf.blit(glow, (int(SWd * (0.3 if kind == "sol" else 0.64)) - glow.get_width() // 2, top),
                      special_flags=pygame.BLEND_RGB_ADD)
    surf.set_clip(old)
    for kind, amount in (("sol", sun), ("lua", night)):
        n = int(70 * amount) if kind == "sol" else int(46 * amount)
        if n <= 0:
            continue
        cx = SWd * (0.3 if kind == "sol" else 0.64)
        for i in range(n):
            t = g.t * (2.2 if kind == "sol" else 1.6) + i * 0.618
            slot, ph = int(t), t % 1.0
            rnd = random.Random(i * 7919 + slot * 104729 + (0 if kind == "sol" else 55))
            y = top + rnd.random() ** 0.8 * (SHd - top)
            spread = 60 + 0.45 * (y - top) if kind == "lua" else SWd * 0.26
            x = cx + rnd.gauss(0, spread)
            b = math.sin(math.pi * ph) * amount
            if b < 0.08:
                continue
            L = int((2 + rnd.random() * 5) * b + 1) * SCALE
            if kind == "sol":
                col = (int(255 * b), int(176 * b), int(90 * b))
            else:
                col = (int(120 * b), int(134 * b), int(170 * b))
            surf.fill(col, (int(x) - L // 2, int(y), L, SCALE), special_flags=pygame.BLEND_RGB_ADD)
            if L >= 5 * SCALE:
                surf.fill(tuple(c // 2 for c in col), (int(x) - L // 4, int(y) - SCALE, L // 2, SCALE),
                          special_flags=pygame.BLEND_RGB_ADD)


# ---------------------------------------------------------------------------
# Vento: árvores, arbustos e tufinhos de grama
# ---------------------------------------------------------------------------
SWAY = {"tree": 1.0, "tree2": 1.0, "tree3": 1.0, "pine": 0.75, "palm": 1.25, "bush": 0.6, "bush2": 0.6, "bush3": 0.6}
PAD = 2                                # px de arte de folga de cada lado (a copa entorta até 2 px)
_frames = {}


def _shear(img, off):
    """Copa entortada `off` px de arte para o lado (o tronco fica parado)."""
    w, h = img.get_size()
    out = pygame.Surface((w + PAD * 2 * SCALE, h), pygame.SRCALPHA)
    H = h // SCALE
    crown = int(H * 0.72)
    for r in range(H):
        wgt = ((crown - r) / crown) ** 1.3 if r < crown else 0.0
        dx = int(round(off * wgt))
        out.blit(img, (PAD * SCALE + dx * SCALE, r * SCALE), (0, r * SCALE, w, SCALE))
    return out


def _tree_frames(kind):
    base = art.object_sprite(kind)
    hit = _frames.get(kind)
    if hit is None or hit[0] is not base:           # a estação troca o desenho da árvore
        hit = (base, {}, {})
        _frames[kind] = hit
    return hit


def wind(g):
    """(força, velocidade) do vento conforme o clima."""
    if g.weather == "chuva":
        return (2.0, 2.7) if getattr(g, "storm", False) else (1.35, 1.9)
    return 1.0, 1.25


def sway_offset(g, o):
    amp, speed = wind(g)
    gust = max(0.0, math.sin(g.t * 0.33 - o.x * 0.06 + o.y * 0.02))     # rajada que atravessa a cidade
    a = amp * SWAY[o.kind] * (0.55 + 0.8 * gust ** 3)
    v = a * math.sin(g.t * speed + o.x * 0.7 + o.y * 0.3)
    return max(-2, min(2, int(round(v))))


def object_image(g, o):
    if o.kind not in SWAY:
        return None
    base, frames, _ = _tree_frames(o.kind)
    off = sway_offset(g, o)
    img = frames.get(off)
    if img is None:
        img = frames[off] = _shear(base, off)
    return img


def faded(g, o):
    """Copa translúcida (a jogadora atrás da árvore), no mesmo quadro do balanço."""
    img = object_image(g, o)
    if img is None:
        from . import scenery
        return scenery.faded(o.kind)
    _, _, fades = _tree_frames(o.kind)
    off = sway_offset(g, o)
    f = fades.get(off)
    if f is None:
        f = img.copy()
        f.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_MULT)
        fades[off] = f
    return f


def _tuft(lean, cols):
    def make():
        base, dk, lt = cols
        s = new(7, 6)
        for (bx, bh, tilt) in ((1, 4, -1), (3, 6, 0), (5, 5, 1), (2, 3, 0)):
            for k in range(bh):
                frac = k / max(1, bh - 1)
                dx = int(round((tilt * 0.6 + lean) * frac))
                c = dk if k < 2 else (lt if k == bh - 1 else base)
                P(s, c, bx + dx, 5 - k)
        return up(s)
    return cached(("tufo", lean, cols), make)


def _tufts(m):
    tufts = getattr(m, "_tufts", None)
    if tufts is None:
        tufts = []
        busy = set()
        for o in m.objects:
            for yy in range(o.y, o.y + o.h):
                for xx in range(o.x, o.x + o.w):
                    busy.add((xx, yy))
        for b in m.buildings:
            for yy in range(b.y, b.y + b.h):
                for xx in range(b.x, b.x + b.w):
                    busy.add((xx, yy))
        for y in range(m.h):
            for x in range(m.w):
                if m.tiles[y][x] != "grass" or (x, y) in busy:
                    continue
                rnd = random.Random(x * 92821 + y * 68917)
                if rnd.random() < 0.16:
                    tufts.append((x * TILE + rnd.randrange(2, 10) * SCALE, y * TILE + rnd.randrange(4, 12) * SCALE,
                                  rnd.random() * 6.28))
        m._tufts = tufts
    return tufts


def draw_ground(g, surf, m, cam):
    """Tufinhos de grama balançando (só ao ar livre e fora do inverno)."""
    from . import seasons, scenery
    if not m.outdoor or seasons.CURRENT["season"] == "winter":
        return
    SWd, SHd = surf.get_size()
    cols = (scenery.GRASS, shade(scenery.GRASS_DK, 0.92), scenery.GRASS_LT)
    amp, speed = wind(g)
    for (px, py, ph) in _tufts(m):
        x, y = px - cam[0], py - cam[1]
        if x < -20 or y < -20 or x > SWd or y > SHd:
            continue
        gust = max(0.0, math.sin(g.t * 0.33 - px / TILE * 0.06 + py / TILE * 0.02))
        v = amp * (0.6 + 0.9 * gust ** 2) * math.sin(g.t * speed * 1.4 + ph)
        surf.blit(_tuft(max(-1, min(1, int(round(v)))), cols), (x, y))

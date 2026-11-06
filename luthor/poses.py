"""Poses dos bonequinhos: sentada de verdade (pernas dobradas), comendo, bebendo e lendo, e algumas carinhas.

Os quadros usam as mesmas peças de sprites.py (cabeça, cabelo, roupa e altura de cada uma) e só trocam as pernas,
os braços ou o rosto. Cada combinação é desenhada uma vez só e fica guardada em cache.

Sentada: o quadril fica na altura do assento (`SEAT_LIFT`, em pixels de arte) e o pé encosta no chão. De frente
aparecem o colo (mais claro, porque a luz vem de cima), a sombra embaixo dos joelhos e as canelas; de lado, a coxa
vai para a frente e a canela desce; de costas, as pernas ficam escondidas e as mãos vão para a mesa.

Braços: "hold" (segurando algo na frente do peito com as duas mãos) e "mouth" (uma das mãos levando à boca).
Rostos: "happy" (olhinhos fechados e sorriso), "read" (olhando para baixo) e "open" (boca aberta na mordida).
"""
import pygame

from . import sprites
from .art import up, mix, shade
from .config import SCALE
from .sprites import (Grid, _palette, _hair, _head, _body_front, _body_side, _outfit_overlay, _broaden, _extras,
                      _resize, _render, OUTFIT_BASE)

# altura do assento em pixels de arte (o corpo desce até ali); a jogadora senta nestes
SEAT_LIFT = {"chair": 7, "chair_blue": 7, "hchair": 6, "stool": 10, "bench": 6, "bench_l": 6, "bench_r": 6,
             "sofa": 8, "sofa_grey": 8, "armchair": 7, "poltrona_roxa": 7}
# NPCs e figurantes também sentam nas poltronas do cinema
NPC_SEATS = dict(SEAT_LIFT, seat=7)

VIEW = {"down": "front", "up": "back", "right": "side", "left": "side"}
PAD = 6                     # margem dos quadros de pose (px de arte de cada lado): braços erguidos, abraço
PANTS = ("P", "R", "p")
FEET = ("O", "o", "U")

# onde fica a comida/livro em cada pose (pixels de arte a partir do canto de cima do quadro, virada para a direita)
ANCHOR = {("front", "hold"): (8.0, 19.5), ("front", "mouth"): (8.5, 15.0),
          ("side", "hold"): (12.5, 18.5), ("side", "mouth"): (14.0, 14.0),
          ("back", "hold"): (8.0, -4.0), ("back", "mouth"): (8.0, -4.0),
          ("front", "up"): (8.0, -1.0), ("back", "up"): (8.0, -1.0), ("side", "up"): (13.0, 13.0),   # up: base do item
          ("front", "toast"): (16.0, 9.0), ("side", "toast"): (13.0, 12.5),
          ("front", "umbrella"): (14.5, 19.0), ("side", "umbrella"): (8.5, 17.0), ("back", "umbrella"): (14.5, 19.0)}

# px de arte entre o centro das duas no beijo (1 tile). De lado o rosto fica 5 px à frente do peito: assim as
# duas se inclinam 1 px (lean) e os narizes/lábios se encostam sem um rosto entrar no outro, e as mãos dadas
# se encontram no meio.
KISS_DIST = 16


def kiss_pose(stage, look, other, lead=False):
    """Pose de quem beija (de lado), de mãos dadas. stage: "close" (mãos dadas, olhos fechando), "kiss" (as duas
    se inclinam e os lábios se encostam) ou "after" (voltam e sorriem coradas). Quem é mais baixa fica na ponta
    dos pés durante o beijo. lead: sobrou da versão antiga (abraço); não muda nada."""
    tip = look.get("height", 0) < other.get("height", 0) and stage == "kiss"
    face = {"close": "shut", "kiss": "kiss", "after": "love"}[stage]
    return dict(arms="reach", face=face, lean=1 if stage == "kiss" else 0, tiptoe=tip, blink=False, bob=0)

_cache = {}


def look_key(look):
    return tuple(sorted((k, tuple(v) if isinstance(v, (tuple, list)) else v) for k, v in look.items()))


def seat_offset(lift):
    """Quanto o desenho desce (px de tela) em relação a ela em pé, para o quadril ficar no assento."""
    return (7 - lift) * SCALE


def anchor(d, where, look):
    """Ponto (px de arte, a partir do canto de cima do quadro) onde a mão segura o item nesta pose."""
    view = VIEW[d]
    ax, ay = ANCHOR[(view, where)]
    if d == "left":
        ax = 16 - ax
    dh = look.get("height", 0)
    if dh < 0 and ay < 25:                     # quem é mais baixa: a cabeça e o peito descem
        ay += -dh
    return ax + PAD, ay


WALK_FR = (0, 1, 0, 2)          # quadro de andar (0..3) -> pernas/braços de sprites.py


def frame(look, d, lift=None, arms=None, face=None, blink=False, swing=0, key=None, walk=0, lean=0, tiptoe=False):
    """Quadro da pose (Surface já ampliada). lift = altura do assento (None = em pé).

    walk: quadro de andar (0..3), para andar com guarda-chuva; lean: cabeça inclinada para a frente (px de arte);
    tiptoe: na ponta dos pés (no beijo, quem é mais baixa)."""
    lk = key or look_key(look)
    ck = (lk, d, lift, arms, face, blink, swing, walk, lean, tiptoe)
    img = _cache.get(ck)
    if img is None:
        if d == "left":
            img = pygame.transform.flip(frame(look, "right", lift, arms, face, blink, swing, lk, walk, lean, tiptoe),
                                        True, False)
        else:
            img = _build(look, d, lift, arms, face, blink, swing, walk, lean, tiptoe)
        if len(_cache) > 3000:                  # não deixa crescer sem fim (troca de roupa, estações...)
            _cache.clear()
        _cache[ck] = img
    return img


def _build(look, d, lift, arms, face, blink, swing, walk=0, lean=0, tiptoe=False):
    view = VIEW[d]
    pal = _palette(look)
    pal["G"] = mix(look["pants"], (255, 255, 255), 0.3)     # colo sentada: a luz de cima bate nas coxas
    pal["B2"] = mix(look["skin"], (255, 90, 130), 0.5)     # bochecha corada (beijo)
    style = look.get("style", "short")
    outfit_full = look.get("outfit", "shirt")
    outfit = OUTFIT_BASE.get(outfit_full, outfit_full)
    sprites._SHORT_SLEEVES["on"] = look.get("sleeves") == "short"
    hair = _hair(style, view)
    g = Grid()
    if view != "back":
        g.mask(hair, behind=True)
    body = Grid()
    fr = 1 if (view == "side" and lift is not None and not arms) else 0     # sentada de lado: mão na coxa
    if lift is None and walk:
        fr = WALK_FR[walk % 4]
    if view == "side":
        _body_side(body, outfit, fr)
    else:
        _body_front(body, outfit, view, fr)
    if outfit_full != outfit:
        _outfit_overlay(body, outfit_full, view, fr)
    if lift is not None:
        _LEGS[view](body, lift, outfit_full, swing)
    if arms and (view, arms) in _ARMS:
        _ARMS[(view, arms)](body)
    elif lift is not None and view == "back":
        _hands_forward(body)
    if look.get("broad") and view != "side":
        _broaden(body)
    g.px.update(body.px)
    _head(g, view, style, blink)
    g.mask(hair, behind=False if view != "back" else None)
    if face and view != "back" and face in _FACES:
        _FACES[face](g, view)
    _extras(g, look, view)
    if arms and (view, arms) in _LATE:          # braço levantado: na frente do cabelo
        _LATE[(view, arms)](g, body, bool(look.get("broad")))
    if lean:
        _lean(g, body, lean)
    if tiptoe:
        _tiptoe(g, view)
    h = _resize(g, look.get("height", 0))
    return up(_render_pad(g, pal, h))


def _render_pad(g, pal, h):
    """Igual a sprites._render, mas com PAD px de margem dos lados (o braço pode passar dos 16 px)."""
    w = 16 + 2 * PAD
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for (x, y), k in g.px.items():
        if -PAD <= x < 16 + PAD and 0 <= y < h:
            s.set_at((x + PAD, y), pal.get(k, (255, 0, 255)))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(-PAD, 16 + PAD):
            if (x, y) in g.px:
                continue
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                n = g.px.get((x + dx, y + dy))
                if n:
                    c = pal.get(n, (0, 0, 0))
                    out.set_at((x + PAD, y), (*mix(shade(c, 0.36), (34, 18, 30), 0.45), 255))
                    break
    out.blit(s, (0, 0))
    return out


def _lean(g, body, n):
    """Cabeça (e cabelo) inclinada n px para a frente; o corpo fica onde está."""
    out = {}
    for (x, y), k in g.px.items():
        if y >= 17 and body.px.get((x, y)) == k:
            continue
        out[(x + n, y)] = k
    for (x, y), k in body.px.items():
        if y >= 17 and g.px.get((x, y)) == k:
            out[(x, y)] = k
    g.px = {p: k for p, k in out.items() if -PAD <= p[0] < 16 + PAD}


def _tiptoe(g, view):
    """Na ponta dos pés: o corpo sobe 1 px e só a ponta do sapato encosta no chão."""
    bottom = max(y for (_x, y) in g.px)
    shoes = [(x, y) for (x, y), k in g.px.items() if y >= bottom - 1 and k in FEET]
    g.px = {(x, y - 1): k for (x, y), k in g.px.items()}
    if view == "side" and shoes:
        front = max(x for (x, _y) in shoes)
        g.px[(front, bottom)] = "U"
        g.px[(front - 1, bottom)] = "U"


# ---------------------------------------------------------------------------
# Pernas sentadas
# ---------------------------------------------------------------------------
def _sit_front(g, lift, outfit, swing):
    sb = 22 + min(lift, 8)                     # última linha do sapato (o pé no chão)
    gown = outfit == "gown"
    tights = outfit == "skirt_suit"
    for (x, y), k in list(g.px.items()):
        if y >= 26 or (y == 25 and k in PANTS + FEET):
            del g.px[(x, y)]
    for (x, y), k in list(g.px.items()):       # o colo (coxas para a frente) pega a luz de cima
        if y in (23, 24):
            if k in ("P", "R"):
                g.px[(x, y)] = "G"
            elif k == "C":
                g.px[(x, y)] = "Q"
    if not gown and g.px.get((6, 24)) in PANTS:   # joelhos para a frente: um pouco mais largos que o quadril
        kn = "p" if tights else "P"
        g.set(4, 24, kn); g.set(11, 24, "p")
        for x0 in (4, 9):
            g.set(x0, 25, kn); g.set(x0 + 1, 25, kn); g.set(x0 + 2, 25, "p")
        g.set(7, 25, "p"); g.set(8, 25, "p")   # sombra entre os joelhos
    for x in range(5, 11):                     # sombrinha embaixo dos joelhos
        if (x, 25) not in g.px:
            g.set(x, 25, "C" if gown else "p")
    if gown:                                   # vestido longo: cai até os tornozelos
        for y in range(26, sb - 1):
            g.row(y, 4, 11, "C")
            g.set(4, y, "c"); g.set(11, y, "c"); g.set(8, y, "c")
        for x0 in (5, 9):
            g.row(sb - 1, x0, x0 + 1, "O"); g.row(sb, x0, x0 + 1, "U")
        return
    col, sh = ("p", "p") if tights else ("P", "p")
    for leg, x0 in enumerate((5, 9)):
        up_ = 1 if swing == leg + 1 else 0     # balançando os pés: um sobe um pouquinho
        for y in range(26, sb - 1 - up_):
            g.set(x0, y, col); g.set(x0 + 1, y, sh)
        fy = sb - 1 - up_
        fx = x0 - 1 if leg == 0 else x0        # pontas dos pés um pouco para fora
        g.row(fy, fx, fx + 2, "O")
        g.set(fx if leg == 0 else fx + 2, fy, "o")
        g.row(fy + 1, fx, fx + 2, "U")


def _sit_side(g, lift, outfit, swing):
    sb = 22 + min(lift, 8)
    gown = outfit == "gown"
    tights = outfit == "skirt_suit"
    for (x, y), k in list(g.px.items()):
        if y >= 24 and (k in PANTS + FEET or gown):
            del g.px[(x, y)]
        elif y >= 25 and (x > 6 or y > 26):    # casaco/avental: só a barra de trás cai do assento
            del g.px[(x, y)]
    if gown:
        for x in range(4, 12):
            g.set(x, 23, "Q"); g.set(x, 24, "C")
        for y in range(25, sb - 1):
            g.row(y, 9, 12, "C"); g.set(12, y, "c")
        g.row(sb - 2, 9, 13, "C"); g.set(13, sb - 2, "c")
        g.row(sb - 1, 11, 13, "O"); g.set(13, sb - 1, "o"); g.row(sb, 11, 13, "U")
        return
    for x in range(5, 12):                     # coxa (2 linhas) do quadril até o joelho
        top, low = ("P", "P") if tights and x <= 9 else ("p", "p") if tights else ("G", "P")
        if g.px.get((x, 23)) in (None,) + PANTS:
            g.set(x, 23, top)
        if g.px.get((x, 24)) in (None,) + PANTS:
            g.set(x, 24, low)
    if tights:
        g.set(9, 24, "p")                      # barra da saia
    elif (4, 24) not in g.px:
        g.set(4, 24, "p")
    col, front = ("p", "p") if tights else ("P", "R")
    kick = 1 if swing else 0                   # balançando: o pé vai um pouquinho para a frente
    for y in range(25, sb - 1):
        dx = kick if y >= sb - 2 else 0
        g.set(10 + dx, y, col); g.set(11 + dx, y, front)
    fx = 10 + kick
    g.row(sb - 1, fx, fx + 3, "O"); g.set(fx + 3, sb - 1, "o")
    g.row(sb, fx, fx + 3, "U")


def _sit_back(g, lift, outfit, swing):
    for (x, y) in list(g.px):
        if y >= 25:
            del g.px[(x, y)]


_LEGS = {"front": _sit_front, "side": _sit_side, "back": _sit_back}


def _hands_forward(g):
    """De costas, sentada à mesa: os antebraços vão para a frente (as mãos somem atrás do corpo)."""
    for (x, y) in list(g.px):
        if y >= 21 and (x <= 4 or x >= 11) and y <= 24:
            del g.px[(x, y)]


# ---------------------------------------------------------------------------
# Braços
# ---------------------------------------------------------------------------
def _clear_arm_front(g, x0):
    out, inn = g.px.get((x0, 18), "C"), g.px.get((x0 + 1, 18), "c")
    short = g.px.get((x0, 20)) == "S"
    for y in range(18, 23):
        g.px.pop((x0, y), None)
        g.px.pop((x0 + 1, y), None)
    if g.px.get((x0, 23)) in ("S", "s"):
        del g.px[(x0, 23)]
    for y in (18, 19, 20):                     # braço de cima continua no lugar
        g.set(x0, y, out); g.set(x0 + 1, y, inn)
    if short:
        g.set(x0, 20, "S"); g.set(x0 + 1, 20, "s")
    return (("S", "s") if short else (out, inn))


def _arms_hold_front(g):
    lo, li = _clear_arm_front(g, 3)
    ro, ri = _clear_arm_front(g, 11)
    g.set(4, 21, lo); g.set(5, 21, li)         # antebraços vindo para a frente
    g.set(11, 21, ro); g.set(10, 21, ri)
    g.set(6, 21, "S"); g.set(6, 20, "s")       # mãos juntas na frente do peito
    g.set(9, 21, "S"); g.set(9, 20, "s")


def _arms_mouth_front(g):
    ro, ri = _clear_arm_front(g, 11)
    g.set(11, 21, ro); g.set(12, 21, ri)       # cotovelo
    g.set(10, 21, ri); g.set(10, 20, ro)       # antebraço sobe pela frente do peito
    g.set(9, 20, ri); g.set(10, 19, ro); g.set(9, 19, ri)
    g.set(10, 18, ro); g.set(9, 18, ri); g.set(9, 17, ro)
    g.set(8, 16, "S"); g.set(9, 16, "s")       # mão no queixo


def _clear_arm_side(g):
    out, inn = g.px.get((6, 18), "C"), g.px.get((7, 18), "c")
    short = g.px.get((6, 20)) == "S"
    for y in range(18, 23):                    # repinta o tronco onde o braço estava
        for x in (6, 7):
            g.set(x, y, "C")
    for x in (6, 7):
        if g.px.get((x, 23)) in ("S", "s"):
            g.set(x, 23, "P")
    g.set(6, 18, out); g.set(7, 18, inn); g.set(6, 19, out); g.set(7, 19, inn)
    return out, inn, (("S", "s") if short else (out, inn))


def _arms_hold_side(g):
    out, inn, (fo, fi) = _clear_arm_side(g)
    g.set(7, 20, out); g.set(8, 20, inn)       # cotovelo
    g.set(9, 20, fo); g.set(10, 20, fi)        # antebraço para a frente
    g.set(11, 20, "S"); g.set(11, 19, "s")     # mão


def _arms_mouth_side(g):
    out, inn, (fo, fi) = _clear_arm_side(g)
    g.set(7, 20, out); g.set(8, 20, inn)
    g.set(9, 19, fo); g.set(10, 19, fi); g.set(10, 18, fo); g.set(11, 17, fo)   # antebraço subindo
    g.set(11, 16, "s"); g.set(12, 16, "S")     # mão na boca


def _drop_arm_front(g, x0):
    """Tira o braço que estava caído (fica só o ombro); guarda as cores para o antebraço levantado."""
    out, inn = g.px.get((x0, 18), "C"), g.px.get((x0 + 1, 18), "c")
    short = g.px.get((x0, 20)) == "S"
    for y in range(19, 23):
        g.px.pop((x0, y), None)
        g.px.pop((x0 + 1, y), None)
    for y in (22, 23):
        if g.px.get((x0, y)) in ("S", "s"):
            del g.px[(x0, y)]
    g.arm_colors = getattr(g, "arm_colors", {})
    g.arm_colors[x0] = ("S", "s") if short else (out, inn)


def _arms_drop_right(g):
    _drop_arm_front(g, 11)


def _arms_drop_both(g):
    _drop_arm_front(g, 11)
    _drop_arm_front(g, 3)


# caminho do braço levantado (borda de fora), do ombro para cima; o lado de dentro é a coluna vizinha
ARM_PATHS = {
    "wave": [(13, 17), (14, 16), (14, 15), (15, 14)],                 # "oi!": mão ao lado do rosto
    "wave2": [(13, 17), (14, 16), (15, 15), (16, 14)],                # mão balançando para fora
}

# "viva!" (o peixe pescado flutua acima da cabeça, como no Stardew): os dois braços abrem em Y, com o fundo
# aparecendo entre o braço e a cabeça (colado na cabeça parecia "mão na nuca" ou orelha), e as mãos abertas
# ficam na altura do alto da cabeça. Precisa de PAD >= 6 (mão em x 19, +1 nos ombros largos, + contorno)
RAISE_PATH = [(13, 17), (14, 16), (15, 15), (16, 14), (17, 13), (18, 12), (18, 11), (19, 10), (19, 9)]
RAISE_CUFF = (19, 8)                       # punho da manga (mais escuro: separa a mão de casaco cor de pele)
RAISE_HAND = [(19, 7, "S"), (18, 7, "S"), (19, 6, "S"), (18, 6, "S"), (18, 5, "s"), (19, 5, "S"),
              (17, 6, "S")]                # mão aberta, arredondada pelo contorno; polegar para dentro


def _late_arm_up(g, body, broad, right=True, path="wave"):
    """Braço levantado em diagonal (por cima do cabelo) e a mão aberta no alto."""
    x0 = 11 if right else 3
    ro, ri = getattr(body, "arm_colors", {}).get(x0, ("C", "c"))
    s = 1 if right else -1
    b = (1 if broad else 0) * s

    def fx(x):                                     # caminho desenhado para a direita; espelha para a esquerda
        return (x if right else 15 - x) + b
    pts = ARM_PATHS[path]
    for (x, y) in pts:
        g.px[(fx(x), y)] = ro
        g.px[(fx(x) + s, y)] = ri
        g.px[(fx(x), y + 1)] = g.px.get((fx(x), y + 1)) if (fx(x), y + 1) in g.px and y + 1 <= 18 else ri
    hx, hy = fx(pts[-1][0]), pts[-1][1] - 1        # mão (2x2) logo acima do antebraço
    g.px[(hx, hy)] = "S"
    g.px[(hx + s, hy)] = "s"
    g.px[(hx, hy - 1)] = "S"
    g.px[(hx + s, hy - 1)] = "S"


def _late_wave(g, body, broad):
    _late_arm_up(g, body, broad, True, "wave")


def _late_wave2(g, body, broad):
    _late_arm_up(g, body, broad, True, "wave2")


def _late_up(g, body, broad):
    """Os dois braços erguidos em Y, por cima do cabelo (sai do ombro e fica sempre ligado ao corpo)."""
    for right in (True, False):
        x0 = 11 if right else 3
        ro, ri = getattr(body, "arm_colors", {}).get(x0, ("C", "c"))
        s = 1 if right else -1
        b = s if broad else 0

        def fx(x):                                 # caminho desenhado para a direita; espelha para a esquerda
            return (x if right else 15 - x) + b
        for (x, y) in RAISE_PATH:
            g.px[(fx(x), y)] = ro                  # borda de fora
            g.px[(fx(x) - s, y)] = ri              # sombra do lado de dentro
        cx, cy = RAISE_CUFF
        cuff = "s" if (ro, ri) == ("S", "s") else ri          # manga curta: o punho é só a pele na sombra
        g.px[(fx(cx), cy)] = cuff
        g.px[(fx(cx) - s, cy)] = cuff
        for (x, y, k) in RAISE_HAND:
            g.px[(fx(x), y)] = k


def _arms_wave_side(g, tilt=0):
    out, inn, (fo, fi) = _clear_arm_side(g)
    g.set(7, 19, out); g.set(8, 19, inn)            # braço para a frente, mão na altura do queixo
    g.set(9, 18, fo); g.set(10, 18, fi); g.set(10, 17, fo); g.set(11, 17, fi)
    g.set(12 + tilt, 15, "S"); g.set(12, 16, "S"); g.set(13, 16, "s")


def _arms_wave2_side(g):
    _arms_wave_side(g, 1)


def _arms_umbrella_front(g):
    ro, ri = _clear_arm_front(g, 11)
    g.px.pop((11, 20), None); g.px.pop((12, 20), None)
    g.set(13, 20, ro); g.set(12, 20, ri)            # cotovelo dobrado para o lado
    g.set(14, 19, "S"); g.set(14, 20, "s")          # mão do lado do corpo (o cabo sobe por fora do rosto)


def _arms_umbrella_side(g):
    out, inn, (fo, fi) = _clear_arm_side(g)
    g.set(6, 20, out); g.set(7, 20, inn)
    g.set(8, 19, fo); g.set(8, 18, fi)
    g.set(8, 17, "S"); g.set(9, 17, "s")


def _arms_reach_side(g):
    """Beijo de mãos dadas: o braço da frente desce em diagonal até o meio do caminho entre as duas (a 1 tile,
    as mãos se encontram; com as duas cabeças em cima, o desenho forma um coraçãozinho)."""
    out, inn, (fo, fi) = _clear_arm_side(g)
    for (x, y) in ((8, 19), (9, 20), (10, 20), (11, 21), (12, 21), (13, 22)):
        o, i = (out, inn) if x < 10 else (fo, fi)
        g.set(x, y, o)
        if (x, y - 1) not in g.px:
            g.set(x, y - 1, i)
    g.set(14, 22, "S"); g.set(15, 22, "S"); g.set(14, 23, "s"); g.set(15, 23, "s")


def _arms_umbrella_back(g):
    _arms_umbrella_front(g)


def _arms_toast_side(g):
    """Brinde de lado: o braço vai reto para a frente na altura do peito (o copo fica longe do rosto e encontra
    o copo de quem está a 1 tile, no meio do caminho)."""
    out, inn, (fo, fi) = _clear_arm_side(g)
    g.set(7, 20, out); g.set(8, 20, inn)            # cotovelo
    for x in range(9, 13):                          # antebraço
        g.set(x, 20, fo if x % 2 else fi)
    g.set(13, 20, "S"); g.set(13, 21, "s")          # mão segurando o copo


def _arms_work_back(g):
    """De costas, mexendo na bancada: os antebraços vão para a frente e somem atrás do corpo."""
    for x0 in (3, 11):
        for y in (21, 22, 23):
            for x in (x0, x0 + 1):
                if y < 23 or g.px.get((x, y)) in ("S", "s"):
                    g.px.pop((x, y), None)


_ARMS = {("front", "hold"): _arms_hold_front, ("front", "mouth"): _arms_mouth_front,
         ("side", "hold"): _arms_hold_side, ("side", "mouth"): _arms_mouth_side,
         ("front", "wave"): _arms_drop_right, ("front", "wave2"): _arms_drop_right,
         ("back", "wave"): _arms_drop_right, ("back", "wave2"): _arms_drop_right,
         ("side", "wave"): _arms_wave_side, ("side", "wave2"): _arms_wave2_side,
         ("front", "up"): _arms_drop_both, ("side", "up"): _arms_wave_side, ("back", "up"): _arms_drop_both,
         ("front", "umbrella"): _arms_umbrella_front, ("side", "umbrella"): _arms_umbrella_side,
         ("back", "umbrella"): _arms_umbrella_back,
         ("front", "toast"): _arms_drop_right, ("side", "toast"): _arms_toast_side,
         ("side", "reach"): _arms_reach_side, ("front", "reach"): _arms_hold_front,
         ("front", "work"): _arms_hold_front, ("side", "work"): _arms_hold_side, ("back", "work"): _arms_work_back}
# a segunda parte do braço levantado entra depois do cabelo (senão o cabelo comprido esconde a mão)
_LATE = {("front", "wave"): _late_wave, ("front", "wave2"): _late_wave2, ("back", "wave"): _late_wave,
         ("back", "wave2"): _late_wave2, ("front", "up"): _late_up, ("back", "up"): _late_up,
         ("front", "toast"): _late_wave}


# ---------------------------------------------------------------------------
# Rostos
# ---------------------------------------------------------------------------
def _clear_eyes(g, view):
    xs = (3, 4, 5, 10, 11, 12) if view == "front" else (11, 12)
    for y in (9, 10, 11):
        for x in xs:
            g.set(x, y, "S")


def _face_happy(g, view):
    """Olhinhos fechados sorrindo (^^) e boca sorrindo."""
    _clear_eyes(g, view)
    if view == "front":
        for (x, y) in ((3, 11), (4, 10), (5, 10), (6, 11), (9, 11), (10, 10), (11, 10), (12, 11)):
            g.set(x, y, "L")
        g.set(6, 14, "M"); g.set(9, 14, "M")
        g.set(7, 15, "M"); g.set(8, 15, "M")
    else:
        g.set(11, 11, "L"); g.set(12, 10, "L"); g.set(13, 11, "L")
        g.set(12, 14, "M"); g.set(13, 14, "M")


def _face_read(g, view):
    """Olhando para baixo (lendo)."""
    _clear_eyes(g, view)
    if view == "front":
        g.row(10, 4, 5, "L"); g.row(10, 10, 11, "L")
        g.set(3, 11, "L"); g.set(12, 11, "L")
        g.set(4, 11, "I"); g.set(5, 11, "i"); g.set(10, 11, "I"); g.set(11, 11, "i")
    else:
        g.row(10, 11, 12, "L")
        g.set(11, 11, "I"); g.set(12, 11, "i")


def _face_open(g, view):
    """Boca aberta (a mordida)."""
    if view == "front":
        g.row(13, 7, 8, "M"); g.row(14, 7, 8, "M")
    else:
        g.set(13, 13, "M"); g.set(13, 14, "M"); g.set(12, 14, "M")


def _face_kiss(g, view):
    """Beijo: olhos fechados, bochecha corada e lábios para a frente."""
    _clear_eyes(g, view)
    if view == "front":
        g.row(11, 3, 5, "L"); g.row(11, 10, 12, "L")
        g.row(12, 3, 4, "B2"); g.row(12, 11, 12, "B2")
        g.set(7, 14, "M"); g.set(8, 14, "M")
        return
    g.row(11, 11, 12, "L"); g.set(10, 10, "L")          # olho fechado, cílio para baixo
    g.row(12, 10, 11, "B2")                             # bochecha corada
    g.set(14, 14, "M")                                  # biquinho


def _face_love(g, view):
    """Depois do beijo: sorrindo com os olhinhos fechados e as bochechas coradas."""
    _face_happy(g, view)
    if view == "front":
        g.row(12, 3, 4, "B2"); g.row(12, 11, 12, "B2")
    else:
        g.row(12, 10, 11, "B2")


def _face_shut(g, view):
    """Olhos fechados, tranquila (golinho, dormindo)."""
    _clear_eyes(g, view)
    if view == "front":
        g.row(11, 4, 5, "L"); g.row(11, 10, 11, "L")
        g.set(3, 10, "L"); g.set(12, 10, "L")
    else:
        g.row(11, 11, 12, "L")


_FACES = {"happy": _face_happy, "read": _face_read, "open": _face_open, "kiss": _face_kiss, "shut": _face_shut,
          "love": _face_love}

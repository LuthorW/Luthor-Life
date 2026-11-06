"""Animações do dia a dia: o que a Letícia faz com as mãos e a vida em volta dela.

  regar      regador inclinando e a água caindo no canteiro (horta do terraço)
  bancada    mãos na bancada, faíscas e cliques ao trabalhar num projeto
  pesca      vara nas mãos, arremesso com a boia voando, ponta da vara envergando na mordida, carretilha
             girando no minigame e o peixe erguido acima da cabeça quando pesca (como no Stardew)
  dormir     deita na cama, puxa o cobertor (respira devagar, "zzz") e só então o dia acaba
  colo       sentada no sofá/poltrona de casa, o bichinho sobe no colo e dorme ali
  aceno      amigos (2+ corações) acenam quando a Letícia passa perto, uma vez por período
  gaivotas   na areia da praia (fogem voando quando ela chega perto) e passando por cima do mar
  gatinho    um gato de rua laranja que passeia pelo Parque Central; dá para fazer carinho (E)
  modo foto  P esconde a interface; Enter tira a foto (saves/fotos), 1 acena, 2 sorri, 3 coração, P/Esc sai
  bebidas    Cerveja Artesanal e Caipirinha (Noonan's) e Taça de Vinho (Trattoria), com ícones próprios;
             NPCs comem e bebem sentados à mesa (entities.NPC._tick_snack) e as cenas usam "segurar"/"beber"/"brinde"

Ganchos no Game: update_fx (sempre), update_world (jogando, sem janelas), handle_play (teclas), world_items
(desenho com profundidade), draw_player_extra (vara de pesca, item erguido), draw_photo (no lugar do HUD).
"""
import math
import os
import random
import time

import pygame

from . import art, audio, poses, entities
from .art import new, R, P, shade
from .config import TILE, SCALE, SCREEN_W, SCREEN_H, SAVE_DIR, C_PINK, C_MUTED, C_GREEN, C_TEXT, C_LILAC
from .data import ITEMS, SHOPS, _food
from .entities import FOOT, draw_shadow, draw_held

# ---------------------------------------------------------------------------
# Bebidas novas (e os ícones)
# ---------------------------------------------------------------------------
ITEMS.update({
    "cerveja": _food("Cerveja Artesanal", 12, 14, "beer", (232, 168, 48), "+12 de energia. A da casa do Noonan's."),
    "caipirinha": _food("Caipirinha", 14, 22, "caipi", (150, 214, 90),
                        "+14 de energia. Receita da Dona Graça, ensinada ao Marco."),
    "taca_vinho": _food("Taça de Vinho", 16, 26, "wineglass", (150, 30, 60), "+16 de energia. Tinto da casa."),
})
for _shop, _new in (("bar", ["cerveja", "caipirinha"]), ("trattoria", ["taca_vinho"])):
    for _k in _new:
        if _k not in SHOPS[_shop]["stock"]:
            SHOPS[_shop]["stock"].append(_k)

_orig_icon = art._icon


def _icon_drinks(kind, color):
    c = color
    s = new(16, 16)
    glass, glass_d = (226, 238, 246), (176, 196, 210)
    if kind == "beer":                                   # caneca com espuma
        R(s, glass_d, 3, 4, 9, 11)
        R(s, c, 4, 6, 7, 8)
        R(s, shade(c, 1.2), 5, 7, 1, 6)
        R(s, (252, 250, 240), 3, 2, 9, 3)
        P(s, (252, 250, 240), 4, 5); P(s, (252, 250, 240), 9, 5)
        R(s, glass_d, 12, 6, 2, 1); R(s, glass_d, 13, 6, 1, 6); R(s, glass_d, 12, 11, 2, 1)
        R(s, shade(glass_d, 0.8), 3, 14, 9, 1)
    elif kind == "caipi":                                # copo baixo com gelo e limão
        R(s, glass_d, 3, 6, 10, 9)
        R(s, (238, 246, 230), 4, 7, 8, 7)
        R(s, c, 4, 10, 8, 4)
        R(s, (250, 250, 255), 5, 8, 2, 2); R(s, (250, 250, 255), 8, 9, 2, 2)
        pygame.draw.circle(s, (120, 200, 70), (12, 6), 3)
        pygame.draw.circle(s, (210, 244, 150), (12, 6), 1)
        R(s, (240, 240, 240), 9, 2, 1, 7)
    elif kind == "wineglass":                            # taça de vinho
        pygame.draw.ellipse(s, glass_d, (3, 1, 10, 9))
        pygame.draw.ellipse(s, glass, (4, 2, 8, 7))
        R(s, c, 4, 5, 8, 3)
        R(s, shade(c, 1.3), 5, 5, 2, 1)
        R(s, glass_d, 7, 9, 2, 4); R(s, glass_d, 4, 13, 8, 2)
    elif kind == "regador":                              # regador de metal
        R(s, c, 3, 6, 8, 7)
        R(s, shade(c, 1.2), 3, 6, 8, 1)
        pygame.draw.line(s, c, (10, 9), (14, 4), 2)
        R(s, shade(c, 0.7), 13, 3, 3, 2)
        pygame.draw.arc(s, shade(c, 0.75), (2, 2, 8, 8), 0.3, 2.8, 1)
    else:
        return _orig_icon(kind, color)
    return s


art._icon = _icon_drinks


# ---------------------------------------------------------------------------
# Sons novos
# ---------------------------------------------------------------------------
def _sfx():
    from .audio import add_note, midi, RATE
    out = {}

    def mk(d):
        return [0.0] * int(d * RATE)
    b = mk(0.35)                                         # tim-tim dos copos
    add_note(b, 0, 0.04, midi(100), "sine", 0.22, 0.001, 0.25)
    add_note(b, 0.005, 0.04, midi(107), "sine", 0.12, 0.001, 0.2)
    out["clink"] = b
    b = mk(0.22)                                         # clique da câmera
    add_note(b, 0, 0.02, 3000, "noise", 0.2, 0.001, 0.02)
    add_note(b, 0.07, 0.03, 1800, "noise", 0.16, 0.001, 0.05)
    out["shutter"] = b
    b = mk(0.5)                                          # água do regador
    add_note(b, 0, 0.4, 2400, "noise", 0.06, 0.08, 0.1)
    out["water"] = b
    b = mk(0.12)                                         # teclinha da bancada
    add_note(b, 0, 0.02, midi(88), "square", 0.06, 0.001, 0.03, 0.25)
    add_note(b, 0.05, 0.02, midi(91), "square", 0.05, 0.001, 0.03, 0.25)
    out["work"] = b
    b = mk(0.3)                                          # arremesso da vara
    add_note(b, 0, 0.2, 900, "noise", 0.08, 0.05, 0.08)
    add_note(b, 0, 0.22, midi(80), "sine", 0.06, 0.01, 0.06, slide=-0.5)
    out["cast"] = b
    b = mk(0.5)                                          # ronronar
    for k in range(5):
        add_note(b, k * 0.09, 0.06, 70, "tri", 0.18, 0.01, 0.03)
    out["purr"] = b
    return out


audio.EXTRA_SFX.append(_sfx)


# ---------------------------------------------------------------------------
# Ações da Letícia (bloqueiam o andar enquanto duram)
# ---------------------------------------------------------------------------
ACT_DUR = {"regar": 1.25, "bancada": 1.3, "pegou": 1.5, "dormir": 2.1}
CAN_COLOR = (90, 160, 176)


def start_act(g, kind, **kw):
    if g.player.seat and kind != "dormir":
        return
    act = dict(kind=kind, t=0.0, drops=[], sparks=[], **kw)
    tile = kw.get("tile")
    if tile and kind in ("regar", "bancada"):
        tx, ty = g.player.tile
        dx, dy = tile[0] - tx, tile[1] - ty
        if dx or dy:
            g.player.dir = ("right" if dx > 0 else "left") if abs(dx) > abs(dy) else ("down" if dy > 0 else "up")
    if kind == "regar":
        audio.sfx("water")
    elif kind == "pegou":
        g.player.dir = "down"
    g.act = act
    g.player.pose = _act_pose(g, act)


def _act_pose(g, act):
    t, k = act["t"], act["kind"]
    if k == "regar":
        return dict(arms="hold", face=None, blink=False, bob=0, src="act")
    if k == "bancada":
        return dict(arms="work", face="read" if g.player.dir == "down" else None, blink=False,
                    bob=int(t * 7) % 2, src="act")
    if k == "pegou":
        return dict(arms="up", face="happy", blink=False, bob=0, src="act")
    return None


def _update_act(g, dt):
    act = getattr(g, "act", None)
    if not act:
        return
    act["t"] += dt
    k = act["kind"]
    if k == "regar":
        if 0.35 < act["t"] < 1.05 and random.random() < dt * 30:
            x, y = _spout(g, act)
            act["drops"].append([x, y, random.uniform(-12, 12), random.uniform(10, 40), 0.0])
    elif k == "bancada":
        if int(act["t"] * 4) != int((act["t"] - dt) * 4):
            audio.sfx("work")
            tx, ty = act["tile"]
            for _ in range(3):
                act["sparks"].append([(tx + random.uniform(0.2, 0.8)) * TILE, (ty + random.uniform(0.1, 0.6)) * TILE,
                                      random.uniform(-20, 20), random.uniform(-60, -30), 0.5])
    elif k == "dormir":
        g.player.hidden = True
    for d in act["drops"]:
        d[3] += 420 * dt
        d[0] += d[2] * dt
        d[1] += d[3] * dt
        d[4] += dt
    act["drops"] = [d for d in act["drops"] if d[4] < 0.32]
    for sp in act["sparks"]:
        sp[0] += sp[2] * dt
        sp[1] += sp[3] * dt
        sp[4] -= dt
    act["sparks"] = [sp for sp in act["sparks"] if sp[4] > 0]
    if act["t"] >= ACT_DUR[k]:
        g.act = None
        if g.player.pose and g.player.pose.get("src") == "act":
            g.player.pose = None
        if k == "dormir":
            g.player.hidden = False
            g.end_day(False)
        return
    g.player.pose = _act_pose(g, act) or g.player.pose


def _hand(g, where="hold"):
    pl = g.player
    if not pl.img_top:
        return pl.x, pl.y - 20 * SCALE
    ax, ay = poses.anchor(pl.dir, where, pl.look)
    return pl.img_top[0] + ax * SCALE, pl.img_top[1] + ay * SCALE


CAN_SPOUT = (5.5, -2.5)          # bico do regador em relação ao centro do desenho (px de arte)


def _can_angle(act):
    t = act["t"]
    if t < 1.05:
        return min(42.0, max(0.0, (t - 0.15) / 0.3 * 42.0))
    return max(0.0, 42.0 * (1.25 - t) / 0.2)


def _spout(g, act):
    """Bico do regador (de onde sai a água), girando junto com o regador."""
    x, y = _can_pos(g, act)
    side = -1 if g.player.dir == "left" else 1
    a = math.radians(_can_angle(act))
    vx, vy = CAN_SPOUT
    rx, ry = vx * math.cos(a) - vy * math.sin(a), vx * math.sin(a) + vy * math.cos(a)
    return x + side * rx * SCALE, y + ry * SCALE


def _can_pos(g, act):
    """Centro do regador: na mão, um pouco para a frente."""
    pl = g.player
    if pl.dir == "up":                                   # de costas: o regador aparece ao lado, na mão direita
        return pl.x + 8 * SCALE, pl.y - 17 * SCALE
    x, y = _hand(g)
    side = {"left": -1, "right": 1}.get(pl.dir, 1)
    return x + side * 3 * SCALE, y - 1 * SCALE


def _can_sprite():
    """Regador de metal (12x9 px de arte): alça em arco, corpo e o bico comprido."""
    def make():
        s = new(13, 10)
        c, d, l = CAN_COLOR, shade(CAN_COLOR, 0.62), shade(CAN_COLOR, 1.3)
        for (x, y) in ((3, 2), (4, 1), (5, 0), (6, 0), (7, 1), (8, 2)):     # alça
            P(s, d, x, y)
        R(s, d, 1, 3, 9, 7)
        R(s, c, 2, 4, 7, 5)
        R(s, l, 2, 4, 7, 1)
        R(s, l, 3, 5, 1, 3)
        for (x, y) in ((9, 6), (10, 5), (11, 4)):                         # bico
            P(s, d, x, y)
            P(s, c, x, y + 1) if y + 1 < 8 else None
        R(s, d, 11, 3, 2, 2)
        return art.up(s)
    return art.cached(("regador_spr",), make)


def _draw_act(g, surf, cam):
    act = getattr(g, "act", None)
    if not act:
        return
    k = act["kind"]
    if k == "regar":
        x, y = _can_pos(g, act)
        ang = _can_angle(act)
        img = _can_sprite()
        flip = g.player.dir == "left"
        if flip:
            img = pygame.transform.flip(img, True, False)
        img = pygame.transform.rotate(img, ang if flip else -ang)
        surf.blit(img, (int(x - cam[0] - img.get_width() / 2), int(y - cam[1] - img.get_height() / 2)))
        for d in act["drops"]:
            pygame.draw.rect(surf, (150, 200, 255), (int(d[0] - cam[0]), int(d[1] - cam[1]), SCALE, SCALE * 2))
    if k == "pegou" and g.player.img_top:               # o peixe flutuando acima da cabeça, entre as mãos
        x, y = _hand(g, "up")                            # y = base do peixe (o ícone tem 3 px vazios embaixo)
        ic = art.item_icon(act["item"], 2)
        rise = int((1 - min(1.0, act["t"] / 0.15)) * 5 * SCALE)        # sobe junto com os braços
        surf.blit(ic, (int(x - cam[0] - ic.get_width() / 2), int(y - cam[1] - ic.get_height() * 13 // 16 + rise)))
    for sp in act["sparks"]:
        c = (255, 236, 150) if sp[4] > 0.25 else (184, 120, 255)
        x, y = int(sp[0] - cam[0]), int(sp[1] - cam[1])
        pygame.draw.line(surf, c, (x - 2, y), (x + 2, y))
        pygame.draw.line(surf, c, (x, y - 2), (x, y + 2))
    if k == "pegou" and g.player.img_top:               # brilho em volta do peixe erguido
        x, y = _hand(g, "up")
        y -= 5 * SCALE                                   # centro do peixe
        r = int(10 + 4 * math.sin(act["t"] * 10))
        for i in range(6):
            a = act["t"] * 2 + i * math.tau / 6
            pygame.draw.circle(surf, (255, 240, 170), (int(x - cam[0] + math.cos(a) * r * SCALE / 1.4),
                                                       int(y - cam[1] + math.sin(a) * r * SCALE / 1.4)), 2)


def go_to_bed(g, bed):
    """Deita na cama, cobre-se e dorme; o resumo da noite vem depois."""
    if g.player.seat:
        g.player.seat = None
    g.player.pose = None
    start_act(g, "dormir", bed=bed)


class Sleeper:
    """A Letícia deitada: a cabeça no travesseiro e o cobertor da própria cama por cima."""

    def __init__(self, g, bed):
        self.g, self.bed = g, bed

    def draw(self, surf, cam):
        g, o = self.g, self.bed
        spr = g.object_image(o)
        sw, sh = spr.get_size()
        bx = o.x * TILE + (o.w * TILE - sw) // 2 - cam[0]
        by = o.base_y - sh - cam[1]
        pl = g.player
        img = poses.frame(pl.look, "down", None, None, "shut", False, 0, pl.look_key)
        t = g.act["t"] if getattr(g, "act", None) else 0.0
        breath = 1 if math.sin(t * 2.4) > 0.3 else 0
        head = img.subsurface((0, 0, img.get_width(), 18 * SCALE))
        hx = bx + sw // 2 - img.get_width() // 2
        surf.blit(head, (hx, by + 4 * SCALE))
        top = 20 * SCALE                                  # do lençol para baixo, o cobertor da cama por cima
        blanket = spr.subsurface((0, top, sw, sh - top))
        surf.blit(blanket, (bx, by + top))
        col = spr.get_at((sw // 2, min(sh - 1, 23 * SCALE)))[:3]
        hi, lo = shade(col, 1.15), shade(col, 0.82)
        cx = bx + sw // 2
        body = pygame.Rect(0, 0, 18 * SCALE, (7 - breath) * SCALE)       # o corpo embaixo do cobertor
        body.midtop = (cx, by + (21 + breath) * SCALE)
        pygame.draw.ellipse(surf, lo, body.move(0, SCALE))
        pygame.draw.ellipse(surf, col, body)
        pygame.draw.arc(surf, hi, body.inflate(-2 * SCALE, 0), 0.5, 2.65, SCALE)
        pygame.draw.rect(surf, (246, 242, 250), (bx + 3 * SCALE, by + top - SCALE, sw - 6 * SCALE, 2 * SCALE))
        pygame.draw.rect(surf, (214, 208, 226), (bx + 3 * SCALE, by + top + SCALE, sw - 6 * SCALE, SCALE))
        if t > 0.5:
            from .cutscenes import draw_emote
            draw_emote(surf, int(cx + 6 * SCALE), int(by + 2 * SCALE), "zzz", min(1.0, (t - 0.5) / 0.3))


# ---------------------------------------------------------------------------
# Vara de pesca
# ---------------------------------------------------------------------------
ROD, ROD_HI, LINE = (92, 60, 40), (150, 108, 70), (236, 236, 244)


def _rod_tip(g, hand, target, bend=0.0, back=0.0):
    """Ponta da vara: para a frente (na direção da água) e erguida; back > 0 = ainda lá atrás (arremesso)."""
    hx, hy = hand
    dx, dy = target[0] - hx, target[1] - hy
    d = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / d, dy / d
    L = 15 * SCALE
    side = 0.25 * L if abs(ux) < 0.5 else 0.0             # de frente/costas: a vara fica do lado da mão direita
    fx, fy = hx + ux * L * 0.78 + side, hy + uy * L * 0.78 - L * 0.5
    bx, by = hx - ux * L * 0.3 + side, hy - uy * L * 0.3 - L * 0.95
    x, y = fx + (bx - fx) * back, fy + (by - fy) * back
    return x + ux * bend * 2 * SCALE, y + bend * 4 * SCALE


def draw_rod(g, surf, cam):
    f, reel = g.fishing, getattr(g, "reel", None)
    if not f and not reel:
        return
    tile = (f or reel)["tile"]
    hand = _hand(g)
    if g.player.dir == "up":
        hand = (g.player.x, g.player.y - 14 * SCALE)
    target = ((tile[0] + 0.5) * TILE, (tile[1] + 0.5) * TILE)
    cast = f.get("cast", 9.0) if f else 9.0
    back = max(0.0, 1 - cast / 0.25) if cast < 0.25 else 0.0
    bend = 0.0
    if f and f["phase"] == "bite":
        bend = 0.8 + math.sin(time.monotonic() * 30) * 0.3
    if reel:
        bend = 1.2 + math.sin(time.monotonic() * 14) * 0.2
    tx, ty = _rod_tip(g, hand, target, bend, back)
    h = (int(hand[0] - cam[0]), int(hand[1] - cam[1]))
    tip = (int(tx - cam[0]), int(ty - cam[1]))
    pygame.draw.line(surf, ROD, h, tip, SCALE + 1)
    pygame.draw.line(surf, ROD_HI, h, (int((h[0] + tip[0]) / 2), int((h[1] + tip[1]) / 2)), 1)
    reel_a = time.monotonic() * (14 if reel else 0)       # carretilha (gira no minigame)
    pygame.draw.circle(surf, (70, 70, 84), h, 2 * SCALE)
    pygame.draw.line(surf, (200, 200, 210), h, (int(h[0] + math.cos(reel_a) * 2 * SCALE),
                                                int(h[1] + math.sin(reel_a) * 2 * SCALE)), 1)
    bx, by = target[0] - cam[0], target[1] - cam[1] + math.sin(g.t * 4) * 3
    if f and f["phase"] == "bite":
        by += 6
    if cast < 0.45:                                       # a boia voa da ponta da vara até a água
        k = max(0.0, (cast - 0.1) / 0.35)
        bx = tip[0] + (bx - tip[0]) * k
        by = tip[1] + (by - tip[1]) * k - math.sin(k * math.pi) * 22 * SCALE
    pts = []
    for i in range(9):                                    # linha com uma barriguinha
        k = i / 8
        sag = math.sin(k * math.pi) * (10 if not reel else 2) * (0.4 if cast < 0.45 else 1)
        pts.append((tip[0] + (bx - tip[0]) * k, tip[1] + (by - tip[1]) * k + sag))
    pygame.draw.lines(surf, LINE, False, pts, 1)
    if not reel:
        pygame.draw.circle(surf, (240, 60, 60), (int(bx), int(by)), 5)
        pygame.draw.circle(surf, (250, 250, 250), (int(bx), int(by) - 3), 3)
        if 0.45 <= cast < 0.9:                            # respingo quando a boia cai
            r = int((cast - 0.45) / 0.45 * 14) + 4
            pygame.draw.ellipse(surf, (220, 240, 255), (int(bx) - r, int(by) - r // 3, 2 * r, 2 * r // 3), 1)


def _update_fishing_pose(g, dt):
    pl = g.player
    f, reel = g.fishing, getattr(g, "reel", None)
    if f:
        f["cast"] = f.get("cast", 0.0) + dt
        if f["cast"] - dt <= 0.0:
            audio.sfx("cast")
    if f or reel:
        if not (pl.pose and pl.pose.get("src") not in (None, "fish")):
            crank = int(time.monotonic() * 12) % 2 if reel else 0
            pl.pose = dict(arms="hold", face=None, blink=False, bob=crank, src="fish")
    elif pl.pose and pl.pose.get("src") == "fish":
        pl.pose = None


def fish_done(g, fish, res):
    """Fim do minigame: tira a carretilha; se pescou, ergue o peixe acima da cabeça."""
    g.reel = None
    if g.player.pose and g.player.pose.get("src") == "fish":
        g.player.pose = None
    if res == "win" and fish in ITEMS:
        start_act(g, "pegou", item=fish)


# ---------------------------------------------------------------------------
# Bichinho no colo
# ---------------------------------------------------------------------------
LAP_SEATS = ("sofa", "sofa_grey", "armchair", "poltrona_roxa")
LAP_ANCHOR = {"front": (8.0, 25.0), "side": (9.5, 23.5)}


def _update_lap(g, dt):
    pet, pl = getattr(g, "pet", None), g.player
    lap = getattr(g, "lap", None)
    if lap:
        lap["t"] += dt
        if not pl.seat or not pet or pet.map != g.map_name:
            _leave_lap(g)
            return
        if random.random() < dt * 0.12:
            pet.emote, pet.emote_t = random.choice(["coracao", "zzz"]), 1.8
            if pet.emote == "coracao":
                audio.sfx("purr")
        return
    if not pet or not pl.seat or pet.map != g.map_name or getattr(pet, "sleeping", False):
        g.lap_wait = 0.0
        return
    o = g.current_map.object_at(*pl.tile) if hasattr(g.current_map, "object_at") else None
    if pl.dir == "up" or not o or o.kind not in LAP_SEATS:
        g.lap_wait = 0.0
        return
    g.lap_wait = getattr(g, "lap_wait", 0.0) + dt
    if g.lap_wait > 2.2 and math.hypot(pet.x - pl.x, pet.y - pl.y) < 6 * TILE:
        g.lap = dict(t=0.0)
        pet.lap = True
        pet.path = []
        pet.sleeping = False
        pet.x, pet.y = pl.x, pl.y + 1
        audio.sfx("purr")


def _leave_lap(g):
    pet = getattr(g, "pet", None)
    g.lap = None
    g.lap_wait = 0.0
    if pet:
        pet.lap = False
        tx, ty = g.player.tile
        m = g.world[pet.map]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)):
            if not m.is_solid(tx + dx, ty + dy) and (tx + dx, ty + dy) not in m.doors:
                pet.place(tx + dx, ty + dy)
                break
        pet.wait = 2.0


from . import activities as _act

_pet_update, _pet_draw = _act.Pet.update, _act.Pet.draw


def _pet_update_lap(self, dt, g):
    if getattr(self, "lap", False):                  # no colo: só o tempo das animações e dos emojis
        self.anim += dt
        if self.emote_t > 0:
            self.emote_t -= dt
            if self.emote_t <= 0:
                self.emote = None
        return
    _pet_update(self, dt, g)


def _pet_draw_lap(self, surf, cam):
    if not getattr(self, "lap", False):              # no colo quem desenha é o LapPet
        _pet_draw(self, surf, cam)


_act.Pet.update = _pet_update_lap
_act.Pet.draw = _pet_draw_lap


class LapPet:
    def __init__(self, g):
        self.g = g

    def draw(self, surf, cam):
        g = self.g
        pet, pl = g.pet, g.player
        if not pl.img_top:
            return
        from .activities import pet_frames, _coat_name
        fr = pet_frames(pet.kind, pet.coat, _coat_name(pet.kind, pet.coat))
        img = fr[("sleep", 0)]
        view = poses.VIEW[pl.dir]
        ax, ay = LAP_ANCHOR.get(view, LAP_ANCHOR["front"])
        if pl.dir == "left":
            ax = 16 - ax
        x = pl.img_top[0] + (ax + poses.PAD) * SCALE - cam[0]
        y = pl.img_top[1] + ay * SCALE - cam[1]
        breath = SCALE // 2 if math.sin(g.lap["t"] * 2.2) > 0 else 0
        surf.blit(img, (int(x - img.get_width() / 2), int(y - img.get_height() + 3 * SCALE - breath)))
        if pet.emote:
            from .cutscenes import draw_emote
            draw_emote(surf, int(x), int(y - img.get_height()), pet.emote, 1 - max(0, pet.emote_t - 1.4))


# ---------------------------------------------------------------------------
# Aceno dos amigos
# ---------------------------------------------------------------------------
def _update_waves(g, dt):
    g.wave_cd = max(0.0, getattr(g, "wave_cd", 0.0) - dt)
    if g.wave_cd > 0 or not g.player.moving:
        return
    waved = g.__dict__.setdefault("waved", set())
    px, py = g.player.x, g.player.y
    for npc in g.npcs.values():
        if npc.map != g.map_name or npc.wave_t > 0 or npc.pose or npc.seat_lift is not None or npc.moving:
            continue
        if g.hearts(npc.key) < 2 and npc.key not in (g.dating, g.partner):
            continue
        key = (npc.key, g.day, g.period)
        if key in waved:
            continue
        d = math.hypot(px - (npc.fx + 0.5) * TILE, py - npc.base_y) / TILE
        if 1.8 <= d <= 4.5:
            waved.add(key)
            npc.face_toward(px, py)
            npc.paused = max(npc.paused, 1.6)
            if entities.UMBRELLA["on"] and npc.map == "city":     # a mão está no guarda-chuva: sorri
                npc.emote, npc.emote_t = "feliz", 1.6
            else:
                npc.wave_t = 1.4
            g.wave_cd = 2.5
            return


# ---------------------------------------------------------------------------
# Gaivotas na praia
# ---------------------------------------------------------------------------
def _gull(frame, flying=False):
    def make():
        white, grey, dark, beak = (246, 246, 250), (170, 176, 190), (60, 60, 70), (240, 190, 60)
        if flying:
            s = new(14, 7)
            up_ = frame % 2 == 0
            R(s, white, 5, 3, 5, 2)
            if up_:
                R(s, grey, 1, 1, 4, 2); R(s, grey, 10, 1, 4, 2)
                P(s, dark, 0, 1); P(s, dark, 13, 1)
            else:
                R(s, grey, 1, 4, 4, 2); R(s, grey, 10, 4, 4, 2)
                P(s, dark, 0, 5); P(s, dark, 13, 5)
            P(s, beak, 10, 3)
            return art.up(s)
        s = new(10, 9)
        peck = frame == 1
        R(s, white, 2, 3, 6, 4)
        R(s, grey, 2, 3, 5, 2)
        P(s, dark, 1, 4); P(s, dark, 1, 3)               # pontinha das asas
        hy = 3 if peck else 1
        R(s, white, 7, hy, 2, 2)
        P(s, dark, 8, hy)
        P(s, beak, 9, hy + 1)
        P(s, (220, 150, 80), 4, 7); P(s, (220, 150, 80), 6, 7)
        P(s, (220, 150, 80), 4, 8); P(s, (220, 150, 80), 6, 8)
        return art.up(s)
    return art.cached(("gaivota", frame, flying), make)


class Gulls:
    """Gaivotas na areia (fogem voando quando a Letícia chega perto) e algumas planando sobre o mar."""

    def __init__(self):
        self.birds, self.flyers = [], []
        self.t, self.spawn_t, self.fly_t = 0.0, 1.0, 4.0

    def reset(self):
        self.birds.clear()
        self.flyers.clear()

    def update(self, dt, g):
        self.t += dt
        if g.map_name != "city" or getattr(g, "storm", False):
            self.reset()
            return
        m = g.current_map
        cam = g.camera(m)
        night = g.darkness(g.minutes) > 0.3
        self.spawn_t -= dt
        if not night and self.spawn_t <= 0 and len(self.birds) < 7:
            self.spawn_t = random.uniform(5, 11)
            for _ in range(10):
                tx = int((cam[0] + random.randrange(0, SCREEN_W)) // TILE)
                ty = int((cam[1] + random.randrange(0, SCREEN_H)) // TILE)
                if m.tile_at(tx, ty) != "sand" or m.is_solid(tx, ty):
                    continue
                if math.hypot(g.player.x - (tx + 0.5) * TILE, g.player.y - (ty + 0.5) * TILE) < 5 * TILE:
                    continue
                for _ in range(random.randrange(1, 4)):
                    self.birds.append(dict(x=(tx + random.uniform(0.1, 0.9)) * TILE,
                                           y=(ty + random.uniform(0.3, 0.9)) * TILE, dir=random.choice((-1, 1)),
                                           peck=random.uniform(0, 3), hop=random.uniform(0.5, 3), fly=None))
                break
        self.fly_t -= dt
        if not night and self.fly_t <= 0:                   # uma gaivota planando sobre o mar
            self.fly_t = random.uniform(6, 14)
            d = random.choice((-1, 1))
            sea_y = 63 * TILE
            self.flyers.append(dict(x=cam[0] + (-40 if d > 0 else SCREEN_W + 40),
                                    y=random.uniform(max(cam[1] + 40, sea_y - 6 * TILE), cam[1] + SCREEN_H - 60),
                                    d=d, ph=random.uniform(0, 6)))
        px, py = g.player.x, g.player.y
        keep = []
        for b in self.birds:
            if b["fly"] is None:
                if night or math.hypot(px - b["x"], py - b["y"]) < 2.4 * TILE:
                    away = 1 if b["x"] > px else -1
                    b["fly"] = [away * random.uniform(70, 110), -random.uniform(70, 120)]
                    b["dir"] = away
                else:
                    b["hop"] -= dt
                    if b["hop"] <= 0:
                        b["hop"] = random.uniform(1.0, 4.0)
                        b["dir"] = random.choice((-1, 1))
                        nx = b["x"] + b["dir"] * random.uniform(3, 8) * SCALE
                        if m.tile_at(int(nx // TILE), int(b["y"] // TILE)) == "sand":
                            b["x"] = nx
            else:
                b["x"] += b["fly"][0] * dt * SCALE
                b["y"] += b["fly"][1] * dt * SCALE
                b["fly"][1] -= 15 * dt
            if -200 < b["x"] - cam[0] < SCREEN_W + 200 and -300 < b["y"] - cam[1] < SCREEN_H + 200:
                keep.append(b)
        self.birds = keep
        for f in self.flyers:
            f["x"] += f["d"] * 42 * SCALE * dt
            f["y"] += math.sin(self.t * 1.3 + f["ph"]) * 6 * dt
        self.flyers = [f for f in self.flyers if -80 < f["x"] - cam[0] < SCREEN_W + 80]

    def draw(self, surf, cam, flying):
        for b in self.birds:
            if (b["fly"] is not None) != flying:
                continue
            if flying:
                img = _gull(int(self.t * 9) % 2, True)
            else:
                img = _gull(1 if (self.t + b["peck"]) % 2.8 < 0.35 else 0)
            if b["dir"] < 0:
                img = pygame.transform.flip(img, True, False)
            x, y = int(b["x"] - cam[0] - img.get_width() / 2), int(b["y"] - cam[1] - img.get_height())
            if not flying:
                draw_shadow(surf, int(b["x"] - cam[0]), int(b["y"] - cam[1]) + SCALE, 7 * SCALE)
            surf.blit(img, (x, y))
        if flying:
            for f in self.flyers:
                img = _gull(int(self.t * 3 + f["ph"]) % 2, True)
                if f["d"] < 0:
                    img = pygame.transform.flip(img, True, False)
                sx, sy = int(f["x"] - cam[0]), int(f["y"] - cam[1])
                sh = pygame.Surface((10 * SCALE, 3 * SCALE), pygame.SRCALPHA)
                pygame.draw.ellipse(sh, (0, 0, 40, 40), sh.get_rect())
                surf.blit(sh, (sx - 5 * SCALE, sy + 30 * SCALE))
                surf.blit(img, (sx - img.get_width() // 2, sy))


# ---------------------------------------------------------------------------
# Gatinho de rua (Parque Central)
# ---------------------------------------------------------------------------
STRAY_COAT = (240, 160, 80)
STRAY_AREA = (2, 24, 38, 47)             # dentro do Parque Central (world.CITY_AREAS["park"])


class StrayCat:
    SPEED = 1.3

    def __init__(self):
        self.x = self.y = None
        self.path = []
        self.state, self.t = "sit", 2.0
        self.dir = "right"
        self.anim = 0.0
        self.emote, self.emote_t = None, 0.0
        self.petted_day = None

    @property
    def base_y(self):
        return self.y

    @property
    def tile(self):
        return int(self.x // TILE), int((self.y - 1) // TILE)

    def _free(self, m, x, y):
        return not m.is_solid(x, y) and m.tile_at(x, y) not in ("road", "water", "deep") and (x, y) not in m.doors

    def _place(self, m):
        x0, y0, x1, y1 = STRAY_AREA
        for _ in range(60):
            x, y = random.randint(x0, x1), random.randint(y0, y1)
            if self._free(m, x, y):
                self.x, self.y = (x + 0.5) * TILE, (y + 1) * TILE - 4
                return True
        return False

    def visible(self, g):
        return g.weather != "chuva" and 7 * 60 <= g.minutes < 22 * 60

    def update(self, dt, g):
        if g.map_name != "city":
            return
        m = g.world["city"]
        if self.x is None and not self._place(m):
            return
        self.anim += dt
        if self.emote_t > 0:
            self.emote_t -= dt
            if self.emote_t <= 0:
                self.emote = None
        pd = math.hypot(g.player.x - self.x, g.player.y - self.y)
        if pd < 1.3 * TILE and g.player.moving and self.state != "walk" and self.petted_day != g.day:
            self._go(m, flee=(g.player.x, g.player.y))        # assustado: sai de perto
        if self.path:
            tx, ty = self.path[0]
            cx, cy = (tx + 0.5) * TILE, (ty + 1) * TILE - 4
            dx, dy = cx - self.x, cy - self.y
            dist = math.hypot(dx, dy)
            sp = self.SPEED * TILE * dt * (2.2 if self.state == "flee" else 1)
            self.dir = ("right" if dx > 0 else "left") if abs(dx) >= abs(dy) else ("down" if dy > 0 else "up")
            if dist <= sp:
                self.x, self.y = cx, cy
                self.path.pop(0)
                if not self.path:
                    self.state, self.t = random.choice([("sit", random.uniform(4, 9)),
                                                        ("sleep", random.uniform(8, 16)),
                                                        ("sit", random.uniform(3, 6))])
            else:
                self.x += dx / dist * sp
                self.y += dy / dist * sp
            return
        self.t -= dt
        if self.t <= 0:
            self._go(m)

    def _go(self, m, flee=None):
        here = self.tile
        x0, y0, x1, y1 = STRAY_AREA
        for _ in range(12):
            if flee:
                ax = 1 if self.x >= flee[0] else -1
                ay = 1 if self.y >= flee[1] else -1
                goal = (here[0] + ax * random.randint(2, 4), here[1] + ay * random.randint(1, 3))
            else:
                goal = (here[0] + random.randint(-5, 5), here[1] + random.randint(-4, 4))
            if not (x0 <= goal[0] <= x1 and y0 <= goal[1] <= y1) or not self._free(m, *goal):
                continue
            path = m.find_path(here, goal, 600)
            if path and len(path) <= 12 and all(m.tile_at(*p) != "road" for p in path):
                self.path = path
                self.state = "flee" if flee else "walk"
                return
        self.state, self.t = "sit", random.uniform(2, 5)

    def draw(self, surf, cam):
        from .activities import pet_frames
        fr = pet_frames("gato", STRAY_COAT, "")
        if self.path:
            img = fr[(self.dir, int(self.anim * (12 if self.state == "flee" else 8)) % 4)]
        elif self.state == "sleep":
            img = fr[("sleep", 0)]
        else:
            img = fr[("blink", 0)] if self.anim % 4.2 < 0.15 else fr[("down", 0)]
        x = int(self.x - img.get_width() // 2 - cam[0])
        y = int(self.y - img.get_height() - cam[1])
        draw_shadow(surf, int(self.x - cam[0]), int(self.y - cam[1]) + SCALE, 12 * SCALE)
        surf.blit(img, (x, y))
        if self.emote:
            from .cutscenes import draw_emote
            draw_emote(surf, int(self.x - cam[0]), y - 2, self.emote, 1 - max(0, self.emote_t - 1.4))


def pet_stray(g, cat):
    cat.path = []
    cat.state, cat.t = "sit", 5.0
    cat.dir = "down"
    cat.emote, cat.emote_t = "coracao", 2.2
    audio.sfx("purr")
    if cat.petted_day != g.day:
        cat.petted_day = g.day
        g.stats["gatinho"] = g.stats.get("gatinho", 0) + 1
        n = g.stats["gatinho"]
        msg = ("O gatinho laranja ronrona e se esfrega na sua perna." if n < 5 else
               "O gatinho laranja já te reconhece: vem correndo e deita de barriga para cima.")
        g.toasts.push(msg, C_PINK)
    else:
        g.toasts.push("O gatinho fecha os olhos e ronrona mais alto.", C_MUTED)


def resolve(g, fx, fy):
    cat = getattr(g, "stray", None)
    if cat and g.map_name == "city" and cat.x is not None and cat.visible(g) and cat.tile == (fx, fy):
        return ("gato", cat)
    return None


# ---------------------------------------------------------------------------
# Modo foto
# ---------------------------------------------------------------------------
PHOTO_DIR = os.path.join(SAVE_DIR, "fotos")


def handle_play(g, ev):
    """Teclas novas. True = a tecla já foi usada aqui."""
    if ev.type != pygame.KEYDOWN:
        busy = getattr(g, "act", None) or getattr(g, "photo_mode", False)
        return bool(busy) and ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL)
    if getattr(g, "act", None):
        return True                                        # regando, pescou, deitando: espera acabar
    if getattr(g, "photo_mode", False):
        if ev.key in (pygame.K_p, pygame.K_ESCAPE):
            g.photo_mode = False
            audio.sfx("cancel")
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_F12):
            g.photo_shot = True
        elif ev.key == pygame.K_1:
            g.player.pose = dict(arms="wave", face="happy", blink=False, bob=0, src="photo", t=1.6)
        elif ev.key == pygame.K_2:
            g.player.pose = dict(arms=None, face="happy", blink=False, bob=0, src="photo", t=1.6)
        elif ev.key == pygame.K_3:
            g.player_emote = dict(kind="coracao", t=0.0)
        return True
    if ev.key == pygame.K_p and not g.fishing:
        g.photo_mode = True
        g.photo_flash = 0.0
        audio.sfx("open")
        return True
    return False


def draw_photo(g, surf):
    """No lugar do HUD: só o mundo. Enter salva a imagem (sem a dica da tela)."""
    if getattr(g, "photo_shot", False):
        g.photo_shot = False
        try:
            os.makedirs(PHOTO_DIR, exist_ok=True)
            name = time.strftime("foto_%Y%m%d_%H%M%S.png")
            path = os.path.join(PHOTO_DIR, name)
            k = 1
            while os.path.exists(path):
                k += 1
                path = os.path.join(PHOTO_DIR, name.replace(".png", f"_{k}.png"))
            pygame.image.save(surf, path)
            g.photo_msg = (f"Foto salva em saves/fotos/{os.path.basename(path)}", 2.5)
        except (OSError, pygame.error):
            g.photo_msg = ("Não deu para salvar a foto.", 2.5)
        g.photo_flash = 0.35
        audio.sfx("shutter")
    fl = getattr(g, "photo_flash", 0.0)
    if fl > 0:
        veil = pygame.Surface((SCREEN_W, SCREEN_H))
        veil.fill((255, 255, 255))
        veil.set_alpha(int(255 * min(1.0, fl / 0.35)))
        surf.blit(veil, (0, 0))
    from . import ui
    msg = getattr(g, "photo_msg", None)
    txt = msg[0] if msg else "MODO FOTO   Enter: fotografar   1: acenar   2: sorrir   3: coração   P: sair"
    w = ui.font(16, True).size(txt)[0] + 30
    r = pygame.Rect(SCREEN_W // 2 - w // 2, SCREEN_H - 46, w, 30)
    ui.panel(surf, r, alpha=150, radius=14)
    ui.text(surf, txt, (r.centerx, r.y + 5), 16, C_GREEN if msg else C_TEXT, bold=True, center=True)
    for c in ((14, 14), (SCREEN_W - 14, 14), (14, SCREEN_H - 14), (SCREEN_W - 14, SCREEN_H - 14)):  # cantos
        sx = 1 if c[0] < SCREEN_W // 2 else -1
        sy = 1 if c[1] < SCREEN_H // 2 else -1
        pygame.draw.line(surf, (250, 250, 250), c, (c[0] + sx * 34, c[1]), 3)
        pygame.draw.line(surf, (250, 250, 250), c, (c[0], c[1] + sy * 34), 3)


# ---------------------------------------------------------------------------
# Ganchos
# ---------------------------------------------------------------------------
def init(g):
    g.act = None
    g.reel = None
    g.lap = None
    g.lap_wait = 0.0
    g.photo_mode = False
    g.photo_shot = False
    g.photo_flash = 0.0
    g.photo_msg = None
    g.waved = set()
    g.wave_cd = 0.0
    g.gulls = Gulls()
    g.stray = StrayCat()


def update_fx(g, dt):
    """Todo quadro (também com janelas abertas: a carretilha gira durante o minigame)."""
    from . import seasons
    entities.UMBRELLA["on"] = g.weather == "chuva" and seasons.CURRENT.get("season") != "winter"
    g.player.umbrella = entities.UMBRELLA["on"] and g.map_name == "city" and g.scene == "play"
    _update_act(g, dt)
    _update_fishing_pose(g, dt)
    if getattr(g, "photo_flash", 0.0) > 0:
        g.photo_flash = max(0.0, g.photo_flash - dt)
    msg = getattr(g, "photo_msg", None)
    if msg:
        g.photo_msg = (msg[0], msg[1] - dt) if msg[1] - dt > 0 else None
    pose = g.player.pose
    if pose and pose.get("src") == "photo":
        pose["t"] -= dt
        if pose["t"] <= 0:
            g.player.pose = None


def update_world(g, dt):
    """Jogando, sem janelas abertas."""
    g.gulls.update(dt, g)
    if g.stray.visible(g):
        g.stray.update(dt, g)
    _update_lap(g, dt)
    _update_waves(g, dt)


def world_items(g, m):
    out = []
    act = getattr(g, "act", None)
    if act and act["kind"] == "dormir" and m.name == g.map_name:
        out.append((act["bed"].base_y + 1, 1, "anim", Sleeper(g, act["bed"])))
    if getattr(g, "lap", None) and g.pet and g.pet.map == m.name and m.name == g.map_name and g.player.seat:
        out.append(((g.player.seat["sort"] if g.player.seat else g.player.y) + 0.5, 1, "anim", LapPet(g)))
    cat = getattr(g, "stray", None)
    if m.name == "city" and cat and cat.x is not None and cat.visible(g):
        out.append((cat.base_y, 1, "anim", cat))
    return out


def draw_ground(g, surf, m, cam):
    if m.name == "city":
        g.gulls.draw(surf, cam, False)


def draw_sky(g, surf, m, cam):
    if m.name == "city":
        g.gulls.draw(surf, cam, True)


def draw_player_extra(g, surf, cam):
    draw_rod(g, surf, cam)
    _draw_act(g, surf, cam)

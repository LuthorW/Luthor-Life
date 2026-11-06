"""Minigames novos: sinuca e dardos no Noonan's, e xadrez com o Brainy (opção na conversa, 1x por dia).

Sinuca: encaçapar as 6 bolas em até 8 tacadas (mira com setas ou mouse, segura E para a força).
Dardos: 9 dardos num alvo de verdade (duplo, triplo, mosca); a mão balança mais com pouca energia.
Xadrez: regras completas (roque, en passant, promoção). O Brainy pensa com uma busca curta e erra de propósito
um pouquinho; quanto mais vezes a Letícia ganha, mais a sério ele joga.
"""
import math
import random
import threading

import pygame

from . import art, ui, audio, world
from .art import new, R, P
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_RED, C_LILAC, C_ACCENT

PLAY_COST = 5


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.jogos = dict(chess_day=-1, chess_wins=0, chess_games=0, pool_best=0, darts_best=0)


def save_state(g):
    return {"jogos": g.jogos}


def load_state(g, d):
    init_state(g)
    g.jogos.update({k: v for k, v in (d.get("jogos") or {}).items() if k in g.jogos})


# ---------------------------------------------------------------------------
# Arte: alvo de dardos num armário de madeira (fica entre os fliperamas do bar)
# ---------------------------------------------------------------------------
def _dardos():
    s = new(16, 30)
    R(s, (92, 58, 36), 1, 2, 14, 27)
    R(s, (120, 78, 48), 2, 3, 12, 25)
    R(s, (70, 42, 26), 1, 28, 14, 2)
    cx, cy = 8, 11
    pygame.draw.circle(s, (30, 28, 32), (cx, cy), 6)
    pygame.draw.circle(s, (236, 224, 196), (cx, cy), 5)
    for a in range(0, 360, 36):
        x = cx + math.sin(math.radians(a)) * 4.5
        y = cy - math.cos(math.radians(a)) * 4.5
        P(s, (30, 28, 32), int(round(x)), int(round(y)))
    pygame.draw.circle(s, (200, 50, 50), (cx, cy), 3, 1)
    pygame.draw.circle(s, (60, 150, 80), (cx, cy), 2)
    P(s, (220, 50, 50), cx, cy)
    # dardos espetados e a lousa do placar
    R(s, (230, 190, 60), 4, 8, 1, 2); R(s, (90, 170, 250), 11, 13, 1, 2)
    R(s, (40, 52, 46), 3, 19, 10, 6)
    for i in range(3):
        R(s, (220, 220, 210), 4, 20 + i * 2, 3 + i * 2, 1)
    return s


art.OBJECT_BUILDERS.update({"dardos": _dardos})
world.OBJECT_DEFS.update({"dardos": (1, 1, True, "obj")})


def add_props(maps):
    """Coloca o alvo de dardos no bar (entre os dois fliperamas)."""
    m = maps.get("bar")
    if m is None or any(o.kind == "dardos" for o in m.objects):
        return
    o = m.add("dardos", 15, 2)
    m.solid[2][15] = True
    return o


# ---------------------------------------------------------------------------
# Ganchos do Game
# ---------------------------------------------------------------------------
def cost(g):
    """Preço de uma partida (de graça com a conta da casa do Marco)."""
    return 0 if "marco_tab" in g.flags else PLAY_COST


def _price(g):
    return "conta da casa" if cost(g) == 0 else f"${cost(g)}"


def object_label(g, o):
    if g.map_name != "bar":
        return None
    if o.kind == "pool":
        return f"Jogar sinuca ({_price(g)})"
    if o.kind == "dardos":
        return f"Jogar dardos ({_price(g)})"
    return None


def use_object(g, o):
    if g.map_name != "bar" or o.kind not in ("pool", "dardos"):
        return False
    if g.money < cost(g):
        g.say(f"Você precisa de ${cost(g)} para jogar.")
        return True
    if g.energy < 8:
        g.say("Você está cansada demais para jogar agora.")
        return True
    if o.kind == "pool":
        _start_pool(g)
    else:
        _start_darts(g)
    return True


def _start_pool(g):
    def go(i):
        if i != 0:
            return
        g.money -= cost(g)

        def done(potted):
            prize = potted * 12 + (60 if potted >= len(Pool.COLORS) else 0)
            g.money += prize
            g.energy = max(0, g.energy - 4)
            if potted > g.jogos["pool_best"]:
                g.jogos["pool_best"] = potted
                if potted >= 3:
                    g.toasts.push(f"Novo recorde na sinuca: {potted} bolas!", C_GOLD)
            g.toasts.push(f"Sinuca: {potted} bola(s) encaçapada(s) (+${prize})", C_GREEN)
        g.push(Pool(done, g.jogos["pool_best"]))
    g.push(ui.Choice(f"Desafio da sinuca ({_price(g)}): encaçape as 6 bolas em até 8 tacadas. "
                     "Cada bola vale $12, e as seis ganham +$60.", ["Jogar!", "Agora não"], go))


def _start_darts(g):
    def go(i):
        if i != 0:
            return
        g.money -= cost(g)
        steady = max(0.0, min(1.0, g.energy / max(1, g.max_energy)))

        def done(total):
            prize = total // 4
            g.money += prize
            g.energy = max(0, g.energy - 3)
            if total > g.jogos["darts_best"]:
                g.jogos["darts_best"] = total
                if total >= 60:
                    g.toasts.push(f"Novo recorde nos dardos: {total} pontos!", C_GOLD)
            g.toasts.push(f"Dardos: {total} pontos (+${prize})", C_GREEN)
        g.push(Darts(done, g.jogos["darts_best"], steady))
    g.push(ui.Choice(f"Dardos ({_price(g)}): 9 dardos, cada 4 pontos valem $1. "
                     "Com pouca energia a mão treme mais.", ["Jogar!", "Agora não"], go))


def talk_options(g, npc, opts, acts):
    if npc.key != "brainy" or g.hearts("brainy") < 2 or g.jogos["chess_day"] == g.abs_day():
        return
    opts.append("Jogar xadrez")
    acts.append(lambda: start_chess(g, npc))


def start_chess(g, npc):
    first = g.jogos["chess_games"] == 0
    lines = (["Xadrez? Eu sempre ando com um tabuleiro de bolso. Sério, olha. Ele dobra!",
              "Você joga com as brancas, então começa. E pode pensar o quanto quiser: eu também penso muito."]
             if first else [random.choice(["Revanche? Eu estudei umas aberturas novas ontem à noite. Por diversão!",
                                           "Brancas pra você, como sempre. Prometo não explicar cada lance.",
                                           "Eu montei o tabuleiro antes de você terminar a pergunta."])])

    def begin():
        g.jogos["chess_day"] = g.abs_day()
        g.jogos["chess_games"] += 1

        def done(result):
            g.energy = max(0, g.energy - 5)
            if result == "win":
                g.jogos["chess_wins"] += 1
                g.add_friendship("brainy", 80)
                txt = ["Xeque-mate. Em mim. Isso foi... muito bem jogado. Posso anotar a partida?"]
                if g.jogos["chess_wins"] == 1:
                    g.flags.add("xadrez_brainy")
                    txt.append("Primeira vitória contra mim! Vou contar pra Sam. Ela vai fingir que não liga.")
                mood = "happy"
            elif result == "draw":
                g.add_friendship("brainy", 50)
                txt = ["Empate! Matematicamente, é o resultado mais elegante. Gostei."]
                mood = "smile"
            else:
                g.add_friendship("brainy", 30)
                txt = ["Boa partida! Você quase me pegou no meio do jogo. Quase mesmo." if result == "lose"
                       else "Tudo bem desistir. Às vezes o melhor lance é ir tomar um café."]
                mood = "smile"
            g.push(ui.Dialog(npc.name, txt, g.portrait_for(npc, mood), subtitle=npc.data["role"]))
        noise = max(6, 40 - 8 * g.jogos["chess_wins"])
        g.push(ChessGame(g, npc, done, noise))
    g.push(ui.Dialog(npc.name, lines, g.portrait_for(npc, "happy"), on_close=begin, subtitle=npc.data["role"]))


# ---------------------------------------------------------------------------
# Sinuca
# ---------------------------------------------------------------------------
class Pool(ui.Modal):
    TW, TH = 600, 300
    BR = 10
    POCKET_R = 19
    SHOTS = 8
    COLORS = [(240, 200, 60), (60, 110, 220), (220, 60, 60), (140, 70, 180), (240, 140, 50), (60, 170, 90)]
    START = (150.0, 150.0)

    def __init__(self, on_done, best=0):
        self.on_done = on_done
        self.best = best
        self.balls = [dict(x=self.START[0], y=self.START[1], vx=0.0, vy=0.0, c=(250, 250, 244), cue=True, live=True)]
        d = self.BR * 2 + 0.6
        k = 0
        for row in range(3):
            for i in range(row + 1):
                self.balls.append(dict(x=410 + row * d * 0.87, y=150 + (i - row / 2) * d, vx=0.0, vy=0.0,
                                       c=self.COLORS[k], cue=False, live=True))
                k += 1
        self.angle = 0.0
        self.power = 0.0
        self.pdir = 1
        self.charging = False
        self.shots = self.SHOTS
        self.potted = 0
        self.moving = False
        self.cue_fell = False
        self.rot = 0
        self.msg, self.msg_t = "Mire na bola amarela e segure E para dar a força.", 4.0
        self.over = False
        self.reported = False
        self.origin = (0, 0)
        self.snd_t = 0.0
        T, H = self.TW, self.TH
        self.pockets = [(2, 2), (T / 2, -3), (T - 2, 2), (2, H - 2), (T / 2, H + 3), (T - 2, H - 2)]

    @property
    def cue(self):
        return self.balls[0]

    # --- entrada ---
    def handle(self, ev):
        if self.over:
            if ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM + ui.CANCEL:
                self.close()
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                self.rot = -1
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.rot = 1
            elif ev.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN) and not self.moving:
                self.charging, self.power, self.pdir = True, 0.0, 1
            elif ev.key == pygame.K_ESCAPE:
                self.over = True
        elif ev.type == pygame.KEYUP:
            if ev.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                self.rot = 0
            elif ev.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN) and self.charging:
                self.shoot()
        elif ev.type == pygame.MOUSEMOTION and not self.moving and not self.charging:
            cx, cy = self.origin[0] + self.cue["x"], self.origin[1] + self.cue["y"]
            mx, my = ev.pos
            if abs(mx - cx) + abs(my - cy) > 4:
                self.angle = math.atan2(my - cy, mx - cx)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not self.moving:
            self.charging, self.power, self.pdir = True, 0.0, 1
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.charging:
            self.shoot()

    def close(self):
        self.done = True
        if not self.reported:
            self.reported = True
            self.on_done(self.potted)

    def shoot(self):
        self.charging = False
        if self.moving or self.power < 0.04:
            return
        sp = 140 + self.power * 980
        self.cue["vx"], self.cue["vy"] = math.cos(self.angle) * sp, math.sin(self.angle) * sp
        self.moving = True
        self.shots -= 1
        self.cue_fell = False
        audio.sfx("blip")

    # --- física ---
    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)
        self.snd_t = max(0.0, self.snd_t - dt)
        if self.over:
            return
        if not self.moving:
            if self.rot:
                fine = pygame.key.get_mods() & pygame.KMOD_SHIFT
                self.angle += self.rot * dt * (0.35 if fine else 1.5)
            if self.charging:
                self.power += self.pdir * dt * 0.9
                if self.power >= 1:
                    self.power, self.pdir = 1.0, -1
                elif self.power <= 0:
                    self.power, self.pdir = 0.0, 1
            return
        n = 6
        h = dt / n
        for _ in range(n):
            self._step(h)
        if all(b["vx"] == 0 and b["vy"] == 0 for b in self.balls if b["live"]):
            self._end_shot()

    def _step(self, h):
        BR, T, H = self.BR, self.TW, self.TH
        live = [b for b in self.balls if b["live"]]
        for b in live:
            sp = math.hypot(b["vx"], b["vy"])
            if sp <= 0:
                continue
            nsp = max(0.0, sp - 130 * h) * (1 - 0.35 * h)
            if nsp < 5:
                b["vx"] = b["vy"] = 0.0
            else:
                b["vx"] *= nsp / sp
                b["vy"] *= nsp / sp
            b["x"] += b["vx"] * h
            b["y"] += b["vy"] * h
            for (px, py) in self.pockets:
                if (b["x"] - px) ** 2 + (b["y"] - py) ** 2 < self.POCKET_R ** 2:
                    self._pot(b)
                    break
            if not b["live"]:
                continue
            hit = False
            if b["x"] < BR:
                b["x"], b["vx"], hit = BR, abs(b["vx"]) * 0.8, True
            elif b["x"] > T - BR:
                b["x"], b["vx"], hit = T - BR, -abs(b["vx"]) * 0.8, True
            if b["y"] < BR:
                b["y"], b["vy"], hit = BR, abs(b["vy"]) * 0.8, True
            elif b["y"] > H - BR:
                b["y"], b["vy"], hit = H - BR, -abs(b["vy"]) * 0.8, True
            if hit and self.snd_t <= 0 and math.hypot(b["vx"], b["vy"]) > 120:
                audio.sfx("move")
                self.snd_t = 0.06
        live = [b for b in self.balls if b["live"]]
        for i in range(len(live)):
            a = live[i]
            for j in range(i + 1, len(live)):
                b = live[j]
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                d2 = dx * dx + dy * dy
                if d2 >= (2 * BR) ** 2 or d2 == 0:
                    continue
                d = math.sqrt(d2)
                nx, ny = dx / d, dy / d
                over = 2 * BR - d
                a["x"] -= nx * over / 2; a["y"] -= ny * over / 2
                b["x"] += nx * over / 2; b["y"] += ny * over / 2
                rel = (a["vx"] - b["vx"]) * nx + (a["vy"] - b["vy"]) * ny
                if rel <= 0:
                    continue
                imp = rel * 0.97
                a["vx"] -= imp * nx; a["vy"] -= imp * ny
                b["vx"] += imp * nx; b["vy"] += imp * ny
                if self.snd_t <= 0 and rel > 60:
                    audio.sfx("blip")
                    self.snd_t = 0.05

    def _pot(self, b):
        b["live"] = False
        b["vx"] = b["vy"] = 0.0
        if b["cue"]:
            self.cue_fell = True
            self.msg, self.msg_t = "A bola branca caiu! Ela volta para o lugar.", 2.5
        else:
            self.potted += 1
            audio.sfx("confirm")
            self.msg, self.msg_t = random.choice(["Na caçapa!", "Bonita!", "Essa foi limpa!", "Mais uma!"]), 1.6

    def _end_shot(self):
        self.moving = False
        if self.cue_fell:
            c = self.cue
            x, y = self.START
            while any(o["live"] and not o["cue"] and math.hypot(o["x"] - x, o["y"] - y) < 2 * self.BR + 2
                      for o in self.balls):
                x += 4
            c.update(x=x, y=y, vx=0.0, vy=0.0, live=True)
        if self.potted >= len(self.COLORS) or self.shots <= 0:
            self.over = True
            audio.sfx("confirm")

    # --- mira ---
    def _aim_hit(self):
        """Primeira bola (ou tabela) no caminho da branca: ponto de contato e a bola atingida."""
        c = self.cue
        dx, dy = math.cos(self.angle), math.sin(self.angle)
        best, hit = 9999.0, None
        for b in self.balls:
            if b is c or not b["live"]:
                continue
            ox, oy = b["x"] - c["x"], b["y"] - c["y"]
            t = ox * dx + oy * dy
            if t <= 0:
                continue
            perp2 = ox * ox + oy * oy - t * t
            r2 = (2 * self.BR) ** 2
            if perp2 > r2:
                continue
            tt = t - math.sqrt(r2 - perp2)
            if tt < best:
                best, hit = tt, b
        BR = self.BR
        for t in ((BR - c["x"]) / dx if dx < 0 else (self.TW - BR - c["x"]) / dx if dx > 0 else 9999,
                  (BR - c["y"]) / dy if dy < 0 else (self.TH - BR - c["y"]) / dy if dy > 0 else 9999):
            if 0 < t < best:
                best, hit = t, None
        return c["x"] + dx * best, c["y"] + dy * best, hit

    # --- desenho ---
    def draw(self, surf):
        outer = pygame.Rect(0, 0, self.TW + 200, self.TH + 222)
        outer.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "SINUCA NO NOONAN'S", (outer.x + 26, outer.y + 16), 26, C_GOLD, bold=True)
        ui.text(surf, f"Tacadas: {self.shots}    Na caçapa: {self.potted}/{len(self.COLORS)}    "
                      f"Recorde: {max(self.best, self.potted)}", (outer.right - 26, outer.y + 22), 18, C_TEXT,
                right=True)
        ox, oy = outer.x + 100, outer.y + 82
        self.origin = (ox, oy)
        rail = pygame.Rect(ox - 26, oy - 26, self.TW + 52, self.TH + 52)
        pygame.draw.rect(surf, (96, 56, 34), rail, border_radius=18)
        pygame.draw.rect(surf, (128, 78, 46), rail.inflate(-8, -8), border_radius=14)
        felt = pygame.Rect(ox, oy, self.TW, self.TH)
        pygame.draw.rect(surf, (30, 112, 76), felt)
        pygame.draw.rect(surf, (24, 92, 62), felt, 3)
        for i in range(1, 4):                                     # marquinhas da tabela
            for x in (ox + self.TW * i / 4,):
                pygame.draw.circle(surf, (236, 220, 170), (int(x), oy - 14), 3)
                pygame.draw.circle(surf, (236, 220, 170), (int(x), oy + self.TH + 14), 3)
        pygame.draw.line(surf, (60, 140, 100), (ox + 150, oy + 4), (ox + 150, oy + self.TH - 4), 1)
        for (px, py) in self.pockets:
            pygame.draw.circle(surf, (16, 12, 14), (int(ox + px), int(oy + py)), self.POCKET_R)
            pygame.draw.circle(surf, (50, 34, 26), (int(ox + px), int(oy + py)), self.POCKET_R, 2)
        if not self.moving and not self.over and self.cue["live"]:
            hx, hy, hit = self._aim_hit()
            cx, cy = ox + self.cue["x"], oy + self.cue["y"]
            dist = math.hypot(hx - self.cue["x"], hy - self.cue["y"])
            steps = int(dist // 12)
            for i in range(1, steps):
                t = i * 12 / max(1, dist)
                pygame.draw.circle(surf, (230, 240, 230), (int(cx + (ox + hx - cx) * t), int(cy + (oy + hy - cy) * t)), 1)
            pygame.draw.circle(surf, (240, 250, 240), (int(ox + hx), int(oy + hy)), self.BR, 1)
            if hit is not None:
                nx, ny = hit["x"] - hx, hit["y"] - hy
                nl = math.hypot(nx, ny) or 1
                ex, ey = hit["x"] + nx / nl * 46, hit["y"] + ny / nl * 46
                pygame.draw.line(surf, (255, 230, 140), (ox + hit["x"], oy + hit["y"]), (ox + ex, oy + ey), 2)
        for b in self.balls:
            if not b["live"]:
                continue
            x, y = int(ox + b["x"]), int(oy + b["y"])
            pygame.draw.circle(surf, (14, 50, 34), (x + 2, y + 3), self.BR)
            pygame.draw.circle(surf, b["c"], (x, y), self.BR)
            if not b["cue"]:
                pygame.draw.circle(surf, (250, 250, 244), (x, y), 4)
            pygame.draw.circle(surf, (255, 255, 255), (x - 3, y - 4), 2)
        if not self.moving and not self.over and self.cue["live"]:   # taco
            cx, cy = ox + self.cue["x"], oy + self.cue["y"]
            back = 16 + self.power * 46
            dx, dy = math.cos(self.angle), math.sin(self.angle)
            a = (cx - dx * back, cy - dy * back)
            b = (cx - dx * (back + 230), cy - dy * (back + 230))
            pygame.draw.line(surf, (60, 36, 20), a, b, 7)
            pygame.draw.line(surf, (214, 176, 112), a, b, 5)
            pygame.draw.line(surf, (240, 236, 226), a, (a[0] - dx * 8, a[1] - dy * 8), 5)
            pygame.draw.line(surf, (90, 140, 220), a, (a[0] - dx * 3, a[1] - dy * 3), 5)
        # barra de força
        bar = pygame.Rect(ox, outer.bottom - 60, self.TW, 14)
        pygame.draw.rect(surf, (40, 30, 52), bar, border_radius=7)
        fill = bar.copy(); fill.w = int(bar.w * self.power)
        col = (90, 220, 120) if self.power < 0.6 else (250, 200, 70) if self.power < 0.85 else (240, 90, 80)
        if fill.w > 0:
            pygame.draw.rect(surf, col, fill, border_radius=7)
        if self.msg_t > 0 and not self.over:
            ui.text(surf, self.msg, (outer.centerx, oy + self.TH + 34), 20, C_GOLD, bold=True, center=True)
        ui.text(surf, "Setas ou mouse: mirar (Shift = devagar)   Segure E ou o clique: força   Esc: parar",
                (outer.centerx, outer.bottom - 34), 16, C_MUTED, center=True)
        if self.over:
            veil = pygame.Surface(outer.size, pygame.SRCALPHA)
            veil.fill((10, 6, 18, 170))
            surf.blit(veil, outer.topleft)
            prize = self.potted * 12 + (60 if self.potted >= len(self.COLORS) else 0)
            title = "MESA LIMPA!" if self.potted >= len(self.COLORS) else "FIM DE JOGO"
            ui.text(surf, title, (outer.centerx, outer.centery - 50), 40, C_GOLD, bold=True, center=True)
            ui.text(surf, f"{self.potted} bola(s)  =  $ {prize}", (outer.centerx, outer.centery + 2), 24, C_TEXT,
                    bold=True, center=True)
            ui.text(surf, "Aperte E para sair", (outer.centerx, outer.centery + 44), 18, C_MUTED, center=True)


# ---------------------------------------------------------------------------
# Dardos
# ---------------------------------------------------------------------------
class Darts(ui.Modal):
    R = 160
    SEG = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    THROWS = 9

    def __init__(self, on_done, best=0, steady=1.0):
        self.on_done = on_done
        self.best = best
        self.sway = 22 + 40 * (1 - steady)
        self.t = random.uniform(0, 20)
        self.aim = [0.0, 0.0]
        self.keys = set()
        self.darts = []
        self.fly = None
        self.total = 0
        self.over = False
        self.reported = False
        self.msg, self.msg_t = "", 0.0
        self.board = None

    def handle(self, ev):
        if self.over:
            if ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM + ui.CANCEL:
                self.close()
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                self.throw()
            elif ev.key == pygame.K_ESCAPE:
                self.over = True
            else:
                self.keys.add(ev.key)
        elif ev.type == pygame.KEYUP:
            self.keys.discard(ev.key)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.throw()

    def close(self):
        self.done = True
        if not self.reported:
            self.reported = True
            self.on_done(self.total)

    def cross(self):
        s = self.sway
        return (self.aim[0] + math.sin(self.t * 1.3) * s + math.sin(self.t * 6.1) * 2,
                self.aim[1] + math.sin(self.t * 1.9 + 1.0) * s * 0.8 + math.cos(self.t * 5.3) * 2)

    def throw(self):
        if self.fly or len(self.darts) >= self.THROWS:
            return
        x, y = self.cross()
        x += random.gauss(0, 3)
        y += random.gauss(0, 3)
        self.fly = dict(x=x, y=y, t=0.0)
        audio.sfx("move")

    def score_at(self, dx, dy):
        r = math.hypot(dx, dy) / self.R * 170
        if r <= 6.35:
            return 50, "Mosca! 50"
        if r <= 15.9:
            return 25, "Anel da mosca: 25"
        if r > 170:
            return 0, "Fora do alvo!"
        ang = math.degrees(math.atan2(dx, -dy)) % 360
        n = self.SEG[int(((ang + 9) % 360) // 18)]
        if 99 <= r <= 107:
            return 3 * n, f"Triplo {n}: {3 * n}"
        if 162 <= r <= 170:
            return 2 * n, f"Duplo {n}: {2 * n}"
        return n, str(n)

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)
        if self.over:
            return
        sp = 170 * dt
        k = self.keys
        if k & {pygame.K_LEFT, pygame.K_a}:
            self.aim[0] -= sp
        if k & {pygame.K_RIGHT, pygame.K_d}:
            self.aim[0] += sp
        if k & {pygame.K_UP, pygame.K_w}:
            self.aim[1] -= sp
        if k & {pygame.K_DOWN, pygame.K_s}:
            self.aim[1] += sp
        lim = self.R * 1.15
        self.aim = [max(-lim, min(lim, v)) for v in self.aim]
        if self.fly:
            self.fly["t"] += dt
            if self.fly["t"] >= 0.22:
                pts, lab = self.score_at(self.fly["x"], self.fly["y"])
                self.darts.append((self.fly["x"], self.fly["y"], pts))
                self.total += pts
                self.msg, self.msg_t = lab, 1.6
                audio.sfx("confirm" if pts >= 40 else "blip")
                self.fly = None
                if len(self.darts) >= self.THROWS:
                    self.over = True

    def _board(self):
        if self.board:
            return self.board
        Rr = self.R
        size = Rr * 2 + 70
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size / 2
        pygame.draw.circle(s, (24, 22, 26), (c, c), Rr + 32)
        k = Rr / 170

        def wedge(r0, r1, i, col):
            a0, a1 = math.radians(i * 18 - 9), math.radians(i * 18 + 9)
            pts = []
            for j in range(7):
                a = a0 + (a1 - a0) * j / 6
                pts.append((c + math.sin(a) * r1 * k, c - math.cos(a) * r1 * k))
            for j in range(6, -1, -1):
                a = a0 + (a1 - a0) * j / 6
                pts.append((c + math.sin(a) * r0 * k, c - math.cos(a) * r0 * k))
            pygame.draw.polygon(s, col, pts)

        for i in range(20):
            dark = i % 2 == 0
            single = (30, 28, 32) if dark else (236, 222, 190)
            ring = (204, 52, 52) if dark else (52, 150, 84)
            wedge(15.9, 99, i, single)
            wedge(99, 107, i, ring)
            wedge(107, 162, i, single)
            wedge(162, 170, i, ring)
        pygame.draw.circle(s, (52, 150, 84), (c, c), 15.9 * k)
        pygame.draw.circle(s, (204, 52, 52), (c, c), 6.35 * k)
        for r in (15.9, 99, 107, 162, 170):
            pygame.draw.circle(s, (170, 170, 176), (c, c), r * k, 1)
        for i, n in enumerate(self.SEG):
            a = math.radians(i * 18)
            ui.text(s, str(n), (c + math.sin(a) * (Rr + 18), c - math.cos(a) * (Rr + 18) - 10), 18,
                    (240, 236, 226), bold=True, center=True)
        self.board = s
        return s

    def draw(self, surf):
        outer = pygame.Rect(0, 0, 820, 560)
        outer.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "DARDOS NO NOONAN'S", (outer.x + 26, outer.y + 16), 26, C_GOLD, bold=True)
        board = self._board()
        bx = outer.x + 40
        by = outer.y + 60
        surf.blit(board, (bx, by))
        c = (bx + board.get_width() // 2, by + board.get_height() // 2)
        for (x, y, _p) in self.darts:
            px, py = int(c[0] + x), int(c[1] + y)
            pygame.draw.line(surf, (40, 40, 44), (px, py), (px + 9, py + 12), 3)
            pygame.draw.polygon(surf, (90, 170, 250), [(px + 7, py + 10), (px + 15, py + 12), (px + 10, py + 18)])
            pygame.draw.circle(surf, (250, 250, 250), (px, py), 2)
        if self.fly:
            f = self.fly["t"] / 0.22
            px, py = c[0] + self.fly["x"], c[1] + self.fly["y"] + (1 - f) * 120
            sz = int(18 - 12 * f)
            pygame.draw.line(surf, (40, 40, 44), (px, py), (px + sz * 0.5, py + sz), 3)
        elif not self.over:
            x, y = self.cross()
            px, py = int(c[0] + x), int(c[1] + y)
            pygame.draw.circle(surf, (255, 255, 255), (px, py), 9, 2)
            pygame.draw.line(surf, (255, 255, 255), (px - 14, py), (px - 5, py), 2)
            pygame.draw.line(surf, (255, 255, 255), (px + 5, py), (px + 14, py), 2)
            pygame.draw.line(surf, (255, 255, 255), (px, py - 14), (px, py - 5), 2)
            pygame.draw.line(surf, (255, 255, 255), (px, py + 5), (px, py + 14), 2)
        # placar
        sx = outer.x + board.get_width() + 70
        ui.text(surf, "Placar", (sx, outer.y + 70), 24, C_LILAC, bold=True)
        for rnd in range(3):
            ds = self.darts[rnd * 3:rnd * 3 + 3]
            txt = "  ".join(str(p) for (_x, _y, p) in ds) or "-"
            ui.text(surf, f"Rodada {rnd + 1}:  {txt}", (sx, outer.y + 110 + rnd * 34), 20, C_TEXT)
        ui.text(surf, f"Total: {self.total}", (sx, outer.y + 220), 28, C_GOLD, bold=True)
        ui.text(surf, f"Recorde: {max(self.best, self.total)}", (sx, outer.y + 258), 18, C_MUTED)
        ui.text(surf, f"Dardos: {self.THROWS - len(self.darts)}", (sx, outer.y + 284), 18, C_MUTED)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (sx, outer.y + 330), 24, C_GREEN, bold=True)
        for i, ln in enumerate(["Setas: ajustar a mira", "E ou clique: arremessar", "Mosca = 50, anel = 25",
                                "Anel de fora: dobro", "Anel do meio: triplo"]):
            ui.text(surf, ln, (sx, outer.y + 390 + i * 24), 16, C_MUTED)
        if self.over:
            veil = pygame.Surface(outer.size, pygame.SRCALPHA)
            veil.fill((10, 6, 18, 170))
            surf.blit(veil, outer.topleft)
            ui.text(surf, "FIM DE JOGO", (outer.centerx, outer.centery - 50), 40, C_GOLD, bold=True, center=True)
            ui.text(surf, f"{self.total} pontos  =  $ {self.total // 4}", (outer.centerx, outer.centery + 2), 24,
                    C_TEXT, bold=True, center=True)
            ui.text(surf, "Aperte E para sair", (outer.centerx, outer.centery + 44), 18, C_MUTED, center=True)


# ---------------------------------------------------------------------------
# Xadrez: regras e a "cabeça" do Brainy
# ---------------------------------------------------------------------------
VAL = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 0}
N_OFF = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
K_OFF = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
B_DIR = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
R_DIR = [(-1, 0), (1, 0), (0, -1), (0, 1)]
CENTER = [0, 1, 2, 3, 3, 2, 1, 0]


def chess_start():
    rows = ["rnbqkbnr", "pppppppp", "........", "........", "........", "........", "PPPPPPPP", "RNBQKBNR"]
    return ([ch for row in rows for ch in row], True, "KQkq", None)


def attacked(b, sq, by_white):
    r, c = divmod(sq, 8)
    pr = r + 1 if by_white else r - 1
    pawn = "P" if by_white else "p"
    if 0 <= pr < 8:
        for dc in (-1, 1):
            if 0 <= c + dc < 8 and b[pr * 8 + c + dc] == pawn:
                return True
    kn, kg = ("N", "K") if by_white else ("n", "k")
    for dr, dc in N_OFF:
        rr, cc = r + dr, c + dc
        if 0 <= rr < 8 and 0 <= cc < 8 and b[rr * 8 + cc] == kn:
            return True
    for dr, dc in K_OFF:
        rr, cc = r + dr, c + dc
        if 0 <= rr < 8 and 0 <= cc < 8 and b[rr * 8 + cc] == kg:
            return True
    for dirs, ps in ((B_DIR, "BQ"), (R_DIR, "RQ")):
        if not by_white:
            ps = ps.lower()
        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                p = b[rr * 8 + cc]
                if p != ".":
                    if p in ps:
                        return True
                    break
                rr += dr
                cc += dc
    return False


def gen_moves(st, captures_only=False):
    b, w, castle, ep = st
    out = []
    for sq, p in enumerate(b):
        if p == "." or p.isupper() != w:
            continue
        r, c = divmod(sq, 8)
        t = p.upper()
        if t == "P":
            d, start, last = (-1, 6, 0) if w else (1, 1, 7)
            rr = r + d
            if not captures_only and 0 <= rr < 8 and b[rr * 8 + c] == ".":
                out.append((sq, rr * 8 + c, "Q" if rr == last else None))
                if r == start and b[(r + 2 * d) * 8 + c] == ".":
                    out.append((sq, (r + 2 * d) * 8 + c, None))
            for dc in (-1, 1):
                cc = c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    to = rr * 8 + cc
                    q = b[to]
                    if (q != "." and q.isupper() != w) or to == ep:
                        out.append((sq, to, "Q" if rr == last else None))
        elif t in "NK":
            for dr, dc in (N_OFF if t == "N" else K_OFF):
                rr, cc = r + dr, c + dc
                if 0 <= rr < 8 and 0 <= cc < 8:
                    q = b[rr * 8 + cc]
                    if (q == "." and not captures_only) or (q != "." and q.isupper() != w):
                        out.append((sq, rr * 8 + cc, None))
            if t == "K" and not captures_only:
                home, opp = (60, False) if w else (4, True)
                kside, qside = ("K", "Q") if w else ("k", "q")
                rook = "R" if w else "r"
                if sq == home and not attacked(b, home, opp):
                    if (kside in castle and b[home + 1] == b[home + 2] == "." and b[home + 3] == rook
                            and not attacked(b, home + 1, opp) and not attacked(b, home + 2, opp)):
                        out.append((home, home + 2, None))
                    if (qside in castle and b[home - 1] == b[home - 2] == b[home - 3] == "." and b[home - 4] == rook
                            and not attacked(b, home - 1, opp) and not attacked(b, home - 2, opp)):
                        out.append((home, home - 2, None))
        else:
            dirs = B_DIR if t == "B" else R_DIR if t == "R" else B_DIR + R_DIR
            for dr, dc in dirs:
                rr, cc = r + dr, c + dc
                while 0 <= rr < 8 and 0 <= cc < 8:
                    q = b[rr * 8 + cc]
                    if q == ".":
                        if not captures_only:
                            out.append((sq, rr * 8 + cc, None))
                    else:
                        if q.isupper() != w:
                            out.append((sq, rr * 8 + cc, None))
                        break
                    rr += dr
                    cc += dc
    return out


def make_move(st, mv):
    b, w, castle, ep = st
    frm, to, promo = mv
    b = b[:]
    p = b[frm]
    t = p.upper()
    nep = None
    if t == "P":
        if to == ep:
            b[to + (8 if w else -8)] = "."
        if abs(to - frm) == 16:
            nep = (frm + to) // 2
    if t == "K" and abs(to - frm) == 2:
        if to == frm + 2:
            b[frm + 1], b[frm + 3] = b[frm + 3], "."
        else:
            b[frm - 1], b[frm - 4] = b[frm - 4], "."
    b[to] = (promo if w else promo.lower()) if promo else p
    b[frm] = "."
    if castle:
        for s, flags in ((60, "KQ"), (4, "kq"), (63, "K"), (56, "Q"), (7, "k"), (0, "q")):
            if frm == s or to == s:
                castle = "".join(x for x in castle if x not in flags)
    return (b, not w, castle, nep)


def king_safe(st_after, white):
    b = st_after[0]
    k = b.index("K" if white else "k")
    return not attacked(b, k, not white)


def legal_moves(st):
    return [mv for mv in gen_moves(st) if king_safe(make_move(st, mv), st[1])]


def in_check(st):
    b, w = st[0], st[1]
    return attacked(b, b.index("K" if w else "k"), not w)


def evaluate(b):
    s = 0
    for sq, p in enumerate(b):
        if p == ".":
            continue
        r, c = divmod(sq, 8)
        t = p.upper()
        v = VAL[t]
        if t in "NB":
            v += (CENTER[r] + CENTER[c]) * 5
        elif t == "P":
            v += ((6 - r) if p.isupper() else (r - 1)) * 6 + (CENTER[c] * 4 if 2 <= r <= 5 else 0)
        elif t == "K":
            v += 12 if r in (0, 7) and c in (1, 2, 6) else 0
        s += v if p.isupper() else -v
    return s


def _order(st, moves):
    b = st[0]
    return sorted(moves, key=lambda m: -(VAL[b[m[1]].upper()] if b[m[1]] != "." else 0) - (800 if m[2] else 0))


def _quiesce(st, alpha, beta, depth):
    stand = evaluate(st[0]) * (1 if st[1] else -1)
    if depth == 0 or stand >= beta:
        return stand
    alpha = max(alpha, stand)
    for mv in _order(st, gen_moves(st, captures_only=True)):
        ns = make_move(st, mv)
        if not king_safe(ns, st[1]):
            continue
        sc = -_quiesce(ns, -beta, -alpha, depth - 1)
        if sc >= beta:
            return sc
        alpha = max(alpha, sc)
    return alpha


def _negamax(st, depth, alpha, beta):
    if depth == 0:
        return _quiesce(st, alpha, beta, 3)
    moves = legal_moves(st)
    if not moves:
        return -100000 - depth if in_check(st) else 0
    best = -10 ** 9
    for mv in _order(st, moves):
        sc = -_negamax(make_move(st, mv), depth - 1, -beta, -alpha)
        if sc > best:
            best = sc
        alpha = max(alpha, sc)
        if alpha >= beta:
            break
    return best


def brainy_move(st, noise=20, depth=2):
    """Melhor lance (com um pouco de 'distração' sorteada, para ele não ser imbatível)."""
    moves = legal_moves(st)
    if not moves:
        return None
    scored = []
    for mv in _order(st, moves):
        sc = -_negamax(make_move(st, mv), depth - 1, -10 ** 9, 10 ** 9)
        scored.append((sc + random.uniform(-noise, noise), mv))
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


# --- pecinhas em pixel art (12x14), contorno calculado sozinho ---
PIECE_ART = {
    "P": ["............", "............", "............", ".....##.....", "....####....", "....####....",
          ".....##.....", "....####....", ".....##.....", "....####....", "...######...", "..########..",
          "..########..", "............"],
    "N": ["............", "....##.#....", "...######...", "..########..", ".####.####..", ".###..####..",
          "......####..", ".....#####..", "....#####...", "....#####...", "...######...", "..########..",
          "..########..", "............"],
    "B": ["............", ".....##.....", "....####....", "...##.###...", "...#.####...", "...######...",
          "....####....", ".....##.....", "....####....", "....####....", "...######...", "..########..",
          "..########..", "............"],
    "R": ["............", "..##.##.##..", "..########..", "..########..", "...######...", "...######...",
          "...######...", "...######...", "...######...", "...######...", "..########..", "..########..",
          ".##########.", "............"],
    "Q": ["............", ".#..#..#..#.", ".##.##.##.##", ".##########.", "..########..", "...######...",
          "....####....", "....####....", "....####....", "...######...", "..########..", "..########..",
          ".##########.", "............"],
    "K": [".....##.....", "....####....", ".....##.....", "..##.##.##..", ".##########.", ".##########.",
          "..########..", "...######...", "....####....", "...######...", "..########..", "..########..",
          ".##########.", "............"],
}
_piece_cache = {}


def piece_img(p, size):
    key = (p, size)
    if key in _piece_cache:
        return _piece_cache[key]
    rows = PIECE_ART[p.upper()]
    white = p.isupper()
    fill, line, shine = (((250, 244, 230), (64, 42, 72), (255, 255, 255)) if white
                         else ((58, 38, 82), (14, 8, 22), (112, 84, 150)))
    s = new(14, 16)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                P(s, fill, x + 1, y + 1)
    for y, row in enumerate(rows):                        # contorno: vizinhos vazios de um pixel cheio
        for x, ch in enumerate(row):
            if ch != "#":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if not (0 <= yy < len(rows) and 0 <= xx < 12 and rows[yy][xx] == "#"):
                    P(s, line, xx + 1, yy + 1)
    for y, row in enumerate(rows):                        # brilho do lado esquerdo
        x = row.find("#")
        if x >= 0 and 2 <= y <= 11 and x + 1 < 12 and row[x + 1] == "#":
            P(s, shine, x + 2, y + 1)
    img = pygame.transform.scale(s, (size, int(size * 16 / 14)))
    _piece_cache[key] = img
    return img


QUIPS = {
    "start": ["Que vença a melhor estratégia. Ou a mais teimosa.", "Prometo não citar teoria de jogos. Muito."],
    "you_take": ["Ah. Eu não tinha visto isso.", "Boa! Anotado.", "Hmm. Essa doeu um pouquinho.",
                 "Você estava esperando esse lance, né?"],
    "he_takes": ["Desculpa! É o jogo.", "Essa peça estava sozinha demais.", "Obrigado pelo presente!",
                 "Cálculo simples. Mas fiquei feliz."],
    "check_you": ["Xeque! Calma, tem saída.", "Xeque. Respira.", "Xeque! Eu sempre quis dizer isso com estilo."],
    "check_him": ["Xeque em mim?! Interessante...", "Ok, ok, estou vendo.", "Ei! Isso foi rápido."],
    "think": ["Hmmm...", "Deixa eu pensar...", "Calculando...", "Uma ideia... não, duas ideias..."],
}


class ChessGame(ui.Modal):
    SQ = 56

    def __init__(self, g, npc, on_done, noise=24):
        self.g = g
        self.npc = npc
        self.on_done = on_done
        self.noise = noise
        self.st = chess_start()
        self.moves = legal_moves(self.st)
        self.cur = 52
        self.sel = None
        self.last = None
        self.result = None
        self.reported = False
        self.thread = None
        self.ai = None
        self.think_t = 0.0
        self.plies = 0
        self.quip, self.quip_t = random.choice(QUIPS["start"]), 4.0
        self.taken = {True: [], False: []}
        self.portrait = g.portrait_for(npc, "smile", 150)
        self.board_xy = (0, 0)
        self.confirm = False

    # --- entrada ---
    def handle(self, ev):
        if self.result:
            if ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM + ui.CANCEL:
                self.close()
            return
        if self.confirm:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_s, pygame.K_y, pygame.K_RETURN, pygame.K_e):
                    self.finish("resign")
                self.confirm = False
            return
        mine = self.st[1]
        if ev.type == pygame.KEYDOWN:
            r, c = divmod(self.cur, 8)
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                c = (c - 1) % 8
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                c = (c + 1) % 8
            elif ev.key in (pygame.K_UP, pygame.K_w):
                r = (r - 1) % 8
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                r = (r + 1) % 8
            elif ev.key in ui.CONFIRM and mine:
                self.pick(self.cur)
            elif ev.key == pygame.K_ESCAPE:
                if self.sel is not None:
                    self.sel = None
                else:
                    self.confirm = True
            self.cur = r * 8 + c
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and mine:
            bx, by = self.board_xy
            c, r = (ev.pos[0] - bx) // self.SQ, (ev.pos[1] - by) // self.SQ
            if 0 <= c < 8 and 0 <= r < 8:
                self.cur = r * 8 + c
                self.pick(self.cur)

    def targets(self, sq):
        return [m for m in self.moves if m[0] == sq]

    def pick(self, sq):
        b = self.st[0]
        if self.sel is not None:
            for m in self.targets(self.sel):
                if m[1] == sq:
                    self.play(m)
                    return
        if b[sq] != "." and b[sq].isupper() and self.targets(sq):
            self.sel = sq
            audio.sfx("move")
        else:
            self.sel = None

    def play(self, mv):
        b = self.st[0]
        white = self.st[1]
        cap = b[mv[1]]
        if cap == "." and b[mv[0]].upper() == "P" and mv[1] == self.st[3]:
            cap = "p" if white else "P"
        self.st = make_move(self.st, mv)
        self.last = mv
        self.sel = None
        self.plies += 1
        if cap != ".":
            self.taken[white].append(cap)
            self.say("you_take" if white else "he_takes", 0.5)
        audio.sfx("confirm" if cap != "." else "blip")
        self.moves = legal_moves(self.st)
        chk = in_check(self.st)
        if not self.moves:
            if chk:
                self.finish("win" if white else "lose")
            else:
                self.finish("draw")
            return
        if chk:
            self.say("check_him" if white else "check_you", 1.0)
        pieces = [p for p in self.st[0] if p != "."]
        if len(pieces) == 2 or self.plies >= 160:
            self.finish("draw")

    def say(self, kind, chance=1.0):
        if random.random() <= chance:
            self.quip, self.quip_t = random.choice(QUIPS[kind]), 3.5

    def finish(self, result):
        self.result = result
        audio.sfx("confirm")

    def close(self):
        self.done = True
        if not self.reported:
            self.reported = True
            self.on_done(self.result or "resign")

    # --- vez do Brainy ---
    def update(self, dt):
        self.quip_t = max(0.0, self.quip_t - dt)
        if self.result or self.st[1]:
            return
        self.think_t += dt
        if self.thread is None:
            st, noise = self.st, self.noise
            self.ai = None
            if random.random() < 0.35:
                self.say("think")

            def work():
                self.ai = brainy_move(st, noise) or "none"
            self.thread = threading.Thread(target=work, daemon=True)
            self.thread.start()
            self.think_t = 0.0
        elif self.ai is not None and self.think_t > 0.7:
            mv, self.ai, self.thread = self.ai, None, None
            if mv != "none":
                self.play(mv)

    # --- desenho ---
    def draw(self, surf):
        outer = pygame.Rect(0, 0, 850, 600)
        outer.center = (SCREEN_W // 2 - 40, SCREEN_H // 2)      # sem cobrir o relógio do HUD
        ui.panel(surf, outer, alpha=255)
        S = self.SQ
        bx, by = outer.x + 48, outer.y + 58
        self.board_xy = (bx, by)
        ui.text(surf, "XADREZ COM O BRAINY", (outer.x + 36, outer.y + 14), 24, C_GOLD, bold=True)
        frame = pygame.Rect(bx - 10, by - 10, S * 8 + 20, S * 8 + 20)
        pygame.draw.rect(surf, (64, 40, 90), frame, border_radius=8)
        b = self.st[0]
        targets = {m[1] for m in self.targets(self.sel)} if self.sel is not None else set()
        king_chk = None
        if in_check(self.st) and not self.result:
            king_chk = b.index("K" if self.st[1] else "k")
        for sq in range(64):
            r, c = divmod(sq, 8)
            rect = pygame.Rect(bx + c * S, by + r * S, S, S)
            light = (r + c) % 2 == 0
            col = (230, 218, 238) if light else (132, 98, 170)
            if self.last and sq in self.last[:2]:
                col = (240, 222, 140) if light else (196, 166, 90)
            if sq == king_chk:
                col = (236, 110, 110)
            pygame.draw.rect(surf, col, rect)
            if sq == self.sel:
                pygame.draw.rect(surf, (90, 220, 130), rect, 4)
            p = b[sq]
            if p != ".":
                img = piece_img(p, 46)
                surf.blit(img, (rect.centerx - img.get_width() // 2, rect.bottom - img.get_height() - 2))
            if sq in targets:
                if p != ".":
                    pygame.draw.rect(surf, (90, 220, 130), rect.inflate(-4, -4), 3, border_radius=6)
                else:
                    pygame.draw.circle(surf, (90, 200, 120), rect.center, 8)
            if sq == self.cur and not self.result and self.st[1]:
                pygame.draw.rect(surf, (255, 255, 255), rect, 3)
        for i in range(8):
            ui.text(surf, "abcdefgh"[i], (bx + i * S + S // 2, by + 8 * S + 10), 14, C_MUTED, center=True)
            ui.text(surf, str(8 - i), (bx - 22, by + i * S + S // 2 - 8), 14, C_MUTED)
        # lado direito: Brainy
        sx = bx + 8 * S + 40
        ui.blit_portrait(surf, self.portrait, (sx, by - 6))
        ph = self.portrait.get_height()
        ui.text(surf, self.npc.name, (sx, by + ph - 2), 24, C_TEXT, bold=True)
        turn = ("Sua vez (brancas)" if self.st[1] else "Brainy está pensando...") if not self.result else ""
        ui.text(surf, turn, (sx, by + ph + 26), 18, C_LILAC)
        if self.quip_t > 0:
            box = pygame.Rect(sx, by + ph + 56, outer.right - sx - 28, 84)
            pygame.draw.rect(surf, (52, 36, 74), box, border_radius=10)
            pygame.draw.rect(surf, (140, 100, 200), box, 2, border_radius=10)
            for i, ln in enumerate(ui.wrap(self.quip, 18, box.w - 24)[:3]):
                ui.text(surf, ln, (box.x + 12, box.y + 10 + i * 24), 18, C_TEXT)
        ty = by + ph + 152
        ui.text(surf, "Peças que você pegou:", (sx, ty), 16, C_MUTED)
        for i, p in enumerate(self.taken[True]):
            img = piece_img(p, 22)
            surf.blit(img, (sx + (i % 10) * 24, ty + 20 + (i // 10) * 26))
        ui.text(surf, "Peças que o Brainy pegou:", (sx, ty + 76), 16, C_MUTED)
        for i, p in enumerate(self.taken[False]):
            img = piece_img(p, 22)
            surf.blit(img, (sx + (i % 10) * 24, ty + 96 + (i // 10) * 26))
        ui.text(surf, "Setas: mover   E: escolher peça e casa   Esc: desistir", (outer.centerx, outer.bottom - 34),
                16, C_MUTED, center=True)
        if self.confirm:
            box = pygame.Rect(0, 0, 420, 120)
            box.center = outer.center
            ui.panel(surf, box)
            ui.text(surf, "Desistir da partida?", (box.centerx, box.y + 24), 24, C_TEXT, bold=True, center=True)
            ui.text(surf, "E: sim, desistir    Outra tecla: continuar", (box.centerx, box.y + 70), 18, C_MUTED,
                    center=True)
        if self.result:
            veil = pygame.Surface(outer.size, pygame.SRCALPHA)
            veil.fill((10, 6, 18, 150))
            surf.blit(veil, outer.topleft)
            title = {"win": "XEQUE-MATE! VOCÊ VENCEU", "lose": "XEQUE-MATE... O BRAINY VENCEU",
                     "draw": "EMPATE", "resign": "VOCÊ DESISTIU"}[self.result]
            ui.text(surf, title, (outer.centerx, outer.centery - 30), 38, C_GOLD, bold=True, center=True)
            ui.text(surf, "Aperte E para sair", (outer.centerx, outer.centery + 22), 18, C_MUTED, center=True)

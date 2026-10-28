"""Marina Luthor: o clube náutico da Luthor Corp, dirigido pelo Ian (diretor da divisão náutica, funcionário
e amigo de longa data da Letícia).

O que dá para fazer:
- Pesca em alto-mar: passeio pago até um ponto do oceano com peixes que não existem no píer.
- Passeio ao pôr do sol: recupera energia; também vira lugar de encontro com a Lucy ou a Vittoria.
- Regata de fim de semana: minigame de veleiros (desviar de boias, aproveitar o vento), prêmio em dinheiro.
- Encomendas náuticas: o Ian pede peças feitas no laboratório e paga mais que a Mesa de Contratos.
"""
import math
import random

import pygame

from . import art, ui
from .art import new, R, P, shade, mix
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_RED, C_LILAC, C_ACCENT_2, TILE
from .data import FISH, ITEMS, PROJECTS, PRODUCT_NAMES
from .world import DECK_START, CITY_DOORS

# ---------------------------------------------------------------------------
# Peixes de alto-mar e produtos náuticos (entram nas coleções, no aquário e no Terminal P&D)
# ---------------------------------------------------------------------------
DEEP_FISH = {
    "dourado": dict(name="Dourado", value=210, diff=60, where="deep", quarters=[1, 2, 3, 4], hours=(360, 1260),
                    color=(220, 200, 70)),
    "garoupa": dict(name="Garoupa", value=260, diff=66, where="deep", quarters=[1, 2, 3, 4], hours=(360, 1560),
                    color=(150, 100, 70)),
    "barracuda": dict(name="Barracuda", value=170, diff=55, where="deep", quarters=[1, 2, 3, 4],
                      hours=(360, 1560), color=(170, 180, 190)),
    "marlim": dict(name="Marlim-Azul", value=450, diff=86, where="deep", quarters=[1, 2, 3, 4], hours=(360, 1140),
                   color=(60, 90, 190)),
}
for _k, _f in DEEP_FISH.items():
    FISH[_k] = _f
    ITEMS[_k] = dict(name=_f["name"], kind="fish", value=_f["value"], icon="fish", color=_f["color"],
                     desc=f"Peixe de alto-mar. Vale ${_f['value']}. Bom para cozinhar ou para o aquário.")

NAUTICAL = {
    "sonar": dict(name="Sonar Náutico", product="Sonar Náutico", days=4, cost=70, value=170,
                  color=(90, 200, 230), icon="sonar"),
    "motor_nautico": dict(name="Motor Náutico Elétrico", product="Motor Náutico", days=6, cost=130, value=320,
                          color=(120, 150, 190), icon="engine"),
    "casco_inteligente": dict(name="Casco Inteligente", product="Casco Inteligente", days=8, cost=190, value=460,
                              color=(80, 120, 200), icon="hull"),
}
for _k, _p in NAUTICAL.items():
    PROJECTS[_k] = dict(name=_p["name"], days=_p["days"], cost=_p["cost"], value=_p["value"], quarters=[1, 2, 3, 4],
                        color=_p["color"], icon=_p["icon"], locked_flag="marina")
    PRODUCT_NAMES[_k] = _p["product"]
    ITEMS["prop_" + _k] = dict(name="Proposta: " + _p["name"], kind="proposal", project=_k, price=_p["cost"],
                               icon="folder", color=_p["color"],
                               desc=f"Inicia o {_p['name']} numa bancada. Pronto em {_p['days']} dias de trabalho.")
    ITEMS[_k] = dict(name=_p["product"], kind="product", value=_p["value"], icon=_p["icon"], color=_p["color"],
                     desc=f"Peça náutica. Vale ${_p['value']} na Mesa de Contratos; o Ian paga mais na marina.")

ORDER_BONUS = 1.25          # encomenda do Ian paga 25% a mais (é para a própria Luthor Corp)
PRICES = dict(fishing=120, sunset=80, regatta=50)
REGATTA_PRIZES = {1: 600, 2: 300, 3: 120}


# ícones dos produtos náuticos
_prev_icon = art._icon


def _icon_nautical(kind, color):
    c = color
    s = new(16, 16)
    if kind == "engine":
        R(s, shade(c, 0.7), 2, 4, 10, 9)
        R(s, c, 3, 5, 8, 7)
        for x in (4, 7, 10):
            R(s, shade(c, 1.3), x, 3, 2, 2)
        R(s, (90, 90, 100), 12, 7, 3, 3)
        pygame.draw.circle(s, (230, 190, 70), (14, 12), 2)
    elif kind == "hull":
        pygame.draw.polygon(s, c, [(1, 6), (15, 6), (12, 13), (4, 13)])
        R(s, shade(c, 1.35), 2, 6, 12, 2)
        R(s, (150, 230, 255), 6, 9, 4, 2)
        P(s, (255, 255, 255), 7, 9)
    elif kind == "sonar":
        pygame.draw.circle(s, shade(c, 0.6), (8, 8), 7)
        pygame.draw.circle(s, c, (8, 8), 5, 1)
        pygame.draw.circle(s, c, (8, 8), 2)
        pygame.draw.line(s, (180, 255, 200), (8, 8), (13, 4))
        P(s, (180, 255, 200), 11, 10)
    else:
        return _prev_icon(kind, color)
    return s


art._icon = _icon_nautical


# ---------------------------------------------------------------------------
# Estado (save)
# ---------------------------------------------------------------------------
def init_state(g):
    g.marina = dict(order=None, regatta_day=-1, sunset_day=-1, trips=0, regattas=0, wins=0)


def save_state(g):
    return dict(marina=g.marina)


def load_state(g, d):
    init_state(g)
    g.marina.update({k: v for k, v in d.get("marina", {}).items() if k in g.marina})
    o = g.marina.get("order")
    if o and o.get("item") not in ITEMS:
        g.marina["order"] = None


def price(g, what):
    p = PRICES[what]
    return p // 2 if "marina_vip" in g.flags and what != "regatta" else p


# ---------------------------------------------------------------------------
# Encomendas do Ian
# ---------------------------------------------------------------------------
def new_order(g):
    item = random.choice(list(NAUTICAL))
    qty = 1 if NAUTICAL[item]["days"] >= 6 else random.choice([1, 2])
    reward = int(NAUTICAL[item]["value"] * qty * ORDER_BONUS)
    g.marina["order"] = dict(item=item, qty=qty, reward=reward, deadline=g.abs_day() + NAUTICAL[item]["days"] + 5)


def order_text(g):
    o = g.marina.get("order")
    if not o:
        return None
    have = g.count_item(o["item"])
    return f"Encomenda Ian: {ITEMS[o['item']]['name']} {have}/{o['qty']}"


def talk_options(g, npc, opts, acts):
    """Opções extras na conversa com o Ian (primeira visita, encomendas)."""
    if npc.key != "ian":
        return
    if "marina" not in g.flags:
        g.flags.add("marina")
        g.toasts.push("Novas propostas náuticas no Terminal P&D (sonar, motor e casco).", C_GOLD, "prop_sonar")
    o = g.marina.get("order")
    if o and g.count_item(o["item"]) >= o["qty"]:
        opts.append(f"Entregar {o['qty']}x {ITEMS[o['item']]['name']}"); acts.append(lambda: deliver(g, npc))
    elif not o:
        opts.append("Pedir uma encomenda"); acts.append(lambda: ask_order(g, npc))
    else:
        opts.append("Ver a encomenda"); acts.append(lambda: show_order(g, npc))


def ask_order(g, npc):
    new_order(g)
    o = g.marina["order"]
    g.push(ui.Dialog(npc.name, [f"Preciso de {o['qty']}x {ITEMS[o['item']]['name']} pra frota da marina.",
                                f"Faz no laboratório e me traz até o dia {o['deadline'] - g.abs_day() + g.day}. "
                                f"Pago ${o['reward']}, 25% a mais que a Mesa de Contratos: é pra casa, afinal."],
                     g.portrait_for(npc, "happy"), subtitle=npc.data["role"]))


def show_order(g, npc):
    o = g.marina["order"]
    left = max(0, o["deadline"] - g.abs_day())
    g.push(ui.Dialog(npc.name, [f"Ainda espero {o['qty']}x {ITEMS[o['item']]['name']}. "
                                f"Faltam {left} dia(s). Pago ${o['reward']}.",
                                "A proposta está no Terminal P&D da sua torre."],
                     g.portrait_for(npc), subtitle=npc.data["role"]))


def deliver(g, npc):
    o = g.marina["order"]
    g.remove_item(o["item"], o["qty"])
    g.money += o["reward"]
    g.stats["earned"] = g.stats.get("earned", 0) + o["reward"]
    g.marina["order"] = None
    g.add_friendship("ian", 120)
    g.toasts.push(f"Encomenda entregue: +${o['reward']}", C_GOLD, o["item"])
    g.push(ui.Dialog(npc.name, ["Isso é engenharia Luthor de verdade. Os barcos vão voar.",
                                f"Aqui está: ${o['reward']}. Sempre que quiser, tenho mais pedidos."],
                     g.portrait_for(npc, "happy"), on_close=lambda: g.check_events("ian"), subtitle=npc.data["role"]))


def night(g, notes):
    o = g.marina.get("order")
    if o and g.abs_day() > o["deadline"]:
        g.marina["order"] = None
        notes.append(("A encomenda do Ian venceu. Ele mandou um 'sem problemas, fica pra próxima'.", C_MUTED))


# ---------------------------------------------------------------------------
# Balcão de passeios
# ---------------------------------------------------------------------------
def use_object(g, o):
    if o.kind == "charter":
        open_charter(g)
        return True
    if o.kind == "helm":
        g.push(ui.Choice("Voltar para a Marina Luthor?", ["Voltar", "Ficar pescando"],
                         lambda i: return_to_marina(g) if i == 0 else None))
        return True
    return False


def target_label(g, o):
    return {"charter": "Passeios", "helm": "Voltar"}.get(o.kind)


def open_charter(g):
    opts, acts = [], []
    m = g.minutes
    if 6 * 60 <= m < 17 * 60:
        opts.append(f"Pesca em alto-mar (${price(g, 'fishing')})"); acts.append(lambda: start_fishing_trip(g))
    if 16 * 60 + 30 <= m < 19 * 60 + 30 and g.marina["sunset_day"] != g.abs_day():
        opts.append(f"Passeio ao pôr do sol (${price(g, 'sunset')})"); acts.append(lambda: start_sunset(g))
    if g.weekday >= 5 and 8 * 60 <= m < 17 * 60 and g.marina["regatta_day"] != g.abs_day():
        opts.append(f"Regata de fim de semana (inscrição ${price(g, 'regatta')})"); acts.append(lambda: start_regatta(g))
    if not opts:
        g.say("Quadro de passeios: pesca em alto-mar das 6h às 17h, pôr do sol das 16h30 às 19h30 "
              "e regata aos sábados e domingos, das 8h às 17h.")
        return
    opts.append("Sair"); acts.append(lambda: None)
    g.push(ui.Choice("Marina Luthor: passeios", opts, lambda i: acts[i]()))


def _pay(g, what):
    p = price(g, what)
    if g.money < p:
        g.toasts.push("Dinheiro insuficiente.", C_RED)
        return False
    g.money -= p
    return True


def start_fishing_trip(g):
    if not _pay(g, "fishing"):
        return
    g.marina["trips"] += 1
    g.minutes += 30
    g.warp("altomar", DECK_START[0], DECK_START[1], "right")
    g.toasts.push("Alto-mar! Marlim, dourado, garoupa e barracuda só aparecem aqui.", C_LILAC)
    g.toasts.push("Use o timão para voltar para a marina.", C_MUTED)


def return_to_marina(g):
    g.minutes += 30
    cx, cy = CITY_DOORS["marina"]
    g.warp("city", 96, 59, "up")


def start_sunset(g):
    if not _pay(g, "sunset"):
        return
    g.marina["sunset_day"] = g.abs_day()
    from .cutscenes import Cutscene
    steps = [
        ("ator", "player", 30, 13, "right"),
        ("camera_ja", 26, 13),
        ("fade_in",),
        ("legenda", "Passeio ao pôr do sol", 2.0),
        ("narra", "O barco desliza devagar. O farol acende e a cidade inteira fica laranja."),
        ("fala", "player", "Faz tempo que eu não fico parada assim, sem planilha e sem reunião.", "feliz"),
        ("efeito", "brilhos", 2.5),
        ("esperar", 2.0),
        ("fade_out",),
    ]

    def done():
        g.energy = min(g.max_energy, g.energy + 50)
        g.minutes = max(g.minutes, 19 * 60) + 30
        for n in g.npcs.values():
            n.check_schedule(g.minutes)
        cx, cy = CITY_DOORS["marina"]
        g.map_name = "city"
        g.player.place_tile(cx, cy + 1, "down")
        g.toasts.push("Passeio ao pôr do sol: +50 de energia.", C_GREEN)
    g.push(Cutscene(g, dict(map="altomar", time=18 * 60 + 40, steps=steps), on_end=done))


def start_regatta(g):
    if not _pay(g, "regatta"):
        return
    g.marina["regatta_day"] = g.abs_day()

    def done(place):
        g.marina["regattas"] += 1
        prize = REGATTA_PRIZES.get(place, 0)
        g.minutes += 60
        if prize:
            g.money += prize
            g.stats["earned"] = g.stats.get("earned", 0) + prize
        if place == 1:
            g.marina["wins"] += 1
            g.add_friendship("ian", 40)
        msg = {1: "1º lugar! Troféu e", 2: "2º lugar!", 3: "3º lugar!"}.get(place, f"{place}º lugar.")
        g.toasts.push(f"Regata: {msg} +${prize}" if prize else f"Regata: {msg} Fica pra próxima!",
                      C_GOLD if prize else C_MUTED)
    g.push(Regatta(done))


def date_scene_steps(key):
    """Encontro no iate ao pôr do sol (lugar de encontro 'marina')."""
    return [
        ("ator", key, 31, 13, "left"),
        ("ator", "player", 29, 13, "right"),
        ("camera_ja", 28, 13),
        ("fade_in",),
        ("legenda", "Um passeio de iate ao pôr do sol", 2.0),
    ]


# ---------------------------------------------------------------------------
# Regata (minigame)
# ---------------------------------------------------------------------------
class Regatta(ui.Modal):
    W, H = 560, 600
    LENGTH = 5200            # distância da prova (em unidades de tela)
    LANE_W = 420

    def __init__(self, on_done):
        self.on_done = on_done
        self.t = -3.0
        self.x = 0.5                    # posição do veleiro (0..1 na largura da raia)
        self.dist = 0.0
        self.speed = 0.0
        self.slow = 0.0
        self.boost = 0.0
        rnd = random.Random()
        self.rivals = [dict(name=n, color=c, dist=0.0, base=b, ph=rnd.uniform(0, 6))
                       for n, c, b in (("Ian", (60, 90, 190), 222), ("Clube Gotham", (220, 70, 70), 208),
                                       ("Marlins", (240, 190, 60), 196))]
        self.buoys = []
        self.winds = []
        y = 500
        while y < self.LENGTH - 200:
            self.buoys.append(dict(x=rnd.uniform(0.08, 0.92), y=y, hit=False))
            if rnd.random() < 0.55:
                self.buoys.append(dict(x=rnd.uniform(0.08, 0.92), y=y + rnd.uniform(60, 120), hit=False))
            if rnd.random() < 0.6:
                self.winds.append(dict(x=rnd.uniform(0.1, 0.9), y=y + rnd.uniform(150, 260), w=0.16, h=170))
            y += rnd.uniform(240, 330)
        self.finished = []
        self.place = None
        self.over_t = 0.0

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and self.place is not None and self.over_t > 0.8 and ev.key in (
                ui.CONFIRM + ui.CANCEL):
            self.done = True
            self.on_done(self.place)

    def update(self, dt):
        self.t += dt
        if self.place is not None:
            self.over_t += dt
            return
        if self.t < 0:
            return
        keys = pygame.key.get_pressed()
        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.x = min(0.97, max(0.03, self.x + mx * 0.75 * dt))
        target = 210.0
        if self.boost > 0:
            target = 330.0
            self.boost -= dt
        if self.slow > 0:
            target = 70.0
            self.slow -= dt
        self.speed += (target - self.speed) * min(1.0, dt * 2.5)
        self.dist += self.speed * dt
        for b in self.buoys:
            if not b["hit"] and abs(b["y"] - self.dist) < 22 and abs(b["x"] - self.x) * self.LANE_W < 22:
                b["hit"] = True
                self.slow = 1.0
                self.boost = 0
        for w in self.winds:
            if w["y"] - w["h"] < self.dist < w["y"] and abs(w["x"] - self.x) < w["w"] / 2:
                self.boost = max(self.boost, 1.2)
        for r in self.rivals:
            if r["dist"] < self.LENGTH:
                r["dist"] += (r["base"] + math.sin(self.t * 0.8 + r["ph"]) * 30) * dt
                if r["dist"] >= self.LENGTH:
                    self.finished.append(r["name"])
        if self.dist >= self.LENGTH:
            self.place = len(self.finished) + 1

    def draw(self, surf):
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((6, 4, 16, 170))
        surf.blit(veil, (0, 0))
        rect = pygame.Rect(0, 0, self.W, self.H)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, "REGATA DA MARINA LUTHOR", (rect.centerx, rect.y + 14), 22, C_TEXT, bold=True, center=True)
        lane = pygame.Rect(rect.x + 20, rect.y + 50, self.LANE_W, rect.h - 100)
        pygame.draw.rect(surf, (40, 110, 190), lane)
        clip = surf.get_clip()
        surf.set_clip(lane)
        base_y = lane.bottom - 70                       # onde fica o veleiro da Letícia
        off = self.dist % 40
        for i in range(-1, lane.h // 40 + 2):
            y = lane.y + i * 40 + off
            for k in range(6):
                x = lane.x + (k * 77 + i * 31) % lane.w
                pygame.draw.line(surf, (90, 160, 225), (x, y), (x + 14, y), 2)

        def sy(d):
            return base_y - (d - self.dist)
        for w in self.winds:
            top, bot = sy(w["y"]), sy(w["y"] - w["h"])
            if bot < lane.y or top > lane.bottom:
                continue
            x = lane.x + w["x"] * lane.w
            zone = pygame.Surface((int(w["w"] * lane.w), int(bot - top)), pygame.SRCALPHA)
            zone.fill((230, 250, 255, 55))
            surf.blit(zone, (x - zone.get_width() // 2, top))
            for k in range(3):
                yy = top + 20 + k * 50
                if yy < bot - 10:
                    pygame.draw.polygon(surf, (240, 255, 255), [(x, yy - 10), (x - 8, yy + 4), (x + 8, yy + 4)])
        finish = sy(self.LENGTH)
        if lane.y - 10 < finish < lane.bottom:
            for k in range(0, lane.w, 20):
                pygame.draw.rect(surf, (250, 250, 250) if (k // 20) % 2 == 0 else (30, 30, 40),
                                 (lane.x + k, finish - 6, 20, 12))
        for b in self.buoys:
            y = sy(b["y"])
            if lane.y - 20 < y < lane.bottom + 20:
                x = lane.x + b["x"] * lane.w
                col = (120, 80, 60) if b["hit"] else (245, 120, 40)
                pygame.draw.circle(surf, col, (int(x), int(y)), 10)
                pygame.draw.rect(surf, (250, 250, 250), (x - 10, y - 2, 20, 4))
        for i, r in enumerate(self.rivals):
            y = sy(r["dist"])
            if lane.y - 30 < y < lane.bottom + 30:
                _boat(surf, lane.x + (0.2 + i * 0.3) * lane.w, y, r["color"])
        _boat(surf, lane.x + self.x * lane.w, base_y, (184, 76, 255), wake=self.speed > 250)
        surf.set_clip(clip)
        pygame.draw.rect(surf, (90, 150, 220), lane, 2)
        # barra de progresso lateral
        bar = pygame.Rect(lane.right + 22, lane.y, 18, lane.h)
        pygame.draw.rect(surf, (30, 24, 46), bar, border_radius=6)
        for r in self.rivals:
            y = bar.bottom - min(1, r["dist"] / self.LENGTH) * bar.h
            pygame.draw.circle(surf, r["color"], (bar.centerx, int(y)), 6)
        y = bar.bottom - min(1, self.dist / self.LENGTH) * bar.h
        pygame.draw.circle(surf, (184, 76, 255), (bar.centerx, int(y)), 8)
        pygame.draw.circle(surf, (255, 255, 255), (bar.centerx, int(y)), 8, 2)
        ui.text(surf, "chegada", (bar.centerx, bar.y - 22), 14, C_MUTED, center=True)
        speed_kn = int(self.speed / 18)
        ui.text(surf, f"{speed_kn} nós", (bar.centerx, bar.bottom + 4), 15, C_LILAC, center=True)
        hint = "A/D ou setas: desviar das boias   ·   passe pelas faixas de vento para acelerar"
        ui.text(surf, hint, (rect.centerx, rect.bottom - 40), 15, C_MUTED, center=True)
        if self.t < 0:
            n = int(-self.t) + 1
            ui.text(surf, str(n), (lane.centerx, lane.centery - 40), 72, C_GOLD, bold=True, center=True)
        elif self.t < 0.8:
            ui.text(surf, "VAI!", (lane.centerx, lane.centery - 40), 64, C_GREEN, bold=True, center=True)
        if self.place is not None:
            box = pygame.Rect(0, 0, 340, 130)
            box.center = lane.center
            ui.panel(surf, box)
            prize = REGATTA_PRIZES.get(self.place, 0)
            ui.text(surf, f"{self.place}º lugar!", (box.centerx, box.y + 18), 40, C_GOLD if prize else C_TEXT,
                    bold=True, center=True)
            ui.text(surf, f"Prêmio: ${prize}" if prize else "Sem prêmio desta vez.", (box.centerx, box.y + 70), 20,
                    C_GREEN if prize else C_MUTED, center=True)
            ui.text(surf, "Enter para continuar", (box.centerx, box.y + 98), 15, C_MUTED, center=True)


def _boat(surf, x, y, sail, wake=False):
    x, y = int(x), int(y)
    if wake:
        for k in range(3):
            pygame.draw.line(surf, (200, 230, 255), (x - 6 - k * 3, y + 14 + k * 6), (x + 6 + k * 3, y + 14 + k * 6), 2)
    pygame.draw.polygon(surf, (245, 245, 250), [(x - 9, y), (x + 9, y), (x + 6, y + 12), (x - 6, y + 12)])
    pygame.draw.line(surf, (80, 70, 60), (x, y - 26), (x, y), 2)
    pygame.draw.polygon(surf, sail, [(x + 1, y - 26), (x + 1, y - 2), (x + 14, y - 2)])
    pygame.draw.polygon(surf, (250, 250, 250), [(x - 1, y - 22), (x - 1, y - 2), (x - 11, y - 2)])

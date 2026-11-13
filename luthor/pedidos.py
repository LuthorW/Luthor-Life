"""Quadro de pedidos do Grão Nobre (como o "Help Wanted" do Stardew).

Um quadro de cortiça de pé perto das mesas do café (`BOARD` = (8, 2), 2x1). Toda noite ele ganha bilhetes novos
(espaços liberados aos poucos: `UNLOCK`, pelo número de pedidos entregues); cada bilhete é um pedido de um morador: peixe, colheita da horta, coletável ou prato. A Letícia
aceita no quadro (no máx. `MAX_ACTIVE` ao mesmo tempo) e entrega conversando com quem pediu, até o prazo. Pagamento
em dinheiro + amizade; nada de castigo se o prazo passar (o bilhete só some). Estado em `g.pedidos`.
"""
import random

import pygame

from . import art, world, ui, audio, seasons
from .art import new, R, P, shade
from .config import C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_PINK, C_RED, DAYS_PER_QUARTER
from .data import ITEMS, FISH, CROPS, FORAGE, RECIPES
from .characters import NPCS, NPC_ORDER

BOARD = (8, 2)
MAX_OFFERS = 3              # espaços do quadro (bilhetes no quadro + pedidos aceitos)
UNLOCK = (0, 3, 7)          # o espaço N abre depois de entregar UNLOCK[N] pedidos (no começo, só 1 espaço)
MAX_ACTIVE = 2
OFFER_DAYS = 3              # o bilhete fica no quadro por 3 dias se ninguém aceitar
DEADLINE = 3                # dias para entregar depois de aceitar

REASONS = {
    "fish": ["para um jantar especial", "para testar uma receita nova", "porque prometi um churrasco",
             "para a festa do prédio", "para impressionar a minha mãe no domingo"],
    "crop": ["para uma salada fresquinha", "para um molho caseiro", "porque o mercado acabou",
             "para um suco verde (não me julga)", "para enfeitar a mesa do almoço"],
    "forage": ["para a minha coleção", "para um presente artesanal", "para decorar a sala",
               "para um projeto da faculdade do meu sobrinho", "porque achei bonito e não sei explicar"],
    "dish": ["para o aniversário de uma amiga", "porque não sei cozinhar nem arroz", "para a reunião de amanhã",
             "para levar num piquenique", "porque estou com saudade de comida caseira"],
}
THANKS = ["Perfeito! Era exatamente isso. Obrigada por ler o quadro!",
          "Você viu meu bilhete! Nem acredito. Muito obrigada!",
          "Que rapidez! Pode deixar que eu conto pra todo mundo quem me salvou.",
          "Ah, que alívio. Toma aqui o combinado, e mais um obrigada de brinde."]


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.pedidos = dict(offers=[], active=[], done=0, seq=0)


def save_state(g):
    return {"pedidos": g.pedidos}


def load_state(g, d):
    init_state(g)
    p = d.get("pedidos") or {}
    ok = lambda r: isinstance(r, dict) and r.get("item") in ITEMS and r.get("npc") in NPCS
    g.pedidos["offers"] = [r for r in p.get("offers", []) if ok(r)]
    g.pedidos["active"] = [r for r in p.get("active", []) if ok(r)]
    g.pedidos["done"] = int(p.get("done", 0))
    g.pedidos["seq"] = int(p.get("seq", 0))
    room = max(0, slots(g) - len(g.pedidos["active"]))       # saves antigos: só os espaços já liberados
    g.pedidos["offers"] = g.pedidos["offers"][:room]
    if not g.pedidos["offers"] and not g.pedidos["active"]:
        refill(g)


def slots(g):
    """Quantos espaços do quadro estão liberados (1 no começo; mais conforme a Letícia entrega pedidos)."""
    return sum(1 for need in UNLOCK if g.pedidos["done"] >= need)


def max_active(g):
    return min(MAX_ACTIVE, slots(g))


# ---------------------------------------------------------------------------
# Bilhetes
# ---------------------------------------------------------------------------
def _pool(g):
    season = seasons.of_quarter(g.quarter)
    out = []
    for k, f in FISH.items():
        if f["where"] in ("sea", "pond") and g.quarter in f["quarters"] and not f.get("weather") \
                and f["value"] <= 120 and not f.get("legendary") and k in ITEMS:
            out.append(("fish", k))
    for c in CROPS.values():
        if c["item"] in ITEMS:
            out.append(("crop", c["item"]))
    for k in FORAGE:
        if k in ITEMS and season in seasons.FORAGE_SEASONS.get(k, seasons.SEASONS):
            out.append(("forage", k))
    for k in RECIPES:
        if k in ITEMS:
            out.append(("dish", k))
    return out


def _make(g):
    taken = {r["npc"] for r in g.pedidos["offers"] + g.pedidos["active"]}
    if g.request:
        taken.add(g.request["npc"])
    who = [k for k in NPC_ORDER if k not in taken]
    pool = _pool(g)
    if not who or not pool:
        return None
    kind, item = random.choice(pool)
    value = ITEMS[item].get("value", 30) or 30
    qty = {"fish": random.choice([1, 1, 2]), "crop": random.choice([2, 3, 4]),
           "forage": random.choice([1, 2, 3]), "dish": 1}[kind]
    reward = int(value * qty * {"fish": 2.0, "crop": 2.4, "forage": 2.2, "dish": 1.8}[kind]) + 30
    reward = int(round(reward / 5.0) * 5)
    g.pedidos["seq"] += 1
    return dict(id=g.pedidos["seq"], npc=random.choice(who), kind=kind, item=item, qty=qty, reward=reward,
                pts=60 + 20 * qty, reason=random.choice(REASONS[kind]), posted=g.abs_day(), deadline=None)


def refill(g):
    tries = 0
    while len(g.pedidos["offers"]) + len(g.pedidos["active"]) < slots(g) and tries < 12:
        tries += 1
        r = _make(g)
        if r:
            g.pedidos["offers"].append(r)


def night(g, notes):
    """Bilhetes velhos saem, pedidos aceitos que passaram do prazo somem (sem castigo) e chegam bilhetes novos."""
    today = g.abs_day()
    for r in [r for r in g.pedidos["active"] if r["deadline"] is not None and today > r["deadline"]]:
        g.pedidos["active"].remove(r)
        notes.append((f"O pedido de {NPCS[r['npc']]['short']} no quadro do Grão Nobre venceu. "
                      "Sem problema: tem bilhete novo lá.", C_MUTED))
    g.pedidos["offers"] = [r for r in g.pedidos["offers"] if today - r["posted"] < OFFER_DAYS]
    before = len(g.pedidos["offers"])
    if random.random() < 0.8 or before == 0:
        refill(g)
    if len(g.pedidos["offers"]) > before:
        notes.append(("Bilhetes novos no quadro de pedidos do Grão Nobre.", C_GOLD))


def label(r):
    return f"{r['qty']}x {ITEMS[r['item']]['name']}"


def days_left(g, r):
    return r["deadline"] - g.abs_day() if r["deadline"] is not None else None


def hud_lines(g):
    out = []
    for r in g.pedidos["active"]:
        have = min(g.count_item(r["item"]), r["qty"])
        ok = have >= r["qty"]
        out.append((f"Quadro {NPCS[r['npc']]['short']}: {ITEMS[r['item']]['name']} {have}/{r['qty']}",
                    C_GREEN if ok else (240, 200, 140)))
    return out


# ---------------------------------------------------------------------------
# Aceitar no quadro e entregar conversando
# ---------------------------------------------------------------------------
def object_label(g, o):
    if o.kind == "quadro_pedidos":
        n = len(g.pedidos["offers"])
        return f"Quadro de pedidos ({n} bilhete{'s' if n != 1 else ''})"
    return None


def use_object(g, o):
    if o.kind != "quadro_pedidos":
        return False
    if g.pedidos["seq"] == 0:                       # jogo novo: os primeiros bilhetes já estão lá
        refill(g)
    audio.sfx("open")
    g.push(Board(g))
    return True


def accept(g, r):
    if len(g.pedidos["active"]) >= max_active(g):
        n = max_active(g)
        return False, (f"Você já tem {n} pedido{'s' if n > 1 else ''} do quadro. Entregue antes de pegar outro.")
    g.pedidos["offers"].remove(r)
    r["deadline"] = g.abs_day() + DEADLINE
    g.pedidos["active"].append(r)
    return True, f"Pedido aceito: {label(r)} para {NPCS[r['npc']]['short']} em até {DEADLINE} dias."


def talk(g, npc):
    """Entrega na conversa. True = a conversa foi usada aqui."""
    for r in g.pedidos["active"]:
        if r["npc"] != npc.key:
            continue
        if g.count_item(r["item"]) < r["qty"]:
            return False
        g.remove_item(r["item"], r["qty"])
        g.pedidos["active"].remove(r)
        before = slots(g)
        g.pedidos["done"] += 1
        if slots(g) > before:
            g.toasts.push("Mais um espaço liberado no quadro de pedidos do Grão Nobre!", C_GOLD)
        g.money += r["reward"]
        g.add_friendship(npc.key, r["pts"])
        audio.sfx("reward")
        g.toasts.push(f"Pedido do quadro entregue: +${r['reward']}", C_GOLD, r["item"])
        g.push(ui.Dialog(npc.name, [random.choice(THANKS), f"Aqui está: ${r['reward']}."],
                         g.portrait_for(npc, "happy"), subtitle=npc.data["role"],
                         on_close=lambda k=npc.key: g.check_events(k)))
        return True
    return False


# ---------------------------------------------------------------------------
# Tela do quadro
# ---------------------------------------------------------------------------
NOTE_COLORS = ((255, 244, 170), (190, 230, 255), (255, 206, 220), (210, 246, 200))


class Board(ui.Modal):
    def __init__(self, g):
        self.g = g
        self.sel = 0
        self.msg, self.msg_t, self.msg_ok = "", 0.0, True

    def rows(self):
        return self.g.pedidos["offers"] + self.g.pedidos["active"]

    def handle(self, ev):
        rows = self.rows()
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w) and rows:
            self.sel = (self.sel - 1) % len(rows); audio.sfx("move")
        elif ev.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s) and rows:
            self.sel = (self.sel + 1) % len(rows); audio.sfx("move")
        elif ev.key in ui.CONFIRM and rows:
            r = rows[min(self.sel, len(rows) - 1)]
            if r in self.g.pedidos["active"]:
                audio.sfx("blip")
                self.say(f"Já é seu: leve {label(r)} para {NPCS[r['npc']]['short']} e converse com ela.", True)
                return
            ok, msg = accept(self.g, r)
            audio.sfx("confirm" if ok else "blip")
            self.say(msg, ok)
        elif ev.key in ui.CANCEL:
            self.done = True

    def say(self, msg, ok):
        self.msg, self.msg_t, self.msg_ok = msg, 3.0, ok

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)

    def draw(self, surf):
        g = self.g
        outer = pygame.Rect(0, 0, 860, 520)
        outer.center = (640 - 50, 350)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "Quadro de pedidos", (outer.x + 28, outer.y + 16), 28, C_GOLD, bold=True)
        ui.text(surf, f"Grão Nobre  ·  pedidos entregues: {g.pedidos['done']}", (outer.x + 30, outer.y + 52), 16,
                C_LILAC)
        cork = pygame.Rect(outer.x + 24, outer.y + 84, outer.w - 48, 330)
        ui.slot(surf, cork, fill=(150, 104, 66))
        rng = random.Random(7)
        for _ in range(140):                                # textura da cortiça
            x = rng.randrange(cork.x + 4, cork.right - 4)
            y = rng.randrange(cork.y + 4, cork.bottom - 4)
            pygame.draw.rect(surf, (128, 86, 52) if rng.random() < 0.6 else (172, 124, 82), (x, y, 2, 2))
        rows = self.rows()
        self.sel = min(self.sel, max(0, len(rows) - 1))
        n_open = slots(g)
        w = min(250, (cork.w - 40 - 16 * (MAX_OFFERS - 1)) // MAX_OFFERS)
        x0 = cork.centerx - (w * MAX_OFFERS + 16 * (MAX_OFFERS - 1)) // 2
        ink = (60, 40, 30)
        for i in range(MAX_OFFERS):
            note = pygame.Rect(x0 + i * (w + 16), cork.y + 26 + (i % 2) * 10, w, 270)
            if i >= len(rows):
                if i < n_open:                                  # espaço liberado, sem bilhete hoje
                    ui.cut_rect(surf, (128, 86, 52), note, 2)
                    ui.text(surf, "Espaço livre", (note.centerx, note.centery - 22), 18, (230, 210, 180),
                            bold=True, center=True, shadow=False)
                    ui.text(surf, "bilhete novo à noite", (note.centerx, note.centery + 4), 15, (220, 196, 160),
                            center=True, shadow=False)
                else:                                           # espaço trancado
                    ui.cut_rect(surf, (96, 70, 50), note, 2)
                    lx, ly = note.centerx - 12, note.centery - 50
                    pygame.draw.rect(surf, (200, 176, 110), (lx, ly + 12, 24, 18))
                    pygame.draw.rect(surf, (200, 176, 110), (lx + 4, ly, 4, 12))
                    pygame.draw.rect(surf, (200, 176, 110), (lx + 16, ly, 4, 12))
                    pygame.draw.rect(surf, (200, 176, 110), (lx + 4, ly, 16, 4))
                    pygame.draw.rect(surf, (90, 66, 40), (lx + 10, ly + 17, 4, 8))
                    need = UNLOCK[i] - g.pedidos["done"]
                    ui.text(surf, "Trancado", (note.centerx, note.centery - 6), 18, (230, 210, 180), bold=True,
                            center=True, shadow=False)
                    for k, ln in enumerate(ui.wrap(f"Entregue mais {need} pedido{'s' if need != 1 else ''} "
                                                   "para liberar", 15, w - 30)):
                        ui.text(surf, ln, (note.centerx, note.centery + 20 + k * 19), 15, (220, 196, 160),
                                center=True, shadow=False)
                continue
            r = rows[i]
            active = r in g.pedidos["active"]
            col = NOTE_COLORS[r["id"] % len(NOTE_COLORS)]
            if i == self.sel:
                ui.cut_rect(surf, (255, 240, 200), note.inflate(8, 8), 2)
            ui.cut_rect(surf, shade(col, 0.82), note.move(3, 4), 2)
            ui.cut_rect(surf, col, note, 2)
            pygame.draw.circle(surf, (210, 50, 70) if not active else (60, 160, 90), (note.centerx, note.y + 8), 6)
            npc = NPCS[r["npc"]]
            ui.text(surf, f"De: {npc['short']}", (note.x + 14, note.y + 22), 19, ink, bold=True, shadow=False)
            surf.blit(art.item_icon(r["item"], 3), (note.centerx - 24, note.y + 52))
            ui.text(surf, label(r), (note.centerx, note.y + 104), 18, ink, bold=True, center=True, shadow=False)
            for k, ln in enumerate(ui.wrap(r["reason"], 15, w - 24)[:2]):
                ui.text(surf, ln, (note.centerx, note.y + 132 + k * 19), 15, (90, 70, 56), center=True,
                        shadow=False)
            ui.text(surf, f"Paga ${r['reward']}", (note.centerx, note.y + 186), 18, (40, 110, 60), bold=True,
                    center=True, shadow=False)
            if active:
                left = days_left(g, r)
                txt = "entrega hoje!" if left == 0 else f"aceito · {left} dia{'s' if left != 1 else ''}"
                have = min(g.count_item(r["item"]), r["qty"])
                ui.text(surf, txt, (note.centerx, note.y + 214), 15, (140, 60, 120), bold=True, center=True,
                        shadow=False)
                ui.text(surf, f"na mochila: {have}/{r['qty']}", (note.centerx, note.y + 236), 14, (90, 70, 56),
                        center=True, shadow=False)
            else:
                ui.text(surf, "E: aceitar", (note.centerx, note.y + 222), 15, (90, 70, 56), center=True, shadow=False)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (outer.centerx, outer.bottom - 70), 17, C_GREEN if self.msg_ok else C_RED,
                    bold=True, center=True)
        else:
            ui.text(surf, f"Pedidos aceitos: {len(g.pedidos['active'])}/{max_active(g)}  ·  entregue conversando "
                          "com quem pediu, até o prazo", (outer.centerx, outer.bottom - 70), 16, C_MUTED, center=True)
        ui.text(surf, "Setas: escolher   E: aceitar   Esc: sair", (outer.centerx, outer.bottom - 34), 16, C_MUTED,
                center=True)


# ---------------------------------------------------------------------------
# Arte: quadro de cortiça de pé
# ---------------------------------------------------------------------------
def _quadro_pedidos():
    s = new(32, 30)
    wood, dark = (122, 82, 50), (84, 54, 32)
    R(s, dark, 3, 20, 2, 10); R(s, dark, 27, 20, 2, 10)              # pernas
    R(s, wood, 3, 20, 1, 10); R(s, wood, 27, 20, 1, 10)
    R(s, dark, 0, 0, 32, 22)                                          # moldura
    R(s, wood, 1, 1, 30, 20)
    R(s, (176, 128, 84), 2, 2, 28, 18)                                # cortiça
    rng = random.Random(3)
    for _ in range(40):
        P(s, (150, 104, 66), rng.randrange(2, 30), rng.randrange(2, 20))
    for (x, y, c, pin) in ((4, 4, (255, 244, 170), (210, 50, 70)), (13, 3, (190, 230, 255), (60, 160, 90)),
                           (21, 5, (255, 206, 220), (70, 110, 220))):
        R(s, shade(c, 0.8), x + 1, y + 1, 7, 9)
        R(s, c, x, y, 7, 9)
        for k in range(3):
            R(s, (120, 110, 100), x + 1, y + 3 + k * 2, 5 - (k == 2) * 2, 1)
        P(s, pin, x + 3, y)
    R(s, (240, 214, 140), 9, 15, 14, 3)                               # plaquinha
    R(s, (90, 60, 30), 10, 16, 12, 1)
    return s


art.OBJECT_BUILDERS.update({"quadro_pedidos": _quadro_pedidos})
world.OBJECT_DEFS.update({"quadro_pedidos": (2, 1, True, "obj")})
FLAVOR = {"quadro_pedidos": "Bilhetes dos moradores pedindo ajuda. Quem ajuda ganha uns trocados e amizade."}

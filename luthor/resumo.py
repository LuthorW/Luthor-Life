"""Tela do fim do dia (depois de dormir ou desmaiar).

À esquerda as vendas da noite (as maiores, com ícone) e o total por tipo; à direita a ação LCORP, o dinheiro e o
dia que começa; embaixo os avisos da noite. V (ou Tab) abre a lista com TODOS os itens vendidos, separados por
tipo, com a quantidade, o preço de cada um e o total. Enter começa o novo dia.
"""
import math

import pygame

from . import ui, art, audio
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_RED, C_PINK
from .data import ITEMS

KINDS = (("product", "Produtos"), ("fish", "Peixes"), ("dish", "Pratos"), ("crop", "Colheita"),
         ("forage", "Coletáveis"), ("junk", "Achados"))
KIND_NAME = dict(KINDS)
OPEN_KEYS = (pygame.K_v, pygame.K_TAB)
TOP = 5                                         # vendas mostradas na tela; o resto fica na lista (V)


def money(v):
    return f"$ {v:,}".replace(",", ".")


def _sorted(table):
    return sorted(table, key=lambda r: -r[2])


def by_kind(table):
    out = {}
    for item, n, val in table:
        k = ITEMS[item]["kind"]
        out[k] = out.get(k, 0) + val
    return [(k, out[k]) for k, _ in KINDS if k in out] + [(k, v) for k, v in out.items() if k not in KIND_NAME]


def handle(g, ev):
    if ev.type == pygame.KEYDOWN and ev.key in OPEN_KEYS:
        open_sales(g)
    elif ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM:
        g.start_fade(g.begin_day)


def open_sales(g):
    s = g.summary
    if not s or not (s["table"] or s["notes"]):
        audio.sfx("cancel")
        return
    audio.sfx("open")
    rows = []
    for k, total in by_kind(s["table"]):
        items = _sorted([r for r in s["table"] if ITEMS[r[0]]["kind"] == k])
        rows.append(("head", k, total, sum(n for _, n, _ in items)))
        rows += [("item",) + r for r in items]
    if s["notes"]:                                   # e os avisos da noite, todos
        rows.append(("notes_head",))
        for msg, color in s["notes"]:
            lines = ui.wrap(msg, 17, 700)
            for i, line in enumerate(lines):
                rows.append(("note", line, color, i == 0))

    def draw_row(surf, r, row, sel):
        if row[0] == "notes_head":
            ui.text(surf, "Avisos da noite", (r.x + 12, r.y + 8), 22, C_LILAC, bold=True)
            surf.fill((80, 60, 110), (r.x + 10, r.bottom - 4, r.w - 20, ui.U))
            return
        if row[0] == "note":
            _, line, color, first = row
            ui.text(surf, ("- " if first else "  ") + line, (r.x + 14, r.y + 10), 17, color)
            return
        if row[0] == "head":
            _, k, total, n = row
            ui.text(surf, KIND_NAME.get(k, k.title()), (r.x + 12, r.y + 8), 22, C_LILAC, bold=True)
            ui.text(surf, f"{n} {'item' if n == 1 else 'itens'}", (r.x + 200, r.y + 12), 16, C_MUTED)
            ui.text(surf, money(total), (r.right - 14, r.y + 8), 22, C_GOLD, bold=True, right=True)
            surf.fill((80, 60, 110), (r.x + 10, r.bottom - 4, r.w - 20, ui.U))
            return
        _, item, n, val = row
        surf.blit(art.item_icon(item, 2), (r.x + 12, r.y + 3))
        ui.text(surf, ITEMS[item]["name"], (r.x + 56, r.y + 8), 19, C_TEXT)
        unit = val // max(1, n)
        ui.text(surf, f"{n} x {money(unit)}", (r.right - 170, r.y + 10), 17, C_MUTED, right=True)
        ui.text(surf, money(val), (r.right - 14, r.y + 8), 19, C_GOLD, right=True)

    n_items = sum(n for _, n, _ in s["table"])
    sub = (f"{n_items} itens vendidos  ·  total {money(s['earnings'])}" if n_items else "Nada vendido nesta noite.")
    g.push(ui.ScrollPanel("Vendas da noite", lambda: rows, draw_row, 44, sub, close_keys=OPEN_KEYS))


def _button(surf, r, key, label, on, t):
    ui.box(surf, r, (110, 30, 170) if on else (40, 28, 60), border=(184, 76, 255) if on else (80, 56, 112), cut=2)
    kw = ui.font(18, True).size(key)[0] + 16
    kr = pygame.Rect(r.x + 10, r.centery - 13, kw, 26)
    ui.box(surf, kr, (24, 14, 36), cut=1)
    ui.text(surf, key, (kr.centerx, kr.y + 2), 18, C_GOLD, bold=True, center=True)
    ui.text(surf, label, (kr.right + 10, r.centery - 12), 20, C_TEXT if on else C_MUTED, bold=on)


def draw(g, surf):
    s = g.summary
    surf.fill((10, 6, 18))
    for i in range(0, SCREEN_H, 4):                      # céu da noite: degradê bem leve
        c = int(8 + 14 * i / SCREEN_H)
        surf.fill((c, c // 2 + 2, c + 10), (0, i, SCREEN_W, 4))
    for k in range(40):                                  # estrelinhas
        x = (k * 337) % SCREEN_W
        y = (k * 151) % 120 + 6
        if (int(g.t * 2) + k) % 7:
            surf.fill((200, 190, 240), (x, y, 2, 2))
    d, q, y = s["date"]
    ui.text(surf, "Fim do dia", (SCREEN_W // 2, 22), 40, C_TEXT, bold=True, center=True)
    ui.text(surf, g.date_label(d, q, y), (SCREEN_W // 2, 72), 20, C_LILAC, center=True)

    # --- vendas -----------------------------------------------------------
    L = pygame.Rect(90, 112, 690, 400)
    ui.panel(surf, L)
    ui.text(surf, "Vendas da noite", (L.x + 26, L.y + 18), 22, C_LILAC, bold=True)
    n_items = sum(n for _, n, _ in s["table"])
    if s["table"]:
        ui.text(surf, f"{n_items} {'item' if n_items == 1 else 'itens'}", (L.right - 26, L.y + 22), 17, C_MUTED,
                right=True)
    yy = L.y + 58
    table = _sorted(s["table"])
    if not table:
        ui.text(surf, "Nada vendido hoje.", (L.x + 26, yy + 4), 19, C_MUTED)
        ui.text(surf, "Deixe produtos, peixes ou pratos na Mesa de Contratos ou", (L.x + 26, yy + 40), 16, C_MUTED)
        ui.text(surf, "na caixa de coleta do píer: eles são vendidos à noite.", (L.x + 26, yy + 62), 16, C_MUTED)
    for item, n, val in table[:TOP]:
        row = pygame.Rect(L.x + 18, yy - 4, L.w - 36, 38)
        ui.slot(surf, (row.x + 4, row.y + 2, 34, 34))
        surf.blit(art.item_icon(item, 2), (row.x + 5, row.y + 3))
        ui.text(surf, ITEMS[item]["name"], (row.x + 50, row.y + 6), 19)
        ui.text(surf, f"{n}x", (row.right - 150, row.y + 8), 17, C_MUTED, right=True)
        ui.text(surf, money(val), (row.right - 8, row.y + 6), 19, C_GOLD, right=True)
        yy += 40
    if len(table) > TOP:
        ui.text(surf, f"+ {len(table) - TOP} outros itens (aperte V para ver todos)", (L.x + 68, yy), 16, C_MUTED)
    # total por tipo
    base = L.bottom - 80
    surf.fill((80, 60, 110), (L.x + 22, base - 8, L.w - 44, ui.U))
    x = L.x + 26
    for k, v in by_kind(s["table"])[:4]:
        lab = f"{KIND_NAME.get(k, k)}: {money(v)}"
        ui.text(surf, lab, (x, base), 15, C_MUTED)
        x += ui.font(15).size(lab)[0] + 24
    ui.text(surf, "Total", (L.x + 26, L.bottom - 48), 24, C_TEXT, bold=True)
    ui.text(surf, money(s["earnings"]), (L.right - 26, L.bottom - 48), 26, C_GOLD, bold=True, right=True)

    # --- bolsa, dinheiro e o novo dia ---------------------------------------
    R = pygame.Rect(L.right + 20, 112, SCREEN_W - 90 - L.right - 20, 400)
    ui.panel(surf, R)
    a, b = s["stock"]
    up = b >= a
    col = C_GREEN if up else C_RED
    ui.text(surf, "Ação LCORP", (R.x + 24, R.y + 18), 20, C_LILAC, bold=True)
    ui.text(surf, f"$ {b:.2f}".replace(".", ","), (R.x + 24, R.y + 48), 34, C_TEXT, bold=True)
    ax, ay = R.right - 40, R.y + 68
    if up:
        pygame.draw.polygon(surf, col, [(ax - 12, ay + 7), (ax + 12, ay + 7), (ax, ay - 9)])
    else:
        pygame.draw.polygon(surf, col, [(ax - 12, ay - 7), (ax + 12, ay - 7), (ax, ay + 9)])
    sign = "+" if up else ""
    pct = (b - a) / a * 100 if a else 0
    ui.text(surf, f"{sign}{b - a:.2f} ({sign}{pct:.1f}%)  ontem $ {a:.2f}".replace(".", ","), (R.x + 24, R.y + 92),
            16, col)
    surf.fill((80, 60, 110), (R.x + 20, R.y + 126, R.w - 40, ui.U))
    ui.text(surf, "Dinheiro", (R.x + 24, R.y + 140), 20, C_LILAC, bold=True)
    ui.text(surf, money(g.money), (R.x + 24, R.y + 168), 30, C_GOLD, bold=True)
    if g.shares:
        ui.text(surf, f"{g.shares} ações = {money(int(g.shares * b))}", (R.x + 24, R.y + 204), 16, C_MUTED)
    surf.fill((80, 60, 110), (R.x + 20, R.y + 236, R.w - 40, ui.U))
    ui.text(surf, "Novo dia", (R.x + 24, R.y + 250), 20, C_LILAC, bold=True)
    ui.text(surf, g.date_label(short=True), (R.x + 24, R.y + 280), 19, C_TEXT)
    from . import seasons
    if g.weather == "chuva":
        snow = seasons.CURRENT.get("season") == "winter"
        kind, label = ("snow", "Neve") if snow else (("storm", "Tempestade") if getattr(g, "storm", False)
                                                      else ("rain", "Chuva"))
    else:
        kind, label = "sun", "Sol"
    ui.draw_weather_icon(surf, (R.right - 52, R.y + 300), kind, False, pygame.time.get_ticks())
    ui.text(surf, label, (R.x + 24, R.y + 308), 17, C_MUTED)
    ui.text(surf, f"Energia: {int(g.energy)}/{g.max_energy}", (R.x + 24, R.y + 344), 17, C_GREEN)

    # --- avisos da noite ------------------------------------------------------
    notes = s["notes"]
    yy, shown = 526, 0
    for msg, color in notes:
        lines = ui.wrap(msg, 17, SCREEN_W - 220)
        if yy + 23 * len(lines) > SCREEN_H - 84:
            break
        for line in lines:
            ui.text(surf, line, (SCREEN_W // 2, yy), 17, color, center=True)
            yy += 23
        yy += 3
        shown += 1
    if shown < len(notes):
        ui.text(surf, f"+ {len(notes) - shown} avisos (V)", (SCREEN_W // 2, yy), 15, C_MUTED, center=True)

    # --- botões ---------------------------------------------------------------
    blink = int(g.t * 2) % 2 == 0
    _button(surf, pygame.Rect(SCREEN_W // 2 - 380, SCREEN_H - 66, 360, 44), "V", "Ver vendas e avisos",
            bool(s["table"] or s["notes"]), g.t)
    _button(surf, pygame.Rect(SCREEN_W // 2 + 20, SCREEN_H - 66, 360, 44), "Enter", "Começar o novo dia", blink, g.t)
    ui.text(surf, "Jogo salvo.", (SCREEN_W - 24, SCREEN_H - 24), 14, C_MUTED, right=True)

"""Habilidades da Letícia: pesca, ciência, culinária e carisma sobem de nível com o uso.

Cada uma vai do nível 0 ao 5 (`LEVELS` = experiência total para cada nível). A experiência vem de `gain(g, chave,
pontos)`, chamado pelo Game: peixe pescado, dia de bancada, produto lançado, prato cozido, conversa e presente.
Os bônus são pequenos e valem desde o nível 1 (`fish_bar`, `work_energy`, `food_mult`, `talk_mult`, `gift_mult`);
no nível 5 cada habilidade dá um bônus extra no preço (`sell_mult`) ou nos presentes. O painel fica no celular (T).
"""
import pygame

from . import audio, ui
from .config import C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC

LEVELS = (60, 180, 400, 750, 1200)            # experiência total para chegar a cada nível (1..5)
MAX_LEVEL = len(LEVELS)

SKILLS = {
    "pesca": dict(name="Pesca", color=(110, 190, 240), icon="peixe",
                  how="Pescar no píer, no lago e no alto-mar.",
                  perk="Barra de captura 6% maior por nível; a cada 2 níveis a linha vai 1 tile mais longe.",
                  top="Nível 5: peixes valem 10% a mais."),
    "ciencia": dict(name="Ciência", color=(190, 130, 255), icon="frasco",
                    how="Trabalhar nas bancadas e lançar produtos.",
                    perk="A bancada gasta 6% menos energia por nível.",
                    top="Nível 5: produtos valem 10% a mais."),
    "culinaria": dict(name="Culinária", color=(255, 170, 90), icon="panela",
                      how="Cozinhar no fogão.",
                      perk="Comida dá 5% mais energia por nível.",
                      top="Nível 5: pratos valem 15% a mais."),
    "carisma": dict(name="Carisma", color=(255, 130, 170), icon="balao",
                    how="Conversar e dar presentes.",
                    perk="Conversas rendem 5% mais amizade por nível.",
                    top="Nível 5: presentes rendem 10% mais amizade."),
}
ORDER = list(SKILLS)
TITLES = ("Iniciante", "Curiosa", "Dedicada", "Experiente", "Especialista", "Mestra")


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.skills = {k: 0 for k in SKILLS}


def save_state(g):
    return {"skills": dict(g.skills)}


def load_state(g, d):
    init_state(g)
    for k, v in (d.get("skills") or {}).items():
        if k in g.skills:
            g.skills[k] = max(0, int(v))


def level(g, key):
    xp = getattr(g, "skills", {}).get(key, 0)
    return sum(1 for t in LEVELS if xp >= t)


def progress(g, key):
    """(xp dentro do nível, xp que o nível pede); no nível máximo devolve (1, 1)."""
    lv = level(g, key)
    if lv >= MAX_LEVEL:
        return 1, 1
    xp = g.skills.get(key, 0)
    lo = LEVELS[lv - 1] if lv else 0
    return xp - lo, LEVELS[lv] - lo


def gain(g, key, pts):
    if key not in SKILLS or pts <= 0 or not hasattr(g, "skills"):
        return
    before = level(g, key)
    g.skills[key] = g.skills.get(key, 0) + int(pts)
    after = level(g, key)
    if after > before:
        s = SKILLS[key]
        audio.sfx("reward")
        g.toasts.push(f"{s['name']} subiu para o nível {after} ({TITLES[after]})! "
                      + (s["top"] if after == MAX_LEVEL else s["perk"]), s["color"])
        if hasattr(g, "player_emote"):
            g.player_emote = dict(kind="estrela", t=0.0)


# ---------------------------------------------------------------------------
# Bônus (chamados pelo Game)
# ---------------------------------------------------------------------------
def fish_bar(g, bar):
    return int(bar * (1 + 0.06 * level(g, "pesca")))


def work_energy(g, cost):
    return max(1, int(round(cost * (1 - 0.06 * level(g, "ciencia")))))


def food_mult(g):
    return 1 + 0.05 * level(g, "culinaria")


def talk_mult(g):
    return 1 + 0.05 * level(g, "carisma")


def gift_mult(g):
    return 1.10 if level(g, "carisma") >= MAX_LEVEL else 1.0


def sell_mult(g, kind):
    if kind == "fish" and level(g, "pesca") >= MAX_LEVEL:
        return 1.10
    if kind == "product" and level(g, "ciencia") >= MAX_LEVEL:
        return 1.10
    if kind == "dish" and level(g, "culinaria") >= MAX_LEVEL:
        return 1.15
    return 1.0


# ---------------------------------------------------------------------------
# Ícones das habilidades (desenhados com pygame, sem caracteres especiais)
# ---------------------------------------------------------------------------
def draw_icon(surf, key, x, y, k=3):
    s = SKILLS[key]
    c = s["color"]
    dark = tuple(max(0, v - 90) for v in c)

    def R(px, py, w, h, col):
        pygame.draw.rect(surf, col, (x + px * k, y + py * k, w * k, h * k))
    icon = s["icon"]
    if icon == "peixe":
        R(2, 4, 7, 4, c); R(1, 5, 1, 2, c); R(9, 3, 1, 6, c); R(10, 2, 1, 2, c); R(10, 8, 1, 2, c)
        R(3, 5, 1, 1, dark); R(5, 4, 3, 1, (230, 245, 255))
    elif icon == "frasco":
        R(4, 1, 4, 1, dark); R(5, 2, 2, 3, (220, 230, 240)); R(3, 5, 6, 5, (220, 230, 240))
        R(4, 7, 4, 3, c); R(5, 6, 1, 1, c)
    elif icon == "panela":
        R(2, 5, 8, 4, c); R(1, 5, 1, 1, dark); R(10, 5, 1, 1, dark); R(2, 4, 8, 1, dark); R(5, 3, 2, 1, dark)
        R(4, 1, 1, 2, (230, 230, 240)); R(7, 0, 1, 2, (230, 230, 240))
    else:
        R(1, 2, 10, 6, c); R(3, 8, 2, 2, c); R(3, 4, 1, 1, dark); R(6, 4, 1, 1, dark); R(9, 4, 1, 1, dark)


def draw_panel(surf, g, rect):
    """Lista das 4 habilidades com barra de progresso (usada no app do celular)."""
    y = rect.y
    for key in ORDER:
        s = SKILLS[key]
        lv = level(g, key)
        box = pygame.Rect(rect.x, y, rect.w, 92)
        ui.box(surf, box, (34, 24, 50))
        draw_icon(surf, key, box.x + 10, box.y + 12, 3)
        ui.text(surf, s["name"], (box.x + 52, box.y + 6), 20, C_TEXT, bold=True)
        ui.text(surf, f"Nível {lv}  ·  {TITLES[lv]}", (box.right - 10, box.y + 9), 15, s["color"], right=True)
        cur, need = progress(g, key)
        bar = pygame.Rect(box.x + 52, box.y + 34, box.w - 132, 10)
        ui.slot(surf, bar, fill=(18, 12, 28))
        fill = bar.inflate(-4, -4)
        fill.w = int(fill.w * min(1.0, cur / need))
        if fill.w > 0:
            pygame.draw.rect(surf, s["color"], fill)
        txt = "nível máximo" if lv >= MAX_LEVEL else f"{cur}/{need}"
        ui.text(surf, txt, (box.right - 10, box.y + 30), 13, C_MUTED, right=True)
        ui.text(surf, s["how"], (box.x + 52, box.y + 48), 13, C_MUTED)
        ui.text(surf, s["top"] if lv >= MAX_LEVEL else s["perk"], (box.x + 52, box.y + 66), 13,
                C_GOLD if lv >= MAX_LEVEL else C_LILAC)
        y += 98
    return y

"""Brinquedoteca da pediatria no saguão do Conti Moretti e o voluntariado da Letícia.

O cantinho fica no saguão, à direita da recepção (x 19..24, y 12..14): tapete de EVA, mesinha com giz de cera, baú
de brinquedos e a placa da pediatria. Crianças internadas brincam ali em alguns horários (trabalhadores de crowd.py).

No baú (24,12), das 9h às 19h, uma vez por dia: contar uma história (-10 de energia) ou levar um doce/brinquedo da
mochila. Dá amizade com as cinco médicas (mais com doce e ainda mais com pelúcia), carisma e conta visitas. Na 5ª
visita as crianças dão um porta-retrato com um desenho delas. A 1ª e a 5ª visita viram manchete da CatCo.

Estado em `g.pediatria` (visits, last).
"""
import random

import pygame

from . import art, world, audio, habilidades, noticias, ui
from .art import new, R, P, shade
from .config import C_GREEN, C_GOLD, C_MUTED, C_PINK
from .characters import DOCTOR_KEYS, NPCS
from .data import ITEMS

OPEN = (9 * 60, 19 * 60)
STORY_ENERGY = 10
GIFTS = ["pelucia", "rosquinha", "croissant", "tiramisu", "chocolate", "bolo", "torta_morango", "chocolate_belga",
         "macarons", "torta_abobora", "chocolate_quente"]
DRAWING_AT = 5            # visitas para ganhar o desenho
KID_NAMES = ["a Bia", "o Davi", "o Juninho", "a Lara", "o Pedrinho"]


# ---------------------------------------------------------------------------
# Arte
# ---------------------------------------------------------------------------
def _tapete_infantil():
    s = new(64, 48)
    cols = [(240, 120, 120), (250, 200, 90), (120, 200, 140), (110, 170, 230), (190, 140, 220)]
    for ty in range(3):
        for tx in range(4):
            c = cols[(tx + ty * 2) % len(cols)]
            R(s, c, tx * 16, ty * 16, 16, 16)
            R(s, shade(c, 1.12), tx * 16, ty * 16, 16, 1)
            R(s, shade(c, 0.85), tx * 16, ty * 16 + 15, 16, 1)
            R(s, shade(c, 0.85), tx * 16 + 15, ty * 16, 1, 16)
            # encaixe de quebra-cabeça e uma letrinha em relevo
            R(s, shade(c, 0.9), tx * 16 + 6, ty * 16 + 15, 4, 1)
            lc = shade(c, 1.25)
            R(s, lc, tx * 16 + 6, ty * 16 + 5, 1, 6); R(s, lc, tx * 16 + 9, ty * 16 + 5, 1, 6)
            R(s, lc, tx * 16 + 6, ty * 16 + 5, 4, 1); R(s, lc, tx * 16 + 6, ty * 16 + 8, 4, 1)
    return s


def _mesinha_infantil():
    s = new(32, 20)
    top = (250, 230, 140)
    R(s, (230, 120, 110), 3, 10, 2, 9); R(s, (110, 170, 230), 27, 10, 2, 9)          # pés coloridos
    R(s, (120, 200, 140), 3, 16, 2, 3); R(s, (190, 140, 220), 27, 16, 2, 3)
    R(s, top, 1, 5, 30, 6)
    R(s, shade(top, 1.1), 1, 5, 30, 1)
    R(s, shade(top, 0.8), 1, 10, 30, 1)
    R(s, (250, 250, 252), 4, 4, 9, 6)                                             # desenho: casinha e sol
    R(s, (230, 90, 90), 6, 6, 3, 3); P(s, (250, 200, 60), 11, 5)
    R(s, (250, 250, 252), 16, 5, 8, 5)                                            # desenho: coração
    P(s, (230, 80, 120), 19, 6); P(s, (230, 80, 120), 21, 6); R(s, (230, 80, 120), 19, 7, 3, 1)
    P(s, (230, 80, 120), 20, 8)
    for i, c in enumerate([(230, 60, 60), (60, 120, 220), (60, 170, 80), (240, 190, 40)]):   # giz de cera
        R(s, c, 25 + i, 6 + (i % 2), 1, 3)
    return s


def _bau_brinquedos():
    s = new(16, 24)
    wood = (200, 130, 80)
    R(s, (70, 50, 40), 2, 2, 12, 2)                                              # tampa aberta
    R(s, shade(wood, 0.9), 2, 3, 12, 4)
    R(s, (120, 80, 50), 2, 9, 12, 1)
    pygame.draw.circle(s, (170, 110, 70), (6, 9), 3)                            # ursinho espiando
    P(s, (170, 110, 70), 4, 6); P(s, (170, 110, 70), 8, 6)
    P(s, (30, 20, 20), 5, 9); P(s, (30, 20, 20), 7, 9)
    pygame.draw.circle(s, (230, 70, 70), (11, 9), 2)                            # bola
    P(s, (250, 250, 250), 10, 8)
    R(s, wood, 1, 10, 14, 12)
    R(s, shade(wood, 1.15), 1, 10, 14, 1)
    R(s, shade(wood, 0.8), 1, 21, 14, 1)
    for i, c in enumerate([(240, 90, 90), (250, 200, 80), (110, 170, 230)]):     # bloquinhos pintados
        R(s, c, 3 + i * 4, 13, 3, 3)
        P(s, shade(c, 1.3), 3 + i * 4, 13)
    R(s, (60, 40, 30), 2, 22, 2, 2); R(s, (60, 40, 30), 12, 22, 2, 2)
    return s


def _placa_pediatria():
    s = new(16, 30)
    R(s, (150, 156, 166), 7, 14, 2, 14)
    R(s, (120, 126, 136), 4, 27, 8, 2)
    R(s, (18, 63, 53), 1, 2, 14, 13)                                             # verde do Conti Moretti
    R(s, (251, 250, 248), 2, 3, 12, 11)
    for i, c in enumerate([(230, 80, 80), (250, 170, 60), (250, 220, 80), (110, 190, 120), (90, 150, 230)]):
        pygame.draw.arc(s, c, (3 + i // 2, 5 + i, 10 - i, 10 - i), 0, 3.15, 1)   # arco-íris
    P(s, (230, 80, 120), 7, 11); P(s, (230, 80, 120), 9, 11); R(s, (230, 80, 120), 7, 12, 3, 1)
    P(s, (230, 80, 120), 8, 13)
    return s


art.OBJECT_BUILDERS.update({"tapete_infantil": _tapete_infantil, "mesinha_infantil": _mesinha_infantil,
                            "bau_brinquedos": _bau_brinquedos, "placa_pediatria": _placa_pediatria})
world.OBJECT_DEFS.update({"tapete_infantil": (4, 3, False, "decal"), "mesinha_infantil": (2, 1, True, "obj"),
                          "bau_brinquedos": (1, 1, True, "obj"), "placa_pediatria": (1, 1, True, "obj")})

FLAVOR = {
    "mesinha_infantil": "Desenhos de giz de cera: uma casinha, um sol de óculos e uma moça de cabelo comprido escrito "
                        "\"TIA LETÍSSIA\".",
    "placa_pediatria": "Brinquedoteca da Pediatria. \"Aqui dentro a gente brinca, lá fora a gente sara.\"",
    "tapete_infantil": "Tapete de EVA em pecinhas de quebra-cabeça. Falta o \"Q\". Ninguém sabe onde está.",
}


def furnish(m):
    """Cantinho da pediatria no saguão do hospital (chamado por world.build_hospital)."""
    m.add("tapete_infantil", 20, 12)
    m.add("mesinha_infantil", 21, 13)
    m.add("bau_brinquedos", 24, 12)
    m.add("placa_pediatria", 19, 12)


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.pediatria = dict(visits=0, last=-1)


def save_state(g):
    return {"pediatria": g.pediatria}


def load_state(g, d):
    init_state(g)
    for k, v in (d.get("pediatria") or {}).items():
        if k in g.pediatria:
            g.pediatria[k] = v


# ---------------------------------------------------------------------------
# Voluntariado
# ---------------------------------------------------------------------------
def _open(g):
    return OPEN[0] <= g.minutes < OPEN[1]


def object_label(g, o):
    if o.kind != "bau_brinquedos":
        return None
    if _open(g) and g.pediatria["last"] != g.abs_day():
        return "Brinquedoteca: ser voluntária"
    return "Brinquedoteca"


def _gifts_in_bag(g):
    seen = []
    for s in g.inventory:
        if s and s[0] in GIFTS and s[0] not in seen:
            seen.append(s[0])
    return seen


def use_object(g, o):
    if o.kind != "bau_brinquedos":
        return False
    if not _open(g):
        g.say("A brinquedoteca abre das 9h às 19h. As crianças estão dormindo, ou fingindo.")
        return True
    if g.pediatria["last"] == g.abs_day():
        g.say("Você já passou na brinquedoteca hoje. As crianças ainda estão falando disso.")
        return True
    gifts = _gifts_in_bag(g)
    opts = [f"Contar uma história (-{STORY_ENERGY} de energia)"]
    opts += [f"Levar {ITEMS[k]['name']}" for k in gifts[:4]]
    opts.append("Agora não")
    audio.sfx("confirm")

    def pick(i):
        if i == 0:
            if g.energy < STORY_ENERGY:
                g.say("Você está cansada demais para fazer as vozes dos personagens hoje.")
                return
            g.energy -= STORY_ENERGY
            _visit(g, None)
        elif i <= len(gifts[:4]):
            _visit(g, gifts[i - 1])
    q = "Brinquedoteca da pediatria. Como você quer ajudar?"
    if not gifts:
        q += " (doces e pelúcias da mochila também alegram o dia)"
    g.push(ui.Choice(q, opts, pick))
    return True


STORY = [
    "Você conta a história de uma cientista que inventou um guarda-chuva que não vira. As crianças pedem a versão "
    "com dragão.",
    "Você lê \"O Pequeno Príncipe\" fazendo uma voz diferente para a raposa. {kid} chora um pouquinho e diz que é "
    "alergia.",
    "Você inventa uma história sobre um peixe lendário do Parque Central. {kid} jura que já viu o peixe.",
    "Você conta como era a Luthor Corp quando era só uma garagem. {kid} quer saber se tinha robô. Tinha um.",
]
GIFT_LINES = [
    "{kid} divide o presente com todo mundo sem ninguém pedir. As enfermeiras se olham, emocionadas.",
    "{kid} arregala os olhos: \"É PRA MIM?\" A brinquedoteca inteira ouve.",
    "{kid} esconde o presente embaixo da blusa \"para não acabar\". Depois mostra para todas as médicas.",
]
DOCTOR_LINES = {
    "izzie": "Elas ficam tão felizes quando você vem. Eu também. Não conta para ninguém.",
    "addison": "Hoje ninguém reclamou de remédio. Isso é obra sua, não minha.",
    "meredith": "Dia ruim aqui dentro vira dia bom quando a brinquedoteca enche. Obrigada.",
    "yang": "Estatisticamente, criança feliz recupera mais rápido. Então isso aqui é medicina. Continue.",
    "milany": "Você sempre foi boa com crianças. Desde quando a gente era uma.",
}


def _cap(s):
    return s[:1].upper() + s[1:]


def _visit(g, item):
    kid = random.choice(KID_NAMES)
    pts = 25
    if item:
        g.remove_item(item)
        pts = 60 if item == "pelucia" else 40
        lines = [random.choice(GIFT_LINES).format(kid=_cap(kid))]
    else:
        lines = [random.choice(STORY).format(kid=_cap(kid))]
    for k in DOCTOR_KEYS:
        if k in g.npcs:
            g.add_friendship(k, pts)
    habilidades.gain(g, "carisma", 12 if not item else 18)
    p = g.pediatria
    p["visits"] += 1
    p["last"] = g.abs_day()
    if p["visits"] == 1 or p["visits"] == DRAWING_AT:
        noticias.event(g, "pediatria")
    here = [k for k in ("izzie", "addison", "meredith", "yang", "milany") if k in g.npcs
            and g.npcs[k].map == "hospital"]
    audio.sfx("love")
    g.player_emote = dict(kind="coracao", t=0.0)
    if here:
        doc = g.npcs[here[0]]
        lines.append(f"{doc.data['short']}: \"{DOCTOR_LINES[here[0]]}\"")
    g.push(ui.Dialog("Brinquedoteca", lines))
    g.toasts.push(f"Voluntariado na pediatria: +{pts} de amizade com as médicas.", C_PINK)
    if p["visits"] == DRAWING_AT:
        if g.add_item("porta_retrato"):
            g.toasts.push("As crianças te deram um porta-retrato com um desenho delas!", C_GOLD, "porta_retrato")
        g.flags.add("pediatria_amiga")

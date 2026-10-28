"""Presentes extras: itens novos nas lojas e o que cada personagem acha deles.

Cada personagem tem gostos próprios (ama / gosta / não gosta); o que não está listado é neutro.
Presente amado mostra o retrato tímido e presente ruim, o retrato "ruim".
"""
import pygame

from . import art
from .art import new, R, P, shade, mix
from .data import ITEMS, SHOPS
from .characters import NPCS


def _gift(name, price, icon, color, desc):
    return dict(name=name, kind="gift", price=price, icon=icon, color=color, desc=desc)


NEW_GIFTS = {
    "chocolate_belga": _gift("Chocolate Belga", 45, "chocbox", (110, 60, 40), "Uma caixinha de bombons finos."),
    "cha_ervas": _gift("Chá de Ervas", 30, "tea", (120, 170, 90), "Camomila, cidreira e hortelã. Acalma até CEO."),
    "caneca_lcorp": _gift("Caneca Luthor Corp", 25, "mug", (138, 0, 230), "Roxa, com o logo da empresa. Clássica."),
    "orquidea": _gift("Orquídea Branca", 85, "orchid", (245, 240, 250), "Elegante e difícil de matar. Quase."),
    "suculenta": _gift("Vasinho de Suculenta", 30, "succulent", (110, 170, 110), "Pequena, fofa e quase imortal."),
    "perfume": _gift("Perfume Italiano", 160, "perfume", (230, 170, 200), "Notas de bergamota e jasmim."),
    "vinil": _gift("Disco de Vinil", 70, "vinyl", (40, 36, 44), "Um clássico dos anos 80, remasterizado."),
    "aquarela": _gift("Aquarela da Orla", 120, "canvas", (120, 180, 230), "O farol e o píer ao pôr do sol."),
    "pelucia": _gift("Gatinho de Pelúcia", 40, "plush", (240, 170, 90), "Macio e de olhos enormes."),
    "filme_foto": _gift("Filme Fotográfico", 35, "film", (230, 190, 60), "Filme 35 mm para câmera analógica."),
    "camisa_milan": _gift("Camisa do Milan", 110, "jersey", (200, 30, 40), "Rossonera, temporada 2034."),
    "luvas_vela": _gift("Luvas de Vela", 60, "gloves", (40, 60, 110), "Luvas de couro para velejar."),
}
ITEMS.update(NEW_GIFTS)

# onde comprar
for shop, items in {"cafe": ["chocolate_belga", "cha_ervas", "caneca_lcorp"],
                    "market": ["orquidea", "suculenta", "perfume"],
                    "books": ["vinil", "aquarela", "pelucia", "filme_foto"],
                    "bar": ["camisa_milan"],
                    "bait": ["luvas_vela"]}.items():
    for it in items:
        if it not in SHOPS[shop]["stock"]:
            SHOPS[shop]["stock"].append(it)

# gostos de cada personagem (o que não aparece é neutro)
TASTES = {
    "sam": dict(love=["perfume"], like=["orquidea", "chocolate_belga", "caneca_lcorp"], dislike=["pelucia"]),
    "brainy": dict(love=["cha_ervas", "vinil"], like=["suculenta", "caneca_lcorp"], dislike=["perfume"]),
    "jess": dict(love=["caneca_lcorp", "orquidea"], like=["chocolate_belga", "suculenta", "pelucia"],
                 dislike=["luvas_vela"]),
    "rafa": dict(love=["vinil", "chocolate_belga"], like=["cha_ervas", "caneca_lcorp"], dislike=["perfume"]),
    "lucy": dict(love=["aquarela"], like=["vinil", "chocolate_belga", "filme_foto"], dislike=["pelucia"]),
    "vittoria": dict(love=["camisa_milan", "perfume"], like=["orquidea", "chocolate_belga"],
                     dislike=["caneca_lcorp"]),
    "nia": dict(love=["aquarela", "pelucia"], like=["cha_ervas", "vinil"], dislike=["luvas_vela"]),
    "barry": dict(love=["filme_foto"], like=["chocolate_belga", "vinil", "pelucia"], dislike=["perfume"]),
    "theo": dict(love=["aquarela"], like=["cha_ervas", "vinil"], dislike=["caneca_lcorp"]),
    "bea": dict(love=["suculenta", "orquidea"], like=["cha_ervas"], dislike=["perfume"]),
    "graca": dict(love=["orquidea"], like=["chocolate_belga", "cha_ervas", "vinil"], dislike=["filme_foto"]),
    "marco": dict(love=["vinil"], like=["camisa_milan", "chocolate_belga"], dislike=["cha_ervas"]),
    "joca": dict(love=["luvas_vela"], like=["cha_ervas", "caneca_lcorp"], dislike=["perfume"]),
    "ian": dict(love=["luvas_vela", "aquarela"], like=["vinil", "caneca_lcorp"], dislike=["pelucia"]),
    "yang": dict(love=["caneca_lcorp"], like=["chocolate_belga"], dislike=["pelucia", "suculenta"]),
    "meredith": dict(love=["vinil"], like=["cha_ervas", "aquarela"], dislike=["perfume"]),
    "milany": dict(love=["orquidea"], like=["perfume", "cha_ervas"], dislike=["luvas_vela"]),
    "lexie": dict(love=["pelucia"], like=["suculenta", "chocolate_belga"], dislike=["camisa_milan"]),
    "izzie": dict(love=["chocolate_belga"], like=["pelucia", "orquidea"], dislike=["cha_ervas"]),
    "addison": dict(love=["perfume"], like=["orquidea", "aquarela"], dislike=["caneca_lcorp"]),
}
for _k, _t in TASTES.items():
    if _k not in NPCS:
        continue
    gifts = NPCS[_k].setdefault("gifts", {})
    for _kind, _items in _t.items():
        lst = gifts.setdefault(_kind, [])
        for it in _items:
            # um item só pode estar numa categoria
            for other in ("love", "like", "dislike"):
                if other != _kind and it in gifts.get(other, []):
                    gifts[other].remove(it)
            if it not in lst:
                lst.append(it)


# ---------------------------------------------------------------------------
# Ícones (16x16)
# ---------------------------------------------------------------------------
_prev_icon = art._icon


def _icon_gifts(kind, color):
    c = color
    s = new(16, 16)
    if kind == "chocbox":
        R(s, (200, 40, 60), 2, 5, 12, 9)
        R(s, (240, 200, 90), 7, 5, 2, 9); R(s, (240, 200, 90), 2, 8, 12, 2)
        pygame.draw.circle(s, (240, 200, 90), (6, 4), 2); pygame.draw.circle(s, (240, 200, 90), (10, 4), 2)
        R(s, shade((200, 40, 60), 0.7), 2, 13, 12, 1)
    elif kind == "tea":
        R(s, (240, 236, 226), 3, 6, 9, 8)
        R(s, (200, 196, 186), 3, 13, 9, 1)
        pygame.draw.circle(s, (240, 236, 226), (13, 9), 2, 1)
        R(s, c, 4, 7, 7, 2)
        P(s, (230, 230, 230), 6, 3); P(s, (230, 230, 230), 7, 2); P(s, (230, 230, 230), 8, 4)
    elif kind == "mug":
        R(s, c, 3, 4, 9, 10)
        R(s, shade(c, 1.3), 3, 4, 9, 2)
        pygame.draw.circle(s, c, (13, 9), 3, 2)
        R(s, (250, 250, 250), 6, 8, 2, 4); R(s, (250, 250, 250), 6, 11, 4, 1)
    elif kind == "orchid":
        R(s, (90, 150, 80), 7, 7, 2, 7)
        R(s, (190, 120, 80), 4, 12, 8, 4)
        for (x, y) in ((5, 5), (10, 4), (8, 8)):
            pygame.draw.circle(s, c, (x, y), 2)
            P(s, (200, 80, 160), x, y)
    elif kind == "succulent":
        R(s, (190, 110, 80), 4, 10, 8, 5)
        R(s, (210, 130, 96), 3, 9, 10, 2)
        for (x, y, r) in ((8, 7, 3), (5, 8, 2), (11, 8, 2), (8, 4, 2)):
            pygame.draw.circle(s, c, (x, y), r)
        P(s, mix(c, (255, 255, 255), 0.4), 8, 5)
    elif kind == "perfume":
        R(s, (220, 220, 230), 6, 2, 4, 3)
        pygame.draw.rect(s, c, (3, 5, 10, 10), border_radius=2)
        R(s, mix(c, (255, 255, 255), 0.5), 5, 7, 2, 5)
        R(s, (214, 172, 84), 6, 5, 4, 1)
    elif kind == "vinyl":
        pygame.draw.circle(s, (30, 26, 34), (8, 8), 7)
        pygame.draw.circle(s, (60, 56, 66), (8, 8), 5, 1)
        pygame.draw.circle(s, (200, 60, 80), (8, 8), 2)
        P(s, (120, 116, 130), 5, 4)
    elif kind == "canvas":
        R(s, (150, 110, 70), 1, 2, 14, 12)
        R(s, (250, 210, 160), 2, 3, 12, 5)
        R(s, c, 2, 8, 12, 5)
        R(s, (250, 250, 250), 11, 4, 1, 4); R(s, (220, 60, 60), 11, 5, 1, 1)
        R(s, (120, 80, 50), 3, 8, 5, 1)
    elif kind == "plush":
        pygame.draw.circle(s, c, (8, 9), 5)
        pygame.draw.polygon(s, c, [(3, 6), (4, 1), (7, 5)]); pygame.draw.polygon(s, c, [(13, 6), (12, 1), (9, 5)])
        P(s, (40, 30, 30), 6, 9); P(s, (40, 30, 30), 10, 9); P(s, (240, 120, 140), 8, 11)
    elif kind == "film":
        R(s, (40, 40, 46), 3, 3, 10, 11)
        R(s, c, 4, 5, 8, 7)
        R(s, (250, 250, 250), 5, 7, 6, 1)
        R(s, (90, 90, 96), 6, 1, 4, 2)
    elif kind == "jersey":
        pygame.draw.polygon(s, c, [(4, 3), (12, 3), (15, 7), (12, 8), (12, 15), (4, 15), (4, 8), (1, 7)])
        for x in (6, 9):
            R(s, (20, 20, 24), x, 4, 2, 11)
        R(s, (250, 250, 250), 7, 3, 2, 1)
    elif kind == "gloves":
        for x0 in (2, 9):
            R(s, c, x0, 6, 5, 8)
            for k in range(4):
                R(s, c, x0 + k + (1 if k else 0), 3, 1, 4)
            R(s, (214, 172, 84), x0, 12, 5, 1)
    else:
        return _prev_icon(kind, color)
    return s


art._icon = _icon_gifts

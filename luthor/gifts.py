"""Presentes extras: itens novos nas lojas e o que cada personagem acha deles.

Cada personagem tem gostos próprios (ama / gosta / não gosta); o que não está listado é neutro.
Presente amado mostra o retrato tímido e presente ruim, o retrato "ruim".
"""
import pygame

from . import art
from .art import new, R, P, shade, mix
from .data import ITEMS, SHOPS, FORAGE
from .characters import NPCS

# o que cada personagem já não gostava antes desta leva (a fala original de "não gostei" fala desses itens)
_FIRST_DISLIKE = {k: list(v.get("gifts", {}).get("dislike", [])) for k, v in NPCS.items()}


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


# ===========================================================================
# Mais presentes (segunda leva)
# ===========================================================================
MORE_GIFTS = {
    "macarons": _gift("Caixa de Macarons", 50, "g_macaron", (240, 170, 200), "Seis macarons coloridos, delicados."),
    "cafe_especial": _gift("Café Especial em Grãos", 55, "g_coffeebag", (120, 80, 50),
                           "Grãos do sul de Minas, torra média. Cheiro de manhã boa."),
    "vela_aromatica": _gift("Vela Aromática", 40, "g_candle", (240, 200, 160), "Baunilha e lavanda. Acende e relaxa."),
    "lenco_seda": _gift("Lenço de Seda", 95, "g_scarf", (184, 76, 255), "Estampa geométrica, toque macio."),
    "bonsai": _gift("Bonsai", 140, "g_bonsai", (80, 150, 80), "Uma arvorezinha de vinte anos, paciente como ninguém."),
    "mel": _gift("Mel Artesanal", 35, "g_honey", (240, 170, 40), "Pote de mel silvestre do interior."),
    "oculos_sol": _gift("Óculos de Sol", 90, "g_shades", (30, 30, 36), "Armação clássica. Estilo de iate."),
    "caneta_tinteiro": _gift("Caneta-Tinteiro", 130, "g_pen", (40, 50, 90),
                             "Pena de aço e corpo laqueado. Assina contratos com classe."),
    "quebra_cabeca": _gift("Quebra-Cabeça 1000 Peças", 55, "g_puzzle", (110, 170, 230),
                           "O mapa de National City em mil pedacinhos."),
    "jogo_tabuleiro": _gift("Jogo de Tabuleiro", 75, "g_board", (200, 60, 60), "Estratégia, traição e amizades testadas."),
    "kit_pintura": _gift("Kit de Pintura", 65, "g_palette", (230, 200, 150), "Tintas, pincéis e uma tela em branco."),
    "whisky": _gift("Uísque Envelhecido", 180, "g_whisky", (200, 130, 50), "Doze anos em barril de carvalho."),
    "miniatura_veleiro": _gift("Veleiro em Miniatura", 150, "g_ship", (240, 240, 244), "Feito à mão, com velas de linho."),
    "sais_banho": _gift("Sais de Banho", 45, "g_bathsalt", (190, 160, 230), "Lavanda e sal marinho. Banho de spa em casa."),
}
ITEMS.update(MORE_GIFTS)
for shop, items in {"cafe": ["macarons", "cafe_especial"],
                    "market": ["vela_aromatica", "lenco_seda", "bonsai", "mel", "oculos_sol"],
                    "books": ["caneta_tinteiro", "quebra_cabeca", "jogo_tabuleiro", "kit_pintura"],
                    "bar": ["whisky"],
                    "bait": ["miniatura_veleiro"],
                    "pharmacy": ["sais_banho"]}.items():
    for it in items:
        if it not in SHOPS[shop]["stock"]:
            SHOPS[shop]["stock"].append(it)

# ---------------------------------------------------------------------------
# Coletáveis novos (aparecem na praia e no parque como os outros)
# ---------------------------------------------------------------------------
NEW_FORAGE = {
    "pena": dict(name="Pena de Gaivota", value=15, where="beach", weight=34, icon="g_feather", color=(236, 236, 242)),
    "seixo": dict(name="Pedrinha Lisa", value=12, where="beach", weight=30, icon="g_pebble", color=(150, 156, 170)),
    "pinha": dict(name="Pinha", value=18, where="park", weight=30, icon="g_pinecone", color=(140, 96, 60)),
    "dente_leao": dict(name="Dente-de-leão", value=10, where="park", weight=30, icon="g_dandelion",
                       color=(250, 250, 250)),
}
FORAGE.update(NEW_FORAGE)
for _key, _f in NEW_FORAGE.items():
    _where = "praia" if _f["where"] == "beach" else "grama do parque"
    ITEMS[_key] = dict(name=_f["name"], kind="forage", value=_f["value"], icon=_f["icon"], color=_f["color"],
                       desc=f"Achado na {_where}. Vale ${_f['value']}. Dá para vender ou presentear.")

# Gostos com os presentes novos e os coletáveis.
# Coletável é neutro para quase todo mundo; alguns gostam e alguns odeiam (os que aparecem em dislike).
TASTES_2 = {
    "sam": dict(love=["lenco_seda", "caneta_tinteiro"], like=["cafe_especial", "vela_aromatica", "whisky"],
                dislike=["quebra_cabeca", "amora"]),
    "brainy": dict(love=["quebra_cabeca", "bonsai"], like=["jogo_tabuleiro", "caneta_tinteiro", "seixo"],
                   dislike=["oculos_sol", "sais_banho", "pinha"]),
    "jess": dict(love=["vela_aromatica", "macarons"], like=["caneta_tinteiro", "sais_banho", "mel", "dente_leao"],
                 dislike=["whisky", "pinha"]),
    "rafa": dict(love=["cafe_especial"], like=["macarons", "mel", "jogo_tabuleiro"], dislike=["sais_banho", "seixo"]),
    "lucy": dict(love=["caneta_tinteiro", "whisky"], like=["oculos_sol", "cafe_especial", "jogo_tabuleiro"],
                 dislike=["lenco_seda", "seixo"]),
    "vittoria": dict(love=["lenco_seda", "oculos_sol"], like=["macarons", "mel", "vela_aromatica"],
                     dislike=["jogo_tabuleiro", "pena"]),
    "nia": dict(love=["kit_pintura"], like=["macarons", "vela_aromatica", "quebra_cabeca", "dente_leao"],
                dislike=["whisky"]),
    "barry": dict(love=["jogo_tabuleiro"], like=["macarons", "oculos_sol", "cafe_especial", "pena"],
                  dislike=["whisky", "dente_leao"]),
    "theo": dict(love=["caneta_tinteiro", "quebra_cabeca"], like=["cafe_especial", "vela_aromatica", "pinha"],
                 dislike=["oculos_sol", "vidro_mar"]),
    "bea": dict(love=["bonsai", "mel"], like=["vela_aromatica", "kit_pintura", "pinha"],
                dislike=["whisky", "coral", "dente_leao"]),
    "graca": dict(love=["mel"], like=["cafe_especial", "lenco_seda", "vela_aromatica"],
                  dislike=["macarons", "vidro_mar"]),
    "marco": dict(love=["whisky"], like=["jogo_tabuleiro", "oculos_sol"], dislike=["sais_banho", "concha"]),
    "joca": dict(love=["miniatura_veleiro"], like=["mel", "oculos_sol", "seixo"],
                 dislike=["lenco_seda", "estrela_mar", "flor_silvestre"]),
    "ian": dict(love=["miniatura_veleiro", "oculos_sol"], like=["whisky", "cafe_especial", "pena"],
                dislike=["vela_aromatica", "coral", "estrela_mar"]),
    "yang": dict(love=["cafe_especial"], like=["quebra_cabeca", "caneta_tinteiro"],
                 dislike=["vela_aromatica", "sais_banho", "concha", "flor_silvestre"]),
    "meredith": dict(love=["whisky"], like=["vela_aromatica", "mel", "jogo_tabuleiro"], dislike=["macarons"]),
    "milany": dict(love=["macarons"], like=["sais_banho", "lenco_seda", "mel"], dislike=["whisky"]),
    "izzie": dict(love=["mel"], like=["macarons", "kit_pintura", "vela_aromatica"], dislike=["quebra_cabeca", "pena"]),
    "addison": dict(love=["lenco_seda"], like=["whisky", "sais_banho", "oculos_sol"],
                    dislike=["jogo_tabuleiro", "amora"]),
}
for _k, _t in TASTES_2.items():
    if _k not in NPCS:
        continue
    gifts = NPCS[_k].setdefault("gifts", {})
    for _kind, _items in _t.items():
        lst = gifts.setdefault(_kind, [])
        for it in _items:
            for other in ("love", "like", "dislike"):
                if other != _kind and it in gifts.get(other, []):
                    gifts[other].remove(it)
            if it not in lst:
                lst.append(it)


# ---------------------------------------------------------------------------
# Ícones da segunda leva e desenhos dos coletáveis novos no chão
# ---------------------------------------------------------------------------
def _mini_new(kind, c):
    """Coletáveis novos no chão (10x10 de arte)."""
    s = new(10, 10)
    d = shade(c, 0.7)
    if kind == "g_feather":
        pygame.draw.line(s, shade(c, 0.6), (2, 8), (8, 1))
        pygame.draw.polygon(s, c, [(3, 6), (6, 1), (9, 1), (6, 6), (4, 8)])
        P(s, (120, 120, 130), 8, 1)
    elif kind == "g_pebble":
        pygame.draw.ellipse(s, c, (1, 3, 8, 5))
        P(s, shade(c, 1.4), 3, 4)
        P(s, d, 6, 6)
    elif kind == "g_pinecone":
        pygame.draw.ellipse(s, c, (2, 1, 6, 8))
        for y in (3, 5, 7):
            R(s, d, 3, y, 4, 1)
        P(s, (70, 130, 60), 5, 0)
    elif kind == "g_dandelion":
        R(s, (70, 150, 80), 5, 5, 1, 5)
        pygame.draw.circle(s, (210, 210, 220), (5, 3), 3)
        pygame.draw.circle(s, c, (5, 3), 2)
        P(s, (200, 200, 120), 5, 3)
    else:
        return None
    return s


from . import activities  # noqa: E402

_prev_mini = activities._mini


def _mini_all(kind, c):
    m = _mini_new(kind, c)
    return m if m is not None else _prev_mini(kind, c)


activities._mini = _mini_all
_prev_icon2 = art._icon


def _icon_gifts2(kind, color):
    c = color
    m = _mini_new(kind, c)
    s = new(16, 16)
    if m is not None:
        s.blit(pygame.transform.scale(m, (15, 15)), (0, 0))
        return s
    if kind == "g_macaron":
        for i, cc in enumerate(((240, 170, 200), (170, 220, 170), (250, 220, 130))):
            y = 3 + i * 4
            R(s, cc, 4, y, 8, 3)
            R(s, (250, 244, 236), 4, y + 1, 8, 1)
            R(s, shade(cc, 0.8), 4, y + 2, 8, 1)
    elif kind == "g_coffeebag":
        pygame.draw.polygon(s, (200, 170, 120), [(4, 3), (12, 3), (13, 15), (3, 15)])
        R(s, (170, 140, 90), 4, 3, 8, 2)
        R(s, c, 6, 8, 4, 4)
        P(s, (250, 240, 220), 7, 9)
    elif kind == "g_candle":
        R(s, (200, 200, 210), 3, 13, 10, 2)
        R(s, c, 5, 6, 6, 8)
        R(s, shade(c, 1.15), 5, 6, 2, 8)
        R(s, (40, 40, 40), 8, 4, 1, 2)
        pygame.draw.ellipse(s, (255, 190, 60), (7, 1, 3, 4))
    elif kind == "g_scarf":
        pygame.draw.polygon(s, c, [(2, 3), (14, 3), (11, 9), (12, 15), (9, 15), (8, 9)])
        for x in (4, 8, 12):
            P(s, (250, 220, 120), x, 4)
        R(s, shade(c, 0.75), 9, 14, 3, 1)
    elif kind == "g_bonsai":
        R(s, (110, 70, 50), 7, 7, 2, 5)
        R(s, (90, 90, 110), 3, 12, 10, 3)
        for (x, y, r) in ((5, 6, 3), (10, 5, 3), (8, 3, 2)):
            pygame.draw.circle(s, c, (x, y), r)
        P(s, shade(c, 1.4), 9, 3)
    elif kind == "g_honey":
        R(s, (240, 236, 220), 4, 2, 8, 3)
        R(s, (200, 60, 50), 4, 4, 8, 1)
        R(s, c, 3, 5, 10, 10)
        R(s, shade(c, 1.25), 4, 6, 2, 7)
        R(s, (250, 240, 220), 6, 9, 4, 3)
    elif kind == "g_shades":
        for x0 in (1, 9):
            pygame.draw.ellipse(s, c, (x0, 6, 6, 5))
            P(s, (120, 120, 140), x0 + 1, 7)
        R(s, c, 7, 7, 2, 1)
        R(s, c, 0, 6, 1, 2)
        R(s, c, 15, 6, 1, 2)
    elif kind == "g_pen":
        pygame.draw.line(s, c, (3, 13), (12, 4), 3)
        pygame.draw.line(s, (214, 172, 84), (10, 6), (11, 5), 3)
        pygame.draw.polygon(s, (200, 200, 210), [(2, 14), (1, 15), (4, 13), (3, 12)])
    elif kind == "g_puzzle":
        R(s, c, 2, 2, 12, 12)
        R(s, shade(c, 0.7), 8, 2, 1, 12)
        R(s, shade(c, 0.7), 2, 8, 12, 1)
        pygame.draw.circle(s, c, (8, 5), 2)
        pygame.draw.circle(s, c, (5, 8), 2)
        R(s, (250, 210, 120), 9, 9, 5, 5)
    elif kind == "g_board":
        R(s, c, 2, 3, 12, 11)
        R(s, (250, 240, 220), 3, 4, 10, 9)
        for (x, y) in ((4, 5), (8, 5), (6, 7), (10, 7), (4, 9), (8, 9), (6, 11), (10, 11)):
            R(s, shade(c, 0.9), x, y, 2, 2)
        P(s, (60, 120, 220), 5, 6)
    elif kind == "g_palette":
        pygame.draw.ellipse(s, c, (1, 3, 14, 10))
        pygame.draw.circle(s, (0, 0, 0, 0), (10, 10), 2)
        for (x, y, cc) in ((4, 6, (220, 60, 60)), (7, 5, (60, 120, 220)), (10, 6, (250, 210, 60)),
                           (4, 9, (70, 170, 90))):
            pygame.draw.circle(s, cc, (x, y), 1)
    elif kind == "g_whisky":
        R(s, (90, 60, 40), 7, 1, 2, 2)
        R(s, (230, 230, 236), 6, 3, 4, 2)
        R(s, (230, 230, 236), 4, 5, 8, 10)
        R(s, c, 5, 8, 6, 6)
        R(s, (250, 240, 220), 5, 9, 6, 2)
    elif kind == "g_ship":
        pygame.draw.polygon(s, (120, 80, 50), [(2, 11), (14, 11), (12, 14), (4, 14)])
        R(s, (90, 60, 40), 8, 2, 1, 9)
        pygame.draw.polygon(s, c, [(7, 3), (7, 10), (2, 10)])
        pygame.draw.polygon(s, shade(c, 0.9), [(9, 2), (9, 10), (14, 10)])
        R(s, (200, 60, 60), 8, 1, 2, 1)
    elif kind == "g_bathsalt":
        R(s, (240, 240, 246), 5, 1, 6, 2)
        pygame.draw.rect(s, (230, 230, 240), (3, 3, 10, 12), border_radius=2)
        R(s, c, 4, 7, 8, 7)
        for (x, y) in ((5, 8), (8, 10), (10, 8), (6, 12)):
            P(s, (250, 250, 255), x, y)
    else:
        return _prev_icon2(kind, color)
    return s


art._icon = _icon_gifts2


# ---------------------------------------------------------------------------
# Falas de "não gostei" para coletáveis e presentes novos
# (a fala original de cada personagem cita um item específico, então só vale para os itens de antes)
# ---------------------------------------------------------------------------
DISLIKE_LINES = {
    # personagem: (coletável odiado, outro presente que não gostou)
    "sam": ("Você achou isso no chão? ...Vou fingir que veio numa caixinha.",
            "Obrigada, mas não é bem o meu estilo. Fica a intenção."),
    "brainy": ("Um objeto coletado sem critério algum. Vou catalogar. E descartar.",
               "Este presente não tem utilidade mensurável para mim. Mas registro o gesto."),
    "jess": ("Hm... isso estava jogado por aí? Vou guardar na gaveta das coisas estranhas.",
             "Ah... obrigada. Vou achar um lugar pra isso. Um dia."),
    "rafa": ("Você tirou isso do chão, né? Eu trabalho com comida, Letícia. Higiene!",
             "Valeu... mas não tem nada a ver comigo, sabe?"),
    "lucy": ("Isso estava no chão, Luthor? Vou usar de prova num caso de presentes ruins.",
             "Hm. Não é a minha cara. Mas anotei que você tentou."),
    "vittoria": ("Ah... uma lembrancinha da rua. Que... rústico. Grazie, eu acho.",
                 "Não é bem o meu gosto, cara. Mas obrigada pela intenção."),
    "nia": ("Isso me dá uma sensação estranha. Sonhei com algo assim e não foi bom.",
            "Ah... obrigada. Não é muito eu, mas valeu o carinho."),
    "barry": ("Isso aí estava largado na rua? Nem pra foto serve, desculpa.",
              "Hm... não curto muito, mas valeu por lembrar de mim!"),
    "theo": ("Achado ao acaso, hein? Nem todo achado vira uma boa história.",
             "Obrigado... mas esse não entra na minha estante."),
    "bea": ("Ai, isso aí estraga a minha horta! Tira daqui, filha.",
            "Obrigada, querida, mas isso não é pra mim."),
    "graca": ("Coisa do chão na minha cozinha? Nem pensar, filha. Leva lá pra fora.",
              "Ah, minha filha... isso aí não combina comigo. Mas obrigada."),
    "marco": ("Isso aqui é lixo de praia, Letícia. Eu varro isso da porta do bar todo dia.",
              "Hm. Não é a minha praia. Mas valeu."),
    "joca": ("Isso aí é do mar e do mato, moça. Lugar dele é lá, não no meu bolso.",
             "Obrigado, moça, mas isso não serve pra pescaria nenhuma."),
    "ian": ("Chefe, isso devia ter ficado onde estava. A gente protege o mar, lembra?",
            "Valeu, mas não é muito a minha. Fica a intenção."),
    "yang": ("Você me deu uma coisa do chão. Eu sou cirurgiã. Pensa nas bactérias.",
             "Não. Mas obrigada. Agora vai."),
    "meredith": ("Hm... isso me lembra um dia ruim. Mas obrigada por pensar em mim.",
                 "Não é bem o meu tipo de coisa. A intenção conta, viu?"),
    "milany": ("Coisa achada no chão? Por favor, lava as mãos. Médica falando.",
               "Hm... não é bem o meu estilo. Mas obrigada pelo carinho."),
    "izzie": ("Ai, não! Eu tenho pavor disso. Juro que não é frescura!",
              "Ah... obrigada! Não é muito a minha cara, mas obrigada mesmo."),
    "addison": ("Algo que você achou no chão. Que... espontâneo. Não.",
                "Não, querida. Mas aprecio a tentativa."),
}


def dislike_line(key, item):
    """Fala de 'não gostei' certa para o item, ou None para usar a fala original da personagem."""
    lines = DISLIKE_LINES.get(key)
    if not lines or item in _FIRST_DISLIKE.get(key, ()):
        return None
    return lines[0] if ITEMS.get(item, {}).get("kind") == "forage" else lines[1]

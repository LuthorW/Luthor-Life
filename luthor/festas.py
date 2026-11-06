"""Festas das estações, aniversários das personagens e o calendário (tecla C).

- Aniversários: cada personagem faz aniversário num dia do ano. Presente nesse dia vale mais
  (amado x5, gostou x3, neutro x2) e ela usa um balãozinho o dia todo.
- Festas: uma por estação, no estilo das festas do Stardew. A cidade inteira vai, as barracas e enfeites
  aparecem no dia (objetos temporários no mapa da cidade), a anfitriã abre a festa com uma cena e cada
  festa tem uma atividade: dança das flores, sopa do luau, concurso da feira e amigo secreto.
"""
import math
import random

import pygame

from . import art, ui, audio, seasons
from .art import new, R, P, shade, mix
from .config import (TILE, SCALE, SCREEN_W, SCREEN_H, DAYS_PER_QUARTER, WEEKDAYS, HEART_POINTS, C_TEXT, C_MUTED,
                     C_LILAC, C_GOLD, C_GREEN, C_PINK, C_ACCENT, C_ACCENT_2)
from .characters import NPCS, NPC_ORDER, ROMANCES
from .data import ITEMS, FISH
from . import world

FEMALE_WORD = {"brainy": "o", "rafa": "o", "barry": "o", "theo": "o", "marco": "o", "joca": "o", "ian": "o"}


def _g(key):
    """'a' ou 'o', para concordar com quem fala (obrigada / obrigado)."""
    return FEMALE_WORD.get(key, "a")


def season_name(q):
    return seasons.NAMES[seasons.of_quarter(q)]


def fmt_hour(m):
    m %= 24 * 60
    return f"{m // 60}h{m % 60:02d}" if m % 60 else f"{m // 60}h"


# ===========================================================================
# Aniversários
# ===========================================================================
BIRTHDAYS = {   # chave: (trimestre, dia). Nenhum cai em dia de festa (7 e 10 do inverno).
    "meredith": (1, 2), "lucy": (1, 4), "jess": (1, 9), "joca": (1, 12), "bea": (1, 14),
    "ian": (2, 3), "nia": (2, 5), "theo": (2, 9), "vittoria": (2, 11), "izzie": (2, 13),
    "barry": (3, 2), "rafa": (3, 4), "sam": (3, 6), "graca": (3, 10), "milany": (3, 13),
    "brainy": (4, 3), "marco": (4, 6), "addison": (4, 8), "yang": (4, 12),
}
BDAY_MULT = {"love": 5, "like": 3, "neutral": 2, "dislike": 1}

BDAY_CHAT = {
    "sam": "Hoje é meu aniversário! A Ruby me acordou com panqueca queimada e um cartão cheio de glitter. Melhor dia.",
    "brainy": "Hoje completo mais uma volta ao redor do Sol. Estatisticamente irrelevante. Emocionalmente... um pouco relevante.",
    "jess": "É meu aniversário! Eu mesma coloquei na sua agenda, com lembrete três dias antes. Só pra garantir.",
    "rafa": "Aniversário hoje! O pessoal do café escreveu 'parabéns' na espuma de todos os meus cappuccinos.",
    "lucy": "Pois é, hoje é meu aniversário. Não conta pra redação: da última vez cantaram parabéns no meio da reunião de pauta.",
    "vittoria": "Hoje é meu aniversário. A Dona Graça me proibiu de entrar na cozinha da Trattoria. Acho que tem bolo vindo.",
    "nia": "Hoje é meu aniversário! Sonhei que ganhava um presente com laço azul. Vamos ver se meus sonhos acertam de novo.",
    "barry": "Aniversário hoje! Cheguei atrasado na minha própria festa surpresa. Duas vezes. Não me pergunte como.",
    "theo": "Hoje é meu aniversário. Pretendo comemorar do jeito certo: chá, um livro novo e silêncio absoluto.",
    "bea": "É meu aniversário, querida! Os fornecedores mandaram flores. Vendi metade antes do almoço, claro.",
    "graca": "Hoje é meu aniversário, minha filha! Fiz bolo de fubá pra equipe inteira. Aniversariante que se preze cozinha.",
    "marco": "Aniversário hoje. A casa paga uma rodada pra quem souber. Ou seja: pra você, agora.",
    "joca": "Hoje faço aniversário, moça! Pedi de presente um peixe grande. O mar ainda não entregou.",
    "ian": "Aniversário hoje! Lembra do bolo de lama que a gente fez nas férias no interior? Ainda acho que o meu ficou mais bonito.",
    "yang": "É meu aniversário. Não, não vou parar o plantão por isso. Mas aceito café.",
    "meredith": "Hoje é meu aniversário. Ninguém no hospital sabe. Vamos manter assim, tá?",
    "milany": "Hoje é meu aniversário! A equipe da cardio encheu o posto de balões em forma de coração. Literalmente.",
    "izzie": "É meu aniversário! Fiz cupcakes pra ala inteira. Sobrou um. Quer?",
    "addison": "Hoje é meu aniversário. Decidi que este ano eu faço trinta e... bom, eu decidi.",
}

BDAY_GIFT = {
    "love": ["Você lembrou do meu aniversário E acertou no presente? Isso é covardia. Obrigad{g}!",
             "Melhor presente de aniversário que eu ganhei hoje. E olha que a concorrência foi grande!",
             "No meu aniversário? É exatamente o que eu queria. Como você sabia?"],
    "like": ["Um presente de aniversário! Que gentileza. Obrigad{g} por lembrar.",
             "Você lembrou do meu aniversário! Adorei, de verdade."],
    "neutral": ["Ah, um presente de aniversário! Fico feliz que você lembrou.",
                "Que gentil lembrar do meu aniversário. Obrigad{g}!"],
    "dislike": ["Bom... no aniversário o que vale é a intenção, né? Obrigad{g} por lembrar.",
                "Não é bem o meu estilo... mas você lembrou do meu aniversário, e isso conta."],
}


def birthday_keys(q, d):
    return [k for k in NPC_ORDER if BIRTHDAYS.get(k) == (q, d)]


def birthday_today(g):
    return birthday_keys(g.quarter, g.day)


def is_birthday(g, key):
    return BIRTHDAYS.get(key) == (g.quarter, g.day)


def birthday_label(key):
    q, d = BIRTHDAYS[key]
    return f"{d} de {season_name(q)}"


def _names(keys):
    names = [NPCS[k]["short"] for k in keys]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " e " + names[-1]


# ===========================================================================
# Itens novos (barracas das festas e o porta-retrato do aniversário de namoro)
# ===========================================================================
NEW_ITEMS = {
    "coroa_flores": dict(name="Coroa de Flores", kind="gift", price=60, icon="flowercrown", color=(245, 140, 190),
                         desc="Trançada na Festa das Flores. Fica linda em qualquer cabeça."),
    "agua_coco": dict(name="Água de Coco", kind="food", energy=30, price=15, icon="coconut", color=(120, 80, 50),
                      desc="+30 de energia. Gelada, direto do coco. Aperte F para beber."),
    "torta_abobora": dict(name="Torta de Abóbora", kind="food", energy=60, price=70, icon="pie", color=(232, 140, 50),
                          desc="+60 de energia. A receita campeã da Feira da Colheita."),
    "chocolate_quente": dict(name="Chocolate Quente", kind="food", energy=40, price=25, icon="cocoa",
                             color=(120, 70, 40), desc="+40 de energia. Com chantilly e canela."),
    "porta_retrato": dict(name="Porta-retrato", kind="gift", price=90, icon="frame", color=(214, 172, 84),
                          desc="Uma moldura dourada esperando a foto certa."),
}
ITEMS.update(NEW_ITEMS)

TASTES = {
    "jess": dict(love=["coroa_flores"], like=["chocolate_quente", "porta_retrato"]),
    "nia": dict(love=["coroa_flores"], like=["chocolate_quente", "porta_retrato"]),
    "bea": dict(love=["torta_abobora"], like=["coroa_flores"]),
    "graca": dict(love=["torta_abobora"], like=["agua_coco"]),
    "lucy": dict(love=["porta_retrato"], like=["chocolate_quente", "coroa_flores"]),
    "vittoria": dict(love=["porta_retrato"], like=["coroa_flores"]),
    "brainy": dict(love=["chocolate_quente"]),
    "theo": dict(like=["chocolate_quente", "torta_abobora"]),
    "barry": dict(like=["chocolate_quente", "agua_coco"]),
    "ian": dict(like=["agua_coco"]),
    "joca": dict(like=["agua_coco", "torta_abobora"]),
    "sam": dict(like=["torta_abobora", "porta_retrato"]),
    "izzie": dict(like=["torta_abobora", "coroa_flores"]),
    "milany": dict(like=["coroa_flores"]),
    "meredith": dict(like=["chocolate_quente"]),
    "yang": dict(dislike=["coroa_flores"]),
}
for _k, _t in TASTES.items():
    _gifts = NPCS[_k].setdefault("gifts", {})
    for _kind, _items in _t.items():
        _lst = _gifts.setdefault(_kind, [])
        for _it in _items:
            for _other in ("love", "like", "dislike"):
                if _other != _kind and _it in _gifts.get(_other, []):
                    _gifts[_other].remove(_it)
            if _it not in _lst:
                _lst.append(_it)


# --- ícones -----------------------------------------------------------------
_prev_icon = art._icon


def _icon_festas(kind, color):
    s = new(16, 16)
    c = color
    if kind == "flowercrown":
        pygame.draw.ellipse(s, (90, 150, 70), (1, 5, 14, 8), 2)
        for i, col in enumerate(((245, 140, 190), (255, 220, 90), (255, 255, 255), (190, 140, 240), (245, 140, 190))):
            x = 2 + i * 3
            y = 6 if i in (0, 4) else (5 if i == 2 else 4)
            pygame.draw.circle(s, col, (x, y + 4), 2)
            P(s, (255, 230, 120), x, y + 4)
    elif kind == "coconut":
        pygame.draw.circle(s, (120, 80, 50), (8, 10), 5)
        pygame.draw.circle(s, (150, 104, 66), (7, 9), 3)
        pygame.draw.ellipse(s, (250, 248, 236), (5, 5, 6, 3))
        R(s, (240, 90, 120), 10, 1, 1, 6); R(s, (240, 90, 120), 10, 1, 3, 1)
        P(s, (90, 170, 80), 4, 6); P(s, (90, 170, 80), 3, 5)
    elif kind == "pie":
        pygame.draw.ellipse(s, (214, 168, 100), (1, 6, 14, 8))
        pygame.draw.ellipse(s, c, (3, 6, 10, 5))
        for x in (4, 7, 10):
            P(s, (240, 200, 130), x, 8)
        R(s, shade((214, 168, 100), 0.75), 2, 12, 12, 1)
    elif kind == "cocoa":
        R(s, (230, 226, 216), 3, 6, 9, 8)
        R(s, (196, 190, 180), 3, 13, 9, 1)
        pygame.draw.circle(s, (230, 226, 216), (13, 9), 2, 1)
        R(s, c, 4, 6, 7, 2)
        pygame.draw.ellipse(s, (255, 252, 246), (4, 3, 7, 4))
        P(s, (170, 110, 60), 7, 4)
    elif kind == "frame":
        R(s, c, 2, 2, 12, 12)
        R(s, shade(c, 1.25), 2, 2, 12, 1)
        R(s, (150, 200, 240), 4, 4, 8, 8)
        R(s, (110, 170, 90), 4, 9, 8, 3)
        pygame.draw.circle(s, (255, 230, 120), (9, 6), 1)
        R(s, shade(c, 0.7), 2, 13, 12, 1)
    else:
        return _prev_icon(kind, color)
    return s


art._icon = _icon_festas


# ===========================================================================
# Arte das festas (objetos temporários)
# ===========================================================================
WOOD = (150, 100, 60)


def _barraca(c1, c2, goods, straw=False):
    s = new(32, 40)
    dk = shade(WOOD, 0.7)
    R(s, dk, 2, 12, 2, 28); R(s, dk, 28, 12, 2, 28)
    R(s, WOOD, 0, 26, 32, 12)
    R(s, shade(WOOD, 1.18), 0, 26, 32, 2)
    R(s, shade(WOOD, 0.62), 0, 37, 32, 3)
    for x in (8, 16, 24):
        R(s, dk, x, 28, 1, 9)
    if straw:                                    # telhado de palha (luau)
        for y in range(4, 15):
            w = 32 - abs(9 - y) // 3
            R(s, c1 if y % 2 else c2, (32 - w) // 2, y, w, 1)
        for x in range(1, 31, 3):
            R(s, shade(c1, 0.75), x, 13, 1, 3)
    else:
        R(s, shade(c1, 0.75), 1, 3, 30, 3)
        for i in range(8):
            R(s, c1 if i % 2 == 0 else c2, i * 4, 6, 4, 8)
        for i in range(8):
            pygame.draw.circle(s, c1 if i % 2 == 0 else c2, (i * 4 + 2, 14), 2)
        R(s, shade(c1, 0.8), 0, 5, 32, 1)
    goods(s)
    return s


def _goods_flores(s):
    for i, x in enumerate((3, 9, 15, 21, 27)):
        R(s, (176, 110, 70), x, 23, 3, 3)
        col = ((245, 120, 170), (255, 210, 70), (250, 250, 255), (180, 130, 240), (255, 150, 90))[i]
        pygame.draw.circle(s, (90, 160, 80), (x + 1, 22), 2)
        pygame.draw.circle(s, col, (x + 1, 20), 2)
        P(s, (255, 236, 140), x + 1, 20)


def _goods_luau(s):
    for x in (4, 12, 20):
        pygame.draw.circle(s, (120, 80, 50), (x + 2, 23), 3)
        pygame.draw.ellipse(s, (246, 242, 230), (x, 20, 4, 2))
        R(s, (240, 90, 120), x + 3, 17, 1, 4)
    R(s, (240, 190, 60), 26, 19, 4, 6)                     # abacaxi
    R(s, (200, 150, 40), 26, 21, 4, 1); R(s, (200, 150, 40), 26, 23, 4, 1)
    R(s, (90, 170, 80), 27, 16, 2, 3)


def _goods_feira(s):
    for x in (2, 10):
        pygame.draw.ellipse(s, (232, 130, 40), (x, 20, 7, 6))
        R(s, (90, 130, 60), x + 3, 19, 1, 2)
    R(s, (176, 120, 70), 19, 21, 11, 5)
    for x in (20, 23, 26):
        pygame.draw.circle(s, (220, 50, 60), (x + 1, 21), 2)


def _goods_luzes(s):
    for x in (3, 10, 17, 24):
        R(s, (240, 236, 226), x, 20, 5, 6)
        R(s, (120, 70, 40), x + 1, 20, 3, 1)
        pygame.draw.circle(s, (240, 236, 226), (x + 6, 23), 1)
        P(s, (220, 220, 220), x + 2, 18); P(s, (220, 220, 220), x + 3, 16)
    for i, x in enumerate(range(2, 31, 4)):                # luzinhas no toldo
        P(s, ((255, 220, 90), (240, 90, 110), (110, 200, 255))[i % 3], x, 15)


def _barraca_flores():
    return _barraca((245, 140, 190), (255, 250, 250), _goods_flores)


def _barraca_luau():
    return _barraca((214, 180, 100), (190, 150, 80), _goods_luau, straw=True)


def _barraca_feira():
    return _barraca((236, 140, 50), (255, 244, 220), _goods_feira)


def _barraca_luzes():
    return _barraca((150, 40, 60), (40, 110, 70), _goods_luzes)


def _arco():
    s = new(64, 52)
    white = (244, 240, 232)
    for x in (2, 58):
        R(s, white, x, 14, 4, 38)
        R(s, shade(white, 0.8), x + 3, 14, 1, 38)
        for y in range(18, 50, 6):
            pygame.draw.circle(s, (90, 160, 80), (x + (0 if y % 12 else 4), y), 2)
    rnd = random.Random(7)
    pts = []
    for x in range(2, 62):
        y = 18 - 14 * (1 - ((x - 32) / 30) ** 2)
        pts.append((x, y))
        pygame.draw.circle(s, (80, 150, 70), (x, int(y)), 3)
    for x, y in pts[::2]:
        pygame.draw.circle(s, (100, 176, 84), (x, int(y) - 1), 2)
    flowers = ((245, 120, 170), (255, 220, 80), (255, 255, 255), (190, 140, 240), (255, 150, 90))
    for x, y in pts[1::4]:
        col = rnd.choice(flowers)
        yy = int(y) + rnd.randint(-2, 2)
        pygame.draw.circle(s, col, (x, yy), 2)
        P(s, (255, 236, 140), x, yy)
    return s


def _mastro():
    s = new(16, 62)
    R(s, (244, 240, 232), 7, 8, 2, 52)
    R(s, (200, 194, 186), 8, 8, 1, 52)
    ribbons = ((245, 120, 170), (255, 210, 70), (120, 190, 250), (150, 210, 110))
    for i, col in enumerate(ribbons):
        side = -1 if i % 2 == 0 else 1
        for t in range(0, 26):
            x = 8 + side * (t * (5 + i % 2) // 26)
            y = 9 + t + (i // 2) * 3
            P(s, col, x, y)
            if t % 5 == 0:
                P(s, shade(col, 0.8), x, y + 1)
    pygame.draw.ellipse(s, (90, 150, 70), (3, 4, 10, 6), 2)
    for x, col in ((4, (245, 120, 170)), (8, (255, 220, 80)), (12, (255, 255, 255))):
        pygame.draw.circle(s, col, (x, 6), 2)
    for x, col in ((2, (255, 150, 90)), (6, (190, 140, 240)), (10, (245, 120, 170)), (14, (255, 220, 80))):
        pygame.draw.circle(s, (90, 160, 80), (x, 59), 2)
        P(s, col, x, 58)
    return s


def _vaso():
    s = new(16, 18)
    R(s, (190, 140, 80), 3, 10, 10, 7)
    for y in (11, 13, 15):
        R(s, (160, 112, 60), 3, y, 10, 1)
    R(s, (210, 160, 100), 2, 9, 12, 2)
    for (x, y, col) in ((4, 6, (245, 120, 170)), (8, 4, (255, 220, 80)), (12, 6, (255, 255, 255)),
                        (6, 8, (190, 140, 240)), (10, 8, (255, 150, 90))):
        pygame.draw.circle(s, (90, 160, 80), (x, y + 2), 2)
        pygame.draw.circle(s, col, (x, y), 2)
        P(s, (255, 236, 140), x, y)
    return s


def _fogueira(f=0):
    s = new(16, 22)
    for (x, y) in ((1, 18), (4, 20), (8, 21), (12, 20), (14, 18), (3, 16), (13, 16)):
        pygame.draw.circle(s, (130, 126, 120), (x, y), 2)
        P(s, (160, 156, 150), x - 1, y - 1)
    R(s, (110, 70, 40), 3, 16, 10, 2)
    R(s, (90, 56, 32), 5, 14, 6, 2)
    flick = (0, 1, -1)[f % 3]
    pygame.draw.polygon(s, (240, 110, 40), [(3, 16), (8, 3 + flick), (13, 16)])
    pygame.draw.polygon(s, (255, 190, 60), [(5, 16), (8 + flick, 7), (11, 16)])
    pygame.draw.polygon(s, (255, 244, 170), [(7, 16), (8, 11 - flick), (9, 16)])
    P(s, (255, 200, 80), 4 + f % 3, 4); P(s, (255, 160, 60), 11 - f % 2, 6)
    return s


def _tocha(f=0):
    s = new(16, 32)
    R(s, (170, 130, 70), 7, 10, 2, 22)
    for y in (14, 20, 26):
        R(s, (130, 96, 50), 7, y, 2, 1)
    R(s, (120, 86, 46), 6, 7, 4, 4)
    flick = (0, 1, -1)[f % 3]
    pygame.draw.polygon(s, (240, 110, 40), [(5, 7), (8, 0 + max(0, flick)), (11, 7)])
    pygame.draw.polygon(s, (255, 210, 90), [(7, 7), (8 + flick, 3), (9, 7)])
    return s


def _caldeirao():
    s = new(16, 24)
    R(s, (90, 70, 50), 2, 4, 1, 18); R(s, (90, 70, 50), 13, 4, 1, 18)
    R(s, (90, 70, 50), 2, 4, 12, 1)
    R(s, (110, 70, 40), 4, 20, 8, 2)
    pygame.draw.polygon(s, (255, 160, 60), [(5, 21), (8, 17), (11, 21)])
    pygame.draw.ellipse(s, (40, 38, 44), (3, 9, 10, 10))
    R(s, (40, 38, 44), 3, 9, 10, 4)
    pygame.draw.ellipse(s, (230, 150, 60), (4, 8, 8, 3))
    P(s, (250, 210, 120), 6, 9); P(s, (120, 170, 80), 9, 9)
    R(s, (70, 66, 74), 3, 9, 10, 1)
    for (x, y) in ((6, 5), (7, 3), (9, 6), (10, 4)):
        P(s, (230, 230, 236), x, y)
    return s


def _mesa_concurso():
    s = new(32, 24)
    R(s, (120, 80, 50), 3, 16, 2, 8); R(s, (120, 80, 50), 27, 16, 2, 8)
    R(s, (250, 248, 240), 0, 10, 32, 8)
    R(s, (90, 140, 220), 0, 16, 32, 2)
    for x in range(0, 32, 4):
        R(s, (210, 206, 196), x, 12, 2, 4)
    # troféu
    R(s, (230, 186, 60), 5, 2, 6, 5); R(s, (230, 186, 60), 7, 7, 2, 2); R(s, (200, 150, 40), 5, 9, 6, 1)
    P(s, (255, 240, 160), 6, 3); P(s, (230, 186, 60), 4, 3); P(s, (230, 186, 60), 11, 3)
    # roseta azul
    pygame.draw.circle(s, (70, 120, 220), (24, 6), 4)
    pygame.draw.circle(s, (250, 250, 250), (24, 6), 2)
    R(s, (70, 120, 220), 22, 9, 2, 3); R(s, (70, 120, 220), 25, 9, 2, 3)
    pygame.draw.ellipse(s, (232, 130, 40), (14, 4, 7, 6))
    R(s, (90, 130, 60), 17, 3, 1, 2)
    return s


def _abobora_pilha():
    s = new(16, 16)
    for (x, y, w, h) in ((0, 8, 9, 7), (7, 8, 9, 7), (4, 2, 8, 7)):
        pygame.draw.ellipse(s, (232, 130, 40), (x, y, w, h))
        R(s, (200, 100, 30), x + w // 2, y + 1, 1, h - 2)
        P(s, (255, 180, 90), x + 2, y + 2)
    R(s, (90, 130, 60), 8, 1, 1, 2)
    return s


def _fardo():
    s = new(16, 14)
    R(s, (222, 186, 90), 0, 2, 16, 12)
    R(s, (240, 210, 120), 0, 2, 16, 2)
    for y in (5, 8, 11):
        R(s, (196, 160, 70), 0, y, 16, 1)
    R(s, (150, 110, 60), 4, 2, 1, 12); R(s, (150, 110, 60), 11, 2, 1, 12)
    return s


def _lanterna_festa(f=0):
    s = new(16, 32)
    R(s, (70, 50, 40), 7, 6, 2, 26)
    R(s, (70, 50, 40), 7, 5, 6, 1)
    R(s, (60, 40, 30), 12, 6, 1, 2)
    glow = (240, 70, 60) if f % 2 == 0 else (250, 96, 70)
    pygame.draw.ellipse(s, glow, (9, 8, 7, 9))
    R(s, (60, 40, 30), 10, 8, 5, 1); R(s, (60, 40, 30), 10, 16, 5, 1)
    R(s, (255, 200, 120), 11, 11, 3, 3)
    return s


def _arvore_luzes(f=0):
    s = new(32, 60)
    R(s, (110, 74, 44), 14, 50, 4, 8)
    for i, (y, w) in enumerate(((8, 8), (16, 14), (24, 20), (32, 24), (40, 28))):
        pygame.draw.polygon(s, (40, 110, 70) if i % 2 else (50, 126, 80), [(16, y - 8), (16 - w // 2, y + 10), (16 + w // 2, y + 10)])
    rnd = random.Random(11)
    cols = ((255, 220, 90), (240, 90, 110), (110, 200, 255), (250, 250, 250))
    for i in range(26):
        y = rnd.randint(10, 49)
        half = (y - 2) * 14 // 48
        x = 16 + rnd.randint(-half, half)
        col = cols[(i + f) % len(cols)]
        P(s, col, x, y)
        if (i + f) % 3 == 0:
            P(s, mix(col, (255, 255, 255), 0.5), x, y - 1)
    pygame.draw.polygon(s, (255, 214, 80), [(16, 0), (18, 4), (22, 4), (19, 7), (20, 11), (16, 8), (12, 11), (13, 7), (10, 4), (14, 4)])
    P(s, (255, 250, 200), 16, 4)
    R(s, (150, 40, 60), 10, 56, 12, 4)
    return s


def _mesa_presentes():
    s = new(32, 26)
    R(s, (110, 74, 44), 3, 18, 2, 8); R(s, (110, 74, 44), 27, 18, 2, 8)
    R(s, (160, 40, 60), 0, 12, 32, 8)
    R(s, (130, 30, 50), 0, 18, 32, 2)
    R(s, (230, 190, 90), 0, 12, 32, 1)
    for (x, y, w, h, col) in ((2, 4, 7, 8, (70, 140, 220)), (10, 6, 6, 6, (250, 250, 250)),
                              (17, 2, 7, 10, (90, 170, 100)), (25, 6, 6, 6, (240, 200, 70))):
        R(s, col, x, y, w, h)
        R(s, (220, 50, 70) if col != (240, 200, 70) else (150, 40, 60), x + w // 2, y, 1, h)
        R(s, (220, 50, 70) if col != (240, 200, 70) else (150, 40, 60), x, y + h // 2, w, 1)
        P(s, (220, 50, 70), x + w // 2 - 1, y - 1); P(s, (220, 50, 70), x + w // 2 + 1, y - 1)
    return s


art.OBJECT_BUILDERS.update({
    "barraca_flores": _barraca_flores, "barraca_luau": _barraca_luau, "barraca_feira": _barraca_feira,
    "barraca_luzes": _barraca_luzes, "festa_arco": _arco, "festa_mastro": _mastro, "festa_vaso": _vaso,
    "fogueira": _fogueira, "tocha": _tocha, "caldeirao": _caldeirao, "mesa_concurso": _mesa_concurso,
    "abobora_pilha": _abobora_pilha, "fardo": _fardo, "lanterna_festa": _lanterna_festa,
    "arvore_luzes": _arvore_luzes, "mesa_presentes": _mesa_presentes,
})
world.OBJECT_DEFS.update({
    "barraca_flores": (2, 1, True, "obj"), "barraca_luau": (2, 1, True, "obj"), "barraca_feira": (2, 1, True, "obj"),
    "barraca_luzes": (2, 1, True, "obj"), "festa_arco": (4, 1, False, "obj"), "festa_mastro": (1, 1, True, "obj"),
    "festa_vaso": (1, 1, True, "obj"), "fogueira": (1, 1, True, "obj"), "tocha": (1, 1, True, "obj"),
    "caldeirao": (1, 1, True, "obj"), "mesa_concurso": (2, 1, True, "obj"), "abobora_pilha": (1, 1, True, "obj"),
    "fardo": (1, 1, True, "obj"), "lanterna_festa": (1, 1, True, "obj"), "arvore_luzes": (2, 1, True, "obj"),
    "mesa_presentes": (2, 1, True, "obj"),
})
SHADOWS = {"barraca_flores": 60, "barraca_luau": 60, "barraca_feira": 60, "barraca_luzes": 60, "festa_mastro": 16,
           "festa_vaso": 26, "caldeirao": 24, "mesa_concurso": 56, "abobora_pilha": 28, "fardo": 28,
           "lanterna_festa": 14, "arvore_luzes": 46, "mesa_presentes": 56, "tocha": 12}
ANIMATED = {"fogueira": (_fogueira, 3, 7), "tocha": (_tocha, 3, 6), "lanterna_festa": (_lanterna_festa, 2, 2),
            "arvore_luzes": (_arvore_luzes, 4, 2)}
LIGHT_Y = {"fogueira": 8, "tocha": 28, "lanterna_festa": 20, "arvore_luzes": 30}    # altura da luz (px de arte)


def object_image(g, o):
    """Quadros animados (fogo, tochas, lanternas e o pisca-pisca da árvore)."""
    a = ANIMATED.get(o.kind)
    if not a:
        return None
    fn, n, fps = a
    f = (int(g.t * fps) + o.x) % n
    return art.cached(("festa", o.kind, f), lambda: art.up(fn(f)))


# ===========================================================================
# As festas
# ===========================================================================
FESTIVALS = {
    "flores": dict(
        name="Festa das Flores", quarter=1, day=7, start=9 * 60, end=15 * 60, host="nia",
        place="no Parque Central", where="Parque Central", area=(13, 28, 27, 42), audience=(20, 39, "up"), entry=(20, 44),
        host_spot=(22, 38, "left"), effect="petalas", activity="festa_mastro",
        props=[("festa_mastro", 20, 38), ("festa_arco", 18, 41), ("festa_arco", 18, 28), ("barraca_flores", 14, 39),
               ("festa_vaso", 14, 35), ("festa_vaso", 26, 35), ("festa_vaso", 14, 29), ("festa_vaso", 26, 29)],
        shop=["coroa_flores", "flores", "girassois", "soda", "rosquinha"],
        speech=["Bom dia, National City! Bem-vindos à Festa das Flores!",
                "A primavera chegou, o parque está florido e, pela primeira vez, a Luthor Corp patrocinou as coroas de flores. Obrigada, chefe!",
                "Tem barraca de flores, comida e, ao meio-dia... a Dança das Flores em volta do mastro. Escolham seus pares!"]),
    "luau": dict(
        name="Luau de Verão", quarter=2, day=7, start=18 * 60, end=23 * 60, host="graca",
        place="na praia", where="praia", area=(16, 53, 44, 60), audience=(29, 56, "down"), entry=(29, 53),
        host_spot=(27, 57, "down"), effect="brilhos", activity="caldeirao",
        props=[("fogueira", 30, 58), ("caldeirao", 26, 57), ("tocha", 24, 55), ("tocha", 36, 56), ("tocha", 24, 59),
               ("tocha", 36, 59), ("barraca_luau", 39, 57)],
        shop=["agua_coco", "soda", "drink", "petiscos"],
        speech=["Boa noite, gente bonita! Bem-vindos ao Luau de Verão!",
                "A tradição é a mesma da minha terra: cada um traz um ingrediente e põe no caldeirão. Eu provo e digo se ficou bom.",
                "Peixe, legume, prato pronto... só não me venham com lata velha do píer, hein? Joca, tô olhando pra você!"]),
    "feira": dict(
        name="Feira da Colheita", quarter=3, day=7, start=10 * 60, end=17 * 60, host="sam",
        place="no calçadão central", where="calçadão central", area=(46, 32, 86, 36), audience=(65, 36, "right"), entry=(65, 33),
        host_spot=(66, 35, "down"), effect="confete", activity="mesa_concurso",
        # linhas 37-38 ficam atrás dos telhados dos prédios de baixo: a feira usa só a parte aberta
        props=[("mesa_concurso", 66, 36), ("barraca_feira", 58, 37), ("abobora_pilha", 63, 36),
               ("abobora_pilha", 70, 36), ("fardo", 54, 36), ("fardo", 79, 36), ("fardo", 71, 36)],
        shop=["torta_abobora", "semente_abobora", "girassois", "cha_ervas"],
        speech=["Atenção, National City! Está aberta a Feira da Colheita!",
                "Como CFO da Luthor Corp, eu fui escolhida para julgar o concurso. Sim, eu trouxe uma planilha de critérios.",
                "Tragam o melhor que vocês têm para a mesa do concurso: colheita, peixe, prato ou invenção. Boa sorte a todos!"]),
    "luzes": dict(
        name="Noite das Luzes", quarter=4, day=10, start=18 * 60, end=22 * 60, host="jess",
        place="no Jardim do Mirante", where="Jardim do Mirante", area=(85, 5, 109, 14), audience=(97, 11, "up"), entry=(97, 16),
        host_spot=(99, 8, "down"), effect="brilhos", activity="mesa_presentes",
        props=[("arvore_luzes", 97, 7), ("mesa_presentes", 100, 7), ("barraca_luzes", 89, 7),
               ("lanterna_festa", 92, 7), ("lanterna_festa", 103, 7), ("lanterna_festa", 86, 11),
               ("lanterna_festa", 109, 11), ("lanterna_festa", 95, 14), ("lanterna_festa", 100, 14)],
        shop=["chocolate_quente", "porta_retrato", "chocolate_belga", "cha_ervas"],
        speech=["Boa noite, pessoal! Bem-vindos à Noite das Luzes!",
                "Eu organizei tudo, então está tudo no horário: as lanternas, o chocolate quente e, claro, o amigo secreto.",
                "Entreguem o presente de vocês para quem tiraram. E agora... três, dois, um... acendam as luzes!"]),
}
for _k, _f in FESTIVALS.items():
    _f["key"] = _k

FEST_LINES = {
    "flores": ["Que festa linda! O parque inteiro tem cheiro de flor.",
               "Você já viu a barraca de flores? A coroa de flores é a coisa mais fofa da festa.",
               "Eu nunca sei dançar a Dança das Flores, mas todo ano eu tento.",
               "A primavera em National City é a melhor época do ano. Não aceito discussão.",
               "Comi três rosquinhas e ainda nem é meio-dia. É festa, né?",
               "Olha o mastro! Dizem que quem dança em volta dele tem sorte o ano inteiro."],
    "luau": ["Nada como areia nos pés e uma fogueira, né?",
             "Já pôs alguma coisa no caldeirão da Dona Graça? Ela é exigente!",
             "A água de coco da barraca está geladinha. Recomendo.",
             "Olha as estrelas hoje. Dá até pra esquecer que amanhã é dia útil.",
             "O mar fica lindo com as tochas acesas.",
             "Se eu sumir, fui dar um mergulho. Brincadeira. Talvez."],
    "feira": ["Você vai inscrever alguma coisa no concurso? A Sam leva isso muito a sério.",
              "As abóboras deste ano estão enormes!",
              "A torta de abóbora da barraca acabou de sair do forno. Corre!",
              "Eu adoro o outono. A cidade fica toda cor de laranja.",
              "Dizem que a Sam tem uma planilha com notas de zero a dez para cada critério. Eu acredito.",
              "Feira boa é feira cheia. E hoje está lotada!"],
    "luzes": ["Olha as lanternas! A Jess acertou em tudo este ano.",
              "Já entregou o seu amigo secreto? Eu estou nervosa com o meu!",
              "Um chocolate quente agora resolve qualquer frio.",
              "Essa árvore cheia de luzes é a coisa mais bonita da cidade.",
              "A Noite das Luzes é a minha festa favorita. É quando a cidade inteira fica junta.",
              "Faz frio, mas com tanta luz nem dá pra reclamar."],
}
FEST_SPECIAL = {
    "flores": {"lucy": "Vim cobrir a festa pra CatCo. ...E talvez dançar, se alguém me chamar. Hipoteticamente.",
               "vittoria": "O Gruppo Ricci doou as flores das mesas. Eu escolhi uma por uma. Ficou bonito, não?",
               "nia": "Eu sonhei com essa festa semana passada. Só não lembro se no sonho eu tropeçava na dança..."},
    "luau": {"lucy": "Luau na praia, fogueira, estrelas... Isso é muito mais legal do que a festa da firma da CatCo.",
             "vittoria": "A Dona Graça manda no caldeirão. Até eu obedeço, e eu sou a chefe dela.",
             "graca": "Bota um ingrediente bom no caldeirão, minha filha! Peixe fresco é sempre bem-vindo."},
    "feira": {"lucy": "Estou entrevistando os participantes do concurso. O Joca jura que o peixe dele 'tem personalidade'.",
              "vittoria": "Estou de olho nas abóboras. A Dona Graça quer fazer sopa pra rede inteira.",
              "sam": "Critérios do concurso: qualidade, apresentação e valor de mercado. Sim, eu sou divertida."},
    "luzes": {"lucy": "Essa é a noite mais bonita do ano. ...Com a companhia certa, melhor ainda.",
              "vittoria": "Em Roma também acendemos luzes no inverno. Aqui é diferente... mas eu gosto muito.",
              "jess": "Lanternas no horário, chocolate quente na temperatura certa. Eu poderia chorar de felicidade."},
}

DANCE_LINES = {
    "romance": ["Eu estava torcendo pra você me chamar.", "Só não pisa no meu pé, tá? ...Brincadeira. Pode pisar."],
    "friend": ["Eu danço mal, já vou avisando! Mas com você até que vai.", "Uma dança com a CEO? Vou contar pra todo mundo."],
}


def festival_on(q, d):
    for f in FESTIVALS.values():
        if f["quarter"] == q and f["day"] == d:
            return f
    return None


def today(g):
    return festival_on(g.quarter, g.day)


def active(g):
    """A festa de hoje, se estiver acontecendo agora."""
    f = today(g)
    if f and f["start"] <= g.minutes < f["end"]:
        return f
    return None


def evening_busy(g):
    """Festa à noite hoje: não dá para marcar encontro para as 20h."""
    f = today(g)
    return bool(f and f["start"] < 22 * 60 and f["end"] > 19 * 60 and g.minutes < f["end"])


def _tag(g, f, what):
    return f"{f['key']}:{g.year}:{what}"


def done(g, f, what):
    return _tag(g, f, what) in g.festa["done"]


def mark(g, f, what):
    t = _tag(g, f, what)
    if t not in g.festa["done"]:
        g.festa["done"].append(t)


# --- objetos temporários no mapa da cidade ---------------------------------------
def sync(g):
    """Monta as barracas e enfeites no dia da festa e desmonta no dia seguinte."""
    m = g.world["city"]
    f = today(g)
    want = f["key"] if f else None
    placed = getattr(m, "festa_props", None)
    if placed and placed[0] != want:
        _, objs, saved = placed
        for o in objs:
            if o in m.objects:
                m.objects.remove(o)
        for (x, y), v in saved.items():
            m.solid[y][x] = v
        m.festa_props = None
        placed = None
    if want and not placed:
        objs, saved = [], {}
        for kind, x, y in f["props"]:
            o = world.Obj(kind, x, y, data=("festa", want))
            objs.append(o)
            m.objects.append(o)
            if o.solid:
                for yy in range(y, y + o.h):
                    for xx in range(x, x + o.w):
                        if m.in_bounds(xx, yy):
                            saved.setdefault((xx, yy), m.solid[yy][xx])
                            m.solid[yy][xx] = True
        m.festa_props = (want, objs, saved)


def _prop_tiles(f):
    out = set()
    for kind, x, y in f["props"]:
        w, h = world.OBJECT_DEFS[kind][:2]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                out.add((xx, yy))
    return out


_SPOTS = {}


def spots(g, f):
    """Lugar de cada personagem na festa (calculado uma vez): espalhadas em volta do centro, longe das
    barracas, das portas e do caminho da entrada."""
    if f["key"] in _SPOTS:
        return _SPOTS[f["key"]]
    m = g.world["city"]
    x0, y0, x1, y1 = f["area"]
    props = _prop_tiles(f)
    near_props = {(x + dx, y + dy) for (x, y) in props for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    near_doors = {(x + dx, y + dy) for (x, y) in m.doors for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    # roda livre em volta da atividade (a dança acontece em volta do mastro)
    ring = set()
    for kind, x, y in f["props"]:
        if kind == f["activity"]:
            w, h = world.OBJECT_DEFS[kind][:2]
            ring |= {(xx, yy) for yy in range(y - 2, y + h + 2) for xx in range(x - 2, x + w + 2)}
    ax, ay, _ = f["audience"]
    ex, ey = f["entry"]
    hx, hy, _ = f["host_spot"]
    lane = {(ax, y) for y in range(min(ay, ey), max(ay, ey) + 1)}      # caminho da Letícia na cena de abertura
    cx, cy = (ax + hx) / 2, (ay + hy) / 2
    cands = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            p = (x, y)
            if p in props or p in near_props or p in near_doors or p in lane or p in ring or p in m.road:
                continue
            if abs(x - ax) <= 1 and abs(y - ay) <= 1 or abs(x - hx) <= 1 and abs(y - hy) <= 1:
                continue
            if m.is_solid(x, y) or m.tile_at(x, y) in ("water", "sea", "sea_foam", "fountain"):
                continue
            d = math.hypot(x - cx, y - cy)
            cands.append((abs(d - 4.5) + ((x * 7 + y * 13) % 5) * 0.05, x, y))
    cands.sort()
    picked = []
    for _, x, y in cands:
        if all(max(abs(x - px), abs(y - py)) >= 2 for px, py in picked):
            picked.append((x, y))
    order = [k for k in ("lucy", "vittoria") if k != f["host"]]
    order += [k for k in NPC_ORDER if k not in order and k != f["host"]]
    out = {f["host"]: (hx, hy, f["host_spot"][2])}
    for k, (x, y) in zip(order, picked):
        dx, dy = cx - x, cy - y
        d = ("right" if dx > 0 else "left") if abs(dx) > abs(dy) else ("down" if dy > 0 else "up")
        out[k] = (x, y, d)
    _SPOTS[f["key"]] = out
    return out


def override(g, npc):
    """No dia da festa, a pessoa vai para o seu lugar uma hora antes e volta à rotina no fim."""
    f = today(g)
    if not f:
        return
    spot = spots(g, f).get(npc.key)
    if not spot:
        return
    x, y, d = spot
    start, end = f["start"] - 60, f["end"]
    sch = npc.schedule
    last = None
    for e in sch:
        if e[0] <= end:
            last = e
    new_s = [e for e in sch if e[0] < start] + [(start, "city", x, y, d)]
    if last is not None:
        new_s.append((end, last[1], last[2], last[3], last[4]))
    new_s += [e for e in sch if e[0] > end]
    npc.schedule = new_s


def at_festival(g, npc):
    f = active(g)
    if not f or npc.map != "city":
        return None
    spot = spots(g, f).get(npc.key)
    if spot and abs(npc.fx - spot[0]) + abs(npc.fy - spot[1]) <= 3:
        return f
    return None


# --- estado ------------------------------------------------------------------
def init_state(g):
    g.festa = dict(done=[], said=[], secret=None)


def save_state(g):
    return {"festa": g.festa}


def load_state(g, d):
    fs = d.get("festa") or {}
    g.festa = dict(done=list(fs.get("done", [])), said=list(fs.get("said", [])), secret=fs.get("secret"))


# --- conversa e presentes -------------------------------------------------------
def chat_line(g, npc):
    """Fala especial de aniversário ou de festa (uma vez), ou None para a fala normal."""
    key = npc.key
    said = g.festa["said"]
    if is_birthday(g, key):
        tag = f"bday:{g.year}:{key}"
        if tag not in said:
            said.append(tag)
            return BDAY_CHAT.get(key)
    f = at_festival(g, npc)
    if f:
        tag = f"{f['key']}:{g.year}:{key}"
        if tag not in said:
            said.append(tag)
            special = FEST_SPECIAL.get(f["key"], {}).get(key)
            if special:
                return special
            pool = FEST_LINES[f["key"]]
            return pool[(NPC_ORDER.index(key) + g.year) % len(pool)]
    return None


def gift_bonus(g, key, item, taste):
    """(multiplicador, fala extra, aviso) para presentes em dia de aniversário ou de amigo secreto."""
    if is_birthday(g, key):
        line = random.choice(BDAY_GIFT[taste]).format(g=_g(key))
        return BDAY_MULT[taste], line, f"Presente de aniversário: amizade x{BDAY_MULT[taste]}!"
    sec = g.festa.get("secret")
    f = today(g)
    if f and f["key"] == "luzes" and sec and sec.get("year") == g.year and sec.get("to") == key and not sec.get("given"):
        sec["given"] = True
        mult = {"love": 3, "like": 2, "neutral": 2, "dislike": 1}[taste]
        return mult, "Espera... foi você que me tirou no amigo secreto? Que surpresa boa!", f"Amigo secreto entregue: amizade x{mult}!"
    return 1, None, None


def after_gift(g, key):
    """Depois de entregar o amigo secreto, quem tirou a Letícia aparece com o presente dela."""
    sec = g.festa.get("secret")
    if not sec or sec.get("year") != g.year or sec.get("to") != key or not sec.get("given") or sec.get("got"):
        return
    sec["got"] = True
    frm = sec["frm"]
    item = sec["item"]
    npc = g.npcs[frm]
    g.add_item(item)
    g.add_friendship(frm, 40)
    g.toasts.push(f"Amigo secreto: {NPCS[frm]['short']} te deu {ITEMS[item]['name']}!", C_GREEN, item)
    g.push(ui.Dialog(npc.name, [f"Surpresa! Eu tirei você no amigo secreto. Feliz Noite das Luzes, Letícia!",
                                f"Espero que goste: {ITEMS[item]['name']}."],
                     g.portrait_for(npc, "happy"), subtitle="amigo secreto"))


SECRET_GIFTS = ["chocolate_quente", "chocolate_belga", "cha_ervas", "caneca_lcorp", "livro", "orquidea",
                "porta_retrato", "vinho"]


def _draw_secret(g):
    rnd = random.Random(g.year * 31 + 7)
    keys = [k for k in NPC_ORDER]
    to = rnd.choice(keys)
    frm = rnd.choice([k for k in keys if k != to])
    item = rnd.choice([i for i in SECRET_GIFTS if i in ITEMS])
    g.festa["secret"] = dict(year=g.year, to=to, frm=frm, item=item, given=False, got=False)


# --- noite / manhã ---------------------------------------------------------------
def night(g, notes):
    """Chamado depois que o dia vira (process_night): avisos, clima e sorteio do amigo secreto."""
    f = today(g)
    if f and f["quarter"] != 4:
        g.weather = "sol"                               # festa com tempo bom (no inverno, a neve fica)
    nxt_q, nxt_d = (g.quarter, g.day + 1) if g.day < DAYS_PER_QUARTER else (g.quarter % 4 + 1, 1)
    fn = festival_on(nxt_q, nxt_d)
    if fn and fn["quarter"] != 4:
        g.weather_tomorrow = "sol"
    if f:
        notes.append((f"Hoje tem {f['name']} {f['place']}, das {fmt_hour(f['start'])} às {fmt_hour(f['end'])}! "
                      f"A cidade inteira vai (as lojas fecham).", C_GOLD))
    elif fn:
        notes.append((f"Amanhã: {fn['name']} {fn['place']}.", C_LILAC))
    keys = birthday_today(g)
    if keys:
        notes.append((f"Hoje é aniversário de {_names(keys)}! Presente amado vale 5x.", C_PINK))
    nk = birthday_keys(nxt_q, nxt_d)
    if nk:
        notes.append((f"Amanhã é aniversário de {_names(nk)}.", C_MUTED))
    if g.quarter == 4 and g.day <= FESTIVALS["luzes"]["day"]:
        sec = g.festa.get("secret")
        if not sec or sec.get("year") != g.year:
            _draw_secret(g)
            sec = g.festa["secret"]
            notes.append((f"Sorteio do amigo secreto da Noite das Luzes: você tirou {NPCS[sec['to']]['short']}! "
                          f"Entregue um presente no dia {FESTIVALS['luzes']['day']}.", C_GOLD))


def hud_lines(g):
    out = []
    f = today(g)
    if f and g.minutes < f["end"]:
        out.append((f"{f['name']}: {f['where']}, {fmt_hour(f['start'])} às {fmt_hour(f['end'])}", C_GOLD))
    sec = g.festa.get("secret")
    if (sec and sec.get("year") == g.year and g.quarter == 4 and g.day <= FESTIVALS["luzes"]["day"]
            and not sec.get("given")):
        out.append((f"Amigo secreto: presente para {NPCS[sec['to']]['short']}", C_GOLD))
    keys = [k for k in birthday_today(g) if k not in g.gifted]
    if keys:
        out.append((f"Aniversário: {_names(keys)}", C_PINK))
    return out


# --- cena de abertura e atividades -------------------------------------------------
def _face(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    return ("right" if dx > 0 else "left") if abs(dx) > abs(dy) else ("down" if dy > 0 else "up")


def _crowd_steps(g, f, skip=()):
    steps = []
    for k, (x, y, d) in spots(g, f).items():
        if k not in skip:
            steps.append(("ator", k, x, y, d))
    return steps


def opening_scene(g, f):
    host = f["host"]
    hx, hy, hd = f["host_spot"]
    ax, ay, ad = f["audience"]
    ex, ey = f["entry"]
    others = [k for k in spots(g, f) if k != host]
    fan = others[2] if len(others) > 2 else host
    steps = _crowd_steps(g, f) + [
        ("ator", "player", ex, ey, "up" if ey > ay else "down"),
        ("camera_ja", ax, ay),
        ("fade_in",),
        ("legenda", f["name"], 2.2),
        ("andar", "player", ax, ay),
        ("virar", "player", _face(ax, ay, hx, hy)),
        ("virar", host, _face(hx, hy, ax, ay)),
        ("emote", host, "feliz"),
        ("fala", host, f["speech"][0], "happy"),
        ("fala", host, f["speech"][1]),
        ("efeito", f["effect"], 3),
        ("emote", fan, "musica"),
        ("fala", host, f["speech"][2], "happy"),
        ("virar", "player", ad),
        ("esperar", 0.5),
        ("fade_out",),
    ]
    return dict(map="city", time=g.minutes, weather=g.weather, npc=host, steps=steps)


def check(g):
    """Toca a abertura da festa quando a Letícia chega ao lugar (uma vez por festa)."""
    f = active(g)
    if not f or g.map_name != "city" or done(g, f, "abertura"):
        return False
    x0, y0, x1, y1 = f["area"]
    tx, ty = g.player.tile
    if not (x0 - 3 <= tx <= x1 + 3 and y0 - 3 <= ty <= y1 + 3):
        return False
    mark(g, f, "abertura")

    def end():
        ax, ay, ad = f["audience"]
        g.player.place_tile(ax, ay, ad)
        for k, npc in g.npcs.items():
            if k in spots(g, f):
                npc.snap_to_schedule(g.minutes)
        g.toasts.push(f"{f['name']}: fale com todo mundo e aproveite a festa!", C_GOLD)
    g.play_scene(f"festa_{f['key']}", opening_scene(g, f), on_end=end, remember=False)
    return True


def object_label(g, o):
    data = o.data if isinstance(o.data, tuple) else None
    if not data or data[0] != "festa":
        return None
    k = o.kind
    if k.startswith("barraca_"):
        return "Barraca da festa"
    f = FESTIVALS[data[1]]
    on = active(g) is f
    if k == "festa_mastro":
        return "Dança das Flores" if on else "Mastro das flores"
    if k == "caldeirao":
        return "Caldeirão do luau" if on else "Caldeirão"
    if k == "mesa_concurso":
        return "Concurso da feira" if on else "Mesa do concurso"
    if k == "mesa_presentes":
        return "Amigo secreto" if on else "Mesa de presentes"
    return None


def use_object(g, o):
    data = o.data if isinstance(o.data, tuple) else None
    if not data or data[0] != "festa":
        return False
    f = FESTIVALS[data[1]]
    k = o.kind
    on = active(g) is f
    if k.startswith("barraca_"):
        if not on:
            g.say("A barraca ainda está fechada. Abre na hora da festa." if g.minutes < f["start"]
                  else "A barraca já fechou. Até a próxima festa!")
            return True
        stock = [i for i in f["shop"] if i in ITEMS and "price" in ITEMS[i]]

        def entries():
            return [dict(label=ITEMS[i]["name"], price=ITEMS[i]["price"], desc=ITEMS[i]["desc"], item=i,
                         buy=g._buy_item(i, ITEMS[i]["price"]), enabled=lambda p=ITEMS[i]["price"]: g.money >= p)
                    for i in stock]
        g.push(ui.Shop(f["name"], "Barraca da festa: só hoje!", entries, g))
        return True
    if not on:
        g.say({"festa_mastro": "Um mastro enfeitado com fitas e flores. A dança começa na hora da festa.",
               "caldeirao": "Um caldeirão enorme. A Dona Graça vai fazer a sopa do luau aqui.",
               "mesa_concurso": "A mesa do concurso da feira. A Sam já colou etiquetas com critérios.",
               "mesa_presentes": "A mesa do amigo secreto, cheia de embrulhos."}.get(k, "Enfeite da festa."))
        return True
    if k == "festa_mastro":
        dance(g, f)
    elif k == "caldeirao":
        soup(g, f)
    elif k == "mesa_concurso":
        contest(g, f)
    elif k == "mesa_presentes":
        sec = g.festa.get("secret")
        if not sec or sec.get("year") != g.year:
            _draw_secret(g)
            sec = g.festa["secret"]
        to = NPCS[sec["to"]]["short"]
        if not sec.get("given"):
            g.say(f"Seu amigo secreto é {to}! Escolha um presente na barra e converse com {to} segurando o presente.")
        else:
            g.say(f"Você já entregou o presente para {to}. Feliz Noite das Luzes!")
    return True


def dance(g, f):
    if done(g, f, "danca"):
        g.say("Você já dançou a Dança das Flores este ano. Que tal uma rosquinha?")
        return
    keys = [k for k in NPC_ORDER if g.hearts(k) >= 4 and k in spots(g, f)]
    keys.sort(key=lambda k: (k not in (g.dating, g.partner), -g.friendship[k]))
    if not keys:
        g.say("Ninguém aceitou dançar com você... ainda. É preciso ter pelo menos 4 corações com a pessoa.")
        return
    keys = keys[:8]

    def pick(i):
        if i >= len(keys):
            return
        _dance_scene(g, f, keys[i])
    g.push(ui.Choice("Com quem dançar a Dança das Flores?", [NPCS[k]["name"] for k in keys] + ["Agora não"], pick))


def _dance_scene(g, f, key):
    mark(g, f, "danca")
    mx, my = 20, 38                                     # o mastro
    close = key in (g.dating, g.partner)
    romance = close or key in ROMANCES
    pool = DANCE_LINES["romance" if romance else "friend"]
    steps = _crowd_steps(g, f, skip=(key,)) + [
        ("ator", key, mx + 2, my + 2, "left"),
        ("ator", "player", mx - 2, my + 2, "right"),
        ("camera_ja", mx, my + 1),
        ("fade_in",),
        ("legenda", "A Dança das Flores", 2.0),
        ("fala", key, pool[0], "love" if romance else "happy"),
        ("andar", "player", mx - 1, my + 1),
        ("andar", key, mx + 1, my + 1),
        ("pulo", "player"), ("pulo", key),
        ("efeito", "petalas", 4),
        ("andar_", "player", mx - 1, my - 1),
        ("andar", key, mx + 1, my - 1),
        ("pulo", "player"), ("pulo", key),
        ("andar_", "player", mx - 1, my + 1),
        ("andar", key, mx + 1, my + 1),
        ("emote", key, "coracao" if romance else "musica"),
        ("andar_", "player", mx - 1, my + 2),
        ("andar", key, mx + 1, my + 2),
        ("fala", key, pool[1], "love" if romance else "happy"),
    ]
    if close:
        steps += [("beijo", "player", key), ("efeito", "coracoes", 2.5)]
    else:
        steps += [("emote", "player", "feliz")]
    steps += [("esperar", 0.6), ("fade_out",)]
    scene = dict(map="city", time=g.minutes, weather=g.weather, npc=key, steps=steps)

    def end():
        g.add_friendship(key, 150 if close else 120)
        g.minutes = min(f["end"] - 10, g.minutes + 30)
        ax, ay, ad = f["audience"]
        g.player.place_tile(ax, ay, ad)
        g.toasts.push(f"Dança das Flores com {NPCS[key]['short']}: +amizade!", C_PINK)
        from . import casal
        casal.note(g, key, 3)
    g.play_scene("festa_danca", scene, on_end=end, remember=False)


def _soup_rating(item):
    it = ITEMS[item]
    kind = it["kind"]
    if kind in ("tool", "proposal", "seed", "bait", "book", "product", "treat", "junk", "gift"):
        return "estranho"
    val = FISH[item]["value"] if item in FISH else (it.get("value") or it.get("price", 0))
    if val >= 110:
        return "otimo"
    if val >= 45:
        return "bom"
    return "ok"


SOUP = {
    "otimo": (60, ["*prova* ...Ai, meu Deus. Isso aqui tá divino! Gente, a sopa deste ano é a melhor que eu já fiz!",
                   "Quem trouxe isso? A Letícia? Pode vir aqui que eu vou te dar um abraço!"], "happy"),
    "bom": (30, ["*prova* Hmm! Ficou bom, viu? Encorpado. A turma vai repetir.",
                 "Obrigada pelo ingrediente, minha filha. Deu sustância."], "happy"),
    "ok": (10, ["*prova* ...É. Tá gostosinha. Simples, mas honesta.",
                "No ano que vem traz um peixe bom do píer, hein? Mas obrigada!"], None),
    "estranho": (0, ["*prova* ...Isso é... crocante. Por que a sopa tá crocante?",
                     "Vamos chamar de 'cozinha experimental'. Ninguém se machucou, pelo menos!"], "smile"),
}


def soup(g, f):
    if done(g, f, "sopa"):
        g.say("A sopa já está pronta. Todo mundo está repetindo!")
        return
    item = g.selected_item()
    if not item:
        g.say("Escolha um ingrediente na barra (peixe, legume, prato...) e coloque no caldeirão.")
        return

    def yes(i):
        if i != 0:
            return
        g.remove_item(item)
        mark(g, f, "sopa")
        rating = _soup_rating(item)
        pts, lines, mood = SOUP[rating]
        for k in NPC_ORDER:
            cap = g.heart_cap(k) * HEART_POINTS
            g.friendship[k] = max(0, min(cap, g.friendship[k] + pts))
        audio.sfx("reward" if pts else "gift")
        if pts:
            g.toasts.push(f"Todo mundo provou a sopa: +{pts} de amizade com todos!", C_GOLD)
        graca = g.npcs["graca"]
        g.push(ui.Dialog(graca.name, lines, g.portrait_for(graca, mood), subtitle="sopa do luau"))
    g.push(ui.Choice(f"Colocar {ITEMS[item]['name']} no caldeirão?", ["Colocar", "Melhor não"], yes))


def contest(g, f):
    if done(g, f, "concurso"):
        g.say("Você já participou do concurso deste ano. A Sam ainda está atualizando a planilha.")
        return
    item = g.selected_item()
    if not item or ITEMS[item]["kind"] in ("tool", "proposal", "bait", "treat"):
        g.say("Escolha na barra o que inscrever no concurso: colheita, peixe, prato, produto ou presente.")
        return
    it = ITEMS[item]
    val = it.get("value") or it.get("price", 0)
    if item in FISH:
        val = FISH[item]["value"]

    def yes(i):
        if i != 0:
            return
        mark(g, f, "concurso")
        score = val * random.uniform(0.9, 1.15)
        sam = g.npcs["sam"]
        if score >= 280:
            prize, place, mood = 600, "primeiro lugar", "happy"
            g.flags.add("trofeu_feira")
            lines = [f"Avaliei: {it['name']}. Qualidade, apresentação, valor de mercado... nota máxima.",
                     f"Primeiro lugar para Letícia Luthor! E não, eu não favoreci a minha chefe. Está tudo na planilha."]
        elif score >= 120:
            prize, place, mood = 300, "segundo lugar", "smile"
            lines = [f"{it['name']}. Muito bom. Perdeu por pouco no critério 'apresentação'.",
                     "Segundo lugar! Parabéns, Letícia."]
        else:
            prize, place, mood = 100, "menção honrosa", None
            lines = [f"{it['name']}... honesto. A planilha não mente.",
                     "Menção honrosa! No ano que vem você traz algo mais caprichado, eu sei."]
        g.money += prize
        g.add_friendship("sam", 40)
        audio.sfx("reward")
        g.toasts.push(f"Concurso da feira: {place}! +${prize} (o item voltou para a mochila)", C_GOLD)
        g.push(ui.Dialog(sam.name, lines, g.portrait_for(sam, mood), subtitle="concurso da feira"))
    g.push(ui.Choice(f"Inscrever {it['name']} no concurso? (a Sam devolve depois)", ["Inscrever", "Melhor não"], yes))


# --- desenho ---------------------------------------------------------------------
def lights(g, m, cam, lamps):
    """Luz da fogueira, das tochas e das lanternas no escuro (como os postes)."""
    placed = getattr(m, "festa_props", None) if m.name == "city" else None
    if not placed:
        return
    for o in placed[1]:
        h = LIGHT_Y.get(o.kind)
        if h is None:
            continue
        x = o.x * TILE + o.w * TILE // 2 - cam[0]
        y = o.base_y - h * SCALE - cam[1]
        if -200 < x < SCREEN_W + 200 and -200 < y < SCREEN_H + 200:
            lamps.append((int(x), int(y)))


def draw_npc_extra(g, surf, npc, cam, key):
    """Balãozinho de aniversário amarrado na mão da aniversariante (NPC ou ator de cena)."""
    hx = (npc.fx + 0.5) * TILE + 6 * SCALE - cam[0]
    hy = npc.base_y - 13 * SCALE - cam[1]
    sway = math.sin(g.t * 2 + npc.fx) * 2 * SCALE
    bx, by = hx + 4 * SCALE + sway, hy - 26 * SCALE
    pygame.draw.line(surf, (240, 240, 240), (int(hx), int(hy)), (int(bx), int(by + 6 * SCALE)), 1)
    col = (240, 90, 140) if NPC_ORDER.index(key) % 2 else (150, 90, 240)
    r = pygame.Rect(0, 0, 8 * SCALE, 10 * SCALE)
    r.center = (int(bx), int(by))
    pygame.draw.ellipse(surf, col, r)
    pygame.draw.ellipse(surf, shade(col, 0.7), r, 1)
    pygame.draw.circle(surf, mix(col, (255, 255, 255), 0.6), (r.x + 2 * SCALE, r.y + 3 * SCALE), SCALE)
    pygame.draw.polygon(surf, col, [(r.centerx, r.bottom - 1), (r.centerx - 2, r.bottom + 3), (r.centerx + 2, r.bottom + 3)])


# ===========================================================================
# Calendário (tecla C)
# ===========================================================================
class Calendar(ui.Modal):
    W, H = 940, 600

    def __init__(self, g):
        self.g = g
        self.q = g.quarter
        self.off = 0                                    # trimestres à frente do atual

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_LEFT, pygame.K_a):
                self.off -= 1
                audio.sfx("move")
            elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.off += 1
                audio.sfx("move")
            elif ev.key in ui.CONFIRM or ev.key in ui.CANCEL or ev.key == pygame.K_c:
                self.done = True
        elif ev.type == pygame.MOUSEWHEEL:
            self.off -= ev.y

    def draw(self, surf):
        from . import casal
        g = self.g
        q = (g.quarter - 1 + self.off) % 4 + 1
        year = g.year + (g.quarter - 1 + self.off) // 4
        rect = pygame.Rect(0, 0, self.W, self.H)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, f"Calendário · {season_name(q)} {year}", (rect.centerx, rect.y + 16), 30, C_LILAC, bold=True,
                center=True)
        ui.text(surf, "<", (rect.x + 40, rect.y + 16), 30, C_ACCENT_2, bold=True, center=True)
        ui.text(surf, ">", (rect.right - 40, rect.y + 16), 30, C_ACCENT_2, bold=True, center=True)
        gx, gy = rect.x + 24, rect.y + 70
        cw, ch = (rect.w - 48) // 7, 196
        for i, wd in enumerate(WEEKDAYS):
            ui.text(surf, wd, (gx + i * cw + cw // 2, gy), 17, C_MUTED, bold=True, center=True)
        anniv = casal.anniversary_on(g)
        for d in range(1, DAYS_PER_QUARTER + 1):
            col, row = (d - 1) % 7, (d - 1) // 7
            cell = pygame.Rect(gx + col * cw + 3, gy + 26 + row * (ch + 6), cw - 6, ch)
            f = festival_on(q, d)
            is_today = (q, d, year) == (g.quarter, g.day, g.year)
            past = (year, q, d) < (g.year, g.quarter, g.day)
            fill = (70, 52, 26) if f else ((52, 36, 78) if is_today else (34, 26, 50))
            pygame.draw.rect(surf, fill, cell, border_radius=8)
            border = C_ACCENT_2 if is_today else ((214, 172, 84) if f else (70, 58, 96))
            pygame.draw.rect(surf, border, cell, 3 if is_today else 1, border_radius=8)
            ui.text(surf, str(d), (cell.x + 8, cell.y + 4), 20, C_MUTED if past else C_TEXT, bold=True)
            y = cell.y + 30
            if f:
                for ln in ui.wrap(f["name"], 15, cell.w - 12):
                    ui.text(surf, ln, (cell.centerx, y), 15, C_GOLD, bold=True, center=True)
                    y += 18
                ui.text(surf, f"{fmt_hour(f['start'])}-{fmt_hour(f['end'])}", (cell.centerx, y), 13, C_GOLD, center=True)
                y += 20
            if anniv and anniv == (q, d) and year > casal.since_year(g):
                ui.text(surf, "Namoro!", (cell.centerx, y), 15, C_PINK, bold=True, center=True)
                y += 20
            for k in birthday_keys(q, d):
                npc = g.npcs[k]
                p = g.portrait_for(npc, size=64)
                ui.blit_portrait(surf, p, (cell.centerx - 32, y))
                ui.text(surf, NPCS[k]["short"], (cell.centerx, y + 66), 15, C_PINK, bold=True, center=True)
                y += 88
        ui.text(surf, "Aniversário: presente amado vale 5x.  Festas: a cidade inteira vai, com barracas e atividades.",
                (rect.x + 28, rect.bottom - 62), 15, C_MUTED)
        ui.text(surf, "Setas: outras estações", (rect.x + 28, rect.bottom - 36), 16, C_MUTED)
        ui.text(surf, "Esc / E / C: fechar", (rect.right - 24, rect.bottom - 36), 16, C_MUTED, right=True)

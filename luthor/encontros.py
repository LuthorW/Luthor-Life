"""Encontros especiais com a namorada (Lucy ou Vittoria), cada um com cena própria.

Entram na lista "Convidar para um encontro" junto com os lugares de sempre:
  piquenique  Parque Central, na toalha xadrez (energia extra)
  veleiro     do píer da marina para o alto-mar, ao pôr do sol (experiência de pesca)
  cinema      Cine National: as duas escolhem o filme, sentadas lado a lado (a cena genérica do cinema saiu)
  cozinhar    jantar feito a quatro mãos na cobertura: a Letícia escolhe o prato e ganha o prato pronto
`scene(g, key, place)` devolve a cena (ou None para a cena genérica); `after` dá o bônus de cada um.
"""
import random

from . import habilidades
from .characters import NPCS, ROMANCES
from .data import ITEMS
from .config import C_PINK, C_GREEN, C_GOLD

PLACES = {
    "piquenique": ("city", 31, 36, "left", "um piquenique no Parque Central"),
    "veleiro": ("city", 96, 60, "down", "um passeio de veleiro ao pôr do sol"),
    "cozinhar": ("home", 22, 3, "left", "um jantar feito a quatro mãos na cobertura"),
}
for _k in ROMANCES:
    for _p in PLACES.values():
        if _p not in NPCS[_k]["date_places"]:
            NPCS[_k]["date_places"].append(_p)

CINEMA = ("cinema", 13, 5)

LINES = {
    "piquenique": {
        "lucy": ["Toalha xadrez, sanduíche cortado em triângulo e uma garrafa térmica. Eu pesquisei \"piquenique romântico\". Não ri.",
                 "Sabe o que eu gosto aqui? Ninguém me reconhece como repórter, ninguém te reconhece como CEO. Somos só duas moças na grama."],
        "vittoria": ["Eu trouxe só o essencial: focaccia, queijo, uvas, três tipos de doce e um vinho. O essencial italiano.",
                     "Um piquenique de verdade não tem relógio. Eu tirei o meu. Tira o seu também, amore."],
    },
    "veleiro": {
        "lucy": ["Eu não sei velejar. Você sabe velejar? ...O Ian sabe velejar. Ótimo, eu confio no Ian.",
                 "Olha o sol entrando no mar. Se eu escrevesse isso numa matéria, o editor cortava por ser bonito demais."],
        "vittoria": ["Um veleiro! Na Itália meu tio tinha um. Ele enjoava. Eu não. Vamos ver se você puxou a ele.",
                     "O mar, o pôr do sol e você no leme. Se a Dona Graça visse, ia dizer que é coisa de novela."],
    },
    "cinema": {
        "lucy": ["Eu comprei pipoca grande. Não é para dividir, é para eu comer enquanto você finge que não quer.",
                 "Quando o filme acabar, eu quero sua análise completa. Com notas. Eu sei que você vai fazer notas."],
        "vittoria": ["Eu nunca venho ao cinema. Sempre tem reunião. Hoje a reunião é com você, e a pauta é pipoca.",
                     "Se eu chorar no fim, você não viu nada. Combinado?"],
    },
    "cozinhar": {
        "lucy": ["Eu sei fazer três coisas: café, torrada e caos. Você vai ter que me guiar.",
                 "Avental vestido. Pareço uma chef? Não responde, eu vi a sua cara."],
        "vittoria": ["Cozinhar na sua cozinha? Ela é linda. Nunca foi usada. Dá para ver. Hoje ela estreia.",
                     "Regra da casa Ricci: quem cozinha junto, come junto e lava junto. A terceira parte é a mais importante."],
    },
}
FILM = {
    "lucy": {0: "Romance? Você? ...Tá. Mas se for previsível eu vou cochichar o final.",
             1: "Terror! Finalmente alguém com bom gosto. Eu seguro a sua mão. Por você, claro.",
             2: "Comédia. Ótimo. Eu rio alto, já aviso. A sala inteira vai saber."},
    "vittoria": {0: "Romance. Perfeito. Eu choro, você finge que não vê, e depois a gente janta.",
                 1: "Terror?! Tudo bem. Eu sou corajosa. Eu só vou ficar de olho fechado o filme inteiro.",
                 2: "Comédia! Eu rio igual à minha nonna: batendo na perna de quem está do lado. Desculpa antecipada."},
}
DISHES = [("Lasanha da nonna", "lasanha_nonna"), ("Risoto de cogumelos", "risoto"), ("Massa ao pesto", "massa_pesto")]
DISH_REPLY = {
    "lucy": ["Lasanha? Eu ralo o queijo. É a única etapa em que eu sou confiável.",
             "Risoto exige mexer sem parar. Eu sou ótima em fazer a mesma coisa sem parar. Pergunta para o meu editor.",
             "Massa ao pesto: verde, rápida e cheirosa. Já gostei."],
    "vittoria": ["A lasanha da nonna! Você aprendeu com o caderno? Eu vou fingir que não estou emocionada.",
                 "Risoto. Paciência e manteiga. Duas coisas que eu tenho de sobra. A paciência nem tanto.",
                 "Pesto! Manjericão da horta do terraço? Agora sim, isso é amor."],
}
_pick = {}


def init_state(g):
    g.encontros = dict(kinds=[], count=0)


def save_state(g):
    return {"encontros": g.encontros}


def load_state(g, d):
    init_state(g)
    e = d.get("encontros") or {}
    g.encontros["kinds"] = [k for k in e.get("kinds", []) if k in PLACES or k == "cinema"]
    g.encontros["count"] = int(e.get("count", 0))


def kind_of(place):
    m, x, y = place[0], place[1], place[2]
    if (m, x, y) == CINEMA:
        return "cinema"
    for k, p in PLACES.items():
        if (p[0], p[1], p[2]) == (m, x, y):
            return k
    return None


def _say(key, kind, i):
    return LINES[kind][key][i]


def scene(g, key, place):
    kind = kind_of(place)
    if not kind or key not in LINES["piquenique"]:
        return None
    return BUILD[kind](g, key)


def _piquenique(g, key):
    steps = [
        ("ator", key, 31, 36, "left"),
        ("ator", "player", 28, 39, "up"),
        ("camera_ja", 29, 36), ("fade_in",),
        ("legenda", "Piquenique no Parque Central", 1.8),
        ("andar", "player", 28, 36), ("virar", "player", "right"),
        ("fala", key, _say(key, "piquenique", 0), "love"),
        ("fala", "player", "Toalha xadrez, comida e você. Já é o melhor encontro do ano."),
        ("narra", "As duas dividem a toalha xadrez da mesinha. Os vagalumes do parque acendem um por um, como se alguém tivesse ligado a cidade."),
        ("fala", key, _say(key, "piquenique", 1), "happy"),
        ("escolha", "O que dizer?", [
            ("Devia ter mais noites assim. Sem agenda.", 30, "Então marca na agenda. Uma noite sem agenda, toda semana."),
            ("Você pensa em tudo, sabia?", 30, "Penso em você. O resto vem junto."),
            ("Me passa mais um doce. E fica mais um pouco.", 30, "Os dois pedidos foram aceitos."),
        ]),
        ("emote", key, "coracao"),
        ("efeito", "petalas", 2),
        ("esperar", 1.2),
        ("legenda", "Mais tarde...", 1.4),
        ("fade_out",),
    ]
    return dict(map="city", time=19 * 60 + 40, weather="sol", npc=key, steps=steps)


def _veleiro(g, key):
    steps = [
        ("ator", key, 96, 64, "up"),
        ("ator", "player", 96, 61, "down"),
        ("camera_ja", 96, 63), ("fade_in",),
        ("legenda", "Píer da Marina Luthor, pôr do sol", 1.8),
        ("andar", "player", 96, 62),
        ("fala", key, _say(key, "veleiro", 0), "happy"),
        ("fala", "player", "O Ian deixou o veleiro pronto. E me ensinou o nó de marinheiro. Duas vezes."),
        ("fade_out",),
        ("mapa", "altomar", 18 * 60 + 50),
        ("ator", key, 24, 13, "left"),
        ("ator", "player", 22, 13, "right"),
        ("camera_ja", 23, 13), ("fade_in",),
        ("legenda", "Em alto-mar", 1.4),
        ("fala", key, _say(key, "veleiro", 1), "love"),
        ("escolha", "O que dizer?", [
            ("Eu queria parar o tempo aqui.", 30, "Então para. Só por hoje, a gente manda no relógio."),
            ("Você fica linda com essa luz.", 30, "E você fica convencida quando acerta o elogio."),
            ("Da próxima vez, você pilota.", 30, "Combinado. Mas se a gente afundar, a culpa é sua."),
        ]),
        ("andar", "player", 23, 13),
        ("beijo", "player", key),
        ("efeito", "coracoes", 2),
        ("esperar", 1.0),
        ("legenda", "O sol some no mar...", 1.6),
        ("fade_out",),
    ]
    return dict(map="city", time=18 * 60 + 30, weather="sol", npc=key, steps=steps)


def _cinema(g, key):
    def choose(i):
        return lambda gg: _pick.__setitem__("film", i)
    steps = [
        ("ator", key, 13, 5, "up"), ("sentar", key),
        ("ator", "player", 10, 12, "up"),
        ("segurar", key, "soda"),
        ("camera_ja", 11, 7), ("fade_in",),
        ("legenda", "Cine National, sessão das 20h", 1.8),
        ("andar", "player", 11, 5), ("andar", "player", 12, 5), ("sentar", "player"),
        ("fala", key, _say(key, "cinema", 0), "happy"),
        ("escolha", "Qual filme vocês vão ver?", [
            ("Um romance.", 20, FILM[key][0], "love", choose(0)),
            ("Um terror.", 20, FILM[key][1], "happy", choose(1)),
            ("Uma comédia.", 20, FILM[key][2], "happy", choose(2)),
        ]),
        ("narra", "As luzes se apagam. Por duas horas, a CEO da Luthor Corp é só alguém dividindo pipoca no escuro."),
        ("emote", key, "coracao"),
        ("emote", "player", "feliz"),
        ("fala", key, _say(key, "cinema", 1), "love"),
        ("fala", "player", "Eu fiz notas mentais. Três páginas."),
        ("esperar", 0.8),
        ("legenda", "Depois da sessão...", 1.4),
        ("fade_out",),
    ]
    return dict(map="cinema", time=20 * 60 + 10, npc=key, steps=steps)


def _cozinhar(g, key):
    def choose(i):
        return lambda gg: _pick.__setitem__("dish", i)
    steps = [
        ("ator", key, 22, 3, "left"),
        ("ator", "player", 20, 4, "up"),
        ("camera_ja", 21, 4), ("fade_in",),
        ("legenda", "Cozinha da cobertura", 1.6),
        ("andar", "player", 20, 3), ("virar", "player", "right"),
        ("fala", key, _say(key, "cozinhar", 0), "happy"),
        ("escolha", "O que vocês vão cozinhar?", [
            (DISHES[0][0], 20, DISH_REPLY[key][0], "happy", choose(0)),
            (DISHES[1][0], 20, DISH_REPLY[key][1], "happy", choose(1)),
            (DISHES[2][0], 20, DISH_REPLY[key][2], "happy", choose(2)),
        ]),
        ("virar", "player", "up"), ("virar", key, "up"),
        ("narra", "Panela no fogo, música baixinha e farinha onde não devia ter farinha. A cozinha nunca esteve tão cheia."),
        ("efeito", "brilhos", 1.2),
        ("virar", "player", "right"), ("virar", key, "left"),
        ("fala", key, _say(key, "cozinhar", 1), "love"),
        ("fade_out",),
        ("ator", "player", 20, 13, "right"), ("sentar", "player"),
        ("ator", key, 23, 13, "left"), ("sentar", key),
        ("camera_ja", 21, 12), ("fade_in",),
        ("legenda", "O jantar está servido", 1.4),
        ("fala", "player", "A gente cozinhou isso. Nós duas. Sem ninguém se machucar."),
        ("fala", key, "Quase ninguém. Mas foi só um corte no orgulho.", "happy"),
        ("segurar", key, "taca_vinho"), ("segurar", "player", "taca_vinho"),
        ("emote", key, "coracao"),
        ("esperar", 0.8),
        ("fade_out",),
    ]
    return dict(map="home", time=20 * 60 + 5, npc=key, steps=steps)


BUILD = {"piquenique": _piquenique, "veleiro": _veleiro, "cinema": _cinema, "cozinhar": _cozinhar}


def after(g, key, place):
    """Bônus de cada encontro especial (o encontro em si já dá amizade e energia em Game.do_date)."""
    kind = kind_of(place)
    if not kind:
        return
    g.encontros["count"] += 1
    if kind not in g.encontros["kinds"]:
        g.encontros["kinds"].append(kind)
    if kind == "piquenique":
        g.energy = g.max_energy
        g.toasts.push("Piquenique: energia cheia!", C_GREEN)
    elif kind == "veleiro":
        habilidades.gain(g, "pesca", 25)
        g.toasts.push("Veleiro ao pôr do sol: experiência de pesca!", C_GREEN)
    elif kind == "cinema":
        habilidades.gain(g, "carisma", 10)
    elif kind == "cozinhar":
        dish = DISHES[_pick.get("dish", 0)][1]
        habilidades.gain(g, "culinaria", 20)
        if dish in ITEMS and g.add_item(dish):
            g.toasts.push(f"Jantar a quatro mãos: {ITEMS[dish]['name']} na mochila!", C_GREEN, dish)
    _pick.clear()


from . import scenetest  # noqa: E402
for _kind, _fn in BUILD.items():
    for _k in ROMANCES:
        scenetest.DYNAMIC[f"encontro_{_kind}_{_k}"] = (lambda f, k: (lambda g: f(g, k)))(_fn, _k)

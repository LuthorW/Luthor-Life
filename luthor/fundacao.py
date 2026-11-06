"""Fundação Luthor: projetos de doação para a cidade (como os pacotes do Centro Comunitário do Stardew).

A mesa da Fundação fica na sede da Luthor Corp. Cada projeto pede itens (e o último também dinheiro); quando
tudo foi doado, a obra fica pronta na manhã seguinte, aparece na cidade e libera um benefício:

  Coreto do Parque ........ conversas rendem 10% mais amizade
  Peixaria do Píer ........ peixes valem 10% a mais
  Horta Comunitária ....... cesta de ingredientes toda segunda (pegar nos canteiros)
  Lanternas do Bosque ..... mais coletáveis por dia
  Biblioteca do Bairro .... 15% de desconto na Bayside Books e no Mercado
  Praça da Fundação ....... (depois de todos) inauguração com a cidade inteira e +1 coração com todo mundo
"""
import random

import pygame

from . import art, ui, audio, world, festas
from .art import new, R, P, shade
from .characters import NPCS
from .data import ITEMS
from .config import (SCREEN_W, SCREEN_H, HEART_POINTS, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_ACCENT, C_PINK)

PROJECTS = [
    dict(key="coreto", name="Coreto do Parque", place="no Parque Central",
         desc="Um coreto branco no meio do parque, para música no domingo e conversa fiada no resto da semana.",
         items=[("flor_silvestre", 3), ("dente_leao", 2), ("girassois", 1), ("rosa_jardim", 1)],
         perk="Conversas rendem 10% mais amizade."),
    dict(key="peixaria", name="Peixaria do Píer", place="na praia, ao lado do píer",
         desc="Uma barraca para os pescadores venderem direto na orla. O Seu Joca vai ser o primeiro cliente.",
         items=[("sardinha", 3), ("robalo", 1), ("linguado", 1), ("carpa", 1), ("tilapia", 1)],
         perk="Peixes valem 10% a mais."),
    dict(key="horta", name="Horta Comunitária", place="no canto sul do parque",
         desc="Canteiros abertos para o bairro inteiro plantar. Quem doa as primeiras mudas ganha a primeira cesta.",
         items=[("tomate", 3), ("manjericao", 3), ("morango", 2), ("abobora", 1)],
         perk="Toda segunda tem uma cesta de ingredientes nos canteiros."),
    dict(key="lanternas", name="Lanternas do Bosque", place="no Bosque Bayside",
         desc="Postes novos em volta do lago do bosque, para ninguém mais tropeçar em pinha no escuro.",
         items=[("concha", 3), ("vidro_mar", 2), ("estrela_mar", 1), ("pena", 2), ("pinha", 2)],
         perk="Mais coletáveis aparecem todos os dias."),
    dict(key="biblioteca", name="Biblioteca do Bairro", place="entre a Bayside Books e o Mercado",
         desc="Uma caixinha de livros livres: pegue um, deixe outro. As lojas vizinhas prometeram apoiar.",
         items=[("livro", 1), ("policial", 1), ("jornal", 2), ("relatorio", 2), ("caneta_tinteiro", 1)],
         perk="15% de desconto na Bayside Books e no Mercado Central."),
    dict(key="praca", name="Praça da Fundação", place="na calçada em frente ao Mercado",
         desc="O monumento que fecha a primeira fase da Fundação Luthor, com uma inauguração para a cidade inteira.",
         items=[("software", 2), ("athena", 1), ("coral", 1), ("trevo4", 1)], money=5000,
         perk="Inauguração com a cidade toda e +1 coração com todo mundo."),
]
BY_KEY = {p["key"]: p for p in PROJECTS}
FINAL = "praca"

# objetos que cada obra coloca na cidade: (tipo, x, y); árvores e enfeites embaixo saem
PROPS = {
    "coreto": [("coreto", 35, 26)],
    "peixaria": [("peixaria", 64, 57), ("bench", 55, 57), ("bench", 56, 57)],
    "horta": [("canteiro_horta", 10, 47), ("canteiro_horta", 13, 47), ("canteiro_horta", 16, 47)],
    "lanternas": [("lamp", 93, 28), ("lamp", 106, 28), ("lamp", 90, 31), ("lamp", 109, 31), ("lamp", 90, 37),
                  ("lamp", 109, 37)],
    "biblioteca": [("biblioteca_livre", 58, 28)],
    "praca": [("monumento", 63, 22), ("flowerpot", 61, 23), ("flowerpot2", 66, 23)],
}
HQ_DESK = (4, 12)
MONUMENT = (63, 22)
CESTA = [("tomate", 2), ("manjericao", 2), ("ovos", 2), ("leite", 1), ("morango", 1)]
BOOK_LINES = [
    "\"Quem planta árvore sabendo que não vai sentar na sombra entendeu alguma coisa da vida.\" Alguém sublinhou.",
    "Um livro de receitas da Dona Graça, autografado: \"Sal a gosto. O gosto é meu.\"",
    "Um guia de pássaros de National City. Tem uma pena marcando a página das gaivotas.",
    "Um romance policial com o final arrancado. Tem um bilhete: \"Foi o mordomo. Desculpa.\"",
    "Um manual de vela do Ian, cheio de anotações na margem: \"NÃO soltar a escota.\"",
    "Um livro de poesia com uma flor seca dentro. Você devolve com cuidado.",
    "Um atlas antigo com Gotham circulada a lápis. Você fecha rápido.",
    "\"Como falar em público sem desmaiar\", da biblioteca da Jess. Muito usado.",
]


# ---------------------------------------------------------------------------
# Arte
# ---------------------------------------------------------------------------
WHITE = (246, 244, 238)
ROOF = (122, 72, 170)


def _mesa_fundacao():
    s = new(32, 30)
    wood = (120, 78, 52)
    R(s, shade(wood, 0.7), 1, 16, 30, 14)
    R(s, wood, 0, 12, 32, 6)
    R(s, shade(wood, 1.2), 0, 12, 32, 1)
    R(s, (90, 40, 140), 4, 18, 24, 10)                     # pano roxo da Fundação
    R(s, (150, 90, 210), 4, 18, 24, 1)
    R(s, (250, 230, 140), 14, 20, 4, 6)                    # "L" dourado
    R(s, (90, 40, 140), 16, 20, 2, 4)
    R(s, (210, 210, 220), 3, 4, 9, 8)                      # urna de vidro com moedas
    R(s, (240, 240, 250), 3, 4, 9, 1)
    R(s, (60, 60, 70), 6, 4, 3, 1)
    R(s, (240, 200, 80), 4, 9, 7, 3)
    P(s, (255, 236, 150), 6, 9)
    R(s, (250, 248, 240), 17, 6, 11, 6)                    # prancheta com a lista
    for y in (7, 9):
        R(s, (150, 150, 170), 19, y, 7, 1)
    R(s, (184, 76, 255), 22, 3, 2, 3)
    return s


def _coreto():
    s = new(48, 58)
    floor = (196, 170, 130)
    R(s, shade(floor, 0.7), 2, 48, 44, 8)                  # base
    R(s, floor, 1, 44, 46, 6)
    R(s, shade(floor, 1.15), 1, 44, 46, 1)
    R(s, shade(floor, 0.6), 18, 50, 12, 6)                 # degraus
    R(s, shade(floor, 0.85), 19, 52, 10, 1)
    for x in (3, 15, 32, 44):                              # colunas
        R(s, WHITE, x, 18, 3, 27)
        R(s, shade(WHITE, 0.8), x + 2, 18, 1, 27)
    for x in range(5, 44, 3):                              # parapeito
        if not 16 <= x <= 31:
            R(s, WHITE, x, 38, 1, 6)
    R(s, WHITE, 3, 37, 13, 1); R(s, WHITE, 32, 37, 15, 1)
    # telhado em pagode
    for i, y in enumerate(range(4, 20)):
        w = 18 + i * 2 + (2 if y > 16 else 0)
        col = ROOF if (y // 3) % 2 else shade(ROOF, 1.15)
        R(s, col, 24 - w // 2, y, w, 1)
    R(s, shade(ROOF, 0.7), 0, 19, 48, 2)
    for x in range(1, 48, 4):
        R(s, (250, 230, 140), x, 21, 2, 1)
    R(s, (240, 200, 80), 23, 0, 2, 5)                      # ponteira dourada
    P(s, (255, 236, 150), 23, 0)
    return s


def _goods_peixe(s):
    for i, x in enumerate((3, 10, 17, 24)):
        col = ((150, 170, 190), (200, 150, 120), (120, 150, 170), (230, 170, 110))[i]
        pygame.draw.ellipse(s, col, (x, 20, 6, 3))
        P(s, shade(col, 0.6), x + 6, 21)
        P(s, (30, 30, 40), x + 1, 21)
    R(s, (200, 230, 240), 2, 24, 28, 2)                    # gelo


def _peixaria():
    return festas._barraca((60, 120, 200), (246, 248, 252), _goods_peixe)


def _canteiro_horta():
    s = new(32, 28)
    wood = (150, 102, 62)
    R(s, shade(wood, 0.62), 0, 16, 32, 12)                 # caixa de madeira
    R(s, wood, 0, 14, 32, 3)
    R(s, shade(wood, 1.2), 0, 14, 32, 1)
    for x in (10, 21):
        R(s, shade(wood, 0.5), x, 17, 1, 11)
    R(s, (92, 62, 42), 2, 16, 28, 2)                       # terra
    # tomateiro, alface, manjericão e morangos
    leaf = (72, 152, 70)
    for cx in (5, 26):
        R(s, shade(leaf, 0.7), cx, 4, 1, 13)               # estaca
        for (dx, dy) in ((-2, 6), (1, 8), (-1, 11), (2, 12), (-2, 14), (1, 4)):
            pygame.draw.circle(s, leaf, (cx + dx, dy), 2)
        for (dx, dy) in ((-2, 9), (2, 11), (0, 14)):
            pygame.draw.circle(s, (226, 58, 48), (cx + dx, dy), 1)
            P(s, (255, 150, 130), cx + dx, dy - 1)
    for cx in (12, 19):                                    # alface
        pygame.draw.circle(s, (120, 196, 90), (cx, 14), 3)
        pygame.draw.circle(s, (160, 220, 120), (cx, 13), 2)
        P(s, (200, 240, 160), cx, 12)
    for x in (9, 16, 22):                                  # manjericão
        R(s, (60, 140, 60), x, 12, 2, 4)
        P(s, (90, 180, 80), x - 1, 12); P(s, (90, 180, 80), x + 2, 13)
    for x in (14, 23):                                     # morangos
        P(s, (236, 50, 80), x, 16)
    return s


def _biblioteca_livre():
    s = new(16, 30)
    wood = (150, 90, 60)
    R(s, shade(wood, 0.6), 7, 18, 2, 12)                   # poste
    R(s, wood, 1, 5, 14, 14)
    R(s, shade(wood, 0.7), 1, 17, 14, 2)
    R(s, ROOF, 0, 2, 16, 3)                                # telhadinho roxo
    R(s, shade(ROOF, 1.2), 1, 1, 14, 1)
    R(s, (160, 200, 220), 3, 7, 10, 9)                     # porta de vidro
    for i, x in enumerate(range(4, 12, 2)):               # livros
        col = ((220, 70, 70), (70, 120, 200), (240, 200, 80), (90, 170, 100))[i]
        R(s, col, x, 9 + (i % 2), 2, 6 - (i % 2))
    R(s, (250, 250, 255), 3, 7, 10, 1)
    P(s, (250, 230, 140), 12, 12)
    return s


def _monumento():
    s = new(32, 48)
    stone = (196, 192, 204)
    R(s, shade(stone, 0.65), 2, 40, 28, 8)                 # base
    R(s, shade(stone, 0.85), 2, 38, 28, 3)
    R(s, stone, 6, 22, 20, 17)                             # pedestal
    R(s, shade(stone, 1.15), 6, 22, 20, 1)
    R(s, shade(stone, 0.75), 24, 22, 2, 17)
    R(s, (180, 140, 80), 9, 27, 14, 8)                     # placa de bronze
    R(s, (220, 180, 110), 9, 27, 14, 1)
    for y in (29, 31, 33):
        R(s, (120, 90, 50), 11, y, 10, 1)
    # escultura: duas mãos segurando uma chama roxa
    bronze = (170, 120, 70)
    R(s, bronze, 9, 16, 14, 6)
    R(s, shade(bronze, 1.2), 9, 16, 14, 1)
    R(s, bronze, 8, 12, 4, 5); R(s, bronze, 20, 12, 4, 5)
    for y, w in ((2, 2), (4, 4), (6, 6), (8, 8), (10, 8), (12, 6)):
        R(s, (150, 70, 220), 16 - w // 2, y, w, 2)
    for y, w in ((6, 2), (8, 4), (10, 4)):
        R(s, (230, 190, 255), 16 - w // 2, y, w, 2)
    P(s, (255, 250, 220), 16, 9)
    return s


art.OBJECT_BUILDERS.update({"mesa_fundacao": _mesa_fundacao, "coreto": _coreto, "peixaria": _peixaria,
                            "canteiro_horta": _canteiro_horta, "biblioteca_livre": _biblioteca_livre,
                            "monumento": _monumento})
world.OBJECT_DEFS.update({"mesa_fundacao": (2, 1, True, "obj"), "coreto": (3, 2, True, "obj"),
                          "peixaria": (2, 1, True, "obj"), "canteiro_horta": (2, 1, True, "obj"),
                          "biblioteca_livre": (1, 1, True, "obj"), "monumento": (2, 1, True, "obj")})
world.HITBOXES.update({"biblioteca_livre": (3, 6, 10, 10)})


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.fundacao = dict(given={}, money={}, ready=[], built=[], cesta=False, cesta_day=-1, inaug=False)
    apply(g)


def save_state(g):
    return {"fundacao": g.fundacao}


def load_state(g, d):
    init_state(g)
    f = d.get("fundacao") or {}
    for k in g.fundacao:
        if k in f:
            g.fundacao[k] = f[k]
    g.fundacao["built"] = [k for k in g.fundacao["built"] if k in BY_KEY]
    g.fundacao["ready"] = [k for k in g.fundacao["ready"] if k in BY_KEY and k not in g.fundacao["built"]]
    apply(g)


def built(g, key):
    return key in getattr(g, "fundacao", {}).get("built", ())


def unlocked(g, key):
    return key != FINAL or all(built(g, p["key"]) for p in PROJECTS if p["key"] != FINAL)


def remaining(g, p):
    given = g.fundacao["given"].get(p["key"], {})
    out = [(it, n - given.get(it, 0)) for it, n in p["items"] if n - given.get(it, 0) > 0]
    money = p.get("money", 0) - g.fundacao["money"].get(p["key"], 0)
    return out, max(0, money)


def complete(g, p):
    items, money = remaining(g, p)
    return not items and not money


# --- benefícios ------------------------------------------------------------
def talk_mult(g):
    return 1.1 if built(g, "coreto") else 1.0


def fish_mult(g):
    return 1.1 if built(g, "peixaria") else 1.0


def shop_mult(g, shop_id):
    return 0.85 if built(g, "biblioteca") and shop_id in ("books", "market") else 1.0


def forage_bonus(g):
    """(praia, parque) a mais por dia."""
    return (1, 2) if built(g, "lanternas") else (0, 0)


# ---------------------------------------------------------------------------
# Objetos na sede e na cidade
# ---------------------------------------------------------------------------
def _recompute(m, tiles):
    for (x, y) in tiles:
        if not m.in_bounds(x, y):
            continue
        solid = m.tiles[y][x] in world.SOLID_TILES or m.building_at(x, y) is not None
        if not solid:
            solid = any(o.solid and o.x <= x < o.x + o.w and o.y <= y < o.y + o.h for o in m.objects)
        m.solid[y][x] = solid


def _footprint(kind, x, y):
    w, h = world.OBJECT_DEFS[kind][:2]
    return [(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)]


def apply(g):
    """Coloca a mesa na sede e as obras prontas na cidade (e tira as que não deviam estar lá)."""
    hq = g.world.get("hq")
    if hq is not None and not any(o.kind == "mesa_fundacao" for o in hq.objects):
        hq.add("mesa_fundacao", *HQ_DESK, data=("fundacao", "mesa"))
        _recompute(hq, _footprint("mesa_fundacao", *HQ_DESK))
    m = g.world.get("city")
    if m is None:
        return
    done = set(g.fundacao["built"]) if hasattr(g, "fundacao") else set()
    have = {o.data[1] for o in m.objects if isinstance(o.data, tuple) and o.data[0] == "fundacao"}
    touched = set()
    for key in have - done:                                  # jogo novo ou save sem a obra
        for o in [o for o in m.objects if o.data == ("fundacao", key)]:
            m.objects.remove(o)
            touched.update(_footprint(o.kind, o.x, o.y))
        for o in getattr(m, "fundacao_removed", {}).pop(key, []):
            m.objects.append(o)
            touched.update(_footprint(o.kind, o.x, o.y))
    removed = m.__dict__.setdefault("fundacao_removed", {})
    for key in done - have:
        for kind, x, y in PROPS[key]:
            fp = _footprint(kind, x, y)
            area = set(fp)
            if kind in ("coreto", "monumento", "peixaria"):    # árvore ou arbusto logo abaixo também sai
                area |= {(xx, yy + 1) for (xx, yy) in fp}
            gone = [o for o in m.objects if not (isinstance(o.data, tuple) and o.data[0] in ("fundacao", "festa"))
                    and any((xx, yy) in area for xx, yy in _footprint(o.kind, o.x, o.y))]
            for o in gone:
                m.objects.remove(o)
                touched.update(_footprint(o.kind, o.x, o.y))
            removed.setdefault(key, []).extend(gone)
            m.add(kind, x, y, data=("fundacao", key))
            touched.update(fp)
    if touched:
        _recompute(m, touched)
        festas._SPOTS.clear()                                # lugares das festas são recalculados


# ---------------------------------------------------------------------------
# Noite e manhã
# ---------------------------------------------------------------------------
def night(g, notes):
    f = g.fundacao
    for key in list(f["ready"]):
        if key not in f["built"]:
            f["built"].append(key)
            p = BY_KEY[key]
            if key == FINAL:
                notes.append((f"Fundação Luthor: a {p['name']} está pronta! A inauguração é amanhã, das 9h às 18h.",
                              C_GOLD))
            else:
                notes.append((f"Fundação Luthor: obra entregue {p['place']}: {p['name']}! {p['perk']}", C_GOLD))
    f["ready"] = []


def morning(g):
    f = g.fundacao
    apply(g)
    if built(g, "horta") and g.weekday == 0 and f["cesta_day"] != g.abs_day():
        f["cesta"] = True
        f["cesta_day"] = g.abs_day()
        g.toasts.push("Horta Comunitária: a cesta da semana está nos canteiros do parque.", C_GREEN)
    if built(g, FINAL) and not f["inaug"] and not festas.today(g):
        g.toasts.push("Hoje: inauguração da Praça da Fundação, em frente ao Mercado (9h às 18h)!", C_GOLD)


def hud_lines(g):
    """Linha do HUD no dia da inauguração e da cesta da horta."""
    out = []
    if built(g, FINAL) and not g.fundacao["inaug"] and not festas.today(g) and g.minutes < 18 * 60:
        out.append(("Inauguração da Praça da Fundação: frente do Mercado (9h-18h)", C_GOLD))
    if g.fundacao["cesta"]:
        out.append(("Cesta da Horta Comunitária no parque", C_GREEN))
    return out


# ---------------------------------------------------------------------------
# Inauguração
# ---------------------------------------------------------------------------
CROWD = [("sam", 65, 23, "left"), ("jess", 60, 22, "right"), ("brainy", 59, 23, "right"), ("nia", 67, 22, "left"),
         ("barry", 68, 23, "left"), ("lucy", 61, 21, "down"), ("vittoria", 66, 21, "down"), ("ian", 58, 22, "right"),
         ("rafa", 69, 22, "left"), ("graca", 62, 20, "down"), ("joca", 65, 20, "down"), ("milany", 60, 20, "down"),
         ("theo", 67, 20, "down"), ("bea", 57, 23, "right"), ("marco", 70, 23, "left")]


def check(g):
    f = g.fundacao
    if (f["inaug"] or not built(g, FINAL) or g.map_name != "city" or festas.today(g)
            or not 9 * 60 <= g.minutes <= 18 * 60):
        return False
    tx, ty = g.player.tile
    if abs(tx - MONUMENT[0]) > 9 or abs(ty - MONUMENT[1]) > 6:
        return False
    f["inaug"] = True

    def end():
        g.player.place_tile(63, 23, "down")
        for k in NPCS:
            g.add_friendship(k, HEART_POINTS)
        g.flags.add("fundacao_completa")
        audio.sfx("reward")
        g.toasts.push("A cidade inteira agradece: +1 coração com todo mundo!", C_PINK)
        for npc in g.npcs.values():
            npc.snap_to_schedule(g.minutes)
    g.play_scene("fundacao_inauguracao", scene(g), on_end=end, remember=False)
    return True


def scene(g):
    steps = [("ator", k, x, y, d) for k, x, y, d in CROWD if k in NPCS]
    steps += [
        ("ator", "player", 63, 23, "up"),
        ("camera_ja", 63, 22),
        ("fade_in",),
        ("legenda", "Inauguração da Praça da Fundação", 2.4),
        ("virar", "sam", "left"),
        ("fala", "sam", "Senhoras e senhores, moradores de National City... e Brainy.", "happy"),
        ("emote", "brainy", "gota"),
        ("fala", "sam", "Coreto, peixaria, horta, lanternas, biblioteca. Tudo que esta praça celebra saiu de doações."),
        ("fala", "jess", "E a maior parte delas veio de uma CEO que vive com a mochila cheia de concha e tomate.", "happy"),
        ("emote", "player", "vergonha"),
        ("virar", "player", "down"),
        ("fala", "player", "A cidade fez a parte difícil. Eu só carreguei as coisas."),
        ("fala", "player", "A Fundação Luthor existe para isso: deixar National City um pouco melhor do que a gente encontrou."),
        ("virar", "player", "up"),
        ("efeito", "confete", 3),
        ("emote", "nia", "coracao"),
        ("emote", "joca", "feliz"),
        ("emote", "graca", "estrela"),
        ("fala", "barry", "Todo mundo olhando pra cá! Um, dois... foto!", "happy"),
        ("efeito", "brilhos", 1.5),
        ("esperar", 0.8),
        ("fade_out",),
    ]
    return dict(map="city", time=max(9 * 60, min(g.minutes, 17 * 60)), weather="sol", npc="sam", steps=steps)


# ---------------------------------------------------------------------------
# Ganchos dos objetos
# ---------------------------------------------------------------------------
LABELS = {"coreto": "Coreto do Parque", "peixaria": "Peixaria do Píer", "monumento": "Monumento da Fundação",
          "biblioteca_livre": "Biblioteca do Bairro (ler)"}


def object_label(g, o):
    if not (isinstance(o.data, tuple) and o.data[0] == "fundacao"):
        return None
    if o.kind == "mesa_fundacao":
        return "Fundação Luthor"
    if o.kind == "canteiro_horta":
        return "Pegar a cesta da horta" if g.fundacao["cesta"] else "Horta Comunitária"
    return LABELS.get(o.kind)


def use_object(g, o):
    if not (isinstance(o.data, tuple) and o.data[0] == "fundacao"):
        return False
    k = o.kind
    if k == "mesa_fundacao":
        audio.sfx("page")
        g.push(Panel(g))
    elif k == "canteiro_horta":
        if g.fundacao["cesta"]:
            got = []
            for it, n in CESTA:
                if g.add_item(it, n):
                    got.append(f"{ITEMS[it]['name']} x{n}")
            if got:
                g.fundacao["cesta"] = False
                audio.sfx("pickup")
                g.say("Cesta da Horta Comunitária: " + ", ".join(got) + ". Um bilhete diz: \"Obrigada pelas mudas!\"")
            else:
                g.say("Mochila cheia. A cesta fica esperando aqui.")
        else:
            g.say("Canteiros cheios de tomate, manjericão e morango. Toda segunda tem uma cesta para você.")
    elif k == "biblioteca_livre":
        audio.sfx("page")
        g.say(random.choice(BOOK_LINES))
    elif k == "coreto":
        g.say("O coreto novo. Aos domingos a banda da escola toca aqui, mais ou menos no ritmo.")
    elif k == "peixaria":
        g.say("Peixaria do Píer: \"Peixe fresco da orla. Aqui o pescador recebe 10% a mais.\"")
    elif k == "monumento":
        g.say("\"Praça da Fundação Luthor. Construída pela cidade, para a cidade.\" Embaixo, em letras menores: "
              "\"Com a ajuda de uma CEO de mochila cheia.\"")
    else:
        return False
    return True


# ---------------------------------------------------------------------------
# Painel da Fundação
# ---------------------------------------------------------------------------
class Panel(ui.Modal):
    def __init__(self, g):
        self.g = g
        self.sel = 0
        for i, p in enumerate(PROJECTS):                    # começa no primeiro projeto em aberto
            if unlocked(g, p["key"]) and p["key"] not in g.fundacao["built"] and p["key"] not in g.fundacao["ready"]:
                self.sel = i
                break
        self.msg, self.msg_t, self.msg_col = "", 0.0, C_GREEN

    def say(self, msg, col=C_GREEN):
        self.msg, self.msg_t, self.msg_col = msg, 3.0, col

    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL:
            self.sel = (self.sel - ev.y) % len(PROJECTS)
            audio.sfx("move")
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(PROJECTS); audio.sfx("move")
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(PROJECTS); audio.sfx("move")
        elif ev.key in ui.CONFIRM:
            self.donate()
        elif ev.key in ui.CANCEL:
            self.done = True

    def status(self, p):
        f = self.g.fundacao
        if p["key"] in f["built"]:
            return "pronto", C_GREEN
        if p["key"] in f["ready"]:
            return "amanhã", C_GOLD
        if not unlocked(self.g, p["key"]):
            return "bloqueado", C_MUTED
        total = sum(n for _, n in p["items"])
        left = sum(n for _, n in remaining(self.g, p)[0])
        return f"{total - left}/{total}", C_LILAC

    def donate(self):
        g = self.g
        p = PROJECTS[self.sel]
        key = p["key"]
        f = g.fundacao
        if key in f["built"] or key in f["ready"]:
            self.say("Esse projeto já está completo. Obrigada!", C_MUTED)
            return
        if not unlocked(g, key):
            self.say("Termine os outros cinco projetos primeiro.", C_MUTED)
            audio.sfx("blip")
            return
        items, money = remaining(g, p)
        given = f["given"].setdefault(key, {})
        names = []
        for it, n in items:
            take = min(n, g.count_item(it))
            if take > 0:
                g.remove_item(it, take)
                given[it] = given.get(it, 0) + take
                names.append(f"{ITEMS[it]['name']} x{take}")
        if names:
            audio.sfx("gift")
            self.say("Doado: " + ", ".join(names) + ".")
        items, money = remaining(g, p)
        if not items and money:
            if g.money <= 0:
                self.say("Os itens estão completos. Falta o dinheiro." if names else "Você está sem dinheiro.", C_GOLD)
                return
            amount = min(money, g.money)

            def pay(i):
                if i != 0:
                    return
                g.money -= amount
                f["money"][key] = f["money"].get(key, 0) + amount
                audio.sfx("coin")
                self.say(f"Doado: ${amount}.")
                self.finish_if_done(p)
            g.push(ui.Choice(f"Doar ${amount} para a {p['name']}? (Falta ${money}.)", ["Doar", "Agora não"], pay))
            return
        if not names and items:
            self.say("Nada na mochila que este projeto precise.", C_MUTED)
            audio.sfx("blip")
            return
        self.finish_if_done(p)

    def finish_if_done(self, p):
        if complete(self.g, p) and p["key"] not in self.g.fundacao["ready"]:
            self.g.fundacao["ready"].append(p["key"])
            audio.sfx("reward")
            self.say(f"Projeto completo: {p['name']}! A obra fica pronta amanhã de manhã.", C_GOLD)

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)

    def draw(self, surf):
        g = self.g
        outer = pygame.Rect(0, 0, 900, 580)
        outer.center = (SCREEN_W // 2 - 50, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "Fundação Luthor", (outer.x + 28, outer.y + 16), 30, C_GOLD, bold=True)
        ui.text(surf, f"Dinheiro: ${g.money}", (outer.right - 28, outer.y + 26), 18, C_TEXT, right=True)
        # lista de projetos
        y = outer.y + 70
        for i, p in enumerate(PROJECTS):
            r = pygame.Rect(outer.x + 20, y, 330, 52)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            locked = not unlocked(g, p["key"])
            name = "???" if locked else p["name"]
            ui.text(surf, name, (r.x + 14, r.y + 8), 21, C_TEXT if i == self.sel else C_MUTED, bold=i == self.sel)
            tag, col = self.status(p)
            ui.text(surf, tag, (r.right - 12, r.y + 10), 18, col, right=True)
            if not locked:
                total = sum(n for _, n in p["items"])
                left = sum(n for _, n in remaining(g, p)[0])
                bar = pygame.Rect(r.x + 14, r.y + 36, r.w - 28, 6)
                pygame.draw.rect(surf, (40, 30, 56), bar, border_radius=3)
                frac = 1.0 if p["key"] in g.fundacao["built"] + g.fundacao["ready"] else (total - left) / total
                if frac > 0:
                    pygame.draw.rect(surf, C_GREEN if frac >= 1 else C_LILAC,
                                     (bar.x, bar.y, max(6, int(bar.w * frac)), bar.h), border_radius=3)
            y += 60
        # detalhes
        p = PROJECTS[self.sel]
        x0 = outer.x + 380
        if not unlocked(g, p["key"]):
            ui.text(surf, "Projeto final", (x0, outer.y + 70), 26, C_TEXT, bold=True)
            for i, ln in enumerate(ui.wrap("Complete os outros cinco projetos para descobrir o último.", 19, 480)):
                ui.text(surf, ln, (x0, outer.y + 110 + i * 24), 19, C_MUTED)
        else:
            ui.text(surf, p["name"], (x0, outer.y + 70), 26, C_TEXT, bold=True)
            ui.text(surf, p["place"].capitalize(), (x0, outer.y + 102), 17, C_LILAC)
            yy = outer.y + 130
            for ln in ui.wrap(p["desc"], 18, 480)[:3]:
                ui.text(surf, ln, (x0, yy), 18, C_MUTED)
                yy += 22
            yy += 10
            given = g.fundacao["given"].get(p["key"], {})
            full = p["key"] in g.fundacao["built"] + g.fundacao["ready"]
            for it, n in p["items"]:
                have = n if full else min(n, given.get(it, 0))
                ok = have >= n
                row = pygame.Rect(x0, yy, 480, 34)
                pygame.draw.rect(surf, (52, 38, 72) if not ok else (36, 62, 52), row, border_radius=6)
                surf.blit(art.item_icon(it, 2), (row.x + 6, row.y + 1))
                ui.text(surf, ITEMS[it]["name"], (row.x + 46, row.y + 7), 18, C_TEXT)
                ui.text(surf, f"{have}/{n}", (row.right - 110, row.y + 7), 18, C_GREEN if ok else C_GOLD, right=True)
                bag = g.count_item(it)
                if not ok:
                    ui.text(surf, f"mochila: {bag}", (row.right - 10, row.y + 8), 16,
                            C_GREEN if bag else C_MUTED, right=True)
                yy += 38
            if p.get("money"):
                paid = p["money"] if full else g.fundacao["money"].get(p["key"], 0)
                ok = paid >= p["money"]
                row = pygame.Rect(x0, yy, 480, 34)
                pygame.draw.rect(surf, (52, 38, 72) if not ok else (36, 62, 52), row, border_radius=6)
                ui.text(surf, "$", (row.x + 16, row.y + 5), 22, C_GOLD, bold=True)
                ui.text(surf, "Doação em dinheiro", (row.x + 46, row.y + 7), 18, C_TEXT)
                ui.text(surf, f"${paid}/${p['money']}", (row.right - 10, row.y + 7), 18, C_GREEN if ok else C_GOLD,
                        right=True)
                yy += 38
            yy += 6
            ui.text(surf, "Benefício:", (x0, yy), 18, C_PINK, bold=True)
            for i, ln in enumerate(ui.wrap(p["perk"], 18, 370)[:2]):
                ui.text(surf, ln, (x0 + 108, yy + i * 22), 18, C_TEXT)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (outer.centerx, outer.bottom - 64), 19, self.msg_col, bold=True, center=True)
        ui.text(surf, "Cima/baixo: projeto   E: doar o que estiver na mochila   Esc: sair",
                (outer.centerx, outer.bottom - 32), 16, C_MUTED, center=True)

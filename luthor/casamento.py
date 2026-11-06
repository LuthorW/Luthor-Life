"""Casamento: depois de um tempo morando junto, o anel de noivado, o pedido e a cerimônia com a cidade inteira.

1. Morando junto há pelo menos MIN_DAYS dias, o Anel de Noivado aparece no Mercado Central (com a Bea).
2. Dar o anel para quem mora com você marca o pedido: naquela noite (19h às 23h), no terraço da cobertura.
3. Depois do "sim", o casamento fica marcado para uma semana depois (nunca em dia de festa ou aniversário),
   das 15h às 19h, no Jardim do Mirante. A Sam celebra (tirou a licença pela internet).
4. Casadas: presentes da cidade ($2.000 e +50 de amizade com todo mundo), foto no álbum e falas novas.
"""
import random

import pygame

from . import art, festas, audio, ui
from .art import new, R, P, shade
from .characters import NPCS, ROMANCES
from .data import ITEMS, SHOPS
from .config import DAYS_PER_QUARTER, C_PINK, C_GOLD, C_GREEN

MIN_DAYS = 14
TITLES = {"casamento": "O casamento", "casamento_pedido": "O pedido de casamento",
          # só no modo de teste de cenas (--cenas)
          "casamento_pedido_lucy": "Pedido de casamento (Lucy)", "casamento_pedido_vittoria": "Pedido de casamento (Vittoria)",
          "casamento_lucy": "O casamento (Lucy)", "casamento_vittoria": "O casamento (Vittoria)"}
WEDDING_HOURS = (15 * 60, 19 * 60)
PROPOSAL_HOURS = (19 * 60, 23 * 60)
GARDEN = (97, 11)                     # Jardim do Mirante, em frente ao coreto

ITEMS["anel"] = dict(name="Anel de Noivado", kind="gift", price=3000, icon="ring", color=(240, 200, 90),
                     desc="Ouro e uma pedra roxa, da cor da Luthor Corp. Para quem já mora com você.")
if "anel" not in SHOPS["market"]["stock"]:
    SHOPS["market"]["stock"].append("anel")

_prev_icon = art._icon


def _icon_ring(kind, color):
    if kind != "ring":
        return _prev_icon(kind, color)
    s = new(16, 16)
    pygame.draw.circle(s, color, (8, 10), 5, 2)
    pygame.draw.circle(s, shade(color, 1.3), (7, 9), 5, 1)
    R(s, (150, 70, 220), 6, 2, 5, 4)                       # pedra roxa
    R(s, (210, 160, 255), 7, 2, 2, 2)
    P(s, (255, 255, 255), 7, 2)
    return s


art._icon = _icon_ring


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.casamento = dict(moved=None, proposal=False, proposal_day=-1, engaged=None, wedding=None, wedding_qd=None,
                       married=False, line_day=-1)


def save_state(g):
    return {"casamento": g.casamento}


def load_state(g, d):
    init_state(g)
    c = d.get("casamento") or {}
    for k in g.casamento:
        if k in c:
            g.casamento[k] = c[k]
    if g.casamento["wedding_qd"]:
        g.casamento["wedding_qd"] = list(g.casamento["wedding_qd"])
    if g.partner and g.casamento["moved"] is None:   # save de antes: começa a contar de hoje
        g.casamento["moved"] = g.abs_day()


def moved_in(g):
    """Chamado quando a parceira se muda para a cobertura."""
    g.casamento["moved"] = g.abs_day()


def days_together(g):
    m = g.casamento["moved"]
    return 0 if m is None else g.abs_day() - m


def married(g):
    return bool(getattr(g, "casamento", {}).get("married"))


def status(g, key):
    if key == g.partner and married(g):
        return "casadas"
    if key == g.partner and g.casamento["engaged"] is not None:
        return "noivas"
    return None


def can_buy_ring(g):
    if not g.partner:
        return False, "Bea: 'Anel de noivado? Primeiro mora junto, querida!'"
    if days_together(g) < MIN_DAYS:
        return False, f"Bea: 'Morem juntas mais um pouquinho. Daqui a {MIN_DAYS - days_together(g)} dia(s), quem sabe?'"
    if g.casamento["engaged"] is not None or g.casamento["proposal"]:
        return False, "Bea: 'Você já tem um anel, lembra? Só falta a festa!'"
    return True, ""


# ---------------------------------------------------------------------------
# Datas
# ---------------------------------------------------------------------------
def _step(year, q, d):
    d += 1
    if d > DAYS_PER_QUARTER:
        d, q = 1, q + 1
        if q > 4:
            q, year = 1, year + 1
    return year, q, d


def _pick_wedding(g):
    y, q, d = g.year, g.quarter, g.day
    for _ in range(7):
        y, q, d = _step(y, q, d)
    while festas.festival_on(q, d) or festas.birthday_keys(q, d):
        y, q, d = _step(y, q, d)
    return g.abs_day(y, q, d), [y, q, d]


def wedding_label(g):
    y, q, d = g.casamento["wedding_qd"]
    return f"dia {d} de {festas.season_name(q)}"


def wedding_today(g):
    return (g.partner and not married(g) and g.casamento["wedding"] is not None
            and g.casamento["wedding"] == g.abs_day())


# ---------------------------------------------------------------------------
# Ganchos
# ---------------------------------------------------------------------------
def give_ring(g, npc):
    """Presente "anel". Devolve True se tratou o presente."""
    key = npc.key
    d = NPCS[key]
    if key != g.partner:
        g.push(ui.Dialog(npc.name, ["Um anel de noivado? Letícia... isso é para alguém muito especial. Guarda."],
                         g.portrait_for(npc, "shy"), subtitle=d["role"]))
        return True
    if g.casamento["engaged"] is not None or g.casamento["proposal"]:
        g.say("O pedido já foi feito. Agora é só esperar o grande dia!")
        return True
    if days_together(g) < MIN_DAYS:
        g.push(ui.Dialog(npc.name, ["Isso é... um anel? Espera, guarda isso! A gente acabou de se mudar.",
                                    "Deixa a gente brigar pelo controle remoto primeiro. Depois você me pergunta."],
                         g.portrait_for(npc, "shy"), subtitle=d["role"]))
        return True
    g.remove_item("anel")
    g.casamento["proposal"] = True
    g.casamento["proposal_day"] = g.abs_day()
    audio.sfx("love")
    g.say(f"Você esconde o anel no bolso antes que {d['short']} perceba. Hoje à noite, no terraço da cobertura, "
          f"entre 19h e 23h. Vai ser lá.")
    g.toasts.push("Pedido de casamento: hoje, no terraço da cobertura (19h às 23h).", C_PINK)
    return True


def night(g, notes):
    c = g.casamento                                    # pedido que não aconteceu fica para a noite seguinte
    if c["wedding"] is not None and not c["married"] and c["wedding"] == g.abs_day() + 1 and g.partner:
        notes.append((f"Amanhã é o casamento! Jardim do Mirante, das 15h às 19h. A cidade inteira vai.", C_PINK))


def morning(g):
    c = g.casamento
    if wedding_today(g):
        g.toasts.push("Hoje é o seu casamento! Jardim do Mirante, entre 15h e 19h.", C_PINK)
    elif c["proposal"] and c["engaged"] is None:
        g.toasts.push("O anel continua no seu bolso: terraço da cobertura, entre 19h e 23h.", C_PINK)


def hud_lines(g):
    c = g.casamento
    out = []
    if c["proposal"] and c["engaged"] is None and g.partner:
        out.append(("Pedido de casamento: terraço da cobertura (19h-23h)", C_PINK))
    elif wedding_today(g) and g.minutes < WEDDING_HOURS[1]:
        out.append(("Seu casamento: Jardim do Mirante (15h-19h)", C_PINK))
    elif c["engaged"] is not None and not c["married"] and c["wedding_qd"]:
        out.append((f"Casamento: {wedding_label(g)}, no Jardim do Mirante", C_PINK))
    return out


def check(g):
    c = g.casamento
    key = g.partner
    if not key:
        return False
    if (c["proposal"] and c["engaged"] is None and g.map_name == "terrace"
            and PROPOSAL_HOURS[0] <= g.minutes <= PROPOSAL_HOURS[1]):
        def end():
            c["proposal"] = False
            c["engaged"] = g.abs_day()
            c["wedding"], c["wedding_qd"] = _pick_wedding(g)
            g.add_friendship(key, 150)
            g.toasts.push(f"Noivas! O casamento é no {wedding_label(g)}, no Jardim do Mirante.", C_PINK)
            g.player.place_tile(13, 6, "right")
        g.play_scene("casamento_pedido", proposal_scene(g, key), on_end=end)
        return True
    if wedding_today(g) and g.map_name == "city" and WEDDING_HOURS[0] <= g.minutes <= WEDDING_HOURS[1]:
        tx, ty = g.player.tile
        if abs(tx - GARDEN[0]) <= 12 and abs(ty - GARDEN[1]) <= 9:
            def end():
                c["married"] = True
                g.flags.add("casadas")
                g.money += 2000
                for k in NPCS:
                    g.add_friendship(k, 50)
                g.add_friendship(key, 200)
                audio.sfx("reward")
                g.toasts.push("Casadas! Presentes da cidade: $2.000 e muito carinho.", C_PINK)
                g.player.place_tile(97, 8, "down")
                for npc in g.npcs.values():
                    npc.snap_to_schedule(g.minutes)
            g.play_scene("casamento", wedding_scene(g, key), on_end=end)
            return True
    return False


MARRIED_LINES = {
    "lucy": ["Bom dia, esposa. Ainda não me acostumei a dizer isso. Vou dizer até acostumar.",
             "A Cat Grant mandou um cartão de casamento. Diz só: \"Finalmente.\" Típico.",
             "Lembra do pacto? Ninguém decide pela outra. Então eu decidi te perguntar: pizza ou sushi hoje?",
             "Eu ainda guardo o bilhete de Gotham. O que você não deixou. Agora a gente escreve os bilhetes juntas.",
             "Sabe a melhor matéria que eu já escrevi? Os votos. Nem precisou de revisão."],
    "vittoria": ["Buongiorno, moglie mia. Esposa. Eu ensaiei a semana inteira.",
                 "A nonna ia te adorar. Ela dizia: case com quem divide a sobremesa. Você divide.",
                 "Hoje eu desliguei o celular às oito. Vida, não só empresas. Lembra?",
                 "A Dona Graça ainda chora quando fala do casamento. E depois pede pra eu contar de novo.",
                 "Eu reservei a nossa mesa na Trattoria para todo aniversário de casamento. Até os noventa anos."],
}


def chat_line(g, npc):
    """Uma fala de casada por dia (na primeira conversa com a esposa)."""
    c = g.casamento
    if not married(g) or npc.key != g.partner or c["line_day"] == g.abs_day() or random.random() > 0.6:
        return None
    c["line_day"] = g.abs_day()
    pool = MARRIED_LINES.get(npc.key)
    return random.choice(pool) if pool else None


# ---------------------------------------------------------------------------
# Cenas
# ---------------------------------------------------------------------------
PROPOSAL = {
    "lucy": dict(
        before=["Você está estranha a noite toda. Mexendo no bolso. Eu sou repórter, Luthor, eu percebo.",
                "Se for uma matéria exclusiva, eu aceito. Se for uma notícia ruim... me conta logo."],
        answer=["...Você está me pedindo em casamento. No terraço. Com as luzinhas acesas.",
                "Lembra do pacto? Ninguém decide pela outra. Então eu decido: sim. Sim, sim, sim."],
        choices=[("Lucy Williams, você quer casar comigo?", 80, "Você ensaiou isso. Eu sei que ensaiou. Sim!"),
                 ("Eu fugi uma vez. Nunca mais. Casa comigo?", 90, "...Você não vai mais fugir. Eu não vou deixar. Sim."),
                 ("Isso é uma matéria exclusiva. Aceita?", 60, "A maior da minha carreira. Aceito.")]),
    "vittoria": dict(
        before=["Amore, você não tocou no vinho. Você SEMPRE toca no vinho. O que houve?",
                "Se é sobre o Gruppo Ricci comprar o prédio do lado, eu juro que ia te contar."],
        answer=["Isso é... um anel. Letícia. Você comprou um anel e não me deixou escolher o vinho da ocasião?",
                "Sim. Mil vezes sim. Vamos ter uma vida, lembra? Agora é para sempre."],
        choices=[("Vittoria Ricci, quer casar comigo?", 80, "Sim! Ai, eu vou chorar e borrar tudo. Sim!"),
                 ("Uma vida, não só empresas. Para sempre?", 90, "Para sempre. Com folgas, domingos e sobremesa."),
                 ("A Bea disse que era um bom investimento.", 55, "A Bea tem razão. É o melhor investimento da sua vida.")]),
}


def proposal_scene(g, key):
    d = PROPOSAL.get(key) or PROPOSAL["lucy"]
    steps = [
        ("ator", key, 15, 5, "left"), ("ator", "player", 13, 11, "up"),
        ("camera_ja", 13, 6), ("fade_in",),
        ("legenda", "Terraço da cobertura, noite", 2.0),
        ("andar", "player", 13, 5), ("virar", "player", "right"),
        ("fala", key, d["before"][0], "smile"),
        ("fala", key, d["before"][1]),
        ("emote", "player", "reticencias"),
        ("narra", "Você respira fundo, tira a caixinha do bolso e abre. A pedra roxa brilha com as luzinhas do terraço."),
        ("emote", key, "surpresa"),
        ("escolha", "O que dizer?", d["choices"]),
        ("fala", key, d["answer"][0], "shy"),
        ("fala", key, d["answer"][1], "love"),
        ("pulo", key),
        ("beijo", "player", key),
        ("efeito", "coracoes", 3),
        ("legenda", "Noivas!", 2.0),
        ("esperar", 0.6), ("fade_out",),
    ]
    return dict(map="terrace", time=max(g.minutes, 20 * 60), npc=key, steps=steps)


VOWS = {
    "lucy": ["Eu passei anos achando que você tinha ido embora porque não se importava.",
             "Hoje eu sei que você foi embora porque se importava demais. Então aqui vai o meu voto:",
             "Ninguém decide pela outra. Nada de segredos. E, quando der medo, a gente fica. Juntas."],
    "vittoria": ["Eu tinha medo de me apaixonar por alguém tão ocupada quanto eu.",
                 "Aí você apareceu às seis da manhã para varrer o chão da minha inauguração.",
                 "Prometo folgas, domingos e sobremesa dividida. Uma vida, não só empresas. Para sempre."],
}
MADRINHA = {"lucy": "nia", "vittoria": "graca"}
GUESTS = [(90, 11), (92, 11), (94, 11), (100, 11), (102, 11), (104, 11), (89, 12), (91, 12), (93, 12), (95, 12),
          (100, 12), (102, 12), (104, 12), (106, 12), (90, 13), (92, 13), (104, 13), (106, 13)]


def wedding_scene(g, key):
    mad = MADRINHA.get(key, "nia")
    special = {"sam", "jess", mad, key}
    guests = [k for k in NPCS if k not in special]
    steps = [("ator", "sam", 97, 6, "down"), ("ator", "jess", 95, 8, "up"), ("ator", mad, 100, 8, "up")]
    for k, (x, y) in zip(guests, GUESTS):
        steps.append(("ator", k, x, y, "up"))
    vows = VOWS.get(key) or VOWS["lucy"]
    steps += [
        ("ator", "player", 97, 15, "up"), ("ator", key, 98, 15, "up"),
        ("camera_ja", 97, 11), ("fade_in",),
        ("legenda", "Jardim do Mirante, o grande dia", 2.4),
        ("efeito", "petalas", 4),
        ("andar_", key, 98, 8), ("andar", "player", 97, 8),
        ("andar_", key, 98, 7), ("andar", "player", 96, 7),
        ("virar", "player", "right"), ("virar", key, "left"),
        ("fala", "sam", "Boa tarde a todos. Eu tirei a licença de celebrante pela internet ontem. É válida. Eu conferi três vezes.",
         "happy"),
        ("emote", "brainy", "gota"),
        ("fala", "sam", "Eu conheço a Letícia há muitos anos. Já vi essa mulher enfrentar conselho, tio e mercado em queda."),
        ("fala", "sam", "Nunca vi ela tão nervosa quanto hoje. Então já sabemos que é amor.", "smile"),
        ("emote", "player", "vergonha"),
        ("fala", "sam", "Os votos. Noiva número um, a CEO. Sem slides, por favor."),
        ("escolha", "Seus votos:", [
            ("\"Você é a melhor decisão que eu já tomei. E eu tomo decisão o dia inteiro.\"", 80,
             "...Isso foi muito você. E foi perfeito."),
            ("\"Eu prometo chegar em casa antes das dez. Na maioria das vezes.\"", 60,
             "Na maioria das vezes. Está gravado, todo mundo ouviu!"),
            ("\"Eu escolheria você de novo, todos os dias, em qualquer cidade.\"", 90,
             "Em qualquer cidade. Eu também. Eu também."),
        ]),
        ("fala", key, vows[0], "love"),
        ("fala", key, vows[1], "smile"),
        ("fala", key, vows[2], "love"),
        ("emote", "graca", "triste") if mad != "graca" else ("emote", "bea", "triste"),
        ("fala", "sam", "Pelo poder que a internet me deu: eu vos declaro casadas. Pode beijar a noiva. As duas podem.", "happy"),
        ("beijo", "player", key),
        ("efeito", "confete", 3),
        ("efeito", "coracoes", 3),
        ("emote", mad, "coracao"), ("emote", "jess", "coracao"), ("emote", "barry", "estrela"),
        ("fala", "barry", "Todo mundo olhando pra cá! Essa vai para o álbum. E para a capa!", "happy"),
        ("legenda", "Casadas!", 2.6),
        ("esperar", 0.8), ("fade_out",),
    ]
    return dict(map="city", time=max(g.minutes, 17 * 60), weather="sol", npc=key, steps=steps)


def replay_scene(g, k):
    """Rever cenas: o pedido e a cerimônia com a esposa de hoje."""
    key = g.partner or "lucy"
    return proposal_scene(g, key) if k == "casamento_pedido" else wedding_scene(g, key)

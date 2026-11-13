"""Casamento: pedido, noivado, cerimônia e vida de casadas."""
import random
import pygame
from . import art, festas, audio, ui
from .art import new, R, P, shade
from .characters import NPCS, ROMANCES
from .data import ITEMS, SHOPS
from .config import DAYS_PER_QUARTER, C_PINK, C_GOLD, C_GREEN
MIN_DAYS = 14
TITLES = {"casamento": "O casamento", "casamento_pedido": "O pedido de casamento",
          "casamento_pedido_lucy": "Pedido de casamento (Lucy)", "casamento_pedido_vittoria": "Pedido de casamento (Vittoria)",
          "casamento_lucy": "O casamento (Lucy)", "casamento_vittoria": "O casamento (Vittoria)"}
WEDDING_HOURS = (15 * 60, 19 * 60)
PROPOSAL_HOURS = (19 * 60, 23 * 60)
GARDEN = (97, 11)
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
    R(s, (150, 70, 220), 6, 2, 5, 4)
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
    if g.partner and g.casamento["moved"] is None:
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
        return False, "Bea: 'Você já tem um anel, lembra? Agora só falta o grande dia!'"
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
    from . import surpresa
    while festas.festival_on(q, d) or festas.birthday_keys(q, d) or (q, d) == surpresa.BDAY:
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
    """Presente 'anel'. Devolve True se tratou o presente."""
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
    c = g.casamento
    if c["wedding"] is not None and not c["married"] and c["wedding"] == g.abs_day() + 1 and g.partner:
        notes.append(("Amanhã é o casamento! Jardim do Mirante, das 15h às 19h. A cidade inteira vai.", C_PINK))
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
# ---------------------------------------------------------------------------
# Falas depois do casamento
# ---------------------------------------------------------------------------
MARRIED_LINES = {
    "lucy": [
        "Bom dia, esposa. Ainda não me acostumei a dizer isso. Vou dizer até acostumar.",
        "A Cat Grant mandou um cartão de casamento. Diz só: \"Finalmente.\" Típico.",
        "Lembra do pacto? Ninguém decide pela outra. Então eu decidi te perguntar: pizza ou sushi hoje?",
        "Eu ainda guardo o bilhete de Gotham. O que você não deixou. Agora a gente escreve os bilhetes juntas.",
        "Sabe a melhor matéria que eu já escrevi? Os votos. Nem precisou de revisão.",
        "Acho que vou continuar te chamando de Luthor. É meu apelido favorito para minha esposa.",
        "Hoje quero uma noite sem pauta, sem prazo e sem celular. Só nós duas."
    ],
    "vittoria": [
        "Buongiorno, moglie mia. Esposa. Eu ensaiei a semana inteira.",
        "A nonna ia te adorar. Ela dizia: case com quem divide a sobremesa. Você divide.",
        "Hoje eu desliguei o celular às oito. Vida, não só empresas. Lembra?",
        "A Dona Graça ainda chora quando fala do casamento. E depois pede pra eu contar de novo.",
        "Eu reservei a nossa mesa na Trattoria para todo aniversário de casamento. Até os noventa anos.",
        "Hoje o Gruppo Ricci pode esperar. Minha esposa tem prioridade na agenda.",
        "Você sabe que a receita da nonna agora também é sua, não sabe?"
    ],
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
        before=[
            "Você está estranha a noite toda. Olhou para o relógio umas quatro vezes e não para de mexer no bolso.",
            "Eu sou repórter, Luthor. Percebo quando alguém está escondendo alguma coisa. Mas espero que seja uma surpresa boa."
        ],
        answer=[
            "Você está me pedindo em casamento... Aqui, no nosso terraço, com essas luzes todas.",
            "Eu passei tanto tempo imaginando como seria ter você de volta na minha vida. E agora posso imaginar o resto dela também. Sim. Claro que sim."
        ],
        choices=[
            ("Lucy Freya Williams, quer construir o resto da vida comigo?", 80, "Você ensaiou esse discurso. Aposto que até escreveu versões diferentes. Sim!"),
            ("Eu não quero mais deixar o medo decidir por nós. Casa comigo?", 90, "Então vamos decidir juntas. Hoje, amanhã e todos os dias. Sim!"),
            ("Prometo que essa é a única pergunta que não vou transformar numa reunião.", 60, "Ainda bem, porque minha resposta é sim. E não precisa colocar em ata.")
        ]),
    "vittoria": dict(
        before=[
            "Amore, você está quieta demais. E ainda não tocou no vinho. Isso é muito suspeito.",
            "Se está tentando organizar alguma surpresa, espero que tenha deixado espaço para sobremesa."
        ],
        answer=[
            "Letícia... é um anel. Você realmente preparou tudo isso sem me contar?",
            "Eu quero dividir os dias tranquilos, os dias corridos, as refeições improvisadas e todos os planos que ainda vamos fazer. Sim. Quero casar com você."
        ],
        choices=[
            ("Vittoria Sophia Ricci, quer se casar comigo?", 80, "Sì! Sim! Mil vezes sim!"),
            ("Quero uma vida com você. Não só nossos negócios, nossos planos ou nossas agendas.", 90, "Uma vida inteira. E prometo reservar espaço para muitos jantares a dois."),
            ("A Bea disse que era um bom investimento. Eu concordei.", 55, "A Bea tem razão. Esse é o melhor investimento da minha vida.")
        ])
}
def proposal_scene(g, key):
    d = PROPOSAL.get(key) or PROPOSAL["lucy"]
    steps = [
        ("ator", key, 15, 5, "left"),
        ("ator", "player", 13, 11, "up"),
        ("camera_ja", 13, 6),
        ("fade_in",),
        ("legenda", "Terraço da cobertura, noite", 2.0),
        ("andar", "player", 13, 5),
        ("virar", "player", "right"),
        ("fala", key, d["before"][0], "smile"),
        ("fala", key, d["before"][1]),
        ("fala", "player", "Eu passei o dia tentando encontrar as palavras certas. Acho que nenhuma delas vai ser suficiente."),
        ("emote", "player", "reticencias"),
        ("esperar", 1.3),
        ("narra", "Você respira fundo, tira a caixinha do bolso e abre. A pedra roxa brilha com as luzinhas do terraço."),
        ("emote", key, "surpresa"),
        ("esperar", 1.3),
        ("fala", "player", "Eu não consigo prometer que tudo será perfeito. Mas posso prometer que não vou esconder de você quando tiver medo, nem tomar decisões que pertencem a nós duas."),
        ("escolha", "O que dizer?", d["choices"]),
        ("fala", key, d["answer"][0], "shy"),
        ("fala", key, d["answer"][1], "love"),
        ("fala", "player", "Então está decidido. Vamos fazer isso juntas."),
        ("pulo", key),
        ("beijo", "player", key),
        ("efeito", "coracoes", 3),
        ("legenda", "Noivas!", 2.0),
        ("esperar", 0.8),
        ("fade_out",),
    ]
    return dict(map="terrace", time=max(g.minutes, 20 * 60), npc=key, steps=steps)
VOWS = {
    "lucy": [
        "Eu prometo nunca mais deixar que o silêncio decida por nós.",
        "Prometo perguntar, escutar e confiar que você pode dividir comigo até as partes mais difíceis.",
        "E, quando a vida mudar de rumo, quero que a gente escolha o caminho lado a lado. Eu escolho você, Letícia. Todos os dias."
    ],
    "vittoria": [
        "Eu prometo continuar construindo coisas ao seu lado, mas sem esquecer de aproveitar o que já temos.",
        "Prometo dividir as responsabilidades, as alegrias, as preocupações e, naturalmente, a sobremesa.",
        "Quero uma vida cheia de planos, mas com espaço para mudar de ideia. Você é minha casa, Letícia. Sempre."
    ],
}
MADRINHA = {"lucy": "nia", "vittoria": "graca"}
GUESTS = [
    (90, 11), (92, 11), (94, 11), (100, 11), (102, 11), (104, 11),
    (89, 12), (91, 12), (93, 12), (95, 12), (100, 12), (102, 12),
    (104, 12), (106, 12), (90, 13), (92, 13), (104, 13), (106, 13)
]
def wedding_scene(g, key):
    mad = MADRINHA.get(key, "nia")
    special = {"sam", "jess", mad, key}
    guests = [k for k in NPCS if k not in special]
    steps = [
        ("ator", "sam", 97, 6, "down"),
        ("ator", "jess", 95, 8, "up"),
        ("ator", mad, 100, 8, "up")
    ]
    for k, (x, y) in zip(guests, GUESTS):
        steps.append(("ator", k, x, y, "up"))
    vows = VOWS.get(key) or VOWS["lucy"]
    steps += [
        ("ator", "player", 97, 15, "up"),
        ("ator", key, 98, 15, "up"),
        ("camera_ja", 97, 11),
        ("fade_in",),
        ("legenda", "Jardim do Mirante, o grande dia", 2.4),
        ("efeito", "petalas", 4),
        ("andar_", key, 98, 8),
        ("andar", "player", 97, 8),
        ("andar_", key, 98, 7),
        ("andar", "player", 96, 7),
        ("virar", "player", "right"),
        ("virar", key, "left"),
        ("fala", "sam", "Boa tarde a todos! Obrigada por estarem aqui para celebrar essas duas pessoas tão importantes para mim."),
        ("fala", "sam", "Eu conheço a Letícia desde antes de ela comandar a Luthor Corp, antes das reuniões e dos conselhos. Conheço a pessoa por trás de todos esses títulos."),
        ("fala", "sam", "E hoje eu tenho o privilégio de estar aqui não como amiga que dá conselhos, mas como a celebrante que vai oficializar essa escolha."),
        ("fala", "sam", "Prometo tentar não fazer um discurso enorme. Sei que a Letícia gosta de reuniões objetivas."),
        ("emote", "brainy", "gota"),
        ("esperar", 1.3),
        ("fala", "sam", "Mas não prometo nada. Uma ocasião dessas merece algumas palavras a mais."),
        ("fala", "sam", "Letícia, você passou muito tempo tentando carregar tudo sozinha. Hoje, olha ao seu lado. Você não precisa fazer isso nunca mais."),
        ("fala", "sam", "E você, noiva, obrigada por escolher caminhar com ela. Sei o quanto isso significa."),
        ("fala", "sam", "Agora vamos aos votos. Noiva número um, a CEO. Sem slides, por favor."),
        ("emote", "player", "vergonha"),
        ("esperar", 1.3),
        ("escolha", "O que Letícia promete?", [
            ("\"Você é a melhor decisão que eu já tomei. E eu tomo decisão o dia inteiro.\"", 80, "...Isso foi muito você. E foi perfeito."),
            ("\"Eu prometo chegar em casa antes das dez. Na maioria das vezes.\"", 60, "Na maioria das vezes. Está gravado, todo mundo ouviu!"),
            ("\"Eu escolheria você de novo, todos os dias, em qualquer cidade.\"", 90, "Em qualquer cidade. Eu também. Eu também.")
        ]),
        ("fala", key, vows[0], "love"),
        ("fala", key, vows[1], "smile"),
        ("fala", key, vows[2], "love"),
        ("emote", mad, "triste"),
        ("esperar", 1.3),
        ("fala", "sam", "Então, diante das pessoas que vocês escolheram para estar aqui, chegou a hora de fazer a pergunta mais importante."),
        ("fala", "sam", "Vocês escolhem uma à outra, hoje e em todos os dias que vierem?"),
        ("fala", "player", "Escolho."),
        ("fala", key, "Escolho. Com tudo o que sou."),
        ("fala", "sam", "Pelo poder que a internet me deu — e pela alegria de poder chamar vocês de família — eu vos declaro casadas!"),
        ("fala", "sam", "Pode beijar a noiva. As duas podem."),
        ("beijo", "player", key),
        ("efeito", "confete", 3),
        ("efeito", "coracoes", 3),
        ("emote", mad, "coracao"),
        ("esperar", 1.3),
        ("emote", "jess", "coracao"),
        ("esperar", 1.3),
        ("emote", "barry", "estrela"),
        ("esperar", 1.3),
        ("fala", "jess", "Eu sabia que esse dia ia ser lindo. Mas acho que ninguém aqui estava preparado para ver vocês duas assim."),
        ("fala", "barry", "Todo mundo olhando pra cá! Essa vai para o álbum. E para a capa!"),
        ("fala", "sam", "Agora chega de cerimônia. Quero ver essas duas aproveitando a festa!"),
        ("legenda", "Casadas!", 2.6),
        ("esperar", 0.8),
        ("fade_out",)
    ]
    return dict(map="city", time=max(g.minutes, 17 * 60), weather="sol", npc=key, steps=steps)
def replay_scene(g, k):
    """Rever o pedido ou a cerimônia; os sufixos permitem testar Lucy e Vittoria separadamente."""
    if k.endswith("_lucy"):
        key = "lucy"
    elif k.endswith("_vittoria"):
        key = "vittoria"
    else:
        key = g.partner or "lucy"
    if k.startswith("casamento_pedido"):
        return proposal_scene(g, key)
    return wedding_scene(g, key)
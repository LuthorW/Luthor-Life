"""Degustação de vinhos com a Vittoria, na sala de degustação da sede do Gruppo Ricci.

Na adega (1,8 do mapa `ricci`), com a Vittoria na sede e pelo menos 2 corações com ela: uma vez por semana.
As duas sentam à mesa de prova (cadeiras 1,10 e 4,10) e a Vittoria serve três taças. Para cada uma ela descreve a cor,
o aroma, o corpo e dá uma pista da região; a Letícia escolhe entre três nomes. Acertar dá mais amizade (+30, errar
+10: nunca tira), culinária e, com 2 ou mais acertos, uma garrafa de Vinho Tinto. Os três certos pela primeira vez:
flag `sommelier`, conquista e manchete na CatCo.

Estado em `g.degust` (last, count, best).
"""
import random

from . import audio, habilidades, noticias, ui
from .config import C_GREEN, C_GOLD, C_MUTED

MIN_HEARTS = 2
EVERY = 7                 # dias entre uma degustação e outra
ROOM = "ricci"

# nome, cor, aroma, boca, pista da região, curiosidade
WINES = [
    ("Chianti Classico", "rubi brilhante", "cereja e violeta", "médio, com acidez boa para massa",
     "da Toscana, entre Florença e Siena", "O galo preto no gargalo é o símbolo da região."),
    ("Barolo", "granada clara, quase alaranjada na borda", "rosa seca e alcatrão", "encorpado, taninos firmes",
     "do Piemonte, no norte", "Chamam de rei dos vinhos. A minha nonna dizia que é um rei mal-humorado."),
    ("Brunello di Montalcino", "rubi escuro", "ameixa, couro e um pouco de tabaco", "encorpado e longo",
     "de uma cidadezinha num morro da Toscana", "Fica anos no barril antes de sair. Paciência de italiano."),
    ("Prosecco", "palha bem clarinho, com bolhas finas", "maçã verde e pera", "leve e espumante",
     "do Vêneto, perto de Veneza", "É o que eu sirvo na inauguração de cada casa nova."),
    ("Amarone", "quase preto", "uva-passa, chocolate e cereja madura", "muito encorpado, quente",
     "do Vêneto, perto de Verona", "As uvas secam em esteiras de palha antes de virar vinho."),
    ("Malbec", "violeta intensa", "amora e baunilha", "encorpado, mas macio",
     "de Mendoza, do outro lado dos Andes", "O intruso da noite: o único que não é italiano."),
    ("Pinot Noir", "rubi transparente, dá para ler através dele", "morango e cogumelo", "leve e delicado",
     "da Borgonha, na França", "A uva mais difícil de cultivar. E a mais teimosa."),
    ("Moscato d'Asti", "dourado", "pêssego e flor de laranjeira", "docinho e frisante",
     "do Piemonte, para a sobremesa", "Tem pouco álcool. A Dona Graça toma com o pudim."),
]

INTRO = [
    "Você veio! Senta, a mesa de prova já está pronta. Três taças, três vinhos, nenhum rótulo.",
    "Hoje eu escolhi três garrafas que contam uma história. Vamos ver se você escuta.",
    "Regra da casa: primeiro olha, depois cheira, depois prova. E nada de espiar a adega.",
]
RIGHT = ["Isso! Você tem nariz.", "Acertou! Eu sabia que você ia pegar esse.", "Perfeito. Dona Graça ia aplaudir."]
WRONG = ["Quase! Era o {w}.", "Não... era o {w}. Mas foi um bom palpite.", "Esse engana todo mundo: era o {w}."]
END = {
    3: "Três de três. Letícia Luthor, você está proibida de abrir uma vinícola. Eu não aguento a concorrência.",
    2: "Dois de três! Já dá para escolher o vinho do nosso jantar. Leva essa garrafa, é presente.",
    1: "Um acerto. Ninguém nasce sommelier. Semana que vem tem mais.",
    0: "Nenhum, mas você riu em todos. Isso também é degustação. Volta semana que vem?",
}


def init_state(g):
    g.degust = dict(last=-99, count=0, best=0)


def save_state(g):
    return {"degust": g.degust}


def load_state(g, d):
    init_state(g)
    for k, v in (d.get("degust") or {}).items():
        if k in g.degust:
            g.degust[k] = v


def _vittoria_here(g):
    n = g.npcs.get("vittoria")
    return n is not None and n.map == ROOM


def available(g):
    """(pode, motivo)"""
    if not _vittoria_here(g):
        return False, "A Vittoria faz as degustações quando está aqui na sede. Volte em horário de expediente."
    if g.hearts("vittoria") < MIN_HEARTS:
        return False, "Vittoria: \"Degustação é para os clientes da casa. Volta mais vezes na Trattoria e a gente marca.\""
    wait = EVERY - (g.abs_day() - g.degust["last"])
    if wait > 0:
        return False, f"Vittoria: \"A próxima degustação é daqui a {wait} dia(s). Eu preciso escolher as garrafas.\""
    return True, ""


def object_label(g, o):
    if o.kind == "adega" and g.map_name == ROOM:
        return "Degustação com a Vittoria" if available(g)[0] else "Adega"
    return None


def use_object(g, o):
    if o.kind != "adega" or g.map_name != ROOM:
        return False
    ok, why = available(g)
    if not ok:
        from .lugares import FLAVOR
        g.push(ui.Dialog("", [FLAVOR["adega"], why]))
        return True
    audio.sfx("confirm")
    g.push(ui.Choice("Fazer a degustação com a Vittoria? (uma por semana)", ["Vamos!", "Agora não"],
                     lambda i: start(g) if i == 0 else None))
    return True


def scene(g, wines=None, rnd=random):
    """Monta a cena da degustação (três taças) com as escolhas e o placar."""
    wines = wines or rnd.sample(WINES, 3)
    score = {"n": 0}

    def hit(_g):
        score["n"] += 1

    steps = [
        ("ator", "vittoria", 4, 10, "left"), ("ator", "player", 1, 10, "right"),
        ("sentar", "vittoria"), ("sentar", "player"),
        ("camera_ja", 3, 10), ("fade_in",),
        ("fala", "vittoria", rnd.choice(INTRO), "happy"),
    ]
    for i, w in enumerate(wines):
        name, cor, aroma, boca, regiao, fato = w
        others = rnd.sample([x[0] for x in WINES if x[0] != name], 2)
        opts = others + [name]
        rnd.shuffle(opts)
        steps += [
            ("segurar", "vittoria", "taca_vinho"), ("segurar", "player", "taca_vinho"),
            ("fala", "vittoria", f"Taça {i + 1}. Olha a cor: {cor}. Agora o nariz: {aroma}."),
            ("beber", "player"),
            ("fala", "vittoria", f"Na boca, {boca}. E uma pista: ele vem {regiao}."),
            ("escolha", "Qual é o vinho?",
             [(o, 30, rnd.choice(RIGHT) + " " + fato, "happy", hit) if o == name else
              (o, 10, rnd.choice(WRONG).format(w=name) + " " + fato, "smile") for o in opts]),
        ]

    def finish(gg):
        n = score["n"]
        _reward(gg, n)
        out = [("fala", "vittoria", END[n], "love" if n >= 2 else "happy")]
        if n >= 2:
            out.append(("brinde", "player", "vittoria"))
        return out

    steps += [("chamar", finish), ("esperar", 0.4), ("fade_out",)]
    return dict(map=ROOM, npc="vittoria", steps=steps), score


def _reward(g, n):
    d = g.degust
    d["last"] = g.abs_day()
    d["count"] += 1
    first_perfect = n == 3 and d["best"] < 3
    d["best"] = max(d["best"], n)
    habilidades.gain(g, "culinaria", 10 + 10 * n)
    if n >= 2:
        if g.add_item("vinho"):
            g.toasts.push("A Vittoria te deu uma garrafa de Vinho Tinto.", C_GOLD, "vinho")
        else:
            g.toasts.push("Mochila cheia: a garrafa de vinho ficou com a Vittoria.", C_MUTED)
    if first_perfect:
        g.flags.add("sommelier")
        noticias.event(g, "sommelier")
        g.toasts.push("Paladar de sommelier! Três vinhos certos.", C_GREEN)


def start(g):
    sc, _ = scene(g)
    g.play_scene("degustacao", scene=sc, remember=False)

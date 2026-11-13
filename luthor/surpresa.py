"""Aniversário da Letícia: festa surpresa no terraço da cobertura (dia 8 do verão).

- De manhã a Jess manda uma mensagem inocente ("passa no terraço às 20h? não é trabalho, prometo").
- Durante o dia, quem conversa com a Letícia deseja feliz aniversário (e jura que não sabe de nada).
- Das 19h às 23h, ao chegar no terraço: "SURPRESA!". Vêm as amigas com 2+ corações (a namorada sempre),
  confete, parabéns, um presente de cada uma e bolo. Tudo dá amizade; nada tira.
- Se a Letícia não aparecer, ninguém fica bravo: no dia seguinte a Jess entrega um pedaço de bolo.
"""
import random

from . import ui, audio, festas, celular, noticias
from .characters import NPCS, NPC_ORDER
from .data import ITEMS
from .config import C_PINK, C_GOLD, C_GREEN, C_LILAC

BDAY = (2, 8)                       # (trimestre, dia): verão, dia 8 (o dia depois do Luau)
START, END = 19 * 60, 23 * 60
MAX_GUESTS = 9
HOST = "jess"

# o que cada uma dá de presente (item, fala curta ao entregar)
GIFTS = {
    "sam": ("suculenta", "Uma suculenta. Ela sobrevive a qualquer agenda. Igual a você."),
    "brainy": ("quebra_cabeca", "Um quebra-cabeça de mil peças. Eu já cronometrei: você monta em três dias."),
    "jess": ("caneta_tinteiro", "Uma caneta-tinteiro. Para assinar contratos com estilo. E cartões de agradecimento."),
    "rafa": ("cafe_especial", "Café especial, torra da casa. Rotulei: \"só para a aniversariante\"."),
    "lucy": ("vinil", "Um vinil. Aquele que a gente ouvia em Gotham. Achei num sebo e quase chorei no caixa."),
    "vittoria": ("vinho", "Um vinho da safra do ano em que você nasceu. Tive que ligar para três amigos na Itália."),
    "nia": ("aquarela", "Uma aquarela do terraço. Eu sonhei com essa vista antes de pintar."),
    "barry": ("porta_retrato", "Um porta-retrato com a foto da equipe. Saiu tremida. A felicidade tremia."),
    "theo": ("livro", "Um livro raro, primeira edição. Prometa que não vai ler no banho."),
    "bea": ("girassois", "Girassóis! Os mais altos do mercado. Brigaram comigo por eles."),
    "graca": ("bolo", "Bolo de fubá, minha filha. Aniversariante não cozinha, só come."),
    "marco": ("whisky", "Um single malt guardado para ocasiões especiais. Esta é uma."),
    "joca": ("mel", "Mel de abelha do sítio do meu compadre. Adoça até reunião de conselho."),
    "ian": ("miniatura_veleiro", "Um veleirinho de madeira, igual ao que a gente fazia nas férias no interior."),
    "celeste": ("lenco_seda", "Um lenço de seda, feito à mão. Em Lyon, presente de aniversário se usa no mesmo dia."),
    "yang": ("chocolate_belga", "Chocolate belga. Não é sentimental. É só chocolate bom. ...Feliz aniversário."),
    "meredith": ("cha_ervas", "Chá de ervas. Para os dias difíceis. E para os bons também."),
    "milany": ("kit_cuidado", "Um kit de cuidados. Receita médica: um dia de folga por mês."),
    "izzie": ("macarons", "Macarons! Fiz de seis sabores. Os de pistache já eram, desculpa, testei muito."),
    "addison": ("perfume", "Um perfume. Elegante, discreto e marcante. Como alguém que eu conheço."),
}
DEFAULT_GIFT = ("chocolate_belga", "Feliz aniversário, Letícia!")

# falas do dia (a primeira conversa com cada uma): ninguém entrega a surpresa
DAY_LINES = [
    "Feliz aniversário, Letícia! ...Hoje à noite? Não, não tenho nada marcado. Por quê?",
    "Parabéns! Muitos anos de vida, muitos produtos lançados e pouquíssimas reuniões.",
    "Feliz aniversário! E não, eu não sei de nada. De nada mesmo. Para de me olhar assim.",
    "Hoje é o seu dia! Aproveita. E... passa no terraço mais tarde. Digo, se quiser. Tanto faz. Tchau!",
    "Parabéns, Letícia! Quantos anos? Não responde, CEO não tem idade, tem mandato.",
    "Feliz aniversário! Eu ia te dar o presente agora, mas... depois. Depois é melhor.",
]
SPECIAL_DAY = {
    "jess": "Feliz aniversário, chefe! Bloqueei a sua agenda depois das 19h. Motivo: \"assuntos pessoais\". Não pergunta.",
    "lucy": "Feliz aniversário. Eu tinha um discurso pronto, mas você me olhou e eu esqueci. Depois eu lembro. Hoje à noite, talvez.",
    "vittoria": "Buon compleanno, tesoro! Não posso falar muito agora, estou... ocupada. Com coisas. De trabalho. Ciao!",
    "sam": "Parabéns! A Ruby fez um cartão com glitter. Cuidado: o glitter vai morar na sua bolsa para sempre.",
    "brainy": "Feliz aniversário! Hoje à noite eu... não posso dizer. Eu sou péssimo guardando segredo. Esquece que eu falei \"hoje à noite\".",
    "graca": "Parabéns, minha filha! Que Deus te dê saúde e juízo. Juízo principalmente.",
}

JESS_MSG = ("Chefe, feliz aniversário! A sua agenda está livre depois das 19h. Passa no terraço da cobertura lá pelas "
            "20h? Preciso te mostrar uma coisa. Não é trabalho. Prometo.",
            [("Uma coisa? Que coisa?", "Uma coisa. Às 20h. No terraço. Não pense demais. (Você vai pensar demais.)"),
             ("Combinado. Obrigada, Jess.", "Não precisa agradecer ainda! Quer dizer... de nada. Até mais tarde!"),
             ("Isso está com cara de surpresa.", "Surpresa? Que surpresa? Eu nem sei o que é essa palavra. Até às 20h!")])
celular.REPLIES_FOR[JESS_MSG[0]] = JESS_MSG[1]


# --- estado -----------------------------------------------------------------
def init_state(g):
    g.surpresa = dict(done=[], said=[], hint=0, missed=[])


def save_state(g):
    return {"surpresa": g.surpresa}


def load_state(g, d):
    init_state(g)
    s = d.get("surpresa") or {}
    for k in ("done", "said", "missed"):
        g.surpresa[k] = list(s.get(k, []))
    g.surpresa["hint"] = int(s.get("hint", 0))


def is_today(g):
    return (g.quarter, g.day) == BDAY


def done(g):
    return g.year in g.surpresa["done"]


def active(g):
    return is_today(g) and START <= g.minutes < END and not done(g)


def guests(g):
    """A namorada (ou quem mora junto) sempre; depois as amigas com mais corações (2+). Mínimo: Jess e Sam."""
    first = [k for k in (g.partner, g.dating) if k]
    rest = sorted((k for k in NPC_ORDER if k not in first and g.hearts(k) >= 2),
                  key=lambda k: (-g.hearts(k), NPC_ORDER.index(k)))
    out = []
    for k in first + rest:
        if k not in out:
            out.append(k)
    for k in (HOST, "sam"):
        if k not in out:
            out.append(k)
    if HOST in out:                      # a Jess organiza: sempre aparece
        out.remove(HOST)
        out.insert(0, HOST)
    return out[:MAX_GUESTS]


# --- conversa, HUD, calendário e agenda -------------------------------------
def chat_line(g, npc):
    if not is_today(g) or done(g) or g.hearts(npc.key) < 1:
        return None
    tag = f"{g.year}:{npc.key}"
    if tag in g.surpresa["said"]:
        return None
    g.surpresa["said"].append(tag)
    line = SPECIAL_DAY.get(npc.key)
    if not line:
        line = DAY_LINES[(NPC_ORDER.index(npc.key) + g.year) % len(DAY_LINES)]
    return line


def hud_lines(g):
    if not is_today(g) or done(g) or g.minutes >= END:
        return []
    if g.surpresa["hint"] == g.year:
        return [("Seu aniversário! A Jess pediu: terraço da cobertura, 20h", C_PINK)]
    return [("Hoje é o seu aniversário!", C_PINK)]


def _cal(g, q, d, year):
    return [("Seu aniversário!", C_PINK)] if (q, d) == BDAY else []


def _agenda(g, y, q, d):
    return [("Seu aniversário!", C_PINK)] if (q, d) == BDAY else []


festas.CAL_EXTRA.append(_cal)
celular.AGENDA_EXTRA.append(_agenda)
noticias.EXTRA_EVENTS["aniversario"] = (70, "Festa surpresa no terraço da Luthor",
                                        "Os amigos da CEO organizaram uma festa surpresa no terraço da cobertura. "
                                        "Fontes confirmam: ela fingiu que não desconfiava de nada.")


def morning(g):
    if not is_today(g) or done(g):
        return
    g.toasts.push("Hoje é o seu aniversário, Letícia!", C_PINK)
    if g.surpresa["hint"] != g.year:
        g.surpresa["hint"] = g.year
        celular._send(g, HOST, JESS_MSG[0])


def night(g, notes):
    """Se a festa passou sem a Letícia, a Jess guarda bolo (sem bronca)."""
    y, q, d = g.date_from_abs(g.abs_day() - 1)
    if (q, d) == BDAY and y not in g.surpresa["done"] and y not in g.surpresa["missed"]:
        g.surpresa["missed"].append(y)
        g.add_item("bolo")
        g.add_friendship(HOST, 20)
        notes.append(("A turma te esperou no terraço ontem à noite... A Jess guardou um pedaço de bolo para você "
                      "(está na mochila). Feliz aniversário atrasado!", C_PINK))


# --- a cena ------------------------------------------------------------------
# lugares no terraço (em volta do centro, virados para onde a Letícia para: 10,7). Tudo na metade de cima,
# para a caixa de fala não tapar ninguém.
SPOTS = [(10, 5), (8, 5), (12, 5), (7, 6), (13, 6), (9, 3), (11, 3), (6, 5), (14, 5), (15, 6)]
STOP = (10, 7)


def _face(x, y, tx, ty):
    dx, dy = tx - x, ty - y
    return ("right" if dx > 0 else "left") if abs(dx) > abs(dy) else ("down" if dy > 0 else "up")


def scene(g):
    m = g.world["terrace"]
    keys = guests(g)
    spots = [p for p in SPOTS if not m.is_solid(*p)]
    placed = list(zip(keys, spots))
    sx, sy = STOP
    lover = next((k for k in (g.partner, g.dating) if k and k in dict(placed)), None)
    steps = []
    for k, (x, y) in placed:
        steps.append(("ator", k, x, y, _face(x, y, sx, sy)))
    steps += [
        ("ator", "player", 10, 11, "up"),
        ("camera_ja", 10, 6),
        ("fade_in",),
        ("legenda", "Terraço da cobertura", 1.6),
        ("andar", "player", sx, sy),
        ("fala", HOST, "SURPRESAAA!", "happy"),
        ("efeito", "confete", 3),
    ]
    for k, _ in placed[1:6]:
        steps.append(("emote", k, random.choice(["feliz", "estrela", "coracao", "musica"])))
    steps += [
        ("emote", "player", "surpresa"),
        ("fala", "player", "Vocês... Isso tudo é pra mim?"),
        ("fala", HOST, "Feliz aniversário, chefe! Eu bloqueei a sua agenda, a Sam fez a planilha da festa e o "
                       "resto da turma trouxe o resto.", "happy"),
    ]
    if lover:
        steps += [
            ("andar", lover, sx + 1, sy),
            ("virar", lover, "left"), ("virar", "player", "right"),
            ("fala", lover, "Você achou mesmo que a gente ia deixar passar? Feliz aniversário, amor.", "love"),
            ("beijo", "player", lover),
            ("efeito", "coracoes", 2),
            ("virar", "player", "up"),
        ]
    steps += [
        ("escolha", "O que dizer para todo mundo?", [
            ("Eu não desconfiei de nada. ...Tá, só um pouquinho.", 20, "Um pouquinho? A Jess mandou mensagem com 'prometo'. Ninguém promete nada às 7h."),
            ("Obrigada. De verdade. Eu não sei nem o que dizer.", 30, "Então não diz nada. Sopra as velas!"),
            ("Quem foi que deixou o Brainy guardar o segredo?", 20, "Ele contou para três pessoas e um pombo. Mas deu certo!"),
        ]),
        ("narra", "Alguém apaga as luzes do terraço. A Jess aparece com um bolo cheio de velas, e todo mundo "
                  "canta parabéns, desafinado e feliz."),
        ("efeito", "brilhos", 2),
        ("narra", "Você fecha os olhos, faz um pedido e sopra as velas de uma vez só."),
        ("efeito", "confete", 2),
    ]
    for k, _ in placed[:5]:
        steps.append(("fala", k, GIFTS.get(k, DEFAULT_GIFT)[1], "happy"))
    if len(placed) > 5:
        steps.append(("narra", "E os presentes continuam chegando, um mais caprichado que o outro."))
    steps += [
        ("fala", "player", "Obrigada, gente. Esse é o melhor aniversário que eu já tive."),
        ("efeito", "coracoes", 2),
        ("esperar", 0.8),
        ("legenda", "A festa vai até tarde...", 1.8),
        ("fade_out",),
    ]
    return dict(map="terrace", time=max(START, min(g.minutes, END - 30)), weather="sol", npc=HOST, steps=steps), [k for k, _ in placed]


def _finish(g, who):
    g.surpresa["done"].append(g.year)
    got = []
    for k in who:
        item, _ = GIFTS.get(k, DEFAULT_GIFT)
        if item in ITEMS and g.add_item(item):
            got.append(ITEMS[item]["name"])
        g.add_friendship(k, 40)
    g.energy = g.max_energy
    g.minutes = max(g.minutes, 22 * 60 + 30)
    for n in g.npcs.values():
        n.check_schedule(g.minutes)
    noticias.event(g, "aniversario")
    g.stats["aniversarios"] = g.stats.get("aniversarios", 0) + 1
    audio.sfx("reward")
    g.toasts.push(f"Presentes de aniversário: {len(got)} (estão na mochila)", C_GOLD)
    g.toasts.push("Energia cheia e amizade com todo mundo que veio!", C_GREEN)


def check(g):
    if g.map_name != "terrace" or not active(g):
        return False
    sc, who = scene(g)
    g.play_scene("aniversario_leticia", sc, on_end=lambda: _finish(g, who), remember=False)
    return True


def _test_scene(g):
    return scene(g)[0]


from . import scenetest  # noqa: E402  (lista do modo de teste de cenas)
scenetest.DYNAMIC["aniversario_leticia"] = _test_scene

"""Vida a dois e ciúmes leves.

- Morando junto (depois do pingente): café da manhã juntas em algumas manhãs (sempre no fim de semana),
  pequenos pedidos do dia a dia (sem castigo se não der) e o aniversário de namoro, a cada ano do jogo
  (4 estações = 56 dias), com um jantar especial. O aniversário também vale para quem só namora.
- Ciúmes leves entre a Lucy e a Vittoria: se a Letícia der muito mais atenção a uma, a outra comenta.
  Todas as respostas são boas: nunca tira amizade.
"""
import random

from . import ui, audio
from .config import DAYS_PER_QUARTER, C_PINK, C_GOLD, C_MUTED
from .characters import NPCS, ROMANCES
from .data import ITEMS

YEAR_DAYS = 4 * DAYS_PER_QUARTER


def other(key):
    return next((k for k in ROMANCES if k != key), None)


# --- estado ------------------------------------------------------------------
def init_state(g):
    g.casal = dict(since=None, wish=None, last_wish=None, breakfast=False, anniv=[],
                   attn={k: [] for k in ROMANCES}, jealous={k: -99 for k in ROMANCES}, used=[])


def save_state(g):
    return {"casal": g.casal}


def load_state(g, d):
    init_state(g)
    c = d.get("casal") or {}
    for k in ("since", "wish", "last_wish", "breakfast"):
        if k in c:
            g.casal[k] = c[k]
    g.casal["anniv"] = list(c.get("anniv", []))
    g.casal["used"] = list(c.get("used", []))
    for k in ROMANCES:
        g.casal["attn"][k] = [list(e) for e in c.get("attn", {}).get(k, [])]
        g.casal["jealous"][k] = c.get("jealous", {}).get(k, -99)
    if g.dating and g.casal["since"] is None:      # save de antes: o namoro passa a contar de hoje
        g.casal["since"] = g.abs_day()


def start_dating(g, key):
    g.casal["since"] = g.abs_day()


def _pick(g, tag, pool):
    """Fala sem repetir até acabarem as opções."""
    used = g.casal["used"]
    fresh = [ln for ln in pool if f"{tag}|{ln}" not in used]
    if not fresh:
        for ln in pool:
            if f"{tag}|{ln}" in used:
                used.remove(f"{tag}|{ln}")
        fresh = list(pool)
    ln = random.choice(fresh)
    used.append(f"{tag}|{ln}")
    return ln


# ===========================================================================
# Aniversário de namoro
# ===========================================================================
def anniversary_today(g):
    """Quantos anos de namoro fazem hoje (0 = hoje não é aniversário)."""
    s = g.casal.get("since")
    if s is None or not g.dating:
        return 0
    n = g.abs_day() - s
    return n // YEAR_DAYS if n > 0 and n % YEAR_DAYS == 0 else 0


def anniversary_on(g):
    """(trimestre, dia) do aniversário de namoro, para o calendário."""
    s = g.casal.get("since")
    if s is None or not g.dating:
        return None
    _, q, d = g.date_from_abs(s)
    return (q, d)


def since_year(g):
    s = g.casal.get("since")
    return g.date_from_abs(s)[0] if s is not None else 9999


def dinner_place(g, key):
    if g.partner == key:                            # morando junto: jantar no terraço, com as luzinhas
        return ("terrace", 15, 5, "left", "um jantar no terraço da cobertura")
    m, x, y, d, desc = NPCS[key]["date_places"][0]
    return (m, x, y, d, desc)


def _anniv_tag(g):
    return f"{g.dating}:{g.abs_day()}"


def override(g, npc):
    """Na noite do aniversário de namoro ela espera no lugar do jantar (18h às 23h). Morando junto, ela já
    está em casa à noite (a cena no terraço começa quando a Letícia chega na cobertura)."""
    if npc.key != g.dating or npc.key == g.partner or not anniversary_today(g) or _anniv_tag(g) in g.casal["anniv"]:
        return
    m, x, y, d, _ = dinner_place(g, npc.key)
    start, end = 18 * 60, 23 * 60
    sch = npc.schedule
    last = None
    for e in sch:
        if e[0] <= end:
            last = e
    new_s = [e for e in sch if e[0] < start] + [(start, m, x, y, d)]
    if last is not None:
        new_s.append((end, last[1], last[2], last[3], last[4]))
    new_s += [e for e in sch if e[0] > end]
    npc.schedule = new_s


ANNIV = {
    "lucy": ["Feliz aniversário de namoro, Luthor. Investiguei bastante e descobri o lugar perfeito pra comemorar. Fontes confiáveis.",
             "Sabe o que eu pensei hoje? Que a gente quase se perdeu lá em Gotham. E olha a gente aqui. Eu escolheria você de novo, todas as vezes."],
    "vittoria": ["Feliz aniversário, amore. Eu reservei tudo, escolhi o vinho e desliguei o celular. Sim, o celular do Gruppo Ricci também.",
                 "Quando a gente começou, eu tinha medo de me apaixonar por alguém tão ocupada quanto eu. Hoje eu só tenho medo de o jantar esfriar."],
}
ANNIV_CHOICES = {
    "lucy": [("Você é a melhor coisa que me aconteceu.", 60, "Para. Você vai me fazer chorar antes da sobremesa."),
             ("Que venham muitos outros anos.", 50, "Muitos. Eu já estou anotando tudo na agenda."),
             ("Eu trouxe uma coisa... meu coração. Brega demais?", 40, "Brega demais. Eu amei.")],
    "vittoria": [("Você é a melhor coisa que me aconteceu.", 60, "Ah, Letícia... e você é a minha."),
                 ("Que venham muitos outros anos.", 50, "Muitos, sim. Com folgas. Nós prometemos, lembra?"),
                 ("Eu trouxe uma coisa... meu coração. Brega demais?", 40, "Bregíssimo. Perfetto.")],
}


def _beside(g, m, x, y):
    gmap = g.world[m]
    for (dx, dy, face) in ((-1, 0, "right"), (1, 0, "left"), (0, 1, "up"), (0, -1, "down")):
        if not gmap.is_solid(x + dx, y + dy):
            return x + dx, y + dy, face
    return x, y + 1, "up"


def anniversary_scene(g, key, n):
    m, x, y, d, desc = dinner_place(g, key)
    lines = ANNIV.get(key) or ["Feliz aniversário de namoro.", "Eu escolheria você de novo."]
    title = f"{n} ano de namoro" if n == 1 else f"{n} anos de namoro"
    if m == "terrace":
        start = [("ator", key, 15, 5, "left"), ("ator", "player", 13, 11, "up"), ("camera_ja", 13, 6),
                 ("fade_in",), ("legenda", title, 2.2), ("andar", "player", 13, 5), ("virar", "player", "right")]
    else:
        px, py, pd = _beside(g, m, x, y)
        start = [("ator", key, x, y, d), ("ator", "player", px, py, pd), ("camera_ja", x, y), ("fade_in",),
                 ("legenda", title, 2.2),
                 ("virar", key, {"left": "right", "right": "left", "up": "down", "down": "up"}[pd])]
    steps = start + [
        ("fala", key, lines[0], "love"),
        ("fala", "player", "Feliz aniversário pra nós."),
        ("emote", key, "vergonha"),
        ("fala", key, lines[1], "love"),
        ("escolha", "O que dizer?", ANNIV_CHOICES.get(key, [("Eu te amo.", 50, "Eu também te amo.")])),
        ("fala", key, "Ah, e isso é pra você. Abre!", "happy"),
        ("narra", "Ela te entrega um porta-retrato com uma foto das duas, rindo, num dia qualquer."),
        ("beijo", "player", key),
        ("efeito", "coracoes", 3),
        ("esperar", 1.0),
        ("fade_out",),
    ]
    return dict(map=m, time=max(g.minutes, 19 * 60), npc=key, steps=steps)


def check(g):
    """Jantar de aniversário: toca quando a Letícia chega ao lugar marcado, entre 18h e 23h."""
    n = anniversary_today(g)
    key = g.dating
    if not n or _anniv_tag(g) in g.casal["anniv"] or not (18 * 60 <= g.minutes <= 23 * 60):
        return False
    m, x, y, d, _ = dinner_place(g, key)
    if g.map_name != m and not (m == "terrace" and g.map_name == "home"):
        return False
    if m == "city":
        tx, ty = g.player.tile
        if abs(tx - x) + abs(ty - y) > 10:
            return False
    g.casal["anniv"].append(_anniv_tag(g))

    def end():
        g.add_friendship(key, 150)
        g.add_item("porta_retrato")
        g.toasts.push(f"Aniversário de namoro com {NPCS[key]['short']}: ganhou um Porta-retrato!", C_PINK, "porta_retrato")
        npc = g.npcs[key]
        npc.snap_to_schedule(g.minutes)
    g.play_scene("aniversario_namoro", anniversary_scene(g, key, n), on_end=end, remember=False)
    return True


def gift_bonus(g, key, taste):
    """Presente no dia do aniversário de namoro vale mais."""
    if key == g.dating and anniversary_today(g):
        mult = {"love": 3, "like": 3, "neutral": 2, "dislike": 1}[taste]
        return mult, "No nosso aniversário? Você é impossível. Eu amei.", f"Presente de aniversário de namoro: x{mult}!"
    return 1, None, None


# ===========================================================================
# Café da manhã juntas
# ===========================================================================
BREAKFAST = {
    "lucy": ["Bom dia, Luthor. Panqueca com mel ou com mais mel? Não aceito 'só café' como resposta.",
             "Acordei cedo e escrevi meia matéria. A outra metade depende de um beijo de bom dia.",
             "Você roncou. Pouquinho. Vou guardar essa informação pra uma chantagem futura.",
             "Fiz o café do jeito que você gosta: forte o suficiente pra enfrentar o conselho da Luthor Corp.",
             "Li as manchetes de hoje. Nenhuma sobre a Luthor Corp. Dia tranquilo, pelo visto!",
             "Sabe o que eu mais gosto de morar com você? Ninguém me julga por comer panqueca às seis da manhã."],
    "vittoria": ["Buongiorno, amore. Café, croissant e uma laranja. Café da manhã de quem quer viver muito.",
                 "Acordei pensando no cardápio de outono. Depois pensei em você. Nessa ordem, mas por muito pouco.",
                 "Não fui eu que fiz os croissants, foi a padaria da esquina. Mas eu escolhi com muito amor.",
                 "Hoje tenho três reuniões e uma inauguração. Mas os primeiros vinte minutos do dia são seus.",
                 "Você fica linda com essa cara de sono. Não conta pra ninguém que eu disse isso.",
                 "Lá em casa, na Itália, café da manhã era corrido. Com você eu gosto de demorar."],
}
PLAYER_BREAKFAST = ["Bom dia pra você também.", "Isso cheira bem demais pra uma manhã de trabalho.",
                    "Se eu me atrasar, a culpa é sua.", "Eu podia me acostumar com isso.",
                    "Você é a melhor parte da manhã.", "Cinco minutinhos e eu já vou."]
BREAKFAST_FOOD = {"lucy": "panquecas", "vittoria": "croissant"}


def breakfast_scene(g, key):
    line = _pick(g, f"cafe_{key}", BREAKFAST.get(key, ["Bom dia!"]))
    steps = [
        ("ator", key, 22, 4, "up"),
        ("ator", "player", 16, 4, "right"),
        ("camera_ja", 20, 5),
        ("fade_in",),
        ("legenda", "Café da manhã", 1.6),
        ("andar", "player", 20, 4),
        ("virar", key, "left"),
        ("emote", key, "feliz"),
        ("fala", key, line, "love"),
        ("fala", "player", random.choice(PLAYER_BREAKFAST)),
        ("beijo", "player", key),
        ("efeito", "coracoes", 2),
        ("esperar", 0.6),
        ("fade_out",),
    ]
    return dict(map="home", time=g.minutes + 20, npc=key, steps=steps)


def morning(g):
    """Começo do dia (depois do resumo da noite): café da manhã e o pedido do dia."""
    key = g.partner
    w = g.casal.get("wish")
    if key and w and not w.get("done"):
        g.toasts.push(f"{NPCS[key]['short']} pediu: {w['text']}.", C_PINK)
    if not key or not g.casal.get("breakfast") or g.map_name != "home":
        return
    g.casal["breakfast"] = False

    def end():
        g.minutes = max(g.minutes, 6 * 60 + 30)
        g.player.place_tile(20, 4, "right")
        food = BREAKFAST_FOOD.get(key)
        g.add_friendship(key, 20)
        if food in ITEMS and g.add_item(food):
            g.toasts.push(f"Café da manhã com {NPCS[key]['short']}: ela embrulhou {ITEMS[food]['name']} pra você!",
                          C_PINK, food)
        note(g, key, 1)
    g.play_scene("cafe_da_manha", breakfast_scene(g, key), on_end=end, remember=False)


# ===========================================================================
# Pequenos pedidos do dia a dia
# ===========================================================================
WISHES = {
    "lucy": [("item", "cappuccino", 1, "um cappuccino do Grão Nobre"),
             ("item", "policial", 1, "um livro policial novo"),
             ("item", "flores", 1, "flores para a mesa da sala"),
             ("item", "chocolate_belga", 1, "uma caixinha de chocolate"),
             ("visit", None, 0, "uma visita no trabalho dela, só para dar um oi"),
             ("home", None, 0, "que você chegue em casa entre 19h e 22h para ver um filme")],
    "vittoria": [("item", "girassois", 1, "girassóis para a cozinha"),
                 ("item", "vinho", 1, "um vinho para o jantar"),
                 ("item", "fish", 1, "um peixe fresco para o jantar"),
                 ("item", "tomate", 3, "3 tomates do mercado"),
                 ("visit", None, 0, "uma visita no trabalho dela, para almoçarem juntas"),
                 ("home", None, 0, "que você chegue em casa entre 19h e 22h para jantarem juntas")],
}
WISH_THANKS = {
    "lucy": ["Você lembrou! Viu? É por isso que eu te amo. E pelo café. Mas principalmente por isso.",
             "Entregue com sucesso. Cinco estrelas para o serviço de entregas da CEO."],
    "vittoria": ["Grazie, amore! Você é perfeita, sabia?",
                 "Você lembrou... isso vale mais do que qualquer presente caro."],
}
WISH_VISIT = {"lucy": "Você veio! A redação inteira vai fofocar agora. ...Deixa eles.",
              "vittoria": "Você veio me ver! Senta, tem uma mesa reservada pra você. Sempre tem."}
WISH_HOME = {"lucy": "Você chegou cedo! Pipoca, coberta e um filme de detetive. Perfeito.",
             "vittoria": "Você chegou! O jantar está quase pronto. Senta, eu sirvo."}


def _new_wish(g, key):
    opts = [w for w in WISHES.get(key, []) if w[0] != "item" or w[1] == "fish" or w[1] in ITEMS]
    opts = [w for w in opts if w[3] != g.casal.get("last_wish")] or opts
    if not opts:
        return None
    kind, item, qty, text = random.choice(opts)
    g.casal["last_wish"] = text
    return dict(kind=kind, item=item, qty=qty, text=text, done=False)


def _reward(g, npc, line):
    key = npc.key
    g.casal["wish"]["done"] = True
    g.add_friendship(key, 60)
    audio.sfx("love")
    g.toasts.push(f"Pedido de {NPCS[key]['short']} atendido: +amizade", C_PINK)
    g.push(ui.Dialog(npc.name, [line], g.portrait_for(npc, "love"), subtitle=npc.data["role"]))
    note(g, key, 1)


def talk(g, npc):
    """Entrega do pedido do dia ao conversar (como os pedidos dos e-mails). True se tratou a conversa."""
    w = g.casal.get("wish")
    if not w or w.get("done") or npc.key != g.partner:
        return False
    if w["kind"] == "item":
        have = g.count_fish() if w["item"] == "fish" else g.count_item(w["item"])
        if have < w["qty"]:
            return False
        if w["item"] == "fish":
            g.remove_fish(w["qty"])
        else:
            g.remove_item(w["item"], w["qty"])
        _reward(g, npc, _pick(g, f"obg_{npc.key}", WISH_THANKS.get(npc.key, ["Obrigada!"])))
        return True
    if w["kind"] == "visit" and npc.map not in ("home", "terrace", None):
        _reward(g, npc, WISH_VISIT.get(npc.key, "Você veio me ver!"))
        return True
    return False


def tick(g):
    w = g.casal.get("wish")
    key = g.partner
    if (key and w and not w.get("done") and w["kind"] == "home" and 19 * 60 <= g.minutes <= 22 * 60
            and g.map_name in ("home", "terrace") and not g.modals):
        _reward(g, g.npcs[key], WISH_HOME.get(key, "Você chegou!"))


# ===========================================================================
# Ciúmes leves (Lucy e Vittoria)
# ===========================================================================
JEALOUS = {
    "lucy": {
        "livre": ["Então... a Vittoria Ricci, hein? Um passarinho da CatCo me contou que você virou cliente VIP da Trattoria.",
                  "Vi você e a Vittoria no calçadão. Ela ri de tudo que você fala ou eu é que sou observadora demais? Repórter, sabe como é."],
        "junto": ["Não tô com ciúmes. Só tô anotando quantas vezes você passou na Trattoria essa semana. Por motivos jornalísticos.",
                  "A Vittoria é ótima, eu sei. Só me promete que ainda sou eu que ganho o último café do dia?"],
        "replies": ["...Tá bom, essa foi boa. Ponto pra você, Luthor.",
                    "Eu sei. Só gosto de ver você se explicar.",
                    "Fofa?! Eu sou uma jornalista séria. ...Que bom que você achou fofo."],
    },
    "vittoria": {
        "livre": ["Vi você e a Lucy Williams rindo no Grão Nobre. Ela é encantadora... não que eu esteja contando, eh.",
                  "A repórter da CatCo de novo? Hm. Dizem que ela faz perguntas demais. Eu prefiro responder com comida."],
        "junto": ["Você anda muito com a Lucy, cara mia. Não é ciúme. É só... um pouquinho de ciúme. Italiano, sabe?",
                  "Eu confio em você, de verdade. Mas da próxima vez que for ao café com a Lucy, me traz um cannoli, sim?"],
        "replies": ["Ah, Letícia. Assim você me desarma.",
                    "Eu sei, eu sei. Esquece. Já passou.",
                    "Fofa? Eu? Hmph. ...Talvez um pouquinho."],
    },
}
JEALOUS_COOLDOWN = 4            # dias entre um comentário e outro
ATTN_DAYS = 3                   # janela de atenção que conta


def note(g, key, w):
    """Registra atenção dada a uma das românticas (conversa 1, presente 2-3, encontro/dança 3)."""
    if key in ROMANCES:
        g.casal["attn"][key].append([g.abs_day(), w])


def score(g, key):
    today = g.abs_day()
    return sum(w for d, w in g.casal["attn"].get(key, []) if 0 <= today - d < ATTN_DAYS)


def jealous_chat(g, npc):
    """Se a Letícia deu muito mais atenção à outra, ela comenta (de leve). True se tratou a conversa."""
    x = npc.key
    y = other(x)
    if x not in ROMANCES or y is None:
        return False
    if y in (g.dating, g.partner) or g.hearts(x) < 3:
        return False                                # se a Letícia namora a outra, ela respeita
    today = g.abs_day()
    if today - g.casal["jealous"].get(x, -99) < JEALOUS_COOLDOWN:
        return False
    close = x in (g.dating, g.partner)
    sy, sx = score(g, y), score(g, x)
    if sy < (3 if close else 4) or sy < sx + 2:
        return False
    g.casal["jealous"][x] = today
    data = JEALOUS[x]
    comment = _pick(g, f"ciume_{x}_{'junto' if close else 'livre'}", data["junto" if close else "livre"])
    opts = [("Você é especial pra mim, sabia?", 40 if close else 30),
            ("Somos só amigas. Juro.", 25),
            ("Ciúmes, é? Que fofa.", 20)]

    def pick(i):
        pts = opts[i][1]
        g.add_friendship(x, pts)
        g.push(ui.Dialog(npc.name, [data["replies"][i]], g.portrait_for(npc, "love" if i == 0 else "happy"),
                         subtitle=npc.data["role"]))

    def ask():
        g.push(ui.Choice(f"{npc.data['short']}", [o[0] for o in opts], pick))
    g.push(ui.Dialog(npc.name, [comment], g.portrait_for(npc, "shy"), on_close=ask, subtitle=npc.data["role"]))
    return True


# ===========================================================================
# Noite e HUD
# ===========================================================================
def night(g, notes, passed_out):
    """Depois que o dia vira (process_night)."""
    today = g.abs_day()
    for k in ROMANCES:
        g.casal["attn"][k] = [e for e in g.casal["attn"][k] if today - e[0] < 7]
    key = g.partner
    g.casal["wish"] = None
    g.casal["breakfast"] = False
    if key:
        if random.random() < 0.65:
            g.casal["wish"] = _new_wish(g, key)
            if g.casal["wish"]:
                notes.append((f"{NPCS[key]['short']} pediu: {g.casal['wish']['text']}.", C_PINK))
        g.casal["breakfast"] = not passed_out and (g.weekday >= 5 or random.random() < 0.35)
    n = anniversary_today(g)
    if n:
        m, x, y, d, desc = dinner_place(g, g.dating)
        where = desc
        anos = "1 ano" if n == 1 else f"{n} anos"
        notes.append((f"Hoje faz {anos} de namoro com {NPCS[g.dating]['short']}! Jantar especial: {where}, "
                      f"entre 18h e 23h. Presente hoje vale 3x.", C_PINK))


def hud_lines(g):
    out = []
    w = g.casal.get("wish")
    if g.partner and w and not w.get("done"):
        txt = w["text"]
        if w["kind"] == "item":
            have = g.count_fish() if w["item"] == "fish" else g.count_item(w["item"])
            txt += f" ({min(have, w['qty'])}/{w['qty']})"
        out.append((f"Pedido da {NPCS[g.partner]['short']}: {txt}", C_PINK))
    n = anniversary_today(g)
    if n and _anniv_tag(g) not in g.casal["anniv"] and g.minutes <= 23 * 60:
        m, x, y, d, desc = dinner_place(g, g.dating)
        where = "terraço da cobertura" if m == "terrace" else desc
        out.append((f"Aniversário de namoro: {where} (18h a 23h)", C_PINK))
    return out

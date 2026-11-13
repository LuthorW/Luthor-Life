"""Notícias que reagem ao que a Letícia faz.

Toda noite o jogo compara o estado de agora com o da noite anterior (`snapshot`) e escreve as manchetes da CatCo do
dia seguinte: lançamentos, peixes lendários, namoro, mudança, casamento, obras da Fundação, a ação LCORP disparando,
o bichinho novo, a entrevista na CatCo TV... Coisas que não dá para descobrir comparando (o nome do produto lançado,
a degustação perfeita, a visita à pediatria) entram pelo `event` na hora em que acontecem.

As manchetes aparecem:
- no resumo da noite ("Na capa da CatCo hoje: ...");
- na banca de jornais (70,15), no jornal da TV e no bloco "CatCo" dos e-mails;
- em algumas falas (REACTIVE) da Nia, do Barry, da Lucy e do Harry;
- no arquivo da CatCo, depois que as matérias antigas acabam.

Estado em `g.noticias` (snap, feed, events). Saves antigos: a primeira noite só tira a foto do estado, sem manchetes.
"""
import random

from . import ui, dialogue
from .config import C_LILAC
from .data import ITEMS, FISH, NEWS
from .characters import NPCS

FEED_MAX = 40


def init_state(g):
    g.noticias = dict(snap={}, feed=[], events=[], total=0)


def save_state(g):
    return {"noticias": g.noticias}


def load_state(g, d):
    init_state(g)
    for k, v in (d.get("noticias") or {}).items():
        if k in g.noticias:
            g.noticias[k] = v


# Acontecimentos novos que viram manchete (módulos novos registram): tipo -> (prioridade, título, texto)
EXTRA_EVENTS = {}


def event(g, kind, **data):
    """Algo que aconteceu hoje e vira notícia amanhã (lançamento, degustação, pediatria...)."""
    ev = dict(kind=kind, **data)
    g.noticias["events"].append(ev)


# ---------------------------------------------------------------------------
# Foto do estado e diferenças
# ---------------------------------------------------------------------------
def snapshot(g):
    pet = getattr(g, "pet", None)
    return dict(
        fish=sorted(g.fish_caught), dating=g.dating, partner=g.partner,
        flags=sorted(f for f in g.flags if f in FLAG_NEWS),
        built=list(getattr(g, "fundacao", {}).get("built", [])),
        stock=g.stock, earned=g.stats.get("earned", 0),
        pet=getattr(pet, "name", None) if pet else None,
        interviews=getattr(g, "catco", {}).get("interviews", 0),
    )


def _name(key):
    return NPCS[key]["short"] if key in NPCS else key


# flags que viram manchete: (prioridade, título, texto)
FLAG_NEWS = {
    "casadas": (100, "Casamento do ano no Jardim do Mirante",
                "Letícia Luthor e {p} disseram sim diante da cidade inteira. A Sam celebrou; a Jess chorou duas vezes, "
                "segundo fontes."),
    "luthor_livre": (95, "A Luthor Corp é de Letícia",
                     "Conrad e Edmund Luthor vendem as ações depois da votação do conselho. A CEO promete \"menos sombra, "
                     "mais laboratório\"."),
    "celeste_desfile": (70, "Desfile ao pôr do sol no píer",
                        "Celeste Waite levou La Boutique para a areia. Na primeira fila, de óculos escuros: a CEO da "
                        "Luthor Corp."),
}
LAUNCH = [
    ("Luthor Corp lança {item}", "O laboratório da Luthor Corp colocou {item} no mercado. As primeiras unidades "
                                 "esgotaram antes do almoço."),
    ("Novidade da Luthor Corp: {item}", "A CEO apresentou {item} pessoalmente. O Brainy pediu para não ser fotografado. "
                                        "Foi fotografado."),
    ("{item} chega às lojas", "Fila na porta da Luthor Corp. Os analistas dizem que {item} é \"a cara de National City\"."),
]


def _diff(g, old, new):
    """Lista de (prioridade, tipo, título, texto)."""
    out = []
    p = g.partner or g.dating
    for f in new["flags"]:
        if f not in old.get("flags", []):
            pr, t, x = FLAG_NEWS[f]
            out.append((pr, f, t, x.format(p=_name(p) if p else "a noiva")))
    if new["dating"] and new["dating"] != old.get("dating"):
        x = (f"Letícia Luthor e {_name(new['dating'])} foram vistas de mãos dadas na orla. As duas não quiseram "
             "comentar. Sorriram muito, isso sim.")
        if new["dating"] == "lucy":
            x += " Nota da redação: a repórter Lucy Williams se recusou a revisar esta matéria."
        out.append((90, "namoro", "Coluna social: é namoro!", x))
    if new["partner"] and new["partner"] != old.get("partner"):
        out.append((85, "mudanca", "Caminhão de mudança no Residencial Luthor",
                    f"{_name(new['partner'])} agora mora na cobertura da CEO. Os vizinhos garantem: as caixas tinham "
                    "mais livros que roupas."))
    new_fish = [f for f in new["fish"] if f not in old.get("fish", []) and f in FISH]
    legend = [f for f in new_fish if FISH[f].get("legendary")]
    for f in legend:
        out.append((80, "lenda", "Lenda fisgada!",
                    f"A CEO Letícia Luthor pescou um {ITEMS[f]['name']}. O Barry tirou a foto e jura que não tem montagem."))
    others = [f for f in new_fish if f not in legend]
    if others:
        names = ", ".join(ITEMS[f]["name"] for f in others[:3])
        out.append((30, "pesca", "Pescaria da CEO",
                    f"Letícia Luthor foi vista no píer com uma vara e um balde: {names}. A peixaria agradece."))
    from . import fundacao
    projs = {pj["key"]: pj for pj in getattr(fundacao, "PROJECTS", [])}
    for k in new["built"]:
        if k not in old.get("built", []) and k in projs:
            pj = projs[k]
            out.append((75, "fundacao", f"Fundação Luthor entrega: {pj['name']}",
                        f"A obra ficou pronta {pj.get('place', 'na cidade')}. Os moradores já estão usando."))
    if new["interviews"] > old.get("interviews", 0):
        out.append((58, "entrevista", "CEO no CatCo ao Vivo",
                    "A entrevista de Letícia Luthor foi a mais vista da semana na CatCo TV. O corte de cabelo também "
                    "virou assunto."))
    d = round(new["stock"] - old.get("stock", new["stock"]), 2)
    if d >= 3:
        out.append((55, "alta", "LCORP dispara",
                    f"A ação da Luthor Corp subiu $ {d:.2f} num dia e fechou a $ {new['stock']:.2f}.".replace(".", ",")))
    elif d <= -3:
        out.append((40, "baixa", "LCORP recua",
                    f"A ação da Luthor Corp caiu $ {-d:.2f}. Analistas pedem calma. A Sam também.".replace(".", ",")))
    earned = new["earned"] - old.get("earned", new["earned"])
    if earned >= 3000:
        out.append((45, "vendas", "Dia de recorde na Luthor Corp",
                    f"As vendas da Luthor Corp passaram de $ {earned:,} num único dia.".replace(",", ".")))
    if new["pet"] and new["pet"] != old.get("pet"):
        out.append((50, "bichinho", "A CEO tem um novo melhor amigo",
                    f"{new['pet']} chegou à cobertura e, segundo fontes, já manda em tudo."))
    # acontecimentos do dia
    launches = [e["item"] for e in g.noticias["events"] if e["kind"] == "launch" and e.get("item") in ITEMS]
    if len(launches) == 1:
        t, x = random.choice(LAUNCH)
        it = ITEMS[launches[0]]["name"]
        out.append((60, "lancamento", t.format(item=it), x.format(item=it)))
    elif launches:
        out.append((62, "lancamento", f"Luthor Corp lança {len(launches)} produtos num dia só",
                    "O laboratório não para: " + ", ".join(ITEMS[i]["name"] for i in launches[:3]) + "."))
    for e in g.noticias["events"]:
        if e["kind"] == "sommelier":
            out.append((65, "sommelier", "CEO tem paladar de sommelier",
                        "Na sede do Gruppo Ricci, Letícia Luthor acertou os três vinhos da degustação. Vittoria Ricci: "
                        "\"Nem eu acerto todos.\""))
        elif e["kind"] == "pediatria":
            out.append((55, "pediatria", "Visita surpresa na pediatria",
                        "A CEO passou a tarde na brinquedoteca do Conti Moretti. As crianças pedem bis. As médicas "
                        "também."))
        elif e["kind"] in EXTRA_EVENTS:
            prio, title, text = EXTRA_EVENTS[e["kind"]]
            out.append((prio, e["kind"], title, text))
    return out


def night(g, notes):
    """Escreve as manchetes do dia que começa. Chamado no fim de `Game.process_night`."""
    st = g.noticias
    new = snapshot(g)
    old = st.get("snap") or {}
    if not old:                                       # jogo novo ou save antigo: só guarda a foto
        st["snap"] = new
        st["events"] = []
        return
    items = sorted(_diff(g, old, new), key=lambda t: -t[0])[:3]
    day = g.abs_day()
    for pr, kind, title, text in items:
        st["feed"].append(dict(day=day, prio=pr, kind=kind, title=title, text=text))
        st["total"] = st.get("total", 0) + 1
    st["feed"] = st["feed"][-FEED_MAX:]
    st["snap"] = new
    st["events"] = []
    if items:
        notes.append((f"Na capa da CatCo hoje: \"{items[0][2]}\"", C_LILAC))


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def fresh(g, kind=None):
    """Manchetes de hoje (as de ontem também valem para a banca)."""
    day = g.abs_day()
    out = [n for n in g.noticias["feed"] if n["day"] >= day - 1 and (kind is None or n["kind"] == kind)]
    return sorted(out, key=lambda n: (-n["day"], -n["prio"]))


def headline(g):
    f = fresh(g)
    return f[0] if f else None


def kiosk(g):
    """Banca de jornais."""
    n = headline(g)
    if not n:
        g.say("Banca de jornal. Manchete da CatCo: " + random.choice(NEWS))
        return
    lines = [f"Manchete da CatCo: \"{n['title']}\"", n["text"]]
    more = [x for x in fresh(g) if x is not n][:2]
    if more:
        lines.append("Também nesta edição: " + " · ".join(x["title"] for x in more) + ".")
    g.push(ui.Dialog("Banca de jornal", lines))


def tv_line(g):
    n = headline(g)
    if n:
        return f"Destaque do dia: {_dot(n['title'])} {n['text']}"
    return random.choice(NEWS)


def email_line(g):
    n = headline(g)
    return f"{_dot(n['title'])} {n['text']}" if n else random.choice(NEWS)


def _dot(t):
    """Título com ponto final (sem duplicar "!" ou "?")."""
    return t if t[-1:] in ".!?" else t + "."


def archive_pick(g):
    """Uma manchete antiga sobre a Letícia (para o arquivo da CatCo)."""
    feed = g.noticias["feed"]
    return random.choice(feed) if feed else None


# falas que comentam a capa do dia (cada uma é dita uma vez, como as outras falas reativas)
dialogue.REACTIVE.extend([
    ("nia", lambda g: bool(fresh(g)), "Viu a capa de hoje? Eu disse que ia ser você. Eu sonhei. Com o título e tudo."),
    ("rafa", lambda g: bool(fresh(g)), "Todo mundo aqui no café está lendo sobre você hoje. Quer o jornal junto com o "
                                       "cappuccino?"),                      # Harry (chave interna rafa)
    ("barry", lambda g: bool(fresh(g, "lenda")), "A foto do seu peixe lendário é a minha melhor capa do ano. Obrigado "
                                                 "por não soltar a vara."),
    ("barry", lambda g: bool(fresh(g, "fundacao")), "Fotografei a obra nova da Fundação de manhã cedo. A luz estava "
                                                    "perfeita. A cidade também."),
    ("lucy", lambda g: bool(fresh(g, "lancamento")), "Eu escrevi a matéria do lançamento. Tentei ser imparcial. Tentei."),
    ("lucy", lambda g: bool(fresh(g, "entrevista")), "Assisti à sua entrevista na CatCo TV. Você responde melhor na "
                                                     "câmera do que para mim. Anotado."),
    ("sam", lambda g: bool(fresh(g, "alta")), "Viu a manchete? \"LCORP dispara\". Vou emoldurar. Do lado do extrato."),
    ("vittoria", lambda g: bool(fresh(g, "sommelier")), "Você saiu no jornal por causa dos meus vinhos. Agora todo "
                                                        "mundo quer a degustação. Obrigada. Eu acho."),
    ("izzie", lambda g: bool(fresh(g, "pediatria")), "As crianças recortaram a matéria da CatCo e colaram na parede da "
                                                     "brinquedoteca. Do lado dos desenhos de você."),
])

"""Primeira coleção da Celeste Waite, com investimento da Letícia (depois do desfile no píer).

- Depois da cena celeste_8 (flag `celeste_desfile`), a conversa com a Celeste ganha "Investir na coleção ($2500)".
- Três noites depois a coleção é lançada: manchete na CatCo, 4 looks novos na La Boutique (aba Roupas) e
  royalties de $150 por semana para a Luthor Corp (flag `colecao_celeste`).
"""
from . import ui, audio, boutique, closet, noticias, dialogue
from .data import FLAG_LABELS
from .config import C_PINK, C_GOLD, C_GREEN, C_LILAC

PRICE = 2500
DAYS = 3
ROYALTY = 150
FLAG = "colecao_celeste"

LOOKS = {
    "lyon_vinho": ("Vestido Lyon", 520, dict(outfit="dress", cloth=(124, 28, 54), accent=(232, 210, 120)),
                   "Vinho como o cabelo da Celeste, cinto dourado. A peça que abre a coleção."),
    "trench_lilas": ("Trench lilás", 700, dict(outfit="trench", cloth=(176, 150, 214), accent=(64, 40, 92)),
                     "O sobretudo da coleção, em lilás Luthor. Para garoar com elegância."),
    "riviera": ("Conjunto Riviera", 580, dict(outfit="skirt_suit", cloth=(32, 46, 88), accent=(246, 242, 232),
                                               pants=(32, 46, 88)),
                "Azul-marinho com botões claros. Inspirado nas férias da Celeste no sul da França."),
    "seda_rose": ("Blusa de seda rosé", 340, dict(outfit="blouse", cloth=(240, 214, 222), accent=(150, 90, 220),
                                                    pants=(46, 38, 58)),
                  "Seda leve, calça escura. A peça \"para o dia inteiro\" da coleção."),
}
closet.LOOKS.update(LOOKS)
closet.ORDER[:] = list(closet.LOOKS)
closet.GENERIC.update({
    "lyon_vinho": ["É da coleção da Celeste! Ficou perfeito em você.", "Vinho com dourado. Elegância pura."],
    "trench_lilas": ["Trench lilás? Isso é muito Luthor.", "Esse casaco tem cara de capa de revista."],
    "riviera": ["Parece que você acabou de descer de um iate na Riviera.", "Azul-marinho combina com você."],
    "seda_rose": ["Que blusa linda. É seda?", "Rosé fica ótimo em você."],
})
closet.SPECIAL.setdefault("celeste", {}).update({
    "lyon_vinho": "Minha primeira peça na vitrine, e na mulher que acreditou nela. Eu vou chorar de novo.",
    "trench_lilas": "O trench! Ele foi desenhado num guardanapo do Grão Nobre. Olha onde ele chegou.",
})
FLAG_LABELS[FLAG] = "Coleção Celeste Waite lançada! Looks novos na La Boutique e royalties toda semana."

STATE = {"launched": False}       # a loja consulta isto (não recebe o Game)
_orig_for_sale = boutique.looks_for_sale


def _for_sale():
    """Os looks da coleção só aparecem na loja depois do lançamento."""
    keys = _orig_for_sale()
    if not STATE["launched"]:
        keys = [k for k in keys if k not in LOOKS]
    return keys


boutique.looks_for_sale = _for_sale

noticias.EXTRA_EVENTS["colecao"] = (72, "Celeste Waite lança a primeira coleção",
                                    "A estilista de Lyon apresentou a coleção feita com investimento da Luthor Corp. "
                                    "As peças esgotaram em uma tarde. A CEO já foi vista com o vestido vinho.")
dialogue.REACTIVE.extend([
    ("celeste", lambda g: bool(noticias.fresh(g, "colecao")),
     "Saí na CatCo! Minha mãe ligou de Lyon chorando. Depois ligou de novo só para chorar mais um pouco."),
    ("lucy", lambda g: bool(noticias.fresh(g, "colecao")),
     "A coleção da Celeste esgotou numa tarde. Eu escrevi a matéria. E comprei a blusa rosé. Sem comentários."),
    ("vittoria", lambda g: bool(noticias.fresh(g, "colecao")),
     "Vi a coleção da Celeste. O vestido vinho é um escândalo. Elegante, mas um escândalo."),
])


# --- estado -----------------------------------------------------------------
def init_state(g):
    g.colecao = dict(invested=None, launched=None, said=False, paid=0)
    _sync(g)


def save_state(g):
    return {"colecao": g.colecao}


def load_state(g, d):
    init_state(g)
    c = d.get("colecao") or {}
    for k in ("invested", "launched"):
        g.colecao[k] = c.get(k)
    g.colecao["said"] = bool(c.get("said", False))
    g.colecao["paid"] = int(c.get("paid", 0))
    _sync(g)


def _sync(g):
    STATE["launched"] = bool(g.colecao.get("launched"))


# --- conversa ------------------------------------------------------------------
def talk_options(g, npc, opts, acts):
    if npc.key != "celeste" or "celeste_desfile" not in g.flags or g.colecao["invested"] is not None:
        return
    opts.append(f"Investir na coleção (${PRICE})")
    acts.append(lambda: _offer(g, npc))


def _offer(g, npc):
    def pick(i):
        if i != 0:
            g.push(ui.Dialog(npc.name, ["Sem pressa! O caderno espera. Eu espero. A minha mãe é que não espera muito."],
                             g.portrait_for(npc, "smile"), subtitle=npc.data["role"]))
            return
        if g.money < PRICE:
            g.push(ui.Dialog(npc.name, [f"Faltam ${PRICE - g.money}. Mas olha, eu já fico feliz só de você ter "
                                        "pensado nisso."], g.portrait_for(npc, "smile"), subtitle=npc.data["role"]))
            return
        g.money -= PRICE
        g.colecao["invested"] = g.abs_day()
        g.add_friendship("celeste", 150)
        audio.sfx("reward")
        g.toasts.push(f"Investimento na coleção da Celeste: lançamento em {DAYS} dias.", C_GOLD)
        g.push(ui.Dialog(npc.name, [
            "Você... está falando sério? Uma coleção inteira? Com o meu nome na etiqueta?",
            "Eu vou precisar sentar. Não, eu vou precisar desenhar. Tenho dez anos de caderno esperando por isso.",
            f"Em {DAYS} dias a coleção sai. E a primeira peça vai ter um bordado pequenininho: \"L.L.\". Merci, Letícia."],
            g.portrait_for(npc, "love"), subtitle=npc.data["role"]))
    g.push(ui.Choice(f"Investir ${PRICE} na primeira coleção da Celeste?",
                     [f"Sim, vamos lançar a coleção (${PRICE})", "Ainda não"], pick))


def chat_line(g, npc):
    if npc.key != "celeste" or not g.colecao["launched"] or g.colecao["said"]:
        return None
    g.colecao["said"] = True
    return ("A coleção está na vitrine! Separei os quatro looks na aba de roupas. E toda semana mando a sua parte "
            "dos royalties. Investidora, sócia e musa: você acumula cargos.")


# --- noite -------------------------------------------------------------------
def night(g, notes):
    c = g.colecao
    day = g.abs_day()
    if c["invested"] is not None and not c["launched"] and day - c["invested"] >= DAYS:
        c["launched"] = day
        g.flags.add(FLAG)
        _sync(g)
        noticias.event(g, "colecao")
        notes.append(("Lançamento da coleção Celeste Waite! Quatro looks novos na La Boutique e royalties de "
                      f"${ROYALTY} por semana.", C_PINK))
        return
    if c["launched"] and day > c["launched"] and (day - c["launched"]) % 7 == 0:
        g.money += ROYALTY
        c["paid"] += ROYALTY
        notes.append((f"Royalties da coleção da Celeste: +${ROYALTY}.", C_GOLD))


def hud_lines(g):
    c = g.colecao
    if c["invested"] is not None and not c["launched"]:
        left = DAYS - (g.abs_day() - c["invested"])
        return [(f"Coleção da Celeste: lançamento em {max(1, left)} dia(s)", C_LILAC)]
    return []

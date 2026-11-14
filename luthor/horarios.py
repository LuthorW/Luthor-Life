"""Horário de funcionamento dos prédios da cidade (como as lojas do Stardew).

Fora do horário a porta fica trancada. Quem comanda o lugar libera a entrada a qualquer hora quando a Letícia
tem corações suficientes com essa pessoa: 2 nas lojas, cafés e restaurantes, 4 nos escritórios (CatCo e Gruppo
Ricci). A Luthor Corp (sede e Marina), o hospital e as casas não fecham (a portaria do Bayside tem horário próprio,
em world.BAYSIDE_HOURS).

Cena, encontro ou visita marcada ali naquele horário também abre a porta: a pessoa está te esperando.
"""
from . import audio
from .characters import NPCS
from .config import C_LILAC

# lugar -> (abre, fecha, quem comanda, corações para entrar fora do horário). 26h = até o fim do dia (2h).
OPEN_HOURS = {
    "cafe": (6 * 60, 22 * 60, ("rafa",), 2),
    "market": (7 * 60, 20 * 60, ("bea",), 2),
    "books": (8 * 60, 21 * 60, ("theo",), 2),
    "boutique": (9 * 60, 19 * 60, ("celeste",), 2),
    "trattoria": (9 * 60, 23 * 60, ("graca", "vittoria"), 2),
    "bar": (16 * 60, 26 * 60, ("marco",), 2),
    "cinema": (12 * 60, 26 * 60, (), 0),
    "catco": (8 * 60, 20 * 60, ("lucy", "nia", "barry"), 4),
    "ricci": (9 * 60, 19 * 60, ("vittoria",), 4),
}

# ganchos extras: fn(g, lugar) -> True quando algo marcado ali deve abrir a porta
INVITES = []


def fmt(m):
    m %= 24 * 60
    return f"{m // 60}h{m % 60:02d}" if m % 60 else f"{m // 60}h"


def hours_text(place):
    a, b, _, _ = OPEN_HOURS[place]
    return f"das {fmt(a)} às {fmt(b)}"


def _names(keys):
    names = [NPCS[k]["short"] for k in keys]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " ou " + names[-1]


def unlock_text(place):
    """'Com 2 corações com Harry, ...' (vazio se ninguém libera)."""
    _, _, owners, h = OPEN_HOURS[place]
    if not owners:
        return ""
    return f"Com {h} corações com {_names(owners)}, você pode entrar a qualquer hora."


def is_open(place, minutes):
    if place not in OPEN_HOURS:
        return True
    a, b, _, _ = OPEN_HOURS[place]
    return a <= minutes < b


def friend_key(g, place):
    """Quem comanda o lugar e já deixa a Letícia entrar fora do horário (ou None)."""
    _, _, owners, h = OPEN_HOURS[place]
    for k in owners:
        if k in g.friendship and (g.hearts(k) >= h or g.dating == k or g.partner == k):
            return k
    return None


def invited(g, place):
    """Tem cena, encontro ou visita marcada neste lugar agora?"""
    t = g.minutes
    from .cutscenes import SCENES
    for _k, _h, ev in g.pending_scene_events():
        sc = ev.get("scene")
        if sc and sc in SCENES and g.SCENE_TRIGGER_MAP.get(SCENES[sc]["map"], SCENES[sc]["map"]) == place:
            _, a, b = g.scene_place(sc)
            if a <= t <= b:
                return True
    if g.proposal and not g.dating:
        sc = f"{g.proposal}_pedido"
        if sc in SCENES and SCENES[sc]["map"] == place:
            _, a, b = g.scene_place(sc)
            if a <= t <= b:
                return True
    if g.date and not g.date.get("done") and g.date.get("map") == place:
        return True
    from . import andrea, casal
    v = andrea.active(g)
    if v and v[1] == place:
        return True
    if g.dating and casal.anniversary_today(g) and casal.dinner_place(g, g.dating)[0] == place \
            and 18 * 60 <= t < 23 * 60:
        return True
    return any(fn(g, place) for fn in INVITES)


def can_enter(g, place):
    """Chamado quando a Letícia pisa na porta de um prédio, na cidade. Fechado = mensagem e volta um passo."""
    if place not in OPEN_HOURS or is_open(place, g.minutes):
        return True
    if invited(g, place):
        return True
    k = friend_key(g, place)
    if k:
        g.toasts.push(f"Fora do horário: {NPCS[k]['short']} deixou a porta aberta para você.", C_LILAC)
        return True
    audio.sfx("cancel")
    label = g.world[place].label
    extra = unlock_text(place)
    g.say(f"Fechado agora. {label} funciona {hours_text(place)}." + (f" {extra}" if extra else ""))
    return False

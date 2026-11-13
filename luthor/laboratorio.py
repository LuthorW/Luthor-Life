"""Melhorias do laboratório da sede: equipamentos comprados no painel ao lado do Terminal P&D (11,2).

  centrifuga       Centrífuga de alta rotação  $1800  projetos 1 dia mais rápidos (soma com o Brainy; mínimo 1)
  impressora       Impressora 3D industrial    $2400  produtos do laboratório valem 10% a mais
  estufa           Câmara de crescimento       $1500  libera o Projeto Gaia (biotecnologia)
  supercomputador  Supercomputador Prometeu     $4000  libera o Projeto Prometeu (o produto mais caro)
Cada equipamento comprado aparece encostado na parede do laboratório. Estado em `g.lab["owned"]`.
"""
import pygame

from . import art, world, ui, audio, lighting
from .art import new, R, P, shade
from .data import PROJECTS, ITEMS, PRODUCT_NAMES, FLAG_LABELS
from .config import C_GOLD, C_GREEN, C_LILAC, C_MUTED, C_TEXT

PANEL = (11, 2)
UPGRADES = [
    dict(key="centrifuga", name="Centrífuga de alta rotação", price=1800, obj="centrifuga", pos=(13, 2),
         desc="Projetos ficam prontos 1 dia mais cedo (mínimo 1 dia)."),
    dict(key="impressora", name="Impressora 3D industrial", price=2400, obj="impressora3d", pos=(17, 2),
         desc="Produtos do laboratório valem 10% a mais."),
    dict(key="estufa", name="Câmara de crescimento", price=1500, obj="estufa_lab", pos=(15, 2),
         desc="Libera o Projeto Gaia no Terminal P&D."),
    dict(key="supercomputador", name="Supercomputador Prometeu", price=4000, obj="supercomputador", pos=(20, 2),
         desc="Libera o Projeto Prometeu no Terminal P&D."),
]
BY_KEY = {u["key"]: u for u in UPGRADES}

NEW_PROJECTS = {
    "gaia": dict(name="Projeto Gaia", product="Semente Gaia", days=6, cost=140, value=340, color=(110, 210, 120),
                 icon="dna", flag="lab_estufa", desc="Semente que cresce em qualquer solo. A horta do terraço aprova."),
    "prometeu": dict(name="Projeto Prometeu", product="Núcleo Prometeu", days=10, cost=300, value=820,
                     color=(255, 150, 70), icon="orb", flag="lab_super",
                     desc="Processador que aprende sozinho. O Brainy chama de \"filho\"."),
}
for _k, _p in NEW_PROJECTS.items():
    PROJECTS[_k] = dict(name=_p["name"], days=_p["days"], cost=_p["cost"], value=_p["value"], quarters=[1, 2, 3, 4],
                        color=_p["color"], icon=_p["icon"], locked_flag=_p["flag"])
    PRODUCT_NAMES[_k] = _p["product"]
    ITEMS["prop_" + _k] = dict(name="Proposta: " + _p["name"], kind="proposal", project=_k, price=_p["cost"],
                               icon="folder", color=_p["color"],
                               desc=f"Inicia o {_p['name']} numa bancada. Pronto em {_p['days']} dias de trabalho.")
    ITEMS[_k] = dict(name=_p["product"], kind="product", value=_p["value"], icon=_p["icon"], color=_p["color"],
                     desc=f"{_p['desc']} Vale ${_p['value']} na Mesa de Contratos.")
FLAG_LABELS["lab_estufa"] = "Câmara de crescimento instalada: Projeto Gaia liberado no Terminal P&D."
FLAG_LABELS["lab_super"] = "Supercomputador Prometeu ligado: Projeto Prometeu liberado no Terminal P&D."
FLAGS = {"estufa": "lab_estufa", "supercomputador": "lab_super"}


# --- arte ---------------------------------------------------------------------
STEEL, STEEL_D = (150, 156, 172), (92, 96, 112)
PURPLE, GLOW = (120, 40, 190), (200, 150, 255)


def _painel():
    s = new(16, 28)
    R(s, (44, 40, 58), 2, 4, 12, 22)
    R(s, (60, 56, 78), 2, 4, 12, 2)
    R(s, (24, 22, 34), 4, 7, 8, 7)
    R(s, PURPLE, 5, 8, 6, 5)
    for i, c in enumerate(((120, 230, 140), GLOW, (240, 200, 90))):
        R(s, c, 5 + i * 2, 16, 1, 1)
    R(s, GLOW, 5, 9, 4, 1); R(s, GLOW, 5, 11, 3, 1)
    R(s, (80, 76, 96), 4, 19, 8, 2)
    R(s, (34, 30, 44), 3, 24, 10, 2)
    return s


def _centrifuga():
    s = new(16, 24)
    R(s, STEEL_D, 1, 10, 14, 14)
    R(s, STEEL, 1, 10, 14, 2)
    pygame.draw.ellipse(s, (220, 224, 234), (2, 5, 12, 7))
    pygame.draw.ellipse(s, STEEL_D, (4, 6, 8, 5), 1)
    P(s, PURPLE, 8, 8)
    R(s, (40, 40, 52), 4, 15, 8, 4)
    R(s, (120, 230, 140), 5, 16, 2, 1); R(s, GLOW, 8, 17, 3, 1)
    R(s, (60, 60, 72), 2, 22, 12, 2)
    return s


def _estufa():
    s = new(16, 28)
    R(s, STEEL_D, 1, 4, 14, 24)
    R(s, (170, 220, 200), 2, 6, 12, 14)
    R(s, (200, 240, 220), 2, 6, 3, 14)
    for x, h in ((4, 6), (8, 9), (11, 5)):
        R(s, (70, 150, 70), x, 19 - h, 1, h)
        R(s, (110, 200, 100), x - 1, 19 - h, 3, 2)
    R(s, (240, 120, 200), 3, 5, 10, 1)                 # luz de crescimento
    R(s, (60, 60, 72), 1, 21, 14, 7)
    R(s, (120, 230, 140), 3, 23, 3, 1)
    return s


def _impressora():
    s = new(32, 26)
    R(s, (52, 50, 64), 1, 4, 30, 22)
    R(s, (72, 70, 88), 1, 4, 30, 2)
    R(s, (190, 220, 240), 4, 7, 24, 11)                 # porta de vidro
    R(s, (220, 240, 250), 4, 7, 4, 11)
    R(s, STEEL, 6, 9, 20, 1)                            # trilho
    R(s, PURPLE, 14, 9, 4, 2)                           # cabeça de impressão
    R(s, (240, 200, 90), 13, 14, 6, 4)                  # peça sendo impressa
    R(s, (34, 30, 44), 2, 20, 28, 4)
    R(s, (120, 230, 140), 4, 21, 2, 1); R(s, GLOW, 7, 21, 6, 1)
    return s


def _supercomputador():
    s = new(32, 32)
    for x in (1, 17):
        R(s, (30, 28, 40), x, 4, 14, 28)
        R(s, (48, 44, 62), x, 4, 14, 2)
        for y in range(8, 28, 3):
            R(s, (20, 18, 28), x + 2, y, 10, 2)
            P(s, (120, 230, 140) if (x + y) % 2 else GLOW, x + 3, y)
            P(s, (240, 200, 90), x + 10, y + 1)
    R(s, PURPLE, 15, 10, 2, 16)                          # cabos
    return s


art.OBJECT_BUILDERS.update({"painel_lab": _painel, "centrifuga": _centrifuga, "estufa_lab": _estufa,
                            "impressora3d": _impressora, "supercomputador": _supercomputador})
world.OBJECT_DEFS.update({"painel_lab": (1, 1, True, "obj"), "centrifuga": (1, 1, True, "obj"),
                          "estufa_lab": (1, 1, True, "obj"), "impressora3d": (2, 1, True, "obj"),
                          "supercomputador": (2, 1, True, "obj")})
lighting.EMITTERS.update({"painel_lab": ((150, 90, 230), 1.4), "supercomputador": ((110, 200, 150), 2.0),
                          "estufa_lab": ((220, 110, 200), 1.4)})


# --- estado e objetos no mapa ---------------------------------------------------------
def init_state(g):
    g.lab = dict(owned=[])
    apply(g)


def save_state(g):
    return {"lab": g.lab}


def load_state(g, d):
    g.lab = dict(owned=[k for k in (d.get("lab") or {}).get("owned", []) if k in BY_KEY])
    for k in g.lab["owned"]:
        if k in FLAGS:
            g.flags.add(FLAGS[k])
    apply(g)


def _recompute(m, tiles):
    for (x, y) in tiles:
        if m.in_bounds(x, y):
            solid = m.tiles[y][x] in world.SOLID_TILES or m.building_at(x, y) is not None
            if not solid:
                solid = any(o.solid and o.x <= x < o.x + o.w and o.y <= y < o.y + o.h for o in m.objects)
            m.solid[y][x] = solid


def _tiles(kind, x, y):
    w, h = world.OBJECT_DEFS[kind][:2]
    return [(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)]


def apply(g):
    """Painel sempre; cada equipamento só se foi comprado."""
    m = getattr(g, "world", {}).get("hq") if hasattr(g, "world") else None
    if m is None:
        return
    want = {("painel_lab",) + PANEL}
    for k in getattr(g, "lab", {}).get("owned", []):
        if k in FLAGS and hasattr(g, "flags"):
            g.flags.add(FLAGS[k])
        u = BY_KEY[k]
        want.add((u["obj"],) + u["pos"])
    have = {(o.kind, o.x, o.y): o for o in m.objects if isinstance(o.data, tuple) and o.data[0] == "lab"}
    touched = []
    for key, o in have.items():
        if key not in want:
            m.objects.remove(o)
            touched += _tiles(*key)
    for key in want - set(have):
        m.add(key[0], key[1], key[2], data=("lab", key[0]))
        touched += _tiles(*key)
    if touched:
        _recompute(m, touched)


# --- efeitos nos números do jogo ---------------------------------------------------------
def days_off(g):
    return 1 if "centrifuga" in g.lab["owned"] else 0


def sell_mult(g, item):
    if "impressora" in g.lab["owned"] and ITEMS.get(item, {}).get("kind") == "product":
        return 1.10
    return 1.0


# --- painel -------------------------------------------------------------------------------
def object_label(g, o):
    if o.kind == "painel_lab":
        return "Melhorias do laboratório"
    if isinstance(o.data, tuple) and o.data[0] == "lab":
        return next((u["name"] for u in UPGRADES if u["obj"] == o.kind), None)
    return None


def use_object(g, o):
    if o.kind == "painel_lab":
        open_panel(g)
        return True
    u = next((u for u in UPGRADES if u["obj"] == o.kind), None)
    if u:
        g.say(f"{u['name']}: {u['desc']}")
        return True
    return False


def open_panel(g):
    left = [u for u in UPGRADES if u["key"] not in g.lab["owned"]]
    if not left:
        g.say("O laboratório está completo. O Brainy diz que é o mais bonito da costa oeste.")
        return
    opts = [f"{u['name']} (${u['price']}): {u['desc']}" for u in left] + ["Fechar"]

    def pick(i):
        if i >= len(left):
            return
        u = left[i]
        if g.money < u["price"]:
            audio.sfx("blip")
            g.say(f"Faltam ${u['price'] - g.money} para a {u['name']}.")
            return
        g.money -= u["price"]
        g.lab["owned"].append(u["key"])
        if u["key"] in FLAGS:
            g.flags.add(FLAGS[u["key"]])
            g.toasts.push(FLAG_LABELS[FLAGS[u["key"]]], C_GOLD)
        apply(g)
        audio.sfx("reward")
        g.toasts.push(f"Instalado: {u['name']}!", C_GREEN)
        g.say(f"A equipe instala a {u['name']} encostada na parede do laboratório. {u['desc']}")
    g.push(ui.Choice("Melhorias do laboratório", opts, pick))

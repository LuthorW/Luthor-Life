"""Gera a wiki do Luthor Life (docs/wiki/) direto dos dados do jogo.

Rodar:  py gerar_wiki.py
- Não mexe no save: abre o jogo sem janela só para ler os dados e desenhar os ícones.
- Escreve as páginas .html, a busca (busca.js) e as imagens em docs/wiki/img/.
- wiki.css e wiki.js são escritos à mão e ficam como estão.
- Os retratos da wiki são cópias menores em WebP (docs/wiki/img/retratos); os originais em
  assets/portraits continuam intactos.
Rode de novo sempre que mudar falas, presentes, itens, peixes, rotinas etc.
"""
import os
import sys
import json
import html
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "docs", "wiki")
IMG = os.path.join(OUT, "img")

# o jogo pode gravar as configurações ao abrir: guarda e devolve no fim
_BACKUP = {f: open(f, "rb").read() for f in ("saves/settings.json", "saves/save.json") if os.path.exists(f)}

import pygame  # noqa: E402
from luthor.game import Game  # noqa: E402
from luthor import (art, data, characters, festas, conquistas, hospital, habilidades, fundacao,  # noqa: E402
                    laboratorio, marina, activities, historia, citymap, seasons, config, world, boutique,
                    closet, andrea, clube, celular, horarios, degustacao, surpresa, encontros, pediatria, pedidos, casamento)

g = Game()
g.save = lambda *a, **k: None

NPCS = characters.NPCS
ORDER = list(characters.NPC_ORDER)
ITEMS = data.ITEMS
SEASON = {1: "Primavera", 2: "Verão", 3: "Outono", 4: "Inverno"}
SEASON_Q = {"spring": 1, "summer": 2, "autumn": 3, "winter": 4}
WD = config.WEEKDAYS
WD_FULL = config.WEEKDAYS_FULL
MALE = {"brainy", "rafa", "barry", "theo", "marco", "joca", "ian"}
HP = config.HEART_POINTS
GP = config.GIFT_POINTS
GROUPS = [
    ("Luthor Corp", ["sam", "brainy", "jess", "ian"]),
    ("CatCo", ["lucy", "nia", "barry"]),
    ("Moradores", ["vittoria", "rafa", "theo", "bea", "graca", "marco", "joca", "celeste"]),
    ("Conti Moretti", list(characters.DOCTOR_KEYS)),
    ("De fora da cidade", ["andrea"]),
]

esc = html.escape


def hm(m):
    m = int(m) % 1440
    return f"{m // 60}h{m % 60:02d}" if m % 60 else f"{m // 60}h"


def money(v):
    return "$" + f"{int(v):,}".replace(",", ".")


def cap(t):
    return t[:1].upper() + t[1:]


def day_name(q, d):
    return f"{d} de {SEASON[q]}"


def weekday(d):
    return WD_FULL[(d - 1) % 7]


def seasons_txt(qs):
    qs = sorted(set(int(q) for q in qs))
    return "Ano todo" if qs == [1, 2, 3, 4] else ", ".join(SEASON[q] for q in qs)


# --- links e imagens ----------------------------------------------------------
def ico(k, size=32, cls="ico"):
    return f'<img class="{cls}" src="img/itens/{k}.png" alt="" width="{size}" height="{size}" loading="lazy">'


def item(k, size=32):
    if k == "fish":
        return f'<a class="item" href="peixes.html">{ico("sardinha", size)}Qualquer peixe</a>'
    if k not in ITEMS:
        return esc(k)
    return f'<a class="item" href="item-{k}.html">{ico(k, size)}{esc(ITEMS[k]["name"])}</a>'


def head(k):
    return f'<img class="cab" src="img/cabecas/{k}.png" alt="" width="24" height="24" loading="lazy">'


def short(k):
    return NPCS[k]["short"] if k in NPCS else k


def npc(k, full=False):
    if k == "leticia":
        return f'<a class="npc" href="leticia.html">{head(k)}Letícia</a>'
    if k == "andrea":
        return f'<a class="npc" href="andrea.html">{head(k)}{"Andrea Rojas" if full else "Andrea"}</a>'
    nm = NPCS[k]["name"] if full else short(k)
    return f'<a class="npc" href="{k}.html">{head(k)}{esc(nm)}</a>'


def shot(name, alt, cap=None):
    """Captura do jogo que já existe no site (docs/img)."""
    if not os.path.exists(os.path.join(ROOT, "docs", "img", name + ".png")):
        return ""
    c = f"<figcaption>{cap}</figcaption>" if cap else ""
    return f'<figure class="foto"><img src="../img/{name}.png" alt="{esc(alt)}" loading="lazy">{c}</figure>'


def table(headers, rows, cls="wikitable", sortable=False):
    c = cls + (" ordenavel" if sortable else "")
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c_}</td>" for c_ in r) + "</tr>" for r in rows)
    return f'<div class="tabela"><table class="{c}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def box(kind, title, body):
    return f'<div class="aviso {kind}"><b>{title}</b> {body}</div>'


# --- quem mora/trabalha onde ------------------------------------------------------
def map_label(m):
    if m in g.world:
        return g.world[m].label
    return m


AREA_NAMES = {"park": "Parque Central", "woods": "Bosque Bayside", "garden": "Jardim do Mirante", "beach": "Praia"}


def place(m, x, y):
    if m is None:
        return "Fora do centro"
    if m == "city":
        for a, rects in world.CITY_AREAS.items():
            for (x0, y0, x1, y1) in rects:
                if x0 <= x <= x1 and y0 <= y <= y1:
                    return AREA_NAMES[a]
        if y >= 61:
            return "Píer"
        return "Ruas de National City"
    if m.startswith("apt_"):
        return "Em casa"
    return map_label(m)


def place_link(m):
    return f'<a href="lugares.html#{m}">{esc(map_label(m))}</a>'


def home_of(k):
    if k in world.APARTMENTS:
        m = world.APARTMENTS[k]
        predio = "Residencial Luthor" if k in ("sam", "ian", "milany") else "Apartamentos Bayside"
        return f"{esc(map_label(m))} ({predio})"
    return "Fora do centro (não dá para visitar)"


# --- gostos ------------------------------------------------------------------------
def tastes(k):
    gd = NPCS[k].get("gifts", {})
    out = {}
    for t in ("love", "like", "dislike"):
        for it in gd.get(t, []):
            out[it] = t
    return out


TASTE = {k: tastes(k) for k in ORDER}
TASTE_LABEL = {"love": "Ama", "like": "Gosta", "neutral": "Neutro", "dislike": "Não gosta"}


def taste_of(k, it):
    return TASTE[k].get(it, "neutral")


# --- de onde vem cada item --------------------------------------------------------
SOURCES = {k: [] for k in ITEMS}
USES = {k: [] for k in ITEMS}
SHOP_PLACE = {"cafe": ("cafe", "rafa"), "market": ("market", "bea"), "books": ("books", "theo"),
              "trattoria": ("trattoria", "graca"), "bar": ("bar", "marco"), "pharmacy": ("hospital", None),
              "bait": ("city", "joca")}
for sk, s in data.SHOPS.items():
    for it in s["stock"]:
        if it in SOURCES:
            p = ITEMS[it].get("price")
            SOURCES[it].append(f'Loja: <a href="lojas.html#{sk}">{esc(s["title"])}</a>' + (f" ({money(p)})" if p else ""))
for it, a in boutique.ACCESSORIES.items():
    if it in SOURCES:
        SOURCES[it].append(f'Loja: <a href="lojas.html#boutique">La Boutique</a> ({money(a["price"])})')
for fk, f in festas.FESTIVALS.items():
    for it in f.get("shop", []):
        if it in SOURCES:
            SOURCES[it].append(f'Barraca da <a href="festas.html#{fk}">{esc(f["name"])}</a>')
for ck, c in data.CROPS.items():
    if c["item"] in SOURCES:
        SOURCES[c["item"]].append(f'Colheita na <a href="horta.html">horta do terraço</a> ({c["days"]} dias)')
for fk, f in data.FORAGE.items():
    if fk in SOURCES:
        qs = seasons.FORAGE_SEASONS.get(fk)
        when = seasons_txt([SEASON_Q[s] for s in qs]) if qs else "Ano todo"
        SOURCES[fk].append(f'Coletável: {AREA_NAMES.get(f["where"], f["where"])} ({when})')
FISH_WHERE = {"sea": "Mar (píer e praia)", "pond": "Lago", "deep": "Alto-mar (barco da Marina)"}
ALL_FISH = dict(data.FISH)
for k, v in marina.DEEP_FISH.items():
    ALL_FISH.setdefault(k, v)
for k, f in ALL_FISH.items():
    if k in SOURCES:
        SOURCES[k].append(f'<a href="peixes.html">Pesca</a>: {FISH_WHERE.get(f["where"], f["where"])}')
for rk, r in data.RECIPES.items():
    if rk in SOURCES:
        SOURCES[rk].append('<a href="receitas.html">Cozinhar no fogão</a>')
    for need in r["needs"]:
        if need in USES:
            USES[need].append(f'Receita: {item(rk)}')
for pk, p in data.PROJECTS.items():
    if pk in SOURCES:
        SOURCES[pk].append(f'<a href="laboratorio.html">Laboratório</a> ({p["days"]} dias numa bancada)')
    if "prop_" + pk in SOURCES:
        SOURCES["prop_" + pk].append('<a href="laboratorio.html">Terminal P&amp;D</a> da sede')
for p in fundacao.PROJECTS:
    for it, n in p["items"]:
        if it in USES:
            USES[it].append(f'Fundação Luthor: <a href="fundacao.html#{p["key"]}">{esc(p["name"])}</a> (×{n})')
for k in ORDER:
    for h, e in NPCS[k].get("events", {}).items():
        it = e.get("gift")
        if it in SOURCES:
            SOURCES[it].append(f'Presente de {npc(k)} ({h} corações)')
for it in pediatria.GIFTS:
    if it in USES:
        USES[it].append('<a href="atividades.html#pediatria">Brinquedoteca</a> (doce ou pelúcia para as crianças)')


# --- página ------------------------------------------------------------------------
NAV = [
    ("Início", [("index.html", "Página principal"), ("guia.html", "Primeiros passos"),
                ("controles.html", "Controles")]),
    ("Gente", [("personagens.html", "Personagens"), ("leticia.html", "Letícia Luthor"),
               ("presentes.html", "Presentes"), ("romance.html", "Romance")]),
    ("National City", [("lugares.html", "Lugares"), ("calendario.html", "Calendário"), ("festas.html", "Festas"),
                       ("estacoes.html", "Estações e clima")]),
    ("Coisas", [("itens.html", "Itens"), ("peixes.html", "Peixes"), ("receitas.html", "Receitas"),
                ("horta.html", "Horta e coletáveis"), ("lojas.html", "Lojas")]),
    ("Luthor Corp", [("laboratorio.html", "Laboratório"), ("fundacao.html", "Fundação Luthor"),
                     ("historia.html", "História")]),
    ("Vida na cidade", [("atividades.html", "Atividades"), ("hospital.html", "Conti Moretti"),
                        ("habilidades.html", "Habilidades"), ("conquistas.html", "Conquistas")]),
]
ATUAL = ' class="atual"'
INDEX = []  # busca: título, url, categoria, ícone


def nav_html(cur):
    out = []
    for title, links in NAV:
        lis = "".join(f'<li><a href="{u}"{ATUAL if u == cur else ""}>{esc(t)}</a></li>' for u, t in links)
        out.append(f"<h3>{esc(title)}</h3><ul>{lis}</ul>")
    out.append('<h3>Ferramentas</h3><ul><li><a href="#" id="aleatoria">Página aleatória</a></li>'
               '<li><a href="../index.html">Site do jogo</a></li>'
               '<li><a href="https://github.com/LuthorW/Luthor-Life">Código no GitHub</a></li></ul>')
    return "".join(out)


def write(fname, title, body, crumbs=(), desc="", cat="Página", icon=None, index=True):
    trail = '<a href="index.html">Wiki</a>' + "".join(f' <span>›</span> <a href="{u}">{esc(t)}</a>' for u, t in crumbs)
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Wiki Luthor Life</title>
<meta name="description" content="{esc(desc or title)}">
<link rel="icon" href="../img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="wiki.css">
<script>try{{var t=localStorage.getItem("wiki-tema");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<header class="topo">
  <button class="menu" aria-label="Abrir o menu">☰</button>
  <a class="marca" href="index.html"><img src="img/cabecas/leticia.png" alt="" width="32" height="32"><span>Luthor Life</span><em>Wiki</em></a>
  <div class="busca">
    <input type="search" placeholder="Buscar na wiki..." aria-label="Buscar na wiki" autocomplete="off">
    <ul class="resultados" hidden></ul>
  </div>
  <button class="tema" aria-label="Trocar tema claro/escuro">◐</button>
</header>
<div class="corpo">
  <nav class="lateral">{nav_html(fname)}</nav>
  <main class="artigo">
    <nav class="trilha">{trail}</nav>
    <h1>{esc(title)}</h1>
{body}
  </main>
</div>
<footer class="rodape">Wiki feita a partir dos dados do jogo <b>Luthor Life</b> (gerar_wiki.py). Fã-jogo sem fins lucrativos.</footer>
<script src="busca.js"></script>
<script src="wiki.js"></script>
</body>
</html>
"""
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    if index:
        INDEX.append(dict(t=title, u=fname, c=cat, i=icon or ""))


# ============================ imagens ===============================================
def save_png(surf, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(surf, path)


def make_images():
    for k in ITEMS:
        save_png(art.item_icon(k, 4), os.path.join(IMG, "itens", k + ".png"))
    # cabeças a partir dos bonequinhos do site (16x34 em escala 6: corta a cabeça e reduz para 3x)
    for f in os.listdir(os.path.join(ROOT, "docs", "img", "chars")):
        s = pygame.image.load(os.path.join(ROOT, "docs", "img", "chars", f))
        top = 0
        w, h = s.get_size()
        for y in range(h):                     # primeira linha com pixel visível
            if any(s.get_at((x, y)).a > 0 for x in range(0, w, 3)):
                top = y
                break
        side = min(w, h - top, 96)
        cut = s.subsurface(pygame.Rect((w - side) // 2, top, side, side)).copy()
        save_png(pygame.transform.scale(cut, (48, 48)), os.path.join(IMG, "cabecas", f))
    # medalhas
    for a in conquistas.ACHIEVEMENTS:
        s = pygame.Surface((64, 68), pygame.SRCALPHA)
        conquistas.badge(s, pygame.Rect(2, 0, 60, 60), a[0], True)
        save_png(s, os.path.join(IMG, "medalhas", a[0] + ".png"))
    # mapa da cidade
    try:
        save_png(citymap._base(g), os.path.join(IMG, "mapa.png"))
    except Exception as e:  # o mapa é só enfeite
        print("mapa:", e)
    # Andrea Rojas: não é NPC da cidade, o bonequinho sai do look dela (historia.EXTRAS)
    f0 = art.character_frames(historia.EXTRAS[andrea.KEY]["look"])[("down", 0)]
    c = pygame.Surface((16, 34), pygame.SRCALPHA)
    c.blit(pygame.transform.scale(f0, (16, 32)), (0, 2))
    big = pygame.transform.scale(c, (96, 204))
    save_png(big, os.path.join(IMG, "andrea.png"))
    save_png(pygame.transform.scale(big.subsurface(pygame.Rect(0, 0, 96, 96)).copy(), (48, 48)),
             os.path.join(IMG, "cabecas", "andrea.png"))
    make_portraits()


PORTRAITS = {}   # chave -> [(arquivo webp, humor)]
MOODS = [(None, "Normal"), ("happy", "Feliz"), ("bad", "Mau humor"), ("shy", "Timidez")]


def make_portraits():
    from PIL import Image
    src_dir = os.path.join(ROOT, "assets", "portraits")
    out_dir = os.path.join(IMG, "retratos")
    os.makedirs(out_dir, exist_ok=True)
    for k in ORDER + ["leticia", "andrea"]:
        base = os.path.splitext(NPCS[k]["portrait"])[0] if k in NPCS else k
        got = []
        seen = set()
        for mood, label in MOODS:
            fn = art.portrait_file(base, mood)
            src = os.path.join(src_dir, fn) if fn else None
            if not src or not os.path.exists(src) or fn in seen:
                continue
            seen.add(fn)
            dst = os.path.join(out_dir, os.path.splitext(fn)[0] + ".webp")
            if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
                im = Image.open(src).convert("RGBA")
                im.thumbnail((520, 520), Image.LANCZOS)
                im.save(dst, "WEBP", quality=90, method=6)
            got.append((os.path.basename(dst), label))
        PORTRAITS[k] = got


# ============================ personagens ===========================================
BIO = {
    "sam": "Samantha Arias é a CFO da Luthor Corp: cuida dos números, dos contratos e da paciência do conselho. "
           "Trabalha na salinha de vidro da sede, mora no Residencial Luthor e corre na orla de manhã cedo.",
    "brainy": "Querl Dox, o Brainy, é o CTO da Luthor Corp. Calcula a probabilidade de tudo, mora nos Apartamentos "
              "Bayside e joga xadrez a sério (e joga melhor cada vez que perde).",
    "jess": "Jess é a assistente executiva da Letícia e cuida da recepção da sede. Sabe a agenda de todo mundo, "
            "organiza a Noite das Luzes e nunca esquece um aniversário.",
    "rafa": "Harry é o barista do Café Grão Nobre. Sabe o pedido de meia cidade de cor e está sempre "
            "atrás do balcão, de manhã até a noite.",
    "lucy": "Lucy Williams é repórter investigativa da CatCo. Ela e a Letícia tiveram algo no passado, em Gotham, "
            "que terminou sem explicação. É um dos dois romances do jogo.",
    "vittoria": "Vittoria Ricci é a dona do Gruppo Ricci, rede de restaurantes de National City. Trabalhou anos na "
                "cozinha dos outros, abriu a própria Trattoria e agora inaugura a sede. Não é chef: quem cozinha "
                "é a Dona Graça. É um dos dois romances do jogo.",
    "nia": "Nia Nal é repórter da CatCo e colega da Lucy. Escreve sobre a cidade, anota sonhos num caderno e é a "
           "anfitriã da Festa das Flores.",
    "barry": "Barry Allen é o fotógrafo da CatCo, amigo da Nia e da Lucy. Está sempre atrasado e sempre com a "
             "câmera: é ele quem monta o álbum de fotos da Letícia.",
    "theo": "Theo é o livreiro da Bayside Books. Vende livros que dão bônus permanentes e organiza o clube do livro "
            "às quintas.",
    "bea": "Bea é a dona do Mercado Central: verduras, sementes, flores e ingredientes fresquinhos.",
    "graca": "Dona Graça é a chef brasileira da Ricci Trattoria: trinta anos de fogão, dez deles na Itália. "
             "É a anfitriã do Luau de Verão.",
    "marco": "Marco é o barman do Noonan's, o pub com fliperama, sinuca, dardos e karaokê.",
    "joca": "Seu Joca é o pescador do píer. Vende iscas na barraca e ensina a pescar a quem pedir.",
    "ian": "Ian é o diretor da Marina Luthor, a divisão náutica da Luthor Corp. Funcionário da Letícia e amigo de "
           "infância das férias no interior.",
    "celeste": "Celeste Waite é a estilista da La Boutique. Francesa de Lyon, estudou moda em Milão e tem o cabelo "
               "pintado cor de vinho.",
    "yang": "A Dra. Cristina Yang é da direção médica do Conti Moretti Hospitais. Direta, competitiva e "
            "cirurgiã de mão cheia.",
    "meredith": "A Dra. Meredith Grey é da direção médica do Conti Moretti Hospitais. Calma, observadora e sempre "
                "com cara de quem dormiu pouco.",
    "milany": "A Dra. Milany Moretti comanda o Centro Cardiovascular do Conti Moretti. Mora no Residencial Luthor.",
    "izzie": "A Dra. Izzie Stevens comanda o Centro de Oncologia do Conti Moretti e faz muffins para a ala inteira.",
    "addison": "A Dra. Addison Montgomery comanda o Centro Materno-Infantil do Conti Moretti. Salto alto e plantão "
               "de 24 horas.",
}
SCHED_LABEL = {"default": "Dias úteis", "weekend": "Fim de semana", "rain": "Dia de chuva"}


def sched_rows(rows):
    out = []
    last = None
    for r in rows:
        m, mp, x, y = r[0], r[1], r[2], r[3]
        lb = place(mp, x, y)
        if lb == last:
            continue
        last = lb
        if mp and mp != "city" and not mp.startswith("apt_") and mp in g.world:
            lb = place_link(mp)
        out.append((hm(m), lb))
    return out


def schedule_html(k):
    d = NPCS[k]
    if k in characters.DOCTOR_KEYS:
        parts = ['<p>As médicas não têm rotina fixa: o plantão no Conti Moretti alterna os postos sem repetir, '
                 'o almoço é cada dia num lugar e há 2 folgas por semana. Um exemplo de semana:</p><div class="rotinas">']
        for day in range(1, 4):
            try:
                rows = characters.doctor_schedule(k, day)
            except Exception:
                continue
            parts.append(f'<div>{table(["Hora", "Lugar"], sched_rows(rows))}<p class="legenda">{weekday(day).capitalize()}</p></div>')
        parts.append("</div>")
        return "".join(parts)
    sc = d["schedule"]
    parts = ['<div class="rotinas">']
    for kind in ("default", "weekend", "rain"):
        if kind in sc:
            lab = SCHED_LABEL[kind]
            if kind == "default" and "weekend" not in sc:
                lab = "Todos os dias"
            parts.append(f'<div><h4>{lab}</h4>{table(["Hora", "Lugar"], sched_rows(sc[kind]))}</div>')
    parts.append("</div>")
    note = ""
    if d.get("romance"):
        note = '<p class="nota">Com encontro marcado, a agenda das 19h às 22h é o encontro.</p>'
    return "".join(parts) + note


def events_html(k):
    ev = NPCS[k].get("events", {})
    if not ev:
        return "<p>Sem eventos de coração.</p>"
    rows = []
    for h in sorted(ev, key=int):
        e = ev[h]
        sc = e.get("scene")
        if sc:
            title = esc(g.scene_title(sc))
            try:
                where, a, b = g.scene_place(sc)
                when = f"{esc(where)}, das {hm(a)} às {hm(b)}"
            except Exception:
                when = "Na hora"
        else:
            title = "Conversa"
            when = "Na próxima conversa"
        if int(h) == 0:
            when += " <i>(surpresa: sem aviso)</i>"
        rew = []
        if e.get("gift") in ITEMS:
            rew.append("Presente: " + item(e["gift"]))
        lab = data.FLAG_LABELS.get(e.get("flag"))
        if lab:
            rew.append(esc(lab))
        rows.append([f'<span class="coracoes">♥</span> {h}', title, when,
                     "<br>".join(rew) or "—"])
    return table(["Corações", "Evento", "Onde e quando", "O que ganha"], rows)


def gifts_html(k, compact=False):
    ts = TASTE[k]
    groups = {"love": [], "like": [], "dislike": []}
    for it, t in ts.items():
        if it in ITEMS:
            groups[t].append(it)
    rows = []
    for t, pts in (("love", GP["love"]), ("like", GP["like"]), ("neutral", GP["neutral"]), ("dislike", GP["dislike"])):
        if t == "neutral":
            cell = "Todo o resto (coletáveis e itens comuns)"
        else:
            its = sorted(groups[t], key=lambda i: ITEMS[i]["name"])
            cell = '<div class="itens">' + "".join(item(i) for i in its) + "</div>" if its else "—"
        sign = "+" if pts > 0 else "−"
        rows.append([f'<span class="gosto {t}">{TASTE_LABEL[t]}</span><br><small>{sign}{abs(pts)} pontos</small>', cell])
    return table(["Reação", "Itens"], rows, cls="wikitable presentes")


def infobox(title, img_html, rows, cls=""):
    trs = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rows if b)
    return f'<aside class="infobox {cls}"><div class="ib-titulo">{esc(title)}</div>{img_html}<table>{trs}</table></aside>'


def portrait_img(k, big=True):
    ps = PORTRAITS.get(k) or []
    if ps:
        return f'<img class="retrato" src="img/retratos/{ps[0][0]}" alt="Retrato" loading="lazy">'
    return f'<img class="boneco grande" src="{sprite(k)}" alt="Bonequinho" loading="lazy">'


def sprite(k):
    return "img/andrea.png" if k == "andrea" else f"../img/chars/{k}.png"


def char_page(k):
    d = NPCS[k]
    bd = festas.BIRTHDAYS.get(k)
    cap = 10 if k in characters.ROMANCES else config.FRIEND_CAP_HEARTS
    img = portrait_img(k) + f'<div class="ib-boneco"><img class="boneco" src="../img/chars/{k}.png" alt="" loading="lazy"></div>'
    loves = [i for i, t in TASTE[k].items() if t == "love" and i in ITEMS][:4]
    rows = [
        ("Nome", esc(d["name"])),
        ("Trabalho", esc(d["role"])),
        ("Aniversário", f'<a href="calendario.html">{day_name(*bd)}</a>' if bd else "—"),
        ("Mora em", home_of(k)),
        ("Romance", '<a href="romance.html">Sim</a>' if k in characters.ROMANCES else "Não"),
        ("Corações", f"até {cap}"),
        ("Ama", " ".join(item(i) for i in loves)),
    ]
    body = [infobox(d["name"], img, rows, "pessoa")]
    body.append(f'<p class="lead">{esc(BIO.get(k, d["role"]))}</p>')
    if k in characters.ROMANCES:
        body.append(box("rosa", "Romance:", "dê as Rosas com 8 corações para namorar e o Pingente com 10 para morar "
                        'junto. Veja a página <a href="romance.html">Romance</a>.'))
    body.append("<h2>Rotina</h2>")
    body.append(schedule_html(k))
    body.append("<h2>Presentes</h2>")
    if bd:
        body.append(f'<p>No aniversário ({day_name(*bd)}), o presente vale mais: amado ×5, gostou ×3 e neutro ×2.</p>')
    body.append(gifts_html(k))
    body.append("<h2>Eventos de coração</h2>")
    body.append(events_html(k))
    lines = d.get("lines") or {}
    quotes = []
    for key, lab in (("low", "Logo que se conhecem"), ("mid", "Com amizade"), ("high", "Bem próximas")):
        ls = lines.get(key) if isinstance(lines, dict) else None
        if ls:
            quotes.append(f'<blockquote><p>“{esc(ls[0])}”</p><cite>{lab}</cite></blockquote>')
    if quotes:
        body.append("<h2>Falas</h2>" + "".join(quotes))
    body.append(messages_html(celular.MSGS.get(k, []), celular.MORNING.get(k, []), k in MALE))
    ps = PORTRAITS.get(k) or []
    if len(ps) > 1:
        figs = "".join(f'<figure><img src="img/retratos/{f}" alt="{esc(lab)}" loading="lazy"><figcaption>{lab}</figcaption></figure>'
                       for f, lab in ps)
        body.append(f'<h2>Retratos</h2><div class="galeria-retratos">{figs}</div>')
    elif not ps:
        body.append('<p class="nota">Ainda sem retrato desenhado: a caixa de fala usa o bonequinho.</p>')
    body.append(navbox())
    write(f"{k}.html", d["name"], "\n".join(body), [("personagens.html", "Personagens")],
          desc=f'{d["name"]}: {d["role"]}. Rotina, presentes e eventos.', cat="Personagem", icon=f"cabecas/{k}.png")


def messages_html(msgs, morning, male, title=True):
    """Mensagens do celular: o texto e as 3 respostas (com a volta), escondidas num <details>."""
    if not msgs and not morning:
        return ""
    def one(t, rs):
        lis = "".join(f'<li><b>{esc(a)}</b> <span>→ {esc(b)}</span></li>' for a, b in rs)
        return f'<div class="msg"><p class="balao">{esc(t)}</p><ul>{lis}</ul></div>'
    who = "ele" if male else "ela"
    out = ['<h2>Mensagens no celular</h2>' if title else "",
           f'<p>Com 2 corações, {who} manda mensagens de vez em quando (app Mensagens, tecla <kbd>T</kbd>). '
           'Responder dá amizade e carisma.</p>' if title else "",
           f'<details class="spoiler"><summary>Ver as {len(msgs) + len(morning)} mensagens e as respostas</summary>']
    out += [one(t, rs) for t, rs in msgs]
    if morning:
        out.append("<h4>Bom dia (namorando)</h4>")
        out += [one(t, rs) for t, rs in morning]
    out.append("</details>")
    return "".join(out)


def navbox():
    rows = "".join(f'<tr><th>{esc(t)}</th><td>{" ".join(npc(k) for k in ks)}</td></tr>' for t, ks in GROUPS)
    return f'<table class="navbox"><caption><a href="personagens.html">Personagens de National City</a></caption>{rows}</table>'


def personagens_page():
    body = ['<p class="lead">National City tem 20 pessoas para conhecer. Conversar uma vez por período (manhã, tarde e noite) '
            'e dar presentes enche os corações. Cada coração vale ' + str(HP) + ' pontos. Só a Lucy e a Vittoria passam de '
            f'{config.FRIEND_CAP_HEARTS} corações, e só namorando.</p>']
    for title, ks in GROUPS:
        if "andrea" in ks:                     # a Andrea tem seção própria logo abaixo
            continue
        cards = []
        for k in ks:
            d = NPCS[k]
            bd = festas.BIRTHDAYS.get(k)
            pill = '<span class="pill rosa">romance</span>' if k in characters.ROMANCES else ""
            cards.append(f'<a class="cartao-pessoa" href="{k}.html"><img src="../img/chars/{k}.png" alt="" loading="lazy">'
                         f'<b>{esc(d["name"])}</b><span>{esc(d["role"])}</span>'
                         f'<small>Aniversário: {day_name(*bd) if bd else "—"}</small>{pill}</a>')
        body.append(f'<h2>{esc(title)}</h2><div class="grade-pessoas">{"".join(cards)}</div>')
    body.append('<h2>De fora da cidade</h2><div class="grade-pessoas"><a class="cartao-pessoa" href="andrea.html">'
                '<img src="img/andrea.png" alt=""><b>Andrea Rojas</b><span>Amiga da Letícia, de Metrópolis</span>'
                '<small>Visita uma vez por estação</small></a></div>')
    body.append('<h2>Protagonista</h2><div class="grade-pessoas"><a class="cartao-pessoa" href="leticia.html">'
                '<img src="../img/chars/leticia.png" alt=""><b>Letícia Luthor</b><span>CEO da Luthor Corp</span>'
                f'<small>Aniversário: {day_name(*surpresa.BDAY)}</small></a></div>')
    write("personagens.html", "Personagens", "\n".join(body), desc="Todas as personagens de Luthor Life.", cat="Página")


def leticia_page():
    img = portrait_img("leticia") + '<div class="ib-boneco"><img class="boneco" src="../img/chars/leticia.png" alt=""></div>'
    rows = [("Nome", "Letícia Luthor"), ("Trabalho", "CEO da Luthor Corp"),
            ("Aniversário", f'<a href="calendario.html">{day_name(*surpresa.BDAY)}</a>'),
            ("Mora em", "Cobertura Luthor (Residencial Luthor)"), ("Olhos", "Verdes")]
    body = [infobox("Letícia Luthor", img, rows, "pessoa"),
            '<p class="lead">Letícia Luthor é a protagonista: a jovem CEO da Luthor Corp, em National City. Depois da '
            'morte do pai, Alexander, ela assume a empresa, o laboratório e um conselho cheio de opiniões. Os tios, '
            'Conrad e Edmund, querem a empresa de volta.</p>',
            "<h2>O dia a dia</h2>",
            "<p>O dia começa às 6h na cobertura e termina quando ela vai dormir (ou às 2h, quando desmaia e acorda no "
            'hospital). Entre uma coisa e outra: trabalhar no <a href="laboratorio.html">laboratório</a>, vender '
            'produtos na Mesa de Contratos, <a href="peixes.html">pescar</a>, cozinhar, cuidar da '
            '<a href="horta.html">horta</a>, conversar com a cidade e, quem sabe, se apaixonar.</p>',
            "<h2>Aniversário</h2>",
            f'<p>No dia {surpresa.BDAY[1]} do Outono (véspera da Feira da Colheita) as amigas preparam uma festa surpresa no '
            'terraço, das 19h às 23h, com a Jess de anfitriã. Vão a namorada e as amigas com 2 ou mais corações, cada uma '
            'com um presente. Quem perde a festa ganha o bolo da Jess na manhã seguinte.</p>',
            "<h2>Closet</h2>",
            f'<p>O guarda-roupa da cobertura tem {len(closet.LOOKS)} looks e os acessórios comprados na '
            '<a href="lojas.html#boutique">La Boutique</a>. A roupa escolhida aparece no jogo e nas cenas, e as amigas '
            'comentam o look.</p>',
            shot("closet", "Closet da Letícia"),
            navbox()]
    write("leticia.html", "Letícia Luthor", "\n".join(body), [("personagens.html", "Personagens")],
          desc="Letícia Luthor, a protagonista.", cat="Personagem", icon="cabecas/leticia.png")


def andrea_page():
    k = "andrea"
    img = portrait_img(k) + '<div class="ib-boneco"><img class="boneco" src="img/andrea.png" alt=""></div>'
    rows = [("Nome", "Andrea Rojas"), ("Quem é", "Amiga da Letícia desde a faculdade"),
            ("Mora em", "Metrópolis"), ("Na cidade", "Uma visita por estação"),
            ("Celular", f"{len(andrea.MSGS)} conversas no app Mensagens")]
    vis = []
    for q, v in sorted(andrea.VISITS.items()):
        gift = andrea.GIFTS.get(q)
        vis.append([f"<b>{SEASON[q]}</b>", f"Dia {v[0]} ({weekday(v[0])})", esc(cap(v[4])),
                    f"{hm(v[2])} às {hm(v[3])}", item(gift) if gift in ITEMS else "—"])
    body = [infobox("Andrea Rojas", img, rows, "pessoa"),
            '<p class="lead">Andrea Rojas é amiga da Letícia desde a faculdade, em Gotham, e hoje comanda os próprios '
            'negócios em Metrópolis. Não mora em National City, então não entra no painel de relacionamentos: a amizade '
            'cresce pelas mensagens e pelas visitas. Ela não tem nada a ver com a Luthor Corp: é só amiga.</p>',
            "<h2>Visitas</h2>",
            "<p>Uma vez por estação ela vem à cidade. Na véspera chega um aviso, de manhã o convite pelo celular, e a cena "
            "toca quando a Letícia chega ao lugar no horário. Cada visita dá um presente, energia (+30), "
            "carisma e <b>bom astral</b>: as conversas rendem 25% mais amizade até o fim do dia.</p>",
            table(["Estação", "Dia", "Onde", "Horário", "Presente"], vis),
            "<h2>Mensagens</h2>",
            f"<p>A partir do {andrea.FIRST_DAY}º dia ela manda mensagens de vez em quando, como as amigas da cidade. Cada "
            "mensagem tem três respostas e ela sempre responde de volta.</p>",
            messages_html(andrea.MSGS, [], False, title=False),
            shot("andrea","Visita da Andrea no terraço", "A visita de inverno, no terraço"),
            shot("celular", "Mensagem da Andrea no celular")]
    ps = PORTRAITS.get(k) or []
    if len(ps) > 1:
        figs = "".join(f'<figure><img src="img/retratos/{f}" alt="{esc(lab)}" loading="lazy"><figcaption>{lab}</figcaption></figure>'
                       for f, lab in ps)
        body.append(f'<h2>Retratos</h2><div class="galeria-retratos">{figs}</div>')
    body.append(navbox())
    write("andrea.html", "Andrea Rojas", "\n".join(body), [("personagens.html", "Personagens")],
          desc="Andrea Rojas, amiga da Letícia que mora em Metrópolis.", cat="Personagem", icon="cabecas/andrea.png")


# ============================ presentes / romance ====================================
def presentes_page():
    rows = []
    for k in ORDER:
        loves = sorted([i for i, t in TASTE[k].items() if t == "love" and i in ITEMS], key=lambda i: ITEMS[i]["name"])
        bd = festas.BIRTHDAYS.get(k)
        rows.append([npc(k), '<div class="itens">' + "".join(item(i) for i in loves) + "</div>",
                     day_name(*bd) if bd else "—"])
    body = ['<p class="lead">Cada personagem aceita até 2 presentes por semana e 1 por dia. Coletáveis também são '
            'presenteáveis: são neutros para quase todo mundo, mas algumas pessoas adoram e outras detestam.</p>',
            table(["Reação", "Amizade", "Retrato"],
                  [[f'<span class="gosto love">Ama</span>', f'+{GP["love"]}', "Tímido"],
                   [f'<span class="gosto like">Gosta</span>', f'+{GP["like"]}', "Feliz"],
                   [f'<span class="gosto neutral">Neutro</span>', f'+{GP["neutral"]}', "Normal"],
                   [f'<span class="gosto dislike">Não gosta</span>', f'{GP["dislike"]}', "Mau humor"]]),
            f'<p>Um coração = {HP} pontos. No aniversário: amado ×5, gostou ×3, neutro ×2. A Dra. Addison, com 3 corações, '
            'faz os presentes renderem 15% a mais.</p>',
            "<h2>O que cada uma ama</h2>",
            table(["Personagem", "Presentes amados", "Aniversário"], rows),
            '<p>A lista completa (gosta e não gosta) está na página de cada personagem. Cada item mostra quem gosta '
            'dele na própria página.</p>']
    write("presentes.html", "Presentes", "\n".join(body), desc="Guia de presentes: o que cada personagem ama.")


def romance_page():
    body = ['<p class="lead">Duas pessoas podem namorar a Letícia: <b>Lucy Williams</b> e <b>Vittoria Ricci</b>. '
            'Todas as outras amizades param em 8 corações.</p>']
    cards = []
    for k in characters.ROMANCES:
        d = NPCS[k]
        places = d.get("date_places", [])
        lis = "".join(f"<li>{esc(p[4])}</li>" for p in places)
        cards.append(f'<div class="cartao-romance"><img src="../img/chars/{k}.png" alt=""><div><h3>{npc(k, True)}</h3>'
                     f'<p>{esc(BIO[k])}</p><h4>Encontros</h4><ul>{lis}</ul></div></div>')
    body.append('<div class="romances">' + "".join(cards) + "</div>")
    steps = [
        ("Até 8 corações", "Converse todo dia e dê presentes. Os eventos de coração contam a história de cada uma. "
                           "Antes do namoro, a amizade para em 8 corações (os corações 9 e 10 aparecem com cadeado)."),
        ("Rosas (8 corações)", f'Compre o {item("rosas")} e entregue. Ela marca o pedido de namoro para um lugar e horário '
                               '(linha rosa no HUD). A cena termina com um beijo.'),
        ("Namoro", 'Convide para encontros à noite (19h–22h), dê beijos (+30 de amizade uma vez por dia) e abra os corações '
                   '9 e 10. Encontros especiais: piquenique, veleiro ao pôr do sol, cinema a dois e jantar na cobertura.'),
        ("Pingente (10 corações)", f'O {item("pingente")} é o convite para morar junto na cobertura.'),
        ("Vida a dois", "Café da manhã juntas em algumas manhãs (sempre no fim de semana), um pedido pequeno por dia e "
                        "aniversário de namoro a cada 56 dias, com jantar e presente."),
        ("Noivado", f'Depois de {casamento.MIN_DAYS} dias morando junto, o {item("anel_noivado") if "anel_noivado" in ITEMS else "Anel de Noivado"} '
                    'aparece no Mercado. Dar o anel marca o pedido para a mesma noite, no terraço (19h–23h).'),
        ("Casamento", "7 dias depois do sim, das 15h às 19h, no Jardim do Mirante. A Sam celebra, a Jess fica de um lado e a "
                      "madrinha do outro (a Nia para a Lucy, a Dona Graça para a Vittoria). No fim: $2.000 e amizade com todos."),
    ]
    body.append("<h2>Passo a passo</h2>")
    body.append('<ol class="passos">' + "".join(f"<li><b>{t}</b><p>{x}</p></li>" for t, x in steps) + "</ol>")
    body.append("<h2>Ciúmes leves</h2><p>Conversas, presentes, encontros e beijos com uma das duas contam atenção nos "
                "últimos 3 dias. Se uma receber bem mais que a outra, a outra comenta na próxima conversa (no máximo a cada "
                "4 dias). Qualquer resposta dá amizade. Depois que a Letícia namora uma, a outra não sente mais ciúmes.</p>")
    body.append(shot("casamento", "Casamento no Jardim do Mirante", "O casamento no Jardim do Mirante"))
    write("romance.html", "Romance", "\n".join(body), desc="Como namorar, morar junto e casar.")


# ============================ calendário / festas / estações =========================
def calendar_events():
    ev = {(q, d): [] for q in range(1, 5) for d in range(1, 15)}
    for k, (q, d) in festas.BIRTHDAYS.items():
        if k in NPCS:
            ev[(q, d)].append(f'<span class="ev niver">{head(k)}<a href="{k}.html">{esc(short(k))}</a></span>')
    q, d = surpresa.BDAY
    ev[(q, d)].append(f'<span class="ev niver">{head("leticia")}<a href="leticia.html">Letícia</a></span>')
    for fk, f in festas.FESTIVALS.items():
        ev[(f["quarter"], f["day"])].append(f'<span class="ev festa"><a href="festas.html#{fk}">{esc(f["name"])}</a></span>')
    for q, v in andrea.VISITS.items():
        ev[(q, v[0])].append('<span class="ev visita"><a href="andrea.html">Visita da Andrea</a></span>')
    ev[(4, 1)].append('<span class="ev festa"><a href="festas.html#luzes">Sorteio do amigo secreto</a></span>')
    return ev


def calendario_page():
    ev = calendar_events()
    body = [f'<p class="lead">O ano tem 4 estações de {config.DAYS_PER_QUARTER} dias. O dia 1 de cada estação é uma '
            'segunda-feira. O calendário do jogo abre com a tecla <kbd>C</kbd>.</p>',
            '<p class="legenda-cal"><span class="ev niver">Aniversário</span> <span class="ev festa">Festa</span> '
            '<span class="ev visita">Visita</span> <span class="ev semana">Toda semana</span></p>']
    weekly = {1: ["Corrida com a Sam 6h"], 3: ["Corrida com a Sam 6h", "Clube do livro 18h"], 5: ["Corrida com a Sam 6h"]}
    for q in range(1, 5):
        cells = "".join(f'<div class="dia-semana">{w}</div>' for w in WD)
        for d in range(1, 15):
            wd = (d - 1) % 7
            items = "".join(ev[(q, d)])
            wk = "".join(f'<span class="ev semana">{t}</span>' for t in weekly.get(wd, []))
            fds = " fds" if wd >= 5 else ""
            cells += f'<div class="dia{fds}"><b>{d}</b>{items}{wk}</div>'
        body.append(f'<h2 id="{["", "primavera", "verao", "outono", "inverno"][q]}">{SEASON[q]}</h2>'
                    f'<div class="calendario">{cells}</div>')
    body.append(shot("calendario", "Calendário do jogo"))
    write("calendario.html", "Calendário", "\n".join(body), desc="Aniversários, festas e eventos de cada estação.")


FEST_IMG = {"flores": "festa_flores", "luau": "luau", "feira": "feira", "luzes": "noite_luzes"}
FEST_ACT = {
    "flores": "Dança das Flores no mastro: convide alguém com 4 ou mais corações para dançar.",
    "luau": "Sopa do caldeirão: cada um põe um ingrediente e a Dona Graça prova. O ingrediente dá amizade com todos (nunca tira).",
    "feira": "Concurso da Feira: inscreva um item e o júri julga pelo valor. Prêmios de $600, $300 e $100, e o item volta para você.",
    "luzes": "Amigo secreto: o nome é sorteado no 1º dia do inverno. O presente vale ×3 e a Letícia ganha um de volta.",
}


def festas_page():
    body = ['<p class="lead">Uma festa por estação. No dia da festa a cidade inteira vai para lá, faz sol (menos no inverno) '
            'e não dá para marcar encontro à noite. Cada festa tem uma barraca que só vende naquele dia.</p>']
    for fk, f in festas.FESTIVALS.items():
        shop = '<div class="itens">' + "".join(item(i) for i in f.get("shop", []) if i in ITEMS) + "</div>"
        rows = [("Data", f'{day_name(f["quarter"], f["day"])} ({weekday(f["day"])})'),
                ("Horário", f'{hm(f["start"])} às {hm(f["end"])}'), ("Lugar", esc(cap(f["place"]))),
                ("Anfitriã" if f["host"] not in MALE else "Anfitrião", npc(f["host"])), ("Barraca", shop)]
        speech = f.get("speech") or []
        q = f'<blockquote><p>“{esc(speech[0])}”</p><cite>{esc(short(f["host"]))}</cite></blockquote>' if speech else ""
        body.append(f'<h2 id="{fk}">{esc(f["name"])}</h2>' + infobox(f["name"], "", rows, "festa")
                    + f'<p>{FEST_ACT.get(fk, "")}</p>' + q + shot(FEST_IMG.get(fk, ""), f["name"]) + '<div class="limpa"></div>')
    body.append('<h2>Aniversários</h2><p>Cada personagem faz aniversário num dia do <a href="calendario.html">calendário</a> '
                '(nunca em dia de festa). Na noite anterior chega um aviso, e no dia a pessoa segura um balão. Presente no '
                'aniversário: amado ×5, gostou ×3, neutro ×2.</p>')
    write("festas.html", "Festas", "\n".join(body), desc="As quatro festas do ano e os aniversários.")


def estacoes_page():
    rain = {"spring": 25, "summer": 12, "autumn": 32, "winter": 35}
    from luthor import clima
    rows = []
    for sk, q in SEASON_Q.items():
        fish = [k for k, f in data.FISH.items() if q in f["quarters"] and len(f["quarters"]) < 4]
        forage = [k for k, s in seasons.FORAGE_SEASONS.items() if sk in s]
        rows.append([f"<b>{SEASON[q]}</b>", f"{rain[sk]}%", f"{int(clima.STORM_CHANCE[sk] * 100)}% das chuvas" if clima.STORM_CHANCE[sk] else "—",
                     '<div class="itens">' + "".join(item(i) for i in fish) + "</div>",
                     '<div class="itens">' + "".join(item(i) for i in forage) + "</div>"])
    body = ['<p class="lead">Cada estação tem 14 dias. A grama, as árvores, os coletáveis, os peixes e as roupas de todo mundo '
            'mudam com ela. No inverno a chuva vira neve.</p>',
            table(["Estação", "Chuva", "Tempestade", "Peixes só desta estação", "Coletáveis da estação"], rows),
            "<h2>Clima</h2>",
            "<ul><li><b>Sol</b> ou <b>chuva</b> é sorteado na véspera e aparece na TV e no app Tempo do celular.</li>"
            "<li>Chovendo, todo mundo na rua anda de guarda-chuva e algumas pessoas mudam a rotina (veja a rotina de chuva "
            "de cada personagem).</li>"
            "<li><b>Tempestade:</b> raios clareiam a tela e trovões ressoam. Para peixes, rotinas e figurantes continua "
            "sendo chuva.</li></ul>"]
    write("estacoes.html", "Estações e clima", "\n".join(body), desc="O que muda em cada estação, chuva e tempestade.")


# ============================ itens =================================================
KIND = [("gift", "Presentes"), ("food", "Comidas e bebidas"), ("dish", "Pratos"), ("ingredient", "Ingredientes"),
        ("crop", "Colheita"), ("seed", "Sementes"), ("forage", "Coletáveis"), ("fish", "Peixes"), ("product", "Produtos"),
        ("proposal", "Propostas de projeto"), ("book", "Livros"), ("acessorio", "Acessórios"), ("treat", "Petiscos"),
        ("bait", "Isca"), ("tool", "Ferramentas"), ("junk", "Tralhas")]
KIND_NAME = dict(KIND)


def price_cells(it):
    p = it.get("price")
    v = it.get("value")
    return (money(p) if p else "—"), (money(v) if v else "—")


def itens_page():
    body = [f'<p class="lead">{len(ITEMS)} itens no jogo. Clique num item para ver de onde ele vem, para que serve e quem '
            'gosta de ganhar.</p>']
    toc = " · ".join(f'<a href="#{k}">{n}</a>' for k, n in KIND if any(v["kind"] == k for v in ITEMS.values()))
    body.append(f'<p class="indice">{toc}</p>')
    for kind, name in KIND:
        ks = [k for k, v in ITEMS.items() if v["kind"] == kind]
        if not ks:
            continue
        rows = []
        for k in sorted(ks, key=lambda k: ITEMS[k]["name"]):
            it = ITEMS[k]
            buy, sell = price_cells(it)
            rows.append([item(k), esc(it.get("desc", "")), buy, sell])
        body.append(f'<h2 id="{kind}">{name}</h2>' + table(["Item", "Descrição", "Compra", "Venda"], rows, sortable=True))
    write("itens.html", "Itens", "\n".join(body), desc="Todos os itens do jogo.")


def item_page(k):
    it = ITEMS[k]
    buy, sell = price_cells(it)
    rows = [("Tipo", f'<a href="itens.html#{it["kind"]}">{KIND_NAME.get(it["kind"], it["kind"])}</a>'),
            ("Compra", buy if buy != "—" else ""), ("Venda", sell if sell != "—" else "")]
    if it.get("energy"):
        rows.append(("Energia", f'+{it["energy"]}'))
    if k in ALL_FISH:
        f = ALL_FISH[k]
        rows += [("Onde", FISH_WHERE.get(f["where"], f["where"])), ("Estações", seasons_txt(f["quarters"])),
                 ("Horário", f'{hm(f["hours"][0])} às {hm(f["hours"][1])}')]
    img = f'<div class="ib-icone">{ico(k, 96, "ico grande")}</div>'
    body = [infobox(it["name"], img, rows, "coisa"), f'<p class="lead">{esc(it.get("desc", ""))}</p>']
    if k in data.RECIPES:
        r = data.RECIPES[k]
        need = ", ".join(f"{item(n)} ×{q}" for n, q in r["needs"].items())
        book = f' Precisa do livro {item(r["book"])}.' if r.get("book") else ""
        body.append(f"<h2>Receita</h2><p>{need}.{book}</p>")
    src = SOURCES.get(k) or []
    body.append("<h2>Como conseguir</h2>" + ("<ul>" + "".join(f"<li>{s}</li>" for s in src) + "</ul>" if src
                                              else "<p>Não é vendido em loja: aparece em eventos ou como recompensa.</p>"))
    uses = USES.get(k) or []
    if uses:
        body.append("<h2>Usado em</h2><ul>" + "".join(f"<li>{u}</li>" for u in uses) + "</ul>")
    if it["kind"] not in ("proposal", "tool", "seed"):
        groups = {"love": [], "like": [], "dislike": []}
        for n in ORDER:
            t = taste_of(n, k)
            if t in groups:
                groups[t].append(n)
        rows = []
        for t in ("love", "like", "dislike"):
            if groups[t]:
                rows.append([f'<span class="gosto {t}">{TASTE_LABEL[t]}</span>', " ".join(npc(n) for n in groups[t])])
        rows.append(['<span class="gosto neutral">Neutro</span>', "Todas as outras personagens"])
        body.append("<h2>Como presente</h2>" + table(["Reação", "Personagens"], rows))
    write(f"item-{k}.html", it["name"], "\n".join(body), [("itens.html", "Itens")],
          desc=it.get("desc", it["name"]), cat=KIND_NAME.get(it["kind"], "Item"), icon=f"itens/{k}.png")


def peixes_page():
    rows = []
    for k, f in sorted(ALL_FISH.items(), key=lambda kv: (kv[1]["where"] == "deep", kv[1]["value"])):
        diff = int(f.get("diff", 0))
        bar = f'<span class="dific" style="--d:{min(100, diff)}%" title="{diff}"></span>'
        rows.append([item(k), money(f["value"]), FISH_WHERE.get(f["where"], f["where"]), seasons_txt(f["quarters"]),
                     f'{hm(f["hours"][0])}–{hm(f["hours"][1])}', bar])
    body = ['<p class="lead">Escolha a vara na barra, fique de frente para a água e aperte <kbd>E</kbd>. Quando aparecer '
            'o “!”, aperte de novo e mantenha o peixe dentro da barra até a linha encher. O Seu Joca vende iscas no píer e o '
            '<a href="item-livro_pesca.html">Manual do Pescador</a> deixa a barra 30% maior.</p>',
            table(["Peixe", "Valor", "Onde", "Estações", "Horário", "Dificuldade"], rows, sortable=True),
            "<h2>Alto-mar</h2><p>Os peixes de alto-mar só aparecem no passeio de pesca da Marina Luthor "
            f'({money(marina.PRICES["fishing"])}). Com o evento de 4 corações do Ian, eles valem 15% a mais.</p>',
            "<h2>Bônus</h2><ul><li>Peixaria do Píer (Fundação Luthor): peixes valem 10% a mais.</li>"
            "<li>Barry, evento de coração: +$50 por espécie nova.</li><li>Habilidade de pesca: barra maior a cada nível; "
            "no nível 5, peixes valem 10% a mais.</li><li>Aquário da cobertura: cada espécie pescada aparece lá.</li></ul>",
            shot("fishing", "Minigame de pesca")]
    write("peixes.html", "Peixes", "\n".join(body), desc="Todos os peixes: onde, quando e quanto valem.")


def receitas_page():
    rows = []
    for k, r in data.RECIPES.items():
        need = "<br>".join(f"{item(n)} ×{q}" for n, q in r["needs"].items())
        learn = item(r["book"]) if r.get("book") else "Desde o começo"
        rows.append([item(k), need, f'+{r["energy"]}', money(r["value"]), learn])
    body = ['<p class="lead">Cozinhe no fogão da cobertura (<kbd>E</kbd>). Os pratos dão energia, viram presentes ótimos e '
            'rendem bem na venda. A habilidade de culinária aumenta a energia que a comida dá.</p>',
            table(["Prato", "Ingredientes", "Energia", "Venda", "Como aprender"], rows, sortable=True),
            shot("cozinhar", "Fogão da cobertura")]
    write("receitas.html", "Receitas", "\n".join(body), desc="Todas as receitas do fogão.")


def horta_page():
    rows = []
    for ck, c in data.CROPS.items():
        seed = next((k for k, v in ITEMS.items() if v["kind"] == "seed" and v.get("crop") == ck), None)
        out = c["item"]
        rows.append([item(seed) if seed else esc(c["name"]), money(c["seed"]), f'{c["days"]} dias',
                     f'{item(out)} ×{c["qty"]}', f'a cada {c["regrow"]} dias' if c.get("regrow") else "Não",
                     money(ITEMS[out]["value"]) if out in ITEMS and ITEMS[out].get("value") else "—"])
    frows = []
    for k, f in data.FORAGE.items():
        qs = seasons.FORAGE_SEASONS.get(k)
        frows.append([item(k), AREA_NAMES.get(f["where"], f["where"]),
                      seasons_txt([SEASON_Q[s] for s in qs]) if qs else "Ano todo", money(f["value"])])
    body = ['<p class="lead">A horta fica no terraço da cobertura. Compre sementes no Mercado Central, plante num canteiro '
            'e regue todo dia. Chuva rega sozinha.</p>',
            table(["Semente", "Preço", "Cresce em", "Colheita", "Rebrota", "Venda"], rows, sortable=True),
            '<h2>Coletáveis</h2><p>Coisinhas que aparecem no chão do parque, do bosque e da praia todas as manhãs. Aperte '
            '<kbd>E</kbd> para pegar. As Lanternas do Bosque (Fundação Luthor) fazem aparecer mais.</p>',
            table(["Coletável", "Onde", "Estações", "Venda"], frows, sortable=True),
            shot("terrace", "Terraço com a horta")]
    write("horta.html", "Horta e coletáveis", "\n".join(body), desc="Sementes, colheitas e coletáveis.")


def lojas_page():
    body = ['<p class="lead">Lojas de National City. Os preços mudam com alguns bônus de amizade (veja abaixo de cada loja).</p>']
    for sk, s in data.SHOPS.items():
        mp, who = SHOP_PLACE.get(sk, (None, None))
        rows = []
        for k in s["stock"]:
            if k in ITEMS:
                rows.append([item(k), money(ITEMS[k].get("price", 0)), esc(ITEMS[k].get("desc", ""))])
        meta = []
        if mp:
            meta.append("Lugar: " + (place_link(mp) if mp != "city" else "píer, na praia"))
        if who:
            meta.append("Quem atende: " + npc(who))
        lab = data.FLAG_LABELS.get(s.get("discount_flag"))
        if lab:
            meta.append("Bônus: " + esc(lab))
        body.append(f'<h2 id="{sk}">{esc(s["title"])}</h2><p class="sub">{esc(s["subtitle"])}</p><p>{" · ".join(meta)}</p>'
                    + table(["Item", "Preço", "Descrição"], rows, sortable=True))
    rows = [[item(k), money(a["price"]), esc(a.get("slot", "").capitalize()), esc(a.get("desc", ""))]
            for k, a in boutique.ACCESSORIES.items() if k in ITEMS]
    looks = [[esc(v[0]), money(v[1]), esc(v[3])] for v in closet.LOOKS.values() if v[1]]
    body.append('<h2 id="boutique">La Boutique</h2><p class="sub">Roupas e acessórios da Celeste.</p>'
                f'<p>Lugar: {place_link("boutique")} · Quem atende: {npc("celeste")} · Com o evento de 4 corações, '
                '20% de desconto. Tem provador: dá para ver o look antes de comprar.</p>'
                "<h3>Acessórios</h3>" + table(["Acessório", "Preço", "Onde vai", "Descrição"], rows, sortable=True)
                + "<h3>Roupas</h3>" + table(["Look", "Preço", "Descrição"], looks, sortable=True)
                + shot("boutique", "La Boutique"))
    p = marina.PRICES
    body.append('<h2 id="marina">Marina Luthor</h2>'
                f'<p>Passeios com o {npc("ian")}: pesca no alto-mar ({money(p["fishing"])}), pôr do sol ({money(p["sunset"])}) e '
                f'regata ({money(p["regatta"])}; prêmios de {money(marina.REGATTA_PRIZES[1])}, {money(marina.REGATTA_PRIZES[2])} '
                f'e {money(marina.REGATTA_PRIZES[3])}). As encomendas do Ian pagam 25% a mais que a Mesa de Contratos.</p>')
    write("lojas.html", "Lojas", "\n".join(body), desc="O que cada loja vende e por quanto.")


# ============================ lugares ===============================================
PLACE_TXT = {
    "home": ("Cobertura Luthor", "A casa da Letícia: cama, fogão, aquário, closet, piano, computador (ações e decoração), "
             "mural de fotos e a caminha do bichinho. O elevador desce para a portaria do Residencial Luthor.", "decorar"),
    "terrace": ("Terraço", "Em cima da cobertura: horta, espreguiçadeira, telescópio e a vista da cidade. Palco da festa "
                "surpresa e do pedido de casamento.", "terrace"),
    "hq": ("Sede da Luthor Corp", "Escritório da Letícia, laboratório com as bancadas, Terminal P&D, Mesa de Contratos, "
           "sala de reuniões do conselho, a salinha da Sam e a mesa da Fundação Luthor.", "lab"),
    "cafe": ("Café Grão Nobre", "O café do Harry, com o quadro de pedidos dos moradores na parede.", None),
    "catco": ("CatCo Worldwide Media", "A redação da Lucy, da Nia e do Barry, com o estúdio da CatCo TV e o arquivo de "
              "matérias antigas.", "arquivo"),
    "books": ("Bayside Books", "A livraria do Theo. Livros com bônus permanentes e o clube do livro às quintas.", "clube"),
    "market": ("Mercado Central", "A loja da Bea: ingredientes, sementes, flores e presentes. O Anel de Noivado aparece aqui.", None),
    "trattoria": ("Ricci Trattoria", "O restaurante da Dona Graça, o primeiro da Vittoria.", "dialog"),
    "bar": ("Noonan's", "O pub do Marco: fliperama Meteoro, sinuca, dardos e karaokê.", "karaoke"),
    "cinema": ("Cine National", "Sessões de cinema com pipoca. Ótimo lugar para um encontro.", "movie"),
    "hospital": ("Conti Moretti Hospitais", "Consultas com bônus do dia, farmácia, brinquedoteca e o leito onde a Letícia "
                 "acorda quando desmaia.", "hospital"),
    "ricci": ("Gruppo Ricci", "A sede da rede de restaurantes da Vittoria, com o escritório dela, a sala de projetos e a adega.",
              "ricci"),
    "marina": ("Marina Luthor", "A divisão náutica da Luthor Corp, com o Ian. Passeios de barco, regata e encomendas.", "marina"),
    "boutique": ("La Boutique", "A loja da Celeste, com provador.", "boutique"),
    "bayside": ("Apartamentos Bayside", "Portaria (aberta das 7h às 23h) dos apartamentos da Lucy, Vittoria, Brainy, Jess, "
                "Nia e Barry. A porta de cada apartamento abre com a pessoa em casa e 2 corações.", None),
    "residencial": ("Residencial Luthor", "Portaria sempre aberta, com os apartamentos da Sam, do Ian e da Milany e o "
                    "elevador da cobertura.", None),
}
OUTDOOR = [("Parque Central", "Chafariz, lago para pescar, coletáveis e a Festa das Flores.", "park"),
           ("Bosque Bayside", "Árvores grandes, pinhas e um lago tranquilo.", "woods"),
           ("Jardim do Mirante", "Jardim no alto da cidade: Noite das Luzes e casamento.", "garden"),
           ("Praia e píer", "Mar, conchas, pesca no píer, o Luau e a barraca do Seu Joca.", "beach")]


def lugares_page():
    regular = {}
    for k in ORDER:
        sc = NPCS[k]["schedule"]
        rows = sc["default"] if isinstance(sc, dict) else []
        for r in rows:
            if r[1] and r[1] in PLACE_TXT and r[1] not in ("bayside", "residencial", "home"):
                regular.setdefault(r[1], [])
                if k not in regular[r[1]]:
                    regular[r[1]].append(k)
    body = ['<p class="lead">National City é uma cidade à beira-mar. O mapa abre com a tecla <kbd>M</kbd> e mostra onde '
            'cada pessoa está.</p>']
    if os.path.exists(os.path.join(IMG, "mapa.png")):
        body.append('<figure class="foto mapa"><img src="img/mapa.png" alt="Mapa de National City"><figcaption>Mapa de '
                    'National City</figcaption></figure>')
    body.append("<h2>Ao ar livre</h2>")
    for n, t, im in OUTDOOR:
        body.append(f'<div class="lugar">{shot(im, n)}<div><h3>{n}</h3><p>{t}</p></div></div>')
    body.append("<h2>Prédios</h2>")
    body.append('<p>As lojas, os restaurantes e os escritórios têm <b>horário de funcionamento</b>: fora dele a porta fica '
                'trancada. Quem comanda o lugar deixa a Letícia entrar a qualquer hora com <b>2 corações</b> (lojas, cafés '
                'e restaurantes) ou <b>4 corações</b> (CatCo e Gruppo Ricci). Encontros, eventos e visitas marcados ali '
                'também abrem a porta. A Luthor Corp, a Marina, o hospital e as casas não fecham.</p>')
    hrows = []
    for m, (a, b, owners, h) in horarios.OPEN_HOURS.items():
        quem = " ".join(npc(k) for k in owners) if owners else "—"
        hrows.append([f'<a href="#{m}">{esc(PLACE_TXT[m][0] if m in PLACE_TXT else m)}</a>', esc(horarios.hours_text(m)),
                      quem, f"{h} corações" if owners else "ninguém"])
    body.append(table(["Lugar", "Horário", "Quem libera", "Fora do horário"], hrows))
    for m, (n, t, im) in PLACE_TXT.items():
        who = regular.get(m, [])
        w = f'<p class="quem">Quem aparece: {" ".join(npc(k) for k in who)}</p>' if who else ""
        hr = (f'<p class="quem">Horário: {esc(horarios.hours_text(m))}</p>' if m in horarios.OPEN_HOURS
              else '<p class="quem">Horário: sempre aberto</p>' if m in ("hq", "marina", "hospital") else "")
        body.append(f'<div class="lugar" id="{m}">{shot(im, n) if im else ""}<div><h3>{esc(n)}</h3><p>{t}</p>{hr}{w}</div></div>')
    write("lugares.html", "Lugares", "\n".join(body), desc="Lugares de National City.")


# ============================ empresa ===============================================
def laboratorio_page():
    rows = []
    for k, p in data.PROJECTS.items():
        lock = p.get("locked_flag")
        how = "Desde o começo"
        if lock:
            how = esc(data.FLAG_LABELS.get(lock, "")) or {"gaia": "Câmara de crescimento", "prometeu": "Supercomputador"}.get(k, "Desbloqueio especial")
        rows.append([item(k) if k in ITEMS else esc(p["name"]), money(p["cost"]), f'{p["days"]} dias', money(p["value"]),
                     seasons_txt(p["quarters"]), how])
    up = [[esc(u["name"]), money(u["price"]), esc(u["desc"])] for u in laboratorio.UPGRADES]
    body = ['<p class="lead">O coração da Luthor Corp. É assim que a Letícia ganha dinheiro.</p>',
            '<ol class="passos"><li><b>Proposta</b><p>Compre a proposta no Terminal P&amp;D da sede. Cada projeto só aparece '
            'nas estações em que está em alta.</p></li><li><b>Bancada</b><p>Coloque a proposta numa bancada e trabalhe nela '
            '(<kbd>E</kbd>) um pouco por dia. Projetos só avançam nos dias em que alguém trabalha.</p></li><li><b>Produto</b>'
            '<p>Quando fica pronto, o produto vai para a mochila.</p></li><li><b>Mesa de Contratos</b><p>Coloque o produto na '
            'mesa: ele é vendido à noite. As vendas também mexem na ação LCORP.</p></li></ol>',
            "<h2>Projetos</h2>", table(["Produto", "Proposta", "Tempo", "Valor", "Estações", "Como liberar"], rows, sortable=True),
            "<h2>Melhorias do laboratório</h2><p>Compradas no painel do laboratório. Cada uma aparece encostada na parede.</p>",
            table(["Melhoria", "Preço", "Efeito"], up),
            "<h2>Ações LCORP</h2><p>A ação da Luthor Corp muda toda noite: um pouco de sorte, mais o quanto você vendeu "
            "(cada $800 em produtos sobe a ação) e bônus de amizade. Compre e venda pelo computador da cobertura ou pelo "
            "app Bolsa do celular.</p>",
            "<h2>Bônus</h2><ul><li>Sam, 4 corações: Mesa de Contratos +10%. Sam, 8 corações: +25% (35% no total).</li>"
            "<li>Brainy, 6 corações: projetos 1 dia mais rápidos.</li><li>Jess, 5 corações: das 9h às 12h o relógio anda 10% "
            "mais devagar.</li><li>História da Luthor Corp concluída: produtos +10%.</li><li>Habilidade de ciência: bancada "
            "gasta menos energia; no nível 5, produtos +10%.</li><li>Anúncio na CatCo TV: produtos +15% por 3 noites.</li></ul>",
            shot("lab", "Laboratório da sede")]
    write("laboratorio.html", "Laboratório", "\n".join(body), desc="Projetos, melhorias e ações da Luthor Corp.")


def fundacao_page():
    body = ['<p class="lead">A Fundação Luthor faz obras para a cidade. Na mesa da Fundação, na sede, doe os itens pedidos '
            '(ou o dinheiro). A obra aparece na cidade na noite seguinte e dá um benefício para sempre. A Praça só abre com as '
            'outras cinco prontas.</p>']
    for p in fundacao.PROJECTS:
        its = "".join(f"<li>{item(i)} ×{n}</li>" for i, n in p["items"])
        mon = f"<li>{money(p['money'])}</li>" if p.get("money") else ""
        body.append(f'<h2 id="{p["key"]}">{esc(p["name"])}</h2><p>{esc(p["desc"])} <i>({esc(p["place"])})</i></p>'
                    f'<div class="duas"><div><h4>Doações</h4><ul class="lista-itens">{its}{mon}</ul></div>'
                    f'<div><h4>Benefício</h4><p>{esc(p["perk"])}</p></div></div>')
    body.append(shot("fundacao", "Obras da Fundação na cidade"))
    write("fundacao.html", "Fundação Luthor", "\n".join(body), desc="As obras da Fundação Luthor.")


def historia_page():
    goals = ["Lance 5 produtos no laboratório.", "Fature $6.000 no total.", "Leve a ação LCORP a $110.",
             "Chegue a 4 corações com Sam, Brainy, Jess e Ian."]
    rows = []
    for i, c in enumerate(historia.CHAPTERS):
        rows.append([str(i + 1), esc(c["title"]), f'{esc(c["where"])}, das {c["hours"][0]}h às {c["hours"][1]}h',
                     goals[i] if i < len(goals) else "Fim: produtos +10%, $3.000 e amizade com a equipe."])
    body = ['<p class="lead">A partir do 3º dia começa a história da Luthor Corp: os tios Conrad e Edmund querem a empresa de '
            'volta. São 5 capítulos. Cada um tem uma cena (aparece no HUD com o lugar e o horário) e, depois, um objetivo que '
            'libera o próximo.</p>',
            '<details class="spoiler"><summary>Mostrar os capítulos (spoiler)</summary>'
            + table(["#", "Capítulo", "Onde e quando", "Objetivo depois"], rows)
            + "<p>A mesa da sala de reuniões da sede mostra os capítulos já vistos.</p></details>",
            "<h2>Eventos de coração</h2><p>Além da história da empresa, cada personagem tem seus eventos de coração, com cenas "
            "que tocam no lugar e horário certos (veja a página de cada personagem). Eles também podem ser revistos no menu de "
            "pausa.</p>",
            shot("cutscene", "Cena do jogo")]
    write("historia.html", "História", "\n".join(body), desc="Os capítulos da história da Luthor Corp.")


# ============================ vida ===================================================
def hospital_page():
    rows = []
    for s in hospital.SPECIALTIES:
        rows.append([f"<b>{esc(s[1])}</b>", npc(s[2]) if s[2] in NPCS else esc(s[2]), esc(s[3]), esc(s[5])])
    body = [f'<p class="lead">O Conti Moretti Hospitais tem 12 especialidades. Uma consulta custa {money(hospital.CONSULT_PRICE)}: '
            'enche a energia e dá um bônus que vale até a noite.</p>',
            table(["Especialidade", "Médica", "Sobre", "Bônus do dia"], rows),
            "<h2>Outras coisas</h2><ul><li><b>Farmácia</b>: remédios e vitaminas (veja as <a href=\"lojas.html#pharmacy\">lojas</a>).</li>"
            f"<li><b>Doação</b>: {money(hospital.DONATION)} por estação; a Ala Luthor ganha uma placa.</li>"
            "<li><b>Desmaio</b>: às 2h a Letícia desmaia e acorda num leito, com conta para pagar (de graça com a Meredith a 3 "
            "corações).</li><li><b>Brinquedoteca</b>: das 9h às 19h, uma vez por dia, contar história ou levar doce para as "
            "crianças. Ver <a href=\"atividades.html#pediatria\">Atividades</a>.</li></ul>",
            "<h2>Benefícios das médicas (3 corações)</h2><ul><li>Milany: consulta pela metade do preço.</li><li>Meredith: "
            "hospital grátis se desmaiar.</li><li>Cristina: contrato de $200 toda segunda.</li><li>Izzie e Addison: presentes."
            "</li></ul>",
            shot("hospital", "Conti Moretti Hospitais")]
    write("hospital.html", "Conti Moretti Hospitais", "\n".join(body), desc="Especialidades, consultas e bônus.")


def habilidades_page():
    rows = [[f'<b>{esc(s["name"])}</b>', esc(s["how"]), esc(s["perk"]), esc(s["top"])] for s in habilidades.SKILLS.values()]
    lv = table(["Nível"] + [str(i + 1) for i in range(len(habilidades.LEVELS))],
               [["Experiência"] + [str(x) for x in habilidades.LEVELS]])
    body = ['<p class="lead">Quatro habilidades sobem com o uso, do nível 0 ao 5. Cada nível dá um bônus pequeno e o nível 5 '
            'dá um extra. Veja tudo no app Habilidades do celular.</p>',
            table(["Habilidade", "Como subir", "Bônus por nível", "Nível 5"], rows), "<h2>Experiência por nível</h2>", lv]
    write("habilidades.html", "Habilidades", "\n".join(body), desc="Pesca, ciência, culinária e carisma.")


def conquistas_page():
    body = [f'<p class="lead">{len(conquistas.ACHIEVEMENTS)} medalhas em 4 categorias. A tecla <kbd>K</kbd> abre o painel.</p>']
    for ck, cname, col in conquistas.CATEGORIES:
        cards = "".join(f'<div class="medalha"><img src="img/medalhas/{a[0]}.png" alt="" loading="lazy"><div><b>{esc(a[2])}</b>'
                        f'<span>{esc(a[3])}</span></div></div>' for a in conquistas.ACHIEVEMENTS if a[1] == ck)
        body.append(f'<h2>{esc(cname)}</h2><div class="medalhas">{cards}</div>')
    write("conquistas.html", "Conquistas", "\n".join(body), desc="Todas as medalhas.")


def atividades_page():
    songs = ", ".join(f"<i>{esc(s['title'])}</i>" for s in activities.SONGS)
    movies = "".join(f"<li><i>{esc(m['title'])}</i> ({esc(m['genre'])})</li>" for m in activities.MOVIES)
    books = "".join(f"<li><i>{esc(b[0])}</i></li>" for b in clube.BOOKS)
    wines = ", ".join(esc(w[0]) for w in degustacao.WINES)
    sec = [
        ("pesca", "Pesca", '<p>No píer, no lago e no alto-mar. Ver <a href="peixes.html">Peixes</a>.</p>', "fishing"),
        ("cozinha", "Cozinhar", '<p>Fogão da cobertura. Ver <a href="receitas.html">Receitas</a>.</p>', None),
        ("horta", "Horta", '<p>Canteiros no terraço. Ver <a href="horta.html">Horta e coletáveis</a>.</p>', None),
        ("bichinho", "Bichinho", "<p>Adote um gato ou um cachorro e dê o nome que quiser. Ele dorme na caminha da sala, "
                                 "anda pela casa e deita no colo quando a Letícia senta no sofá. Petiscos deixam ele feliz.</p>", None),
        ("karaoke", "Karaokê", f"<p>No Noonan's, à noite. Aperte as setas no ritmo. Músicas: {songs}.</p>", "karaoke"),
        ("cinema", "Cinema", f"<p>Sessões no Cine National:</p><ul>{movies}</ul>", "movie"),
        ("jogos", "Fliperama, sinuca, dardos e xadrez", "<p>No Noonan's: fliperama Meteoro, sinuca (6 bolas em 8 tacadas) e "
                                                       "dardos (9 dardos). Xadrez com o Brainy, uma vez por dia, pela conversa: "
                                                       "ele joga mais sério conforme a Letícia ganha.</p>", "sinuca"),
        ("marina", "Marina", f'<p>Passeios de barco e regata com o Ian. Ver <a href="lojas.html#marina">Marina Luthor</a>.</p>',
         "regata"),
        ("clube", "Clube do livro", f"<p>Quintas, das 18h às 20h, na Bayside Books (Theo com 3 corações). Dá amizade, carisma "
                                   f"e, a cada 3 reuniões, um livro. Livros do clube:</p><ul>{books}</ul>", "clube"),
        ("corrida", "Corrida com a Sam", "<p>Terças, quintas e sábados, das 6h às 7h40, na orla (Sam com 2 corações): +40 de "
                                         "amizade, +20 de energia máxima no dia e +5 para sempre a cada 5 corridas (até +25).</p>",
         "corrida"),
        ("degustacao", "Degustação de vinhos", f"<p>Uma vez por semana com a Vittoria, na adega do Gruppo Ricci (2 corações). "
                                               f"Ela descreve três taças e a Letícia adivinha o vinho. Vinhos: {wines}.</p>", None),
        ("pediatria", "Brinquedoteca", f"<p>No saguão do Conti Moretti, das 9h às 19h, uma vez por dia: contar uma história "
                                       f"(−{pediatria.STORY_ENERGY} de energia) ou levar um doce/pelúcia. Dá amizade com as médicas "
                                       f"e carisma. Na {pediatria.DRAWING_AT}ª visita as crianças dão um desenho.</p>", None),
        ("pedidos", "Quadro de pedidos", f"<p>No Café Grão Nobre. Bilhetes novos chegam à noite; aceite um e entregue o item "
                                         f"conversando com quem pediu em até {pedidos.DEADLINE} dias. Paga dinheiro e amizade, "
                                         "sem castigo se não der. Começa com 1 espaço e vai a 3.</p>", None),
        ("celular", "Celular", "<p>Tecla <kbd>T</kbd>. Apps: Mensagens (as amigas mandam mensagens e você escolhe a resposta), "
                               "Agenda, Tempo, Bolsa, Fotos, Pedidos, Habilidades e Mapa.</p>", "celular"),
        ("andrea", "Andrea Rojas", "<p><a href=\"andrea.html\">Andrea Rojas</a> é amiga da Letícia e mora em Metrópolis. Manda mensagens e visita a cidade uma vez por "
                                   "estação (aviso na véspera): café, praia, Trattoria ou terraço. A visita rende $400 de "
                                   "bom astral, energia, carisma e um presente.</p>", "andrea"),
        ("catco", "CatCo TV e notícias", "<p>Entrevista ao vivo uma vez por semana no estúdio da CatCo, anúncio de $400 (produtos "
                                         "+15% por 3 noites) e o arquivo de matérias antigas. As manchetes da CatCo reagem ao "
                                         "que a Letícia faz: aparecem na banca, na TV e nas conversas.</p>", "arquivo"),
        ("album", "Álbum e modo foto", "<p>Com 2 corações, o Barry dá um álbum: cada cena especial vira uma foto. A tecla "
                                       "<kbd>P</kbd> abre o modo foto (Enter salva). As fotos vão para o mural da cobertura.</p>",
         "album"),
        ("decorar", "Decorar a cobertura", "<p>Pelo computador de casa: compre e arraste móveis pela sala.</p>", "decorar"),
        ("momentos", "Momentos", "<p>12 cenas curtas entre duas personagens, no máximo uma por dia, quando a Letícia passa "
                                 "perto do lugar no horário certo. Dão +20 de amizade com as duas.</p>", "momento"),
        ("encontros", "Encontros especiais", '<p>Piquenique, veleiro ao pôr do sol, cinema a dois e jantar a quatro mãos. Ver '
                                             '<a href="romance.html">Romance</a>.</p>', "piquenique"),
    ]
    body = ['<p class="lead">Tudo o que dá para fazer em National City além de trabalhar.</p>',
            '<p class="indice">' + " · ".join(f'<a href="#{k}">{t}</a>' for k, t, _, _ in sec) + "</p>"]
    for k, t, x, im in sec:
        body.append(f'<h2 id="{k}">{t}</h2><div class="lugar">{shot(im, t) if im else ""}<div>{x}</div></div>')
    write("atividades.html", "Atividades", "\n".join(body), desc="Pesca, karaokê, cinema, jogos e muito mais.")


# ============================ início ==================================================
def guia_page():
    body = ['<p class="lead">Primeiros passos para quem acabou de chegar a National City.</p>',
            "<h2>O dia</h2>",
            "<ul><li>O dia vai das 6h às 2h. Cada 7 segundos reais são 10 minutos no jogo. Conversas e menus pausam o relógio.</li>"
            "<li>Durma na cama da cobertura para salvar o jogo e começar o dia seguinte. Às 2h a Letícia desmaia e acorda "
            "no hospital, com conta para pagar.</li>"
            "<li>A barra de energia cai quando você trabalha. Comer, beber e dormir enchem de novo.</li></ul>",
            "<h2>Dinheiro</h2>",
            '<ul><li>O jeito principal é o <a href="laboratorio.html">laboratório</a>: proposta → bancada → produto → Mesa de '
            'Contratos.</li><li>Também dá para vender <a href="peixes.html">peixes</a>, <a href="receitas.html">pratos</a>, '
            '<a href="horta.html">colheitas e coletáveis</a> e investir em ações LCORP.</li></ul>',
            "<h2>Amizades</h2>",
            f'<ul><li>Converse com cada pessoa uma vez por período: manhã (6h–12h), tarde (12h–18h) e noite (18h–2h).</li>'
            f'<li>Dê <a href="presentes.html">presentes</a>: até 1 por dia e 2 por semana para cada pessoa.</li>'
            f'<li>{HP} pontos = 1 coração. Os eventos de coração liberam cenas e bônus.</li>'
            '<li>Amigas com 2 corações acenam quando você passa, mandam mensagens no celular e abrem a porta de casa.</li></ul>',
            "<h2>Dicas do jogo</h2>",
            "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in data.TIPS) + "</ul>"]
    write("guia.html", "Primeiros passos", "\n".join(body), desc="Guia para começar a jogar.")


def controles_page():
    keys = [("W A S D / setas", "Andar (com Shift, devagar)"), ("E / Espaço", "Interagir, conversar, trabalhar, pescar"),
            ("1 … 0, -, =", "Escolher item da barra (ou rodinha do mouse)"), ("F", "Comer, beber, ler ou vestir o item escolhido"),
            ("I / Tab", "Mochila (24 espaços)"), ("O", "Objetivos"), ("R", "Relacionamentos"), ("M", "Mapa da cidade"),
            ("C", "Calendário"), ("T", "Celular"), ("K", "Conquistas"), ("P", "Modo foto (Enter salva; 1 acena, 2 sorri, 3 coração)"),
            ("Ctrl+rodinha / Ctrl+- / Ctrl+=", "Zoom: afastar ou aproximar a câmera (75% a 175%; 100% é o padrão)"),
            ("Esc", "Pausa: aba Menu (objetivos, relacionamentos, coleções, cenas) e aba Configurações (tela cheia, zoom, som, controles)"), ("F11", "Tela cheia"),
            ("Setas / D F J K", "Karaokê")]
    rows = [[" ".join(f"<kbd>{esc(x)}</kbd>" for x in k.split(" ") if x not in ("/",)), esc(v)] for k, v in keys]
    body = [table(["Tecla", "O que faz"], rows),
            '<p>Jogar: no Windows, baixe o <a href="https://github.com/LuthorW/Luthor-Life/releases/latest/download/'
            'LuthorLife.exe">LuthorLife.exe</a> e dê dois cliques (não precisa instalar nada). No Linux e no macOS, '
            'com Python: <code>python main.py</code> (precisa só do <code>pygame-ce</code>).</p>']
    write("controles.html", "Controles", "\n".join(body), desc="Teclas do jogo.")


def index_page():
    portals = [("personagens.html", "Personagens", "cabecas/lucy.png"), ("presentes.html", "Presentes", "itens/rosas.png"),
               ("calendario.html", "Calendário", "itens/coroa_flores.png"), ("festas.html", "Festas", "itens/agua_coco.png"),
               ("peixes.html", "Peixes", "itens/robalo.png"), ("receitas.html", "Receitas", "itens/lasanha_nonna.png"),
               ("horta.html", "Horta", "itens/tomate.png"), ("itens.html", "Itens", "itens/chocolate_belga.png"),
               ("lojas.html", "Lojas", "itens/cappuccino.png"), ("laboratorio.html", "Laboratório", "itens/athena.png"),
               ("lugares.html", "Lugares", "cabecas/leticia.png"), ("romance.html", "Romance", "itens/pingente.png"),
               ("atividades.html", "Atividades", "itens/vara_fibra.png"), ("hospital.html", "Hospital", "cabecas/milany.png"),
               ("habilidades.html", "Habilidades", "itens/livro.png"), ("conquistas.html", "Conquistas", "itens/trevo4.png")]
    cards = "".join(f'<a class="portal" href="{u}"><img src="img/{i}" alt="" width="40" height="40">{esc(t)}</a>'
                    for u, t, i in portals if os.path.exists(os.path.join(IMG, i)))
    heads = "".join(f'<a href="{k}.html" title="{esc(NPCS[k]["name"])}"><img src="img/cabecas/{k}.png" alt="{esc(short(k))}" '
                    f'width="48" height="48"></a>' for k in ORDER)
    tips = json.dumps(list(data.TIPS), ensure_ascii=False)
    body = [f'<div class="banner"><img src="../img/title.png" alt="Luthor Life"><div><p>Bem-vinda à <b>wiki do Luthor Life</b>, '
            'o jogo de simulação de vida em pixel art em que você é Letícia Luthor, CEO da Luthor Corp, em National City.</p>'
            f'<p>Aqui estão todas as personagens, presentes, peixes, receitas, festas e segredos do jogo: '
            f'<b>{len(ORDER)}</b> personagens, <b>{len(ITEMS)}</b> itens, <b>{len(ALL_FISH)}</b> peixes e '
            f'<b>{len(conquistas.ACHIEVEMENTS)}</b> conquistas.</p></div></div>',
            f'<div class="portais">{cards}</div>',
            '<div class="duas"><section class="caixa"><h2>Novo por aqui?</h2><p>Comece pelos <a href="guia.html">primeiros '
            'passos</a> e pelos <a href="controles.html">controles</a>. Depois, veja o que cada pessoa ama na página de '
            '<a href="presentes.html">presentes</a>.</p></section>'
            f'<section class="caixa"><h2>Você sabia?</h2><p id="dica"></p></section></div>',
            f'<section class="caixa"><h2>Gente de National City</h2><div class="cabecas">{heads}</div></section>',
            f'<script>(function(){{var d={tips};var e=document.getElementById("dica");'
            f'if(e)e.textContent=d[Math.floor(Math.random()*d.length)];}})();</script>']
    write("index.html", "Wiki do Luthor Life", "\n".join(body), desc="Wiki do jogo Luthor Life.")


# ============================ busca ==================================================
def write_index():
    with open(os.path.join(OUT, "busca.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("window.WIKI_INDEX=" + json.dumps(INDEX, ensure_ascii=False, separators=(",", ":")) + ";\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):                  # páginas antigas saem (itens que deixaram de existir)
        if f.endswith(".html"):
            os.remove(os.path.join(OUT, f))
    make_images()
    random.seed(1)
    index_page()
    guia_page()
    controles_page()
    personagens_page()
    leticia_page()
    andrea_page()
    for k in ORDER:
        char_page(k)
    presentes_page()
    romance_page()
    calendario_page()
    festas_page()
    estacoes_page()
    itens_page()
    for k in ITEMS:
        item_page(k)
    peixes_page()
    receitas_page()
    horta_page()
    lojas_page()
    lugares_page()
    laboratorio_page()
    fundacao_page()
    historia_page()
    hospital_page()
    habilidades_page()
    conquistas_page()
    atividades_page()
    write_index()
    print(f"wiki: {len(INDEX)} páginas em {OUT}")


if __name__ == "__main__":
    try:
        main()
    finally:
        for f, b in _BACKUP.items():
            open(f, "wb").write(b)

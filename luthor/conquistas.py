"""Conquistas: metas com medalha (tecla K ou menu de pausa).

Cada conquista olha o que o jogo já guarda (estatísticas, coleções, amizades, flags...). `check` roda a cada 10 minutos
do relógio e no fim do dia; a conquista nova aparece num aviso no alto da tela (`draw_banner`), com som. Num save antigo,
as que já estavam cumpridas entram sem aviso (`sync`, chamado no load). Estado em `g.conquistas` (got, when), por save.
"""
import math

import pygame

from . import art, ui, audio
from .art import new, R, P
from .config import SCREEN_W, SCREEN_H, MAX_STATIONS, DAYS_PER_QUARTER, HEART_POINTS, C_TEXT, C_MUTED, C_GOLD, \
    C_GREEN, C_LILAC
from .data import ITEMS, FISH, RECIPES, BOOKS, FORAGE

CATEGORIES = [("corp", "Luthor Corp", (150, 70, 230)), ("amigos", "Amizades e amor", (226, 92, 150)),
              ("lazer", "Lazer", (52, 168, 160)), ("cidade", "National City", (214, 160, 52))]
CAT_COLOR = {k: c for k, _, c in CATEGORIES}


def _hearts(g):
    return [g.friendship[k] // HEART_POINTS for k in g.friendship]


def _people(g):
    from .characters import NPC_ORDER
    return [k for k in NPC_ORDER if k in g.friendship]


def _stat(g, k):
    return int(g.stats.get(k, 0) or 0)


def _romance(g):
    return 1 if (g.dating or g.partner or "casadas" in g.flags) else 0


def _festas(g):
    return len({t.split(":")[0] for t in g.festa.get("done", [])})


def _story(g):
    from . import historia
    return g.historia.get("ch", 0), len(historia.CHAPTERS)


def _foundation(g):
    from . import fundacao
    return len(g.fundacao.get("built", [])), len(fundacao.PROJECTS)


def _looks(g):
    from . import closet
    return len(set(g.closet.get("owned", [])) & set(closet.LOOKS)), len(closet.LOOKS)


def _days(g):
    return g.abs_day() - 1, 4 * DAYS_PER_QUARTER


# (chave, categoria, nome, descrição, ícone, progresso(g) -> (atual, meta))
ACHIEVEMENTS = [
    ("lancamento", "corp", "Primeiro lançamento", "Lance um produto no laboratório.", "prop_relatorio",
     lambda g: (_stat(g, "launched"), 1)),
    ("linha", "corp", "Linha de produção", "Lance 25 produtos.", "prop_software", lambda g: (_stat(g, "launched"), 25)),
    ("gigante", "corp", "Gigante da tecnologia", "Lance 100 produtos.", "prop_athena",
     lambda g: (_stat(g, "launched"), 100)),
    ("laboratorio", "corp", "Laboratório completo", f"Libere as {MAX_STATIONS} bancadas do laboratório.", "software",
     lambda g: (sum(1 for s in g.stations if s["unlocked"]), MAX_STATIONS)),
    ("cofre", "corp", "Cofre cheio", "Tenha $ 10.000 de uma vez.", "*moeda", lambda g: (g.money, 10000)),
    ("fortuna", "corp", "Fortuna Luthor", "Fature $ 100.000 no total.", "*moedas", lambda g: (_stat(g, "earned"), 100000)),
    ("wall_street", "corp", "Wall Street", "Faça a ação LCORP chegar a $ 200.", "*acao", lambda g: (int(g.stock), 200)),
    ("historia", "corp", "A Luthor Corp é minha", "Termine a história da Luthor Corp (os tios e o conselho).",
     "relatorio", _story),
    ("fundacao", "corp", "Coração de National City", "Termine todas as obras da Fundação Luthor.", "flores",
     _foundation),

    ("amizade", "amigos", "Primeira amizade", "Chegue a 4 corações com alguém.", "*coracao",
     lambda g: (max(_hearts(g) or [0]), 4)),
    ("popular", "amigos", "Popular", "Tenha 5 corações com 10 pessoas.", "*coracoes",
     lambda g: (sum(1 for h in _hearts(g) if h >= 5), 10)),
    ("melhores", "amigos", "Melhores amigas", "Chegue a 10 corações com alguém.", "*coracao",
     lambda g: (max(_hearts(g) or [0]), 10)),
    ("todo_mundo", "amigos", "Todo mundo te ama", "Tenha 6 corações com todas as pessoas da cidade.", "*coracoes",
     lambda g: (sum(1 for k in _people(g) if g.friendship[k] // HEART_POINTS >= 6), len(_people(g)))),
    ("generosa", "amigos", "Mão aberta", "Dê 50 presentes.", "girassois", lambda g: (_stat(g, "gifts"), 50)),
    ("namoro", "amigos", "Namorando!", "Comece a namorar alguém.", "rosas", lambda g: (_romance(g), 1)),
    ("morar", "amigos", "Lar doce lar", "Vá morar junto com a namorada.", "pingente",
     lambda g: (1 if (g.partner or "casadas" in g.flags) else 0, 1)),
    ("casamento", "amigos", "Felizes para sempre", "Case-se no Jardim do Mirante.", "anel",
     lambda g: (1 if "casadas" in g.flags else 0, 1)),
    ("momentos", "amigos", "De olho em tudo", "Veja 6 momentos entre os moradores.", "jornal",
     lambda g: (len(g.momentos.get("seen", [])), 6)),
    ("album", "amigos", "Álbum de memórias", "Tenha 15 fotos no álbum do Barry.", "porta_retrato",
     lambda g: (len(g.album.get("keys", [])), 15)),

    ("peixe", "lazer", "Primeiro peixe", "Pesque um peixe.", "sardinha", lambda g: (len(g.fish_caught), 1)),
    ("aquario", "lazer", "Aquário completo", "Ponha todas as espécies de peixe no aquário.", "koi",
     lambda g: (len(g.aquarium), len(FISH))),
    ("regata", "lazer", "Lobo do mar", "Vença a regata da Marina Luthor.", "*veleiro",
     lambda g: (int(g.marina.get("wins", 0)), 1)),
    ("chef", "lazer", "Chef de cozinha", "Cozinhe todas as receitas.", "lasanha", lambda g: (len(g.cooked), len(RECIPES))),
    ("horta", "lazer", "Dedo verde", "Colha 50 vezes na horta do terraço.", "tomate", lambda g: (_stat(g, "harvest"), 50)),
    ("exploradora", "lazer", "Exploradora", "Encontre todos os coletáveis.", "concha",
     lambda g: (len(g.forage_found), len(FORAGE))),
    ("leitora", "lazer", "Rato de biblioteca", "Leia todos os livros.", "livro",
     lambda g: (sum(1 for b in BOOKS.values() if b["flag"] in g.flags), len(BOOKS))),
    ("karaoke", "lazer", "Estrela do karaokê", "Tire nota S no karaokê do Noonan's.", "*estrela",
     lambda g: (_stat(g, "karaoke_s"), 1)),
    ("cinema", "lazer", "Cinéfila", "Assista a 10 filmes no cinema.", "pipoca", lambda g: (_stat(g, "movies"), 10)),
    ("meteoro", "lazer", "Piloto de elite", "Faça 80 pontos no Meteoro, o fliperama.", "*meteoro",
     lambda g: (_stat(g, "arcade_best"), 80)),
    ("xadrez", "lazer", "Xeque-mate", "Vença o Brainy no xadrez.", "*rei",
     lambda g: (int(g.jogos.get("chess_wins", 0)), 1)),
    ("bichinho", "lazer", "Família de quatro patas", "Adote um bichinho.", "petisco_pet",
     lambda g: (1 if g.pet else 0, 1)),
    ("gatinho", "lazer", "Amiga dos gatos", "Faça carinho no gatinho de rua 10 vezes.", "*pata",
     lambda g: (_stat(g, "gatinho"), 10)),

    ("festeira", "cidade", "Festeira", "Vá às quatro festas das estações.", "coroa_flores", lambda g: (_festas(g), 4)),
    ("check_up", "cidade", "Check-up completo", "Faça consulta nas 12 especialidades do Conti Moretti.", "kit_cuidado",
     lambda g: (len(g.checkups), 12)),
    ("fashion", "cidade", "Fashionista", "Tenha todos os looks do closet.", "*cabide", _looks),
    ("um_ano", "cidade", "Um ano em National City", "Jogue um ano inteiro (as quatro estações).", "*calendario",
     _days),
    ("manchete", "cidade", "Capa da CatCo", "Apareça em 10 manchetes da CatCo.", "jornal",
     lambda g: (getattr(g, "noticias", {}).get("total", 0), 10)),
    ("pediatria", "cidade", "Amiga da pediatria", "Seja voluntária na brinquedoteca do Conti Moretti 5 vezes.",
     "pelucia", lambda g: (getattr(g, "pediatria", {}).get("visits", 0), 5)),
    ("sommelier", "lazer", "Paladar de sommelier", "Acerte os três vinhos numa degustação com a Vittoria.", "vinho",
     lambda g: (getattr(g, "degust", {}).get("best", 0), 3)),
]
BY_KEY = {a[0]: a for a in ACHIEVEMENTS}


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.conquistas = dict(got=[], when={})
    g.medal_queue = []           # avisos esperando a vez: [chave, tempo]


def save_state(g):
    return {"conquistas": g.conquistas}


def load_state(g, d):
    init_state(g)
    c = d.get("conquistas") or {}
    g.conquistas["got"] = [k for k in c.get("got", []) if k in BY_KEY]
    g.conquistas["when"] = {k: v for k, v in (c.get("when") or {}).items() if k in BY_KEY}


def progress(g, key):
    try:
        cur, goal = BY_KEY[key][5](g)
    except Exception:                    # algum sistema ainda sem estado (save muito antigo)
        return 0, 1
    return max(0, int(cur)), max(1, int(goal))


def check(g, quiet=False):
    """Libera as conquistas cumpridas. Devolve quantas entraram agora."""
    got = g.conquistas["got"]
    new_ = 0
    for a in ACHIEVEMENTS:
        k = a[0]
        if k in got:
            continue
        cur, goal = progress(g, k)
        if cur >= goal:
            got.append(k)
            g.conquistas["when"][k] = g.abs_day()
            new_ += 1
            if not quiet:
                g.medal_queue.append([k, 0.0])
    return new_


def sync(g):
    """Depois de carregar: as que já estavam cumpridas entram sem um aviso para cada uma."""
    n = check(g, quiet=True)
    if n:
        g.toasts.push(f"Você já tem {len(g.conquistas['got'])} conquista(s)! Veja na tecla K.", C_GOLD)


# ---------------------------------------------------------------------------
# Ícones
# ---------------------------------------------------------------------------
GOLD, GOLD_D, GOLD_L = (240, 196, 72), (176, 126, 38), (255, 236, 150)
PINK, PINK_D = (240, 80, 130), (170, 40, 90)


def _special(kind):
    s = new(16, 16)
    if kind in ("moeda", "moedas"):
        coins = [(8, 9)] if kind == "moeda" else [(5, 10), (11, 10), (8, 6)]
        for cx, cy in coins:
            pygame.draw.circle(s, GOLD_D, (cx, cy), 5)
            pygame.draw.circle(s, GOLD, (cx, cy), 4)
            P(s, GOLD_L, cx - 2, cy - 2); P(s, GOLD_L, cx - 1, cy - 3)
            R(s, GOLD_D, cx, cy - 2, 1, 5)
    elif kind == "acao":
        R(s, (40, 30, 60), 1, 2, 14, 12)
        pts = [(2, 11), (5, 9), (7, 10), (10, 6), (13, 3)]
        pygame.draw.lines(s, (110, 231, 140), False, pts, 2)
        R(s, (110, 231, 140), 11, 3, 3, 1); R(s, (110, 231, 140), 13, 3, 1, 3)
    elif kind in ("coracao", "coracoes"):
        h = art.heart(True, 2)
        if kind == "coracao":
            s.blit(h, (1, 2))
        else:
            s.blit(art.heart(True, 1), (1, 1)); s.blit(art.heart(True, 1), (9, 1)); s.blit(art.heart(True, 1), (5, 8))
    elif kind == "veleiro":
        R(s, (90, 60, 40), 7, 2, 1, 10)
        pygame.draw.polygon(s, (250, 250, 245), [(8, 2), (8, 10), (14, 10)])
        pygame.draw.polygon(s, (138, 80, 230), [(6, 4), (6, 10), (2, 10)])
        pygame.draw.polygon(s, (120, 70, 50), [(1, 11), (15, 11), (13, 14), (3, 14)])
        R(s, (80, 160, 230), 0, 15, 16, 1)
    elif kind == "estrela":
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = 7 if i % 2 == 0 else 3
            pts.append((8 + r * math.cos(ang), 8.5 + r * math.sin(ang)))
        pygame.draw.polygon(s, GOLD_D, pts)
        pygame.draw.polygon(s, GOLD, [(8 + (x - 8) * 0.75, 8.5 + (y - 8.5) * 0.75) for x, y in pts])
        P(s, GOLD_L, 7, 6)
    elif kind == "meteoro":
        for i in range(5):
            R(s, (255, 170 - i * 20, 60), 1 + i, 1 + i, 3, 1)
        pygame.draw.circle(s, (120, 100, 90), (10, 10), 4)
        pygame.draw.circle(s, (160, 140, 120), (9, 9), 2)
        P(s, (90, 70, 60), 12, 11)
    elif kind == "rei":
        R(s, (230, 226, 216), 7, 1, 2, 4); R(s, (230, 226, 216), 6, 2, 4, 1)
        R(s, (230, 226, 216), 5, 5, 6, 2)
        R(s, (210, 204, 190), 6, 7, 4, 5)
        R(s, (230, 226, 216), 4, 12, 8, 2)
        R(s, (150, 140, 130), 4, 14, 8, 1)
    elif kind == "pata":
        c = (250, 200, 160)
        pygame.draw.circle(s, c, (8, 11), 4)
        for x, y in ((3, 6), (6, 3), (10, 3), (13, 6)):
            pygame.draw.circle(s, c, (x, y), 2)
    elif kind == "cabide":
        pygame.draw.lines(s, (200, 200, 210), False, [(8, 1), (9, 2), (8, 4)], 1)
        pygame.draw.polygon(s, (200, 200, 210), [(8, 4), (1, 9), (15, 9)], 1)
        pygame.draw.polygon(s, (226, 92, 150), [(4, 9), (12, 9), (14, 15), (2, 15)])
        R(s, (250, 140, 190), 5, 10, 2, 4)
    elif kind == "calendario":
        R(s, (250, 246, 238), 2, 3, 12, 12)
        R(s, (226, 70, 90), 2, 3, 12, 3)
        R(s, (120, 110, 130), 4, 1, 1, 3); R(s, (120, 110, 130), 11, 1, 1, 3)
        for i in range(9):
            R(s, (150, 140, 170), 4 + (i % 3) * 3, 8 + (i // 3) * 2, 2, 1)
    return s


def icon(key, k=3, locked=False):
    a = BY_KEY[key]

    def make():
        name = a[4]
        if name.startswith("*"):
            img = art.up(_special(name[1:]), k)
        elif name in ITEMS:
            img = art.item_icon(name, k)
        else:
            img = art.up(_special("estrela"), k)
        if locked:
            img = pygame.transform.grayscale(img)
            img.set_alpha(120)
        return img
    return art.cached(("conquista", key, k, locked), make)


def badge(surf, rect, key, got, t=0.0):
    """Quadradinho da medalha: cor da categoria e borda dourada quando ganha; escuro quando falta."""
    col = CAT_COLOR[BY_KEY[key][1]]
    if got:
        ui.cut_rect(surf, (24, 14, 34), rect.move(0, 3), 2)
        ui.box(surf, rect, art.mix(col, (30, 18, 40), 0.35), border=GOLD, cut=2)
    else:
        ui.box(surf, rect, (30, 20, 42), border=(70, 56, 90), cut=2)
    ic = icon(key, 2 if rect.w < 60 else 3, locked=not got)
    surf.blit(ic, ic.get_rect(center=rect.center))
    if got:                                      # brilho suave que passa na medalha de vez em quando
        k = (t * 0.5 + (sum(map(ord, key)) % 7) / 7) % 3.0
        if k < 1:
            inner = rect.inflate(-6, -6)
            gl = pygame.Surface(inner.size, pygame.SRCALPHA)
            x = int(k * (inner.w + 16)) - 8
            pygame.draw.polygon(gl, (255, 255, 240, 70), [(x, 0), (x + 7, 0), (x + 1, inner.h), (x - 6, inner.h)])
            surf.blit(gl, inner.topleft)


# ---------------------------------------------------------------------------
# Aviso de conquista nova
# ---------------------------------------------------------------------------
BANNER_T = 4.6


def update(g, dt):
    q = g.medal_queue
    if not q:
        return
    if q[0][1] == 0.0:
        audio.sfx("reward")
    q[0][1] += dt
    if q[0][1] >= BANNER_T:
        q.pop(0)


def draw_banner(g, surf):
    q = g.medal_queue
    if not q:
        return
    key, t = q[0]
    a = BY_KEY[key]
    w = max(440, 112 + max(ui.font(26, True).size(a[2])[0], ui.font(15).size(a[3])[0]) + 20)
    h = 92
    slide = min(1.0, t / 0.35, max(0.0, (BANNER_T - t) / 0.35))
    ease = 1 - (1 - slide) ** 3
    # canto de baixo, à esquerda, logo acima da barra de itens (os avisos comuns ficam no alto)
    r = pygame.Rect(int(-w - 10 + (w + 26) * ease), SCREEN_H - 112 - h, w, h)
    ui.panel(surf, r, alpha=245, border=GOLD)
    b = pygame.Rect(r.x + 16, r.y + 14, 64, 64)
    badge(surf, b, key, True, t)
    ui.text(surf, "Conquista desbloqueada!", (r.x + 96, r.y + 12), 16, C_GOLD, bold=True)
    ui.text(surf, a[2], (r.x + 96, r.y + 32), 26, C_TEXT, bold=True)
    ui.text(surf, a[3], (r.x + 96, r.y + 64), 15, C_LILAC)
    for i in range(6):                           # estrelinhas em volta
        ang = t * 2 + i * math.pi / 3
        sx = r.x + 48 + math.cos(ang) * 44
        sy = r.y + 46 + math.sin(ang) * 40
        if r.y + 4 < sy < r.bottom - 4:
            sz = 2 + int(abs(math.sin(t * 5 + i)) * 2)
            pygame.draw.rect(surf, GOLD_L, (int(sx) - sz // 2, int(sy) - sz // 2, sz, sz))


# ---------------------------------------------------------------------------
# Painel (tecla K)
# ---------------------------------------------------------------------------
def open_panel(g):
    check(g, quiet=False)
    audio.sfx("open")
    g.push(Painel(g))


class Painel(ui.Modal):
    W, H = 960, 640
    CARD_W, CARD_H, GAP = 432, 92, 12
    TOP, BOTTOM = 112, 46

    def __init__(self, g):
        self.g = g
        self.off = 0
        self.max_off = 0
        self.t = 0.0

    def handle(self, ev):
        step = 0
        if ev.type == pygame.MOUSEWHEEL:
            step = -ev.y * 60
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                step = -60
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                step = 60
            elif ev.key in (pygame.K_PAGEDOWN,):
                step = 300
            elif ev.key in (pygame.K_PAGEUP,):
                step = -300
            elif ev.key in ui.CONFIRM or ev.key in ui.CANCEL or ev.key == pygame.K_k:
                audio.sfx("cancel")
                self.done = True
                return
        if step:
            self.off = max(0, min(self.max_off, self.off + step))

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        g = self.g
        rect = pygame.Rect(0, 0, self.W, self.H)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect, alpha=250)
        got = set(g.conquistas["got"])
        n, tot = len(got), len(ACHIEVEMENTS)
        ui.text(surf, "Conquistas", (rect.x + 32, rect.y + 18), 32, C_GOLD, bold=True)
        ui.text(surf, f"{n} de {tot}", (rect.right - 32, rect.y + 24), 24, C_TEXT, bold=True, right=True)
        bar = pygame.Rect(rect.x + 34, rect.y + 70, rect.w - 68, 14)
        inner = bar.inflate(-2 * ui.U, -2 * ui.U)
        ui.slot(surf, bar, fill=(30, 20, 44))
        if n:
            fw = max(ui.U * 4, int(inner.w * n / tot))
            surf.fill(GOLD, (inner.x, inner.y, fw, inner.h))
            surf.fill(GOLD_L, (inner.x, inner.y, fw, ui.U))
            surf.fill(art.shade(GOLD, 0.7), (inner.x, inner.bottom - ui.U, fw, ui.U))
        view = pygame.Rect(rect.x + 20, rect.y + self.TOP, rect.w - 40, rect.h - self.TOP - self.BOTTOM)
        sheet = pygame.Surface((view.w, 3000), pygame.SRCALPHA)
        y = 0
        for cat, label, col in CATEGORIES:
            items = [a for a in ACHIEVEMENTS if a[1] == cat]
            have = sum(1 for a in items if a[0] in got)
            ui.box(sheet, pygame.Rect(6, y + 7, 10, 24), col, cut=1)
            ui.text(sheet, label, (22, y + 4), 24, C_TEXT, bold=True)
            ui.text(sheet, f"{have}/{len(items)}", (view.w - 14, y + 8), 18, C_MUTED, right=True)
            y += 40
            for i, a in enumerate(items):
                cx = 8 + (i % 2) * (self.CARD_W + self.GAP)
                cy = y + (i // 2) * (self.CARD_H + self.GAP)
                self._card(sheet, pygame.Rect(cx, cy, self.CARD_W, self.CARD_H), a, a[0] in got)
            y += ((len(items) + 1) // 2) * (self.CARD_H + self.GAP) + 14
        self.max_off = max(0, y - view.h)
        self.off = min(self.off, self.max_off)
        surf.blit(sheet, view.topleft, (0, self.off, view.w, view.h))
        if self.max_off:
            sb = pygame.Rect(rect.right - 14, view.y, 4, view.h)
            surf.fill((40, 30, 58), sb)
            kh = max(24, int(view.h * view.h / (view.h + self.max_off)))
            ky = sb.y + int((view.h - kh) * self.off / self.max_off)
            surf.fill((184, 76, 255), (sb.x, ky, 4, kh))
            surf.fill((223, 197, 255), (sb.x, ky, 4, ui.U))
        ui.text(surf, "Setas / roda: rolar     Esc / K: fechar", (rect.centerx, rect.bottom - 34), 16, C_MUTED,
                center=True)

    def _card(self, surf, r, a, got):
        g = self.g
        key, cat, name, desc = a[0], a[1], a[2], a[3]
        ui.box(surf, r, (58, 36, 82) if got else (38, 26, 54),
               border=art.mix(CAT_COLOR[cat], (40, 26, 56), 0.4) if got else (64, 50, 84), cut=2)
        b = pygame.Rect(r.x + 12, r.y + 13, 66, 66)
        badge(surf, b, key, got, self.t)
        tx = r.x + 92
        ui.text(surf, name, (tx, r.y + 8), 21, C_TEXT if got else (200, 190, 214), bold=True)
        lines = ui.wrap(desc, 15, r.right - tx - 12)
        for j, ln in enumerate(lines[:2]):
            ui.text(surf, ln, (tx, r.y + 34 + j * 19), 15, C_LILAC if got else C_MUTED)
        if got:
            when = g.conquistas["when"].get(key)
            if when:
                yr, q, d = g.date_from_abs(when)
                ui.text(surf, f"Ganha em {g.date_label(d, q, yr)}", (r.right - 12, r.bottom - 24), 14, C_GREEN,
                        right=True)
        else:
            cur, goal = progress(g, key)
            if goal > 1:
                bw = r.right - tx - 70
                bb = pygame.Rect(tx, r.bottom - 18, bw, 8)
                ui.slot(surf, bb.inflate(4, 4), fill=(24, 16, 34))
                fill = int(bw * min(1.0, cur / goal))
                if fill > 0:
                    surf.fill(CAT_COLOR[cat], (bb.x, bb.y, max(4, fill), bb.h))
                    surf.fill(art.mix(CAT_COLOR[cat], (255, 255, 255), 0.4), (bb.x, bb.y, max(4, fill), 2))
                shown = f"{min(cur, goal):,}/{goal:,}".replace(",", ".")
                ui.text(surf, shown, (r.right - 12, r.bottom - 26), 15, C_TEXT, right=True)

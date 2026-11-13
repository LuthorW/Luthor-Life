"""Closet da Letícia: trocar de roupa no guarda-roupa da cobertura (ou no provador da La Boutique).

Alguns looks ela já tem, os outros se compram na La Boutique (boutique.py) e quatro chegam de presente (Lucy,
Vittoria, Ian e Celeste a 6 corações). As personagens comentam cada look novo uma vez.
O look escolhido vale para o bonequinho no jogo e nas cenas; "Roupa da estação" é o jeito antigo (troca sozinha).
Aba Acessórios: os acessórios guardados no closet (`acc`) e os da mochila; um por espaço (`worn`: espaço -> item).
"""
import random

import pygame

from . import art, ui, audio, characters
from .characters import NPCS
from .entities import PLAYER_LOOK
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_ACCENT, C_PINK

# chave: (nome, preço ou None, mudanças no look, descrição)
LOOKS = {
    "estacao": ("Roupa da estação", None, None,
                "Troca sozinha: blazer na primavera, blusa no verão, sobretudo no outono e casaco no inverno."),
    "ceo": ("Terninho de CEO", None, dict(outfit="blazer"),
            "O blazer de sempre. Ninguém discute orçamento com ele."),
    "lab": ("Jaleco do laboratório", None, dict(outfit="labcoat", cloth=(240, 240, 246), accent=(70, 60, 96)),
            "Bolso com três canetas e uma mancha de café que não sai."),
    "fds": ("Fim de semana", 250, dict(outfit="cardigan", cloth=(168, 138, 206), accent=(246, 242, 234),
                                       pants=(62, 84, 130)),
            "Cardigã lilás e jeans. Para fingir que CEO tem folga."),
    "listrada": ("Blusa listrada", 220, dict(outfit="breton", cloth=(40, 52, 96), accent=(246, 244, 238),
                                             pants=(232, 226, 210)),
                 "Listras de marinheira e calça clara. Combina com a marina."),
    "praia": ("Dia de praia", 180, dict(outfit="blouse", cloth=(120, 200, 210), accent=(250, 248, 240),
                                        pants=(232, 214, 176), sleeves="short"),
              "Blusa leve de manga curta, cor de água."),
    "executiva": ("Saia e blazer", 520, dict(outfit="skirt_suit", cloth=(70, 40, 100), accent=(240, 232, 246),
                                            pants=(52, 30, 72)),
                  "O conjunto das reuniões de conselho. Roxo Luthor, claro."),
    "sobretudo": ("Sobretudo cinza", 640, dict(outfit="trench", cloth=(118, 118, 128), accent=(36, 30, 40)),
                  "Comprido, com cinto. Ótimo para dias de vento no calçadão."),
    "inverno": ("Casaco de lã branco", 700, dict(outfit="peacoat", cloth=(236, 232, 224), accent=(70, 40, 100),
                                                 scarf=(138, 60, 200)),
                "Casaco trespassado com cachecol roxo."),
    "tech": ("Jaqueta tech", 900, dict(outfit="tech", cloth=(32, 30, 40), accent=(60, 56, 72)),
             "Linhas de circuito que brilham. O Brainy vai pedir emprestada."),
    "couro": ("Jaqueta de couro", None, dict(outfit="leather", cloth=(44, 36, 42), accent=(232, 228, 236)),
              "Presente da Lucy: igualzinha à dela."),
    "gala": ("Vestido de gala", 1500, dict(outfit="gown", cloth=(110, 24, 150), accent=(232, 210, 120)),
             "Vestido longo roxo com colar dourado. Para as noites em que a Luthor Corp precisa brilhar."),
    "capita": ("Casaco de capitã", None, dict(outfit="captain", cloth=(30, 42, 82), accent=(240, 236, 226)),
               "Presente do Ian, com dragonas douradas. A Marina Luthor aprova."),
}
ORDER = list(LOOKS)
START = {"estacao", "ceo", "lab"}
# presentes de roupa: personagem, corações, look, recado
GIFTS = [
    ("lucy", 6, "couro", "A Lucy deixou um pacote na portaria: uma jaqueta de couro igual à dela, com um bilhete: "
                         "\"Pra você parar de roubar a minha.\""),
    ("vittoria", 6, "gala", "Chegou uma caixa do Gruppo Ricci: um vestido de gala roxo. O cartão diz: "
                            "\"Para a próxima inauguração. Você vai ser a mais elegante. Depois de mim. V.\""),
    ("ian", 6, "capita", "O Ian mandou um casaco de capitã da Marina Luthor: \"Toda dona de iate precisa de um. "
                         "Até as que enjoam no mar.\""),
]

STATE = {"cur": "estacao", "acc": {}}


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.closet = dict(cur="estacao", owned=sorted(START), seen=[], acc=[], worn={})
    STATE["cur"] = "estacao"
    _refresh(g)


def _refresh(g):
    STATE["acc"] = worn_look(g)
    if getattr(g, "player", None) is not None:
        g.player.set_look(player_look())


def save_state(g):
    return {"closet": g.closet}


def load_state(g, d):
    from .boutique import ACCESSORIES
    c = d.get("closet") or {}
    owned = [k for k in c.get("owned", []) if k in LOOKS]
    acc = [k for k in c.get("acc", []) if k in ACCESSORIES]
    worn = {s: k for s, k in (c.get("worn") or {}).items() if k in acc and ACCESSORIES[k]["slot"] == s}
    g.closet = dict(cur=c.get("cur", "estacao") if c.get("cur") in LOOKS else "estacao",
                    owned=sorted(set(owned) | START), seen=list(c.get("seen", [])), acc=acc, worn=worn)
    STATE["cur"] = g.closet["cur"]
    _refresh(g)


def worn_look(g, worn=None):
    """Mudanças no look de todos os acessórios em uso (ou dos de `worn`, para experimentar na loja)."""
    from .boutique import ACCESSORIES
    worn = g.closet.get("worn", {}) if worn is None else worn
    out = {}
    for key in worn.values():
        if key in ACCESSORIES:
            out.update(ACCESSORIES[key]["look"])
    return out


def player_look(key=None, acc=None):
    """Look atual da Letícia (o jogo e as cenas usam este), com os acessórios por cima."""
    key = key or STATE["cur"]
    acc = STATE["acc"] if acc is None else acc
    ov = LOOKS.get(key, LOOKS["estacao"])[2]
    base = characters.dress("leticia", PLAYER_LOOK) if not ov else {**PLAYER_LOOK, **ov}
    return {**base, **acc} if acc else base


def wear(g, key):
    g.closet["cur"] = key
    STATE["cur"] = key
    _refresh(g)


def wear_acc(g, item):
    """Veste o acessório (tira o que estava no mesmo espaço). Se vier da mochila, ele passa a morar no closet."""
    from .boutique import ACCESSORIES
    a = ACCESSORIES[item]
    if item not in g.closet["acc"]:
        if not g.count_item(item):
            return False
        g.remove_item(item)
        g.closet["acc"].append(item)
    g.closet["worn"][a["slot"]] = item
    _refresh(g)
    return True


def take_off(g, slot=None):
    if slot is None:
        g.closet["worn"].clear()
    else:
        g.closet["worn"].pop(slot, None)
    _refresh(g)


def use_item(g, item):
    """F com um acessório da mochila: veste na hora (ele vai para o closet; para dar de presente, compre outro)."""
    from .boutique import ACCESSORIES
    if not wear_acc(g, item):
        return
    audio.sfx("confirm")
    g.toasts.push(f"Usando {ACCESSORIES[item]['name']}. Ele fica guardado no closet da cobertura.", C_GREEN, item)


# ---------------------------------------------------------------------------
# Presentes de roupa (na virada do dia)
# ---------------------------------------------------------------------------
def night(g, notes):
    for who, h, key, msg in GIFTS:
        if key not in g.closet["owned"] and g.hearts(who) >= h:
            g.closet["owned"].append(key)
            notes.append((msg + " (Está no closet.)", C_PINK))


# ---------------------------------------------------------------------------
# Comentários das personagens (um por look, na primeira conversa com ele)
# ---------------------------------------------------------------------------
GENERIC = {
    "ceo": ["Terninho impecável, como sempre.", "Clássica. Nunca erra com esse blazer."],
    "lab": ["De jaleco na rua? Saiu correndo do laboratório, né?", "Gostei do jaleco. Tem até caneta no bolso!"],
    "fds": ["Cardigã! Hoje é dia de folga de verdade?", "Que look tranquilo. Combina com você."],
    "listrada": ["Listras de marinheira! Vai velejar hoje?", "Essa blusa listrada ficou ótima."],
    "praia": ["Roupa de praia! Me leva junto?", "Que cor bonita. Parece o mar de manhã."],
    "executiva": ["Saia e blazer... reunião importante hoje?", "Esse roxo é muito Luthor Corp."],
    "sobretudo": ["Sobretudo cinza! Parece detetive de filme.", "Elegante. E quentinho, imagino."],
    "inverno": ["Esse casaco branco é lindo. Não suja nunca?", "O cachecol roxo deu o toque final."],
    "tech": ["As linhas da jaqueta brilham? Que coisa!", "Jaqueta tech! Parece saída do laboratório do Brainy."],
    "couro": ["Jaqueta de couro? Isso é bem estilo Lucy.", "Que pegada rock and roll hoje!"],
    "gala": ["Uau. Tem festa e ninguém me chamou?", "Vestido de gala no meio do dia! Você é corajosa."],
    "capita": ["Casaco de capitã! O Ian deve ter adorado.", "Bom dia, capitã!"],
}
SPECIAL = {
    "lucy": {"couro": "Você está usando a jaqueta! Ficou melhor em você do que em mim. Não espalha.",
             "gala": "Tá. Eu precisei de uns três segundos pra lembrar o que ia falar.",
             "lab": "O jaleco te deixa com cara de cientista maluca. Num bom sentido.",
             "fds": "Cardigã e jeans... é a Letícia que eu conheci em Gotham."},
    "vittoria": {"gala": "Esse vestido... Pronto. Agora vou ter que inventar uma inauguração só para te ver com ele de novo.",
                 "executiva": "Saia e blazer roxos. Se eu fosse sua concorrente, ficaria preocupada.",
                 "praia": "Roupa de praia num dia de semana? Isso sim é ser dona da própria agenda.",
                 "couro": "Jaqueta de couro. Hmm. Tem dedo de alguém nisso, não tem?"},
    "jess": {"gala": "Você tem algum evento que NÃO está na agenda? Porque eu não estou sabendo.",
             "fds": "Look de folga em dia útil. Vou fingir que não vi e remarcar as onze horas."},
    "sam": {"tech": "A jaqueta tem circuito de verdade? Deixa eu ver. Ah, é LED. Ainda assim, bonita.",
            "lab": "Finalmente alguém usando o jaleco direito."},
    "brainy": {"tech": "VOCÊ COMPROU A JAQUETA TECH. Podemos ser gêmeos de laboratório?",
               "lab": "Jaleco! Agora sim parece uma CEO de ciência."},
    "ian": {"capita": "Olha só, a capitã! Agora você é obrigada a vir no próximo passeio.",
            "listrada": "Listras de marinheira. As férias no interior nunca saíram de você, né?"},
    "barry": {"gala": "PARADA! Só uma foto. Tá, três fotos.", "couro": "Esse visual dá capa de revista."},
    "graca": {"gala": "Ai, que coisa mais linda! Parece noiva de novela.", "praia": "Tá pronta pro luau, minha filha!"},
    "rafa": {"inverno": "Casaco branco e café? Corajosa. Vou caprichar pra não respingar."},
    "nia": {"praia": "Combinou com o céu de hoje! Posso desenhar você assim?"},
}


def chat_line(g, npc):
    key = g.closet["cur"]
    tag = f"{npc.key}:{key}"
    if key == "estacao" or tag in g.closet["seen"]:
        from . import boutique
        return boutique.chat_line(g, npc)          # acessórios novos também ganham comentário
    g.closet["seen"].append(tag)
    line = SPECIAL.get(npc.key, {}).get(key)
    return line or random.choice(GENERIC.get(key, ["Roupa nova? Ficou ótima."]))


# ---------------------------------------------------------------------------
# Ganchos e a tela do closet
# ---------------------------------------------------------------------------
def object_label(g, o):
    if o.kind == "wardrobe" and g.map_name == "home":
        return "Closet"
    if o.kind == "provador":
        return "Provador (trocar de roupa)"
    return None


def use_object(g, o):
    if (o.kind == "wardrobe" and g.map_name == "home") or o.kind == "provador":
        audio.sfx("door")
        g.push(Closet(g))
        return True
    return False


def gift_source(key):
    for who, h, k, _m in GIFTS:
        if k == key:
            return who, h
    return None


class Closet(ui.Modal):
    """Duas abas: Roupas (vestir o que tem) e Acessórios (um por espaço). Comprar é na La Boutique."""
    TABS = ("Roupas", "Acessórios")

    def __init__(self, g):
        self.g = g
        self.tab = 0
        self.sel = [ORDER.index(g.closet["cur"]) if g.closet["cur"] in ORDER else 0, 0]
        self.top = [0, 0]
        self.t = 0.0
        self.msg, self.msg_t = "", 0.0

    def acc_rows(self):
        """Primeira linha: tirar todos; depois os acessórios do closet e os da mochila."""
        from .boutique import ACC_ORDER
        g = self.g
        have = [k for k in ACC_ORDER if k in g.closet["acc"] or g.count_item(k)]
        return [None] + have

    def rows(self):
        return ORDER if self.tab == 0 else self.acc_rows()

    def handle(self, ev):
        n = len(self.rows())
        if ev.type == pygame.MOUSEWHEEL:
            self.sel[self.tab] = (self.sel[self.tab] - ev.y) % n
            audio.sfx("move")
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel[self.tab] = (self.sel[self.tab] - 1) % n; audio.sfx("move")
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel[self.tab] = (self.sel[self.tab] + 1) % n; audio.sfx("move")
        elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_TAB, pygame.K_q):
            self.tab = 1 - self.tab; audio.sfx("move")
        elif ev.key in ui.CONFIRM:
            self.choose()
        elif ev.key in ui.CANCEL:
            self.done = True

    def say(self, msg, t=2.4):
        self.msg, self.msg_t = msg, t

    def choose(self):
        g = self.g
        if self.tab == 1:
            self.choose_acc()
            return
        key = ORDER[self.sel[0]]
        name, price, _ov, _d = LOOKS[key]
        if key in g.closet["owned"]:
            wear(g, key)
            audio.sfx("confirm")
            self.say(f"Vestindo: {name}", 2.0)
            return
        audio.sfx("blip")
        if price is None:
            src = gift_source(key)
            who = NPCS[src[0]]["short"] if src else "alguém"
            self.say(f"Esse só chega de presente ({who}, {src[1] if src else 6} corações).")
        else:
            self.say(f"À venda na La Boutique, ao lado do Grão Nobre (${price}).")

    def choose_acc(self):
        from .boutique import ACCESSORIES, SLOTS
        g = self.g
        rows = self.acc_rows()
        key = rows[min(self.sel[1], len(rows) - 1)]
        if key is None:
            if not g.closet["worn"]:
                audio.sfx("blip")
                self.say("Nenhum acessório em uso." if len(rows) > 1 else
                         "Você ainda não tem acessórios. A La Boutique fica ao lado do Grão Nobre.", 3.0)
                return
            take_off(g)
            audio.sfx("confirm")
            self.say("Tirou todos os acessórios.")
            return
        a = ACCESSORIES[key]
        if g.closet["worn"].get(a["slot"]) == key:
            take_off(g, a["slot"])
            audio.sfx("confirm")
            self.say(f"Tirou: {a['name']}")
            return
        from_bag = key not in g.closet["acc"]
        wear_acc(g, key)
        audio.sfx("confirm")
        self.say(f"Usando: {a['name']} ({SLOTS[a['slot']]})" + (". Saiu da mochila e ficou no closet." if from_bag else ""),
                 3.0)

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)

    def draw(self, surf):
        from .boutique import ACCESSORIES, SLOTS
        g = self.g
        outer = pygame.Rect(0, 0, 860, 580)
        outer.center = (SCREEN_W // 2 - 50, SCREEN_H // 2 - 10)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "Closet da Letícia", (outer.x + 28, outer.y + 16), 28, C_GOLD, bold=True)
        ui.text(surf, f"Dinheiro: ${g.money}", (outer.right - 28, outer.y + 24), 18, C_TEXT, right=True)
        tx = outer.x + 24
        for i, name in enumerate(self.TABS):
            r = pygame.Rect(tx, outer.y + 62, 150, 34)
            if i == self.tab:
                ui.box(surf, r, ui.C_PANEL_2, border=ui.C_ACCENT_2)
            else:
                ui.slot(surf, r, fill=(24, 16, 34))
            ui.text(surf, name, (r.centerx, r.y + 6), 19, C_TEXT if i == self.tab else C_MUTED,
                    bold=i == self.tab, center=True)
            tx += 160
        rows = self.rows()
        sel = self.sel[self.tab] = min(self.sel[self.tab], len(rows) - 1)
        nrows = 9
        top = self.top[self.tab]
        if sel < top:
            top = sel
        elif sel >= top + nrows:
            top = sel - nrows + 1
        self.top[self.tab] = top
        y = outer.y + 108
        for i in range(top, min(len(rows), top + nrows)):
            key = rows[i]
            r = pygame.Rect(outer.x + 20, y, 440, 42)
            if i == sel:
                ui.box(surf, r, ui.C_PANEL_2, border=ui.C_ACCENT_2)
            col = C_TEXT if i == sel else C_MUTED
            if self.tab == 0:
                name, price, _ov, _d = LOOKS[key]
                ui.text(surf, name, (r.x + 14, r.y + 9), 20, col, bold=i == sel)
                if key == g.closet["cur"]:
                    tag, tc = "usando", C_GREEN
                elif key in g.closet["owned"]:
                    tag, tc = "seu", C_LILAC
                elif price is None:
                    src = gift_source(key)
                    tag, tc = (f"presente: {NPCS[src[0]]['short']}" if src else "presente"), C_PINK
                else:
                    tag, tc = "na boutique", C_GOLD
            elif key is None:
                ui.text(surf, "Sem acessórios (tirar todos)", (r.x + 14, r.y + 9), 20, col, bold=i == sel)
                tag, tc = "", C_MUTED
            else:
                a = ACCESSORIES[key]
                surf.blit(art.item_icon(key, 2), (r.x + 8, r.y + 5))
                ui.text(surf, a["name"], (r.x + 52, r.y + 9), 20, col, bold=i == sel)
                if g.closet["worn"].get(a["slot"]) == key:
                    tag, tc = "usando", C_GREEN
                elif key in g.closet["acc"]:
                    tag, tc = SLOTS[a["slot"]].lower(), C_LILAC
                else:
                    tag, tc = "na mochila", C_GOLD
            if tag:
                ui.text(surf, tag, (r.right - 14, r.y + 10), 17, tc, right=True)
            y += 46
        if top > 0:
            ui.text(surf, "mais acima", (outer.x + 240, outer.y + 100), 13, C_MUTED, center=True)
        if top + nrows < len(rows):
            ui.text(surf, "mais abaixo", (outer.x + 240, outer.y + 108 + nrows * 46 - 4), 13, C_MUTED, center=True)
        # prévia: a Letícia girando devagar
        key = rows[sel]
        if self.tab == 0:
            look = player_look(key)
            name, _p, _ov, desc = LOOKS[key]
        elif key is None:
            look = player_look(acc={})
            name, desc = "Sem acessórios", "Só a roupa, sem nada por cima."
        else:
            a = ACCESSORIES[key]
            worn = dict(g.closet["worn"])
            worn[a["slot"]] = key
            look = player_look(acc=worn_look(g, worn))
            name, desc = a["name"], a["desc"]
        frames = art.character_frames(look)
        d = ("down", "left", "up", "right")[int(self.t / 1.4) % 4]
        img = frames[(d, int(self.t * 6) % 4 if int(self.t / 1.4) % 2 else 0)]
        big = pygame.transform.scale_by(img, 3)
        stage = pygame.Rect(outer.x + 480, outer.y + 108, 352, 290)
        ui.slot(surf, stage, fill=(40, 28, 58))
        pygame.draw.ellipse(surf, (28, 18, 40), (stage.centerx - 60, stage.bottom - 46, 120, 26))
        surf.blit(big, (stage.centerx - big.get_width() // 2, stage.bottom - 34 - big.get_height()))
        ui.text(surf, name, (stage.centerx, stage.bottom + 12), 24, C_TEXT, bold=True, center=True)
        for i, ln in enumerate(ui.wrap(desc, 17, 350)[:3]):
            ui.text(surf, ln, (stage.centerx, stage.bottom + 44 + i * 21), 17, C_MUTED, center=True)
        if self.msg_t > 0:
            for i, ln in enumerate(ui.wrap(self.msg, 19, outer.w - 60)[:2]):
                ui.text(surf, ln, (outer.centerx, outer.bottom - 70 + i * 22), 19, C_GREEN, bold=True, center=True)
        ui.text(surf, "Cima/baixo: escolher   Esquerda/direita: aba   E: vestir ou tirar   Esc: sair",
                (outer.centerx, outer.bottom - 28), 16, C_MUTED, center=True)

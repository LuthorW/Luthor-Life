"""Closet da Letícia: trocar de roupa no guarda-roupa da cobertura.

Alguns looks ela já tem, outros vêm do catálogo da Boutique Bayside (compra na hora, pelo próprio closet) e três
chegam de presente (Lucy, Vittoria e Ian a 6 corações). As personagens comentam cada look novo uma vez.
O look escolhido vale para o bonequinho no jogo e nas cenas; "Roupa da estação" é o jeito antigo (troca sozinha).
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

STATE = {"cur": "estacao"}


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.closet = dict(cur="estacao", owned=sorted(START), seen=[])
    STATE["cur"] = "estacao"
    _refresh(g)


def _refresh(g):
    if getattr(g, "player", None) is not None:
        g.player.set_look(player_look())


def save_state(g):
    return {"closet": g.closet}


def load_state(g, d):
    c = d.get("closet") or {}
    owned = [k for k in c.get("owned", []) if k in LOOKS]
    g.closet = dict(cur=c.get("cur", "estacao") if c.get("cur") in LOOKS else "estacao",
                    owned=sorted(set(owned) | START), seen=list(c.get("seen", [])))
    STATE["cur"] = g.closet["cur"]
    _refresh(g)


def player_look(key=None):
    """Look atual da Letícia (o jogo e as cenas usam este)."""
    key = key or STATE["cur"]
    ov = LOOKS.get(key, LOOKS["estacao"])[2]
    if not ov:
        return characters.dress("leticia", PLAYER_LOOK)
    return {**PLAYER_LOOK, **ov}


def wear(g, key):
    g.closet["cur"] = key
    STATE["cur"] = key
    _refresh(g)


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
    if key == "estacao":
        return None
    tag = f"{npc.key}:{key}"
    if tag in g.closet["seen"]:
        return None
    g.closet["seen"].append(tag)
    line = SPECIAL.get(npc.key, {}).get(key)
    return line or random.choice(GENERIC.get(key, ["Roupa nova? Ficou ótima."]))


# ---------------------------------------------------------------------------
# Ganchos e a tela do closet
# ---------------------------------------------------------------------------
def object_label(g, o):
    if o.kind == "wardrobe" and g.map_name == "home":
        return "Closet"
    return None


def use_object(g, o):
    if o.kind == "wardrobe" and g.map_name == "home":
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
    def __init__(self, g):
        self.g = g
        self.sel = ORDER.index(g.closet["cur"]) if g.closet["cur"] in ORDER else 0
        self.top = 0
        self.t = 0.0
        self.msg, self.msg_t = "", 0.0

    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL:
            self.sel = (self.sel - ev.y) % len(ORDER)
            audio.sfx("move")
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(ORDER); audio.sfx("move")
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(ORDER); audio.sfx("move")
        elif ev.key in ui.CONFIRM:
            self.choose()
        elif ev.key in ui.CANCEL:
            self.done = True

    def choose(self):
        g = self.g
        key = ORDER[self.sel]
        name, price, _ov, _d = LOOKS[key]
        if key in g.closet["owned"]:
            wear(g, key)
            audio.sfx("confirm")
            self.msg, self.msg_t = f"Vestindo: {name}", 2.0
            return
        if price is None:
            src = gift_source(key)
            who = NPCS[src[0]]["short"] if src else "alguém"
            self.msg, self.msg_t = f"Esse só chega de presente ({who}, {src[1] if src else 6} corações).", 2.5
            audio.sfx("blip")
            return
        if g.money < price:
            self.msg, self.msg_t = f"Faltam ${price - g.money} para esse look.", 2.0
            audio.sfx("blip")
            return

        def buy(i):
            if i != 0:
                return
            g.money -= price
            g.closet["owned"].append(key)
            wear(g, key)
            audio.sfx("buy")
            self.msg, self.msg_t = f"Comprado e vestido: {name}!", 2.5
        g.push(ui.Choice(f"Encomendar \"{name}\" da Boutique Bayside por ${price}? A entrega é na hora.",
                         ["Comprar e vestir", "Agora não"], buy))

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)

    def draw(self, surf):
        g = self.g
        outer = pygame.Rect(0, 0, 860, 560)
        outer.center = (SCREEN_W // 2 - 40, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "Closet da Letícia", (outer.x + 28, outer.y + 16), 28, C_GOLD, bold=True)
        ui.text(surf, f"Dinheiro: ${g.money}", (outer.right - 28, outer.y + 24), 18, C_TEXT, right=True)
        # lista
        rows = 10
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + rows:
            self.top = self.sel - rows + 1
        y = outer.y + 64
        for i in range(self.top, min(len(ORDER), self.top + rows)):
            key = ORDER[i]
            name, price, _ov, _d = LOOKS[key]
            r = pygame.Rect(outer.x + 20, y, 420, 40)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            ui.text(surf, name, (r.x + 14, r.y + 8), 20, C_TEXT if i == self.sel else C_MUTED)
            if key == g.closet["cur"]:
                tag, col = "usando", C_GREEN
            elif key in g.closet["owned"]:
                tag, col = "seu", C_LILAC
            elif price is None:
                src = gift_source(key)
                tag, col = (f"presente: {NPCS[src[0]]['short']}" if src else "presente"), C_PINK
            else:
                tag, col = f"${price}", C_GOLD
            ui.text(surf, tag, (r.right - 14, r.y + 9), 18, col, right=True)
            y += 44
        if self.top > 0:
            pygame.draw.polygon(surf, C_MUTED, [(outer.x + 230, outer.y + 56), (outer.x + 222, outer.y + 62),
                                                (outer.x + 238, outer.y + 62)])
        if self.top + rows < len(ORDER):
            by = outer.y + 64 + rows * 44
            pygame.draw.polygon(surf, C_MUTED, [(outer.x + 230, by + 6), (outer.x + 222, by), (outer.x + 238, by)])
        # prévia: a Letícia girando devagar
        key = ORDER[self.sel]
        name, price, _ov, desc = LOOKS[key]
        frames = art.character_frames(player_look(key))
        d = ("down", "left", "up", "right")[int(self.t / 1.4) % 4]
        img = frames[(d, int(self.t * 6) % 4 if int(self.t / 1.4) % 2 else 0)]
        big = pygame.transform.scale_by(img, 3)
        px = outer.x + 470 + (360 - big.get_width()) // 2
        stage = pygame.Rect(outer.x + 470, outer.y + 64, 360, 300)
        pygame.draw.rect(surf, (40, 28, 58), stage, border_radius=12)
        pygame.draw.ellipse(surf, (28, 18, 40), (stage.centerx - 60, stage.bottom - 46, 120, 26))
        surf.blit(big, (px, stage.bottom - 34 - big.get_height()))
        ui.text(surf, name, (stage.centerx, stage.bottom + 12), 24, C_TEXT, bold=True, center=True)
        for i, ln in enumerate(ui.wrap(desc, 17, 350)[:3]):
            ui.text(surf, ln, (stage.centerx, stage.bottom + 46 + i * 22), 17, C_MUTED, center=True)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (outer.centerx, outer.bottom - 62), 20, C_GREEN, bold=True, center=True)
        ui.text(surf, "Cima/baixo: escolher   E: vestir ou comprar   Esc: sair", (outer.centerx, outer.bottom - 32),
                16, C_MUTED, center=True)

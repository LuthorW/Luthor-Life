"""La Boutique: loja de roupas e acessórios entre o Grão Nobre e a CatCo, da estilista Celeste Waite.

- Prédio na Avenida Siegel (x 38..43, porta em 42,15) com vitrine de manequins, toldo listrado e letreiro preto.
- Interior (`build`): araras, manequins, provador (abre o closet para trocar de roupa ali mesmo), vitrine de joias,
  estante de bolsas, chapeleiro, espelho e o balcão da Celeste (conversa por cima dele, como nas outras lojas).
- A loja (`BoutiqueShop`, aberta conversando com a Celeste) tem duas abas: Roupas (os looks do closet que se compram,
  mais os exclusivos daqui) e Acessórios. A Letícia aparece experimentando o que está escolhido.
- Acessórios (`ACCESSORIES`) são itens da mochila (kind "acessorio"): dá para presentear (cada personagem ama,
  gosta ou não gosta) ou usar. Usar = F na barra ou o closet, que guarda o acessório e veste no bonequinho
  (um por espaço: cabeça, olhos, orelhas, pescoço e bolsa). O desenho fica em sprites._accessories.
"""
import random

import pygame

from . import art, world, ui, audio, lighting, closet, caprichado
from .art import new, R, P, shade, mix
from .data import ITEMS, FLAG_LABELS
from .characters import NPCS
from .entities import PLAYER_LOOK
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_PINK, C_RED

GOLD = (214, 172, 82)
BLACK = (30, 28, 36)
BLUSH = (238, 206, 208)
CREAM = (248, 242, 234)
VELVET = (110, 40, 120)
CHROME = (186, 188, 200)
DISCOUNT_FLAG = "celeste_vip"
FLAG_LABELS[DISCOUNT_FLAG] = "Cliente VIP da Celeste: 20% de desconto na La Boutique."


# ===========================================================================
# Acessórios
# ===========================================================================
SLOTS = {"cabeca": "Cabeça", "olhos": "Olhos", "orelhas": "Orelhas", "pescoco": "Pescoço", "bolsa": "Bolsa"}
SLOT_ORDER = list(SLOTS)


def _acc(name, slot, price, icon, color, desc, **look):
    return dict(name=name, slot=slot, price=price, icon=icon, color=color, desc=desc, look=look)


ACCESSORIES = {
    "oculos_sol": _acc("Óculos de Sol", "olhos", 140, "a_sunglasses", (30, 26, 34),
                       "Lentes escuras e armação grossa. Ninguém vê a CEO revirando os olhos.",
                       sunglasses=(30, 26, 34)),
    "oculos_aro": _acc("Óculos de Aro Dourado", "olhos", 160, "a_glasses", GOLD,
                       "Aro fino dourado. Dá um ar de quem leu todos os relatórios.",
                       glasses=True, glasses_color=GOLD),
    "chapeu_palha": _acc("Chapéu de Palha", "cabeca", 90, "a_strawhat", (226, 196, 120),
                         "Aba larga para o sol da orla. Combina com a Marina Luthor.", hat=(226, 196, 120)),
    "boina": _acc("Boina Francesa", "cabeca", 85, "a_beret", (150, 30, 50),
                  "Vinho, de lã, inclinada para o lado. Paris em National City.", beret=(150, 30, 50)),
    "tiara_perolas": _acc("Tiara de Pérolas", "cabeca", 220, "a_tiara", (242, 238, 232),
                          "Pérolas pequenas e uma ametista no meio. Discreta, mas nem tanto.",
                          tiara=(242, 238, 232), tiara_jewel=(150, 70, 220)),
    "brincos_ouro": _acc("Brincos de Ouro", "orelhas", 180, "a_earrings", (232, 196, 90),
                         "Argolas pequenas de ouro. Clássicas para qualquer reunião.", earrings=(232, 196, 90)),
    "brincos_perola": _acc("Brincos de Pérola", "orelhas", 150, "a_earrings", (246, 244, 240),
                           "Uma pérola em cada orelha. Elegância sem esforço.", earrings=(246, 244, 240)),
    "colar_ametista": _acc("Colar de Ametista", "pescoco", 280, "a_necklace", (150, 60, 220),
                           "Corrente dourada com uma ametista roxa. Roxo Luthor, de novo.",
                           necklace=(232, 196, 90), pendant=(150, 60, 220)),
    "colar_perolas": _acc("Colar de Pérolas", "pescoco", 240, "a_necklace", (246, 244, 240),
                          "Um fio de pérolas, como nos retratos antigos da família.",
                          necklace=(246, 244, 240), pendant=(246, 244, 240)),
    "lenco_seda": _acc("Lenço de Seda", "pescoco", 110, "a_scarf", (150, 70, 210),
                       "Seda lilás amarrada no pescoço. Leve até no verão.", scarf=(150, 70, 210)),
    "bolsa_couro": _acc("Bolsa de Couro", "bolsa", 320, "a_bag", (124, 72, 44),
                        "Couro caramelo com fecho dourado. Cabe o tablet e três canetas.", bag=(124, 72, 44)),
    "bolsa_grife": _acc("Bolsa de Grife", "bolsa", 520, "a_bag", (110, 30, 160),
                        "Roxa, de alça fina, edição limitada. A Celeste só tinha duas.", bag=(110, 30, 160)),
}
ACC_ORDER = list(ACCESSORIES)
for _k, _a in ACCESSORIES.items():
    ITEMS[_k] = dict(name=_a["name"], kind="acessorio", price=_a["price"], icon=_a["icon"], color=_a["color"],
                     desc=_a["desc"] + " Aperte F para usar ou dê de presente.")


# ---------------------------------------------------------------------------
# Ícones dos acessórios (16x16)
# ---------------------------------------------------------------------------
_prev_icon = art._icon


def _icon_acc(kind, color):
    c = color
    s = new(16, 16)
    if kind == "a_sunglasses":
        c = mix(c, (255, 255, 255), 0.45)          # armação clara para aparecer no fundo escuro da mochila
        for x0 in (1, 9):
            R(s, c, x0, 6, 6, 1)
            R(s, c, x0 - 1 if x0 == 1 else x0 + 6, 6, 1, 2)
            R(s, (24, 20, 34), x0, 7, 6, 3); R(s, (24, 20, 34), x0 + 1, 10, 4, 1)
            P(s, (130, 120, 170), x0 + 1, 7)
        R(s, c, 7, 7, 2, 1)
    elif kind == "a_glasses":
        for x0 in (1, 9):
            pygame.draw.rect(s, c, (x0, 6, 6, 5), 1)
            R(s, (200, 226, 240), x0 + 1, 7, 4, 3)
            P(s, (250, 250, 255), x0 + 1, 7)
        R(s, c, 7, 7, 2, 1)
    elif kind == "a_strawhat":
        pygame.draw.ellipse(s, c, (0, 8, 16, 6))
        pygame.draw.ellipse(s, shade(c, 0.8), (1, 11, 14, 3))
        R(s, c, 4, 3, 8, 7)
        R(s, shade(c, 1.12), 5, 3, 6, 1)
        R(s, (150, 40, 60), 4, 8, 8, 2)
    elif kind == "a_beret":
        pygame.draw.ellipse(s, c, (1, 5, 14, 8))
        R(s, shade(c, 0.7), 2, 11, 12, 2)
        R(s, shade(c, 1.2), 4, 6, 5, 1)
        R(s, shade(c, 0.7), 7, 3, 2, 2)
    elif kind == "a_tiara":
        pygame.draw.arc(s, c, (1, 4, 14, 14), 0.2, 2.94, 2)
        for x in (3, 8, 12):
            pygame.draw.circle(s, c, (x, 5 if x == 8 else 6), 1)
        R(s, (150, 70, 220), 7, 3, 2, 2)
    elif kind == "a_earrings":
        for x in (4, 11):
            R(s, (200, 170, 90), x, 3, 1, 4)
            pygame.draw.circle(s, c, (x, 9), 3)
            pygame.draw.circle(s, shade(c, 0.8), (x, 9), 3, 1)
            P(s, (255, 255, 255), x - 1, 8)
    elif kind == "a_necklace":
        pygame.draw.arc(s, (226, 192, 96) if c != (246, 244, 240) else c, (1, -2, 14, 14), 3.6, 5.8, 1)
        for (x, y) in ((3, 6), (5, 8), (7, 9), (9, 9), (11, 8), (13, 6)):
            P(s, (226, 192, 96) if c != (246, 244, 240) else c, x, y)
        pygame.draw.polygon(s, c, [(8, 10), (11, 12), (8, 15), (5, 12)])
        P(s, mix(c, (255, 255, 255), 0.5), 7, 11)
    elif kind == "a_scarf":
        R(s, c, 2, 3, 12, 4)
        R(s, shade(c, 0.78), 2, 6, 12, 1)
        R(s, c, 8, 7, 3, 7); R(s, shade(c, 0.78), 10, 7, 1, 7)
        R(s, mix(c, (255, 255, 255), 0.3), 3, 4, 4, 1)
    elif kind == "a_bag":
        pygame.draw.arc(s, shade(c, 0.6), (4, 1, 8, 10), 0.0, 3.14, 1)
        R(s, c, 2, 6, 12, 9)
        R(s, shade(c, 0.7), 2, 6, 12, 3)
        R(s, mix(c, (255, 255, 255), 0.25), 3, 9, 1, 5)
        R(s, GOLD, 7, 8, 2, 2)
    else:
        return _prev_icon(kind, color)
    return s


art._icon = _icon_acc


# ===========================================================================
# Looks à venda (os do closet com preço e os exclusivos da boutique)
# ===========================================================================
NEW_LOOKS = {
    "vestido_verao": ("Vestido de verão", 380, dict(outfit="dress_floral", cloth=(248, 238, 218), accent=(228, 92, 124),
                                                    sleeves="short"),
                      "Florido, rodado e de manga curta. A Celeste diz que é \"o vestido mais feliz da loja\"."),
    "pretinho": ("Pretinho básico", 460, dict(outfit="dress", cloth=(32, 30, 38), accent=GOLD),
                 "O vestido preto com cinto dourado que resolve qualquer noite."),
    "terno_branco": ("Terno branco", 680, dict(outfit="blazer", cloth=(244, 242, 238), accent=(110, 30, 160),
                                               pants=(236, 234, 230)),
                     "Branco do blazer à calça. Ousado para quem vive perto de café."),
    "moletom": ("Moletom da Luthor Corp", 160, dict(outfit="shirt", cloth=(124, 52, 188), accent=(240, 236, 246),
                                                    pants=(52, 50, 64)),
                "Roxo, macio e com o L bordado. Uniforme oficial de domingo."),
    "jeans": ("Jaqueta jeans", 300, dict(outfit="leather", cloth=(72, 104, 156), accent=(240, 238, 232),
                                         pants=(40, 44, 64)),
              "Jaqueta jeans com camiseta branca. A Celeste jura que voltou à moda."),
    "assinatura": ("Criação da Celeste", None, dict(outfit="dress", cloth=(98, 36, 150), accent=GOLD),
                   "Vestido roxo feito à mão pela Celeste, com o cinto dourado. Peça única."),
}
closet.LOOKS.update(NEW_LOOKS)
closet.ORDER[:] = list(closet.LOOKS)
closet.GIFTS.append(("celeste", 6, "assinatura",
                     "A Celeste mandou uma caixa preta com laço dourado: o vestido roxo que ela desenhou para você. "
                     "O bilhete diz: \"Peça única. Se alguém perguntar, a estilista é minha amiga.\""))
closet.GENERIC.update({
    "vestido_verao": ["Vestido florido! Hoje é dia de sol, né?", "Que vestido alegre. Combinou com você."],
    "pretinho": ["O pretinho básico nunca falha.", "Elegante! Vai sair hoje à noite?"],
    "terno_branco": ["Terno branco? Coragem! Cuidado com o café.", "Esse branco ficou impecável."],
    "moletom": ["Moletom da empresa! Hoje é dia de folga?", "Que confortável. Também quero um."],
    "jeans": ["Jaqueta jeans! Bem descolada.", "Jeans com jeans? Funcionou, viu?"],
    "assinatura": ["Que vestido lindo! Onde você comprou?", "Esse roxo com dourado... parece feito para você."],
})
closet.SPECIAL.setdefault("celeste", {}).update({
    "assinatura": "Minha criação! Gira, gira! Ficou ainda melhor do que no croqui.",
    "gala": "Vestido de gala no meio do dia? Eu aprovo. A vida é curta para guardar roupa boa.",
    "moletom": "Moletom. Tá. Hoje eu deixo. Mas só hoje.",
    "terno_branco": "Terno branco! Eu disse que ia ficar perfeito em você.",
    "vestido_verao": "O vestido mais feliz da loja na cliente mais ocupada da cidade. Equilíbrio.",
    "pretinho": "O pretinho com o cinto dourado. Sabia que você ia levar.",
})
closet.SPECIAL.setdefault("lucy", {}).update({
    "terno_branco": "Terno branco? Isso é uma declaração. Só não sei do quê ainda.",
    "jeans": "Jaqueta jeans! Agora sim parece que você não manda em ninguém.",
})
closet.SPECIAL.setdefault("vittoria", {}).update({
    "pretinho": "Pretinho e dourado. Cara, assim você me distrai em reunião.",
    "assinatura": "Isso é da Celeste, não é? Ela tem mãos de ouro. E você tem sorte.",
})

# comentários dos acessórios (uma vez por personagem, como os looks)
ACC_LINES = {
    "oculos_sol": ["Óculos escuros! Celebridade na área?", "Esses óculos ficaram ótimos. Misteriosa."],
    "oculos_aro": ["Óculos novos? Ficou com cara de professora. Das boas.", "O aro dourado combinou com você."],
    "chapeu_palha": ["Chapéu de palha! Vai pra praia?", "Que chapéu bonito. Protege do sol e ainda é charmoso."],
    "boina": ["Boina! Très chic.", "Essa boina te deixou com cara de artista."],
    "tiara_perolas": ["Uma tiara! Princesa da Luthor Corp?", "Pérolas no cabelo. Que delicado."],
    "brincos_ouro": ["Brincos novos? Brilharam com a luz.", "Argolas douradas! Clássico."],
    "brincos_perola": ["Brincos de pérola. Elegante como sempre.", "Que brincos lindos."],
    "colar_ametista": ["Que colar bonito! Roxo, claro.", "Essa pedra roxa combina com tudo seu."],
    "colar_perolas": ["Colar de pérolas! Parece retrato de família antiga.", "As pérolas ficaram lindas."],
    "lenco_seda": ["Lenço de seda! Muito charmoso.", "Esse lenço lilás deu um toque especial."],
    "bolsa_couro": ["Bolsa nova! Cabe o laboratório inteiro aí?", "Que bolsa bonita. Couro de verdade?"],
    "bolsa_grife": ["Bolsa de grife! A Celeste te convenceu, né?", "Essa bolsa roxa é de outro mundo."],
}
ACC_SPECIAL = {
    "celeste": {k: "Isso é da minha loja! Ficou ainda melhor em você do que na vitrine." for k in ACCESSORIES},
    "brainy": {"oculos_aro": "Óculos! Finalmente alguém que entende a importância de enxergar bem."},
    "joca": {"chapeu_palha": "Chapéu de palha! Agora sim, moça. Bora pro píer?"},
    "ian": {"chapeu_palha": "Esse chapéu é de quem vai velejar. Tô só dizendo."},
    "lucy": {"oculos_sol": "Óculos escuros, Luthor? Fugindo da imprensa?"},
    "vittoria": {"colar_ametista": "Bella. Essa pedra fica perfeita perto do seu rosto."},
}


# ===========================================================================
# Gostos (ama / gosta / não gosta) dos acessórios
# ===========================================================================
TASTES = {
    "sam": dict(love=["colar_perolas"], like=["brincos_ouro", "bolsa_couro", "oculos_aro"], dislike=["chapeu_palha"]),
    "brainy": dict(love=["oculos_aro"], like=["boina"], dislike=["bolsa_grife", "tiara_perolas"]),
    "jess": dict(love=["bolsa_couro", "oculos_aro"], like=["brincos_perola", "lenco_seda"], dislike=["boina"]),
    "rafa": dict(love=["boina"], like=["oculos_sol"], dislike=["tiara_perolas"]),
    "lucy": dict(love=["oculos_sol"], like=["bolsa_couro", "brincos_ouro"], dislike=["tiara_perolas"]),
    "vittoria": dict(love=["bolsa_grife", "brincos_ouro"], like=["lenco_seda", "colar_ametista", "oculos_sol"],
                     dislike=["chapeu_palha"]),
    "nia": dict(love=["tiara_perolas", "colar_ametista"], like=["lenco_seda", "boina"], dislike=["oculos_sol"]),
    "barry": dict(love=["boina"], like=["oculos_sol"], dislike=["colar_perolas"]),
    "theo": dict(love=["oculos_aro"], like=["boina", "lenco_seda"], dislike=["bolsa_grife"]),
    "bea": dict(love=["chapeu_palha"], like=["lenco_seda"], dislike=["bolsa_grife"]),
    "graca": dict(love=["brincos_ouro"], like=["lenco_seda", "colar_perolas"], dislike=["oculos_sol"]),
    "marco": dict(like=["oculos_sol"], dislike=["tiara_perolas", "colar_perolas"]),
    "joca": dict(love=["chapeu_palha"], like=["oculos_sol"], dislike=["bolsa_grife", "tiara_perolas"]),
    "ian": dict(love=["chapeu_palha"], like=["oculos_sol", "bolsa_couro"], dislike=["tiara_perolas"]),
    "yang": dict(like=["oculos_aro"], dislike=["tiara_perolas", "chapeu_palha"]),
    "meredith": dict(love=["lenco_seda"], like=["brincos_perola", "oculos_sol"], dislike=["bolsa_grife"]),
    "milany": dict(love=["colar_perolas"], like=["brincos_perola", "bolsa_couro"], dislike=["boina"]),
    "izzie": dict(love=["tiara_perolas"], like=["chapeu_palha", "brincos_ouro"], dislike=["oculos_aro"]),
    "addison": dict(love=["brincos_perola", "bolsa_grife"], like=["colar_ametista", "oculos_sol"],
                    dislike=["chapeu_palha"]),
    "celeste": dict(love=["perfume", "aquarela", "orquidea"], like=["flores", "chocolate_belga", "vinil", "cappuccino",
                                                                    "macarons", "coroa_flores", "porta_retrato"],
                    dislike=["lata", "isca", "jornal"]),
}
for _k, _t in TASTES.items():
    if _k not in NPCS:
        continue
    _gifts = NPCS[_k].setdefault("gifts", {})
    for _kind, _items in _t.items():
        _lst = _gifts.setdefault(_kind, [])
        for _it in _items:
            if _it not in ITEMS:
                continue
            for _other in ("love", "like", "dislike"):
                if _other != _kind and _it in _gifts.get(_other, []):
                    _gifts[_other].remove(_it)
            if _it not in _lst:
                _lst.append(_it)


# ===========================================================================
# Arte: móveis da boutique
# ===========================================================================
def _cabide(s, x, top, c, kind):
    """Uma peça pendurada na arara (x = meio, top = linha do cabide)."""
    R(s, CHROME, x, top - 2, 1, 2)
    R(s, shade(CHROME, 0.8), x - 2, top, 5, 1)
    d = shade(c, 0.78)
    if kind == 0:                                 # blusa
        R(s, c, x - 2, top + 1, 5, 7)
        R(s, d, x + 2, top + 1, 1, 7)
        R(s, c, x - 3, top + 1, 1, 3); R(s, c, x + 3, top + 1, 1, 3)
    elif kind == 1:                               # vestido comprido
        R(s, c, x - 2, top + 1, 5, 6)
        R(s, c, x - 3, top + 7, 7, 8)
        R(s, d, x + 3, top + 7, 1, 8)
        R(s, mix(c, (255, 255, 255), 0.25), x - 1, top + 2, 1, 4)
    else:                                         # casaco
        R(s, c, x - 3, top + 1, 7, 11)
        R(s, d, x + 3, top + 1, 1, 11)
        R(s, shade(c, 0.6), x, top + 2, 1, 9)


def _arara(colors):
    def make():
        s = new(32, 32)
        # base e hastes cromadas
        R(s, shade(CHROME, 0.7), 1, 29, 6, 2); R(s, shade(CHROME, 0.7), 25, 29, 6, 2)
        R(s, CHROME, 3, 5, 1, 25); R(s, CHROME, 28, 5, 1, 25)
        R(s, mix(CHROME, (255, 255, 255), 0.4), 2, 5, 28, 1)
        R(s, shade(CHROME, 0.75), 2, 6, 28, 1)
        for i, c in enumerate(colors):
            _cabide(s, 7 + i * 5, 8, c, (i * 2 + len(colors)) % 3)
        return s
    return make


def _manequim(dress, accent):
    def make():
        s = new(16, 32)
        R(s, (60, 54, 64), 3, 30, 10, 2)                        # base
        R(s, (90, 84, 96), 7, 22, 2, 8)                         # haste
        R(s, (230, 220, 210), 7, 1, 2, 2)                        # pescoço do busto
        pygame.draw.ellipse(s, (236, 226, 216), (5, 0, 6, 3))
        # vestido no busto
        R(s, dress, 4, 3, 8, 4)
        R(s, dress, 5, 7, 6, 4)
        R(s, dress, 4, 11, 8, 4)
        R(s, dress, 3, 15, 10, 7)
        R(s, shade(dress, 0.78), 11, 3, 1, 4); R(s, shade(dress, 0.78), 12, 15, 1, 7)
        R(s, mix(dress, (255, 255, 255), 0.3), 5, 4, 1, 3)
        R(s, accent, 5, 10, 6, 1)                               # cinto
        R(s, shade(dress, 0.8), 3, 21, 10, 1)
        P(s, accent, 7, 17); P(s, accent, 10, 19); P(s, accent, 5, 19)
        return s
    return make


def _provador():
    s = new(32, 46)
    wood, wood_dk = (70, 46, 40), (48, 30, 28)
    R(s, wood_dk, 0, 2, 32, 44)
    R(s, wood, 1, 3, 30, 43)
    R(s, (250, 236, 200), 3, 10, 26, 34)                         # luz lá dentro
    # sanefa com friso dourado
    R(s, BLACK, 0, 0, 32, 9)
    R(s, GOLD, 0, 8, 32, 1); R(s, GOLD, 0, 0, 32, 1)
    for x in range(4, 29, 4):
        P(s, GOLD, x, 4)
    # cortinas de veludo presas para os lados (fresta no meio)
    for (x0, x1) in ((3, 14), (18, 29)):
        R(s, VELVET, x0, 9, x1 - x0, 37)
        for x in range(x0 + 1, x1, 3):
            R(s, shade(VELVET, 0.72), x, 9, 1, 37)
            R(s, mix(VELVET, (255, 255, 255), 0.18), x + 1, 9, 1, 37)
    R(s, GOLD, 12, 26, 3, 2); R(s, GOLD, 17, 26, 3, 2)            # prendedores
    R(s, shade(VELVET, 0.6), 3, 44, 26, 2)
    return s


def _vitrine_joias():
    s = new(32, 26)
    base = CREAM
    R(s, shade(base, 0.82), 0, 13, 32, 13)
    R(s, base, 1, 13, 30, 11)
    R(s, GOLD, 0, 13, 32, 1)
    for x in (2, 17):
        R(s, shade(base, 0.92), x, 15, 13, 7)
        R(s, GOLD, x + 6, 18, 2, 1)
    R(s, shade(base, 0.6), 1, 24, 3, 2); R(s, shade(base, 0.6), 28, 24, 3, 2)
    # tampo de vidro com as joias
    R(s, GOLD, 0, 2, 32, 1); R(s, GOLD, 0, 2, 1, 11); R(s, GOLD, 31, 2, 1, 11)
    R(s, (196, 222, 236), 1, 3, 30, 10)
    R(s, (60, 44, 70), 2, 9, 28, 3)                              # veludo do fundo
    pygame.draw.arc(s, (232, 196, 90), (3, 3, 9, 9), 3.4, 6.0, 1)  # colar
    R(s, (150, 60, 220), 7, 10, 2, 2)
    for (x, c) in ((15, (232, 196, 90)), (19, (246, 244, 240)), (23, (232, 196, 90))):
        pygame.draw.circle(s, c, (x, 10), 1)                     # anéis
    R(s, (246, 244, 240), 26, 9, 1, 2); R(s, (246, 244, 240), 28, 9, 1, 2)
    for (x, y) in ((4, 4), (5, 5), (20, 4), (21, 5), (27, 4)):    # reflexo do vidro
        P(s, (240, 250, 255), x, y)
    return s


def _estante_bolsas():
    s = new(32, 38)
    wood = (244, 238, 230)
    R(s, shade(wood, 0.8), 0, 0, 32, 38)
    R(s, wood, 1, 1, 30, 36)
    for y in (12, 24, 36):
        R(s, shade(wood, 0.72), 1, y, 30, 2)
    R(s, GOLD, 0, 0, 32, 1)
    # bolsas (prateleira de cima e do meio)
    for (x, c) in ((3, (124, 72, 44)), (12, (110, 30, 160)), (22, (30, 28, 36))):
        pygame.draw.arc(s, shade(c, 0.7), (x + 1, 2, 6, 7), 0.0, 3.14, 1)
        R(s, c, x, 6, 8, 6); R(s, shade(c, 0.7), x, 6, 8, 2); P(s, GOLD, x + 3, 8)
    for (x, c) in ((3, (220, 150, 160)), (13, (240, 220, 180))):
        R(s, c, x, 17, 10, 7); R(s, shade(c, 0.75), x, 17, 10, 2)
        R(s, shade(c, 0.6), x + 3, 15, 4, 2)
    R(s, (60, 110, 160), 25, 18, 4, 6)
    # sapatos embaixo
    for (x, c) in ((3, (30, 28, 36)), (11, (180, 40, 60)), (20, GOLD)):
        R(s, c, x, 31, 7, 3); R(s, c, x + 5, 28, 2, 3)
        R(s, shade(c, 0.6), x, 33, 7, 1)
    return s


def _chapeleiro():
    s = new(16, 34)
    pole = (70, 46, 40)
    R(s, shade(pole, 0.8), 3, 32, 10, 2)
    R(s, pole, 7, 6, 2, 26)
    R(s, mix(pole, (255, 255, 255), 0.2), 7, 6, 1, 26)
    # chapéu de palha no topo
    pygame.draw.ellipse(s, (226, 196, 120), (1, 4, 14, 4))
    R(s, (226, 196, 120), 4, 0, 8, 6)
    R(s, (150, 40, 60), 4, 4, 8, 1)
    # boina e lenço nos ganchos
    R(s, (150, 30, 50), 9, 12, 6, 3); R(s, shade((150, 30, 50), 0.7), 9, 14, 6, 1)
    R(s, (150, 70, 210), 2, 15, 4, 10); R(s, shade((150, 70, 210), 0.75), 5, 15, 1, 10)
    R(s, CHROME, 6, 13, 1, 1); R(s, CHROME, 9, 11, 1, 1)
    return s


def _espelho_chao():
    s = new(16, 34)
    R(s, shade(GOLD, 0.7), 2, 30, 12, 3)
    R(s, shade(GOLD, 0.8), 3, 25, 2, 6); R(s, shade(GOLD, 0.8), 11, 25, 2, 6)
    pygame.draw.ellipse(s, GOLD, (1, 0, 14, 28))
    pygame.draw.ellipse(s, (186, 214, 228), (3, 2, 10, 24))
    for i in range(7):                                          # reflexo na diagonal
        P(s, (236, 248, 255), 5 + i // 2, 6 + i)
    P(s, (236, 248, 255), 9, 4); P(s, (236, 248, 255), 10, 5)
    pygame.draw.ellipse(s, shade(GOLD, 0.7), (1, 0, 14, 28), 1)
    return s


def _balcao_boutique():
    s = new(48, 26)
    R(s, BLACK, 0, 10, 48, 14)
    for x in range(4, 46, 8):
        R(s, shade(BLACK, 1.5), x, 12, 1, 10)
    R(s, GOLD, 0, 21, 48, 1)
    R(s, (236, 232, 236), 0, 7, 48, 4)                            # tampo de mármore
    R(s, (250, 248, 250), 0, 7, 48, 1)
    for (x, y) in ((6, 9), (14, 8), (30, 9), (40, 8)):
        R(s, (210, 204, 214), x, y, 3, 1)
    R(s, GOLD, 0, 10, 48, 1)
    R(s, shade(BLACK, 0.7), 0, 24, 48, 2)
    # caixa registradora, sacolas e um vaso de rosas
    R(s, (60, 56, 70), 4, 1, 10, 6); R(s, (120, 200, 170), 6, 2, 6, 2); R(s, (40, 38, 48), 3, 6, 12, 1)
    R(s, (240, 170, 186), 20, 0, 8, 7); pygame.draw.arc(s, (190, 110, 130), (21, -3, 6, 6), 0.0, 3.14, 1)
    R(s, (250, 246, 240), 22, 2, 4, 1)
    R(s, BLACK, 29, 2, 6, 5); P(s, GOLD, 31, 4)
    R(s, (230, 230, 240), 39, 3, 4, 4)
    for (x, y) in ((38, 0), (41, 1), (43, 0)):
        R(s, (210, 50, 80), x, y, 2, 2)
    R(s, (70, 140, 76), 40, 2, 1, 2)
    return s


def _quadro_moda():
    s = new(16, 20)
    R(s, BLACK, 1, 0, 14, 19)
    R(s, (248, 244, 238), 2, 1, 12, 17)
    # croqui: silhueta de vestido em traço
    R(s, (60, 50, 60), 7, 3, 2, 2)
    R(s, (200, 60, 100), 6, 5, 4, 4)
    R(s, (200, 60, 100), 5, 9, 6, 6)
    R(s, (60, 50, 60), 6, 15, 1, 2); R(s, (60, 50, 60), 9, 15, 1, 2)
    R(s, GOLD, 6, 9, 4, 1)
    return s


def _letreiro_boutique():
    s = new(32, 16)
    R(s, BLACK, 0, 1, 32, 13)
    R(s, GOLD, 0, 1, 32, 1); R(s, GOLD, 0, 13, 32, 1)
    # cabide dourado no meio, como o logo da loja
    R(s, GOLD, 15, 3, 2, 2); R(s, GOLD, 16, 5, 1, 2)
    pygame.draw.line(s, GOLD, (16, 7), (8, 11)); pygame.draw.line(s, GOLD, (16, 7), (24, 11))
    R(s, GOLD, 8, 11, 17, 1)
    for x in (4, 27):
        P(s, GOLD, x, 7)
    return s


def _tapete_boutique():
    s = new(80, 48)
    field, edge = (236, 196, 200), (200, 150, 160)
    R(s, edge, 0, 0, 80, 48)
    R(s, CREAM, 2, 2, 76, 44)
    R(s, field, 4, 4, 72, 40)
    for y in range(8, 42, 8):
        for x in range(8 + (y // 8 % 2) * 4, 74, 8):
            P(s, shade(field, 0.9), x, y); P(s, mix(field, (255, 255, 255), 0.4), x + 1, y)
    pygame.draw.ellipse(s, mix(field, (255, 255, 255), 0.35), (28, 14, 24, 20), 1)
    return s


art.OBJECT_BUILDERS.update({
    "arara": _arara([(110, 30, 160), (240, 236, 230), (40, 130, 130), (230, 90, 120), (32, 30, 38)]),
    "arara2": _arara([(124, 72, 44), (236, 210, 140), (72, 104, 156), (246, 236, 214), (150, 30, 50)]),
    "manequim": _manequim((98, 36, 150), GOLD),
    "manequim2": _manequim((246, 236, 214), (228, 92, 124)),
    "provador": _provador, "vitrine_joias": _vitrine_joias, "estante_bolsas": _estante_bolsas,
    "chapeleiro": _chapeleiro, "espelho_chao": _espelho_chao, "balcao_boutique": _balcao_boutique,
    "quadro_moda": _quadro_moda, "letreiro_boutique": _letreiro_boutique, "tapete_boutique": _tapete_boutique,
})
world.OBJECT_DEFS.update({
    "arara": (2, 1, True, "obj"), "arara2": (2, 1, True, "obj"), "manequim": (1, 1, True, "obj"),
    "manequim2": (1, 1, True, "obj"), "provador": (2, 2, True, "obj"), "vitrine_joias": (2, 1, True, "obj"),
    "estante_bolsas": (2, 1, True, "obj"), "chapeleiro": (1, 1, True, "obj"), "espelho_chao": (1, 1, True, "obj"),
    "balcao_boutique": (3, 1, True, "obj"), "quadro_moda": (1, 1, False, "wall"),
    "letreiro_boutique": (2, 1, False, "wall"), "tapete_boutique": (5, 3, False, "decal"),
})
world.COUNTERS.add("balcao_boutique")          # conversa com a Celeste por cima do balcão
lighting.EMITTERS["vitrine_joias"] = ((236, 226, 190), 1.3)
lighting.INTERIOR["boutique"] = ((242, 230, 234), (110, 92, 132), (172, 130, 110), 4)

FLAVOR = {
    "arara": "Blusas, vestidos e casacos em ordem de cor. A Celeste reorganiza toda segunda.",
    "arara2": "A arara das novidades. Tem uma etiqueta escrita à mão: \"para a CEO, quando ela tiver tempo\".",
    "manequim": "Um vestido roxo com cinto dourado. A Celeste diz que esse manequim tem mais estilo que muita gente.",
    "manequim2": "Vestido florido de verão. O manequim parece pronto para um piquenique.",
    "provador": "O provador, com cortina de veludo. Dá para trocar de roupa aqui mesmo.",
    "vitrine_joias": "Brincos, anéis e colares em veludo escuro. Tudo brilha um pouco mais aqui.",
    "estante_bolsas": "Bolsas de couro, uma roxa de grife e três pares de sapato que a Jess já namorou.",
    "chapeleiro": "Chapéu de palha, boina e um lenço lilás pendurados com capricho.",
    "espelho_chao": "Um espelho oval de moldura dourada. A Letícia confere o cabelo. Está ótimo.",
    "balcao_boutique": "O balcão de mármore da Celeste, com sacolas rosa e um vaso de rosas.",
    "quadro_moda": "Um croqui da Celeste, assinado no canto: \"primeira coleção, um dia\".",
    "letreiro_boutique": "O cabide dourado, logo da La Boutique.",
    "tapete_boutique": "Um tapete rosa-claro. Ninguém pisa de sapato sujo aqui. Em tese.",
}


def build():
    """Interior da La Boutique (18x12, porta embaixo em x 8).

    Livres: a entrada (7..9, 9..10), o corredor da fileira 4 (atrás do balcão) e o caminho até cada móvel."""
    rows = world._box(18, 12, "o", 8)
    m = world._interior("boutique", rows, "La Boutique")
    m.add("tapete_boutique", 6, 6)
    m.add("window", 3, 1); m.add("quadro_moda", 7, 1); m.add("letreiro_boutique", 9, 1); m.add("window", 12, 1)
    m.add("estante_bolsas", 1, 2); m.add("chapeleiro", 3, 2)
    m.add("arara", 5, 2); m.add("arara2", 8, 2)
    m.add("provador", 13, 2); m.add("plant", 16, 2)
    m.add("arara2", 1, 5); m.add("vitrine_joias", 5, 5)
    m.add("balcao_boutique", 11, 5); m.add("espelho_chao", 15, 5)
    m.add("arara", 1, 8)
    m.add("armchair", 13, 8); m.add("coffee_table", 14, 8); m.add("armchair", 16, 8)
    m.add("manequim", 5, 9); m.add("manequim2", 11, 9)
    m.add("plant", 1, 10); m.add("plant_big", 16, 10)
    m.finalize()
    return m


# ===========================================================================
# Fachada (prédio caprichado, 6x6 + 1 de telhado) e letreiro
# ===========================================================================
def _fachada(W, H, night):
    """Sobrado rosa-claro: janelas em arco com sacada de ferro, placa preta, toldo listrado e vitrine com manequins.

    Porta na coluna 4 (x 64..80), que é o tile da porta (42, 15)."""
    s = new(W, H)
    parede = BLUSH
    R(s, parede, 0, 8, W, H - 8)
    for y in range(12, H - 30, 5):
        R(s, shade(parede, 0.97), 0, y, W, 1)
    caprichado.cornice(s, 2, W, (244, 238, 236), 7)
    R(s, BLACK, 0, 0, W, 3)
    R(s, GOLD, 0, 9, W, 1)
    # andar de cima: duas janelas em arco com sacadinha de ferro
    for x in (12, 58):
        caprichado._arched(s, x, 16, 26, 30, (250, 246, 242), (170, 206, 232), night)
        R(s, BLACK, x - 3, 44, 32, 2)
        for k in range(x - 2, x + 29, 3):
            R(s, BLACK, k, 38, 1, 6)
        R(s, BLACK, x - 3, 38, 32, 1)
    # placa preta com friso dourado (texto em caprichado.draw_label)
    R(s, BLACK, 4, 56, W - 8, 15)
    R(s, GOLD, 4, 56, W - 8, 1); R(s, GOLD, 4, 70, W - 8, 1)
    caprichado.lantern(s, 0, 58, night); caprichado.lantern(s, W - 4, 58, night)
    caprichado.awning(s, 0, 73, W, BLACK, (246, 242, 240), 9, 8, parede)
    # vitrine com dois manequins (colunas 0..3)
    R(s, BLACK, 3, 87, 56, H - 87 - 3)
    glass = caprichado.LIT if night else (186, 214, 232)
    R(s, glass, 5, 89, 52, H - 89 - 6)
    if not night:
        R(s, (226, 240, 250), 5, 89, 52, 2)
        for i in range(10):
            P(s, (220, 236, 248), 40 + i, H - 10 - i)
    for (mx, dress, acc) in ((12, (98, 36, 150), GOLD), (38, (246, 236, 214), (228, 92, 124))):
        R(s, (236, 226, 216), mx + 3, 93, 2, 2)
        R(s, dress, mx, 95, 8, 4); R(s, dress, mx + 1, 99, 6, 3); R(s, dress, mx - 1, 102, 10, 7)
        R(s, acc, mx + 1, 101, 6, 1)
        R(s, (80, 74, 86), mx + 3, 109, 2, H - 115)
    R(s, (240, 170, 186), 25, H - 16, 6, 7)                       # sacolinha rosa na vitrine
    R(s, (30, 28, 36), 3, H - 5, 56, 2)
    # porta de vidro com moldura preta
    R(s, BLACK, 63, 86, 18, H - 86)
    R(s, caprichado.LIT if night else (176, 212, 234), 65, 88, 14, H - 90)
    R(s, (226, 240, 250) if not night else (255, 240, 190), 65, 88, 3, H - 90)
    R(s, GOLD, 76, 100, 1, 6)
    R(s, (110, 104, 120), 61, H - 1, 22, 1)
    caprichado.vaso(s, 84, H - 11, (255, 236, 140))
    caprichado.side_light(s, W, H, 8)
    R(s, (98, 90, 96), 0, H - 2, 61, 2); R(s, (98, 90, 96), 83, H - 2, W - 83, 2)
    return s


caprichado.BUILDERS["boutique"] = _fachada
caprichado.FACADE_DECOR["boutique"] = ["floreira2", "cavalete"]       # letreiro: caprichado.draw_label


# ===========================================================================
# Loja (aberta pela conversa com a Celeste)
# ===========================================================================
def discount(g):
    return 0.8 if DISCOUNT_FLAG in g.flags else 1.0


def look_price(g, key):
    return int(round(closet.LOOKS[key][1] * discount(g)))


def acc_price(g, key):
    return int(round(ACCESSORIES[key]["price"] * discount(g)))


def looks_for_sale():
    return [k for k in closet.ORDER if closet.LOOKS[k][1] is not None]


def open_shop(g):
    audio.sfx("door")
    g.push(BoutiqueShop(g))


class BoutiqueShop(ui.Modal):
    """Duas abas (Roupas / Acessórios); a Letícia experimenta o que está escolhido, à direita."""
    TABS = ("Roupas", "Acessórios")

    def __init__(self, g):
        self.g = g
        self.tab = 0
        self.sel = [0, 0]
        self.top = [0, 0]
        self.t = 0.0
        self.msg, self.msg_t, self.msg_ok = "", 0.0, True

    def keys(self):
        return looks_for_sale() if self.tab == 0 else ACC_ORDER

    def handle(self, ev):
        n = len(self.keys())
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
            self.buy()
        elif ev.key in ui.CANCEL:
            self.done = True

    def say(self, msg, ok=True):
        self.msg, self.msg_t, self.msg_ok = msg, 2.6, ok
        audio.sfx("buy" if ok else "blip")

    def buy(self):
        g = self.g
        key = self.keys()[self.sel[self.tab]]
        if self.tab == 0:
            name = closet.LOOKS[key][0]
            if key in g.closet["owned"]:
                self.say(f"\"{name}\" já está no seu closet.", False)
                return
            price = look_price(g, key)
            if g.money < price:
                self.say(f"Faltam ${price - g.money} para esse look.", False)
                return
            g.money -= price
            g.closet["owned"].append(key)
            g.stats["boutique"] = g.stats.get("boutique", 0) + 1
            self.say(f"\"{name}\" vai para o closet da cobertura. Aperte E no guarda-roupa para vestir.")
            return
        a = ACCESSORIES[key]
        price = acc_price(g, key)
        if g.money < price:
            self.say(f"Faltam ${price - g.money} para {a['name']}.", False)
            return
        if not g.add_item(key):
            self.say("Mochila cheia.", False)
            return
        g.money -= price
        g.stats["boutique"] = g.stats.get("boutique", 0) + 1
        self.say(f"Comprou {a['name']}! Está na mochila: F para usar ou dê de presente.")

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)

    def preview_look(self):
        g = self.g
        key = self.keys()[self.sel[self.tab]]
        if self.tab == 0:
            base = closet.player_look(key, acc=closet.worn_look(g))
        else:
            worn = dict(g.closet.get("worn", {}))
            worn[ACCESSORIES[key]["slot"]] = key
            base = closet.player_look(acc=closet.worn_look(g, worn))
        return base

    def draw(self, surf):
        g = self.g
        outer = pygame.Rect(0, 0, 860, 580)
        outer.center = (SCREEN_W // 2 - 50, SCREEN_H // 2 - 10)
        ui.panel(surf, outer, alpha=255)
        ui.text(surf, "La Boutique", (outer.x + 28, outer.y + 16), 28, C_GOLD, bold=True)
        sub = "Roupas e acessórios da Celeste Waite" + ("  (20% de desconto VIP)" if discount(g) < 1 else "")
        ui.text(surf, sub, (outer.x + 30, outer.y + 52), 16, C_MUTED)
        ui.text(surf, f"$ {g.money:,}".replace(",", "."), (outer.right - 28, outer.y + 20), 24, C_GOLD,
                bold=True, right=True)
        # abas
        tx = outer.x + 24
        for i, name in enumerate(self.TABS):
            r = pygame.Rect(tx, outer.y + 82, 150, 34)
            if i == self.tab:
                ui.box(surf, r, ui.C_PANEL_2, border=ui.C_ACCENT_2)
            else:
                ui.slot(surf, r, fill=(24, 16, 34))
            ui.text(surf, name, (r.centerx, r.y + 6), 19, C_TEXT if i == self.tab else C_MUTED,
                    bold=i == self.tab, center=True)
            tx += 160
        # lista
        keys = self.keys()
        sel = self.sel[self.tab] = min(self.sel[self.tab], len(keys) - 1)
        rows = 7
        top = self.top[self.tab]
        if sel < top:
            top = sel
        elif sel >= top + rows:
            top = sel - rows + 1
        self.top[self.tab] = top
        y = outer.y + 128
        for i in range(top, min(len(keys), top + rows)):
            key = keys[i]
            r = pygame.Rect(outer.x + 20, y, 456, 44)
            if i == sel:
                ui.box(surf, r, ui.C_PANEL_2, border=ui.C_ACCENT_2)
            if self.tab == 0:
                name = closet.LOOKS[key][0]
                owned = key in g.closet["owned"]
                fr = art.character_frames(closet.player_look(key))[("down", 0)]
                head = fr.subsurface((0, 0, fr.get_width(), min(fr.get_height(), 40))).copy()
                surf.blit(head, (r.x + 10, r.y + 2))
                tag, col = ("no closet", C_LILAC) if owned else (f"$ {look_price(g, key)}", C_GOLD)
            else:
                a = ACCESSORIES[key]
                name = a["name"]
                surf.blit(art.item_icon(key, 2), (r.x + 8, r.y + 6))
                have = g.count_item(key) + (1 if key in g.closet.get("acc", []) else 0)
                tag, col = f"$ {acc_price(g, key)}", C_GOLD
                if have:
                    ui.text(surf, f"tem {have}", (r.right - 96, r.y + 13), 15, C_LILAC, right=True)
                name = f"{name}  ·  {SLOTS[a['slot']]}"
            ui.text(surf, name, (r.x + 54, r.y + 11), 19, C_TEXT if i == sel else C_MUTED, bold=i == sel)
            ui.text(surf, tag, (r.right - 14, r.y + 11), 18, col, right=True)
            y += 48
        if top > 0:
            ui.text(surf, "mais acima", (outer.x + 260, outer.y + 120), 13, C_MUTED, center=True)
        if top + rows < len(keys):
            ui.text(surf, "mais abaixo", (outer.x + 260, outer.y + 128 + rows * 48 - 2), 13, C_MUTED, center=True)
        # provador virtual: a Letícia girando devagar com a peça escolhida
        stage = pygame.Rect(outer.x + 494, outer.y + 128, 342, 300)
        ui.slot(surf, stage, fill=(40, 28, 52))
        frames = art.character_frames(self.preview_look())
        d = ("down", "left", "up", "right")[int(self.t / 1.4) % 4]
        img = frames[(d, int(self.t * 6) % 4 if int(self.t / 1.4) % 2 else 0)]
        big = pygame.transform.scale_by(img, 3)
        pygame.draw.ellipse(surf, (28, 18, 40), (stage.centerx - 60, stage.bottom - 46, 120, 26))
        surf.blit(big, (stage.centerx - big.get_width() // 2, stage.bottom - 34 - big.get_height()))
        key = keys[sel]
        if self.tab == 0:
            title, desc = closet.LOOKS[key][0], closet.LOOKS[key][3]
        else:
            title, desc = ACCESSORIES[key]["name"], ACCESSORIES[key]["desc"]
        ui.text(surf, title, (stage.centerx, stage.bottom + 10), 22, C_TEXT, bold=True, center=True)
        for i, ln in enumerate(ui.wrap(desc, 16, 350)[:3]):
            ui.text(surf, ln, (stage.centerx, stage.bottom + 40 + i * 20), 16, C_MUTED, center=True)
        if self.msg_t > 0:
            for i, ln in enumerate(ui.wrap(self.msg, 18, outer.w - 60)[:2]):
                ui.text(surf, ln, (outer.centerx, outer.bottom - 62 + i * 22), 18,
                        C_GREEN if self.msg_ok else C_RED, bold=True, center=True)
        ui.text(surf, "Cima/baixo: escolher   Esquerda/direita: aba   E: comprar   Esc: sair",
                (outer.centerx, outer.bottom - 28), 16, C_MUTED, center=True)


# ===========================================================================
# Comentários dos acessórios nas conversas
# ===========================================================================
def chat_line(g, npc):
    worn = list(g.closet.get("worn", {}).values())
    random.shuffle(worn)
    for key in worn:
        tag = f"{npc.key}:{key}"
        if tag in g.closet["seen"]:
            continue
        g.closet["seen"].append(tag)
        return ACC_SPECIAL.get(npc.key, {}).get(key) or random.choice(ACC_LINES.get(key, ["Acessório novo? Lindo."]))
    return None


# ===========================================================================
# Celeste: falas extras, aniversário, eventos de coração e a cena dos 4 corações
# ===========================================================================
from . import dialogue, festas, gifts, eventos      # noqa: E402
from .cutscenes import SCENES                        # noqa: E402

dialogue.LINES["celeste"] = {
    "manha": ["Bom dia! Acabei de passar o vapor nos vestidos. A loja inteira cheira a lavanda.",
              "Cappuccino no Grão Nobre antes de abrir. O Harry já sabe: espuma em forma de cabide.",
              "Chegou uma caixa de Milão hoje cedo. Abri com as mãos tremendo, como sempre."],
    "tarde": ["A tarde é a hora das noivas. Elas entram decididas e saem com três opções e uma dúvida.",
              "A Jess passou no almoço e experimentou a mesma bolsa pela quarta vez. Uma hora ela leva.",
              "Se você vier de tarde, o sol bate na vitrine e os brincos fazem arco-íris no chão."],
    "noite": ["Fim de expediente. Meus pés estão pedindo um sofá e um filme ruim.",
              "Noite boa para um vestido preto e um drinque no Noonan's. Ou para dormir às nove. Os dois são chiques."],
    "chuva": ["Chuva fina, cliente pouca. Aproveito para desenhar.",
              "Sabia que capa de chuva também pode ser elegante? Eu tenho três. Nenhuma está à venda."],
    "fds": ["Sábado a loja enche de gente que só quer olhar. Eu adoro. Olhar é o primeiro passo.",
            "No domingo eu vejo o pôr do sol na praia. É a única coisa que eu faço sem pensar em roupa."],
    "boutique": ["Esse espelho de moldura dourada eu trouxe de um brechó em Paris. Ele já viu muita gente bonita.",
                 "O manequim da esquerda se chama Gisele. O da direita ainda não tem nome. Aceito sugestões.",
                 "A arara de novidades muda toda segunda. Se você gostou de alguma coisa, não espera até terça."],
    "cafe": ["Dez minutos de café e eu volto a ser gente. Me pergunta de novo daqui a pouco.",
             "O Harry desenhou um cabide na espuma. Esse homem merece um prêmio."],
    "bar": ["Noonan's no sábado é tradição. O Marco já sabe: gim-tônica com pepino.",
            "Eu fico observando o que as pessoas vestem pra sair. É pesquisa de campo. Juro."],
    "city": ["O vento da orla bagunça qualquer penteado. Por isso eu trouxe a boina.",
             "Daqui da praia eu imagino a passarela: mar de fundo, luz dourada, e todo mundo descalço."],
    "t0": ["Roupa boa é a que faz você esquecer que está vestida. A não ser que seja um vestido de gala. Aí você "
           "lembra o tempo todo, e tudo bem.",
           "Meu avô era alfaiate em Lyon, numa salinha em cima de uma padaria. Foi ele que me ensinou a medir duas vezes e cortar uma."],
    "t3": ["Separei um lenço que é a sua cara. Não vou te obrigar a levar. Vou só deixar ele perto do caixa.",
           "Você é a única cliente que pergunta como eu estou antes de perguntar o preço.",
           "Às vezes me escapa um \"chérie\". Desculpa, é o sotaque. Ele só aparece com quem eu gosto.",
           "Lyon é a cidade da seda, sabia? Os italianos discordam. Eu sorrio e não discuto."],
    "t6": ["Sabe que eu desenho pensando em você às vezes? Profissionalmente. Você tem postura de capa de revista.",
           "Se a minha coleção sair um dia, a primeira peça vai ter o seu nome. Já decidi."],
}
dialogue.BUSY["celeste"] = ["Agora não dá, querida, tem cliente no provador! Volta daqui a pouco.",
                            "Tô no meio de uma bainha. Mais tarde a gente conversa!"]
dialogue.REACTIVE += [
    ("celeste", lambda g: len(g.closet.get("acc", [])) >= 3,
     "Três acessórios! Agora você tem uma coleção. Daqui a pouco abre uma loja concorrente."),
    ("celeste", lambda g: g.dating is not None,
     "Namorando, é? Vem cá que eu já sei o que você vai usar no próximo encontro."),
    ("celeste", lambda g: "assinatura" in g.closet.get("owned", []) and g.closet.get("cur") != "assinatura",
     "E o meu vestido roxo? Não deixa ele parado no closet, vestido gosta de passear."),
]

from .falas import MAIS as _MAIS                      # falas extras da Celeste (falas.py)
for _cat, _lst in _MAIS.get("celeste", {}).items():
    _pool = dialogue.LINES["celeste"].setdefault(_cat, [])
    _pool.extend(ln for ln in _lst if ln not in _pool)

festas.BIRTHDAYS["celeste"] = (1, 6)
festas.BDAY_CHAT["celeste"] = ("Hoje é meu aniversário! Minha mãe ligou de Lyon às seis da manhã para cantar "
                               "parabéns. Em francês, no horário de lá. Eu ainda estava dormindo.")
gifts.DISLIKE_LINES["celeste"] = ("Isso estava no chão? Querida, nem a moda vintage aceita isso.",
                                  "Hm. Não é bem o meu estilo. Mas a intenção foi linda.")

eventos.TITLES["celeste_4"] = "Celeste: o caderno de croquis"
SCENES["celeste_4"] = dict(map="boutique", time=19 * 60, npc="celeste", steps=[
    ("ator", "celeste", 12, 4, "down"), ("ator", "player", 8, 10, "up"),
    ("camera_ja", 10, 6), ("fade_in",),
    ("legenda", "La Boutique, hora de fechar", 1.8),
    ("andar", "player", 8, 7), ("andar", "player", 12, 7), ("andar", "player", 12, 6), ("virar", "player", "up"),
    ("fala", "celeste", "Letícia! Eu ia virar a plaquinha para FECHADO, mas para você a loja abre de novo."),
    ("narra", "Em cima do balcão, um caderno de capa preta está aberto. As páginas estão cheias de croquis: "
              "vestidos, casacos e uma bolsa com o fecho em forma de cabide."),
    ("fala", "player", "Isso é seu? São lindos."),
    ("fala", "celeste", "São ideias. Faz dez anos que eu desenho uma coleção que nunca saiu do caderno.", "shy"),
    ("fala", "celeste", "Em Milão eu costurava para os outros. Aqui eu vendo o que os outros costuram. "
                        "Um dia vai ter uma etiqueta escrito Celeste Waite."),
    ("emote", "player", "brilho"),
    ("escolha", "O que dizer?", [
        ("Esse dia pode chegar antes do que você pensa. Eu conheço gente que investe em sonho.", 70,
         "Você está falando sério? Não, não responde agora. Eu vou chorar em cima do croqui."),
        ("O vestido roxo do manequim é daqui, não é? Dá para ver.", 60,
         "É o primeiro da coleção. Você reparou! Ninguém repara."),
        ("Dez anos é muito tempo para guardar uma coisa boa.", 45,
         "É. Acho que eu tinha medo de alguém dizer que era feio. Você não disse."),
    ]),
    ("fala", "celeste", "Sabe o que eu decidi? Cliente que olha o meu caderno desse jeito vira VIP. "
                        "Vinte por cento em tudo, para sempre.", "happy"),
    ("emote", "celeste", "coracao"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])
NPCS["celeste"]["events"].update({
    2: dict(gift="lenco_seda",
            lines=["Toma, esse lenço de seda é seu. Separei porque combina com os seus olhos.",
                   "Não precisa pagar. Considera um investimento: cliente bem vestida faz propaganda."]),
    4: dict(scene="celeste_4", flag=DISCOUNT_FLAG,
            lines=["Cliente VIP é cliente VIP. Vinte por cento, sem discussão."]),
    6: dict(lines=["Fiz uma coisa para você. Chega hoje à noite na cobertura.",
                   "Não abre antes do jantar. Tá, pode abrir. Mas me conta depois."]),
    8: dict(lines=["Fiz as contas: se eu vender mais cinquenta bolsas, faço o desfile na orla.",
                   "Primeira fila, do lado da minha mãe, que vem da França só para isso. Você vai, né?"]),
})


# ===========================================================================
# Desfile da Celeste no píer (evento de 8 corações)
# ===========================================================================
NEW_LOOKS["passarela"] = ("Vestido da passarela", None,
                          dict(outfit="dress", cloth=(238, 226, 250), accent=(150, 90, 220)),
                          "O vestido lilás do primeiro desfile da Celeste, com o seu nome bordado na etiqueta.")
closet.LOOKS["passarela"] = NEW_LOOKS["passarela"]
closet.ORDER[:] = list(closet.LOOKS)
closet.GENERIC["passarela"] = ["É o vestido do desfile! Eu vi as fotos do Barry.", "Lilás de passarela. Perfeito."]
closet.SPECIAL.setdefault("celeste", {})["passarela"] = "Primeira peça da coleção, na primeira modelo. Eu choro toda vez."
FLAG_LABELS["celeste_desfile"] = "Desfile da Celeste no píer! O vestido da passarela chega hoje à noite."
eventos.TITLES["celeste_8"] = "Celeste: o desfile no píer"


def runway_comment(g, key):
    """O que a personagem diz quando a Letícia desfila com a roupa (e os acessórios) de agora."""
    cur = g.closet.get("cur")
    line = closet.SPECIAL.get(key, {}).get(cur)
    if not line and cur in closet.GENERIC:
        line = random.choice(closet.GENERIC[cur])
    if not line:
        worn = list(g.closet.get("worn", {}).values())
        if worn:
            a = random.choice(worn)
            line = ACC_SPECIAL.get(key, {}).get(a) or random.choice(ACC_LINES.get(a, ["Que acessório!"]))
    return line or random.choice(["Ela nasceu para isso!", "Que elegância. Até o mar parou para olhar.",
                                  "Uau. Só uau."])


SCENES["celeste_8"] = dict(map="city", time=17 * 60 + 30, npc="celeste", steps=[
    ("ator", "celeste", 59, 56, "right"), ("ator", "player", 60, 54, "down"),
    ("ator", "lucy", 57, 57, "right"), ("ator", "nia", 57, 59, "right"), ("ator", "barry", 58, 60, "up"),
    ("ator", "vittoria", 63, 57, "left"), ("ator", "jess", 63, 59, "left"), ("ator", "sam", 62, 60, "up"),
    ("camera_ja", 60, 58), ("fade_in",),
    ("legenda", "No píer, ao pôr do sol: o desfile da Celeste", 2.2),
    ("fala", "celeste", "Senhoras e senhores... e Seu Joca, que está pescando ali no fim do píer..."),
    ("fala", "celeste", "Bem-vindos ao primeiro desfile Celeste Waite! A passarela é o píer, a luz é o pôr do sol "
                        "e a trilha sonora são as gaivotas.", "happy"),
    ("fala", "celeste", "Abrindo o desfile, a mulher mais bem vestida de National City: Letícia Luthor!"),
    ("efeito", "brilhos", 1.0),
    ("andar", "player", 60, 62),
    ("virar", "player", "up"),
    ("acenar", "player"),
    ("emote", "barry", "exclamacao"),
    ("fala", "barry", "Segura essa pose! Isso! Isso é capa da CatCo!", "happy"),
    ("comenta_look", "lucy"),
    ("comenta_look", "vittoria"),
    ("emote", "jess", "estrela"),
    ("comenta_look", "jess"),
    ("andar", "player", 60, 56),
    ("virar", "player", "left"), ("virar", "celeste", "right"),
    ("fala", "celeste", "Você foi perfeita. Dez anos de caderno e hoje ele saiu andando pelo píer.", "love"),
    ("escolha", "O que dizer?", [
        ("A coleção é sua. Eu só tive a sorte de vestir primeiro.", 80,
         "Para com isso, que eu tô de rímel. Mas obrigada. De verdade."),
        ("Ano que vem a gente faz na orla inteira. Com telão.", 60,
         "Com telão! E com o Marco servindo drinque com nome de vestido. Anotei."),
        ("Meus pés estão me odiando, mas valeu cada passo.", 40,
         "Ninguém disse que moda era confortável. Disseram que era linda. E foi."),
    ]),
    ("fala", "celeste", "Vou mandar para a cobertura a primeira peça da coleção. Feita sob medida, com o seu nome "
                        "na etiqueta.", "happy"),
    ("emote", "celeste", "coracao"),
    ("efeito", "brilhos", 1.4),
    ("esperar", 0.8), ("fade_out",),
])
NPCS["celeste"]["events"][8] = dict(
    scene="celeste_8", flag="celeste_desfile", mood="love",
    lines=["Ainda estou flutuando por causa do desfile. As fotos do Barry ficaram absurdas.",
           "O vestido lilás chega hoje à noite. Usa com orgulho: você foi a primeira modelo da Celeste Waite."])


def night(g, notes):
    """Depois do desfile, o vestido da passarela chega na cobertura."""
    if "celeste_desfile" in g.flags and "passarela" not in g.closet["owned"]:
        g.closet["owned"].append("passarela")
        notes.append(("Chegou uma caixa lilás da Celeste: o vestido da passarela, com o seu nome na etiqueta. "
                      "(Está no closet.)", C_PINK))

"""Lugares com mais vida: CatCo, Gruppo Ricci, Conti Moretti, portarias e saguão da sede.

- CatCo: estúdio da CatCo TV na antiga sala de vidro (painel, câmera, refletores e duas poltronas). Na câmera dá
  para dar uma entrevista ao vivo (1x por semana, dias úteis das 9h às 18h, três assuntos com efeitos diferentes)
  e comprar um anúncio ($400: produtos +15% por 3 noites). O arquivo da redação tem matérias antigas sobre a
  cidade (uma por dia).
- Mesas de trabalho com o monitor de costas (`desk_r`, `desk_news`): quem trabalha senta atrás delas.
- Sala de degustação do Gruppo Ricci: adega, barris e mesa de prova.
- Leitos ocupados no Conti Moretti (o leito em que a Letícia acorda fica sempre livre).
- Portarias: balcão de madeira com campainha (`balcao_portaria`), caixas de correio e vitrine de produtos na sede.

Estado em `g.catco` (init_state / save_state / load_state). Ganchos em `Game`: object_label, use_object,
object_image, sell_value e process_night.
"""
import math
import random

import pygame

from . import art, world, audio, ui, lighting, habilidades
from .art import new, R, P, shade
from .config import C_GREEN, C_GOLD, C_MUTED

GOLD = (214, 172, 82)
CATCO_RED = (206, 52, 62)


# ---------------------------------------------------------------------------
# Arte
# ---------------------------------------------------------------------------
def _mon_back(s, x, y, w=12, h=9):
    """Monitor visto por trás (quem usa está do outro lado da mesa)."""
    R(s, (32, 32, 42), x, y, w, h)
    R(s, (56, 56, 70), x + 1, y + 1, w - 2, h - 2)
    for yy in range(y + 2, y + h - 2, 2):
        R(s, (46, 46, 58), x + 2, yy, w - 4, 1)
    R(s, (150, 150, 168), x + w // 2 - 1, y + h // 2, 2, 1)          # logo da marca
    R(s, (40, 40, 52), x + w // 2 - 1, y + h, 2, 2)                  # pé


def _desk_r():
    s = art._desk((120, 84, 56), with_pc=False)
    _mon_back(s, 16, 0, 16, 11)
    R(s, (240, 240, 246), 3, 8, 8, 4); R(s, (220, 220, 230), 4, 9, 6, 1)    # papéis
    R(s, (120, 40, 190), 39, 8, 3, 4); P(s, (160, 90, 220), 39, 8)           # caneca
    R(s, (90, 160, 90), 35, 9, 2, 3)                                          # planta pequena
    return s


def _desk_news():
    s = new(32, 28)
    R(s, (200, 200, 210), 0, 12, 32, 16)
    R(s, (230, 230, 236), 0, 12, 32, 3)
    R(s, (150, 150, 160), 2, 18, 28, 1)
    R(s, (176, 176, 188), 3, 20, 10, 6); R(s, (150, 150, 162), 7, 22, 2, 1)   # gaveteiro
    _mon_back(s, 17, 2, 12, 9)
    R(s, (240, 240, 246), 3, 8, 9, 5); R(s, CATCO_RED, 4, 9, 7, 1)            # rascunhos
    R(s, (250, 220, 90), 12, 7, 3, 3)                                          # post-it
    R(s, (240, 240, 246), 13, 11, 3, 2); P(s, (110, 70, 50), 14, 11)          # xícara de café
    return s


def _painel_catco():
    """Cenário do CatCo ao Vivo: skyline de National City, faixa vermelha e a luz de 'no ar'."""
    s = new(48, 24)
    R(s, (30, 34, 54), 0, 0, 48, 24)
    R(s, (44, 52, 86), 1, 1, 46, 14)
    r = random.Random(7)
    x = 2
    while x < 46:
        w = r.randint(3, 5)
        h = r.randint(4, 11)
        R(s, (24, 28, 46), x, 15 - h, w, h)
        for wy in range(15 - h + 1, 14, 2):
            if r.random() < 0.5:
                P(s, (252, 222, 136), x + 1, wy)
        x += w + 1
    R(s, CATCO_RED, 0, 15, 48, 5)
    R(s, shade(CATCO_RED, 1.2), 0, 15, 48, 1)
    for i, cx in enumerate(range(4, 44, 5)):                                    # "CATCO" estilizado
        R(s, (250, 250, 252), cx, 17, 3, 1)
    R(s, (20, 20, 30), 0, 20, 48, 4)
    pygame.draw.circle(s, CATCO_RED, (43, 5), 3)                               # no ar
    P(s, (255, 170, 170), 42, 4)
    return s


def _camera_estudio():
    s = new(16, 30)
    leg = (60, 60, 70)
    pygame.draw.line(s, leg, (8, 16), (2, 29)); pygame.draw.line(s, leg, (8, 16), (14, 29))
    pygame.draw.line(s, leg, (8, 16), (8, 29))
    R(s, (40, 40, 48), 6, 14, 4, 3)
    R(s, (36, 36, 44), 2, 4, 12, 10)                                           # corpo
    R(s, (58, 58, 70), 3, 5, 10, 3)
    R(s, (90, 170, 230), 4, 8, 7, 5); R(s, (160, 210, 250), 5, 9, 3, 1)       # visor virado para quem filma
    R(s, (24, 24, 30), 5, 1, 6, 3)                                             # lente (para o cenário)
    P(s, CATCO_RED, 12, 5)                                                     # luz de gravação
    return s


def _refletor():
    s = new(16, 32)
    R(s, (70, 70, 80), 7, 14, 2, 16)
    pygame.draw.line(s, (70, 70, 80), (8, 29), (3, 31)); pygame.draw.line(s, (70, 70, 80), (8, 29), (13, 31))
    R(s, (40, 40, 48), 1, 2, 14, 12)
    R(s, (250, 246, 230), 2, 3, 12, 10)
    R(s, (255, 255, 248), 4, 5, 8, 6)
    R(s, (30, 30, 36), 1, 13, 14, 1)
    return s


def _arquivo_catco():
    s = new(32, 28)
    metal = (150, 156, 170)
    for x0 in (0, 16):
        R(s, metal, x0 + 1, 6, 14, 22)
        R(s, shade(metal, 1.15), x0 + 1, 6, 14, 1)
        for i, y in enumerate((8, 15, 22)):
            R(s, shade(metal, 0.86), x0 + 2, y, 12, 6)
            R(s, (240, 236, 210), x0 + 5, y + 1, 6, 2)                         # etiqueta
            R(s, (90, 92, 104), x0 + 7, y + 4, 2, 1)                           # puxador
    for i, y in enumerate((0, 2, 4)):                                           # pilha de jornais antigos
        R(s, (232, 226, 206), 3 + i, y, 12, 2)
        R(s, (180, 172, 150), 3 + i, y + 1, 12, 1)
    R(s, CATCO_RED, 20, 2, 8, 4); R(s, (250, 250, 252), 21, 3, 6, 1)           # caixa da CatCo
    return s


def _adega():
    """Adega de parede em losangos, com o topo em arco e garrafas deitadas."""
    s = new(48, 36)
    wood = (92, 52, 36)
    R(s, wood, 0, 4, 48, 32)
    pygame.draw.ellipse(s, wood, (0, 0, 48, 12))
    R(s, shade(wood, 1.25), 2, 4, 44, 1)
    R(s, (50, 26, 20), 3, 6, 42, 26)
    for i in range(-30, 48, 7):                                                 # treliça em losango
        pygame.draw.line(s, shade(wood, 1.1), (3 + i, 6), (3 + i + 26, 32))
        pygame.draw.line(s, shade(wood, 1.1), (3 + i + 26, 6), (3 + i, 32))
    s.set_clip(None)
    r = random.Random(11)
    for y in range(9, 30, 5):
        for x in range(6, 44, 6):
            if r.random() < 0.8:
                c = r.choice([(70, 20, 34), (60, 70, 30), (90, 30, 44), (200, 180, 120)])
                pygame.draw.circle(s, c, (x, y), 2)
                P(s, shade(c, 1.6), x - 1, y - 1)
    R(s, wood, 0, 4, 3, 32); R(s, wood, 45, 4, 3, 32)                          # laterais por cima da treliça
    R(s, shade(wood, 0.7), 0, 32, 48, 4)
    R(s, GOLD, 21, 1, 6, 2)                                                    # plaquinha "Ricci"
    return s


def _barril():
    """Barril de carvalho em pé, barrigudo, com aros de ferro e uma torneirinha."""
    s = new(16, 22)
    oak = (150, 96, 54)
    for y in range(4, 21):
        half = 5 + round(2 * math.sin(math.pi * (y - 4) / 16))
        R(s, shade(oak, 0.72), 8 - half, y, half * 2, 1)
        R(s, oak, 9 - half, y, half * 2 - 2, 1)
        R(s, shade(oak, 1.15), 10 - half, y, 2, 1)                             # brilho na lateral
        for x in range(9 - half + 3, 7 + half, 3):                              # aduelas
            P(s, shade(oak, 0.86), x, y)
    for y in (6, 12, 18):                                                       # aros de ferro
        half = 5 + round(2 * math.sin(math.pi * (y - 4) / 16))
        R(s, (72, 66, 70), 8 - half, y, half * 2, 1)
        P(s, (130, 126, 130), 9 - half, y)
    pygame.draw.ellipse(s, shade(oak, 0.72), (3, 1, 10, 6))
    pygame.draw.ellipse(s, shade(oak, 1.2), (4, 2, 8, 4))
    R(s, (72, 66, 70), 3, 3, 1, 2); R(s, (72, 66, 70), 12, 3, 1, 2)
    R(s, (60, 60, 66), 7, 13, 3, 2); R(s, (90, 30, 44), 8, 15, 1, 1)           # torneirinha e uma gota de vinho
    return s


def _caixas_correio():
    s = new(48, 20)
    brass = (196, 160, 90)
    R(s, (90, 64, 44), 0, 0, 48, 20)
    R(s, shade((90, 64, 44), 1.2), 0, 0, 48, 1)
    for row in range(3):
        for col in range(7):
            x, y = 2 + col * 6 + (col // 4) * 2, 2 + row * 6
            if x + 5 > 46:
                continue
            R(s, brass, x, y, 5, 5)
            R(s, shade(brass, 0.8), x, y + 4, 5, 1)
            R(s, (40, 30, 24), x + 1, y + 1, 3, 1)                              # fresta
            P(s, (250, 240, 200), x + 2, y + 3)
    P(s, (255, 120, 150), 9, 10)                                               # adesivo de gatinho
    return s


def _balcao_portaria():
    s = new(48, 28)
    wood = (120, 78, 50)
    R(s, wood, 0, 8, 48, 20)
    R(s, shade(wood, 0.8), 0, 26, 48, 2)
    for x0 in (3, 18, 33):
        R(s, shade(wood, 0.88), x0, 13, 12, 10)
        R(s, shade(wood, 1.1), x0, 13, 12, 1)
    R(s, (232, 228, 236), 0, 5, 48, 4)                                         # tampo de mármore
    R(s, (250, 248, 252), 0, 5, 48, 1)
    R(s, (240, 236, 220), 6, 2, 10, 4); R(s, (150, 60, 60), 6, 2, 1, 4)        # livro de visitas
    R(s, (200, 200, 210), 6, 3, 9, 1)
    pygame.draw.circle(s, GOLD, (30, 4), 3); R(s, GOLD, 29, 0, 2, 2)           # campainha
    R(s, (60, 60, 70), 28, 6, 5, 1)
    R(s, (60, 50, 60), 39, 0, 2, 6); R(s, (246, 226, 176), 36, 0, 8, 3)        # abajur
    return s


def _vitrine_luthor():
    """Vitrine de produtos da Luthor Corp no saguão da sede."""
    s = new(32, 32)
    R(s, (60, 40, 80), 1, 22, 30, 10)
    R(s, (120, 40, 190), 1, 24, 30, 2)
    R(s, (190, 230, 246), 2, 2, 28, 20)
    R(s, (220, 244, 252), 3, 3, 26, 1)
    R(s, (230, 230, 240), 2, 12, 28, 1)                                        # prateleira de vidro
    R(s, (70, 70, 84), 5, 7, 6, 5); R(s, (150, 230, 160), 6, 8, 4, 2)          # dispositivo
    R(s, (200, 200, 214), 14, 6, 4, 6); P(s, (120, 40, 190), 15, 7)            # frasco
    R(s, (40, 40, 52), 21, 8, 7, 4); R(s, (120, 200, 255), 22, 9, 5, 2)        # tablet
    R(s, (230, 190, 90), 6, 17, 5, 5); R(s, (120, 40, 190), 15, 16, 4, 6)
    R(s, (90, 90, 104), 22, 18, 6, 4); P(s, (255, 90, 90), 23, 19)
    R(s, (150, 120, 190), 1, 1, 30, 1); R(s, (150, 120, 190), 1, 1, 1, 22); R(s, (150, 120, 190), 30, 1, 1, 22)
    return s


# leitos ocupados: o paciente com a cabeça no travesseiro e o cobertor puxado
_SKINS = [(250, 222, 200), (236, 196, 160), (210, 160, 120), (170, 120, 86), (130, 86, 60)]
_HAIRS = [(30, 22, 20), (70, 44, 30), (120, 80, 50), (200, 160, 90), (90, 90, 96), (230, 230, 236)]


def _hbed_paciente(seed):
    return art.cached(("hbed_paciente", seed), lambda: art.up(_draw_paciente(seed)))


def _draw_paciente(seed):
    from .hospital import _hbed
    s = _hbed()
    r = random.Random(seed)
    skin, hair = r.choice(_SKINS), r.choice(_HAIRS)
    blanket = r.choice([(120, 190, 170), (150, 180, 220), (210, 200, 230)])
    R(s, hair, 4, 5, 8, 5)                                                     # cabeça no travesseiro
    R(s, skin, 5, 7, 6, 5)
    R(s, hair, 4, 6, 1, 4); R(s, hair, 11, 6, 1, 4)
    R(s, shade(skin, 0.7), 6, 9, 1, 1); R(s, shade(skin, 0.7), 9, 9, 1, 1)     # olhos fechados
    R(s, blanket, 2, 12, 12, 15)
    R(s, shade(blanket, 1.15), 2, 12, 12, 2)
    R(s, shade(blanket, 0.85), 4, 16, 8, 9)                                    # corpo debaixo do cobertor
    R(s, skin, 3, 14, 2, 4); R(s, skin, 11, 14, 2, 4)                          # braços por cima
    R(s, (250, 250, 252), 4, 13, 8, 1)
    return s


art.OBJECT_BUILDERS.update({
    "desk_r": _desk_r, "desk_news": _desk_news, "painel_catco": _painel_catco, "camera_estudio": _camera_estudio,
    "refletor": _refletor, "arquivo_catco": _arquivo_catco, "adega": _adega, "barril": _barril,
    "caixas_correio": _caixas_correio, "balcao_portaria": _balcao_portaria, "vitrine_luthor": _vitrine_luthor,
})
world.OBJECT_DEFS.update({
    "desk_r": (3, 1, True, "obj"), "painel_catco": (3, 1, False, "wall"), "camera_estudio": (1, 1, True, "obj"),
    "refletor": (1, 1, True, "obj"), "arquivo_catco": (2, 1, True, "obj"), "adega": (3, 1, True, "obj"),
    "barril": (1, 1, True, "obj"), "caixas_correio": (3, 1, False, "wall"), "balcao_portaria": (3, 1, True, "obj"),
    "vitrine_luthor": (2, 1, True, "obj"),
})
world.COUNTERS |= {"desk_r", "balcao_portaria"}
lighting.EMITTERS["refletor"] = ((255, 246, 220), 1.3)
lighting.EMITTERS["painel_catco"] = ((150, 160, 230), 1.0)
lighting.EMITTERS["vitrine_luthor"] = ((200, 220, 255), 1.0)

FLAVOR = {
    "desk_r": "Uma mesa de trabalho arrumada, com o monitor virado para quem senta atrás dela.",
    "painel_catco": "O cenário do CatCo ao Vivo, o programa de entrevistas da CatCo TV. A luz vermelha acende quando "
                    "a câmera grava.",
    "refletor": "Luz de estúdio. Deixa todo mundo com cara de quem dormiu oito horas.",
    "adega": "A adega da sala de degustação: Chianti, Barolo e um Brunello guardado \"para uma ocasião especial\". "
             "Ninguém sabe qual.",
    "barril": "Barris de carvalho da vinícola parceira dos Ricci. Cheiro de madeira e de uva.",
    "caixas_correio": "As caixas de correio dos moradores. Uma delas tem um adesivo de gatinho.",
    "balcao_portaria": "O balcão da portaria: livro de visitas, a campainha e as chaves reserva bem guardadas.",
    "vitrine_luthor": "Os produtos lançados pela Luthor Corp, com plaquinhas escritas à mão pela Jess.",
}
# textos por lugar (a mesma mesa diz coisas diferentes em cada prédio)
PLACE_LOOK = {
    ("ricci", "desk_r"): "A recepção do Gruppo Ricci: a agenda dos fornecedores, cardápios novos para aprovar e um "
                         "vaso de lírios.",
    ("marina", "desk_r"): "A mesa do Ian: cartas náuticas, a escala dos barcos e um café que esfriou faz tempo.",
}
NEWS_DESK = [
    "Rascunhos de matérias, post-its e três xícaras de café frias.",
    "Uma pauta riscada três vezes. Na margem: \"perguntar para a Letícia?\".",
    "Uma foto do Barry presa no monitor: o píer ao pôr do sol. Embaixo, \"capa?\".",
    "Recortes de jornal, um grampeador sem grampos e uma lista de fontes escrita em código.",
]
PATIENTS = [
    "Um paciente em observação, dormindo tranquilo. A enfermagem passa de hora em hora.",
    "Uma senhora se recuperando de uma cirurgia no joelho. Ela acena e volta a fazer as palavras cruzadas.",
    "Um rapaz com o braço engessado, assistindo a um jogo no celular sem som.",
    "Paciente descansando. Na mesinha, um cartão escrito \"melhoras, vô!\" com desenhos de giz de cera.",
    "Alguém dormindo com o soro no braço. O monitor faz um bipe calmo e compassado.",
]

# matérias antigas do arquivo da CatCo (uma por dia, em ordem)
ARTICLES = [
    ("Um laboratório na garagem",
     "Alexander Luthor abre um pequeno laboratório num galpão perto do porto. \"Quero inventar coisas que as "
     "pessoas usem na terça-feira, não só em feiras de tecnologia.\" Nascia a Luthor Corp."),
    ("CatCo chega a National City",
     "Cat Grant compra um jornal quase falido e o rebatiza de CatCo. No primeiro editorial: \"Notícia boa é notícia "
     "verdadeira. E rápida.\""),
    ("O farol volta a acender",
     "Depois de dez anos apagado, o farol do Jardim do Mirante é restaurado pelos moradores. A cidade inteira vai "
     "até a orla ver a primeira volta da luz."),
    ("Uma trattoria no calçadão",
     "Depois de anos trabalhando em restaurantes dos outros, Vittoria Ricci abre a própria casa. Na cozinha, uma "
     "chef brasileira de mão firme: Dona Graça. A fila dobra a esquina na primeira semana."),
    ("Conti Moretti ganha a ala nova",
     "O Conti Moretti Hospitais inaugura doze especialidades e uma ala de internação. A direção promete "
     "\"medicina de ponta com cara de casa\"."),
    ("A nova presidente da Luthor Corp",
     "Após a morte de Alexander Luthor, a filha, Letícia, assume a presidência. Primeira decisão: reabrir o "
     "laboratório para projetos pequenos. \"Menos discurso, mais bancada.\""),
    ("Marina Luthor zarpa",
     "A Luthor Corp cria uma divisão náutica e chama Ian, amigo de infância da CEO, para dirigir a marina. Os "
     "pescadores do píer aprovam: \"Pelo menos ele sabe dar nó.\""),
    ("O melhor café da costa",
     "O Grão Nobre vence o concurso regional de barismo. O campeão, Harry, recusa a entrevista: \"Tem fila.\""),
    ("Noonan's, o pub mais antigo",
     "O Noonan's completa cinquenta anos com a mesma jukebox e, segundo os clientes, o mesmo amendoim."),
    ("Cine National reabre",
     "O cinema do centro reabre com poltronas novas, pipoca de verdade e uma sessão de clássicos às quartas."),
    ("O Gruppo Ricci compra o banco",
     "O prédio do antigo banco do centro vira a sede do Gruppo Ricci. No cofre, agora, só vinho e receitas."),
    ("La Boutique abre as portas",
     "Celeste Waite volta a National City e abre La Boutique entre o Grão Nobre e a CatCo. \"Roupa boa é a que "
     "faz você andar diferente.\""),
]

TOPICS = [
    ("Os produtos da Luthor Corp", "A LCORP deve subir amanhã."),
    ("A Fundação Luthor e a cidade", "+25 de amizade com todo mundo."),
    ("Bastidores, com a Lucy, a Nia e o Barry", "+60 de amizade com a Lucy, a Nia e o Barry."),
]
INTERVIEW_ENERGY = 15
AD_PRICE = 400
AD_DAYS = 3
AD_BONUS = 0.15


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.catco = dict(interview=-99, boost=False, ad_until=-1, read=[], read_day=-1, interviews=0)


def save_state(g):
    return {"catco": dict(g.catco)}


def load_state(g, d):
    init_state(g)
    for k, v in (d.get("catco") or {}).items():
        if k in g.catco:
            g.catco[k] = v


def ad_active(g):
    return g.abs_day() <= g.catco.get("ad_until", -1)


def sell_mult(g, item):
    from .data import ITEMS
    if ad_active(g) and ITEMS[item]["kind"] == "product":
        return 1 + AD_BONUS
    return 1.0


def night(g, notes):
    if g.catco.get("boost"):
        g.catco["boost"] = False
        g.stock = round(g.stock + 1.5, 2)
        notes.append(("A entrevista na CatCo TV animou o mercado: LCORP +$1,50.", C_GREEN))
    if g.catco.get("ad_until", -1) == g.abs_day() - 1:     # a noite já virou o dia
        notes.append(("O anúncio da Luthor Corp na CatCo saiu do ar.", C_MUTED))


def hud_lines(g):
    if ad_active(g):
        return [("Anúncio na CatCo no ar: produtos +15%", (120, 200, 255))]
    return []


# ---------------------------------------------------------------------------
# Hospital: leitos ocupados
# ---------------------------------------------------------------------------
def bed_patient(g, o):
    """Semente do paciente do leito (None = leito vazio). O leito da Letícia (HOSPITAL_BED) fica sempre livre."""
    if o.kind != "hbed" or o.x == world.HOSPITAL_BED[0]:
        return None
    day = g.abs_day() // 2                # o mesmo paciente fica dois dias
    if random.Random(f"leito{day}-{o.x}").random() < 0.3:
        return None
    return day * 31 + o.x


def object_image(g, o):
    if o.kind == "hbed":
        seed = bed_patient(g, o)
        if seed is not None:
            return _hbed_paciente(seed)
    return None


# ---------------------------------------------------------------------------
# Interação
# ---------------------------------------------------------------------------
def object_label(g, o):
    k = o.kind
    if k == "camera_estudio":
        return "Estúdio CatCo TV"
    if k == "arquivo_catco":
        return "Arquivo da CatCo"
    if k == "hbed" and bed_patient(g, o) is not None:
        return "Paciente"
    return None


def use_object(g, o):
    k = o.kind
    if k == "camera_estudio":
        _studio(g)
        return True
    if k == "arquivo_catco":
        _archive(g)
        return True
    if k == "hbed" and bed_patient(g, o) is not None:
        g.say(PATIENTS[bed_patient(g, o) % len(PATIENTS)])
        return True
    if k == "desk_news":
        g.say(NEWS_DESK[(o.x * 7 + o.y + g.abs_day()) % len(NEWS_DESK)])
        return True
    txt = PLACE_LOOK.get((g.map_name, k))
    if txt:
        g.say(txt)
        return True
    return False


def _host(g):
    """Quem apresenta: a Lucy se ela estiver na redação, senão a Nia, senão a equipe da CatCo TV."""
    for key in ("lucy", "nia"):
        n = g.npcs.get(key)
        if n and n.map == "catco":
            return key, n.data["short"]
    return None, "CatCo TV"


def _studio(g):
    audio.sfx("confirm")
    opts = ["Dar uma entrevista ao vivo", f"Anunciar os produtos (${AD_PRICE}, {AD_DAYS} noites)", "Sair"]
    g.push(ui.Choice("Estúdio da CatCo TV. O que você quer fazer?", opts, lambda i: _studio_pick(g, i)))


def _studio_pick(g, i):
    if i == 0:
        if g.weekday >= 5 or not (9 * 60 <= g.minutes < 18 * 60):
            g.say("O CatCo ao Vivo só grava em dias úteis, das 9h às 18h.", "CatCo TV")
            return
        wait = 7 - (g.abs_day() - g.catco["interview"])
        if wait > 0:
            g.say(f"A agenda do programa está cheia. Próxima entrevista: daqui a {wait} dia(s).", "CatCo TV")
            return
        if g.energy < INTERVIEW_ENERGY:
            g.say("Você está cansada demais para encarar as câmeras hoje.")
            return
        g.push(ui.Choice("Sobre o que você quer falar?", [t[0] for t in TOPICS] + ["Deixa para outro dia"],
                         lambda j: _interview(g, j) if j < len(TOPICS) else None))
    elif i == 1:
        if ad_active(g):
            left = g.catco["ad_until"] - g.abs_day() + 1
            g.say(f"O anúncio da Luthor Corp já está no ar (mais {left} noite(s)).", "CatCo TV")
        elif g.money < AD_PRICE:
            g.say(f"Um anúncio custa ${AD_PRICE}. Falta dinheiro.", "CatCo TV")
        else:
            g.money -= AD_PRICE
            g.catco["ad_until"] = g.abs_day() + AD_DAYS - 1
            audio.sfx("buy")
            g.toasts.push(f"Anúncio no ar por {AD_DAYS} noites: produtos valem +15%.", C_GOLD)


INTERVIEW_LINES = [
    ["Boa tarde, National City! Hoje no CatCo ao Vivo: Letícia Luthor.",
     "Os produtos da Luthor Corp estão em todo lugar. Qual é o segredo?",
     "Letícia: \"Fazer coisas que as pessoas usam na terça-feira, não só em feiras de tecnologia.\"",
     "E aí está: a CEO mais ocupada da cidade, de bom humor. Voltamos depois do intervalo!"],
    ["Hoje no CatCo ao Vivo: a Fundação Luthor e o que ela está mudando na cidade.",
     "Letícia: \"A cidade me deu tudo. A Fundação é só a gente devolvendo um pouco.\"",
     "O telefone da redação não para de tocar: gente querendo ajudar. Obrigada, National City!"],
    ["Programa especial: um dia na redação da CatCo, com uma convidada de peso.",
     "A Nia mostra o sistema da mesa dela, o Barry tira fotos de tudo e a Lucy finge que não está rindo.",
     "Letícia: \"Eu só vim dar uma entrevista. Agora sei onde fica o café bom daqui.\"",
     "Bastidores no ar. A audiência adorou!"],
]


def _interview(g, j):
    host_key, host = _host(g)
    g.catco["interview"] = g.abs_day()
    g.catco["interviews"] = g.catco.get("interviews", 0) + 1
    g.energy = max(0, g.energy - INTERVIEW_ENERGY)
    if j == 0:
        g.catco["boost"] = True
    elif j == 1:
        for k in g.npcs:
            g.add_friendship(k, 25)
    else:
        for k in ("lucy", "nia", "barry"):
            if k in g.npcs:
                g.add_friendship(k, 60)
    habilidades.gain(g, "carisma", 30)
    audio.sfx("reward")
    portrait = g.portrait_for(g.npcs[host_key], "happy") if host_key else None
    g.push(ui.Dialog(host, list(INTERVIEW_LINES[j]), portrait, subtitle="CatCo ao Vivo"))
    g.toasts.push("Entrevista no ar! " + TOPICS[j][1], C_GREEN)


def _archive(g):
    day = g.abs_day()
    if g.catco.get("read_day") == day:
        g.say("Você já leu uma matéria antiga hoje. O arquivista pediu, educadamente, para voltar amanhã.")
        return
    read = g.catco.setdefault("read", [])
    left = [i for i in range(len(ARTICLES)) if i not in read]
    if not left:                                    # matérias antigas lidas: agora aparecem as sobre ela
        from . import noticias
        n = noticias.archive_pick(g)
        if n:
            g.catco["read_day"] = day
            audio.sfx("page")
            g.push(ui.Dialog("Arquivo da CatCo", [f"Recorte guardado: \"{n['title']}\"", n["text"]]))
            return
    idx = left[0] if left else random.randrange(len(ARTICLES))
    title, text = ARTICLES[idx]
    if idx not in read:
        read.append(idx)
        habilidades.gain(g, "carisma", 8)
    g.catco["read_day"] = day
    audio.sfx("page")
    g.push(ui.Dialog("Arquivo da CatCo", [f"\"{title}\"", text]))
    if left == [idx]:
        g.toasts.push("Você leu todo o arquivo da CatCo!", C_GOLD)

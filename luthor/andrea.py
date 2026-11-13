"""Andrea Rojas: amiga da Letícia que mora em Metropolis (conselheira do lado dela, nunca rival).

- Mensagens no celular de vez em quando (app Mensagens, com 3 respostas como as das amigas da cidade).
- Uma visita por estação (dia fixo, `VISITS`): na véspera ela avisa, de manhã manda o convite, e a cena toca quando
  a Letícia chega ao lugar no horário (Grão Nobre na primavera, praia no verão, Trattoria no outono, terraço no
  inverno). Cada visita dá energia, carisma, um presente e uma parceria de negócios ($400).
- A amizade com ela fica em `g.andrea["pts"]` (não entra no painel de relacionamentos: ela não mora aqui).
"""
import random

from . import ui, audio, festas, celular, noticias, habilidades
from .historia import EXTRAS
from .data import ITEMS
from .config import C_PINK, C_GOLD, C_GREEN, C_LILAC

KEY = "rojas"
FIRST_DAY = 4                       # mensagens começam no 4º dia de jogo
PARTNERSHIP = 400

celular.EXTRA_SENDERS[KEY] = dict(name="Andrea Rojas", short="Andrea", look=EXTRAS[KEY]["look"],
                                  on_reply=lambda g: _befriend(g, 15))

MSGS = [
    ("Reunião de nove horas em Metropolis. Nove! Horas! Me manda uma foto do mar para eu lembrar que o mundo existe.",
     [("Foto enviada. Com gaivota de brinde.", "A gaivota parece mais calma do que o meu conselho inteiro. Obrigada."),
      ("Respira. Você já sobreviveu a reuniões piores.", "Sobrevivi. Mas eu tinha você do lado, rabiscando o meu caderno."),
      ("Larga tudo e vem para National City.", "Não me tenta. Eu já olhei o preço da passagem. Duas vezes.")]),
    ("Li a CatCo hoje. Você está em todas as páginas. Quando foi que você virou a pessoa mais interessante da costa?",
     [("Sempre fui. Você que demorou a perceber.", "Convencida como na faculdade. Que bom que algumas coisas não mudam."),
      ("A Lucy exagera. Um pouquinho.", "Um pouquinho? Ela escreve como quem gosta muito do assunto. Só digo isso."),
      ("Recorta e guarda. Vou autografar.", "Já recortei. Está na minha geladeira, do lado do imã de Gotham.")]),
    ("Lembra quando a gente fugiu da aula de finanças para ver o mar em Gotham? Hoje eu fugi de um almoço. Mesma sensação.",
     [("E o mar estava cinza, como sempre.", "Cinza e gelado. E mesmo assim foi a melhor tarde do semestre."),
      ("Fugiu para onde?", "Para uma livraria. Comprei três livros e esqueci o guarda-chuva lá. Valeu a pena."),
      ("Não conta para o seu conselho.", "Meu conselho acha que eu estava numa call. Eu estava. Com um café.")]),
    ("Pergunta séria: você está dormindo? Não vale responder \"às vezes\".",
     [("Às vezes. ...Tá, quase nunca.", "Eu sabia. Hoje: celular longe e cama antes da meia-noite. É uma ordem de amiga."),
      ("Estou, sim. A cama da cobertura é ótima.", "Ótimo. Vou fingir que acredito, porque te amo."),
      ("Você está acordada também, então...", "Touché. Combinado: nós duas dormimos agora. Boa noite, Luthor.")]),
    ("Fechei uma parceria hoje e a primeira pessoa para quem eu quis contar foi você. Isso diz muito sobre a minha vida social.",
     [("Parabéns! Eu sabia que você ia conseguir.", "Você sempre sabe. É irritante e maravilhoso ao mesmo tempo."),
      ("Diz que você tem boas amigas.", "Uma ótima amiga. As outras são o meu contador e a minha planta."),
      ("Vamos comemorar na sua próxima visita.", "Fechado. Você escolhe o lugar, eu escolho a sobremesa.")]),
    ("Sonhei que a gente apresentava um projeto juntas e o projetor pegava fogo. A gente ganhava mesmo assim.",
     [("Isso não é sonho, é Gotham 2019.", "Meu Deus, é verdade. O professor nunca se recuperou."),
      ("Ganhar é com a gente mesmo.", "Sempre. Com ou sem projetor."),
      ("Foi um sonho ou uma ameaça?", "Uma profecia. Prepara a apresentação.")]),
    ("Meu assistente perguntou quem é a \"Letícia\" que me faz rir em reunião. Eu disse: \"a única CEO que eu respeito\".",
     [("Só respeita? Achei que admirasse.", "Admiro. Respeito. E roubo umas ideias. Não necessariamente nessa ordem."),
      ("Manda um abraço para o assistente.", "Mandei. Ele ficou vermelho. Agora ele é seu fã."),
      ("Para de rir em reunião, Andrea.", "Impossível. Você manda mensagem nas horas mais erradas.")]),
    ("Metropolis está chovendo há quatro dias. Me conta uma coisa boa de National City.",
     [("O Harry desenhou um gato na espuma do meu café.", "Um gato! Pronto, meu dia melhorou trinta por cento."),
      ("O pôr do sol no píer. Sempre.", "Me guarda um. Na próxima visita, a gente vê juntas."),
      ("Eu. Eu sou a coisa boa de National City.", "Não posso discordar. Mas posso revirar os olhos daqui.")]),
]
for _t, _r in MSGS:
    celular.REPLIES_FOR[_t] = _r

# visita: estação -> (dia, mapa, das, até, onde (texto), convite da manhã)
VISITS = {
    1: (11, "cafe", 9 * 60, 13 * 60, "no Grão Nobre",
        "Surpresa: estou em National City! Café no Grão Nobre, entre 9h e 13h? Eu pago. Você paga o próximo."),
    2: (12, "city", 17 * 60, 20 * 60, "na praia, perto do píer",
        "Cheguei! Fim de tarde na praia, perto do píer, entre 17h e 20h? Trouxe protetor solar e saudade."),
    3: (11, "trattoria", 19 * 60, 22 * 60, "na Ricci Trattoria",
        "Estou na cidade! Jantar na Ricci Trattoria, entre 19h e 22h? Me disseram que a Dona Graça é uma lenda."),
    4: (11, "terrace", 18 * 60, 22 * 60, "no terraço da sua cobertura",
        "Vim te ver antes do fim do ano! Chocolate quente no seu terraço, entre 18h e 22h? Eu levo o chocolate."),
}
for _q, _v in VISITS.items():
    celular.REPLIES_FOR[_v[5]] = [
        ("Estarei lá. Que saudade!", "Eu também. Já estou contando os minutos. Literalmente, abri um cronômetro."),
        ("Você não avisou antes por quê?!", "Porque aí não seria surpresa. E porque eu adoro te ver brava."),
        ("Vou desmarcar tudo.", "Não precisa desmarcar tudo. Só o que for chato. Ou seja, quase tudo.")]

GIFTS = {1: "cafe_especial", 2: "agua_coco", 3: "vinho", 4: "chocolate_quente"}


# --- estado -----------------------------------------------------------------
def init_state(g):
    g.andrea = dict(pts=0, visits=0, seen=[], last_msg=0, invited=[])


def save_state(g):
    return {"andrea": g.andrea}


def load_state(g, d):
    init_state(g)
    a = d.get("andrea") or {}
    g.andrea["pts"] = int(a.get("pts", 0))
    g.andrea["visits"] = int(a.get("visits", 0))
    g.andrea["seen"] = list(a.get("seen", []))
    g.andrea["invited"] = list(a.get("invited", []))
    g.andrea["last_msg"] = int(a.get("last_msg", 0))


def _befriend(g, pts):
    g.andrea["pts"] += pts


def _tag(g):
    return f"{g.year}:{g.quarter}"


def visit_today(g):
    v = VISITS[g.quarter]
    return v if g.day == v[0] and _tag(g) not in g.andrea["seen"] else None


def active(g):
    v = visit_today(g)
    return v if v and v[2] <= g.minutes < v[3] else None


# --- celular, HUD, calendário ----------------------------------------------
def morning(g):
    v = visit_today(g)
    if v and _tag(g) not in g.andrea["invited"]:
        g.andrea["invited"].append(_tag(g))
        celular._send(g, KEY, v[5])
        g.andrea["last_msg"] = g.abs_day()
        return
    day = g.abs_day()
    if day >= FIRST_DAY and day - g.andrea["last_msg"] >= 3 and random.random() < 0.35:
        sent = [m["text"] for m in g.phone["msgs"] if m["npc"] == KEY]
        left = [t for t, _ in MSGS if t not in sent] or [t for t, _ in MSGS]
        celular._send(g, KEY, random.choice(left), toast=False)
        g.andrea["last_msg"] = day


def night(g, notes):
    if g.day + 1 == VISITS[g.quarter][0]:
        notes.append(("Amanhã a Andrea Rojas chega em National City!", C_LILAC))
    if visit_today(g):
        v = VISITS[g.quarter]
        notes.append((f"A Andrea Rojas está na cidade: encontro {v[4]}, das {g.fmt_hour(v[2])} às {g.fmt_hour(v[3])}.",
                       C_PINK))


def hud_lines(g):
    v = visit_today(g)
    if not v or g.minutes >= v[3]:
        return []
    return [(f"Andrea na cidade: {v[4]}, {g.fmt_hour(v[2])} às {g.fmt_hour(v[3])}", C_LILAC)]


def _cal(g, q, d, year):
    return [("Visita da Andrea", C_LILAC)] if VISITS.get(q, (0,))[0] == d else []


def _agenda(g, y, q, d):
    return [(f"Andrea Rojas visita a cidade ({VISITS[q][4]})", C_LILAC)] if VISITS.get(q, (0,))[0] == d else []


festas.CAL_EXTRA.append(_cal)
celular.AGENDA_EXTRA.append(_agenda)
noticias.EXTRA_EVENTS["andrea"] = (50, "Andrea Rojas em National City",
                                   "A executiva de Metropolis foi vista com Letícia Luthor. As duas riram tanto que o "
                                   "garçom pediu para tirar uma foto.")


# --- as cenas -----------------------------------------------------------------
def _intro(g):
    """Primeira visita: reencontro. Depois: \"de novo aqui\"."""
    if g.andrea["visits"] == 0:
        return [("fala", KEY, "Letícia Luthor. Em carne, osso e blazer impecável. Vem cá, me dá um abraço!", "happy"),
                ("fala", "player", "Andrea! Você não avisou que vinha... Você nunca avisa."),
                ("fala", KEY, "Avisar estraga a cara que você faz. Essa aí. Valeu a viagem.")]
    return [("fala", KEY, random.choice(["Olha ela! Cada vez que eu venho você está com mais cara de dona da cidade.",
                                         "Minha CEO favorita! Não conta para os meus sócios que eu disse isso.",
                                         "Cheguei! Trouxe saudade, fofoca de Metropolis e zero paciência para reunião."]),
             "happy"),
            ("fala", "player", random.choice(["Que bom que você veio. Eu estava precisando disso.",
                                              "Você é a melhor parte de cada estação, sabia?",
                                              "Senta, pede alguma coisa e me conta tudo."]))]


def _talk(q):
    """Conversa de cada estação: a amizade antiga, a Luthor Corp e um conselho do lado da Letícia."""
    if q == 1:
        return [
            ("fala", KEY, "Me conta: como é ser a CEO que todo mundo em National City cumprimenta na rua?"),
            ("fala", "player", "Cansativo. E bom. Mais bom do que cansativo, na maior parte dos dias."),
            ("fala", KEY, "É assim que eu sabia que você ia ser. Lembra da faculdade? Você reorganizava até a fila do refeitório."),
            ("escolha", "O que dizer?", [
                ("Eu precisava de alguém que me conhecesse de antes.", 0,
                 "Eu sei. É para isso que eu existo. Para lembrar quem você era antes dos crachás."),
                ("E você? Ainda reorganiza a vida dos outros?", 0,
                 "Só a minha. E mal. Por isso eu venho aqui: para copiar o seu jeito."),
                ("Fica mais uns dias. A cidade é linda na primavera.", 0,
                 "Não me tenta. Mas eu volto no verão. Promessa de amiga."),
            ]),
        ]
    if q == 2:
        return [
            ("fala", KEY, "O mar daqui é mais bonito que o de Gotham. Não conta para Gotham."),
            ("fala", "player", "Seu segredo está seguro. Gotham não lê a CatCo."),
            ("fala", KEY, "Falando nisso: os seus números estão ótimos. Mas você está com cara de quem não tira férias desde a formatura."),
            ("escolha", "O que dizer?", [
                ("Férias são para quem não tem laboratório.", 0,
                 "Errado. Férias são para quem quer continuar tendo laboratório daqui a dez anos."),
                ("Estou tentando. Hoje, por exemplo.", 0,
                 "Hoje conta. Pé na areia conta. Celular no bolso conta mais ainda."),
                ("Você também não tira.", 0,
                 "Por isso eu sei do que estou falando. Combinado: as duas tiram um dia este ano."),
            ]),
        ]
    if q == 3:
        return [
            ("fala", KEY, "Essa lasanha é um crime. Eu vou contratar a Dona Graça e levar para Metropolis."),
            ("fala", "player", "Tenta. Ela te expulsa da cozinha com uma colher de pau."),
            ("fala", KEY, "Justo. Agora, sério: eu ouvi falar dos seus tios. Se precisar de qualquer coisa, eu estou do seu lado. Sempre estive."),
            ("escolha", "O que dizer?", [
                ("Eu sei. Você foi a primeira a chegar na reunião do conselho.", 0,
                 "E vou ser a primeira sempre que precisar. Amiga é para essas coisas."),
                ("Está tudo sob controle. Quase tudo.", 0,
                 "Quase tudo já é muito. O resto a gente resolve no telefone, de madrugada, como antigamente."),
                ("Hoje eu só quero comer lasanha com você.", 0,
                 "Melhor plano da noite. Garçom! Mais uma, por favor."),
            ]),
        ]
    return [
        ("fala", KEY, "Chocolate quente, cobertor e a cidade inteira acesa lá embaixo. Você venceu, Luthor."),
        ("fala", "player", "Venci o quê?"),
        ("fala", KEY, "A vida. Você construiu uma casa aqui. Não o prédio: as pessoas. Eu vi como te olham."),
        ("escolha", "O que dizer?", [
            ("Você faz parte disso, sabia? Mesmo de longe.", 0,
             "Eu sei. Por isso eu volto toda estação. Você é a minha casa fora de casa."),
            ("Demorou, mas eu aprendi a pedir ajuda.", 0,
             "Eu vi. E fico muito orgulhosa. A Letícia da faculdade nunca pedia nada."),
            ("Ano que vem, você vem morar aqui.", 0,
             "Ha! Quem sabe. Metropolis que se cuide."),
        ]),
    ]


def _end(q):
    return [
        ("fala", KEY, random.choice(["Ah, antes que eu esqueça: fechei uma parceria com a Luthor Corp. Pequena, mas boa. "
                                     "Considera presente de amiga.",
                                     "Trouxe uma coisinha. E uma proposta de parceria. A proposta é séria; a coisinha também."]),
         "happy"),
        ("fala", "player", "Andrea... obrigada. Por tudo."),
        ("fala", KEY, "Não agradece. Me liga. E responde as minhas mensagens antes de três dias, por favor.", "happy"),
        ("efeito", "brilhos", 1.2),
        ("esperar", 0.6),
        ("fade_out",),
    ]


def scene(g, q=None):
    q = q or g.quarter
    v = VISITS[q]
    mapn = v[1]
    if mapn == "cafe":
        pos = [("ator", KEY, 12, 7, "right"), ("sentar", KEY), ("ator", "player", 7, 9, "up"),
               ("segurar", KEY, "cappuccino"),
               ("camera_ja", 12, 7), ("fade_in",), ("legenda", "Grão Nobre", 1.6),
               ("andar", "player", 7, 8), ("andar", "player", 14, 8), ("andar", "player", 14, 7), ("sentar", "player")]
    elif mapn == "city":
        pos = [("ator", KEY, 66, 57, "left"), ("ator", "player", 61, 56, "right"),
               ("segurar", KEY, "drink"),
               ("camera_ja", 64, 57), ("fade_in",), ("legenda", "Praia de National City, fim de tarde", 1.8),
               ("andar", "player", 61, 57), ("andar", "player", 64, 57), ("virar", KEY, "left")]
    elif mapn == "trattoria":
        pos = [("ator", KEY, 12, 10, "right"), ("sentar", KEY), ("ator", "player", 10, 11, "up"),
               ("segurar", KEY, "taca_vinho"),
               ("camera_ja", 13, 10), ("fade_in",), ("legenda", "Ricci Trattoria, à noite", 1.6),
               ("andar", "player", 14, 11), ("andar", "player", 14, 10), ("sentar", "player")]
    else:
        pos = [("ator", KEY, 13, 4, "right"), ("sentar", KEY), ("ator", "player", 10, 11, "up"),
               ("segurar", KEY, "cappuccino"),
               ("camera_ja", 14, 6), ("fade_in",), ("legenda", "Terraço da cobertura", 1.6),
               ("andar", "player", 15, 11), ("andar", "player", 15, 4), ("sentar", "player")]
    steps = pos + _intro(g) + _talk(q) + _end(q)
    return dict(map=mapn, time=max(v[2], min(g.minutes, v[3] - 30)), npc=None, steps=steps)


def _finish(g):
    q = g.quarter
    g.andrea["seen"].append(_tag(g))
    g.andrea["visits"] += 1
    _befriend(g, 120)
    g.money += PARTNERSHIP
    g.energy = min(g.max_energy, g.energy + 30)
    habilidades.gain(g, "carisma", 10)
    item = GIFTS[q]
    if item in ITEMS and g.add_item(item):
        g.toasts.push(f"Presente da Andrea: {ITEMS[item]['name']}", C_GREEN, item)
    noticias.event(g, "andrea")
    audio.sfx("reward")
    g.toasts.push(f"Parceria com a empresa da Andrea: +${PARTNERSHIP}. Energia +30.", C_GOLD)


def check(g):
    v = active(g)
    if not v or g.map_name != v[1]:
        return False
    if v[1] == "city":                                   # na praia: só perto do píer
        tx, ty = g.player.tile
        if abs(tx - 64) + abs(ty - 57) > 12:
            return False
    g.play_scene(f"andrea_{g.quarter}", scene(g), on_end=lambda: _finish(g), remember=False)
    return True


from . import scenetest  # noqa: E402
for _q in VISITS:
    scenetest.DYNAMIC[f"andrea_{_q}"] = (lambda q: (lambda g: scene(g, q)))(_q)

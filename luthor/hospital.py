"""Conti Moretti Hospitais — o hospital de National City.

Segue a lógica do site da Conti Moretti: 12 especialidades, lideranças clínicas por área,
agendamento de consultas na recepção e uma jornada de cuidado (acolhimento, diagnóstico,
tratamento e acompanhamento). Cores: verde profundo, papel e cobre.
"""
import random

import pygame

from . import art, ui
from .art import new, up, R, P, shade, mix
from .config import C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_RED, C_PINK

GREEN, GREEN2, COPPER, PAPER = (18, 63, 53), (29, 89, 74), (183, 123, 101), (246, 243, 236)
CMH_GREEN = (110, 200, 160)

# ---------------------------------------------------------------------------
# Lideranças clínicas (como no site) e especialidades
# ---------------------------------------------------------------------------
from .characters import NPCS
from .doctors import DOCTOR_KEYS
LEADERS = {k: NPCS[k] for k in DOCTOR_KEYS}
# especialidade: (nome, líder, descrição do site, conselho, chave do efeito do dia, texto do efeito)
SPECIALTIES = [
    ("cardiologia", "Cardiologia", "milany", "Prevenção, diagnóstico e acompanhamento cardiovascular com cuidado integrado.",
     "Seu coração está ótimo. Caminhe mais, ande menos de elevador.", "Coração em dia: você anda 10% mais rápido hoje."),
    ("neurologia", "Neurologia", "lexie", "Avaliação especializada do sistema nervoso, memória, movimento e qualidade de vida.",
     "Foco é treino. Uma tarefa de cada vez.", "Foco total: trabalhar no laboratório gasta metade da energia hoje."),
    ("ortopedia", "Ortopedia", "meredith", "Diagnóstico, tratamento e reabilitação para mobilidade, trauma e saúde musculoesquelética.",
     "Sua postura na cadeira de CEO é um crime. Alongue a cada hora.", "Coluna alinhada: pescar não gasta energia hoje."),
    ("pediatria", "Pediatria", "addison", "Cuidado integral e acolhedor para acompanhar cada fase do desenvolvimento infantil.",
     "Você não é criança, mas a consulta foi uma graça. Brinque mais.", "Coração de criança: carinho no seu bichinho vale o dobro hoje."),
    ("oncologia", "Oncologia", "izzie", "Cuidado oncológico coordenado, com acompanhamento multidisciplinar em toda a jornada.",
     "Exames preventivos em dia. É assim que se cuida.", "Prevenção em dia: +20 de energia extra agora."),
    ("ginecologia", "Ginecologia & Obstetrícia", "addison", "Saúde da mulher, prevenção, acompanhamento ginecológico e cuidado durante a gestação.",
     "Tudo certo. E cuide também do seu coração... no outro sentido.", "Autocuidado: presentes rendem 25% mais amizade hoje."),
    ("gastro", "Gastroenterologia", "meredith", "Avaliação e acompanhamento do sistema digestivo com apoio diagnóstico integrado.",
     "Menos expresso de estômago vazio, por favor.", "Digestão leve: comidas dão 30% mais energia hoje."),
    ("endocrino", "Endocrinologia", "yang", "Acompanhamento metabólico e hormonal com foco em prevenção e equilíbrio clínico.",
     "Metabolismo de atleta. Irritante, mas parabéns.", "Equilíbrio: pratos cozinhados vendem 20% mais caro hoje."),
    ("dermatologia", "Dermatologia", "izzie", "Saúde da pele, cabelos e unhas com avaliação clínica e acompanhamento individualizado.",
     "Protetor solar. Até dentro do escritório. Sim, eu sei das janelas.", "Brilho próprio: gorjetas do karaokê 50% maiores hoje."),
    ("urologia", "Urologia", "yang", "Cuidado do trato urinário e saúde masculina com abordagem preventiva e especializada.",
     "Beba água. Café não conta como água.", "Hidratada: se desmaiar hoje, o hospital não cobra nada."),
    ("oftalmologia", "Oftalmologia", "lexie", "Avaliação da saúde ocular, prevenção e acompanhamento de alterações da visão.",
     "Visão perfeita. Agora tire os olhos do monitor de vez em quando.", "Olhar atento: você nota mais coletáveis na praia e no parque hoje."),
    ("psiquiatria", "Psiquiatria", "meredith", "Cuidado em saúde mental com escuta qualificada, acompanhamento e integração assistencial.",
     "Você carrega uma cidade nas costas. Pode pedir ajuda. Inclusive pra gente.", "Mente leve: conversas rendem 50% mais amizade hoje."),
]
SPEC = {s[0]: s for s in SPECIALTIES}
CONSULT_PRICE = 90


def consult_price(g):
    return CONSULT_PRICE // 2 if "cmh_discount" in g.flags else CONSULT_PRICE


def leader_portrait(L, size=112):
    return art.portrait(L.get("portrait"), L["look"], size)
DONATION = 1000

# ---------------------------------------------------------------------------
# Arte dos objetos
# ---------------------------------------------------------------------------


def _hreception():
    s = new(64, 26)
    R(s, GREEN, 0, 8, 64, 18)
    R(s, PAPER, 0, 6, 64, 4)
    R(s, COPPER, 0, 10, 64, 2)
    R(s, GREEN2, 2, 13, 60, 1)
    for x in (10, 44):
        R(s, (40, 44, 52), x, 0, 10, 7)
        R(s, (120, 200, 190), x + 1, 1, 8, 5)
    R(s, (240, 240, 240), 28, 4, 6, 3)
    pygame.draw.circle(s, COPPER, (32, 19), 4, 1)
    R(s, PAPER, 31, 16, 2, 6)
    return s


def _hdesk():
    s = new(32, 20)
    R(s, (236, 232, 224), 0, 4, 32, 6)
    R(s, (200, 194, 184), 0, 10, 32, 8)
    R(s, GREEN2, 0, 4, 32, 1)
    R(s, (40, 44, 52), 4, 0, 9, 6); R(s, (140, 210, 200), 5, 1, 7, 4)
    R(s, (250, 250, 250), 18, 5, 6, 2)
    pygame.draw.line(s, (60, 60, 70), (26, 6), (29, 4), 1)
    return s


def _exambed():
    s = new(16, 34)
    R(s, (200, 200, 210), 2, 6, 12, 22)
    R(s, (240, 244, 246), 3, 4, 10, 22)
    R(s, (210, 236, 230), 3, 4, 10, 6)
    R(s, (120, 120, 130), 3, 28, 2, 6); R(s, (120, 120, 130), 11, 28, 2, 6)
    R(s, GREEN2, 2, 26, 12, 2)
    return s


def _hbed():
    s = new(16, 34)
    R(s, (170, 176, 186), 1, 2, 14, 4)
    R(s, (240, 242, 246), 2, 6, 12, 22)
    R(s, (250, 250, 252), 3, 6, 10, 5)
    R(s, (120, 190, 170), 2, 13, 12, 14)
    R(s, (100, 170, 150), 2, 13, 12, 2)
    R(s, (150, 156, 166), 1, 27, 14, 3)
    R(s, (90, 90, 100), 2, 30, 2, 4); R(s, (90, 90, 100), 12, 30, 2, 4)
    return s


def _hchair():
    s = new(16, 18)
    R(s, (40, 130, 110), 3, 2, 10, 8)
    R(s, (60, 160, 136), 4, 3, 8, 3)
    R(s, (50, 146, 122), 3, 9, 10, 4)
    R(s, (150, 150, 160), 4, 13, 1, 5); R(s, (150, 150, 160), 11, 13, 1, 5)
    return s


def _cabinet():
    s = new(16, 24)
    R(s, (230, 232, 236), 1, 2, 14, 22)
    R(s, (200, 204, 210), 1, 12, 14, 1)
    R(s, (160, 220, 230), 3, 4, 10, 6)
    for x in (4, 7, 10):
        R(s, random.Random(x).choice([(230, 90, 90), (90, 150, 220), (240, 200, 90)]), x, 6, 2, 3)
    R(s, (150, 150, 160), 7, 16, 2, 1)
    return s


def _pharma_counter():
    s = new(48, 24)
    R(s, PAPER, 0, 6, 48, 18)
    R(s, GREEN, 0, 4, 48, 3)
    R(s, COPPER, 0, 7, 48, 1)
    R(s, (60, 170, 120), 20, 12, 8, 8)
    R(s, PAPER, 23, 13, 2, 6); R(s, PAPER, 21, 15, 6, 2)
    R(s, (230, 230, 236), 4, 1, 8, 4); R(s, (240, 200, 210), 36, 1, 6, 4)
    return s


def _pharma_shelf():
    s = new(48, 30)
    R(s, (236, 232, 224), 0, 2, 48, 28)
    for y in (6, 14, 22):
        R(s, (200, 194, 184), 2, y + 5, 44, 2)
        rr = random.Random(y)
        for x in range(3, 45, 4):
            c = rr.choice([(230, 100, 100), (100, 160, 230), (250, 220, 120), (140, 210, 160), (240, 240, 240)])
            R(s, c, x, y, 3, 5)
    R(s, GREEN, 0, 0, 48, 3)
    return s


def _vending():
    s = new(16, 30)
    R(s, (200, 50, 60), 1, 2, 14, 28)
    R(s, (40, 40, 50), 3, 5, 8, 16)
    rr = random.Random(5)
    for y in range(6, 20, 4):
        for x in range(4, 11, 3):
            R(s, rr.choice([(250, 220, 120), (120, 200, 255), (240, 140, 190), (140, 230, 150)]), x, y, 2, 2)
    R(s, (230, 230, 236), 12, 8, 2, 6)
    R(s, (20, 20, 26), 3, 23, 8, 3)
    return s


def _monitor():
    s = new(16, 26)
    R(s, (150, 156, 166), 7, 12, 2, 14)
    R(s, (60, 64, 74), 2, 2, 12, 10)
    R(s, (20, 30, 30), 3, 3, 10, 8)
    pts = [(3, 7), (5, 7), (6, 4), (7, 10), (8, 7), (12, 7)]
    pygame.draw.lines(s, (110, 240, 150), False, pts, 1)
    R(s, (100, 100, 110), 4, 24, 8, 2)
    return s


def _cm_rug():
    s = new(64, 48)
    R(s, (232, 208, 199), 0, 0, 64, 48)
    R(s, COPPER, 2, 2, 60, 44)
    R(s, (240, 230, 220), 4, 4, 56, 40)
    # o "M" verde com a cruz de cobre, como no logo
    cx, cy = 32, 24
    for (x, y, w, h) in ((cx - 4, cy - 16, 8, 8), (cx - 4, cy + 8, 8, 8), (cx - 18, cy - 4, 8, 8), (cx + 10, cy - 4, 8, 8)):
        pygame.draw.rect(s, COPPER, (x, y, w, h), 2, border_radius=3)
    R(s, GREEN, cx - 11, cy - 9, 3, 18); R(s, GREEN, cx + 8, cy - 9, 3, 18)
    pygame.draw.line(s, GREEN, (cx - 10, cy - 9), (cx, cy + 3), 3)
    pygame.draw.line(s, GREEN, (cx + 9, cy - 9), (cx, cy + 3), 3)
    return s


def _cm_wall_logo():
    s = new(32, 16)
    R(s, PAPER, 0, 1, 32, 14)
    R(s, COPPER, 0, 14, 32, 2)
    cx, cy = 16, 7
    pygame.draw.rect(s, COPPER, (cx - 2, cy - 6, 4, 4), 1)
    pygame.draw.rect(s, COPPER, (cx - 2, cy + 2, 4, 4), 1)
    R(s, GREEN, cx - 5, cy - 3, 1, 7); R(s, GREEN, cx + 4, cy - 3, 1, 7)
    pygame.draw.line(s, GREEN, (cx - 5, cy - 3), (cx, cy + 2))
    pygame.draw.line(s, GREEN, (cx + 4, cy - 3), (cx, cy + 2))
    return s


def _hsign(kind):
    s = new(16, 14)
    R(s, GREEN, 1, 1, 14, 12)
    R(s, COPPER, 1, 11, 14, 2)
    if kind == 0:    # coração
        pygame.draw.circle(s, (240, 110, 120), (6, 5), 2); pygame.draw.circle(s, (240, 110, 120), (10, 5), 2)
        pygame.draw.polygon(s, (240, 110, 120), [(4, 6), (12, 6), (8, 10)])
    elif kind == 1:  # cérebro
        pygame.draw.ellipse(s, (240, 170, 190), (3, 3, 10, 7))
        pygame.draw.line(s, (200, 120, 150), (8, 3), (8, 9))
    elif kind == 2:  # fita
        pygame.draw.line(s, (240, 190, 210), (6, 3), (10, 10), 2)
        pygame.draw.line(s, (240, 190, 210), (10, 3), (6, 10), 2)
        pygame.draw.circle(s, (240, 190, 210), (8, 4), 2, 1)
    elif kind == 3:  # leito
        R(s, PAPER, 3, 6, 10, 3); R(s, PAPER, 3, 4, 2, 5); R(s, (120, 190, 170), 6, 5, 7, 2)
    else:            # farmácia
        R(s, PAPER, 7, 3, 2, 7); R(s, PAPER, 4, 5, 8, 2)
    return s


def _plaque():
    s = new(16, 14)
    R(s, (200, 170, 90), 2, 2, 12, 10)
    R(s, (240, 210, 120), 3, 3, 10, 8)
    R(s, (120, 40, 190), 7, 4, 2, 5); R(s, (120, 40, 190), 7, 8, 4, 1)
    return s


art.OBJECT_BUILDERS.update({
    "hreception": _hreception, "hdesk": _hdesk, "exambed": _exambed, "hbed": _hbed, "hchair": _hchair,
    "cabinet": _cabinet, "pharma_counter": _pharma_counter, "pharma_shelf": _pharma_shelf, "vending": _vending,
    "monitor": _monitor, "cm_rug": _cm_rug, "cm_wall_logo": _cm_wall_logo, "plaque": _plaque,
    "hsign": lambda: _hsign(0),
})


def sign_sprite(kind):
    return art.cached(("hsign", kind), lambda: up(_hsign(kind)))


# ---------------------------------------------------------------------------
# Lógica
# ---------------------------------------------------------------------------

def init_state(g):
    g.buffs = set()
    g.checkups = set()
    g.consult_today = False
    g.donated_q = None


def save_state(g):
    return dict(buffs=sorted(g.buffs), checkups=sorted(g.checkups), consult_today=g.consult_today,
                donated_q=g.donated_q)


def load_state(g, d):
    g.buffs = set(d.get("buffs", []))
    g.checkups = set(d.get("checkups", []))
    g.consult_today = d.get("consult_today", False)
    g.donated_q = d.get("donated_q")
    ensure_plaque(g)


def night(g):
    g.buffs = set()
    g.consult_today = False


def ensure_plaque(g):
    m = g.world["hospital"]
    if "cmh_wing" in g.flags and not any(o.kind == "plaque" for o in m.objects):
        o = m.add("plaque", 18, 7)
        m.wall_decor.append(o)


def open_hours(g):
    return 7 * 60 <= g.minutes < 22 * 60


def object_label(g, o):
    k = o.kind
    if k == "hreception":
        return "Recepção · Agendamento"
    if k in ("pharma_counter", "pharma_shelf"):
        return "Farmácia Conti Moretti"
    if k == "vending":
        return "Máquina de lanches ($8)"
    if k in ("hbed", "exambed"):
        return "Leito"
    return None


def use_object(g, o):
    k = o.kind
    if k == "hreception":
        open_reception(g)
    elif k in ("pharma_counter", "pharma_shelf"):
        if open_hours(g):
            g.open_shop("pharmacy")
        else:
            g.say("Farmácia fechada. Atendimento das 7h às 22h.")
    elif k == "vending":
        if g.money < 8:
            g.toasts.push("Dinheiro insuficiente.", C_RED)
        elif g.add_item(random.choice(["barra_cereal", "isotonico"])):
            g.money -= 8
            g.toasts.push("A máquina fez um barulho estranho, mas entregou o lanche.", C_GREEN)
    elif k in ("hbed", "exambed"):
        g.say("Um leito arrumadinho. Lençol com cheiro de limpeza e o logo da Conti Moretti bordado.")
    elif k == "hsign":
        names = ["Centro Cardiovascular", "Centro de Neurociências", "Centro de Oncologia", "Internação",
                 "Farmácia"]
        g.say(f"Placa: {names[o.data]}.")
    elif k == "cm_wall_logo":
        g.say("Conti Moretti Hospitais. 'Sua saúde em primeiro lugar.'")
    elif k == "plaque":
        g.say("Placa dourada: 'Ala Luthor — com o apoio da Luthor Corp.' Você sorri.")
    elif k == "cabinet":
        g.say("Armário de materiais. Tudo etiquetado por cor. A Jess aprovaria.")
    elif k == "monitor":
        g.say("Bip... bip... bip. Os sinais vitais estão ótimos.")
    else:
        return False
    return True


def open_reception(g):
    if not open_hours(g):
        g.say("Recepção: atendimento eletivo das 7h às 22h. Emergências pelo pronto-socorro, ao lado.")
        return
    opts, acts = [], []
    opts.append(f"Agendar consulta (${consult_price(g)})"); acts.append(lambda: pick_area(g))
    opts.append("Lideranças clínicas"); acts.append(lambda: show_leaders(g))
    q = (g.year, g.quarter)
    if g.donated_q != list(q) and g.donated_q != q:
        opts.append(f"Doação da Luthor Corp (${DONATION:,})".replace(",", ".")); acts.append(lambda: donate(g))
    opts.append("Sair"); acts.append(lambda: None)
    done = len(g.checkups)
    g.push(ui.Choice(f"Conti Moretti Hospitais — 'Seu cuidado começa aqui.' Check-up: {done}/12 especialidades.",
                     opts, lambda i: acts[i]()))


def pick_area(g):
    if g.consult_today:
        g.say("Recepção: 'Você já passou em consulta hoje. Volte amanhã para outra especialidade!'")
        return
    pages = [SPECIALTIES[:6], SPECIALTIES[6:]]

    def show(page):
        items = pages[page]
        labels = [(("+ " if s[0] in g.checkups else "") + s[1]) for s in items]
        labels.append("Mais especialidades..." if page == 0 else "Voltar")

        def pick(i):
            if i == len(items):
                show(1 - page)
                return
            consult(g, items[i][0])
        g.push(ui.Choice("Selecione uma especialidade:", labels, pick))
    show(0)


def consult(g, key):
    _, name, leader, desc, advice, effect = SPEC[key]
    price = consult_price(g)
    if g.money < price:
        g.say(f"A consulta custa ${price}. Você não tem o suficiente agora.")
        return
    g.money -= price
    g.consult_today = True
    first = key not in g.checkups
    g.checkups.add(key)
    g.buffs.add(key)
    L = LEADERS[leader]

    def after():
        g.minutes += 60
        for n in g.npcs.values():
            n.check_schedule(g.minutes)
        g.energy = max(g.energy, g.max_energy)
        if key == "oncologia":
            g.energy += 20
        if key == "oftalmologia":
            from . import activities
            before = list(g.forage)
            activities.spawn_forage(g)
            g.forage = before + g.forage[:6]
        g.toasts.push(f"Consulta de {name}: energia renovada!", CMH_GREEN)
        g.toasts.push(effect, C_GOLD)
        if len(g.checkups) == 12 and "cmh_checkup" not in g.flags:
            g.flags.add("cmh_checkup")
            g.toasts.push("Check-up completo no Conti Moretti! +15 de energia máxima para sempre.", C_GOLD)
    portrait = leader_portrait(L)
    g.add_friendship(leader, 15)
    lines = [f"{name}. {desc}",
             "Acolhimento, diagnóstico, tratamento e acompanhamento. Vamos lá.",
             advice]
    if first and len(g.checkups) < 12:
        lines.append(f"Você já fez {len(g.checkups)} de 12 especialidades do check-up.")
    g.push(ui.Dialog(L["name"], lines, portrait, on_close=after, subtitle=L["role"]))


def show_leaders(g):
    def draw(surf, rect):
        y = rect.y + 70
        for k, L in LEADERS.items():
            p = leader_portrait(L, 56)
            surf.blit(p, (rect.x + 30, y))
            ui.text(surf, L["name"], (rect.x + 100, y + 6), 19, C_TEXT, bold=True)
            ui.text(surf, L["role"], (rect.x + 100, y + 30), 15, CMH_GREEN)
            y += 66
    g.push(ui.InfoPanel("Lideranças clínicas", draw))


def donate(g):
    def pick(i):
        if i != 0:
            return
        if g.money < DONATION:
            g.say("Saldo insuficiente para a doação.")
            return
        g.money -= DONATION
        g.donated_q = [g.year, g.quarter]
        g.flags.add("cmh_donation_pending")
        first = "cmh_wing" not in g.flags
        g.flags.add("cmh_wing")
        ensure_plaque(g)
        g.toasts.push("Doação feita! A imprensa vai adorar (a ação LCORP sobe esta noite).", C_GOLD)
        if first:
            g.push(ui.Dialog("Dra. Milany Moretti", [
                "Em nome do Conti Moretti: obrigada. Isso vai virar equipamento, leito e gente bem cuidada.",
                "A nova ala vai se chamar Ala Luthor. Já mandamos fazer a placa."],
                leader_portrait(LEADERS["milany"]), subtitle=LEADERS["milany"]["role"]))
        for k in LEADERS:
            g.add_friendship(k, 60)
    g.push(ui.Choice(f"Doar ${DONATION:,} da Luthor Corp ao Conti Moretti? (uma vez por trimestre)".replace(",", "."),
                     ["Doar", "Agora não"], pick))

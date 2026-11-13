"""Corrida matinal com a Sam na orla: terça, quinta e sábado, das 6h às 7h40 (Sam com 2+ corações).

A Sam espera no calçadão da orla (62,53). Conversando com ela no horário aparece "Correr com a Sam" (uma vez por
dia). A primeira corrida tem cena; as outras são rápidas. Cada corrida: +40 de amizade com a Sam, 40 minutos do
relógio e disposição para o dia (energia máxima +20 até dormir, e a energia sobe junto). A cada 5 corridas o
fôlego melhora: +5 de energia máxima para sempre (até +25).
"""
import random

from . import ui, audio, celular
from .config import C_GOLD, C_GREEN, C_LILAC

DAYS = (1, 3, 5)                     # terça, quinta e sábado (g.weekday: 0 = segunda)
START, END = 6 * 60, 7 * 60 + 40
SPOT = ("city", 62, 53, "right")
MIN_HEARTS = 2
DAY_BONUS = 20                       # disposição do dia
EVERY, STEP, CAP = 5, 5, 25          # fôlego permanente

INVITE = ("Comecei a correr na orla: terça, quinta e sábado, às 6h. Vem comigo? Prometo não falar de planilha "
          "nos primeiros dois quilômetros.",
          [("Às 6h? ...Tá. Eu vou.", "Isso! Leva água. E não vale ir de salto."),
           ("Só se tiver café no final.", "Tem um quiosque no calçadão. O café é ruim, mas é café."),
           ("Você fala de planilha correndo?", "Eu penso em planilha correndo. Falar é só no terceiro quilômetro.")])
celular.REPLIES_FOR[INVITE[0]] = INVITE[1]

LINES = [
    "Bom dia, chefe! Hoje a meta é a orla inteira. Ida e volta. Sem parar para tirar foto de gaivota.",
    "Respira pelo nariz, solta pela boca. E não pensa em reunião. Eu vi você pensando em reunião.",
    "A Ruby perguntou por que eu acordo tão cedo. Eu disse: \"para correr com a tia Letícia\". Ela achou loucura.",
    "Você está mais rápida! Ou eu estou mais lenta. Vamos fingir que é você.",
    "Sabia que correndo eu tenho as melhores ideias para o fluxo de caixa? Não, você não quer saber. Corre!",
    "Olha o sol saindo do mar. Isso compensa qualquer despertador.",
]


def init_state(g):
    g.corrida = dict(runs=0, day=-1, invited=False)


def save_state(g):
    return {"corrida": g.corrida}


def load_state(g, d):
    init_state(g)
    c = d.get("corrida") or {}
    g.corrida["runs"] = int(c.get("runs", 0))
    g.corrida["day"] = int(c.get("day", -1))
    g.corrida["invited"] = bool(c.get("invited", False))


def unlocked(g):
    return g.hearts("sam") >= MIN_HEARTS


def bonus(g):
    """Energia máxima extra: fôlego (permanente) + disposição do dia em que correu."""
    c = getattr(g, "corrida", None)
    if not c:
        return 0
    perm = min(CAP, (c["runs"] // EVERY) * STEP)
    return perm + (DAY_BONUS if c["day"] == g.abs_day() else 0)


def run_day(g):
    return g.weekday in DAYS


def open_now(g):
    return run_day(g) and START <= g.minutes < END and g.corrida["day"] != g.abs_day()


def override(g, npc):
    if npc.key != "sam" or not run_day(g) or not unlocked(g):
        return
    m, x, y, d = SPOT
    sch = npc.schedule
    last = None
    for e in sch:
        if e[0] <= END:
            last = e
    new_s = [e for e in sch if e[0] < START] + [(START, m, x, y, d)]
    if last is not None:
        new_s.append((END, last[1], last[2], last[3], last[4]))
    new_s += [e for e in sch if e[0] > END]
    npc.schedule = new_s


def morning(g):
    if unlocked(g) and not g.corrida["invited"]:
        g.corrida["invited"] = True
        celular._send(g, "sam", INVITE[0])


def hud_lines(g):
    if unlocked(g) and g.corrida["invited"] and open_now(g):
        return [("Corrida com a Sam: orla, até 7h40", C_LILAC)]
    return []


def talk_options(g, npc, opts, acts):
    if npc.key != "sam" or g.map_name != "city" or not unlocked(g) or not open_now(g):
        return
    opts.append("Correr com a Sam")
    acts.append(lambda: run(g, npc))


def _reward(g):
    c = g.corrida
    before = bonus(g)
    c["runs"] += 1
    c["day"] = g.abs_day()
    g.energy = min(g.max_energy, g.energy + (bonus(g) - before))      # a energia sobe junto com o máximo
    g.add_friendship("sam", 40)
    g.minutes = min(g.minutes + 40, 25 * 60)
    for n in g.npcs.values():
        n.check_schedule(g.minutes)
    audio.sfx("reward")
    g.toasts.push(f"Corrida na orla: +{DAY_BONUS} de energia máxima hoje, +amizade com a Sam", C_GREEN)
    if c["runs"] % EVERY == 0 and (c["runs"] // EVERY) * STEP <= CAP:
        g.toasts.push(f"Fôlego de corredora: +{STEP} de energia máxima para sempre!", C_GOLD)


def first_scene(g):
    return dict(map="city", time=6 * 60 + 20, npc="sam", steps=[
        ("ator", "sam", 63, 53, "left"),
        ("ator", "player", 61, 53, "right"),
        ("camera_ja", 62, 53), ("fade_in",),
        ("legenda", "Orla de National City, 6h da manhã", 1.8),
        ("fala", "sam", "Você veio! Eu apostei com a Ruby que você ia apertar a soneca três vezes.", "happy"),
        ("fala", "player", "Apertei duas. A terceira eu respeitei você."),
        ("fala", "sam", "Alongou? Ótimo. Mentira, ninguém alonga. Vamos!"),
        ("andar_", "sam", 75, 53), ("andar", "player", 73, 53),     # mesma linha: a Letícia logo atrás da Sam
        ("virar", "sam", "left"), ("virar", "player", "right"),
        ("fala", "sam", "Viu? Correr é igual fechar um trimestre: dói no meio, mas o final é lindo.", "happy"),
        ("escolha", "O que dizer, sem fôlego?", [
            ("Eu... vou... sobreviver.", 30, "Vai. E na quinta você corre mais. É assim que funciona."),
            ("Isso é melhor que café.", 30, "Não conta isso para o Harry. Ele vai ficar ofendido."),
            ("A gente devia fazer isso sempre.", 40, "Terça, quinta e sábado. Já está na sua agenda. A Jess ajudou."),
        ]),
        ("emote", "sam", "estrela"),
        ("esperar", 0.6),
        ("fade_out",),
    ])


def run(g, npc):
    if g.corrida["runs"] == 0:
        g.play_scene("corrida_sam", first_scene(g), on_end=lambda: _reward(g), remember=False)
        return
    g.push(ui.Dialog(npc.name, [random.choice(LINES)], g.portrait_for(npc, "happy"), subtitle="corrida na orla",
                     on_close=lambda: _reward(g)))


from . import scenetest  # noqa: E402
scenetest.DYNAMIC["corrida_sam"] = first_scene

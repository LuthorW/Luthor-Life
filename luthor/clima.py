"""Clima especial: tempestade com raios e trovões, e arco-íris na manhã depois da chuva.

A tempestade é uma chuva mais forte (o clima continua "chuva" para o resto do jogo: rotinas, peixes, figurantes),
com relâmpagos que clareiam a tela e trovões. O arco-íris aparece de manhã (6h às 11h) num dia de sol que vem
depois de um dia de chuva. No inverno não tem nenhum dos dois (a chuva vira neve).
"""
import math
import random

import pygame

from . import audio, seasons
from .config import SCALE

# chance de a chuva de amanhã virar tempestade, por estação
STORM_CHANCE = {"spring": 0.30, "summer": 0.50, "autumn": 0.30, "winter": 0.0}
RAINBOW_CHANCE = 0.70
RAINBOW_FROM, RAINBOW_TO = 6 * 60, 11 * 60


# ---------------------------------------------------------------------------
# Sons (trovão perto e trovão longe), gerados por código como os outros efeitos
# ---------------------------------------------------------------------------
def _thunder_sfx():
    RATE = audio.RATE
    out = {}
    for name, dur, vol, crack, seed in (("trovao", 2.6, 0.95, True, 7), ("trovao_longe", 2.2, 0.55, False, 11)):
        n = int(dur * RATE)
        b = [0.0] * n
        rnd = random.Random(seed)
        lo = lo2 = 0.0
        for k in range(n):
            t = k / RATE
            # ronco: ruído bem filtrado (passa-baixa duplo) com "ondas" de volume
            lo = lo * 0.985 + rnd.uniform(-1, 1) * 0.015
            lo2 = lo2 * 0.96 + lo * 0.04
            env = (1 - math.exp(-t * (30 if crack else 6))) * math.exp(-t * 1.5)
            wob = 0.65 + 0.35 * math.sin(t * 7.3 + math.sin(t * 2.1) * 2)
            b[k] += lo2 * 26 * vol * env * wob
        if crack:                                   # estalo do raio caindo perto
            c = int(0.12 * RATE)
            prev = 0.0
            for k in range(c):
                v = rnd.uniform(-1, 1)
                b[k] += (v - prev) * 0.35 * (1 - k / c) ** 2
                prev = v
        out[name] = b
    return out


audio.EXTRA_SFX.append(_thunder_sfx)
audio.SFX_LEVEL.update(trovao=0.9, trovao_longe=0.7)


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.storm = False
    g.storm_tomorrow = False
    g.rainbow = False
    g.clima_said = set()
    g.flash = 0.0
    g.flash_wait = random.uniform(4, 10)
    g.thunder_at = None


def save_state(g):
    return {"clima": dict(storm=g.storm, storm_tomorrow=g.storm_tomorrow, rainbow=g.rainbow)}


def load_state(g, d):
    d = d.get("clima") or {}
    g.storm = bool(d.get("storm", False)) and g.weather == "chuva"
    g.storm_tomorrow = bool(d.get("storm_tomorrow", False)) and g.weather_tomorrow == "chuva"
    g.rainbow = bool(d.get("rainbow", False)) and g.weather != "chuva"


def night(g, notes, was_rain):
    """Chamada na virada do dia, depois do sorteio do clima (e da festa, que força sol)."""
    season = seasons.of_quarter(g.quarter)
    g.clima_said = set()
    g.storm = g.storm_tomorrow and g.weather == "chuva"
    g.rainbow = (was_rain and g.weather != "chuva" and season != "winter"
                 and random.random() < RAINBOW_CHANCE)
    g.storm_tomorrow = (g.weather_tomorrow == "chuva" and random.random() < STORM_CHANCE[season])


def label(g, weather=None, storm=None):
    """Nome do clima de hoje para o HUD/TV."""
    weather = g.weather if weather is None else weather
    if weather != "chuva":
        return "sol"
    if seasons.of_quarter(g.quarter) == "winter":
        return "neve"
    return "tempestade" if (g.storm if storm is None else storm) else "chuva"


def forecast(g):
    if g.weather_tomorrow != "chuva":
        return "sol o dia todo"
    if seasons.of_quarter(g.quarter) == "winter":
        return "neve"
    return "tempestade com raios (melhor ficar em casa à tarde)" if g.storm_tomorrow else "chuva"


def rainbow_alpha(g, minutes=None):
    """0..1: quanto o arco-íris aparece agora (entra devagar, sai devagar)."""
    if not g.rainbow:
        return 0.0
    m = g.minutes if minutes is None else minutes
    if m < RAINBOW_FROM or m >= RAINBOW_TO:
        return 0.0
    a = min(1.0, (m - RAINBOW_FROM) / 40.0)
    a = min(a, (RAINBOW_TO - m) / 60.0)
    return max(0.0, a)


def morning(g):
    if g.storm:
        g.toasts.push("Tempestade em National City! Raios e trovões o dia todo.", (190, 170, 255))
    if g.rainbow:
        g.toasts.push("Arco-íris no céu! Ele fica até umas 11h.", (255, 214, 120))


# ---------------------------------------------------------------------------
# Relâmpagos
# ---------------------------------------------------------------------------
def update(g, dt, outdoor):
    """Relâmpago de vez em quando nos dias de tempestade (mais fraco dentro dos prédios)."""
    if g.flash > 0:
        g.flash = max(0.0, g.flash - dt * 2.6)
    if g.thunder_at is not None:
        g.thunder_at[0] -= dt
        if g.thunder_at[0] <= 0:
            audio.sfx(g.thunder_at[1])
            g.thunder_at = None
    if not (g.storm and g.weather == "chuva") or seasons.of_quarter(g.quarter) == "winter":
        return
    g.flash_wait -= dt
    if g.flash_wait <= 0:
        g.flash_wait = random.uniform(7, 18)
        near = random.random() < 0.45
        g.flash = (1.0 if near else 0.6) if outdoor else 0.3
        g.flash_kind = random.random() < 0.5             # piscada dupla ou simples
        g.thunder_at = [random.uniform(0.15, 0.4) if near else random.uniform(0.8, 1.8),
                        "trovao" if near and outdoor else "trovao_longe"]


def flash_level(g):
    f = g.flash
    if f <= 0:
        return 0.0
    if getattr(g, "flash_kind", False) and 0.55 < f < 0.75:   # apaga um instante e pisca de novo
        return f * 0.25
    return f


def draw_flash(g, surf, outdoor):
    lv = flash_level(g)
    if lv <= 0:
        return
    W, H = surf.get_size()
    a = int((150 if outdoor else 45) * lv)
    veil = _cache.get(("flash", W, H))
    if veil is None:
        veil = _cache[("flash", W, H)] = pygame.Surface((W, H))
        veil.fill((210, 220, 255))
    veil.set_alpha(a)
    surf.blit(veil, (0, 0))


def draw_rain(surf, t, storm=False):
    """Chuva na tela; na tempestade é mais forte e mais inclinada."""
    W, H = surf.get_size()
    rnd = random.Random(int(t * 20))
    if storm:
        for _ in range(330):
            x = rnd.randrange(W + 160) - 60
            y = rnd.randrange(H)
            pygame.draw.line(surf, (165, 190, 245), (x, y), (x - 9, y + 19), 1)
    else:
        for _ in range(180):
            x = rnd.randrange(W + 100) - 50
            y = rnd.randrange(H)
            pygame.draw.line(surf, (150, 180, 240), (x, y), (x - 5, y + 14), 1)


# ---------------------------------------------------------------------------
# Arco-íris
# ---------------------------------------------------------------------------
_cache = {}
BANDS = [(240, 84, 84), (250, 154, 64), (250, 222, 92), (110, 210, 110), (90, 168, 250), (112, 112, 226),
         (176, 108, 226)]


def _rainbow(W, H):
    key = ("arco", W, H)
    s = _cache.get(key)
    if s is not None:
        return s
    # desenhado em meia resolução e ampliado (fica com cara de pixel art)
    w, h = W // 2, int(H * 0.62) // 2
    small = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = int(w * 0.58), int(h * 1.55)
    r = int(h * 1.42)
    bw = 5
    for i, c in enumerate(BANDS):
        pygame.draw.circle(small, (*c, 120), (cx, cy), r - i * bw, bw)
    # as pontas somem para baixo, e o arco inteiro fica bem suave
    fade = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        k = 1.0 - max(0.0, (y - h * 0.35) / (h * 0.65))
        fade.fill((255, 255, 255, int(255 * max(0.0, k) ** 1.4)), (0, y, w, 1))
    small.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    s = pygame.transform.scale(small, (w * 2, h * 2))
    _cache[key] = s
    return s


def draw_rainbow(g, surf, minutes=None):
    a = rainbow_alpha(g, minutes)
    if a <= 0:
        return
    W, H = surf.get_size()
    arc = _rainbow(W, H)
    arc.set_alpha(int(255 * a * 0.8))
    surf.blit(arc, (0, 0))


# ---------------------------------------------------------------------------
# Falas do dia (uma por personagem, uma vez por dia)
# ---------------------------------------------------------------------------
STORM_LINES = {
    "lucy": "Trovão desse tamanho e o meu editor ainda quer a matéria até as seis. Jornalismo é isso.",
    "vittoria": "Com essa tempestade, metade das reservas cancelou. A outra metade chegou molhada e feliz.",
    "sam": "Desliguei os servidores de teste por precaução. Raio e protótipo não combinam.",
    "brainy": "Cada raio carrega uns cinco bilhões de joules. Eu fiz as contas três vezes. É lindo.",
    "jess": "Remarquei duas reuniões por causa da tempestade. De nada.",
    "nia": "Eu durmo melhor com trovão. Minha avó dizia que é o céu arrumando a casa.",
    "rafa": "Dia de tempestade é dia de chocolate quente. Já deixei a leiteira no fogo.",
    "barry": "Tentei fotografar um raio. Tenho quarenta fotos do céu cinza e uma do meu dedo.",
    "ian": "Mandei recolher os barcos. Mar com raio, nem eu com dezesseis anos encarava.",
    "graca": "Chuva forte assim, lá no Brasil, a gente fazia bolinho de chuva. Vou fazer hoje.",
    "milany": "Dia de tempestade o pronto-socorro enche. Se cuida aí fora, viu?",
    "meredith": "Escorregões, quedas, um guarda-chuva no olho. A tempestade é boa para a residência.",
    "yang": "Trovoada não me assusta. Cirurgia de oito horas assusta. E nem tanto.",
    "izzie": "Eu fiz cookies para a ala inteira. Tempestade pede açúcar.",
    "addison": "Adoro tempestade vista da janela. Da janela, deixo claro.",
}
STORM_GENERIC = [
    "Que trovão! Até a vidraça tremeu.",
    "Melhor ficar debaixo de um teto hoje. Essa tempestade não está de brincadeira.",
    "Contei o tempo entre o raio e o trovão. Está pertinho!",
]
RAINBOW_LINES = {
    "lucy": "Viu o arco-íris? Tirei uma foto pra mandar pra você e fiquei com vergonha de mandar.",
    "vittoria": "Arco-íris logo cedo... Minha nonna diria que é sinal de casa cheia hoje à noite.",
    "sam": "O arco-íris é só refração. Mas é uma refração muito bem-feita, admito.",
    "brainy": "Dá para ver até a faixa violeta hoje. Isso é raro! Anotei no meu caderno.",
    "jess": "Arco-íris às oito da manhã. Até o céu está cumprindo o cronograma.",
    "nia": "Fiz um pedido pro arco-íris. Não posso contar, senão não vale.",
    "rafa": "Hoje tem latte arco-íris. Não pergunta como, só confia.",
    "barry": "ACORDEI CEDO E PEGUEI O ARCO-ÍRIS INTEIRO NA FOTO. Desculpa, tô animado.",
    "ian": "Arco-íris sobre o mar. Nas férias, a gente corria pra tentar achar o pé dele, lembra?",
    "graca": "Depois da chuva sempre vem coisa boa. Olha lá o céu provando.",
    "milany": "Vim trabalhar olhando pro céu. Quase atravessei fora da faixa, não conta pra ninguém.",
    "meredith": "Um arco-íris. Tá bom, vou admitir que é bonito.",
    "yang": "Sim, eu vi o arco-íris. Não, não vou ficar emocionada com física óptica.",
    "izzie": "Arco-íris! Hoje vai ser um dia bom, eu sinto.",
    "addison": "Comecei o dia com arco-íris e café. Já posso ir embora feliz.",
}
RAINBOW_GENERIC = [
    "Você viu o arco-íris hoje cedo? Que coisa linda.",
    "Arco-íris depois da chuva... a cidade inteira parou para olhar.",
    "Dizem que dá sorte ver um arco-íris logo de manhã.",
]


def chat_line(g, npc):
    """Fala de tempestade ou de arco-íris, uma vez por dia para cada personagem."""
    key = npc.key
    if key in g.clima_said:
        return None
    if g.storm and g.weather == "chuva" and seasons.of_quarter(g.quarter) != "winter":
        pool, generic = STORM_LINES, STORM_GENERIC
    elif rainbow_alpha(g) > 0 or (g.rainbow and g.minutes < 13 * 60):
        pool, generic = RAINBOW_LINES, RAINBOW_GENERIC
    else:
        return None
    g.clima_said.add(key)
    return pool.get(key) or random.choice(generic)

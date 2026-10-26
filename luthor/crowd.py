"""Figurantes: moradores de National City que não conversam, mas vivem a cidade.

Cada figurante chega pela rua (ponto de ônibus, beira da cidade ou prédio de apartamentos),
entra num lugar, fica um tempo sentado ou olhando as prateleiras e depois vai embora:
para outro lugar ou de volta para casa. Ninguém nasce dentro de um lugar e ninguém
fica para sempre. Cada um lembra dos últimos lugares que visitou e nunca repete
o mesmo lugar em sequência.

A equipe do Conti Moretti (as lideranças clínicas) também chega pela rua, cumpre o turno
alternando entre consultórios, internação e recepção, e vai embora no fim do expediente.
"""
import math
import random
from collections import deque

from . import art
from .config import TILE, SCALE, C_MUTED
from .entities import NPC
from .characters import NPCS
from .world import CITY_DOORS
from .hospital import LEADERS

# Horário de funcionamento (minutos do dia; fecha depois da meia-noite = > 1440)
VENUES = {
    "cafe": (7 * 60, 19 * 60), "catco": (8 * 60, 20 * 60), "books": (9 * 60, 21 * 60),
    "market": (7 * 60, 19 * 60), "trattoria": (11 * 60 + 30, 23 * 60), "bar": (17 * 60, 25 * 60),
    "cinema": (12 * 60, 24 * 60), "hospital": (7 * 60, 22 * 60), "park": (6 * 60 + 30, 21 * 60),
    "beach": (7 * 60, 20 * 60),
}
WEEKEND_ONLY_CLOSED = {"catco"}     # CatCo quase vazia no fim de semana
ENTRIES = [(1, 14), (70, 17), (1, 39), (70, 42), (10, 14), (58, 18), (66, 39), (36, 38)]

HAIR = [(30, 22, 20), (70, 44, 30), (120, 80, 50), (200, 160, 90), (236, 210, 140), (150, 60, 40), (90, 90, 96),
        (20, 20, 30), (230, 230, 236), (120, 60, 140)]
SKIN = [(250, 222, 200), (236, 196, 160), (210, 160, 120), (170, 120, 86), (130, 86, 60), (96, 62, 44)]
CLOTH = [(200, 60, 70), (60, 110, 200), (240, 200, 80), (90, 170, 110), (240, 240, 240), (40, 40, 50),
         (230, 130, 170), (130, 90, 200), (240, 150, 70), (80, 160, 170), (150, 120, 90)]
PANTS = [(40, 40, 60), (60, 80, 140), (30, 30, 36), (120, 100, 80), (200, 190, 170), (80, 60, 100)]
STYLES = ["short", "long", "cap", "bun", "wavy", "short", "long"]
EYES = [(70, 50, 30), (60, 120, 190), (60, 150, 90), (110, 80, 50), (40, 30, 30)]

NAMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio", "Gabi", "Hugo", "Iara", "João", "Kátia", "Leo",
         "Marta", "Nico", "Olga", "Pedro", "Rita", "Tom", "Vera", "Zé"]


def _look(rnd):
    return dict(hair=rnd.choice(HAIR), skin=rnd.choice(SKIN), cloth=rnd.choice(CLOTH), accent=rnd.choice(CLOTH),
                pants=rnd.choice(PANTS), shoes=(30, 26, 30), style=rnd.choice(STYLES), eyes=rnd.choice(EYES))


class Extra(NPC):
    SPEED = 2.2

    def __init__(self, key, name, look, staff=None):
        super().__init__(key, dict(name=name, short=name, look=look, schedule=[(0, None, 0, 0, "down")],
                                   lines={}, role="", gifts={}))
        self.staff = staff              # chave de LEADERS para a equipe do hospital
        self.label = LEADERS[staff]["name"] if staff else None
        self.history = deque(maxlen=4)  # últimos lugares visitados
        self.venue = None
        self.spot = None
        self.state = "off"              # off | going | staying | leaving
        self.until = 0
        self.off_since = 0
        self.today = 0                  # quantos lugares visitou hoje
        self.goal = None
        self.arrived = True

    def _leg_target(self, world):
        if self.goal and self.goal[0] is None and self.map == "city":
            return min(ENTRIES, key=lambda e: abs(e[0] - self.fx) + abs(e[1] - self.fy))
        return super()._leg_target(world)


class Crowd:
    def __init__(self, world):
        self.world = world
        rnd = random.Random(2034)
        self.extras = [Extra(f"x{i}", NAMES[i], _look(rnd)) for i in range(len(NAMES))]
        self.staff = []      # as médicas agora são personagens completas (doctors.py)
        self.reserved = self._reserved_spots()
        self.spots = {v: self._spots_for(v) for v in VENUES}
        self.venue_last = {}            # lugar -> último figurante enviado

    # ------------------------------------------------------------------
    def all(self):
        return self.extras + self.staff

    def _reserved_spots(self):
        res = set()
        for d in NPCS.values():
            sch = d["schedule"]
            lists = sch.values() if isinstance(sch, dict) else [sch]
            for lst in lists:
                for e in lst:
                    if e[1]:
                        res.add((e[1], e[2], e[3]))
            for p in d.get("date_places", []):
                res.add((p[0], p[1], p[2]))
        return res

    def _spots_for(self, venue):
        """Lugares onde um figurante pode ficar: cadeiras, frente de prateleiras, bancos, areia."""
        if venue in ("park", "beach"):
            m = self.world["city"]
            out = []
            for o in m.objects:
                if venue == "park" and o.kind == "bench" and o.x < 33 and o.y >= 20:
                    out.append((o.x, o.y + 1, "up"))
                elif venue == "park" and o.kind in ("tree", "tree2", "tree3") and 1 < o.x < 33 and 20 <= o.y <= 38:
                    out.append((o.x, o.y + 1, "up"))
                elif venue == "beach" and o.kind in ("umbrella", "umbrella2", "palm"):
                    out.append((o.x, o.y + 1, "down"))
            if venue == "beach":
                out += [(x, 47, "down") for x in (5, 15, 24, 31, 41, 62, 67)]
                out += [(50, 50, "down"), (48, 53, "down"), (52, 53, "down")]
            if venue == "park":
                out += [(15, 29, "right"), (21, 29, "left"), (18, 26, "down"), (18, 31, "up")]
            mapn = "city"
        else:
            m = self.world[venue]
            mapn = venue
            out = []
            for o in m.objects:
                if o.kind in ("chair", "stool", "seat", "hchair", "chair_blue"):
                    d = "up"
                    if m.object_at(o.x + 1, o.y) and m.object_at(o.x + 1, o.y).kind in ("table", "table_it"):
                        d = "right"
                    elif m.object_at(o.x - 1, o.y) and m.object_at(o.x - 1, o.y).kind in ("table", "table_it"):
                        d = "left"
                    out.append((o.x, o.y, d))
                elif o.kind in ("bookshelf", "bookshelf2", "bookshelf3", "produce", "produce2", "fridge2",
                                "flowerstand", "desk_news", "printer", "cooler", "arcade", "jukebox", "pharma_counter",
                                "aquarium", "vending", "hbed", "cafe_counter", "shop_counter", "ticket", "popcorn",
                                "hreception", "counter_it", "rope", "tv_wall"):
                    for xx in range(o.x, o.x + o.w):
                        out.append((xx, o.y + o.h, "up"))
        good = []
        start = CITY_DOORS.get(mapn) if mapn != "city" else (36, 38)
        door = None
        if mapn != "city":
            from .world import INTERIOR_DOORS
            ix, iy = INTERIOR_DOORS[mapn]
            door = (ix, iy - 1)
        for (x, y, d) in out:
            mm = self.world[mapn]
            if not mm.in_bounds(x, y) or (x, y) in mm.doors:
                continue
            o = mm.object_at(x, y)
            if mm.is_solid(x, y) and not (o and not o.solid):
                continue
            if (mapn, x, y) in self.reserved:
                continue
            if door and (abs(x - door[0]) + abs(y - door[1]) <= 1):
                continue
            src = door or start
            if mm.find_path(src, (x, y), 4000) is None and src != (x, y):
                continue
            good.append((x, y, d))
        # sem repetidos
        seen, uniq = set(), []
        for s in good:
            if (s[0], s[1]) not in seen:
                seen.add((s[0], s[1]))
                uniq.append(s)
        return uniq

    # ------------------------------------------------------------------
    def reset_day(self):
        for e in self.all():
            e.map = None
            e.state = "off"
            e.venue = e.spot = None
            e.goal = None
            e.path = None
            e.arrived = True
            e.today = 0
            e.off_since = 0
        self.venue_last = {}

    def to_save(self):
        return {e.key: list(e.history) for e in self.all()}

    def load(self, d):
        for e in self.all():
            e.history.clear()
            e.history.extend(d.get(e.key, []))

    def _open(self, venue, minutes, weekday, weather):
        a, b = VENUES[venue]
        if weekday >= 5 and venue in WEEKEND_ONLY_CLOSED:
            return False
        if weather == "chuva" and venue in ("park", "beach"):
            return False
        return a <= minutes < b - 30

    def _occupied(self, venue):
        return {(e.spot[0], e.spot[1]) for e in self.all() if e.venue == venue and e.spot}

    def _send(self, e, venue, minutes, g):
        spots = [s for s in self.spots[venue] if (s[0], s[1]) not in self._occupied(venue)]
        if not spots:
            return False
        x, y, d = random.choice(spots)
        mapn = "city" if venue in ("park", "beach") else venue
        if e.map is None:
            ex, ey = random.choice(ENTRIES)
            e.place("city", ex, ey, "down")
        e.venue, e.spot = venue, (x, y, d)
        e.goal = (mapn, x, y, d)
        e.path = None
        e.arrived = False
        e.state = "going"
        e.history.append(venue)
        e.today += 1
        self.venue_last[venue] = e.key
        a, b = VENUES[venue]
        stay = random.randint(50, 130) if venue != "hospital" else random.randint(30, 70)
        e.until = min(minutes + stay, b - 10)
        return True

    def _pick_venue(self, e, minutes, g):
        recent = set(list(e.history)[-3:])
        opts = [v for v in VENUES if self._open(v, minutes, g.weekday, g.weather) and v not in recent
                and self.venue_last.get(v) != e.key]
        if not opts:
            return None
        # prefere lugares mais vazios
        weights = [1.0 / (1 + len(self._occupied(v))) * (1.4 if v in ("cafe", "park", "bar", "beach") else 1.0)
                   for v in opts]
        return random.choices(opts, weights)[0]

    def _go_home(self, e):
        e.venue, e.spot = None, None
        e.goal = (None, 0, 0, "down")
        e.path = None
        e.arrived = False
        e.state = "leaving"

    def tick(self, g):
        """Chamado a cada 10 minutos do jogo."""
        minutes = g.minutes
        # quem chegou e já passou da hora vai embora (ou para outro lugar)
        for e in self.extras:
            if e.state == "going" and e.arrived:
                e.state = "staying"
            if e.state == "staying" and (minutes >= e.until or not self._open(e.venue, minutes, g.weekday, g.weather)
                                         and minutes >= VENUES[e.venue][1] - 30):
                nxt = self._pick_venue(e, minutes, g) if e.today < 6 and random.random() < 0.45 else None
                if not (nxt and self._send(e, nxt, minutes, g)):
                    self._go_home(e)
            if e.state == "leaving" and e.map is None:
                e.state = "off"
                e.off_since = minutes
        # novos visitantes: quantos ativos queremos agora
        active = sum(1 for e in self.extras if e.state != "off")
        hour = minutes / 60
        want = 5 if hour < 8 else 11 if hour < 11 else 13 if hour < 19 else 10 if hour < 23 else 3
        if g.weekday >= 5:
            want += 2
        if active < want:
            idle = [e for e in self.extras if e.state == "off" and minutes - e.off_since >= 50 and e.today < 6]
            idle.sort(key=lambda e: (e.today, e.off_since))
            for e in idle[:3]:
                v = self._pick_venue(e, minutes, g)
                if v:
                    self._send(e, v, minutes, g)
        self.tick_staff(g)

    # --- equipe do hospital ------------------------------------------------
    STAFF_SPOTS = {"yang": [(21, 5, "up"), (13, 9, "down"), (15, 2, "down"), (25, 5, "up")],
                   "meredith": [(23, 5, "up"), (9, 2, "down"), (18, 13, "left"), (3, 2, "down")],
                   "milany": [(3, 2, "down"), (8, 13, "left"), (21, 5, "up")],
                   "lexie": [(9, 2, "down"), (25, 5, "up"), (18, 10, "down")],
                   "izzie": [(15, 2, "down"), (23, 5, "up"), (25, 13, "left")],
                   "addison": [(25, 5, "up"), (3, 2, "down"), (9, 10, "down")]}

    def works_today(self, e, g):
        idx = list(LEADERS).index(e.staff)
        return (g.abs_day() + idx) % 7 not in (0, 3) or e.staff in ("milany",)

    def tick_staff(self, g):
        minutes = g.minutes
        for i, e in enumerate(self.staff):
            start = 7 * 60 + 20 * i
            end = 18 * 60 + 30 * i
            if not self.works_today(e, g):
                continue
            if e.state == "off" and start <= minutes < end and e.today == 0:
                self._staff_move(e, minutes, first=True)
                e.today = 1
            elif e.state in ("going", "staying") and minutes >= end:
                self._go_home(e)
            elif e.state == "going" and e.arrived:
                e.state = "staying"
                e.until = minutes + random.randint(50, 120)
            elif e.state == "staying" and minutes >= e.until:
                self._staff_move(e, minutes)
            if e.state == "leaving" and e.map is None:
                e.state = "off"

    def _staff_move(self, e, minutes, first=False):
        spots = self.STAFF_SPOTS[e.staff]
        taken = {(s.spot[0], s.spot[1]) for s in self.staff if s is not e and s.spot}
        last = e.spot
        opts = [s for s in spots if (s[0], s[1]) not in taken and s != last]
        if not opts:
            opts = [s for s in spots if s != last] or spots
        x, y, d = random.choice(opts)
        if first:
            ex, ey = random.choice(ENTRIES[:4])
            e.place("city", ex, ey, "down")
        e.venue, e.spot = "hospital", (x, y, d)
        e.goal = ("hospital", x, y, d)
        e.path = None
        e.arrived = False
        e.state = "going"

    # ------------------------------------------------------------------
    def update(self, dt):
        for e in self.all():
            if e.map is not None or not e.arrived:
                e.update(dt, self.world)

    def on_map(self, name):
        return [e for e in self.all() if e.map == name]

    def staff_at(self, mapn, tx, ty):
        for e in self.staff:
            if e.map == mapn and abs(e.fx - tx) < 0.6 and abs(e.fy - ty) < 0.6:
                return e
        return None

    def extra_at(self, mapn, tx, ty):
        for e in self.extras:
            if e.map == mapn and abs(e.fx - tx) < 0.6 and abs(e.fy - ty) < 0.6:
                return e
        return None


EXTRA_THOUGHTS = {
    "cafe": ["Está concentrada no café e no celular.", "Lendo a CatCo Magazine com um cappuccino."],
    "catco": ["Digitando uma matéria com pressa.", "Falando sozinho: 'prazo, prazo, prazo...'"],
    "books": ["Folheando um livro, totalmente absorto.", "Procurando alguma coisa na prateleira de romances."],
    "market": ["Escolhendo tomates com muito cuidado.", "Comparando o preço de dois queijos."],
    "trattoria": ["Esperando a massa chegar. Com fome.", "Saboreando uma pizza em silêncio."],
    "bar": ["Cantarolando a música da jukebox.", "Assistindo ao jogo na TV do bar."],
    "cinema": ["Esperando a sessão começar.", "Com um balde de pipoca enorme."],
    "hospital": ["Aguardando para ser chamado.", "Lendo um folheto da Conti Moretti."],
    "park": ["Aproveitando o sol no parque.", "Dando milho para os pombos."],
    "beach": ["Olhando o mar.", "Pegando um bronze."],
    None: ["Está com pressa. Nem te viu passar."],
}


def thought(e):
    return random.choice(EXTRA_THOUGHTS.get(e.venue if e.state == "staying" else None, EXTRA_THOUGHTS[None]))

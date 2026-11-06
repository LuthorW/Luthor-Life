"""Jogadora, personagens (NPCs) com rotina diária e carros."""
import math
import random
import time

import pygame

from . import art
from . import sprites  # noqa: F401  (personagens no estilo Stardew)
from . import poses    # sentada, comendo, lendo
from .config import TILE, SCALE

FOOT = 2 * SCALE  # distância do pé até a base do tile
from .world import CITY_DOORS, INTERIOR_DOORS, APT_PARENT, SUB_PARENT, LOBBY_DOORS, APT_DOORS, APARTMENTS

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

# de acordo com o retrato: cabelo escuro ondulado, casaco caramelo por cima de blusa branca
PLAYER_LOOK = dict(hair=(36, 24, 24), skin=(236, 198, 170), cloth=(194, 148, 104), accent=(244, 240, 232),
                   pants=(34, 30, 44), shoes=(22, 16, 26), style="wavy", eyes=(56, 168, 96), outfit="blazer",
                   height=1)

_shadow_cache = {}

# chovendo (fora do inverno): quem está na rua anda de guarda-chuva (ligado por Game.update)
UMBRELLA = {"on": False}
UMB_COLORS = [(214, 64, 84), (64, 112, 214), (246, 196, 64), (120, 64, 186), (58, 160, 120), (238, 124, 52),
              (52, 52, 64), (236, 236, 242), (232, 120, 170), (40, 150, 170)]
PLAYER_UMBRELLA = (128, 44, 200)        # roxo Luthor
_umb_cache = {}

# o que cada um come/bebe sentado à mesa, por lugar
SNACKS = {"cafe": ["expresso", "cappuccino", "croissant", "rosquinha", "sanduiche", "cappuccino"],
          "trattoria": ["pizza", "lasanha", "taca_vinho", "soda", "tiramisu", "taca_vinho"],
          "bar": ["cerveja", "cerveja", "caipirinha", "drink", "petiscos", "taca_vinho"],
          "ricci": ["taca_vinho", "expresso", "cappuccino"],
          "hospital": ["expresso", "sanduiche", "cappuccino"],
          "marina": ["cerveja", "soda", "expresso"]}
DRINK_ICONS = ("cup", "soda", "drink", "beer", "caipi", "wineglass")


def umbrella_img(color):
    """Copa do guarda-chuva (22x9 px de arte), com gomos, varetas e a barra ondulada."""
    img = _umb_cache.get(color)
    if img is None:
        w, h = 22, 9
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        light, dark = art.shade(color, 1.25), art.shade(color, 0.7)
        rows = [(10, 11), (7, 14), (4, 17), (2, 19), (1, 20), (0, 21), (0, 21)]
        for i, (a, b) in enumerate(rows):
            y = i + 1
            for x in range(a, b + 1):
                c = light if x < 6 else (dark if x > 16 else color)
                if y >= 3 and x in (6, 11, 16):
                    c = art.shade(c, 0.8)          # varetas
                s.set_at((x, y), c)
        for x in range(w):                         # barra ondulada
            if x % 5 not in (0, 4):
                s.set_at((x, 8), dark)
        s.set_at((10, 0), (60, 50, 60))
        s.set_at((11, 0), (60, 50, 60))           # ponteira
        out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        for y in range(h):
            for x in range(w):
                if s.get_at((x, y)).a:
                    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                        out.set_at((x + 1 + dx, y + 1 + dy), (40, 24, 40, 255))
        out.blit(s, (1, 1))
        img = art.up(out)
        _umb_cache[color] = img
    return img


def umbrella_color(key):
    return UMB_COLORS[sum(map(ord, str(key))) % len(UMB_COLORS)]


def draw_umbrella(surf, look, d, img_x, img_y, color, phase):
    """phase "back": copa (e, de lado, o cabo) antes do bonequinho; "front": o cabo na frente (de frente/costas)."""
    ax, ay = poses.anchor(d, "umbrella", look)
    hx, hy = img_x + ax * SCALE, img_y + ay * SCALE
    side = d in ("left", "right")
    can = umbrella_img(color)
    top_y = img_y - can.get_height() + 2 * SCALE
    if phase == "back":
        cx = hx if side else img_x + (poses.PAD + 11.5) * SCALE
        if side:
            pygame.draw.rect(surf, (54, 44, 52), (int(hx - SCALE / 2), top_y + can.get_height() - SCALE,
                                                  SCALE, int(hy - top_y - can.get_height() + SCALE)))
        surf.blit(can, (int(cx - can.get_width() / 2), top_y))
    elif not side:
        y0 = top_y + can.get_height() - 2 * SCALE
        pygame.draw.rect(surf, (54, 44, 52), (int(hx - SCALE / 2), y0, SCALE, int(hy - y0)))
        pygame.draw.rect(surf, (90, 76, 86), (int(hx - SCALE / 2), y0, max(1, SCALE // 2), int(hy - y0)))


# Bebida na mão: desenho pequeno, no mesmo tamanho de pixel dos bonequinhos (o ícone da mochila é grande e
# tapava o rosto). Virado para a direita: a alça/mão fica à esquerda, do lado do corpo.
# A = líquido (cor do item), a = líquido escuro, l = brilho, f = espuma, g = vidro, W = louça, s = pires,
# m = metal, L = limão, i = gelo, h = alça
DRINK_SPRITES = {
    "beer": [".fff", "hfff", "hlAa", "hlAa", ".aaa"],             # caneca com espuma
    "wineglass": ["lAA", "AAA", ".a.", ".g.", "ggg"],              # taça: bojo, haste e pé
    "caipi": ["Lgig", "AiAA", "AAiA", "aaaa"],                     # copo baixo com limão e gelo
    "cup": [".AA.", "hWWW", "hWWW", "ssss"],                       # xícara no pires
    "soda": ["mmm", "AAA", "WWW", "AAa", "mmm"],                   # latinha
    "drink": ["AAAAL", ".AAA.", "..a..", "..g..", ".ggg."],        # taça de coquetel
}
# base (meio de baixo) do copo em cada pose, px de arte a partir do canto do quadro sem o PAD, virada p/ a direita.
# Brinde de lado: na altura do peito, na frente do corpo; duas personagens a 1 tile batem os copos no meio.
DRINK_AT = {("front", "hold"): (8.0, 22.0), ("side", "hold"): (12.5, 21.0),
            ("front", "mouth"): (8.0, 19.0), ("side", "mouth"): (14.5, 16.5),
            ("front", "toast"): (16.0, 12.0), ("side", "toast"): (14.0, 22.0)}
_drink_cache = {}


def drink_sprite(item, left=False):
    """Copo/taça/xícara pequenos com contorno escuro (como os bonequinhos), já ampliados."""
    from .data import ITEMS
    it = ITEMS.get(item, {})
    kind, col = it.get("icon"), tuple(it.get("color", (200, 160, 120)))
    key = (kind, col, left)
    img = _drink_cache.get(key)
    if img is None:
        rows = DRINK_SPRITES.get(kind, DRINK_SPRITES["cup"])
        glass, cup = (214, 232, 240), (244, 240, 232)
        pal = {"A": col, "a": art.shade(col, 0.72), "l": art.mix(col, (255, 255, 255), 0.55),
               "f": (250, 246, 232), "g": glass, "W": cup, "s": (210, 206, 220), "m": (196, 200, 212),
               "L": (118, 196, 64), "i": (238, 248, 255), "h": glass if kind == "beer" else cup}
        w, h = len(rows[0]), len(rows)
        s = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        for y, row in enumerate(rows):                 # contorno escuro primeiro
            for x, ch in enumerate(row):
                if ch != ".":
                    c = pal[ch]
                    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                        s.set_at((x + 1 + dx, y + 1 + dy), (*art.mix(art.shade(c, 0.36), (34, 18, 30), 0.45), 255))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    s.set_at((x + 1, y + 1), pal[ch])
        img = art.up(s)
        if left:
            img = pygame.transform.flip(img, True, False)
        _drink_cache[key] = img
    return img


def is_drink(item):
    from .data import ITEMS
    return ITEMS.get(item, {}).get("icon") in DRINK_ICONS


def draw_drink(surf, img_x, img_y, look, d, item, where="hold", tilt=0.0):
    """Bebida na mão. tilt > 0 = a boca do copo vai para o rosto (golinho); < 0 = para a frente (tim-tim)."""
    view = poses.VIEW[d]
    if view == "back":
        return
    ax, ay = DRINK_AT.get((view, where), DRINK_AT[(view, "hold")])
    if d == "left":
        ax = 16 - ax
    dh = look.get("height", 0)
    if dh < 0:                                     # quem é mais baixa: a cabeça e o peito descem
        ay += -dh
    img = drink_sprite(item, d == "left")
    bx, by = img_x + (ax + poses.PAD) * SCALE, img_y + ay * SCALE + SCALE      # +1: contorno de baixo
    if tilt:
        cy = by - img.get_height() / 2
        rot = pygame.transform.rotate(img, -tilt if d == "left" else tilt)
        surf.blit(rot, (int(bx - rot.get_width() / 2), int(cy - rot.get_height() / 2)))
    else:
        surf.blit(img, (int(bx - img.get_width() / 2), int(by - img.get_height())))


def draw_held(surf, img_x, img_y, look, d, item, where="hold", tilt=0.0, bites=0):
    """Comida/bebida na mão (mesma conta do comer da Letícia). tilt: graus do copo inclinando."""
    if poses.VIEW[d] == "back" or not item:
        return
    if is_drink(item):
        draw_drink(surf, img_x, img_y, look, d, item, where, tilt)
        return
    ax, ay = poses.anchor(d, where, look)
    icon = art.item_icon(item, 1)
    if bites:
        icon = icon.copy()
        w = icon.get_width()
        for i in range(min(3, bites)):
            pygame.draw.circle(icon, (0, 0, 0, 0), (w - 2 - i * (w // 4), 2 + i * 3), w // 4 + 1)
    if tilt:
        icon = pygame.transform.rotate(icon, tilt if d == "left" else -tilt)
    x, y = img_x + ax * SCALE, img_y + ay * SCALE
    surf.blit(icon, (int(x - icon.get_width() / 2), int(y - icon.get_height() / 2)))


def idle_frame(frames, d, moving, anim, phase):
    """Escolhe o frame: andando, piscando ou parado (com leve respiração)."""
    if moving:
        f = int(anim) % 4
        return frames[(d, f)], (1 if f in (1, 3) else 0)
    t = time.monotonic() + phase
    if t % 3.7 < 0.13:
        return frames[("blink", d)], 0
    return frames[(d, 0)], (1 if (t % 1.6) < 0.8 else 0)


def draw_shadow(surf, cx, cy, w=10 * SCALE):
    sh = _shadow_cache.get(w)
    if sh is None:
        sh = pygame.Surface((w, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, w, 10))
        _shadow_cache[w] = sh
    surf.blit(sh, (cx - w // 2, cy - SCALE * 2))


class Player:
    SIT_TIME = 0.2            # deslizando até o assento
    SIT_SWAP = 0.1            # quando troca para o quadro sentada
    RISE_TIME = 0.16          # levantando

    def __init__(self):
        self.set_look(PLAYER_LOOK)
        self.x = self.y = 0.0
        self.dir = "down"
        self.moving = False
        self.anim = 0.0
        self.seat = None          # sentada: dict(lift, sort, back=(x, y, dir), t, off) — ver Game.sit
        self.rise = None          # levantando: dict(t, off)
        self.pose = None          # comendo/bebendo/lendo: dict(arms, face, blink, bob, item) — ver Game.update_eat_fx
        self.swing_t = random.uniform(3, 7)       # sentada: de vez em quando balança os pés
        self.swinging = 0.0
        self.img_top = None       # canto de cima do último quadro desenhado (para a comida ficar na mão)
        self.umbrella = False     # na rua, chovendo (Game.update liga)
        self.hidden = False       # deitada na cama: o desenho fica com animacoes.Sleeper

    def set_look(self, look):
        self.look = look
        self.look_key = poses.look_key(look)
        self.frames = art.character_frames(look)

    def tick(self, dt):
        """Tempo das animações de sentar/levantar e do balanço dos pés."""
        if self.seat:
            self.seat["t"] = self.seat.get("t", 9.0) + dt
            if self.swinging > 0:
                self.swinging -= dt
            else:
                self.swing_t -= dt
                if self.swing_t <= 0:
                    self.swinging = random.uniform(1.2, 2.0)
                    self.swing_t = random.uniform(5, 10)
        if self.rise:
            self.rise["t"] += dt
            if self.rise["t"] >= self.RISE_TIME:
                self.rise = None

    def place_tile(self, tx, ty, d=None):
        self.seat = None
        self.rise = None
        self.x = (tx + 0.5) * TILE
        self.y = (ty + 1) * TILE - FOOT
        if d:
            self.dir = d

    def rect_at(self, x, y):
        w, h = int(TILE * 0.58), int(TILE * 0.25)
        return pygame.Rect(int(x - w / 2), int(y - h), w, h)

    @property
    def tile(self):
        return int(self.x // TILE), int((self.y - FOOT) // TILE)

    def facing_tile(self):
        dx, dy = DIRS[self.dir]
        tx, ty = self.tile
        return tx + dx, ty + dy

    def _collides(self, rect, gmap, blockers, old_rect):
        x0, x1 = rect.left // TILE, (rect.right - 1) // TILE
        y0, y1 = rect.top // TILE, (rect.bottom - 1) // TILE
        hit = getattr(gmap, "hitboxes", {})
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if gmap.is_solid(tx, ty):
                    hb = hit.get((tx, ty))
                    if hb is None or rect.colliderect(hb):
                        return True
        for b in blockers:
            if rect.colliderect(b) and not old_rect.colliderect(b):
                return True
        return False

    def _slide(self, vx, vy, gmap, blockers):
        """Bateu de frente numa quina: procura uma brecha logo ao lado e escorrega até ela."""
        old = self.rect_at(self.x, self.y)
        step = abs(vx) + abs(vy)
        for k in range(2, int(TILE * 0.6) + 1, 2):
            for sgn in (-1, 1):
                ox, oy = (0, sgn * k) if vx else (sgn * k, 0)
                if self._collides(self.rect_at(self.x + ox, self.y + oy), gmap, blockers, old):
                    continue
                if self._collides(self.rect_at(self.x + ox + vx, self.y + oy + vy), gmap, blockers, old):
                    continue
                mv = min(step, k)
                sx, sy = (0, sgn * mv) if vx else (sgn * mv, 0)
                if not self._collides(self.rect_at(self.x + sx, self.y + sy), gmap, blockers, old):
                    self.x += sx
                    self.y += sy
                return

    def update(self, dt, move, gmap, blockers, speed):
        mx, my = move
        self.moving = bool(mx or my)
        if self.moving:
            if abs(mx) > abs(my) or (mx and my == 0):
                self.dir = "right" if mx > 0 else "left"
            elif my:
                self.dir = "down" if my > 0 else "up"
            ln = math.hypot(mx, my)
            vx, vy = mx / ln * speed * dt, my / ln * speed * dt
            old = self.rect_at(self.x, self.y)
            nx = self.x + vx
            if not self._collides(self.rect_at(nx, self.y), gmap, blockers, old):
                self.x = nx
            elif vx and not vy:
                self._slide(vx, 0, gmap, blockers)
            old = self.rect_at(self.x, self.y)
            ny = self.y + vy
            if not self._collides(self.rect_at(self.x, ny), gmap, blockers, old):
                self.y = ny
            elif vy and not vx:
                self._slide(0, vy, gmap, blockers)
            self.anim += dt * (10 if speed > 3.8 * TILE else 8)
        else:
            self.anim = 0

    def draw(self, surf, cam):
        sx, sy = self.x - cam[0], self.y - cam[1]
        lift, extra = None, 0
        st = self.seat
        if st:                                   # sentando: desliza até o assento e "plof"
            t = st.get("t", 9.0)
            k = 1 - (1 - min(1.0, t / self.SIT_TIME)) ** 2
            ox, oy = st.get("off", (0, 0))
            sx += ox * (1 - k)
            sy += oy * (1 - k)
            if t >= self.SIT_SWAP:
                lift = st["lift"]
                if t < self.SIT_SWAP + 0.08:
                    extra = SCALE
        elif self.rise:                          # levantando: impulso e volta para onde estava
            t = self.rise["t"]
            k = 1 - (1 - min(1.0, t / self.RISE_TIME)) ** 2
            ox, oy = self.rise["off"]
            sx += ox * (1 - k)
            sy += oy * (1 - k)
            if t < 0.07:
                extra = -SCALE
        sx, sy = int(sx), int(sy)
        if self.hidden:                          # deitada na cama (desenhada por animacoes.Sleeper)
            self.img_top = None
            return
        pose = self.pose
        umb = self.umbrella and lift is None and not pose
        if lift is None and not pose and not umb:
            img, bob = idle_frame(self.frames, self.dir, self.moving, self.anim, 0.0)
            draw_shadow(surf, sx, sy + SCALE)
            y = sy - img.get_height() + FOOT + bob + extra
        else:
            now = time.monotonic()
            blink = now % 3.7 < 0.13
            bob = 1 if (now % 1.6) < 0.8 else 0
            swing = 0
            if lift is not None and self.swinging > 0 and not pose and self.dir != "up":
                swing = (0, 1, 0, 2)[int(self.swinging * 6) % 4]
            arms = face = None
            walk, lean, tip = 0, 0, False
            if pose:
                arms, face = pose.get("arms"), pose.get("face")
                blink = pose.get("blink", blink)
                bob = pose.get("bob", 0)
                walk, lean, tip = pose.get("walk", 0), pose.get("lean", 0), pose.get("tiptoe", False)
            elif umb:
                arms = "umbrella"
                if self.moving:
                    walk = int(self.anim) % 4
                    bob, blink = (1 if walk in (1, 3) else 0), False
            img = poses.frame(self.look, self.dir, lift, arms, face, blink, swing, self.look_key, walk, lean, tip)
            if lift is None:
                draw_shadow(surf, sx, sy + SCALE)
            y = sy - img.get_height() + FOOT + bob + extra + (poses.seat_offset(lift) if lift is not None else 0)
        x = sx - img.get_width() // 2
        if umb:
            draw_umbrella(surf, self.look, self.dir, x, y, PLAYER_UMBRELLA, "back")
        surf.blit(img, (x, y))
        if umb:
            draw_umbrella(surf, self.look, self.dir, x, y, PLAYER_UMBRELLA, "front")
        self.img_top = (x + cam[0], y + cam[1])  # em coordenadas do mundo
        if pose and pose.get("held"):            # item na mão fora do comer (brinde, peixe pescado...)
            hd = pose["held"]
            draw_held(surf, x, y, self.look, self.dir, hd["item"], hd.get("where", "hold"), hd.get("tilt", 0.0))


class NPC:
    SPEED = 2.4

    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.name = data["name"]
        self.frames = art.character_frames(data["look"])
        self.map = None
        self.fx = self.fy = 0.0
        self.dir = "down"
        self.goal = None
        self.path = None
        self.arrived = True
        self.anim = 0.0
        self.moving = False
        self.idle_t = random.uniform(2, 6)
        self.paused = 0.0
        self.phase = random.uniform(0, 10)
        self.schedule = self.base_schedule("default")
        self.seat_lift = None           # sentada numa cadeira/sofá/banqueta (altura do assento) ou None
        self.seat_t = 0.0               # tempo desde que sentou (para o "plof")
        self._seat_key = None
        self._seat_val = None
        self.swing_t = random.uniform(4, 12)
        self.swinging = 0.0
        self.pose = None                # pose definida de fora (beijo): dict como Player.pose
        self.wave_t = 0.0               # acenando para a Letícia
        self.snack = None               # sentada à mesa: comendo/bebendo (ver _tick_snack)
        self.img_top = None

    def base_schedule(self, kind):
        sch = self.data["schedule"]
        if isinstance(sch, list):
            return list(sch)
        return list(sch.get(kind) or sch["default"])

    def plan_day(self, weekday, weather, partner=False, date=None):
        """Monta a rotina do dia: fim de semana, chuva, morar junto e encontros."""
        kind = "default"
        if weather == "chuva" and "rain" in (self.data["schedule"] if isinstance(self.data["schedule"], dict) else {}):
            kind = "rain"
        elif weekday >= 5:
            kind = "weekend"
        sch = self.base_schedule(kind)
        if partner:
            # morando junto: o apartamento antigo vira a cobertura da Letícia
            apt = APARTMENTS.get(self.key)
            sch = [e for e in sch]
            if sch and sch[0][1] in (None, apt):
                sch[0] = (sch[0][0], "home", 20, 7, "up")
            if sch[-1][1] in (None, apt):
                sch[-1] = (sch[-1][0], "home", 14, 12, "left")
            sch = [((t, "home", 14, 12, "left") if m == apt else (t, m, x, y, d)) for (t, m, x, y, d) in sch]
        if date:
            m, x, y, d = date
            start, end = 1140, 1320
            before = [e for e in sch if e[0] < start]
            after = [e for e in sch if e[0] > end]
            last = None
            for e in sch:
                if e[0] <= end:
                    last = e
            sch = before + [(start, m, x, y, d)]
            if last is not None:
                sch.append((end, last[1], last[2], last[3], last[4]))
            sch += after
        self.schedule = sch

    def place(self, m, x, y, d=None):
        self.map = m
        self.fx, self.fy = float(x), float(y)
        if d:
            self.dir = d

    @property
    def tile(self):
        return int(round(self.fx)), int(round(self.fy))

    def rect(self):
        cx = (self.fx + 0.5) * TILE
        cy = (self.fy + 1) * TILE - FOOT
        w, h = int(TILE * 0.66), int(TILE * 0.3)
        return pygame.Rect(int(cx - w / 2), int(cy - h), w, h)

    @property
    def base_y(self):
        return (self.fy + 1) * TILE - FOOT

    def entry_for(self, minutes):
        cur = self.schedule[0]
        for e in self.schedule:
            if e[0] <= minutes:
                cur = e
        return cur

    def snap_to_schedule(self, minutes):
        _, m, x, y, d = self.entry_for(minutes)
        self.goal = (m, x, y, d)
        self.path = []
        self.arrived = True
        if m is None:
            self.map = None
        else:
            self.place(m, x, y, d)

    def check_schedule(self, minutes):
        _, m, x, y, d = self.entry_for(minutes)
        goal = (m, x, y, d)
        if goal != self.goal:
            self.goal = goal
            self.path = None
            self.arrived = False

    def face_toward(self, px, py):
        cx = (self.fx + 0.5) * TILE
        cy = (self.fy + 1) * TILE - FOOT
        dx, dy = px - cx, py - cy
        if abs(dx) > abs(dy):
            self.dir = "right" if dx > 0 else "left"
        else:
            self.dir = "down" if dy > 0 else "up"
        self.paused = 2.5

    # mapas em três níveis: cidade -> prédio (portaria Bayside ou Residencial) -> apartamento/cobertura
    @staticmethod
    def _top(m):
        """O prédio da cidade onde fica o mapa m (o próprio m, se ele já tem porta na rua)."""
        return SUB_PARENT.get(m, m)

    def _leg_target(self, world):
        gmap = self.goal[0]
        if self.map == gmap:
            return (self.goal[1], self.goal[2])
        if self.map in SUB_PARENT:                               # sai do apartamento para o corredor
            return APT_DOORS[self.map]
        if self.map != "city":
            if SUB_PARENT.get(gmap) == self.map:                 # do corredor para o apartamento
                return LOBBY_DOORS[gmap]
            return INTERIOR_DOORS[self.map]
        if gmap is None:
            m = world["city"]
            return min(m.spawn_edges, key=lambda e: abs(e[0] - self.fx) + abs(e[1] - self.fy))
        return CITY_DOORS[self._top(gmap)]

    def _finish_leg(self, world):
        gmap, gx, gy, gd = self.goal
        if self.map == gmap and self.tile == (gx, gy):
            self.dir = gd
            self.arrived = True
            return
        if self.map in SUB_PARENT:
            lx, ly = LOBBY_DOORS[self.map]
            self.place(SUB_PARENT[self.map], lx, ly + 1, "down")
        elif self.map != "city" and SUB_PARENT.get(gmap) == self.map:
            ax, ay = APT_DOORS[gmap]
            self.place(gmap, ax, ay - 1, "up")
        elif self.map != "city":
            cx, cy = CITY_DOORS[self.map]
            self.place("city", cx, cy + 1, "down")
        elif gmap is None:
            self.map = None
            self.arrived = True
        else:
            top = self._top(gmap)
            ix, iy = INTERIOR_DOORS[top]
            self.place(top, ix, iy - 1, "up")
        self.path = None

    def update(self, dt, world):
        self._move(dt, world)
        self._check_seat(dt, world)
        if self.wave_t > 0:
            self.wave_t = max(0.0, self.wave_t - dt)
        self._tick_snack(dt)

    # --- comendo/bebendo à mesa: descansa, pega, leva à boca, segura e às vezes dá outro gole
    def _tick_snack(self, dt):
        if self.seat_lift is None or self.map not in SNACKS:
            self.snack = None
            return
        if self.snack is None:
            self.snack = dict(item=random.choice(SNACKS[self.map]), state="rest", t=random.uniform(1.0, 4.0), sips=0)
            return
        sn = self.snack
        sn["t"] -= dt
        if sn["t"] > 0:
            return
        st = sn["state"]
        if st == "rest":
            sn["state"], sn["t"] = "hold", random.uniform(1.0, 2.2)
        elif st == "hold":
            sn["state"], sn["t"] = "sip", 0.8
            sn["sips"] += 1
        elif st == "sip":
            sn["state"], sn["t"] = "hold2", random.uniform(0.8, 1.6)
        elif random.random() < 0.45:
            sn["state"], sn["t"] = "sip", 0.8
            sn["sips"] += 1
        else:
            sn["state"], sn["t"] = "rest", random.uniform(3.0, 8.0)

    def snack_pose(self):
        sn = self.snack
        if not sn or sn["state"] == "rest":
            return None
        from .data import ITEMS
        drink = ITEMS.get(sn["item"], {}).get("icon") in DRINK_ICONS
        if sn["state"] == "sip":
            k = 0.8 - sn["t"]
            face = "shut" if drink and k > 0.2 else ("open" if not drink and k < 0.25 else None)
            held = dict(item=sn["item"], where="mouth", tilt=min(35.0, k / 0.5 * 35.0) if drink else 0.0,
                        bites=0 if drink else sn["sips"] % 4)
            return dict(arms="mouth", face=face, blink=False, bob=0, held=held)
        bites = 0 if drink else sn["sips"] % 4
        return dict(arms="hold", face=None, bob=0, held=dict(item=sn["item"], where="hold", bites=bites))

    def pose_now(self):
        if self.pose:
            return self.pose
        if self.wave_t > 0:
            return dict(arms="wave" if int(self.wave_t * 6) % 2 else "wave2", face="happy", blink=False, bob=0)
        return self.snack_pose()

    def _check_seat(self, dt, world):
        """Parada em cima de um assento: senta (cadeira, sofá, banqueta, poltrona do cinema)."""
        lift = None
        if self.arrived and not self.moving and self.map in world:
            key = (self.map, self.fx, self.fy)
            if key != self._seat_key:
                self._seat_key = key
                tx, ty = int(round(self.fx)), int(round(self.fy))
                o = None
                if abs(self.fx - tx) < 0.02 and abs(self.fy - ty) < 0.02:
                    o = world[self.map].object_at(tx, ty)
                self._seat_val = poses.NPC_SEATS.get(o.kind) if o is not None else None
            lift = self._seat_val
        else:
            self._seat_key = None
        if lift != self.seat_lift:
            self.seat_lift = lift
            self.seat_t = 0.0
        else:
            self.seat_t += dt
        if lift is not None:
            if self.swinging > 0:
                self.swinging -= dt
            else:
                self.swing_t -= dt
                if self.swing_t <= 0:
                    self.swinging = random.uniform(1.0, 2.0)
                    self.swing_t = random.uniform(6, 16)

    def _move(self, dt, world):
        self.moving = False
        if self.paused > 0:
            self.paused -= dt
            return
        if self.arrived or self.goal is None:
            self._idle(dt)
            return
        gmap, gx, gy, gd = self.goal
        if self.map is None:
            if gmap is None:
                self.arrived = True
                return
            if gmap == "city":
                ex, ey = random.choice(world["city"].spawn_edges)
                self.place("city", ex, ey)
            elif gmap in APT_PARENT:                             # acorda já dentro de casa
                self.place(gmap, gx, gy, gd)
                self.arrived = True
                return
            else:
                ix, iy = INTERIOR_DOORS[gmap]
                self.place(gmap, ix, iy - 1, "up")
            self.path = None
        if self.path is None:
            target = self._leg_target(world)
            path = world[self.map].find_path(self.tile, target)
            if path is None:
                if gmap is None:
                    self.map = None
                else:
                    self.place(gmap, gx, gy, gd)
                self.arrived = True
                return
            self.path = path
        if not self.path:
            self._finish_leg(world)
            return
        tx, ty = self.path[0]
        dx, dy = tx - self.fx, ty - self.fy
        dist = math.hypot(dx, dy)
        step = self.SPEED * dt
        if dist <= step:
            self.fx, self.fy = float(tx), float(ty)
            self.path.pop(0)
        else:
            self.fx += dx / dist * step
            self.fy += dy / dist * step
        if abs(dx) > abs(dy):
            self.dir = "right" if dx > 0 else "left"
        else:
            self.dir = "down" if dy > 0 else "up"
        self.moving = True
        self.anim += dt * 7

    def _idle(self, dt):
        self.idle_t -= dt
        if self.idle_t <= 0 and self.goal:
            self.idle_t = random.uniform(3, 8)
            if self.seat_lift is not None:          # sentada: olha para a mesa e, às vezes, para a frente
                self.dir = random.choice([self.goal[3], self.goal[3], self.goal[3], "down"])
                return
            self.dir = random.choice([self.goal[3], self.goal[3], "down", "left", "right"])
            if random.random() < 0.5:
                self.dir = self.goal[3]

    def current_frames(self):
        """Roupa da estação (characters.dress); médicas trocam o jaleco pela roupa de fora ao sair do hospital."""
        from . import characters as ch
        key = (self.map, ch.SEASON)
        if key != getattr(self, "_frames_key", None):
            m = self.map.name if hasattr(self.map, "name") else self.map
            if self.key in ch.NPCS:
                look = ch.look_for(self.key, m)
            else:                                   # figurantes
                look = ch.dress(None, self.data["look"])
            self._frames_cur, self._frames_key = art.character_frames(look), key
            self._look_cur, self._look_key = look, poses.look_key(look)
        return self._frames_cur

    def draw(self, surf, cam):
        frames = self.current_frames()
        cx = (self.fx + 0.5) * TILE - cam[0]
        cy = self.base_y - cam[1]
        lift = self.seat_lift if self.seat_t >= 0.1 else None
        pose = self.pose_now()
        umb = UMBRELLA["on"] and self.map == "city" and lift is None and not pose
        if lift is None and not pose and not umb:
            img, bob = idle_frame(frames, self.dir, self.moving, self.anim, self.phase)
            draw_shadow(surf, int(cx), int(cy) + SCALE)
            x, y = int(cx - img.get_width() // 2), int(cy - img.get_height() + FOOT + bob)
            surf.blit(img, (x, y))
            self.img_top = (x + cam[0], y + cam[1])
            return
        t = time.monotonic() + self.phase
        blink = t % 3.7 < 0.13
        bob = 1 if (t % 1.6) < 0.8 else 0
        swing = (0, 1, 0, 2)[int(self.swinging * 6) % 4] if self.swinging > 0 and self.dir != "up" else 0
        arms = face = None
        walk, lean, tip = 0, 0, False
        if pose:
            arms, face = pose.get("arms"), pose.get("face")
            blink = pose.get("blink", blink)
            bob = pose.get("bob", bob)
            walk, lean, tip = pose.get("walk", 0), pose.get("lean", 0), pose.get("tiptoe", False)
            if pose.get("arms") or pose.get("face"):
                swing = 0
        elif umb:
            arms = "umbrella"
            if self.moving:
                walk = int(self.anim) % 4
                bob, blink = (1 if walk in (1, 3) else 0), False
        img = poses.frame(self._look_cur, self.dir, lift, arms, face, blink, swing, self._look_key, walk, lean, tip)
        x = int(cx - img.get_width() // 2)
        if lift is None:
            draw_shadow(surf, int(cx), int(cy) + SCALE)
            y = int(cy - img.get_height() + FOOT + bob)
        else:
            plop = SCALE if self.seat_t < 0.18 else 0      # "plof" ao sentar
            y = int(cy - img.get_height() + FOOT + bob + poses.seat_offset(lift) + plop)
        if umb:
            draw_umbrella(surf, self._look_cur, self.dir, x, y, umbrella_color(self.key), "back")
        surf.blit(img, (x, y))
        if umb:
            draw_umbrella(surf, self._look_cur, self.dir, x, y, umbrella_color(self.key), "front")
        self.img_top = (x + cam[0], y + cam[1])
        if pose and pose.get("held"):
            hd = pose["held"]
            draw_held(surf, x, y, self._look_cur, self.dir, hd["item"], hd.get("where", "hold"), hd.get("tilt", 0.0),
                      hd.get("bites", 0))


CAR_COLORS = [(200, 50, 60), (60, 110, 200), (240, 240, 245), (40, 40, 48), (230, 190, 60), (120, 40, 190),
              (70, 150, 110), (150, 150, 160)]


class Car:
    LEN = 32 * SCALE            # comprimento do carro (o desenho tem 32 px de arte)
    GAP = 0.45 * TILE           # distância que um carro deixa para o da frente e para quem está na rua
    LOOK = 2.6 * TILE           # até onde o motorista olha à frente para frear

    def __init__(self, lane_y, direction, map_w):
        self.lane_y = lane_y
        self.dir = direction
        self.speed = random.uniform(3.5, 6.5) * TILE
        self.v = self.speed                     # velocidade atual (freia e acelera aos poucos)
        self.color = random.choice(CAR_COLORS)
        self.x = -2.5 * TILE if direction > 0 else (map_w + 1.5) * TILE
        self.map_w = map_w

    @property
    def base_y(self):
        return (self.lane_y + 1) * TILE - SCALE

    @property
    def front(self):
        return self.x + self.LEN if self.dir > 0 else self.x

    def rect(self):
        """Parte do carro que bloqueia a jogadora (a lataria, sem o teto)."""
        return pygame.Rect(int(self.x + SCALE), int(self.base_y - 10 * SCALE), self.LEN - 2 * SCALE, 10 * SCALE)

    def _room(self, cars, walkers):
        """Quanto o carro ainda pode andar até o carro da frente ou até alguém na pista."""
        room = float("inf")
        for c in cars:
            if c is not self and c.lane_y == self.lane_y and (c.x - self.x) * self.dir > 0:
                room = min(room, abs(c.x - self.x) - self.LEN - self.GAP)
        top, bottom = self.lane_y * TILE, (self.lane_y + 1) * TILE + SCALE     # pés dentro desta faixa
        for (wx, wy) in walkers:
            if not top <= wy <= bottom:
                continue
            d = (wx - self.front) * self.dir           # > 0: à frente do para-choque
            if -self.LEN - TILE * 0.3 < d < self.LOOK + self.GAP:
                room = min(room, d - self.GAP)
        return max(0.0, room)

    def update(self, dt, cars, walkers=()):
        room = self._room(cars, walkers)
        # freia como um carro de verdade: a velocidade máxima é a que ainda dá para parar na folga que sobra
        brake = math.sqrt(2 * 8 * TILE * room)
        self.v = min(self.speed, self.v + 4 * TILE * dt, brake)
        step = min(self.v * dt, room)
        self.x += self.dir * step
        return -4 * TILE < self.x < (self.map_w + 4) * TILE

    def draw(self, surf, cam):
        img = art.car_sprite(self.color, self.dir > 0)
        x = int(self.x - cam[0])
        y = int(self.base_y - img.get_height() - cam[1])
        if -120 < x < surf.get_width() + 20:
            draw_shadow(surf, x + img.get_width() // 2, int(self.base_y - cam[1]) + 2, 28 * SCALE)
            surf.blit(img, (x, y))

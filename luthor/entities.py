"""Jogadora, personagens (NPCs) com rotina diária e carros."""
import math
import random
import time

import pygame

from . import art
from . import sprites  # noqa: F401  (personagens no estilo Stardew)
from .config import TILE, SCALE

FOOT = 2 * SCALE  # distância do pé até a base do tile
from .world import CITY_DOORS, INTERIOR_DOORS

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

# de acordo com o retrato: cabelo escuro ondulado, casaco caramelo por cima de blusa branca
PLAYER_LOOK = dict(hair=(36, 24, 24), skin=(236, 198, 170), cloth=(194, 148, 104), accent=(244, 240, 232),
                   pants=(34, 30, 44), shoes=(22, 16, 26), style="wavy", eyes=(56, 168, 96), outfit="blazer",
                   height=1)

_shadow_cache = {}


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
    def __init__(self):
        self.frames = art.character_frames(PLAYER_LOOK)
        self.x = self.y = 0.0
        self.dir = "down"
        self.moving = False
        self.anim = 0.0

    def place_tile(self, tx, ty, d=None):
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
        img, bob = idle_frame(self.frames, self.dir, self.moving, self.anim, 0.0)
        sx, sy = int(self.x - cam[0]), int(self.y - cam[1])
        draw_shadow(surf, sx, sy + SCALE)
        surf.blit(img, (sx - img.get_width() // 2, sy - img.get_height() + FOOT + bob))


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
            sch = [e for e in sch]
            if sch and sch[0][1] is None:
                sch[0] = (sch[0][0], "home", 20, 7, "up")
            if sch[-1][1] is None:
                sch[-1] = (sch[-1][0], "home", 14, 12, "left")
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

    def _leg_target(self, world):
        gmap = self.goal[0]
        if self.map == gmap:
            return (self.goal[1], self.goal[2])
        if self.map != "city":
            return INTERIOR_DOORS[self.map]
        if gmap is None:
            m = world["city"]
            return min(m.spawn_edges, key=lambda e: abs(e[0] - self.fx) + abs(e[1] - self.fy))
        return CITY_DOORS[gmap]

    def _finish_leg(self, world):
        gmap, gx, gy, gd = self.goal
        if self.map == gmap and self.tile == (gx, gy):
            self.dir = gd
            self.arrived = True
            return
        if self.map != "city":
            cx, cy = CITY_DOORS[self.map]
            self.place("city", cx, cy + 1, "down")
        elif gmap is None:
            self.map = None
            self.arrived = True
        else:
            ix, iy = INTERIOR_DOORS[gmap]
            self.place(gmap, ix, iy - 1, "up")
        self.path = None

    def update(self, dt, world):
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
        return self._frames_cur

    def draw(self, surf, cam):
        img, bob = idle_frame(self.current_frames(), self.dir, self.moving, self.anim, self.phase)
        cx = (self.fx + 0.5) * TILE - cam[0]
        cy = self.base_y - cam[1]
        draw_shadow(surf, int(cx), int(cy) + SCALE)
        surf.blit(img, (int(cx - img.get_width() // 2), int(cy - img.get_height() + FOOT + bob)))


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

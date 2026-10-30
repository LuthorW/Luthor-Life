"""Efeitos de ambiente: borboletas, vagalumes, pétalas, brilhos na água e luz pelas janelas."""
import math
import random

import pygame

from .config import TILE, SCREEN_W, SCREEN_H

SEASON = "spring"           # trocada por seasons.set_season
LEAF_COLORS = [(226, 136, 52), (196, 98, 38), (240, 186, 80), (192, 70, 46)]

BUTTERFLY_COLORS = [(255, 170, 210), (255, 230, 120), (180, 200, 255), (255, 255, 255), (200, 160, 255)]


class Ambient:
    def __init__(self):
        self.butterflies = []
        self.fireflies = []
        self.petals = []
        self.glints = []
        self.t = 0.0
        self._beam_cache = {}
        self._glow = self._make_glow()

    def _make_glow(self):
        s = pygame.Surface((24, 24))
        s.fill((0, 0, 0))
        for r in range(12, 0, -1):
            k = (1 - r / 12) ** 1.5
            pygame.draw.circle(s, (int(200 * k), int(255 * k), int(120 * k)), (12, 12), r)
        return s

    def reset(self):
        self.butterflies.clear()
        self.fireflies.clear()
        self.petals.clear()
        self.glints.clear()

    def update(self, dt, m, cam, minutes, weather):
        self.t += dt
        if not m.outdoor:
            self.reset()
            return
        x0, y0 = cam[0] - 100, cam[1] - 100
        x1, y1 = cam[0] + SCREEN_W + 400, cam[1] + SCREEN_H + 300
        day = 7 * 60 <= minutes <= 18 * 60 and weather != "chuva" and SEASON in ("spring", "summer")
        night = (minutes >= 19 * 60 + 30 or minutes < 5 * 60) and SEASON != "winter"
        # borboletas
        self.butterflies = [b for b in self.butterflies if x0 < b["x"] < x1 and y0 < b["y"] < y1 and day]
        if day and len(self.butterflies) < 5 and random.random() < dt * 0.8:
            self.butterflies.append(dict(x=random.uniform(x0 + 100, x1 - 100), y=random.uniform(y0 + 100, y1 - 100),
                                         a=random.uniform(0, math.tau), c=random.choice(BUTTERFLY_COLORS),
                                         ph=random.uniform(0, 6)))
        for b in self.butterflies:
            b["a"] += random.uniform(-2.5, 2.5) * dt
            b["x"] += math.cos(b["a"]) * 38 * dt
            b["y"] += math.sin(b["a"]) * 26 * dt + math.sin(self.t * 5 + b["ph"]) * 10 * dt
        # vagalumes
        self.fireflies = [f for f in self.fireflies if night and x0 < f["x"] < x1 and y0 < f["y"] < y1]
        max_ff = 30 if SEASON == "summer" else (6 if SEASON == "autumn" else 18)
        if night and weather != "chuva" and len(self.fireflies) < max_ff and random.random() < dt * 3:
            self.fireflies.append(dict(x=random.uniform(x0 + 100, x1 - 100), y=random.uniform(y0 + 100, y1 - 100),
                                       ph=random.uniform(0, 6), vx=random.uniform(-12, 12), vy=random.uniform(-8, 8)))
        for f in self.fireflies:
            f["x"] += (f["vx"] + math.sin(self.t + f["ph"]) * 8) * dt
            f["y"] += (f["vy"] + math.cos(self.t * 0.7 + f["ph"]) * 6) * dt
        # pétalas das cerejeiras (primavera) e folhas secas caindo das árvores (outono)
        falls = {"spring": ("tree2",), "autumn": ("tree", "tree2", "tree3")}.get(SEASON, ())
        if falls and (7 * 60 <= minutes <= 18 * 60 or minutes < 19 * 60):
            for o in m.objects:
                if o.kind in falls and x0 < o.x * TILE < x1 and y0 < o.y * TILE < y1 and random.random() < dt * 0.9:
                    self.petals.append(dict(x=o.x * TILE + random.uniform(-0.2, 1.2) * TILE, y=o.y * TILE - 1.4 * TILE + random.uniform(0, 0.8) * TILE,
                                            life=random.uniform(2.5, 4.5), ph=random.uniform(0, 6)))
        for p in self.petals:
            p["life"] -= dt
            p["y"] += 22 * dt
            p["x"] += math.sin(self.t * 2 + p["ph"]) * 18 * dt + 6 * dt
        self.petals = [p for p in self.petals if p["life"] > 0][-80:]
        # neve caindo no inverno (mais forte nos dias de "chuva", que no inverno viram neve)
        flakes = getattr(self, "flakes", [])
        if SEASON == "winter":
            want = 160 if weather == "chuva" else 45
            while len(flakes) < want:
                flakes.append(dict(x=random.uniform(0, SCREEN_W), y=random.uniform(-SCREEN_H, SCREEN_H),
                                   v=random.uniform(30, 70), r=random.choice((2, 2, 3, 4)), ph=random.uniform(0, 6)))
            for f in flakes:
                f["y"] += f["v"] * dt
                f["x"] += math.sin(self.t * 1.3 + f["ph"]) * 14 * dt
                if f["y"] > SCREEN_H:
                    f["y"] = random.uniform(-40, -4)
                    f["x"] = random.uniform(0, SCREEN_W)
            flakes = flakes[:want]
        else:
            flakes = []
        self.flakes = flakes
        # brilhos na água
        if m.anim_tiles and random.random() < dt * 6:
            cand = [(x, y) for (x, y, t) in random.sample(m.anim_tiles, min(40, len(m.anim_tiles)))
                    if x0 < x * TILE < x1 and y0 < y * TILE < y1]
            if cand:
                x, y = random.choice(cand)
                self.glints.append(dict(x=x * TILE + random.randint(6, 40), y=y * TILE + random.randint(6, 40), life=0.5))
        for g in self.glints:
            g["life"] -= dt
        self.glints = [g for g in self.glints if g["life"] > 0]

    def draw_world(self, surf, cam):
        """Desenhado junto do mundo (antes do escurecimento da noite)."""
        for p in self.petals:
            x, y = int(p["x"] - cam[0]), int(p["y"] - cam[1])
            if SEASON == "autumn":
                c = LEAF_COLORS[int(p["ph"] * 10) % len(LEAF_COLORS)]
                pygame.draw.rect(surf, c, (x, y, 5, 3))
                pygame.draw.rect(surf, (120, 60, 30), (x + 2, y + 1, 1, 1))
            else:
                pygame.draw.rect(surf, (255, 200, 222), (x, y, 4, 3))
                pygame.draw.rect(surf, (255, 236, 244), (x, y, 2, 2))
        for g in self.glints:
            x, y = int(g["x"] - cam[0]), int(g["y"] - cam[1])
            k = int(3 * (g["life"] / 0.5)) + 1
            pygame.draw.line(surf, (255, 255, 255), (x - k, y), (x + k, y))
            pygame.draw.line(surf, (255, 255, 255), (x, y - k), (x, y + k))
        for b in self.butterflies:
            x, y = int(b["x"] - cam[0]), int(b["y"] - cam[1])
            flap = abs(math.sin(self.t * 14 + b["ph"]))
            w = int(2 + flap * 5)
            c = b["c"]
            pygame.draw.ellipse(surf, c, (x - w - 1, y - 4, w, 6))
            pygame.draw.ellipse(surf, c, (x + 1, y - 4, w, 6))
            pygame.draw.rect(surf, (60, 40, 50), (x - 1, y - 4, 2, 6))

    def draw_snow(self, surf):
        """Flocos de neve (em coordenadas de tela), por cima de tudo."""
        for f in getattr(self, "flakes", []):
            x, y, r = int(f["x"]), int(f["y"]), f["r"]
            pygame.draw.rect(surf, (236, 242, 255), (x, y, r, r))
            if r > 2:
                pygame.draw.rect(surf, (255, 255, 255), (x, y, r - 1, r - 1))

    def draw_glow(self, surf, cam):
        """Desenhado depois do escurecimento (brilham no escuro)."""
        for f in self.fireflies:
            x, y = int(f["x"] - cam[0]), int(f["y"] - cam[1])
            k = 0.5 + 0.5 * math.sin(self.t * 3 + f["ph"])
            if k > 0.15:
                surf.blit(self._glow, (x - 12, y - 12), special_flags=pygame.BLEND_RGB_ADD)
                pygame.draw.rect(surf, (230, 255, 170), (x - 1, y - 1, 3, 3))

    def draw_window_light(self, surf, m, cam, minutes):
        """Raios de sol entrando pelas janelas dos interiores durante o dia."""
        if m.outdoor or not (7 * 60 <= minutes <= 17 * 60 + 30):
            return
        strength = 1.0 - abs(minutes - 12 * 60) / (6 * 60)
        alpha = int(18 + 22 * max(0.0, strength))
        for o in m.wall_decor:
            if o.kind not in ("window", "window_big"):
                continue
            w = o.w * TILE
            key = (w, alpha)
            beam = self._beam_cache.get(key)
            if beam is None:
                beam = pygame.Surface((w + TILE * 2, TILE * 3), pygame.SRCALPHA)
                pygame.draw.polygon(beam, (255, 240, 200, alpha),
                                    [(6, 0), (w - 6, 0), (w - 6 + TILE * 1.4, TILE * 3), (6 + TILE * 1.4, TILE * 3)])
                self._beam_cache[key] = beam
            surf.blit(beam, (o.x * TILE - cam[0], (o.y + o.h) * TILE - cam[1]))

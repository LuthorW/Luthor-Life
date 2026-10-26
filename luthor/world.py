"""Mapas de National City."""
from collections import deque
import random

import pygame

from . import art, scenery
from .config import TILE, SCALE

SOLID_TILES = {"wall", "wall_top", "glass", "water", "sea", "sea_foam", "fountain", "void"}
WATER_TILES = {"water": "pond", "sea": "sea", "sea_foam": "sea"}
ANIMATED = {"water", "sea", "sea_foam", "fountain"}

# kind: (largura, altura, sólido, camada). camada: obj | decal (chão) | wall (decoração de parede)
OBJECT_DEFS = {
    "tree": (1, 1, True, "obj"), "tree2": (1, 1, True, "obj"), "tree3": (1, 1, True, "obj"),
    "palm": (1, 1, True, "obj"), "hedge": (1, 1, True, "obj"), "planter": (1, 1, True, "obj"),
    "bush": (1, 1, True, "obj"), "bush2": (1, 1, True, "obj"), "bush3": (1, 1, True, "obj"),
    "lamp": (1, 1, True, "obj"), "bench": (1, 1, True, "obj"), "statue": (1, 1, True, "obj"),
    "hydrant": (1, 1, True, "obj"), "busstop": (2, 1, True, "obj"), "umbrella": (1, 1, True, "obj"),
    "umbrella2": (1, 1, True, "obj"), "lifeguard": (2, 1, True, "obj"), "boat": (3, 1, True, "obj"),
    "kiosk": (3, 1, True, "obj"), "signboard": (1, 1, True, "obj"),
    "bed": (2, 2, True, "obj"), "bed2": (3, 2, True, "obj"), "nightstand": (1, 1, True, "obj"),
    "wardrobe": (2, 1, True, "obj"), "tv": (2, 1, True, "obj"), "tv_big": (3, 1, True, "obj"),
    "sofa": (3, 1, True, "obj"), "sofa_grey": (3, 1, True, "obj"), "armchair": (1, 1, True, "obj"),
    "coffee_table": (2, 1, True, "obj"), "kitchen": (3, 1, True, "obj"), "kitchen2": (2, 1, True, "obj"),
    "island": (3, 1, True, "obj"), "stove": (1, 1, True, "obj"), "fridge": (1, 1, True, "obj"),
    "fridge2": (2, 1, True, "obj"), "plant": (1, 1, True, "obj"), "plant_big": (1, 1, True, "obj"),
    "bookshelf": (2, 1, True, "obj"), "bookshelf2": (2, 1, True, "obj"), "bookshelf3": (2, 1, True, "obj"),
    "ceo_desk": (3, 1, True, "obj"), "desk": (3, 1, True, "obj"), "desk_home": (3, 1, True, "obj"),
    "desk_editor": (3, 1, True, "obj"), "desk_news": (2, 1, True, "obj"), "reception": (3, 1, True, "obj"),
    "station": (1, 1, True, "obj"), "terminal": (1, 1, True, "obj"), "shipbox": (2, 1, True, "obj"),
    "shipbox_pier": (2, 1, True, "obj"), "coffee": (1, 1, True, "obj"), "table": (1, 1, True, "obj"),
    "table_it": (1, 1, True, "obj"), "dining": (2, 1, True, "obj"), "chair": (1, 1, False, "obj"),
    "chair_blue": (1, 1, False, "obj"), "stool": (1, 1, False, "obj"),
    "cafe_counter": (6, 1, True, "obj"), "shop_counter": (4, 1, True, "obj"), "counter_it": (6, 1, True, "obj"),
    "bar_counter": (6, 1, True, "obj"), "cafe_shelf": (3, 1, True, "obj"), "bottle_shelf": (3, 1, True, "obj"),
    "wine_shelf": (3, 1, True, "obj"), "oven": (2, 1, True, "obj"), "produce": (2, 1, True, "obj"),
    "produce2": (2, 1, True, "obj"), "flowerstand": (2, 1, True, "obj"), "printer": (1, 1, True, "obj"),
    "cooler": (1, 1, True, "obj"), "bathtub": (3, 1, True, "obj"), "sink": (1, 1, True, "obj"),
    "aquarium": (3, 1, True, "obj"), "arcade": (1, 1, True, "obj"), "pool": (2, 2, True, "obj"),
    "jukebox": (1, 1, True, "obj"),
    # novos: horta, terraço, cinema, adoção
    "plot": (1, 1, True, "obj"), "telescope": (1, 1, True, "obj"), "petbed": (1, 1, False, "obj"),
    "lounger": (1, 2, True, "obj"), "string_lights": (6, 1, False, "wall"), "railing_plant": (1, 1, True, "obj"),
    "watering": (1, 1, True, "obj"), "petstand": (2, 1, True, "obj"),
    "cine_screen": (10, 1, False, "wall"), "seat": (1, 1, False, "obj"), "ticket": (3, 1, True, "obj"),
    "popcorn": (1, 1, True, "obj"), "film_poster": (1, 1, False, "wall"), "film_poster2": (1, 1, False, "wall"),
    "rope": (1, 1, True, "obj"), "glass_door": (1, 1, False, "wall"),
    # Conti Moretti Hospitais
    "hreception": (4, 1, True, "obj"), "hdesk": (2, 1, True, "obj"), "exambed": (1, 2, True, "obj"),
    "hbed": (1, 2, True, "obj"), "hchair": (1, 1, False, "obj"), "cabinet": (1, 1, True, "obj"),
    "pharma_counter": (3, 1, True, "obj"), "pharma_shelf": (3, 1, True, "obj"), "vending": (1, 1, True, "obj"),
    "monitor": (1, 1, True, "obj"), "cm_rug": (4, 3, False, "decal"), "hsign": (1, 1, False, "wall"),
    "cm_wall_logo": (2, 1, False, "wall"), "plaque": (1, 1, False, "wall"),
    "rug": (4, 3, False, "decal"), "rug_big": (5, 3, False, "decal"), "logo_rug": (6, 3, False, "decal"),
    "rug_red": (3, 2, False, "decal"), "rug_bed": (3, 2, False, "decal"), "rug_green": (4, 3, False, "decal"),
    "catco_rug": (6, 2, False, "decal"),
    "window": (1, 1, False, "wall"), "window_big": (2, 1, False, "wall"), "painting": (1, 1, False, "decal"),
    "painting2": (1, 1, False, "decal"), "poster": (1, 1, False, "decal"), "poster2": (1, 1, False, "decal"),
    "menuboard": (2, 1, False, "decal"), "neon": (2, 1, False, "wall"), "tv_wall": (4, 1, False, "decal"),
    # cenário estilo Stardew (scenery.py)
    "pine": (1, 1, True, "obj"), "tallgrass": (1, 1, False, "obj"), "rock": (1, 1, True, "obj"),
    "rock_big": (1, 1, True, "obj"), "stump": (1, 1, True, "obj"), "log": (2, 1, True, "obj"),
    "fence": (1, 1, True, "obj"), "fence_v": (1, 1, True, "obj"), "picnic": (2, 1, True, "obj"),
    "flowerpot": (1, 1, True, "obj"), "flowerpot2": (1, 1, True, "obj"), "gazebo": (4, 2, True, "obj"),
    "lighthouse": (3, 2, True, "obj"), "towel": (2, 1, False, "decal"), "towel2": (2, 1, False, "decal"),
    "ricci_map": (2, 1, False, "wall"), "sandcastle": (1, 1, True, "obj"), "bench_l": (1, 1, True, "obj"), "bench_r": (1, 1, True, "obj"),
}

# Área que realmente bloqueia a jogadora (x, y, largura, altura em pixels de arte, a partir do canto
# do objeto). Postes, bancos, árvores e arbustos ocupam só a base: dá para contornar sem enroscar.
# NPCs continuam desviando do tile inteiro.
HITBOXES = {
    "lamp": (5, 10, 6, 6), "hydrant": (4, 8, 8, 8), "signboard": (5, 10, 6, 6), "bench": (1, 6, 14, 9),
    "tree": (4, 8, 8, 8), "tree2": (4, 8, 8, 8), "tree3": (4, 8, 8, 8), "pine": (5, 8, 6, 8),
    "palm": (4, 9, 8, 7), "bush": (2, 5, 12, 11), "bush2": (2, 5, 12, 11), "bush3": (2, 5, 12, 11),
    "planter": (2, 5, 12, 11), "umbrella": (6, 9, 4, 7), "umbrella2": (6, 9, 4, 7), "rock": (3, 7, 10, 9),
    "rock_big": (1, 5, 14, 11), "stump": (3, 6, 10, 10), "log": (1, 6, 30, 9), "fence": (0, 7, 16, 8),
    "fence_v": (5, 0, 6, 16), "flowerpot": (3, 8, 10, 8), "flowerpot2": (3, 8, 10, 8), "sandcastle": (2, 7, 12, 9),
    "bench_r": (3, 7, 11, 9), "bench_l": (2, 7, 11, 9),
}

COUNTERS = {"ceo_desk", "desk", "desk_home", "desk_editor", "desk_news", "reception", "cafe_counter", "kitchen",
            "shop_counter", "counter_it", "bar_counter", "island"}
PLOT_SLOTS = [(x, y) for y in (3, 4) for x in range(3, 9)]    # canteiros do terraço


class Obj:
    def __init__(self, kind, x, y, data=None):
        self.kind = kind
        self.x, self.y = x, y
        w, h, solid, layer = OBJECT_DEFS[kind]
        self.w, self.h, self.solid, self.layer = w, h, solid, layer
        self.data = data

    def covers(self, tx, ty):
        return self.x <= tx < self.x + self.w and self.y <= ty < self.y + self.h

    @property
    def base_y(self):
        return (self.y + self.h) * TILE


class Building:
    def __init__(self, name, style, x, y, w, h, extra, door_x, target):
        self.name, self.style = name, style
        self.x, self.y, self.w, self.h, self.extra = x, y, w, h, extra
        self.door = (door_x, y + h - 1)
        self.target = target

    @property
    def base_y(self):
        return (self.y + self.h) * TILE


class GameMap:
    def __init__(self, name, w, h, outdoor=False, label=""):
        self.name, self.w, self.h, self.outdoor, self.label = name, w, h, outdoor, label
        self.tiles = [["grass"] * w for _ in range(h)]
        self.objects = []
        self.buildings = []
        self.doors = {}
        self.solid = None
        self.floor_surface = None
        self.anim_tiles = []
        self.spawn_edges = []
        self.car_lanes = []
        self.wall_decor = []
        self.water_edges = []

    def add(self, kind, x, y, data=None):
        o = Obj(kind, x, y, data)
        self.objects.append(o)
        return o

    def fill(self, x0, y0, x1, y1, t):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.tiles[y][x] = t

    def finalize(self):
        self.solid = [[False] * self.w for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                t = self.tiles[y][x]
                if t in SOLID_TILES:
                    self.solid[y][x] = True
                if t in ANIMATED:
                    self.anim_tiles.append((x, y, t))
        for o in self.objects:
            if o.solid:
                for yy in range(o.y, o.y + o.h):
                    for xx in range(o.x, o.x + o.w):
                        if self.in_bounds(xx, yy):
                            self.solid[yy][xx] = True
        for b in self.buildings:
            for yy in range(b.y, b.y + b.h):
                for xx in range(b.x, b.x + b.w):
                    self.solid[yy][xx] = not ((xx, yy) == b.door and b.target)
        for (dx, dy) in self.doors:
            self.solid[dy][dx] = False
        self.hitboxes = {}
        for o in self.objects:
            hb = HITBOXES.get(o.kind) if o.solid else None
            if not hb:
                continue
            r = pygame.Rect(o.x * TILE + hb[0] * SCALE, o.y * TILE + hb[1] * SCALE, hb[2] * SCALE, hb[3] * SCALE)
            for yy in range(o.y, o.y + o.h):
                for xx in range(o.x, o.x + o.w):
                    if self.in_bounds(xx, yy) and self.tiles[yy][xx] not in SOLID_TILES                             and not self.building_at(xx, yy):
                        self.hitboxes[(xx, yy)] = r
        self.wall_decor = [o for o in self.objects if o.layer == "wall"]
        self._build_floor()

    def _build_floor(self):
        if getattr(self, "open_air", False):
            surf = pygame.Surface((self.w * TILE, self.h * TILE), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
        else:
            surf = pygame.Surface((self.w * TILE, self.h * TILE))
            surf.fill((0, 0, 0))
        r = random.Random(self.name)
        variants = ("grass", "flowers", "pavement", "road", "dirt", "wood", "wood_dark", "carpet", "sand",
                    "plaza", "boardwalk", "pier", "carpet_blue", "office", "terracotta")
        for y in range(self.h):
            for x in range(self.w):
                t = self.tiles[y][x]
                if t == "wall":
                    below = self.tiles[y + 1][x] if y + 1 < self.h else "wall"
                    t = "wall" if below not in ("wall", "wall_top", "void", "glass", "door") else "wall_top"
                    if y == self.h - 1:
                        t = "wall_top"
                if t in ("void",) or t in ANIMATED:
                    continue
                v = r.randrange(4) if t in variants else 0
                surf.blit(art.tile(t, v), (x * TILE, y * TILE))
        # bordas suaves: grama avançando sobre caminhos, areia e calçadas
        grassy = ("grass", "flowers")
        skip = grassy + ("wall", "wall_top", "glass", "void", "door") + tuple(ANIMATED)
        for y in range(self.h):
            for x in range(self.w):
                t = self.tiles[y][x]
                if t in skip:
                    continue
                for side, (dx, dy) in (("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))):
                    if self.tile_at(x + dx, y + dy) in grassy:
                        surf.blit(art.grass_edge(side), (x * TILE, y * TILE))
        for (x, y, t) in self.anim_tiles:
            if t == "sea_foam":
                continue
            for side, (dx, dy) in (("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))):
                n = self.tile_at(x + dx, y + dy)
                if n not in ANIMATED and n != "void":
                    self.water_edges.append((x, y, side))
            # cantos arredondados do lago quando a margem é grama
            for which, (dx, dy) in (("c_tl", (-1, -1)), ("c_tr", (1, -1)), ("c_bl", (-1, 1)), ("c_br", (1, 1))):
                if self.tile_at(x + dx, y) in grassy and self.tile_at(x, y + dy) in grassy:
                    self.water_edges.append((x, y, which))
        # sombras suaves sob os prédios
        for o in self.objects:
            if o.layer == "decal":
                spr = art.object_sprite(o.kind)
                surf.blit(spr, (o.x * TILE, (o.y + o.h) * TILE - spr.get_height()))
        scenery.decorate_floor(self, surf)
        sh = pygame.Surface((TILE, TILE // 3), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 55))
        for b in self.buildings:
            for xx in range(b.x, b.x + b.w + 1):
                if self.in_bounds(xx, b.y + b.h):
                    surf.blit(sh, (xx * TILE, (b.y + b.h) * TILE))
            side = pygame.Surface((TILE // 3, b.h * TILE), pygame.SRCALPHA)
            side.fill((0, 0, 0, 45))
            surf.blit(side, ((b.x + b.w) * TILE, (b.y + 1) * TILE))
        self.floor_surface = surf

    def in_bounds(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def is_solid(self, x, y):
        if not self.in_bounds(x, y):
            return True
        return self.solid[y][x]

    def tile_at(self, x, y):
        return self.tiles[y][x] if self.in_bounds(x, y) else "void"

    def object_at(self, x, y):
        for o in self.objects:
            if o.layer == "obj" and o.covers(x, y):
                return o
        return None

    def building_at(self, x, y):
        for b in self.buildings:
            if b.x <= x < b.x + b.w and b.y <= y < b.y + b.h:
                return b
        return None

    def find_path(self, start, goal, max_nodes=16000):
        if start == goal:
            return []
        if self.is_solid(*goal) and goal not in self.doors:
            return None
        prev = {start: None}
        q = deque([start])
        while q and len(prev) < max_nodes:
            cur = q.popleft()
            if cur == goal:
                break
            x, y = cur
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                n = (nx, ny)
                if n in prev:
                    continue
                if self.is_solid(nx, ny) and n != goal:
                    continue
                prev[n] = cur
                q.append(n)
        if goal not in prev:
            return None
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path


# ---------------------------------------------------------------------------
# Portas
# ---------------------------------------------------------------------------
CITY_DOORS = {"home": (6, 15), "hq": (21, 15), "cafe": (35, 15), "catco": (48, 15),
              "books": (55, 31), "market": (64, 31), "trattoria": (81, 31), "bar": (55, 45), "cinema": (65, 45),
              "hospital": (78, 15), "ricci": (64, 15)}
INTERIOR_DOORS = {"home": (16, 15), "hq": (12, 17), "cafe": (7, 10), "catco": (11, 14),
                  "books": (8, 11), "market": (8, 11), "trattoria": (10, 12), "bar": (8, 11), "cinema": (10, 13),
                  "hospital": (13, 16), "ricci": (10, 13)}
TERRACE_DOOR = (15, 1)      # porta da sala para o terraço (na cobertura)
STATION_SLOTS = [(x, y) for y in (4, 7) for x in (12, 14, 16, 18, 20, 22)]
HOME_BED = (3, 4)          # onde a jogadora acorda


# ---------------------------------------------------------------------------
# Cidade
# ---------------------------------------------------------------------------
# Versão 2 do mapa: a cidade antiga (72x56) foi "esticada" com as faixas abaixo
# (coluna/linha antiga onde a faixa entra, quantidade) e ganhou o Jardim do Mirante,
# o Bosque Bayside e o farol a leste. old_city_xy converte posições de saves antigos.
CITY_LAYOUT = 2
_OLD_X = ((12, 2), (26, 2), (34, 3), (49, 3), (59, 3), (70, 3))
_OLD_Y = ((2, 3), (20, 2), (30, 3), (39, 2), (47, 2))


def old_city_xy(x, y):
    return (x + sum(n for c, n in _OLD_X if c <= x), y + sum(n for c, n in _OLD_Y if c <= y))


CITY_W, CITY_H = 112, 80        # o mar vai até a linha 79: a câmera desce e mostra o oceano
# áreas verdes (x0, y0, x1, y1): figurantes passeiam e coletáveis nascem nelas
CITY_AREAS = {
    "park": [(1, 23, 39, 48)],          # Parque Central
    "woods": [(88, 22, 110, 48)],       # Bosque Bayside
    "garden": [(84, 3, 110, 14)],       # Jardim do Mirante
    "beach": [(0, 55, CITY_W - 1, 60)],
}


def in_area(name, x, y):
    return any(x0 <= x <= x1 and y0 <= y <= y1 for (x0, y0, x1, y1) in CITY_AREAS[name])


def _scatter(m, kinds, area, n, rnd, gap=2, tiles=("grass",), avoid=()):
    """Espalha objetos em tiles livres, mantendo distância entre eles (nunca fecha passagens)."""
    x0, y0, x1, y1 = area
    busy = set()
    for o in m.objects:
        if o.layer == "obj":
            for yy in range(o.y, o.y + o.h):
                for xx in range(o.x, o.x + o.w):
                    busy.add((xx, yy))
    for b in m.buildings:
        for yy in range(b.y, b.y + b.h):
            for xx in range(b.x, b.x + b.w):
                busy.add((xx, yy))
    cand = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if m.tiles[y][x] in tiles]
    rnd.shuffle(cand)
    placed = 0
    for (x, y) in cand:
        if placed >= n:
            break
        if any((x + dx, y + dy) in busy for dx in range(-gap, gap + 1) for dy in range(-gap, gap + 1)):
            continue
        if any(m.tile_at(x + dx, y + dy) in avoid for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue
        m.add(rnd.choice(kinds), x, y)
        busy.add((x, y))
        placed += 1


def build_city():
    W, H = CITY_W, CITY_H
    m = GameMap("city", W, H, outdoor=True, label="National City")
    m.fill(0, 0, W - 1, H - 1, "grass")
    # --- Avenida Siegel (horizontal) ---------------------------------------
    m.fill(1, 16, W - 2, 17, "pavement")
    m.fill(0, 18, W - 1, 18, "road_line_b")
    m.fill(0, 19, W - 1, 19, "road_line_t")
    m.fill(1, 20, W - 2, 21, "pavement")
    for cx in (20, 21, 22, 64, 65, 66, 97, 98):
        m.tiles[18][cx] = "cross"; m.tiles[19][cx] = "cross"
    m.fill(15, 14, 55, 15, "pavement")      # calçada larga da torre, do café e da CatCo
    # --- Rua Bayside (vertical) --------------------------------------------
    m.fill(41, 22, 42, 48, "pavement")
    m.fill(45, 22, 46, 48, "pavement")
    m.fill(43, 20, 43, 51, "road_line_r")
    m.fill(44, 20, 44, 51, "road_line_l")
    m.fill(43, 18, 44, 19, "road")
    for yy in (20, 21):
        m.tiles[yy][43] = "cross_v"; m.tiles[yy][44] = "cross_v"
    # --- Orla ----------------------------------------------------------------
    m.fill(1, 49, W - 2, 49, "pavement")
    m.fill(0, 50, W - 1, 50, "road_line_b")
    m.fill(0, 51, W - 1, 51, "road_line_t")
    m.fill(43, 50, 44, 51, "road")
    m.fill(1, 52, W - 2, 52, "pavement")
    for cx in (19, 20, 59, 60, 98, 99):
        m.tiles[50][cx] = "cross"; m.tiles[51][cx] = "cross"
    m.fill(0, 53, W - 1, 54, "boardwalk")
    m.fill(0, 55, W - 1, 60, "sand")
    m.fill(0, 61, W - 1, 61, "sea_foam")
    m.fill(0, 62, W - 1, H - 1, "sea")
    m.fill(59, 55, 61, 65, "pier")
    m.fill(54, 64, 63, 65, "pier")

    # --- Parque Central -------------------------------------------------------
    m.fill(14, 29, 26, 40, "dirt")          # praça do chafariz
    m.fill(18, 22, 21, 28, "dirt")          # entrada norte
    m.fill(27, 32, 40, 33, "dirt")          # trilha leste até a Rua Bayside
    m.fill(18, 41, 21, 48, "dirt")          # trilha sul até a orla
    m.fill(18, 32, 22, 34, "fountain")
    for (x0, y0, x1, y1) in ((3, 38, 9, 43), (4, 37, 8, 37), (4, 44, 8, 44)):
        m.fill(x0, y0, x1, y1, "water")     # lago
    m.fill(9, 40, 12, 41, "pier")           # deque de pesca do lago
    for (fx, fy, fw, fh) in [(4, 27, 4, 2), (30, 26, 3, 3), (24, 42, 6, 2), (1, 45, 3, 1), (32, 39, 3, 2),
                             (14, 26, 2, 2), (28, 45, 4, 2)]:
        m.fill(fx, fy, fx + fw - 1, fy + fh - 1, "flowers")
    m.add("statue", 20, 33)
    for x in range(1, 41):
        if x not in (18, 19, 20, 21):
            m.add("hedge", x, 22)
    for y in range(23, 49):
        if y not in (32, 33):
            m.add("hedge", 40, y)
    for (bx, by) in [(15, 28), (25, 28), (14, 41), (26, 41), (27, 31), (27, 34), (12, 39)]:
        m.add("bench", bx, by)
    for (tx, ty, k) in [(2, 26, "tree"), (8, 24, "tree2"), (11, 30, "tree3"), (5, 32, "tree"), (2, 35, "tree2"),
                        (15, 45, "tree"), (11, 46, "tree3"), (31, 24, "tree2"), (36, 27, "tree"), (33, 29, "tree3"),
                        (36, 38, "tree"), (31, 43, "tree2"), (37, 45, "tree"), (24, 46, "tree3"), (2, 42, "tree"),
                        (25, 24, "tree"), (11, 26, "tree3"), (35, 35, "pine"), (2, 47, "pine"), (7, 47, "tree2")]:
        m.add(k, tx, ty)
    for (lx, ly) in [(17, 27), (22, 27), (13, 34), (27, 37), (17, 42), (22, 42), (13, 30)]:
        m.add("lamp", lx, ly)
    for (bx, by, k) in [(16, 26, "bush"), (23, 26, "bush2"), (11, 33, "bush3"), (27, 39, "bush"), (11, 37, "bush2"),
                        (6, 29, "bush"), (3, 45, "bush2"), (27, 44, "bush"), (9, 34, "bush3"), (34, 42, "bush"),
                        (5, 24, "bush2"), (37, 30, "bush3"), (13, 43, "bush")]:
        if m.tiles[by][bx] in ("grass", "flowers"):
            m.add(k, bx, by)
    for (px, py) in [(17, 31), (23, 31), (16, 36), (24, 36)]:
        m.add("flowerpot" if px < 20 else "flowerpot2", px, py)
    m.add("picnic", 29, 36)
    m.add("rock_big", 2, 38); m.add("rock", 10, 44); m.add("stump", 34, 47)

    # --- Centro: prédios -------------------------------------------------------
    m.buildings += [
        Building("Residencial Luthor", "home", 2, 8, 9, 8, 2, 6, "home"),
        Building("LUTHOR CORP", "tower", 16, 6, 11, 10, 6, 21, "hq"),
        Building("Grão Nobre", "cafe", 31, 10, 7, 6, 1, 35, "cafe"),
        Building("CatCo Worldwide Media", "catco", 44, 7, 10, 9, 5, 48, "catco"),
        Building("Gruppo Ricci", "ricci", 60, 8, 9, 8, 2, 64, "ricci"),
        Building("Conti Moretti Hospitais", "hospital", 74, 7, 9, 9, 3, 78, "hospital"),
        Building("Bayside Books", "books", 48, 25, 8, 7, 1, 55, "books"),
        Building("Mercado Central", "market", 61, 25, 8, 7, 1, 64, "market"),
        Building("Ricci Trattoria", "trattoria", 74, 25, 9, 7, 1, 81, "trattoria"),
        Building("Noonan's", "bar", 48, 39, 8, 7, 1, 55, "bar"),
        Building("Cine National", "cinema", 61, 39, 9, 7, 2, 65, "cinema"),
        Building("Apartamentos Bayside", "apartments", 75, 39, 8, 7, 2, 79, None),
    ]
    m.fill(39, 11, 41, 13, "flowers")
    for (tx, ty, k) in [(13, 9, "tree"), (13, 13, "tree2"), (29, 8, "tree3"), (40, 8, "tree"), (42, 13, "tree2"),
                        (56, 9, "tree"), (56, 13, "tree3"), (71, 9, "tree2"), (71, 13, "tree"), (58, 6, "pine")]:
        m.add(k, tx, ty)
    for (bx, by) in [(28, 14), (57, 15)]:
        m.add("bench", bx, by)
    for x in (4, 26, 53, 73, 81, 92, 104):
        m.add("lamp", x, 16)
    for x in (8, 34, 51, 77, 90, 106):
        m.add("lamp", x, 21)
    m.add("busstop", 10, 16)
    m.add("busstop", 68, 20)
    m.add("hydrant", 30, 17)
    m.add("hydrant", 54, 20)

    # --- Calçadão comercial ----------------------------------------------------
    m.fill(47, 22, 86, 48, "plaza")
    # Portas das lojas de cima: x 55, 64 e 81 (linha 31); as de baixo abrem para o sul. Nada fica na
    # frente das portas nem no meio dos becos: postes, bancos e bancas ficam encostados na lateral dos
    # prédios, com os bancos virados para o beco. No meio do calçadão só há árvores sob as fachadas.
    for x in (49, 52, 62, 67, 75, 78):
        m.add("planter", x, 35)
    # becos de cima (entre as lojas): banca encostada numa parede, banco e poste na outra
    m.add("petstand", 56, 27)
    m.add("lamp", 60, 27); m.add("bench_l", 60, 29)
    m.add("kiosk", 69, 27, data="news")
    m.add("lamp", 73, 27); m.add("bench_l", 73, 29)
    # becos de baixo: bancos frente a frente, um poste em cada parede
    for (left, right) in ((56, 60), (70, 74)):
        m.add("lamp", left, 40); m.add("lamp", right, 40)
        m.add("bench_r", left, 42); m.add("bench_l", right, 42)
    # bordas do calçadão (oeste junto à Rua Bayside, leste junto ao bosque)
    for y in (27, 41):
        m.add("lamp", 47, y); m.add("bench_l", 47, y + 2)
        m.add("lamp", 83, y); m.add("bench_r", 83, y + 2)
    for (bx, by, k) in [(47, 22, "bush"), (86, 22, "bush2"), (47, 48, "bush3"), (86, 48, "bush")]:
        m.add(k, bx, by)

    # --- Orla e praia ----------------------------------------------------------
    for x in (6, 18, 30, 51, 68, 79, 92, 104):
        m.add("lamp", x, 52)
    for (px, py) in [(3, 55), (14, 56), (37, 55), (52, 56), (73, 55), (81, 56), (90, 56), (97, 55)]:
        m.add("palm", px, py)
    for (ux, uy, k) in [(8, 59, "umbrella"), (21, 56, "umbrella2"), (32, 59, "umbrella"), (45, 59, "umbrella2"),
                        (66, 56, "umbrella"), (86, 59, "umbrella2")]:
        m.add(k, ux, uy)
    for (tx, ty, k) in [(9, 59, "towel"), (22, 56, "towel2"), (46, 59, "towel"), (87, 59, "towel2")]:
        m.add(k, tx, ty)
    m.add("sandcastle", 27, 58); m.add("sandcastle", 70, 59)
    m.add("lifeguard", 76, 59)
    m.add("kiosk", 56, 53, data="bait")     # barraca do Joca, colada na entrada do píer
    m.add("shipbox_pier", 62, 55)
    m.add("signboard", 58, 55)
    m.add("boat", 68, 63)
    m.add("boat", 26, 65)
    for (bx, by) in [(40, 72), (88, 70), (12, 76), (76, 77)]:    # barcos mais longe, em alto-mar
        m.add("boat", bx, by)
    m.add("lighthouse", 104, 56)
    for (rx, ry, k) in [(102, 57, "rock_big"), (108, 56, "rock"), (107, 58, "rock_big"), (101, 59, "rock")]:
        m.add(k, rx, ry)

    # --- Jardim do Mirante (nordeste) -----------------------------------------
    m.fill(97, 8, 98, 15, "dirt")
    m.fill(87, 11, 108, 12, "dirt")
    m.fill(93, 7, 102, 8, "dirt")
    for (fx, fy, fw, fh) in [(88, 6, 4, 3), (104, 6, 4, 3), (88, 13, 5, 2), (103, 13, 5, 2)]:
        m.fill(fx, fy, fx + fw - 1, fy + fh - 1, "flowers")
    m.add("gazebo", 96, 4)
    for (bx, by) in [(94, 13), (101, 13), (93, 6), (102, 6)]:
        m.add("bench", bx, by)
    for (lx, ly) in [(96, 10), (99, 10), (88, 10), (107, 10)]:
        m.add("lamp", lx, ly)
    for x in range(85, 111):
        if x not in (97, 98):
            m.add("fence", x, 15)
    for (tx, ty, k) in [(85, 6, "tree2"), (85, 11, "tree"), (109, 7, "tree3"), (109, 12, "tree2"),
                        (90, 4, "tree"), (106, 3, "pine"), (93, 3, "tree2"), (101, 2, "tree")]:
        m.add(k, tx, ty)
    for (px, py) in [(95, 9), (100, 9)]:
        m.add("flowerpot", px, py)

    # --- Bosque Bayside (sudeste) ----------------------------------------------
    for y in range(22, 49):
        if y not in (35, 36):
            m.add("hedge", 87, y)
    m.fill(87, 35, 92, 36, "dirt")          # entrada pelo calçadão
    m.fill(91, 24, 108, 25, "dirt")         # trilha em volta do lago
    m.fill(91, 24, 92, 40, "dirt")
    m.fill(107, 24, 108, 40, "dirt")
    m.fill(91, 39, 108, 40, "dirt")
    m.fill(98, 41, 99, 48, "dirt")          # saída para a orla
    for (x0, y0, x1, y1) in ((95, 28, 104, 34), (97, 27, 102, 27), (94, 29, 94, 33), (105, 29, 105, 32),
                             (96, 35, 103, 35)):
        m.fill(x0, y0, x1, y1, "water")
    m.fill(99, 35, 100, 38, "pier")         # deque do lago do bosque
    for (fx, fy, fw, fh) in [(94, 42, 3, 2), (102, 46, 4, 2), (89, 27, 1, 3), (110, 30, 1, 4)]:
        m.fill(fx, fy, fx + fw - 1, fy + fh - 1, "flowers")
    for (px, py) in [(102, 42), (105, 44)]:
        m.add("picnic", px, py)
    m.add("log", 94, 37); m.add("stump", 105, 37); m.add("bench", 95, 26); m.add("bench", 103, 26)
    for (lx, ly) in [(93, 34), (106, 34), (97, 41), (100, 41)]:
        m.add("lamp", lx, ly)
    rnd = random.Random("bosque")
    _scatter(m, ["pine", "pine", "tree", "tree3"], (88, 22, 110, 48), 34, rnd, gap=1, avoid=("dirt", "water", "pier"))
    _scatter(m, ["rock", "rock_big", "stump", "bush", "bush3"], (88, 22, 110, 48), 10, rnd, gap=1,
             avoid=("dirt", "pier"))

    # --- capim alto (não bloqueia a passagem) ----------------------------------
    for area, n in (((88, 22, 110, 48), 40), ((1, 23, 39, 48), 26), ((84, 2, 110, 14), 14), ((1, 2, 110, 5), 18)):
        _scatter(m, ["tallgrass"], area, n, rnd, gap=0, tiles=("grass",))

    # --- bordas: floresta em volta da cidade -----------------------------------
    def near_obj(x, y, d=1):
        return any(o.layer == "obj" and o.kind != "tallgrass" and o.x - d <= x < o.x + o.w + d
                   and o.y - d <= y < o.y + o.h + d for o in m.objects)

    for row, first in ((1, 0), (3, 1)):     # duas fileiras desencontradas: as copas fecham a borda
        for x in range(first, W, 2):
            if m.tiles[row][x] != "grass" or near_obj(x, row) \
                    or any(b.x - 1 <= x <= b.x + b.w and b.y <= row + 4 for b in m.buildings):
                continue
            m.objects = [o for o in m.objects if not (o.kind == "tallgrass" and o.x == x and o.y == row)]
            m.add(("pine", "tree", "tree", "tree2", "pine", "tree3")[(x * 7 + row) % 6], x, row)
    for y in range(2, 49, 2):
        if 15 <= y <= 22:
            continue
        for x in (0, W - 1):
            if m.tiles[y][x] in ("grass", "flowers") and not any(o.covers(x, y) for o in m.objects):
                m.add("pine" if (y // 2) % 2 else "tree", x, y)
    for key, (dx, dy) in CITY_DOORS.items():
        ix, iy = INTERIOR_DOORS[key]
        m.doors[(dx, dy)] = (key, ix, iy - 1, "up")
    m.spawn_edges = [(0, 18), (W - 1, 19), (0, 50), (W - 1, 51)]
    m.car_lanes = [(18, -1), (19, 1), (50, -1), (51, 1)]
    m.finalize()
    return m


# ---------------------------------------------------------------------------
# Interiores
# ---------------------------------------------------------------------------

INTERIOR_LEGEND = {"W": "wall", "G": "glass", "o": "wood", "O": "wood_dark", "m": "marble", "l": "lab",
                   "c": "carpet", "b": "carpet_blue", "e": "office", "k": "checker", "t": "tile_white",
                   "r": "terracotta", "D": "door"}


def _interior(name, rows, label):
    m = GameMap(name, len(rows[0]), len(rows), outdoor=False, label=label)
    for y, row in enumerate(rows):
        assert len(row) == m.w, (name, y, len(row), m.w)
        for x, ch in enumerate(row):
            m.tiles[y][x] = INTERIOR_LEGEND[ch]
    dx, dy = INTERIOR_DOORS[name]
    assert m.tiles[dy][dx] == "door", (name, dx, dy)
    cx, cy = CITY_DOORS[name]
    m.doors[(dx, dy)] = ("city", cx, cy + 1, "down")
    return m


def _box(w, h, fill, door_x):
    rows = ["W" * w, "W" * w]
    for _ in range(h - 3):
        rows.append("W" + fill * (w - 2) + "W")
    rows.append("W" * door_x + "D" + "W" * (w - door_x - 1))
    return rows


def build_home():
    rows = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WcccccccWooooooooommmmmmmW",
        "WcccccccWooooooooommmmmmmW",
        "WcccccccWooooooooommmmmmmW",
        "WccccccccooooooooommmmmmmW",
        "WccccccccooooooooommmmmmmW",
        "WcccccccWooooooooommmmmmmW",
        "WcccccccWoooooooooooooooooW"[:26],
        "WWWWtWWWWooooooooooooooooW",
        "WttttttWWooooooooooooooooW",
        "WttttttWWooooooooooooooooW",
        "WttttttWWooooooooooooooooW",
        "WttttttWWooooooooooooooooW",
        "WttttttWWooooooooooooooooW",
        "WWWWWWWWWWWWWWWWDWWWWWWWWW",
    ]
    rows[8] = "WcccccccWooooooooooooooooW"
    m = _interior("home", rows, "Cobertura Luthor")
    # quarto
    m.add("rug_bed", 2, 5)
    m.add("bed2", 2, 2)
    m.add("nightstand", 1, 2); m.add("nightstand", 5, 2)
    m.add("wardrobe", 6, 2)
    m.add("plant", 7, 8)
    m.add("window", 3, 1); m.add("painting", 6, 1)
    # banheiro
    m.add("bathtub", 1, 10)
    m.add("sink", 6, 10)
    m.add("plant", 1, 14)
    # escritório
    m.add("desk_home", 9, 2)
    m.add("bookshelf3", 13, 2)
    m.add("chair_blue", 10, 3)
    # sala
    m.add("window_big", 10, 1); m.add("window_big", 13, 1); m.add("window_big", 16, 1)
    m.add("rug_big", 10, 8)
    m.add("tv_big", 11, 7)
    m.add("coffee_table", 12, 9)
    m.add("sofa", 11, 11)
    m.add("armchair", 15, 9)
    m.add("plant_big", 9, 14); m.add("plant_big", 16, 6)
    m.add("aquarium", 21, 10)
    m.add("dining", 21, 13)
    m.add("chair", 20, 13); m.add("chair", 23, 13)
    # cozinha
    m.add("window", 22, 1); m.add("painting2", 19, 1)
    m.add("kitchen", 18, 2)
    m.add("stove", 21, 2)
    m.add("kitchen2", 22, 2)
    m.add("fridge", 24, 2)
    m.add("island", 19, 5)
    m.add("stool", 19, 6); m.add("stool", 21, 6)
    m.add("petbed", 16, 12)
    # porta de vidro para o terraço
    tx, ty = TERRACE_DOOR
    m.tiles[ty][tx] = "door"
    m.doors[(tx, ty)] = ("terrace", 10, 11, "up")
    m.add("glass_door", tx, ty)
    m.finalize()
    return m


def build_hq():
    rows = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WccccccccWlllllllllllllllW",
        "WGGGmmGGGWGGGGGGmmmGGGGGGW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WmmmmmmmmmmmmmmmmooooooooW",
        "WWWWWWWWWWWWDWWWWWWWWWWWWW",
    ]
    m = _interior("hq", rows, "Sede da Luthor Corp")
    m.add("logo_rug", 9, 13)
    m.add("painting", 4, 1); m.add("window", 2, 1); m.add("window", 7, 1)
    m.add("window_big", 12, 1); m.add("window_big", 16, 1); m.add("window_big", 20, 1)
    m.add("bookshelf", 1, 2)
    m.add("ceo_desk", 3, 4)
    m.add("coffee", 7, 2)
    m.add("plant_big", 8, 8)
    m.add("plant", 1, 8)
    m.add("terminal", 10, 2)
    m.add("shipbox", 23, 2)
    for i, (sx, sy) in enumerate(STATION_SLOTS):
        m.add("station", sx, sy, data=i)
    m.add("reception", 11, 12)
    m.add("sofa_grey", 2, 15)
    m.add("plant_big", 1, 10); m.add("plant", 16, 16)
    m.add("desk", 20, 12)
    m.add("bookshelf2", 23, 15)
    m.add("plant", 24, 10)
    m.add("cooler", 16, 10)
    m.finalize()
    return m


def build_cafe():
    m = _interior("cafe", _box(16, 11, "k", 7), "Café Grão Nobre")
    m.add("rug_red", 6, 7)
    m.add("menuboard", 5, 1); m.add("window", 10, 1); m.add("window", 13, 1)
    m.add("cafe_shelf", 1, 2)
    m.add("coffee", 6, 2)
    m.add("cafe_counter", 2, 4)
    for (tx, ty) in [(10, 4), (13, 4), (10, 7), (13, 7)]:
        m.add("table", tx, ty)
        m.add("chair", tx - 1, ty)
        m.add("chair", tx + 1, ty)
    m.add("plant", 1, 9); m.add("plant", 14, 9)
    m.finalize()
    return m


def build_catco():
    rows = [
        "WWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWW",
        "WeeeeeeeeeeeeeeeGbbbbbbW",
        "WeeeeeeeeeeeeeeeGbbbbbbW",
        "WeeeeeeeeeeeeeeeGbbbbbbW",
        "WeeeeeeeeeeeeeeeGbbbbbbW",
        "WeeeeeeeeeeeeeeeGGGbbGGW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WeeeeeeeeeeeeeeeeeeeeeeW",
        "WWWWWWWWWWWDWWWWWWWWWWWW",
    ]
    m = _interior("catco", rows, "CatCo Worldwide Media")
    m.add("catco_rug", 8, 11)
    m.add("tv_wall", 5, 1)
    m.add("window_big", 1, 1); m.add("window_big", 11, 1)
    m.add("window", 18, 1); m.add("window", 21, 1)
    for (dx, dy) in [(3, 4), (6, 4), (10, 4), (3, 8), (6, 8), (10, 8), (13, 8)]:
        m.add("desk_news", dx, dy)
    m.add("printer", 14, 2)
    m.add("cooler", 1, 10)
    m.add("plant_big", 15, 4); m.add("plant", 22, 12); m.add("plant", 1, 13)
    m.add("desk_editor", 18, 3)
    m.add("bookshelf2", 21, 2)
    m.add("sofa_grey", 17, 12)
    m.add("poster", 15, 1)
    m.finalize()
    return m


def build_books():
    m = _interior("books", _box(18, 12, "o", 8), "Bayside Books")
    m.add("rug_green", 2, 7)
    for i, x in enumerate((1, 3, 5, 7)):
        m.add(["bookshelf", "bookshelf2", "bookshelf3", "bookshelf"][i], x, 2)
    m.add("bookshelf2", 2, 5); m.add("bookshelf3", 6, 5)
    m.add("shop_counter", 12, 5)
    m.add("bookshelf", 14, 2)
    m.add("armchair", 2, 9); m.add("armchair", 5, 9)
    m.add("table", 11, 8); m.add("chair", 10, 8); m.add("chair", 12, 8)
    m.add("plant_big", 16, 9); m.add("plant", 16, 2)
    m.add("window", 10, 1); m.add("poster2", 12, 1)
    m.finalize()
    return m


def build_market():
    m = _interior("market", _box(18, 12, "t", 8), "Mercado Central")
    m.add("produce", 2, 5); m.add("produce2", 5, 5); m.add("produce2", 2, 8); m.add("produce", 5, 8)
    m.add("fridge2", 1, 2); m.add("fridge2", 4, 2); m.add("fridge2", 7, 2)
    m.add("shop_counter", 12, 5)
    m.add("flowerstand", 14, 8)
    m.add("flowerstand", 11, 8)
    m.add("plant", 16, 2); m.add("plant", 1, 10)
    m.add("window", 11, 1); m.add("window", 14, 1)
    m.finalize()
    return m


def build_trattoria():
    m = _interior("trattoria", _box(20, 13, "r", 10), "Ricci Trattoria")
    m.fill(1, 2, 18, 4, "marble")
    m.add("oven", 2, 2)
    m.add("kitchen", 5, 2)
    m.add("stove", 12, 2)
    m.add("wine_shelf", 15, 2)
    m.add("counter_it", 6, 5)
    m.add("window", 8, 1); m.add("painting", 11, 1); m.add("painting2", 4, 1)
    for (tx, ty) in [(3, 8), (7, 8), (13, 8), (17, 8), (3, 10), (11, 10), (15, 10)]:
        m.add("table_it", tx, ty)
        m.add("chair", tx - 1, ty)
        m.add("chair", tx + 1, ty)
    m.add("plant_big", 1, 5); m.add("plant_big", 18, 5)
    m.finalize()
    return m


def build_bar():
    m = _interior("bar", _box(18, 12, "O", 8), "Noonan's")
    m.add("bottle_shelf", 1, 2)
    m.add("bottle_shelf", 5, 2)
    m.add("bar_counter", 2, 4)
    m.add("stool", 3, 5); m.add("stool", 5, 5); m.add("stool", 7, 5)
    m.add("jukebox", 10, 2)
    m.add("arcade", 14, 2); m.add("arcade", 16, 2)
    m.add("pool", 12, 6)
    for (tx, ty) in [(2, 8), (6, 8), (10, 8)]:
        m.add("table", tx, ty)
        m.add("chair", tx - 1, ty)
        m.add("chair", tx + 1, ty)
    m.add("neon", 8, 1); m.add("poster", 12, 1)
    m.add("plant", 16, 9)
    m.finalize()
    return m


def build_terrace():
    W, H = 20, 13
    m = GameMap("terrace", W, H, outdoor=False, label="Terraço da Cobertura")
    m.open_air = True
    for y in range(H):
        for x in range(W):
            m.tiles[y][x] = "void"
    m.fill(1, 1, W - 2, 1, "glass")
    m.fill(1, 1, 1, H - 2, "glass")
    m.fill(W - 2, 1, W - 2, H - 2, "glass")
    m.fill(2, 2, W - 3, H - 2, "wood")
    m.fill(2, 2, 9, 5, "terracotta")
    m.fill(12, 7, 16, 10, "grass")
    m.fill(0, H - 1, W - 1, H - 1, "wall")
    m.tiles[H - 1][10] = "door"
    m.doors[(10, H - 1)] = ("home", TERRACE_DOOR[0], TERRACE_DOOR[1] + 1, "down")
    for i, (px, py) in enumerate(PLOT_SLOTS):
        m.add("plot", px, py, data=i)
    m.add("watering", 2, 3)
    m.add("string_lights", 2, 0); m.add("string_lights", 11, 0)
    m.add("telescope", 16, 2)
    m.add("railing_plant", 11, 2); m.add("railing_plant", 2, 10); m.add("railing_plant", 17, 10)
    m.add("table", 14, 4); m.add("chair", 13, 4); m.add("chair", 15, 4)
    m.add("umbrella", 14, 3)
    m.add("lounger", 3, 7); m.add("lounger", 5, 7)
    m.add("plant_big", 9, 9); m.add("bush", 12, 10); m.add("bush2", 16, 7)
    m.add("lamp", 11, 6); m.add("lamp", 17, 5)
    m.finalize()
    return m


def build_cinema():
    rows = _box(21, 14, "c", 10)
    m = _interior("cinema", rows, "Cine National")
    m.fill(1, 9, 19, 12, "checker")
    m.add("cine_screen", 5, 1)
    for y in (4, 5, 6, 7):
        for x in list(range(3, 9)) + list(range(12, 18)):
            m.add("seat", x, y)
    m.add("ticket", 2, 10)
    m.add("popcorn", 6, 10)
    m.add("film_poster", 2, 1); m.add("film_poster2", 17, 1); m.add("film_poster", 19, 1)
    m.add("rope", 14, 10); m.add("rope", 16, 10)
    m.add("plant", 1, 12); m.add("plant", 19, 12)
    m.finalize()
    return m


HOSPITAL_BED = (20, 4)     # onde a jogadora acorda se desmaiar


def build_hospital():
    rows = [
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WtttttWtttttWtttttWbbbbbbbbW",
        "WtttttWtttttWtttttWbbbbbbbbW",
        "WtttttWtttttWtttttWbbbbbbbbW",
        "WtttttWtttttWtttttWbbbbbbbbW",
        "WtttttWtttttWtttttWbbbbbbbbW",
        "WWWtWWWWWtWWWWWtWWWWWWttWWWW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WmmmmmmmmmmmmmmmmmmmmmmmmmmW",
        "WWWWWWWWWWWWWDWWWWWWWWWWWWWW",
    ]
    m = _interior("hospital", rows, "Conti Moretti Hospitais")
    # consultórios: cardiologia, neurologia, oncologia
    for i, ox in enumerate((1, 7, 13)):
        m.add("cabinet", ox, 2)
        m.add("hdesk", ox + 1, 3)
        m.add("hchair", ox + 1, 4)
        m.add("exambed", ox + 4, 3)
        m.add("plant", ox + 4, 2)
        m.add("hsign", ox + 3, 7, data=i)
        m.add("window", ox + 2, 1)
    # internação
    for x in (20, 22, 24, 26):
        m.add("hbed", x, 2)
    m.add("monitor", 21, 2); m.add("monitor", 25, 2)
    m.add("hsign", 21, 7, data=3)
    m.add("window_big", 22, 1)
    # recepção, farmácia e espera
    m.add("cm_wall_logo", 12, 7)
    m.add("hreception", 11, 10)
    m.add("cm_rug", 11, 12)
    m.add("pharma_shelf", 24, 8)
    m.add("pharma_counter", 24, 10)
    m.add("hsign", 25, 7, data=4)
    for y in (11, 13):
        for x in (2, 3, 4, 5):
            m.add("hchair", x, y)
    m.add("vending", 7, 8)
    m.add("cooler", 8, 8)
    m.add("plant_big", 1, 8); m.add("plant_big", 26, 15); m.add("plant", 1, 15); m.add("plant", 17, 8)
    m.add("table", 4, 15); m.add("chair", 3, 15); m.add("chair", 5, 15)
    m.finalize()
    return m


VITTORIA_DESK = (4, 2)      # onde a Vittoria trabalha na sede


def build_ricci():
    """Sede do Gruppo Ricci: sala da Vittoria, cozinha de testes, sala de degustação e recepção."""
    rows = [
        "WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW",
        "WOOOOOOOGmmmmGkkkkkW",
        "WOOOOOOOGmmmmGkkkkkW",
        "WOOOOOOOmmmmmmkkkkkW",
        "WOOOOOOOGmmmmGkkkkkW",
        "WOOOOOOOGmmmmGkkkkkW",
        "WGGGGGGGGmmmmGGGGGGW",
        "WcccccGmmmmmmmmmmmmW",
        "WcccccGmmmmmmmmmmmmW",
        "WcccccmmmmmmmmmmmmmW",
        "WcccccGmmmmmmmmmmmmW",
        "WcccccGmmmmmmmmmmmmW",
        "WWWWWWWWWWDWWWWWWWWW",
    ]
    m = _interior("ricci", rows, "Gruppo Ricci")
    # sala da Vittoria
    m.add("window_big", 2, 1); m.add("window_big", 5, 1)
    m.add("desk", 3, 3)
    m.add("plant_big", 1, 2); m.add("bookshelf", 6, 2)
    m.add("rug_red", 2, 5)
    m.add("armchair", 1, 6); m.add("armchair", 7, 6)
    # corredor com o mapa dos restaurantes
    m.add("ricci_map", 10, 1)
    m.add("plant", 9, 2); m.add("plant", 12, 2)
    # cozinha de testes
    m.add("window", 16, 1)
    m.add("kitchen", 14, 2); m.add("stove", 17, 2); m.add("fridge", 18, 2)
    m.add("island", 15, 4)
    for x in (15, 16, 17):
        m.add("stool", x, 5)
    # sala de degustação
    m.add("wine_shelf", 1, 8)
    m.add("dining", 2, 10); m.add("chair", 1, 10); m.add("chair", 4, 10)
    m.add("plant", 5, 12)
    # recepção
    m.add("desk", 13, 9)
    m.add("rug_green", 8, 10)
    m.add("sofa_grey", 15, 12)
    m.add("plant_big", 18, 8); m.add("plant_big", 7, 12)
    m.add("coffee", 18, 10)
    m.finalize()
    return m


def build_world():
    return {"city": build_city(), "home": build_home(), "hq": build_hq(), "cafe": build_cafe(),
            "catco": build_catco(), "books": build_books(), "market": build_market(),
            "trattoria": build_trattoria(), "bar": build_bar(), "terrace": build_terrace(),
            "cinema": build_cinema(), "hospital": build_hospital(), "ricci": build_ricci()}

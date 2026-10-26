"""Mapas de National City."""
from collections import deque
import random

import pygame

from . import art
from .config import TILE

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
        # sombras suaves sob os prédios
        for o in self.objects:
            if o.layer == "decal":
                spr = art.object_sprite(o.kind)
                surf.blit(spr, (o.x * TILE, (o.y + o.h) * TILE - spr.get_height()))
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

    def find_path(self, start, goal, max_nodes=6000):
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
CITY_DOORS = {"home": (6, 12), "hq": (19, 12), "cafe": (30, 12), "catco": (41, 12),
              "books": (44, 26), "market": (54, 26), "trattoria": (65, 26), "bar": (44, 37), "cinema": (55, 37),
              "hospital": (65, 12)}
INTERIOR_DOORS = {"home": (16, 15), "hq": (12, 17), "cafe": (7, 10), "catco": (11, 14),
                  "books": (8, 11), "market": (8, 11), "trattoria": (10, 12), "bar": (8, 11), "cinema": (10, 13),
                  "hospital": (13, 16)}
TERRACE_DOOR = (15, 1)      # porta da sala para o terraço (na cobertura)
STATION_SLOTS = [(x, y) for y in (4, 7) for x in (12, 14, 16, 18, 20, 22)]
HOME_BED = (3, 4)          # onde a jogadora acorda


# ---------------------------------------------------------------------------
# Cidade
# ---------------------------------------------------------------------------

def build_city():
    W, H = 72, 56
    m = GameMap("city", W, H, outdoor=True, label="National City")
    m.fill(0, 0, W - 1, H - 1, "grass")
    # Avenida Siegel (horizontal)
    m.fill(1, 13, W - 2, 14, "pavement")
    m.fill(0, 15, W - 1, 15, "road_line_b")
    m.fill(0, 16, W - 1, 16, "road_line_t")
    m.fill(1, 17, W - 2, 18, "pavement")
    for cx in (18, 19, 20, 54, 55, 56):
        m.tiles[15][cx] = "cross"; m.tiles[16][cx] = "cross"
    # frente dos prédios do centro: calçada larga
    m.fill(13, 11, 48, 12, "pavement")
    # Rua Bayside (vertical)
    m.fill(34, 19, 35, 38, "pavement")
    m.fill(38, 19, 39, 38, "pavement")
    m.fill(36, 17, 36, 41, "road_line_r")
    m.fill(37, 17, 37, 41, "road_line_l")
    m.fill(36, 15, 37, 16, "road")
    for yy in (17, 18):
        m.tiles[yy][36] = "cross_v"; m.tiles[yy][37] = "cross_v"
    # Orla (horizontal)
    m.fill(1, 39, W - 2, 39, "pavement")
    m.fill(0, 40, W - 1, 40, "road_line_b")
    m.fill(0, 41, W - 1, 41, "road_line_t")
    m.fill(36, 40, 37, 41, "road")
    m.fill(1, 42, W - 2, 42, "pavement")
    for cx in (17, 18, 49, 50):
        m.tiles[40][cx] = "cross"; m.tiles[41][cx] = "cross"
    m.fill(0, 43, W - 1, 44, "boardwalk")
    m.fill(0, 45, W - 1, 48, "sand")
    m.fill(0, 49, W - 1, 49, "sea_foam")
    m.fill(0, 50, W - 1, H - 1, "sea")
    m.fill(49, 45, 51, 53, "pier")
    m.fill(47, 52, 53, 53, "pier")
    # Parque central
    m.fill(12, 24, 24, 32, "dirt")
    m.fill(16, 20, 19, 23, "dirt")
    m.fill(25, 27, 33, 28, "dirt")
    m.fill(16, 33, 19, 38, "dirt")
    m.fill(16, 27, 20, 29, "fountain")
    m.fill(3, 30, 9, 35, "water")
    m.fill(10, 30, 10, 35, "dirt")
    for (fx, fy, fw, fh) in [(4, 22, 4, 2), (26, 21, 3, 3), (22, 34, 4, 2), (1, 37, 3, 1), (28, 31, 3, 2),
                             (12, 21, 2, 2)]:
        m.fill(fx, fy, fx + fw - 1, fy + fh - 1, "flowers")
    m.add("statue", 18, 28)
    for x in range(1, 33):
        if x not in (16, 17, 18, 19):
            m.add("hedge", x, 19)
    for y in range(20, 39):
        if y not in (27, 28):
            m.add("hedge", 33, y)
    for (bx, by) in [(13, 23), (23, 23), (12, 33), (24, 33), (25, 26), (25, 29)]:
        m.add("bench", bx, by)
    for (tx, ty, k) in [(2, 21, "tree"), (8, 20, "tree2"), (11, 25, "tree3"), (5, 26, "tree"), (2, 28, "tree2"),
                        (13, 36, "tree"), (8, 37, "tree3"), (27, 20, "tree2"), (30, 23, "tree"), (28, 25, "tree3"),
                        (31, 30, "tree"), (27, 35, "tree2"), (31, 36, "tree"), (21, 36, "tree3"), (2, 33, "tree"),
                        (22, 21, "tree"), (10, 22, "tree3")]:
        m.add(k, tx, ty)
    for (lx, ly) in [(15, 22), (20, 22), (12, 29), (24, 29), (15, 34), (20, 34)]:
        m.add("lamp", lx, ly)
    for (bx, by, k) in [(14, 21, "bush"), (21, 21, "bush2"), (11, 27, "bush3"), (25, 31, "bush"), (11, 31, "bush2"),
                        (6, 24, "bush"), (29, 27, "bush3"), (3, 36, "bush2"), (24, 36, "bush"), (9, 28, "bush3"),
                        (30, 34, "bush"), (5, 20, "bush2")]:
        if m.tiles[by][bx] in ("grass", "flowers"):
            m.add(k, bx, by)
    # Centro: prédios
    m.buildings += [
        Building("Residencial Luthor", "home", 2, 5, 9, 8, 2, 6, "home"),
        Building("LUTHOR CORP", "tower", 14, 3, 11, 10, 6, 19, "hq"),
        Building("Grão Nobre", "cafe", 27, 7, 7, 6, 1, 30, "cafe"),
        Building("CatCo Worldwide Media", "catco", 37, 4, 10, 9, 5, 41, "catco"),
        Building("Banco de National City", "bank", 50, 5, 8, 8, 1, 54, None),
        Building("Conti Moretti Hospitais", "hospital", 61, 4, 9, 9, 3, 65, "hospital"),
        Building("Bayside Books", "books", 41, 20, 8, 7, 1, 44, "books"),
        Building("Mercado Central", "market", 51, 20, 8, 7, 1, 54, "market"),
        Building("Ricci Trattoria", "trattoria", 61, 20, 9, 7, 1, 65, "trattoria"),
        Building("Noonan's", "bar", 41, 31, 8, 7, 1, 44, "bar"),
        Building("Cine National", "cinema", 51, 31, 9, 7, 2, 55, "cinema"),
        Building("Apartamentos Bayside", "apartments", 62, 31, 8, 7, 2, 66, None),
    ]
    for (tx, ty, k) in [(12, 6, "tree"), (12, 9, "tree2"), (26, 4, "tree3"), (35, 6, "tree"), (35, 9, "tree2"),
                        (48, 6, "tree"), (48, 9, "tree3"), (59, 7, "tree2"), (59, 10, "tree"), (1, 3, "tree3"),
                        (70, 3, "tree")]:
        m.add(k, tx, ty)
    for x in (4, 24, 46, 60, 68):
        m.add("lamp", x, 13)
    for x in (8, 30, 44, 64):
        m.add("lamp", x, 18)
    m.add("busstop", 10, 13)
    m.add("busstop", 58, 17)
    m.add("hydrant", 26, 14)
    m.add("hydrant", 47, 17)
    # Calçadão comercial
    m.fill(40, 19, 70, 38, "plaza")
    for (px, py) in [(42, 28), (47, 28), (52, 28), (57, 28), (62, 28), (67, 28)]:
        m.add("planter", px, py)
    for (bx, by) in [(44, 29), (54, 29), (64, 29)]:
        m.add("bench", bx, by)
    m.add("kiosk", 58, 27, data="news")
    m.add("petstand", 48, 29)
    for (bx, by, k) in [(40, 19, "bush"), (49, 19, "bush2"), (59, 19, "bush3"), (70, 19, "bush"),
                        (40, 38, "bush2"), (50, 38, "bush3"), (61, 38, "bush")]:
        m.add(k, bx, by)
    for (lx, ly) in [(40, 27), (50, 30), (60, 30), (70, 27)]:
        if m.in_bounds(lx, ly):
            m.add("lamp", lx, ly)
    # Orla e praia
    for x in (6, 16, 26, 44, 58, 66):
        m.add("lamp", x, 42)
    for (px, py) in [(3, 45), (12, 46), (33, 45), (45, 46), (60, 45), (68, 46)]:
        m.add("palm", px, py)
    for (ux, uy, k) in [(8, 47, "umbrella"), (19, 46, "umbrella2"), (28, 47, "umbrella"), (38, 47, "umbrella2"),
                        (56, 46, "umbrella")]:
        m.add(k, ux, uy)
    m.add("lifeguard", 63, 47)
    m.add("kiosk", 45, 43, data="bait")
    m.add("shipbox_pier", 52, 45)
    m.add("signboard", 48, 45)
    m.add("boat", 58, 51)
    m.add("boat", 24, 53)
    # bordas
    for x in range(W):
        if m.tiles[0][x] == "grass":
            m.add("tree" if x % 2 else "tree2", x, 0)
    for y in range(1, 39):
        if y in (13, 14, 15, 16, 17, 18):
            continue
        if m.tiles[y][0] in ("grass", "flowers"):
            m.add("tree", 0, y)
        if m.tiles[y][W - 1] in ("grass", "flowers"):
            m.add("tree2", W - 1, y)
    for key, (dx, dy) in CITY_DOORS.items():
        ix, iy = INTERIOR_DOORS[key]
        m.doors[(dx, dy)] = (key, ix, iy - 1, "up")
    m.spawn_edges = [(0, 15), (W - 1, 16), (0, 40), (W - 1, 41)]
    m.car_lanes = [(15, -1), (16, 1), (40, -1), (41, 1)]
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


def build_world():
    return {"city": build_city(), "home": build_home(), "hq": build_hq(), "cafe": build_cafe(),
            "catco": build_catco(), "books": build_books(), "market": build_market(),
            "trattoria": build_trattoria(), "bar": build_bar(), "terrace": build_terrace(),
            "cinema": build_cinema(), "hospital": build_hospital()}

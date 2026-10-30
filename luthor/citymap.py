"""Mapa de National City (tecla M): a cidade vista de cima, nas cores da estação, com os prédios e onde cada
personagem está agora (quem está num interior aparece na porta do prédio)."""
import math

import pygame

from . import ui, seasons
from .config import SCREEN_W, SCREEN_H, C_LILAC, C_MUTED, C_TEXT, C_PINK, C_ACCENT_2
from .world import CITY_DOORS

T = 7                      # pixels por tile no mapa
TILE_COLORS = {
    "sea": (58, 128, 196), "sea_foam": (140, 196, 230), "water": (74, 150, 214), "fountain": (110, 180, 230),
    "plaza": (214, 204, 186), "pavement": (172, 170, 178), "sand": (236, 214, 160), "dirt": (200, 156, 104),
    "boardwalk": (150, 104, 66), "pier": (140, 96, 60), "cross": (206, 206, 212), "cross_v": (206, 206, 212),
}
ROAD = (72, 72, 84)
BUILDING_COLORS = {"home": (92, 70, 150), "hq": (122, 40, 196), "cafe": (150, 96, 60), "catco": (52, 58, 78),
                   "ricci": (58, 108, 72), "hospital": (18, 63, 53), "books": (110, 70, 50), "market": (176, 90, 60),
                   "trattoria": (160, 50, 50), "bar": (70, 40, 60), "cinema": (60, 40, 110), "marina": (40, 70, 130)}
SHORT = {"home": "Cobertura", "hq": "Luthor Corp", "cafe": "Grão Nobre", "catco": "CatCo", "ricci": "Gruppo Ricci",
         "hospital": "Conti Moretti", "books": "Bayside Books", "market": "Mercado", "trattoria": "Trattoria",
         "bar": "Noonan's", "cinema": "Cine National", "marina": "Marina"}
INSIDE_DOOR = {"terrace": "home", "altomar": "marina"}      # mapas que não têm porta própria na cidade


def _base(g):
    """Desenho fixo do mapa (refeito quando muda a estação)."""
    m = g.world["city"]
    season = seasons.CURRENT["season"]
    grass = seasons.GRASS[season][0]
    leaf = {"spring": (60, 132, 66), "summer": (50, 122, 58), "autumn": (196, 98, 38),
            "winter": (200, 210, 224)}[season]
    s = pygame.Surface((m.w * T, m.h * T))
    for y, row in enumerate(m.tiles):
        for x, t in enumerate(row):
            if t in ("grass", "flowers"):
                c = grass
            elif t.startswith("road"):
                c = ROAD
            else:
                c = TILE_COLORS.get(t, (150, 150, 150))
            s.fill(c, (x * T, y * T, T, T))
            if t.startswith("road_line") and (x + y) % 2 == 0:
                s.fill((220, 190, 70), (x * T + T // 2 - 1, y * T + T // 2 - 1, 2, 2))
    for o in m.objects:
        if o.kind in ("tree", "tree2", "tree3", "pine", "palm", "bush", "bush2", "bush3"):
            r = 3 if o.kind.startswith("bush") else 5
            col = (40, 100, 60) if o.kind == "pine" else ((90, 150, 70) if o.kind == "palm" else leaf)
            pygame.draw.circle(s, col, (o.x * T + T // 2, o.y * T + T // 2), r)
    for b in m.buildings:
        rect = pygame.Rect(b.x * T, b.y * T, b.w * T, b.h * T)
        col = BUILDING_COLORS.get(b.target, (110, 104, 120))
        pygame.draw.rect(s, col, rect, border_radius=3)
        pygame.draw.rect(s, tuple(min(255, c + 50) for c in col), rect, 2, border_radius=3)
        if b.target:
            dx, dy = CITY_DOORS.get(b.target, b.door)
            s.fill((250, 230, 150), (dx * T + 1, dy * T + 1, T - 2, T - 2))
    for b in m.buildings:
        if not b.target:                 # prédios sem entrada (apartamentos) ficam sem nome
            continue
        name = SHORT.get(b.target, b.name)
        img = ui.font(13, True).render(name, False, (250, 248, 255))
        cx, cy = b.x * T + b.w * T // 2, b.y * T + 4
        bg = pygame.Surface((img.get_width() + 6, img.get_height() + 2), pygame.SRCALPHA)
        bg.fill((10, 6, 20, 170))
        s.blit(bg, (cx - bg.get_width() // 2, cy))
        s.blit(img, (cx - img.get_width() // 2, cy + 1))
    return s


def _head(frames):
    fr = frames[("down", 0)]
    top = fr.get_height() - 64                     # personagens mais altas têm linhas a mais em cima
    head = fr.subsurface((0, max(0, top), 32, 30)).copy()
    return pygame.transform.smoothscale(head, (18, 17))


class CityMap(ui.Modal):
    def __init__(self, g):
        self.g = g
        self.t = 0.0

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and (ev.key in ui.CONFIRM or ev.key in ui.CANCEL or ev.key == pygame.K_m):
            self.done = True

    def update(self, dt):
        self.t += dt

    LABELS = {"city": "na rua", "home": "na cobertura", "terrace": "no terraço da cobertura", "hq": "na Luthor Corp",
              "cafe": "no Grão Nobre", "catco": "na CatCo", "ricci": "no Gruppo Ricci", "hospital": "no Conti Moretti",
              "books": "na Bayside Books", "market": "no Mercado Central", "trattoria": "na Ricci Trattoria",
              "bar": "no Noonan's", "cinema": "no Cine National", "marina": "na Marina Luthor",
              "altomar": "em alto-mar"}

    def where(self, mapn):
        """(porta no mapa em tiles ou None, texto do lugar) de quem está em mapn."""
        if mapn == "city":
            return None, self.LABELS["city"]
        return CITY_DOORS.get(INSIDE_DOOR.get(mapn, mapn)), self.LABELS.get(mapn, mapn)

    def draw(self, surf):
        g = self.g
        from .characters import NPCS, NPC_ORDER
        season = seasons.CURRENT["season"]
        base = getattr(g, "_map_cache", None)
        if base is None or base[0] != season:
            g._map_cache = base = (season, _base(g))
        mapimg = base[1]
        rect = pygame.Rect(0, 0, mapimg.get_width() + 380, mapimg.get_height() + 96)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, f"Mapa de National City  —  {seasons.NAMES[season]}", (rect.x + 24, rect.y + 14), 26, C_LILAC,
                bold=True)
        mx, my = rect.x + 20, rect.y + 56
        surf.blit(mapimg, (mx, my))
        pygame.draw.rect(surf, C_ACCENT_2, (mx - 2, my - 2, mapimg.get_width() + 4, mapimg.get_height() + 4), 2,
                         border_radius=4)
        # personagens
        stacks = {}
        rows = []
        for key in NPC_ORDER:
            n = g.npcs.get(key)
            if not n or not n.map:
                continue
            mapn = n.map.name if hasattr(n.map, "name") else n.map
            pos, label = self.where(mapn)
            if pos is None and mapn == "city":
                pos = (n.fx, n.fy)
            rows.append((key, NPCS[key]["short"], label))
            if pos is None:
                continue
            k = stacks.get(pos, 0)
            stacks[pos] = k + 1
            px = mx + int(pos[0] * T) + T // 2 + (k % 4) * 12 - 6
            py = my + int(pos[1] * T) - 14 - (k // 4) * 14
            img = _head(n.current_frames())
            ring = C_PINK if key in ("lucy", "vittoria") else (40, 30, 50)
            pygame.draw.circle(surf, ring, (px, py + 8), 11)
            pygame.draw.circle(surf, (250, 248, 255), (px, py + 8), 10)
            surf.blit(img, (px - 9, py))
        # a jogadora (pisca)
        pmap = g.map_name
        ppos, plabel = self.where(pmap)
        if pmap == "city":
            ppos = g.player.tile
        if ppos:
            px, py = mx + int(ppos[0] * T) + T // 2, my + int(ppos[1] * T) + T // 2
            r = 7 + int(3 * (0.5 + 0.5 * math.sin(self.t * 5)))
            pygame.draw.circle(surf, (110, 231, 140), (px, py), r, 3)
            pygame.draw.circle(surf, (110, 231, 140), (px, py), 3)
        # lista ao lado
        lx = mx + mapimg.get_width() + 24
        ly = my
        ui.text(surf, f"Você: {plabel}", (lx, ly), 17, (110, 231, 140), bold=True)
        ly += 30
        ui.text(surf, "Quem está na cidade agora", (lx, ly), 16, C_MUTED)
        ly += 26
        for key, name, label in rows:
            if ly > rect.bottom - 64:
                ui.text(surf, f"+ {len(rows) - rows.index((key, name, label))} pessoas", (lx, ly), 14, C_MUTED)
                break
            ui.text(surf, name, (lx, ly), 16, C_PINK if key in ("lucy", "vittoria") else C_TEXT, bold=True)
            ui.text(surf, label, (lx + 92, ly + 2), 14, C_MUTED)
            ly += 22
        out = len(NPC_ORDER) - len(rows)
        if out:
            ui.text(surf, f"{out} em casa ou fora da cidade", (lx, ly + 6), 14, C_MUTED)
        ui.text(surf, "M / Esc: fechar", (rect.right - 24, rect.bottom - 30), 16, C_MUTED, right=True)

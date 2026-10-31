"""Iluminação: noite, chuva e pôr do sol com um "mapa de luz".

Em vez de cobrir a tela com um véu azul semitransparente (que deixava tudo acinzentado), o mundo é
MULTIPLICADO por uma camada de luz: escura e azulada à noite, com manchas claras onde há luz (postes,
janelas acesas, portas de lojas, faróis dos carros e um pouco em volta da Letícia). Assim as cores continuam
vivas, o escuro fica azul de verdade e os lugares iluminados aparecem com a cor original.
No pôr do sol a camada fica dourada e ganha um brilho quente por cima.
Chamado por Game.draw_world depois de desenhar o mundo (lighting.apply).
"""
import pygame

from .config import SCALE, TILE

# cor que multiplica o mundo com a escuridão máxima (0,7 em Game.darkness)
NIGHT_OUT = (64, 78, 150)          # rua: noite azul
NIGHT_OPEN = (96, 100, 170)        # terraço (ao ar livre, mas com as luzes da cobertura)
NIGHT_IN = (190, 178, 214)         # interiores: as luzes estão acesas, escurece pouco
RAIN = (0.80, 0.83, 0.90)          # chuva: mais escuro e acinzentado (dia e noite)
# Interiores: (cor de dia, cor de noite, cor da luz do teto, distância entre as luzes em tiles)
# A cor de dia/noite multiplica a sala; as luzes do teto somam por cima, então perto delas fica claro e quente
# e os cantos ficam mais escuros (clima de lugar fechado).
INTERIOR = {
    "_": ((236, 228, 238), (104, 96, 146), (150, 120, 80), 5),
    "home": ((238, 230, 236), (96, 88, 140), (160, 124, 78), 5),
    "hq": ((236, 232, 242), (100, 96, 150), (140, 128, 110), 5),
    "cafe": ((238, 226, 222), (110, 92, 120), (170, 126, 72), 4),
    "catco": ((234, 236, 244), (100, 104, 150), (140, 136, 126), 5),
    "books": ((236, 226, 220), (104, 90, 120), (170, 128, 74), 4),
    "market": ((240, 236, 236), (110, 104, 146), (150, 140, 120), 5),
    "trattoria": ((238, 224, 216), (110, 88, 110), (176, 122, 66), 4),
    "bar": ((196, 176, 206), (80, 62, 104), (150, 90, 110), 4),
    "cinema": ((150, 138, 176), (110, 96, 140), (90, 70, 60), 6),
    "hospital": ((240, 244, 244), (130, 140, 170), (120, 128, 126), 5),
    "ricci": ((238, 228, 228), (100, 88, 130), (166, 122, 76), 5),
    "marina": ((236, 232, 240), (96, 98, 146), (156, 126, 84), 5),
}
# objetos que brilham por conta própria: (cor, raio em tiles)
EMITTERS = {
    "tv_big": ((80, 120, 190), 2.6), "tv_wall": ((80, 120, 190), 2.6), "aquarium": ((60, 150, 170), 2.4),
    "stove": ((190, 100, 40), 1.8), "oven": ((200, 100, 40), 2.2), "neon": ((210, 70, 150), 3.0),
    "jukebox": ((200, 80, 190), 2.4), "arcade": ((80, 120, 230), 2.2), "vending": ((140, 170, 200), 1.8),
    "cooler": ((120, 150, 180), 1.4), "fridge2": ((130, 160, 190), 2.0), "cine_screen": ((150, 160, 210), 6.0),
    "bottle_shelf": ((170, 110, 60), 2.0), "wine_shelf": ((150, 90, 60), 1.6), "monitor": ((70, 150, 140), 1.4),
    "terminal": ((90, 110, 210), 2.0), "ceo_desk": ((120, 120, 170), 1.6), "popcorn": ((200, 150, 60), 1.8),
    "menuboard": ((150, 110, 70), 1.6), "string_lights": ((220, 170, 90), 2.6), "fireplace": ((220, 110, 40), 3.0),
}
NEON_STYLES = ("tower", "bar", "cinema", "marina", "ricci", "catco", "hospital")   # letreiros que brilham à noite

_cache = {}


def _radial(radius, color, power=2.0, squash=1.0):
    """Mancha de luz redonda (ou achatada), forte no meio e sumindo na borda. Sem alfa: para BLEND_RGB_ADD."""
    key = ("radial", radius, color, power, squash)
    s = _cache.get(key)
    if s is None:
        s = pygame.Surface((radius * 2, radius * 2))
        s.fill((0, 0, 0))
        for r in range(radius, 0, -2):
            k = (1 - r / radius) ** power
            pygame.draw.circle(s, tuple(int(c * k) for c in color), (radius, radius), r)
        if squash != 1.0:
            s = pygame.transform.smoothscale(s, (radius * 2, max(2, int(radius * 2 * squash))))
        _cache[key] = s
    return s


def _headlight(facing_right):
    """Facho dos faróis: um leque que vai clareando a pista à frente do carro."""
    key = ("farol", facing_right)
    s = _cache.get(key)
    if s is None:
        L, H = int(4.5 * TILE), int(1.6 * TILE)
        s = pygame.Surface((L, H))
        s.fill((0, 0, 0))
        for i in range(L, 0, -3):
            k = (1 - i / L) ** 1.3 * 0.75
            half = 3 * SCALE + (H / 2 - 3 * SCALE) * (i / L)
            col = (int(255 * k), int(236 * k), int(180 * k))
            pygame.draw.polygon(s, col, [(0, H / 2 - 3 * SCALE), (i, H / 2 - half), (i, H / 2 + half),
                                         (0, H / 2 + 3 * SCALE)])
        s = pygame.transform.smoothscale(pygame.transform.smoothscale(s, (L // 4, H // 4)), (L, H))
        if not facing_right:
            s = pygame.transform.flip(s, True, False)
        _cache[key] = s
    return s


def _window_light(spr):
    """Luz das janelas acesas de um prédio: os pixels amarelos das janelas + um brilho em volta.
    Guardado por desenho (os prédios são cacheados em art.building_sprite)."""
    key = ("janelas", id(spr))
    hit = _cache.get(key)
    if hit is not None and hit[0] is spr:
        return hit[1]
    mask = pygame.mask.from_threshold(spr, (252, 222, 136, 255), (10, 10, 10, 255))
    w, h = spr.get_size()
    light = None
    if mask.count():
        exact = mask.to_surface(setcolor=(228, 222, 210, 255), unsetcolor=(0, 0, 0, 255)).convert()
        small = pygame.transform.smoothscale(exact, (max(1, w // 6), max(1, h // 6)))
        halo = pygame.transform.smoothscale(small, (w, h))
        halo.fill((150, 120, 70), special_flags=pygame.BLEND_RGB_MULT)     # brilho quente e mais fraco
        light = exact
        light.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    _cache[key] = (spr, light)
    return light


def _base_color(m, open_air, dark, sun, rain):
    """Cor da camada de luz sem nenhuma lâmpada (o 'céu' daquela hora)."""
    if m.outdoor:
        night, k = NIGHT_OUT, dark / 0.7
    elif open_air:
        night, k = NIGHT_OPEN, dark / 0.7
    else:
        night, k = NIGHT_IN, dark / 0.7
    k = max(0.0, min(1.0, k))
    c = [255 + (n - 255) * k for n in night]
    if sun > 0 and open_air:                      # fim de tarde: tudo puxa para o dourado
        c = [c[0], c[1] * (1 - 0.13 * sun), c[2] * (1 - 0.30 * sun)]
    if rain:
        c = [v * f for v, f in zip(c, RAIN)]
    return tuple(max(0, min(255, int(v))) for v in c), k


def _ceiling_spots(m, spacing):
    """Lugares das luzes do teto: uma a cada `spacing` tiles, só onde há chão (calculado uma vez por mapa)."""
    spots = getattr(m, "_light_spots", None)
    if spots is None:
        spots = []
        off = spacing // 2
        for y in range(off, m.h, spacing):
            for x in range(off, m.w, spacing):
                t = m.tiles[y][x]
                if t not in ("wall", "wall_top", "void", "glass") and not t.startswith("wall"):
                    spots.append(((x + 0.5) * TILE, (y + 0.5) * TILE))
        m._light_spots = spots
    return spots


def _interior(surf, m, cam, dark, player):
    """Luz de lugar fechado: sala um pouco mais escura, poças de luz do teto e objetos que brilham."""
    SW, SH = surf.get_size()
    day, night, pool_col, spacing = INTERIOR.get(m.name, INTERIOR["_"])
    k = max(0.0, min(1.0, dark / 0.7))
    base = tuple(int(d + (n - d) * k) for d, n in zip(day, night))
    layer = _cache.get(("camada", SW, SH))
    if layer is None:
        layer = _cache[("camada", SW, SH)] = pygame.Surface((SW, SH))
    layer.fill(base)
    add = pygame.BLEND_RGB_ADD
    strength = 0.55 + 0.45 * k                              # as luzes aparecem mais quando lá fora escurece
    pool = _radial(int(spacing * 0.95 * TILE), tuple(int(c * strength) for c in pool_col), 1.3, 0.8)
    pw, ph = pool.get_size()
    for (wx, wy) in _ceiling_spots(m, spacing):
        x, y = int(wx - cam[0]), int(wy - cam[1])
        if -pw < x < SW + pw and -ph < y < SH + ph:
            layer.blit(pool, (x - pw // 2, y - ph // 2), special_flags=add)
    for o in m.objects:
        em = EMITTERS.get(o.kind)
        if em is None:
            continue
        col, rad = em
        cx = int((o.x + o.w / 2) * TILE - cam[0])
        cy = int((o.y + o.h / 2) * TILE - cam[1])
        glow = _radial(int(rad * TILE), tuple(int(c * (0.6 + 0.4 * k)) for c in col), 1.6)
        gw = glow.get_width() // 2
        if -gw < cx < SW + gw and -gw < cy < SH + gw:
            layer.blit(glow, (cx - gw, cy - gw), special_flags=add)
    if player is not None and k > 0.2:
        me = _radial(int(1.6 * TILE), (60, 54, 60), 1.4, 0.8)
        px, py = int(player.x - cam[0]), int(player.y - 12 * SCALE - cam[1])
        layer.blit(me, (px - me.get_width() // 2, py - me.get_height() // 2), special_flags=add)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


def apply(g, surf, m, cam, dark, sun, rain, open_air, lamps, windows, player, cars):
    SW, SH = surf.get_size()
    if not m.outdoor and not open_air:
        _interior(surf, m, cam, dark, player)
        return
    base, k = _base_color(m, open_air, dark, sun, rain)
    if min(base) < 253:
        layer = _cache.get(("camada", SW, SH))
        if layer is None:
            layer = _cache[("camada", SW, SH)] = pygame.Surface((SW, SH))
        layer.fill(base)
        lit = k > 0.25 and (m.outdoor or open_air)        # luzes acendem quando escurece de fato
        if lit:
            add = pygame.BLEND_RGB_ADD
            pool = _radial(int(3.4 * TILE), (255, 196, 120), 1.6, 0.72)      # chão iluminado pelo poste
            for (lx, ly) in lamps:
                cx, cy = lx, ly + 26 * SCALE
                layer.blit(pool, (cx - pool.get_width() // 2, cy - pool.get_height() // 2), special_flags=add)
            for spr, x, y in windows:
                wl = _window_light(spr)
                if wl is not None:
                    layer.blit(wl, (x, y), special_flags=add)
            door = _radial(int(1.9 * TILE), (230, 170, 100), 1.8, 0.7)       # vitrine/porta acesa
            for b in m.buildings:
                if b.target:
                    cx = int((b.door[0] + 0.5) * TILE - cam[0])
                    cy = int((b.door[1] + 1) * TILE - cam[1])
                    if -TILE * 3 < cx < SW + TILE * 3 and -TILE * 3 < cy < SH + TILE * 3:
                        layer.blit(door, (cx - door.get_width() // 2, cy - door.get_height() // 2), special_flags=add)
            for c in cars:
                fx = int(c.front - cam[0])
                fy = int(c.base_y - 6 * SCALE - cam[1])
                beam = _headlight(c.dir > 0)
                bx = fx if c.dir > 0 else fx - beam.get_width()
                if -beam.get_width() < bx < SW and -TILE * 2 < fy < SH + TILE * 2:
                    layer.blit(beam, (bx, fy - beam.get_height() // 2), special_flags=add)
            if player is not None:                    # um pouco de luz em volta da Letícia (ela nunca some)
                me = _radial(int(2.2 * TILE), (120, 110, 120), 1.4, 0.8)
                px, py = int(player.x - cam[0]), int(player.y - 12 * SCALE - cam[1])
                layer.blit(me, (px - me.get_width() // 2, py - me.get_height() // 2), special_flags=add)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        if lit:
            bulb = _radial(int(1.1 * TILE), (255, 214, 140), 2.2)      # brilho da lâmpada em si, por cima do escuro
            for (lx, ly) in lamps:
                surf.blit(bulb, (lx - bulb.get_width() // 2, ly - bulb.get_height() // 2), special_flags=pygame.BLEND_RGB_ADD)
    if sun > 0 and open_air:                          # brilho dourado do pôr do sol
        warm = _cache.get(("dourado", SW, SH))
        if warm is None:
            warm = _cache[("dourado", SW, SH)] = pygame.Surface((SW, SH))
        warm.fill((int(46 * sun), int(22 * sun), int(4 * sun)))
        surf.blit(warm, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

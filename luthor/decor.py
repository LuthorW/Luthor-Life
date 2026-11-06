"""Decorar a cobertura: comprar móveis no catálogo e escolher onde cada um fica.

Entra pelo computador da cobertura ("Decorar a cobertura"). Só os móveis comprados podem ser mexidos (os da casa
original ficam onde estão, porque cenas e rotinas usam esses lugares). Um móvel não pode tapar a porta, um lugar
reservado (onde a namorada, o bichinho e as cenas ficam) nem deixar qualquer canto da casa sem acesso.
Os quadros vão na parede; os tapetes no chão (dá para andar por cima).
"""
import math

import pygame

from . import art, ui, audio, world, lighting
from .art import new, R, P, shade
from .config import SCREEN_W, SCREEN_H, TILE, SCALE, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_RED, C_LILAC, C_ACCENT

HOME = "home"
DOOR_IN = (16, 14)

# tipo: (nome, preço, onde: "chao" | "tapete" | "parede")
CATALOG = {
    "plant": ("Vaso de planta", 60, "chao"),
    "plant_big": ("Planta grande", 120, "chao"),
    "orquidea": ("Orquídea", 90, "chao"),
    "flowerpot": ("Vaso de flores", 50, "chao"),
    "flowerstand": ("Floreira", 140, "chao"),
    "luminaria": ("Luminária de pé", 160, "chao"),
    "armchair": ("Poltrona vermelha", 220, "chao"),
    "poltrona_roxa": ("Poltrona roxa", 300, "chao"),
    "sofa_grey": ("Sofá cinza", 480, "chao"),
    "chair": ("Cadeira", 70, "chao"),
    "cafe_mesa": ("Mesinha redonda", 120, "chao"),
    "coffee_table": ("Mesa de centro", 180, "chao"),
    "bookshelf": ("Estante de livros", 260, "chao"),
    "bookshelf2": ("Estante colorida", 260, "chao"),
    "trophy": ("Estante de troféus", 400, "chao"),
    "statue": ("Estátua", 650, "chao"),
    "piano": ("Piano", 1800, "chao"),
    "rug": ("Tapete grande", 200, "tapete"),
    "rug_green": ("Tapete verde", 200, "tapete"),
    "rug_red": ("Tapete vermelho", 150, "tapete"),
    "painting": ("Quadro de paisagem", 250, "parede"),
    "painting2": ("Quadro abstrato", 250, "parede"),
    "poster": ("Pôster", 80, "parede"),
    "poster2": ("Pôster de filme", 80, "parede"),
}
ORDER = list(CATALOG)


# ---------------------------------------------------------------------------
# Arte nova
# ---------------------------------------------------------------------------
def _luminaria():
    s = new(16, 32)
    R(s, (60, 48, 70), 4, 29, 8, 2)
    R(s, (96, 84, 108), 7, 11, 2, 18)
    R(s, (130, 118, 140), 7, 11, 1, 18)
    pygame.draw.polygon(s, (246, 226, 176), [(2, 11), (13, 11), (11, 3), (4, 3)])
    R(s, (214, 182, 124), 2, 10, 12, 1)
    R(s, (255, 244, 210), 5, 4, 3, 5)
    return s


def _piano():
    s = new(32, 26)
    R(s, (38, 22, 20), 1, 1, 30, 23)
    R(s, (66, 40, 32), 2, 2, 28, 9)
    R(s, (92, 60, 46), 2, 2, 28, 1)
    R(s, (240, 236, 226), 11, 4, 10, 6)
    for y in (5, 7, 9):
        R(s, (120, 110, 130), 12, y, 8, 1)
    R(s, (200, 170, 90), 4, 5, 3, 3); P(s, (255, 230, 140), 5, 5)       # castiçal
    R(s, (250, 250, 246), 2, 12, 28, 5)
    for x in range(3, 30, 3):
        R(s, (30, 26, 30), x, 12, 2, 3)
    R(s, (54, 32, 26), 2, 17, 28, 6)
    R(s, (70, 44, 34), 3, 18, 26, 1)
    R(s, (200, 170, 90), 13, 22, 2, 1); R(s, (200, 170, 90), 17, 22, 2, 1)
    return s


def _orquidea():
    s = new(16, 22)
    R(s, (236, 232, 240), 4, 16, 8, 5); R(s, (200, 196, 210), 4, 20, 8, 1)
    R(s, (70, 130, 70), 7, 6, 1, 10)
    R(s, (60, 120, 60), 3, 14, 4, 2); R(s, (60, 120, 60), 9, 14, 4, 2)
    for (x, y) in ((5, 4), (9, 3), (6, 8), (10, 7)):
        R(s, (232, 140, 210), x, y, 3, 3)
        P(s, (255, 230, 120), x + 1, y + 1)
    return s


def _poltrona_roxa():
    from .art import _armchair
    return _armchair((118, 52, 176))


art.OBJECT_BUILDERS.update({"luminaria": _luminaria, "piano": _piano, "orquidea": _orquidea,
                            "poltrona_roxa": _poltrona_roxa})
world.OBJECT_DEFS.update({"luminaria": (1, 1, True, "obj"), "piano": (2, 1, True, "obj"),
                          "orquidea": (1, 1, True, "obj"), "poltrona_roxa": (1, 1, True, "obj")})
lighting.EMITTERS.update({"luminaria": ((255, 196, 120), 2.6)})


# ---------------------------------------------------------------------------
# Estado e montagem no mapa
# ---------------------------------------------------------------------------
def init_state(g):
    g.decor = dict(placed=[], stored={}, piano_day=-1)
    if getattr(g, "world", None):
        apply(g)


def save_state(g):
    return {"decor": g.decor}


def load_state(g, d):
    dd = d.get("decor") or {}
    g.decor = dict(placed=[list(p) for p in dd.get("placed", []) if p and p[0] in CATALOG],
                   stored={k: int(v) for k, v in (dd.get("stored") or {}).items() if k in CATALOG and v > 0},
                   piano_day=dd.get("piano_day", -1))
    apply(g)


def _recompute(m, floor=False):
    """Refaz o que bloqueia (como world.GameMap.finalize, sem duplicar as animações)."""
    m.solid = [[m.tiles[y][x] in world.SOLID_TILES for x in range(m.w)] for y in range(m.h)]
    for o in m.objects:
        if o.solid:
            for yy in range(o.y, o.y + o.h):
                for xx in range(o.x, o.x + o.w):
                    if m.in_bounds(xx, yy):
                        m.solid[yy][xx] = True
    for (dx, dy) in m.doors:
        m.solid[dy][dx] = False
    m.hitboxes = {}
    for o in m.objects:
        hb = world.HITBOXES.get(o.kind) if o.solid else None
        if not hb:
            continue
        r = pygame.Rect(o.x * TILE + hb[0] * SCALE, o.y * TILE + hb[1] * SCALE, hb[2] * SCALE, hb[3] * SCALE)
        for yy in range(o.y, o.y + o.h):
            for xx in range(o.x, o.x + o.w):
                if m.in_bounds(xx, yy) and m.tiles[yy][xx] not in world.SOLID_TILES:
                    m.hitboxes[(xx, yy)] = r
    m.wall_decor = [o for o in m.objects if o.layer == "wall"]
    if floor:
        m.water_edges = []
        m._build_floor()


def apply(g):
    """Põe no mapa da cobertura os móveis colocados (tira os antigos antes)."""
    m = g.world.get(HOME)
    if m is None:
        return
    had_rug = any(o.data == "decor" and o.layer == "decal" for o in m.objects)
    m.objects = [o for o in m.objects if o.data != "decor"]
    rug = False
    for kind, x, y in g.decor["placed"]:
        o = m.add(kind, x, y, "decor")
        rug = rug or o.layer == "decal"
    _recompute(m, floor=rug or had_rug)


_RES = {}


def _scene_tiles(steps):
    """Tiles por onde os atores passam numa cena (eles andam em linha reta: primeiro em x, depois em y)."""
    pos, out = {}, set()
    for cmd in steps:
        if not isinstance(cmd, tuple) or len(cmd) < 4:
            continue
        if cmd[0] == "ator" and isinstance(cmd[2], int) and isinstance(cmd[3], int):
            pos[cmd[1]] = (cmd[2], cmd[3])
            out.add(pos[cmd[1]])
        elif cmd[0] in ("andar", "andar_") and isinstance(cmd[2], int) and isinstance(cmd[3], int):
            x, y = cmd[2], cmd[3]
            fx, fy = pos.get(cmd[1], (x, y))
            for xx in range(min(fx, x), max(fx, x) + 1):
                out.add((xx, fy))
            for yy in range(min(fy, y), max(fy, y) + 1):
                out.add((x, yy))
            pos[cmd[1]] = (x, y)
    return out


def reserved(g):
    """Lugares que precisam ficar livres: porta, cama, cenas, a namorada e o bichinho."""
    if "home" in _RES:
        return _RES["home"]
    out = {DOOR_IN, (16, 13), world.HOME_BED, (20, 7), (14, 12), (24, 14), (23, 14), (24, 13)}
    out |= {(x, 4) for x in range(16, 23)}                      # café da manhã (casal.py)
    try:
        from .cutscenes import SCENES, move_in_scene
        for sc in SCENES.values():
            if sc.get("map") == HOME:
                out |= _scene_tiles(sc.get("steps", []))
        for key in ("lucy", "vittoria"):
            out |= _scene_tiles(move_in_scene(key).get("steps", []))
    except Exception:
        pass
    _RES["home"] = out
    return out


def _footprint(kind, x, y):
    w, h = world.OBJECT_DEFS[kind][:2]
    return [(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w)]


def _reach(m, blocked=()):
    blocked = set(blocked)
    seen = {DOOR_IN}
    todo = [DOOR_IN]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in seen or not m.in_bounds(*n) or m.solid[n[1]][n[0]] or n in blocked:
                continue
            seen.add(n)
            todo.append(n)
    return seen


def can_place(g, kind, x, y, moving=None):
    """(ok, motivo) para pôr `kind` com o canto em (x, y). `moving` = objeto que está sendo mudado de lugar."""
    m = g.world[HOME]
    where = CATALOG[kind][2]
    tiles = _footprint(kind, x, y)
    others = [o for o in m.objects if o is not moving]
    if any(not m.in_bounds(*t) for t in tiles):
        return False, "Fora da casa."
    if where == "parede":
        if y != 1:
            return False, "Quadros vão na parede."
        for (tx, ty) in tiles:
            if m.tiles[ty][tx] != "wall" or m.tiles[ty + 1][tx] in world.SOLID_TILES:
                return False, "Esse pedaço de parede não dá."
            if any(o.layer in ("wall", "decal") and o.covers(tx, ty) for o in others):
                return False, "Já tem algo pendurado aí."
        return True, ""
    for (tx, ty) in tiles:
        if m.tiles[ty][tx] in world.SOLID_TILES or (tx, ty) in m.doors:
            return False, "Só dá no chão."
    if where == "tapete":
        for (tx, ty) in tiles:
            if any(o.layer == "decal" and o.covers(tx, ty) for o in others):
                return False, "Já tem um tapete aí."
        return True, ""
    res = reserved(g)
    # tira o móvel que está sendo mudado de lugar da conta
    saved = []
    if moving is not None and moving.solid:
        for (tx, ty) in _footprint(moving.kind, moving.x, moving.y):
            if m.in_bounds(tx, ty):
                saved.append((tx, ty, m.solid[ty][tx]))
                m.solid[ty][tx] = False
    try:
        for (tx, ty) in tiles:
            if m.solid[ty][tx] or any(o.layer == "obj" and o.covers(tx, ty) for o in others):
                return False, "Tem outro móvel aí."
            if (tx, ty) in res:
                return False, "Esse lugar precisa ficar livre."
        before = _reach(m)
        after = _reach(m, tiles)
        lost = [t for t in before if t not in after and t not in tiles]
        if lost:
            return False, "Assim um canto da casa fica sem passagem."
        for o in others:                          # todo móvel da casa continua com um lado acessível
            if not o.solid or o.layer != "obj":
                continue
            near = [(xx, yy) for (xx, yy) in _border(o) if (xx, yy) in before]
            if near and not any(t in after for t in near):
                return False, f"Assim não dá para usar outro móvel."
        return True, ""
    finally:
        for (tx, ty, v) in saved:
            m.solid[ty][tx] = v


def _border(o):
    out = []
    for xx in range(o.x - 1, o.x + o.w + 1):
        out += [(xx, o.y - 1), (xx, o.y + o.h)]
    for yy in range(o.y, o.y + o.h):
        out += [(o.x - 1, yy), (o.x + o.w, yy)]
    return out


# ---------------------------------------------------------------------------
# Piano
# ---------------------------------------------------------------------------
def _piano_sfx():
    from .audio import add_note, midi, RATE
    b = [0.0] * int(2.6 * RATE)
    notes = [(0, 64), (0.28, 67), (0.56, 71), (0.84, 72), (1.12, 71), (1.4, 67), (1.68, 69), (2.0, 64)]
    for t, n in notes:
        add_note(b, t, 0.5, midi(n), "tri", 0.26, 0.004, 0.45)
        add_note(b, t, 0.5, midi(n - 12), "sine", 0.12, 0.004, 0.45)
    for t, n in ((0, 48), (1.12, 45), (2.0, 48)):
        add_note(b, t, 0.9, midi(n), "sine", 0.16, 0.01, 0.8)
    return {"piano": b}


audio.EXTRA_SFX.append(_piano_sfx)


def object_label(g, o):
    if o.kind == "piano":
        return "Tocar piano"
    return None


def use_object(g, o):
    if o.kind != "piano":
        return False
    audio.sfx("piano")
    if g.decor["piano_day"] != g.abs_day():
        g.decor["piano_day"] = g.abs_day()
        g.energy = min(g.max_energy, g.energy + 10)
        g.toasts.push("Você tocou uma valsa curtinha. Relaxou! (+10 de energia)", C_LILAC)
    else:
        g.toasts.push("Mais uma música, só para você.", C_LILAC)
    return True


# ---------------------------------------------------------------------------
# Tela de decoração
# ---------------------------------------------------------------------------
def open_editor(g):
    if g.map_name != HOME:
        g.say("Dá para decorar a cobertura pelo computador de casa.")
        return
    g.push(DecorMode(g))


class DecorMode(ui.Modal):
    REPEAT = 0.11

    def __init__(self, g):
        self.g = g
        self.m = g.world[HOME]
        self.mode = "browse"                 # browse | catalog | place
        self.cur = list(g.player.facing_tile())
        self.kind = None
        self.moving = None
        self.sel = 0
        self.top = 0
        self.msg, self.msg_t = "", 0.0
        self.held = None
        self.hold_t = 0.0
        self.t = 0.0

    # --- entrada ---
    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL and self.mode == "catalog":
            self.sel = (self.sel - ev.y) % len(ORDER)
            return
        if ev.type == pygame.KEYUP and self.held == ev.key:
            self.held = None
            return
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        if self.mode == "catalog":
            if k in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(ORDER); audio.sfx("move")
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(ORDER); audio.sfx("move")
            elif k in ui.CONFIRM:
                self.start_place(ORDER[self.sel])
            elif k in ui.CANCEL or k == pygame.K_c:
                self.mode = "browse"
            return
        if k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_UP, pygame.K_w,
                 pygame.K_DOWN, pygame.K_s):
            self.step(k)
            self.held, self.hold_t = k, -0.25
            return
        if self.mode == "place":
            if k in ui.CONFIRM:
                self.place()
            elif k in ui.CANCEL:
                if self.moving is not None:                  # desistiu de mudar: fica onde estava
                    self.moving = None
                self.mode, self.kind = "browse", None
            return
        # browse
        if k == pygame.K_c:
            self.mode = "catalog"
            audio.sfx("page")
        elif k in ui.CONFIRM:
            o = self.decor_at(*self.cur)
            if o is None:
                self.flash("Aqui não tem móvel seu. Aperte C para abrir o catálogo.")
            else:
                self.moving, self.kind, self.mode = o, o.kind, "place"
                self.cur = [o.x, o.y]
                audio.sfx("pickup")
        elif k == pygame.K_g:
            o = self.decor_at(*self.cur)
            if o is None:
                self.flash("Aqui não tem móvel seu para guardar.")
            else:
                self.store(o)
        elif k in ui.CANCEL:
            self.done = True

    def step(self, k):
        dx = (-1 if k in (pygame.K_LEFT, pygame.K_a) else 1 if k in (pygame.K_RIGHT, pygame.K_d) else 0)
        dy = (-1 if k in (pygame.K_UP, pygame.K_w) else 1 if k in (pygame.K_DOWN, pygame.K_s) else 0)
        self.cur[0] = max(0, min(self.m.w - 1, self.cur[0] + dx))
        self.cur[1] = max(1, min(self.m.h - 2, self.cur[1] + dy))

    def update(self, dt):
        self.t += dt
        self.msg_t = max(0.0, self.msg_t - dt)
        if self.held is not None and self.mode != "catalog":
            self.hold_t += dt
            while self.hold_t >= self.REPEAT:
                self.hold_t -= self.REPEAT
                self.step(self.held)

    def flash(self, msg, sound="blip"):
        self.msg, self.msg_t = msg, 2.4
        if sound:
            audio.sfx(sound)

    # --- ações ---
    def decor_at(self, x, y):
        for o in reversed(self.m.objects):
            if o.data == "decor" and o.covers(x, y):
                return o
        return None

    def start_place(self, kind):
        g = self.g
        name, price, where = CATALOG[kind]
        if not g.decor["stored"].get(kind) and g.money < price:
            self.flash(f"Faltam ${price - g.money} para comprar: {name}.")
            return
        self.kind, self.moving, self.mode = kind, None, "place"
        if where == "parede":
            self.cur[1] = 1
        elif self.cur[1] < 2:
            self.cur[1] = 2

    def place(self):
        g = self.g
        x, y = self.cur
        ok, why = can_place(g, self.kind, x, y, self.moving)
        if not ok:
            self.flash(why)
            return
        name, price, _w = CATALOG[self.kind]
        placed = g.decor["placed"]
        if self.moving is not None:
            o = self.moving
            for p in placed:
                if p[0] == o.kind and p[1] == o.x and p[2] == o.y:
                    p[1], p[2] = x, y
                    break
            self.moving = None
            self.mode, self.kind = "browse", None
            apply(g)
            self.flash(f"{name} mudou de lugar.", "confirm")
            return
        st = g.decor["stored"]
        if st.get(self.kind):
            st[self.kind] -= 1
            if st[self.kind] <= 0:
                del st[self.kind]
            txt = f"{name} saiu do depósito."
        else:
            if g.money < price:
                self.flash(f"Faltam ${price - g.money}.")
                return
            g.money -= price
            txt = f"Comprou e colocou: {name} (-${price})."
        placed.append([self.kind, x, y])
        apply(g)
        self.flash(txt, "buy")
        if not st.get(self.kind) and g.money < price:          # acabou: volta a escolher
            self.mode, self.kind = "browse", None

    def store(self, o):
        g = self.g
        for i, p in enumerate(g.decor["placed"]):
            if p[0] == o.kind and p[1] == o.x and p[2] == o.y:
                del g.decor["placed"][i]
                break
        g.decor["stored"][o.kind] = g.decor["stored"].get(o.kind, 0) + 1
        apply(g)
        self.flash(f"{CATALOG[o.kind][0]} foi para o depósito.", "confirm")

    # --- desenho ---
    def camera(self):
        g, m = self.g, self.m
        vw, vh = g.view_size(m)
        px = (self.cur[0] + 0.5) * TILE
        py = (self.cur[1] + 0.5) * TILE
        mw, mh = m.w * TILE, m.h * TILE
        cx = (mw - vw) // 2 if mw <= vw else int(min(max(px - vw / 2, 0), mw - vw))
        cy = (mh - vh) // 2 + 20 if mh <= vh - 40 else int(min(max(py - vh / 2, 0), mh - vh))
        return cx // 2 * 2, cy // 2 * 2

    def draw(self, surf, cam=None):
        if cam is not None:                      # chamado de dentro do draw_world: desenha no mundo
            self.draw_world(surf, cam)
            return
        g = self.g
        g.render_map(surf, self.m, self.camera(), extra=self)
        bar = pygame.Rect(0, SCREEN_H - 92, SCREEN_W, 92)
        veil = pygame.Surface(bar.size, pygame.SRCALPHA)
        veil.fill((18, 10, 30, 225))
        surf.blit(veil, bar.topleft)
        ui.text(surf, "Decorando a cobertura", (24, 16), 26, C_GOLD, bold=True)
        ui.text(surf, f"Dinheiro: ${g.money}", (24, 48), 18, C_TEXT)
        if self.mode == "place":
            name, price, where = CATALOG[self.kind]
            have = self.g.decor["stored"].get(self.kind, 0)
            cost = "mudando de lugar" if self.moving else (f"{have} no depósito" if have else f"${price}")
            ui.text(surf, f"{name}  ({cost})", (24, bar.y + 12), 22, C_TEXT, bold=True)
            ui.text(surf, "Setas: mover   E: colocar aqui   Esc: cancelar", (24, bar.y + 48), 17, C_MUTED)
        else:
            hover = self.decor_at(*self.cur)
            label = f"Aqui: {CATALOG[hover.kind][0]}" if hover else "Escolha um lugar"
            ui.text(surf, label, (24, bar.y + 12), 22, C_TEXT, bold=True)
            ui.text(surf, "Setas: andar   C: catálogo   E: mudar de lugar   G: guardar no depósito   Esc: sair",
                    (24, bar.y + 48), 17, C_MUTED)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (SCREEN_W - 24, bar.y + 14), 20, C_GREEN if "!" in self.msg or "Comprou" in
                    self.msg or "mudou" in self.msg or "depósito" in self.msg else C_GOLD, bold=True, right=True)
        if self.mode == "catalog":
            self.draw_catalog(surf)

    def draw_world(self, surf, cam):
        x, y = self.cur
        if self.mode == "place":
            kind = self.kind
            spr = art.object_sprite(kind)
            w, h = world.OBJECT_DEFS[kind][:2]
            ok, _why = can_place(self.g, kind, x, y, self.moving)
            col = (90, 230, 120, 90) if ok else (240, 80, 80, 110)
            for (tx, ty) in _footprint(kind, x, y):
                box = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                box.fill(col)
                surf.blit(box, (tx * TILE - cam[0], ty * TILE - cam[1]))
            ghost = spr.copy()
            ghost.set_alpha(190 if ok else 120)
            surf.blit(ghost, (x * TILE - cam[0], (y + h) * TILE - spr.get_height() - cam[1]))
            r = pygame.Rect(x * TILE - cam[0], y * TILE - cam[1], w * TILE, h * TILE)
            pygame.draw.rect(surf, (240, 250, 240) if ok else (255, 140, 140), r, 2)
        else:
            o = self.decor_at(x, y)
            if o is not None:
                r = pygame.Rect(o.x * TILE - cam[0], o.y * TILE - cam[1], o.w * TILE, o.h * TILE)
                pygame.draw.rect(surf, (250, 214, 110), r, 2)
            blink = 200 if int(self.t * 3) % 2 else 255
            r = pygame.Rect(x * TILE - cam[0], y * TILE - cam[1], TILE, TILE)
            pygame.draw.rect(surf, (blink, blink, 255), r, 2)

    def draw_catalog(self, surf):
        g = self.g
        outer = pygame.Rect(SCREEN_W - 520, 40, 480, SCREEN_H - 150)
        ui.panel(surf, outer, alpha=250)
        ui.text(surf, "Catálogo de móveis", (outer.x + 22, outer.y + 14), 24, C_GOLD, bold=True)
        rows = 9
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + rows:
            self.top = self.sel - rows + 1
        y = outer.y + 54
        for i in range(self.top, min(len(ORDER), self.top + rows)):
            kind = ORDER[i]
            name, price, where = CATALOG[kind]
            r = pygame.Rect(outer.x + 14, y, outer.w - 28, 48)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            spr = art.object_sprite(kind)
            k = min(40 / spr.get_height(), 56 / spr.get_width(), 1.0)
            icon = pygame.transform.scale(spr, (max(1, int(spr.get_width() * k)), max(1, int(spr.get_height() * k))))
            surf.blit(icon, (r.x + 34 - icon.get_width() // 2, r.centery - icon.get_height() // 2))
            ui.text(surf, name, (r.x + 72, r.y + 4), 19, C_TEXT if i == self.sel else C_MUTED)
            sub = {"chao": "chão", "tapete": "tapete", "parede": "parede"}[where]
            ui.text(surf, sub, (r.x + 72, r.y + 26), 14, C_LILAC)
            have = g.decor["stored"].get(kind, 0)
            ui.text(surf, f"{have} guardado(s)" if have else f"${price}", (r.right - 12, r.y + 13), 18,
                    C_GREEN if have else C_GOLD, right=True)
            y += 52
        ui.text(surf, "E: escolher   Esc: voltar", (outer.centerx, outer.bottom - 30), 16, C_MUTED, center=True)

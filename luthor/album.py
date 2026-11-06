"""Álbum de fotos do Barry: cada cena especial vira uma foto.

O jogo "fotografa" a cena num bom momento (no beijo, se tiver; senão, um pouco depois da metade) e guarda a foto
quando ela termina. As fotos ficam em saves/album/<cena>.png e só são gravadas junto com o save (nos modos de
teste nada vai para o disco). O Barry entrega o álbum a 2 corações (menu de pausa > Álbum de fotos).
Uma foto pode ir para a mesinha com porta-retrato ou para o quadro de foto da parede (catálogo de móveis).
"""
import os

import pygame

from . import art, ui, audio, world, decor
from .art import new, R, P
from .config import SCREEN_W, SCREEN_H, SAVE_DIR, SCALE, TILE, C_TEXT, C_MUTED, C_GOLD, C_GREEN, C_LILAC, C_PINK, C_ACCENT

DIR = os.path.join(SAVE_DIR, "album")
SKIP = ("cafe_da_manha",)
SKIP_PREFIX = ("encontro_",)
THUMB = (480, 300)
EXTRA_TITLES = {"festa_flores": "Festa das Flores", "festa_luau": "Luau de Verão", "festa_feira": "Feira da Colheita",
                "festa_luzes": "Noite das Luzes", "festa_danca": "Dança das Flores",
                "aniversario_namoro": "Aniversário de namoro", "casamento": "O casamento"}


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.album = dict(keys=[], frame=None, given=False)
    g.album_photos = {}
    g.album_dirty = set()


def save_state(g):
    """Grava as fotos novas (só acontece num save de verdade)."""
    if g.album_dirty:
        try:
            os.makedirs(DIR, exist_ok=True)
            for k in list(g.album_dirty):
                img = g.album_photos.get(k)
                if img is not None:
                    pygame.image.save(img, os.path.join(DIR, f"{k}.png"))
            g.album_dirty = set()
        except OSError:
            pass
    return {"album": g.album}


def load_state(g, d):
    a = d.get("album") or {}
    keys = list(a.get("keys", []))
    # o pedido de namoro já teve dois nomes ("namoro_x" e "x_pedido"): fica uma foto só
    keys = [k for k in keys if not (k.startswith("namoro_") and f"{k[7:]}_pedido" in keys)]
    g.album = dict(keys=keys, frame=a.get("frame"), given=bool(a.get("given", False)))
    g.album_photos = {}
    g.album_dirty = set()
    for k in g.album["keys"]:
        path = os.path.join(DIR, f"{k}.png")
        if os.path.exists(path):
            try:
                g.album_photos[k] = pygame.image.load(path).convert()
            except pygame.error:
                pass
    _frame_cache.clear()


def wanted(key):
    return bool(key) and key not in SKIP and not key.startswith(SKIP_PREFIX)


# ---------------------------------------------------------------------------
# Fotografar as cenas
# ---------------------------------------------------------------------------
def attach(g, key, cs):
    """Liga a câmera numa cena: a foto é guardada quando a cena acaba."""
    if not wanted(key):
        return
    cs.album_key = key
    cs.album_snap = None
    cs.album_kiss = False
    orig = cs.on_end

    def end():
        store(g, key, cs)
        if orig:
            orig()
    cs.on_end = end


def capture(cs, surf):
    """Chamado no desenho da cena, logo depois do mundo e antes das faixas pretas e da caixa de fala."""
    if cs.fade > 0.05 or cs.photo is not None or cs.album_kiss:
        return
    if cs.kiss is not None:
        cs.album_kiss = True
    elif cs.album_snap is not None or cs.i < max(3, int(len(cs.steps) * 0.55)):
        return
    W, H = surf.get_size()
    crop = pygame.Rect(0, 0, 560, 350)
    crop.center = _actors_center(cs, W, H)
    crop.clamp_ip(surf.get_rect())
    cs.album_snap = pygame.transform.smoothscale(surf.subsurface(crop).copy(), THUMB)


def _actors_center(cs, W, H):
    """Ponto da tela no meio das personagens da cena (a foto é enquadrada nelas)."""
    g, m = cs.g, cs.map
    acts = list(cs.actors.values())
    if not acts:
        return W // 2, H // 2
    z = g.zoom_for(m)
    vw, vh = g.view_size(m)
    ox, oy = (W - vw * z) / 2, (H - vh * z) / 2
    cam = (int(cs.cam[0]) // 2 * 2, int(cs.cam[1]) // 2 * 2)
    xs = [((a.fx + 0.5) * TILE - cam[0]) * z + ox for a in acts]
    ys = [(getattr(a, "base_y", (a.fy + 1) * TILE) - 16 * SCALE - cam[1]) * z + oy for a in acts]
    pts = [(x, y) for x, y in zip(xs, ys) if -50 < x < W + 50 and -50 < y < H + 50] or list(zip(xs, ys))
    return int(sum(p[0] for p in pts) / len(pts)), int(sum(p[1] for p in pts) / len(pts))


def store(g, key, cs):
    snap = getattr(cs, "album_snap", None)
    if snap is None:
        return
    first = key not in g.album["keys"]
    if first:
        g.album["keys"].append(key)
    if first or key not in g.album_photos:
        g.album_photos[key] = snap
        g.album_dirty.add(key)
        _frame_cache.clear()
        if g.album["given"]:
            g.toasts.push(f"Foto nova no álbum: {title(g, key)}", C_PINK)


def title(g, key):
    return EXTRA_TITLES.get(key) or g.scene_title(key)


# ---------------------------------------------------------------------------
# O Barry entrega o álbum
# ---------------------------------------------------------------------------
def night(g, notes):
    if not g.album["given"] and g.hearts("barry") >= 2:
        g.album["given"] = True
        n = len(g.album_photos)
        extra = f" Ele já colou {n} foto(s) dos seus melhores momentos." if n else ""
        notes.append(("O Barry deixou um presente na portaria: um álbum de fotos com capa roxa e um bilhete: "
                      "\"Pra guardar os momentos bons. Eu cuido das fotos!\"" + extra + " (Menu de pausa: Álbum.)",
                      C_PINK))


# ---------------------------------------------------------------------------
# Porta-retratos (móveis)
# ---------------------------------------------------------------------------
def _retrato_mesa():
    s = new(16, 22)
    R(s, (90, 58, 40), 2, 12, 12, 3)
    R(s, (120, 80, 54), 2, 12, 12, 1)
    R(s, (70, 44, 30), 3, 15, 2, 7); R(s, (70, 44, 30), 11, 15, 2, 7)
    R(s, (214, 172, 84), 3, 2, 10, 9)
    R(s, (150, 110, 190), 4, 3, 8, 7)
    P(s, (250, 210, 240), 7, 5); P(s, (250, 210, 240), 8, 5)
    R(s, (160, 120, 50), 7, 11, 2, 1)
    return s


def _retrato_parede():
    s = new(16, 16)
    R(s, (60, 40, 30), 1, 2, 14, 12)
    R(s, (214, 172, 84), 2, 3, 12, 10)
    R(s, (150, 110, 190), 3, 4, 10, 8)
    P(s, (250, 210, 240), 7, 7); P(s, (250, 210, 240), 8, 7)
    return s


art.OBJECT_BUILDERS.update({"retrato_mesa": _retrato_mesa, "retrato_parede": _retrato_parede})
world.OBJECT_DEFS.update({"retrato_mesa": (1, 1, True, "obj"), "retrato_parede": (1, 1, False, "wall")})
decor.CATALOG.update({"retrato_mesa": ("Mesinha com porta-retrato", 150, "chao"),
                      "retrato_parede": ("Foto emoldurada", 200, "parede")})
decor.ORDER[:] = list(decor.CATALOG)

# área da foto dentro de cada sprite (em pixels de arte)
PHOTO_AREA = {"retrato_mesa": (4, 3, 8, 7), "retrato_parede": (3, 4, 10, 8)}
_frame_cache = {}


def object_image(g, o):
    """Sprite do porta-retrato com a foto escolhida no álbum."""
    if o.kind not in PHOTO_AREA:
        return None
    key = g.album.get("frame")
    photo = g.album_photos.get(key) if key else None
    if photo is None:
        return None
    ck = (o.kind, key)
    if ck in _frame_cache:
        return _frame_cache[ck]
    base = art.object_sprite(o.kind).copy()
    x, y, w, h = PHOTO_AREA[o.kind]
    pw, ph = w * SCALE, h * SCALE
    # recorta o miolo da foto (onde ficam as personagens) no formato da moldura
    sw, sh = photo.get_size()
    aspect = pw / ph
    cw, chh = (int(sh * aspect), sh) if sw / sh > aspect else (sw, int(sw / aspect))
    src = pygame.Rect(0, 0, int(cw * 0.5), int(chh * 0.5))
    src.center = (sw // 2, sh // 2)
    thumb = pygame.transform.smoothscale(photo.subsurface(src), (pw, ph))
    base.blit(thumb, (x * SCALE, y * SCALE))
    _frame_cache[ck] = base
    return base


def wall_image(g, o):
    return object_image(g, o)


# ---------------------------------------------------------------------------
# Tela do álbum
# ---------------------------------------------------------------------------
def open_album(g):
    g.push(Album(g))


class Album(ui.Modal):
    COLS, ROWS = 3, 2

    def __init__(self, g):
        self.g = g
        self.sel = 0
        self.big = False
        self.msg, self.msg_t = "", 0.0

    @property
    def keys(self):
        return [k for k in self.g.album["keys"] if k in self.g.album_photos]

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        keys = self.keys
        n = len(keys)
        if self.big:
            if ev.key in ui.CANCEL or ev.key in ui.CONFIRM:
                self.big = False
            elif ev.key == pygame.K_p and n:
                self.g.album["frame"] = keys[self.sel]
                _frame_cache.clear()
                audio.sfx("confirm")
                self.msg, self.msg_t = "Essa foto agora está nos porta-retratos de casa.", 2.5
            elif ev.key in (pygame.K_LEFT, pygame.K_a) and n:
                self.sel = (self.sel - 1) % n
            elif ev.key in (pygame.K_RIGHT, pygame.K_d) and n:
                self.sel = (self.sel + 1) % n
            return
        if ev.key in ui.CANCEL:
            self.done = True
            return
        if not n:
            if ev.key in ui.CONFIRM:
                self.done = True
            return
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self.sel = (self.sel - 1) % n
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self.sel = (self.sel + 1) % n
        elif ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = max(0, self.sel - self.COLS)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = min(n - 1, self.sel + self.COLS)
        elif ev.key in ui.CONFIRM:
            self.big = True
            audio.sfx("page")
            return
        else:
            return
        audio.sfx("move")

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)

    def draw(self, surf):
        g = self.g
        keys = self.keys
        outer = pygame.Rect(0, 0, 1000, 620)
        outer.center = (SCREEN_W // 2 - 30, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=255, fill=(52, 30, 74))
        ui.text(surf, "Álbum de fotos", (outer.x + 30, outer.y + 16), 30, C_GOLD, bold=True)
        ui.text(surf, "fotos por Barry Allen", (outer.x + 32, outer.y + 52), 16, C_LILAC)
        per = self.COLS * self.ROWS
        pages = max(1, (len(keys) + per - 1) // per)
        page = self.sel // per
        ui.text(surf, f"{len(keys)} foto(s)   ·   página {page + 1} de {pages}", (outer.right - 30, outer.y + 24),
                18, C_TEXT, right=True)
        if not keys:
            for i, ln in enumerate(["O álbum ainda está vazio.",
                                    "Cada cena especial (eventos de coração, festas, pedidos) vira uma foto.",
                                    "Cenas que você já viu podem ser fotografadas de novo em Rever cenas."]):
                ui.text(surf, ln, (outer.centerx, outer.centery - 30 + i * 30), 20, C_TEXT if i == 0 else C_MUTED,
                        center=True)
            return
        cw, ch = 300, 228
        gx = outer.x + (outer.w - self.COLS * cw - (self.COLS - 1) * 20) // 2
        gy = outer.y + 90
        for j, k in enumerate(keys[page * per:(page + 1) * per]):
            i = page * per + j
            col, row = j % self.COLS, j // self.COLS
            r = pygame.Rect(gx + col * (cw + 20), gy + row * (ch + 26), cw, ch)
            tilt = (-1.2, 0.8, -0.6, 1.0, -0.9, 0.7)[j % 6]
            card = pygame.Surface((cw, ch), pygame.SRCALPHA)
            card.fill((250, 246, 238))
            photo = pygame.transform.smoothscale(g.album_photos[k], (cw - 20, int((cw - 20) * 0.625)))
            card.blit(photo, (10, 10))
            ui.text(card, title(g, k), (cw // 2, ch - 40), 18, (60, 40, 80), center=True, shadow=False)
            if k == g.album.get("frame"):
                ui.text(card, "no porta-retrato", (cw // 2, ch - 20), 13, (160, 90, 140), center=True, shadow=False)
            card = pygame.transform.rotate(card, tilt)
            surf.blit(card, card.get_rect(center=r.center))
            if i == self.sel:
                pygame.draw.rect(surf, (255, 214, 110), r.inflate(14, 14), 4, border_radius=6)
        ui.text(surf, "Setas: escolher   E: ver grande   Esc: fechar", (outer.centerx, outer.bottom - 32), 16, C_MUTED,
                center=True)
        if self.big:
            veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            veil.fill((8, 4, 16, 220))
            surf.blit(veil, (0, 0))
            k = keys[self.sel]
            photo = pygame.transform.smoothscale(g.album_photos[k], (800, 500))
            r = photo.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20))
            pygame.draw.rect(surf, (250, 246, 238), r.inflate(36, 90).move(0, 24), border_radius=6)
            surf.blit(photo, r)
            ui.text(surf, title(g, k), (r.centerx, r.bottom + 14), 26, (60, 40, 80), bold=True, center=True,
                    shadow=False)
            ui.text(surf, "Setas: outra foto   P: pôr nos porta-retratos de casa   E: voltar",
                    (SCREEN_W // 2, SCREEN_H - 30), 17, C_MUTED, center=True)
        if self.msg_t > 0:
            ui.text(surf, self.msg, (SCREEN_W // 2, 24), 20, C_GREEN, bold=True, center=True)

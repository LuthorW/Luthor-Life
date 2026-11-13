"""Mural de fotos da cobertura: quadro de cortiça com varal de luzinhas na parede, em cima da escrivaninha.

Mostra até 4 fotos (`SLOTS`), escolhidas no app Fotos do celular (`g.mural` = lista de ids). Sem escolha, mostra as
4 mais recentes. Fotos vêm de dois lugares (`photos`): o álbum do Barry ("album:<cena>", g.album_photos) e o modo foto
(P), que grava em saves/fotos ("foto:<arquivo>"). O desenho entra pelo `album.wall_image` (embrulhado aqui).
"""
import os

import pygame

from . import art, world, album
from .art import new, R, P, shade
from .config import SAVE_DIR, SCALE

SLOTS = 4
PHOTO_DIR = os.path.join(SAVE_DIR, "fotos")
# área de cada foto dentro do quadro (pixels de arte)
AREAS = ((4, 6, 9, 7), (15, 4, 9, 7), (26, 6, 9, 7), (36, 4, 9, 7))
_thumbs = {}            # id -> Surface pequena (miniatura para o celular e o mural)
_cache = {}


def init_state(g):
    g.mural = []


def save_state(g):
    return {"mural": list(g.mural)}


def load_state(g, d):
    g.mural = [str(x) for x in (d.get("mural") or []) if isinstance(x, str)][:SLOTS]
    _cache.clear()


# ---------------------------------------------------------------------------
# Fotos
# ---------------------------------------------------------------------------
def _mode_files():
    try:
        names = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(".png")]
    except OSError:
        return []
    names.sort(key=lambda f: os.path.getmtime(os.path.join(PHOTO_DIR, f)))
    return names


def photos(g):
    """Lista (id, título, Surface) do mais antigo para o mais novo."""
    out = []
    for k in g.album.get("keys", []):
        img = g.album_photos.get(k)
        if img is not None:
            out.append((f"album:{k}", album.title(g, k), img))
    for f in _mode_files():
        pid = f"foto:{f}"
        img = _load_mode(pid, f)
        if img is not None:
            stamp = f[5:13]
            when = f"{stamp[6:8]}/{stamp[4:6]}" if stamp.isdigit() else ""
            out.append((pid, f"Modo foto {when}".strip(), img))
    return out


def _load_mode(pid, fname):
    if pid in _thumbs:
        return _thumbs[pid]
    try:
        full = pygame.image.load(os.path.join(PHOTO_DIR, fname))
    except (pygame.error, OSError, FileNotFoundError):
        _thumbs[pid] = None
        return None
    # recorta o miolo (a Letícia fica no meio da tela) no formato das fotos do álbum
    w, h = full.get_size()
    crop = pygame.Rect(0, 0, int(w * 0.5), int(h * 0.5))
    crop.center = (w // 2, h // 2)
    img = pygame.transform.smoothscale(full.subsurface(crop).copy(), album.THUMB)
    _thumbs[pid] = img
    return img


def shown(g):
    """Ids das fotos que estão no mural (as escolhidas ou, sem escolha, as 4 mais novas)."""
    ids = [p[0] for p in photos(g)]
    chosen = [i for i in g.mural if i in ids]
    if chosen:
        return chosen[:SLOTS]
    return ids[-SLOTS:]


def toggle(g, pid):
    """Põe/tira uma foto do mural. Devolve a mensagem."""
    if pid in g.mural:
        g.mural.remove(pid)
        _cache.clear()
        return "Foto tirada do mural."
    if len(g.mural) >= SLOTS:
        return f"O mural já tem {SLOTS} fotos. Tire uma antes."
    g.mural.append(pid)
    _cache.clear()
    return "Foto presa no mural da cobertura!"


def forget_cache():
    _cache.clear()


# ---------------------------------------------------------------------------
# Arte
# ---------------------------------------------------------------------------
def _mural():
    s = new(48, 22)
    wood, dark = (122, 82, 50), (78, 50, 30)
    R(s, dark, 0, 2, 48, 20)
    R(s, wood, 1, 3, 46, 18)
    R(s, shade(wood, 1.2), 1, 3, 46, 1)
    R(s, (182, 134, 90), 2, 4, 44, 16)                                 # cortiça
    for i in range(0, 44, 3):
        P(s, (160, 112, 72), 2 + i, 4 + (i * 7) % 15)
        P(s, (196, 150, 104), 3 + (i * 5) % 43, 5 + (i * 3) % 14)
    for (x, y, w, h) in AREAS:                                          # alfinetes esperando fotos
        P(s, (200, 70, 90), x + w // 2, y - 1)
    # varal de luzinhas por cima
    for x in range(0, 48):
        y = 1 + (abs((x % 12) - 6) // 3)
        P(s, (60, 50, 40), x, y)
        if x % 4 == 2:
            P(s, ((255, 226, 130), (255, 170, 200), (170, 220, 255))[(x // 4) % 3], x, y + 1)
    return s


def mural_image(g):
    ids = tuple(shown(g))
    if ids in _cache:
        return _cache[ids]
    base = art.object_sprite("mural_fotos").copy()
    pics = {p[0]: p[2] for p in photos(g)}
    for (x, y, w, h), pid in zip(AREAS, ids):
        img = pics.get(pid)
        if img is None:
            continue
        pw, ph = w * SCALE, h * SCALE
        S = SCALE                                                       # moldura branca (polaroid) e sombra
        pygame.draw.rect(base, (90, 70, 56), (x * S, (y + 1) * S, (w + 2) * S, (h + 3) * S))
        pygame.draw.rect(base, (250, 248, 240), ((x - 1) * S, (y - 1) * S, (w + 2) * S, (h + 3) * S))
        sw, sh = img.get_size()
        aspect = pw / ph
        cw, chh = (int(sh * aspect), sh) if sw / sh > aspect else (sw, int(sw / aspect))
        src = pygame.Rect(0, 0, int(cw * 0.6), int(chh * 0.6))
        src.center = (sw // 2, sh // 2)
        base.blit(pygame.transform.smoothscale(img.subsurface(src), (pw, ph)), (x * SCALE, y * SCALE))
        pygame.draw.rect(base, (220, 60, 80), ((x + w // 2) * SCALE, (y - 1) * SCALE, SCALE, SCALE))
    _cache.clear()
    _cache[ids] = base
    return base


art.OBJECT_BUILDERS.update({"mural_fotos": _mural})
world.OBJECT_DEFS.update({"mural_fotos": (3, 1, False, "wall")})
FLAVOR = {"mural_fotos": "O mural de fotos. As fotos se escolhem no app Fotos do celular (T)."}

_prev_wall_image = album.wall_image


def _wall_image(g, o):
    if o.kind == "mural_fotos":
        return mural_image(g)
    return _prev_wall_image(g, o)


album.wall_image = _wall_image

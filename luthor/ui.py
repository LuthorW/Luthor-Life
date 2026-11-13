"""Interface: fontes, painéis, diálogos, menus, loja, HUD e barra de itens."""
import os

import math

import pygame

from . import art, audio
from .config import (ASSETS, SCREEN_W, SCREEN_H, C_PANEL, C_PANEL_2, C_BORDER, C_BORDER_DIM, C_ACCENT, C_ACCENT_2,
                     C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_RED, C_ENERGY, HEART_POINTS, MAX_HEARTS)
from .data import ITEMS

# Retratos desenhados neste quadro, para a tela cheia redesenhar em alta resolução (Game.present):
# (arquivo, retângulo, área visível, fundo antes do retrato, como ficou depois)
HD = []


def blit_portrait(surf, img, pos):
    """Desenha um retrato e o registra para ser redesenhado nítido em telas maiores que 1280x720."""
    r = pygame.Rect(pos, img.get_size())
    clip = r.clip(surf.get_clip())          # respeita o recorte (listas com rolagem)
    src = art.PORTRAIT_SRC.get(id(img))
    if not src or surf.get_size() != (SCREEN_W, SCREEN_H) or clip.w <= 0 or clip.h <= 0:
        surf.blit(img, pos)
        return
    bg = surf.subsurface(clip).copy()
    surf.blit(img, pos)
    HD.append((src, r, clip, bg, surf.subsurface(clip).copy()))
from .config import HOTBAR_SIZE

CONFIRM = (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER)
CANCEL = (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_q)

_fonts = {}
FONT_FILE = os.path.join(ASSETS, "fonts", "Jersey10.ttf")
PIXEL_FONT = os.path.exists(FONT_FILE)


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        f = None
        if os.path.exists(FONT_FILE):
            try:
                f = pygame.font.Font(FONT_FILE, int(size * 1.5))
            except Exception:
                f = None
        if f is None:
            for name in ("Segoe UI", "Trebuchet MS", "DejaVu Sans", "Arial"):
                try:
                    path = pygame.font.match_font(name, bold=bold)
                except Exception:
                    path = None
                if path:
                    f = pygame.font.Font(path, size)
                    break
        if f is None:
            f = pygame.font.Font(None, int(size * 1.35))
            f.set_bold(bold)
        _fonts[key] = f
    return _fonts[key]


def text(surf, msg, pos, size=20, color=C_TEXT, bold=False, center=False, right=False, shadow=True):
    f = font(size, bold)
    img = f.render(str(msg), not PIXEL_FONT, color)
    x, y = pos
    if center:
        x -= img.get_width() // 2
    if right:
        x -= img.get_width()
    if shadow:
        sh = f.render(str(msg), not PIXEL_FONT, (10, 6, 16))
        surf.blit(sh, (x + 1, y + 2))
    surf.blit(img, (x, y))
    return img.get_width()


def wrap(msg, size, width, bold=False):
    f = font(size, bold)
    lines = []
    for para in str(msg).split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if f.size(test)[0] <= width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


_panel_cache = {}
U = 2                                   # 1 pixel de arte na interface (as molduras seguem a grade da pixel art)
GEM, GEM_LT, GEM_DK, GEM_LINE = (232, 186, 82), (255, 236, 164), (178, 122, 46), (86, 50, 22)


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def cut_rect(s, color, r, cut=1):
    """Retângulo com cantos em escadinha (cut = degraus de 1 px de arte), como as molduras do Stardew."""
    x, y, w, h = pygame.Rect(r)
    cut = max(0, min(cut, w // (2 * U), h // (2 * U)))
    for i in range(cut):
        ins = (cut - i) * U
        s.fill(color, (x + ins, y + i * U, w - 2 * ins, U))
        s.fill(color, (x + ins, y + h - (i + 1) * U, w - 2 * ins, U))
    s.fill(color, (x, y + cut * U, w, h - 2 * cut * U))


def _gem(s, cx, cy):
    """Pedrinha dourada em losango (7x7 px de arte) nos cantos dos painéis grandes."""
    for r, col in ((3, GEM_LINE), (2, GEM)):
        for dy in range(-r, r + 1):
            k = r - abs(dy)
            s.fill(col, (cx + (-k) * U, cy + dy * U, (2 * k + 1) * U, U))
    s.fill(GEM_LT, (cx - U, cy - U, U, U)); s.fill(GEM_LT, (cx, cy - 2 * U, U, U))
    s.fill(GEM_DK, (cx + U, cy + U, U, U)); s.fill(GEM_DK, (cx, cy + 2 * U, U, U))


def panel_image(size, alpha=235, border=C_BORDER, radius=14, fill=C_PANEL):
    """Moldura em pixel art: contorno escuro, chanfro claro em cima/à esquerda e escuro embaixo/à direita, faixa
    na cor da borda, filete interno e fundo com degradê; pedrinhas douradas nos cantos dos painéis grandes."""
    border = tuple(border or C_BORDER)
    key = (tuple(size), alpha, border, radius, tuple(fill))
    img = _panel_cache.get(key)
    if img is not None:
        return img
    w, h = size
    c = 2 if radius >= 10 else 1
    img = pygame.Surface((w + U, h + 2 * U), pygame.SRCALPHA)
    cut_rect(img, (0, 0, 0, 80), (U, 2 * U, w, h), c)                      # sombra
    cut_rect(img, (24, 12, 36, 255), (0, 0, w, h), c)                       # contorno
    cut_rect(img, (*_shade(border, 0.58), 255), (U, U, w - 2 * U, h - 2 * U), c - 1)          # chanfro escuro
    cut_rect(img, (*_mix(border, (255, 255, 255), 0.42), 255), (U, U, w - 3 * U, h - 3 * U), c - 1)  # claro
    cut_rect(img, (*border, 255), (2 * U, 2 * U, w - 4 * U, h - 4 * U), c - 2)                   # faixa
    img.fill((30, 16, 46, 255), (3 * U, 3 * U, w - 6 * U, h - 6 * U))                      # filete interno
    bx, by, bw, bh = 4 * U, 4 * U, w - 8 * U, h - 8 * U
    top = tuple(min(255, int(v * 1.35) + 6) for v in fill)
    for y in range(0, bh, U):
        t = y / max(1, bh - 1)
        col = tuple(int(top[i] + (fill[i] - top[i]) * min(1, t * 2.2)) for i in range(3))
        img.fill((*col, alpha), (bx, by + y, bw, min(U, bh - y)))
    img.fill((*_mix(top, (255, 255, 255), 0.18), alpha), (bx, by, bw, U))               # brilho em cima
    img.fill((*_shade(fill, 0.7), alpha), (bx, by + bh - U, bw, U))                       # sombra embaixo
    if min(w, h) >= 96:
        for (gx, gy) in ((3 * U, 3 * U), (w - 4 * U, 3 * U), (3 * U, h - 4 * U), (w - 4 * U, h - 4 * U)):
            _gem(img, gx, gy)
    if len(_panel_cache) > 300:
        _panel_cache.clear()
    _panel_cache[key] = img
    return img


def panel(surf, rect, alpha=235, border=C_BORDER, radius=14, fill=C_PANEL):
    """Painel com moldura em pixel art (veja panel_image)."""
    rect = pygame.Rect(rect)
    surf.blit(panel_image(rect.size, alpha, border, radius, fill), rect.topleft)


def box(surf, rect, fill, border=None, cut=1, light=None):
    """Caixinha em pixel art (cartões, linhas de lista): contorno, borda opcional e brilho de 1 px em cima."""
    r = pygame.Rect(rect)
    cut_rect(surf, (20, 10, 30), r, cut)
    inner = r.inflate(-2 * U, -2 * U)
    if border:
        cut_rect(surf, border, inner, cut - 1)
        inner = inner.inflate(-2 * U, -2 * U)
    surf.fill(fill, inner)
    surf.fill(light or _mix(fill, (255, 255, 255), 0.16), (inner.x, inner.y, inner.w, U))
    surf.fill(_shade(fill, 0.72), (inner.x, inner.bottom - U, inner.w, U))
    return inner


def slot(surf, rect, selected=False, fill=(18, 12, 28)):
    """Espaço de item afundado (barra de itens, mochila); o escolhido ganha moldura clara e cantinhos dourados."""
    r = pygame.Rect(rect)
    cut_rect(surf, (10, 6, 16), r, 1)
    inner = r.inflate(-2 * U, -2 * U)
    surf.fill(fill, inner)
    surf.fill((6, 3, 10), (inner.x, inner.y, inner.w, U))
    surf.fill((6, 3, 10), (inner.x, inner.y, U, inner.h))
    surf.fill(_mix(fill, C_BORDER_DIM, 0.6), (inner.x + U, inner.bottom - U, inner.w - U, U))
    surf.fill(_mix(fill, C_BORDER_DIM, 0.6), (inner.right - U, inner.y + U, U, inner.h - U))
    if selected:
        cut_rect(surf, C_ACCENT_2, r, 1)
        surf.fill((255, 255, 255), (r.x + 2 * U, r.y + U, r.w - 4 * U, U))
        hole = r.inflate(-4 * U, -4 * U)
        surf.fill(fill, hole)
        L = 4 * U
        for (cx, cy, sx, sy) in ((r.x, r.y, 1, 1), (r.right - U, r.y, -1, 1), (r.x, r.bottom - U, 1, -1),
                                 (r.right - U, r.bottom - U, -1, -1)):
            surf.fill(GEM, (min(cx, cx + sx * (L - U)), cy, L, U))
            surf.fill(GEM, (cx, min(cy, cy + sy * (L - U)), U, L))


def highlight(surf, rect, color=C_ACCENT, alpha=120):
    """Faixa da opção escolhida (listas e menus), com cantos em escadinha e brilho em cima."""
    r = pygame.Rect(rect)
    hl = pygame.Surface(r.size, pygame.SRCALPHA)
    cut_rect(hl, (*color, alpha), hl.get_rect(), 1)
    hl.fill((*_mix(color, (255, 255, 255), 0.5), min(255, alpha + 60)), (U, 0, r.w - 2 * U, U))
    hl.fill((*_shade(color, 0.6), alpha), (U, r.h - U, r.w - 2 * U, U))
    surf.blit(hl, r.topleft)


def name_tag(surf, x, y, name, color=None):
    f = font(20, True)
    w = f.size(name)[0] + 28
    r = pygame.Rect(x, y, w, 32)
    col = color or C_ACCENT
    cut_rect(surf, (24, 12, 36), r.inflate(2 * U, 2 * U), 2)
    cut_rect(surf, _shade(col, 0.62), r, 1)
    cut_rect(surf, _mix(col, (255, 255, 255), 0.35), (r.x, r.y, r.w - U, r.h - U), 1)
    surf.fill(col, r.inflate(-2 * U, -2 * U))
    surf.fill(_mix(col, (255, 255, 255), 0.55), (r.x + 3 * U, r.y + 2 * U, r.w - 6 * U, U))
    text(surf, name, (r.centerx, r.y + 4), 20, C_TEXT, bold=True, center=True)
    return r


def hearts_row(surf, x, y, points, k=2, total=MAX_HEARTS, locked_from=None):
    """Fileira de corações. A partir de `locked_from` eles aparecem trancados (cadeado), ainda não liberados."""
    n = points // HEART_POINTS
    for i in range(total):
        img = art.heart(i < n, k)
        hx = x + i * (img.get_width() + 3)
        if locked_from is not None and i >= locked_from:
            dim = img.copy()
            dim.fill((90, 80, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(dim, (hx, y))
            w, h = img.get_size()                     # cadeadinho em pixel art no meio do coração
            u = max(1, k)
            bx, by = hx + w // 2 - 3 * u, y + h // 2 - u
            pygame.draw.rect(surf, (210, 190, 120), (bx, by, 6 * u, 4 * u))
            pygame.draw.rect(surf, (210, 190, 120), (bx + u, by - 3 * u, u, 3 * u))
            pygame.draw.rect(surf, (210, 190, 120), (bx + 4 * u, by - 3 * u, u, 3 * u))
            pygame.draw.rect(surf, (210, 190, 120), (bx + u, by - 3 * u, 4 * u, u))
            pygame.draw.rect(surf, (90, 70, 40), (bx + 2 * u + u // 2, by + u, u, 2 * u))
        else:
            surf.blit(img, (hx, y))


# ---------------------------------------------------------------------------
# Modais
# ---------------------------------------------------------------------------

class Modal:
    blocks_time = True
    done = False

    def handle(self, ev):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


class Dialog(Modal):
    """Caixa de fala com retrato e efeito de máquina de escrever."""

    def __init__(self, speaker, lines, portrait=None, on_close=None, subtitle=""):
        self.speaker = speaker
        self.subtitle = subtitle
        self.lines = [l for l in lines if l]
        self.portrait = portrait
        self.on_close = on_close
        self.i = 0
        self.shown = 0.0
        self.t = 0.0

    @property
    def current(self):
        return self.lines[self.i] if self.lines else ""

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and (ev.key in CONFIRM or ev.key in CANCEL):
            if self.shown < len(self.current):
                self.shown = len(self.current)
            else:
                self.i += 1
                self.shown = 0
                if self.i >= len(self.lines):
                    self.done = True
                    if self.on_close:
                        self.on_close()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))

    def update(self, dt):
        self.t += dt
        before = int(self.shown)
        self.shown = min(len(self.current), self.shown + dt * 55)
        if int(self.shown) > before and self.current[before:int(self.shown)].strip():
            audio.blip()                 # letrinhas aparecendo

    H = 224                 # altura da caixa de fala (5% menor que a anterior, de 236)
    PORTRAIT = art.PORTRAIT_SIZE   # retrato grande e solto, ao lado da caixa (não fica por cima dela)

    def draw(self, surf):
        """Retrato grande à esquerda, fora da caixa; a caixa de texto começa ao lado dele, com o nome em cima."""
        bottom = SCREEN_H - 18
        x0 = 24
        if self.portrait is not None:
            p = self.portrait
            has_alpha = bool(p.get_flags() & pygame.SRCALPHA)
            size = self.PORTRAIT
            if p.get_width() != size:
                p = pygame.transform.smoothscale(p, (size, size))
            px, py = x0, bottom - size
            if not has_alpha:            # foto quadrada (sem transparência): ganha moldura
                cut_rect(surf, C_ACCENT, (px - 4, py - 4, size + 8, size + 8), 2)
            blit_portrait(surf, p, (px, py))
            x0 = px + size + 14
        rect = pygame.Rect(x0, bottom - self.H, SCREEN_W - 24 - x0, self.H)
        panel(surf, rect)
        tx = rect.x + 28
        if self.speaker:
            tag = name_tag(surf, tx - 4, rect.y - 18, self.speaker)
            if self.subtitle:
                text(surf, self.subtitle, (tag.right + 12, rect.y - 12), 16, C_LILAC)
        elif self.subtitle:
            text(surf, self.subtitle, (tx, rect.y + 14), 16, C_MUTED)
        visible = self.current[: int(self.shown)]
        y = rect.y + 32
        for line in wrap(visible, 24, rect.right - tx - 34):
            text(surf, line, (tx, y), 24)
            y += 34
        if self.shown >= len(self.current) and int(self.t * 2) % 2 == 0:
            pygame.draw.polygon(surf, C_ACCENT_2, [(rect.right - 36, rect.bottom - 28),
                                                   (rect.right - 20, rect.bottom - 28),
                                                   (rect.right - 28, rect.bottom - 19)])


class Choice(Modal):
    """Caixa de escolhas no pé da tela, como no Stardew: pergunta em cima e as opções em lista, com uma
    setinha na escolhida. Muitas opções rolam (no máximo VISIBLE por vez; a rodinha do mouse também rola)."""
    VISIBLE = 6
    ROW = 38

    def __init__(self, question, options, on_pick, on_cancel=None):
        self.question = question
        self.options = options
        self.on_pick = on_pick
        self.on_cancel = on_cancel
        self.sel = 0
        self.top = 0
        self.t = 0.0

    def _move(self, d):
        self.sel = (self.sel + d) % len(self.options)

    def _pick(self):
        self.done = True
        self.on_pick(self.sel)

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self._move(-1)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self._move(1)
            elif ev.key in CONFIRM:
                self._pick()
            elif ev.key in CANCEL:
                self.done = True
                if self.on_cancel:
                    self.on_cancel()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (4, 5):
                self._move(-1 if ev.button == 4 else 1)

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        n = len(self.options)
        vis = min(n, self.VISIBLE)
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + vis:
            self.top = self.sel - vis + 1
        x0, w = 24, SCREEN_W - 48
        qlines = wrap(self.question, 24, w - 64, bold=True) if self.question else []
        h = 26 + len(qlines) * 32 + (10 if qlines else 0) + vis * self.ROW + 18
        rect = pygame.Rect(x0, SCREEN_H - 18 - h, w, h)
        panel(surf, rect)
        y = rect.y + 22
        for l in qlines:
            text(surf, l, (rect.x + 32, y), 24, bold=True)
            y += 32
        if qlines:
            surf.fill(C_BORDER_DIM, (rect.x + 28, y + 2, rect.w - 56, U))
            surf.fill((12, 6, 20), (rect.x + 28, y + 2 + U, rect.w - 56, U))
            y += 10
        bob = int(math.sin(self.t * 7) * 3)
        for i in range(self.top, self.top + vis):
            r = pygame.Rect(rect.x + 22, y, rect.w - 44, self.ROW - 4)
            on = i == self.sel
            if on:
                highlight(surf, r)
                ax, ay = r.x + 12 + bob, r.centery          # setinha apontando para a opção
                pygame.draw.polygon(surf, C_ACCENT_2, [(ax, ay - 8), (ax + 12, ay), (ax, ay + 8)])
            text(surf, self.options[i], (r.x + 36, r.y + 4), 22, C_TEXT if on else C_MUTED)
            y += self.ROW
        if n > vis:                                        # setinhas de rolagem
            cx = rect.right - 34
            if self.top > 0:
                pygame.draw.polygon(surf, C_ACCENT_2, [(cx - 7, rect.y + 30), (cx + 7, rect.y + 30), (cx, rect.y + 22)])
            if self.top + vis < n:
                pygame.draw.polygon(surf, C_ACCENT_2, [(cx - 7, rect.bottom - 26), (cx + 7, rect.bottom - 26),
                                                       (cx, rect.bottom - 18)])


class Shop(Modal):
    """entries: lista de dicts {label, price, desc, item (opcional), buy: callable, enabled: callable}"""

    def __init__(self, title, subtitle, entries_fn, game):
        self.title = title
        self.subtitle = subtitle
        self.entries_fn = entries_fn
        self.game = game
        self.sel = 0
        self.flash = ""
        self.flash_t = 0

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        entries = self.entries_fn()
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(entries)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(entries)
        elif ev.key in CONFIRM:
            e = entries[self.sel]
            ok, msg = e["buy"]()
            self.flash, self.flash_t = msg, 2.0
            self.flash_ok = ok
        elif ev.key in CANCEL:
            self.done = True

    def update(self, dt):
        self.flash_t -= dt

    def draw(self, surf):
        entries = self.entries_fn()
        self.sel = min(self.sel, len(entries) - 1)
        rect = pygame.Rect(0, 0, 700, 500)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 40)
        panel(surf, rect)
        text(surf, self.title, (rect.x + 28, rect.y + 18), 28, C_LILAC, bold=True)
        text(surf, self.subtitle, (rect.x + 30, rect.y + 56), 17, C_MUTED)
        text(surf, f"$ {self.game.money:,}".replace(",", "."), (rect.right - 28, rect.y + 22), 26, C_GOLD,
             bold=True, right=True)
        y = rect.y + 92
        visible = 7
        start = max(0, min(self.sel - visible // 2, len(entries) - visible))
        for i in range(start, min(len(entries), start + visible)):
            e = entries[i]
            r = pygame.Rect(rect.x + 20, y, rect.w - 40, 46)
            enabled = e.get("enabled", lambda: True)()
            if i == self.sel:
                box(surf, r, C_PANEL_2, border=C_ACCENT_2)
            if e.get("item"):
                surf.blit(art.item_icon(e["item"], 2), (r.x + 8, r.y + 7))
            col = C_TEXT if enabled else C_MUTED
            text(surf, e["label"], (r.x + 54, r.y + 11), 19, col, bold=i == self.sel)
            text(surf, f"$ {e['price']}", (r.right - 14, r.y + 11), 19, C_GOLD if enabled else C_MUTED,
                 right=True)
            y += 50
        e = entries[self.sel]
        dr = pygame.Rect(rect.x + 20, rect.bottom - 68, rect.w - 40, 50)
        slot(surf, dr, fill=(14, 10, 22))
        if self.flash_t > 0:
            text(surf, self.flash, (dr.x + 14, dr.y + 13), 18, C_GREEN if self.flash_ok else C_RED)
        else:
            text(surf, e.get("desc", ""), (dr.x + 14, dr.y + 13), 17, C_MUTED)
        text(surf, "Setas: escolher   E/Enter: comprar   Esc: sair", (rect.centerx, rect.bottom + 4), 16,
             C_MUTED, center=True)


class InfoPanel(Modal):
    """Painel genérico de leitura (objetivos, relacionamentos, controles, e-mails)."""

    TOP, BOTTOM = 60, 48            # área rolável: entre o título e a linha de "fechar"

    def __init__(self, title, draw_fn, on_close=None, scroll=False, close_keys=()):
        """scroll=True: draw_fn desenha numa folha alta e devolve até onde desenhou (y); setas/roda rolam."""
        self.title = title
        self.draw_fn = draw_fn
        self.on_close = on_close
        self.scroll = scroll
        self.close_keys = close_keys
        self.off = 0
        self.max_off = 0

    def handle(self, ev):
        if self.scroll:
            step = 0
            if ev.type == pygame.MOUSEWHEEL:
                step = -ev.y * 50
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_UP, pygame.K_w):
                step = -50
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_DOWN, pygame.K_s):
                step = 50
            if step:
                self.off = max(0, min(self.max_off, self.off + step))
                return
        if ev.type == pygame.KEYDOWN and (ev.key in CONFIRM or ev.key in CANCEL or ev.key in self.close_keys):
            self.done = True
            if self.on_close:
                self.on_close()

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 720, 520)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        panel(surf, rect)
        text(surf, self.title, (rect.x + 28, rect.y + 18), 28, C_LILAC, bold=True)
        if not self.scroll:
            self.draw_fn(surf, rect)
            text(surf, "Esc / E: fechar", (rect.right - 24, rect.bottom - 34), 16, C_MUTED, right=True)
            return
        # conteúdo numa folha alta; mostra só a janela entre o título e o rodapé
        sheet = pygame.Surface((rect.w, 2000), pygame.SRCALPHA)
        end = self.draw_fn(sheet, pygame.Rect(0, 0, rect.w, rect.h)) or rect.h
        view_h = rect.h - self.TOP - self.BOTTOM
        self.max_off = max(0, end + 10 - self.TOP - view_h)
        self.off = min(self.off, self.max_off)
        surf.blit(sheet, (rect.x, rect.y + self.TOP), (0, self.TOP + self.off, rect.w, view_h))
        if self.max_off:
            # linha entre o título e o conteúdo que rola (o texto some atrás dela, não "gruda" no título)
            surf.fill((70, 52, 100), (rect.x + 24, rect.y + self.TOP - U, rect.w - 48, U))
            # barrinha de rolagem
            bar = pygame.Rect(rect.right - 14, rect.y + self.TOP, 4, view_h)
            surf.fill((40, 30, 58), bar)
            kh = max(24, int(view_h * view_h / (view_h + self.max_off)))
            ky = bar.y + int((view_h - kh) * self.off / self.max_off)
            surf.fill(C_ACCENT_2, (bar.x, ky, 4, kh))
            surf.fill(C_LILAC, (bar.x, ky, 4, U))
            text(surf, "Setas / roda: rolar", (rect.x + 28, rect.bottom - 34), 16, C_MUTED)
        text(surf, "Esc / E: fechar", (rect.right - 24, rect.bottom - 34), 16, C_MUTED, right=True)


class TextPrompt(Modal):
    """Digitar um nome curto. Enter confirma, Tab troca pela próxima sugestão, Esc volta."""

    def __init__(self, title, on_confirm, initial="", suggestions=(), max_len=12, info="", on_cancel=None):
        self.title = title
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.value = initial
        self.suggestions = list(suggestions)
        self.max_len = max_len
        self.info = info
        self.t = 0.0
        self.k = 0
        try:
            pygame.key.start_text_input()
        except Exception:
            pass

    def update(self, dt):
        self.t += dt

    def handle(self, ev):
        if ev.type == pygame.TEXTINPUT:
            if self.t < 0.12:                  # a tecla que abriu a caixa não vira letra do nome
                return
            for ch in ev.text:
                if (ch.isalnum() or ch in " -'") and len(self.value) < self.max_len:
                    self.value += ch
            return
        if ev.type != pygame.KEYDOWN or self.t < 0.12:
            return
        if ev.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif ev.key == pygame.K_TAB and self.suggestions:
            self.value = self.suggestions[self.k % len(self.suggestions)]
            self.k += 1
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            name = " ".join(self.value.split())
            if name:
                self.done = True
                self.on_confirm(name[0].upper() + name[1:])
        elif ev.key == pygame.K_ESCAPE:
            self.done = True
            if self.on_cancel:
                self.on_cancel()

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 560, 230)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 30)
        panel(surf, rect)
        text(surf, self.title, (rect.centerx, rect.y + 18), 24, C_TEXT, bold=True, center=True)
        if self.info:
            text(surf, self.info, (rect.centerx, rect.y + 52), 16, C_MUTED, center=True)
        field = pygame.Rect(rect.x + 60, rect.y + 86, rect.w - 120, 52)
        box(surf, field, C_PANEL_2, border=C_ACCENT_2, cut=2)
        img = font(30, True).render(self.value, False, C_GOLD)
        surf.blit(img, (field.centerx - img.get_width() // 2, field.y + 10))
        if int(self.t * 2) % 2 == 0:              # cursor piscando
            cx = field.centerx + img.get_width() // 2 + 3
            pygame.draw.rect(surf, C_GOLD, (cx, field.y + 12, 3, 28))
        hint = "Digite o nome   Enter: confirmar   Esc: voltar"
        if self.suggestions:
            hint = "Digite o nome   Tab: sugestão   Enter: confirmar   Esc: voltar"
        text(surf, hint, (rect.centerx, rect.bottom - 40), 15, C_MUTED, center=True)


class NumberPrompt(Modal):
    """Escolher uma quantidade: digite o número ou use as setas."""

    def __init__(self, title, unit_price, max_n, on_confirm, verb="Confirmar", info="", color=C_GOLD):
        self.title = title
        self.price = unit_price
        self.max_n = max(0, int(max_n))
        self.on_confirm = on_confirm
        self.verb = verb
        self.info = info
        self.color = color
        self.n = 1 if self.max_n >= 1 else 0
        self.typed = False

    def _set(self, v):
        self.n = max(0, min(self.max_n, int(v)))

    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL:
            self._set(self.n + ev.y)
            return
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        digit = None
        if pygame.K_0 <= k <= pygame.K_9:
            digit = k - pygame.K_0
        elif pygame.K_KP0 <= k <= pygame.K_KP9:
            digit = k - pygame.K_KP0
        if digit is not None:
            base = self.n if self.typed else 0
            self.typed = True
            self._set(min(base * 10 + digit, 10 ** 9))
        elif k == pygame.K_BACKSPACE:
            self.typed = True
            self._set(self.n // 10)
        elif k in (pygame.K_RIGHT, pygame.K_d):
            self._set(self.n + 1)
        elif k in (pygame.K_LEFT, pygame.K_a):
            self._set(self.n - 1)
        elif k in (pygame.K_UP, pygame.K_w):
            self._set(self.n + 10)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self._set(self.n - 10)
        elif k == pygame.K_PAGEUP:
            self._set(self.n + 100)
        elif k == pygame.K_PAGEDOWN:
            self._set(self.n - 100)
        elif k == pygame.K_m:
            self._set(self.max_n)
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
            if self.n > 0:
                self.done = True
                self.on_confirm(self.n)
        elif k in (pygame.K_ESCAPE, pygame.K_q):
            self.done = True

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 560, 300)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 30)
        panel(surf, rect)
        text(surf, self.title, (rect.centerx, rect.y + 20), 24, C_LILAC, bold=True, center=True)
        if self.info:
            text(surf, self.info, (rect.centerx, rect.y + 54), 17, C_MUTED, center=True)
        field = pygame.Rect(0, 0, 220, 64)
        field.center = (rect.centerx, rect.y + 120)
        box(surf, field, C_PANEL_2, border=C_ACCENT_2, cut=2)
        text(surf, f"{self.n:,}".replace(",", "."), (field.centerx, field.y + 10), 40, C_TEXT, bold=True, center=True)
        for dx, sym in ((-150, "<"), (150, ">")):
            text(surf, sym, (field.centerx + dx, field.y + 14), 32, C_MUTED, bold=True, center=True)
        total = int(round(self.price * self.n))
        text(surf, f"Total: $ {total:,}".replace(",", "."), (rect.centerx, rect.y + 168), 22, self.color, bold=True,
             center=True)
        text(surf, f"Máximo possível: {self.max_n:,}".replace(",", "."), (rect.centerx, rect.y + 198), 16, C_MUTED,
             center=True)
        text(surf, f"Digite o número · setas: 1 ou 10 · M: máximo · Enter: {self.verb} · Esc: voltar",
             (rect.centerx, rect.bottom - 40), 15, C_MUTED, center=True)


class Toasts:
    def __init__(self):
        self.items = []

    def push(self, msg, color=C_TEXT, icon=None):
        self.items.append([msg, color, icon, 3.2])
        self.items = self.items[-5:]

    def update(self, dt):
        for t in self.items:
            t[3] -= dt
        self.items = [t for t in self.items if t[3] > 0]

    def draw(self, surf):
        y = 16
        for msg, color, icon, life in self.items:
            alpha = min(1.0, life / 0.5)
            w = font(18).size(msg)[0] + (56 if icon else 32)
            s = panel_image((w, 40), 228, C_BORDER_DIM, 8).copy()
            if alpha < 1:
                s.set_alpha(int(255 * alpha))
            x = 16
            if icon:
                s.blit(art.item_icon(icon, 2), (10, 4))
                x = 48
            img = font(18).render(msg, not PIXEL_FONT, color)
            img.set_alpha(int(255 * alpha))
            s.blit(img, (x, 9))
            surf.blit(s, (16, y))
            y += 46


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

_WEATHER_CACHE = {}


def _cloud_art(night):
    """Nuvem fofinha em pixel art (24x14 px de arte): contorno, sombra embaixo e brilho em cima."""
    key = ("cloud", night)
    if key in _WEATHER_CACHE:
        return _WEATHER_CACHE[key]
    w, h = 26, 16
    puffs = [(7, 9, 5), (13, 6, 6), (19, 9, 5)]
    inside = lambda x, y, grow=0: (any((x - cx) ** 2 + (y - cy) ** 2 <= (r + grow) ** 2 for cx, cy, r in puffs)
                                   or (3 - grow <= x <= 22 + grow and 9 <= y <= 13 + grow))
    if night:
        line, base, shadow, light = (40, 46, 74), (150, 158, 190), (112, 120, 156), (190, 198, 224)
    else:
        line, base, shadow, light = (70, 82, 120), (236, 240, 250), (186, 196, 222), (255, 255, 255)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            if inside(x, y):
                c = base
                if not inside(x, y - 2) and y < 10:      # brilho na borda de cima de cada bolota
                    c = light
                if y >= 12:                              # sombra embaixo
                    c = shadow
                s.set_at((x, y), c)
            elif inside(x, y, 1):
                s.set_at((x, y), line)
    _WEATHER_CACHE[key] = s
    return s


def draw_weather_icon(surf, center, kind, night, ticks):
    """Ícone do clima no HUD: sol (raios girando devagar), lua, nuvem com chuva ou com neve (animadas)."""
    cx, cy = center
    S = 2
    if kind == "sun":
        rot = (ticks / 80.0) % 360
        for a in range(8):
            v = pygame.math.Vector2(1, 0).rotate(a * 45 + rot)
            pygame.draw.line(surf, (255, 196, 70), (cx + v.x * 14, cy + v.y * 14), (cx + v.x * 19, cy + v.y * 19), 3)
        pygame.draw.circle(surf, (226, 150, 40), (cx, cy), 12)
        pygame.draw.circle(surf, (255, 210, 90), (cx, cy), 10)
        pygame.draw.circle(surf, (255, 240, 170), (cx - 3, cy - 3), 4)
        return
    if kind == "moon":
        pygame.draw.circle(surf, (250, 244, 214), (cx, cy), 12)
        pygame.draw.circle(surf, (34, 24, 50), (cx + 6, cy - 4), 10)
        for (dx, dy) in ((-16, -10), (12, 12), (16, -14)):
            pygame.draw.rect(surf, (250, 244, 214), (cx + dx, cy + dy, 2, 2))
        return
    if kind == "rainbow":                        # arco-íris com o sol espiando
        cols = [(240, 84, 84), (250, 154, 64), (250, 222, 92), (110, 210, 110), (90, 168, 250), (176, 108, 226)]
        for i, c in enumerate(cols):
            pygame.draw.circle(surf, c, (cx, cy + 10), 21 - i * 3, 3, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(surf, (226, 150, 40), (cx + 12, cy + 6), 7)
        pygame.draw.circle(surf, (255, 214, 96), (cx + 12, cy + 6), 5)
        return
    cloud = pygame.transform.scale_by(_cloud_art(night), S)
    top = cy - 20
    if night:                                    # lua espiando atrás da nuvem
        pygame.draw.circle(surf, (250, 244, 214), (cx + 18, top + 5), 9)
        pygame.draw.circle(surf, (34, 24, 50), (cx + 23, top + 1), 8)
    # pingos (ou flocos) caindo em loop por baixo da nuvem
    t = ticks / 1000.0
    for i, dx in enumerate((-12, -2, 8, 16)):
        ph = (t * (0.7 if kind == "snow" else 1.6) + i * 0.37) % 1.0
        y = top + 26 + ph * 11
        x = cx + dx - (0 if kind == "snow" else ph * 4)
        if kind in ("rain", "storm"):
            col = (110, 170, 255)
            pygame.draw.line(surf, col, (x, y), (x - 2, y + 6), 2)
        else:
            sway = math.sin(t * 3 + i) * 2
            col = (240, 246, 255)
            px, py = int(x + sway), int(y)
            pygame.draw.rect(surf, col, (px - 1, py - 3, 2, 6))
            pygame.draw.rect(surf, col, (px - 3, py - 1, 6, 2))
    surf.blit(cloud, (cx - cloud.get_width() // 2, top))
    if kind == "storm" and (ticks // 140) % 9 in (0, 2):     # raio piscando por baixo da nuvem
        bolt = [(cx + 2, top + 18), (cx - 5, top + 30), (cx, top + 30), (cx - 4, top + 41), (cx + 7, top + 26),
                (cx + 2, top + 26), (cx + 6, top + 18)]
        pygame.draw.polygon(surf, (255, 226, 90), bolt)
        pygame.draw.polygon(surf, (190, 130, 30), bolt, 1)


def draw_hud(surf, g):
    # Relógio / data
    r = pygame.Rect(SCREEN_W - 236, 12, 224, 118)
    panel(surf, r, alpha=240)
    text(surf, g.date_label(short=True), (r.x + 16, r.y + 10), 18, C_LILAC, bold=True)
    text(surf, g.time_label(), (r.x + 16, r.y + 34), 34, C_TEXT, bold=True)
    wx, wy = r.right - 44, r.y + 56            # abaixo da data, para não cobrir o nome da estação
    night = g.minutes >= 19 * 60 or g.minutes < 6 * 60
    if g.weather == "chuva":
        from . import seasons
        snow = seasons.CURRENT["season"] == "winter"
        kind = "snow" if snow else ("storm" if getattr(g, "storm", False) else "rain")
        draw_weather_icon(surf, (wx, wy), kind, night, pygame.time.get_ticks())
    elif getattr(g, "rainbow", False) and 6 * 60 <= g.minutes < 11 * 60:
        draw_weather_icon(surf, (wx, wy), "rainbow", False, pygame.time.get_ticks())
    elif night:
        draw_weather_icon(surf, (wx, wy), "moon", True, 0)
    else:
        draw_weather_icon(surf, (wx, wy), "sun", False, pygame.time.get_ticks())
    up = g.stock >= g.stock_prev
    text(surf, f"LCORP {g.stock:.2f}".replace(".", ","), (r.x + 16, r.y + 82), 18, C_MUTED, bold=True)
    col = C_GREEN if up else C_RED
    ax, ay = r.right - 30, r.y + 92
    if up:
        pygame.draw.polygon(surf, col, [(ax - 7, ay + 4), (ax + 7, ay + 4), (ax, ay - 5)])
    else:
        pygame.draw.polygon(surf, col, [(ax - 7, ay - 4), (ax + 7, ay - 4), (ax, ay + 5)])
    # Dinheiro
    m = pygame.Rect(SCREEN_W - 236, 136, 224, 44)
    panel(surf, m, alpha=240, border=(200, 160, 80), radius=8)
    text(surf, "$", (m.x + 16, m.y + 9), 22, C_GOLD, bold=True)
    text(surf, f"{g.money:,}".replace(",", "."), (m.right - 16, m.y + 9), 22, C_GOLD, bold=True, right=True)
    # Energia (escondida enquanto uma fala está aberta, para não ficar atrás do retrato)
    if any(isinstance(m, Dialog) for m in g.modals):
        text(surf, g.current_map.label, (SCREEN_W - 24, 186), 15, C_MUTED, right=True)
        return
    # barra simples, como era antes (a dona preferiu sem brilho nem risquinhos)
    e = pygame.Rect(SCREEN_W - 46, SCREEN_H - 214, 32, 180)
    panel(surf, e, alpha=225, radius=10)
    inner = pygame.Rect(e.x + 7, e.y + 26, e.w - 14, e.h - 34)
    pygame.draw.rect(surf, (20, 16, 26), inner, border_radius=4)
    frac = max(0.0, g.energy / g.max_energy)
    fh = int(inner.h * frac)
    color = C_ENERGY if frac > 0.35 else ((250, 200, 80) if frac > 0.15 else C_RED)
    pygame.draw.rect(surf, color, (inner.x, inner.bottom - fh, inner.w, fh), border_radius=4)
    text(surf, "E", (e.centerx, e.y + 4), 18, C_TEXT, bold=True, center=True)
    # Local
    text(surf, g.current_map.label, (SCREEN_W - 24, 186), 15, C_MUTED, right=True)


def draw_hotbar(surf, g):
    n = HOTBAR_SIZE
    slot_w = 56
    gap = 4
    w = n * (slot_w + gap) - gap + 16
    x0 = (SCREEN_W - w) // 2
    y0 = SCREEN_H - slot_w - 22
    panel(surf, (x0, y0, w, slot_w + 14), alpha=220, radius=8)
    for i, s in enumerate(g.inventory[:HOTBAR_SIZE]):
        r = pygame.Rect(x0 + 8 + i * (slot_w + gap), y0 + 7, slot_w, slot_w)
        slot(surf, r, i == g.selected)
        if s:
            icon = art.item_icon(s[0], 3)
            surf.blit(icon, (r.centerx - icon.get_width() // 2, r.centery - icon.get_height() // 2))
            if s[1] > 1:
                text(surf, str(s[1]), (r.right - 5, r.bottom - 22), 16, C_TEXT, bold=True, right=True)
        label = "0" if i == 9 else ("-" if i == 10 else ("=" if i == 11 else str(i + 1)))
        text(surf, label, (r.x + 5, r.y + 2), 12, C_MUTED, shadow=False)
    if g.hotbar_label_t > 0 and g.selected < len(g.inventory):
        s = g.inventory[g.selected]
        if s:
            msg = ITEMS[s[0]]["name"]
            fw = font(18, True).size(msg)[0] + 28
            lr = pygame.Rect(SCREEN_W // 2 - fw // 2, y0 - 42, fw, 34)
            panel(surf, lr, alpha=230, radius=10)
            text(surf, msg, (lr.centerx, lr.y + 6), 18, C_TEXT, bold=True, center=True)


class ScrollPanel(Modal):
    """Lista rolável: rows_fn() -> lista; draw_row(surf, rect, row, selected)."""

    def __init__(self, title, rows_fn, draw_row, row_h=96, subtitle="", close_keys=()):
        self.close_keys = close_keys
        self.title = title
        self.subtitle = subtitle
        self.rows_fn = rows_fn
        self.draw_row = draw_row
        self.row_h = row_h
        self.sel = 0
        self.off = 0.0                  # rolagem suave (em pixels)

    def handle(self, ev):
        n = max(1, len(self.rows_fn()))
        if ev.type == pygame.MOUSEWHEEL:
            self.sel = max(0, min(n - 1, self.sel - ev.y))
            return
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % n
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % n
        elif ev.key in CONFIRM or ev.key in CANCEL or ev.key in self.close_keys:
            self.done = True

    def draw(self, surf):
        rows = self.rows_fn()
        rect = pygame.Rect(0, 0, 820, 600)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        panel(surf, rect)
        text(surf, self.title, (rect.x + 28, rect.y + 16), 28, C_LILAC, bold=True)
        if self.subtitle:
            text(surf, self.subtitle, (rect.x + 30, rect.y + 54), 16, C_MUTED)
        top = rect.y + 84
        view = pygame.Rect(rect.x + 8, top, rect.w - 16, rect.h - 130)
        total = len(rows) * self.row_h
        max_off = max(0, total - view.h)
        # a linha escolhida fica sempre à vista; a lista desliza até ela
        want = min(max(self.off, (self.sel + 1) * self.row_h - view.h), self.sel * self.row_h)
        want = max(0, min(max_off, want))
        self.off += (want - self.off) * 0.35
        if abs(want - self.off) < 1:
            self.off = want
        surf.set_clip(view)
        first = int(self.off // self.row_h)
        for i in range(first, min(len(rows), first + view.h // self.row_h + 2)):
            r = pygame.Rect(rect.x + 20, top + i * self.row_h - int(self.off), rect.w - 48, self.row_h - 6)
            if i == self.sel:
                box(surf, r, C_PANEL_2, border=C_ACCENT_2, cut=2)
            self.draw_row(surf, r, rows[i], i == self.sel)
        surf.set_clip(None)
        if max_off:
            bar = pygame.Rect(rect.right - 18, top, 4, view.h)
            surf.fill((40, 30, 58), bar)
            kh = max(24, int(view.h * view.h / total))
            ky = bar.y + int((view.h - kh) * self.off / max_off)
            surf.fill(C_ACCENT_2, (bar.x, ky, 4, kh))
            surf.fill(C_LILAC, (bar.x, ky, 4, U))
            text(surf, f"{self.sel + 1}/{len(rows)}", (rect.x + 30, rect.bottom - 34), 15, C_MUTED)
        text(surf, "Setas / roda: rolar   Esc / E: fechar", (rect.right - 24, rect.bottom - 34), 16, C_MUTED,
             right=True)

"""Interface: fontes, painéis, diálogos, menus, loja, HUD e barra de itens."""
import os

import pygame

from . import art
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


def panel(surf, rect, alpha=235, border=C_BORDER, radius=14, fill=C_PANEL):
    """Painel fofo: sombra, gradiente suave, borda dupla."""
    rect = pygame.Rect(rect)
    border = border or C_BORDER
    key = (rect.size, alpha, tuple(border), radius, tuple(fill))
    img = _panel_cache.get(key)
    if img is None:
        w, h = rect.size
        img = pygame.Surface((w + 6, h + 6), pygame.SRCALPHA)
        pygame.draw.rect(img, (0, 0, 0, 70), (4, 5, w, h), border_radius=radius)
        body = pygame.Surface((w, h), pygame.SRCALPHA)
        top = tuple(min(255, int(c * 1.35) + 6) for c in fill)
        for y in range(h):
            t = y / max(1, h - 1)
            c = tuple(int(top[i] + (fill[i] - top[i]) * min(1, t * 2.2)) for i in range(3))
            pygame.draw.line(body, (*c, alpha), (0, y), (w, y))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        img.blit(body, (0, 0))
        pygame.draw.rect(img, (28, 16, 40, 255), (0, 0, w, h), 3, border_radius=radius)
        pygame.draw.rect(img, (*border, 255), (3, 3, w - 6, h - 6), 2, border_radius=max(2, radius - 3))
        pygame.draw.line(img, (255, 255, 255, 45), (radius, 6), (w - radius, 6))
        if len(_panel_cache) > 300:
            _panel_cache.clear()
        _panel_cache[key] = img
    surf.blit(img, rect.topleft)


def name_tag(surf, x, y, name, color=None):
    f = font(20, True)
    w = f.size(name)[0] + 28
    r = pygame.Rect(x, y, w, 32)
    pygame.draw.rect(surf, (28, 16, 40), r.inflate(6, 6), border_radius=16)
    pygame.draw.rect(surf, color or C_ACCENT, r, border_radius=14)
    pygame.draw.rect(surf, (255, 255, 255), (r.x + 10, r.y + 4, w - 20, 2), border_radius=1)
    text(surf, name, (r.centerx, r.y + 4), 20, C_TEXT, bold=True, center=True)
    return r


def hearts_row(surf, x, y, points, k=2):
    n = points // HEART_POINTS
    for i in range(MAX_HEARTS):
        img = art.heart(i < n, k)
        surf.blit(img, (x + i * (img.get_width() + 3), y))


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
        self.shown = min(len(self.current), self.shown + dt * 55)

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
                pygame.draw.rect(surf, C_ACCENT, (px - 4, py - 4, size + 8, size + 8), border_radius=8)
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
    def __init__(self, question, options, on_pick, on_cancel=None):
        self.question = question
        self.options = options
        self.on_pick = on_pick
        self.on_cancel = on_cancel
        self.sel = 0

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(self.options)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(self.options)
        elif ev.key in CONFIRM:
            self.done = True
            self.on_pick(self.sel)
        elif ev.key in CANCEL:
            self.done = True
            if self.on_cancel:
                self.on_cancel()

    def draw(self, surf):
        lines = wrap(self.question, 22, 520)
        h = 40 + len(lines) * 30 + len(self.options) * 40 + 20
        rect = pygame.Rect(0, 0, 600, h)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 40)
        panel(surf, rect)
        y = rect.y + 22
        for l in lines:
            text(surf, l, (rect.centerx, y), 22, bold=True, center=True)
            y += 30
        y += 10
        for i, opt in enumerate(self.options):
            r = pygame.Rect(rect.x + 40, y, rect.w - 80, 34)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            text(surf, opt, (r.centerx, r.y + 6), 20, center=True, color=C_TEXT if i == self.sel else C_MUTED)
            y += 40


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
                pygame.draw.rect(surf, C_PANEL_2, r, border_radius=8)
                pygame.draw.rect(surf, C_ACCENT_2, r, 2, border_radius=8)
            if e.get("item"):
                surf.blit(art.item_icon(e["item"], 2), (r.x + 8, r.y + 7))
            col = C_TEXT if enabled else C_MUTED
            text(surf, e["label"], (r.x + 54, r.y + 11), 19, col, bold=i == self.sel)
            text(surf, f"$ {e['price']}", (r.right - 14, r.y + 11), 19, C_GOLD if enabled else C_MUTED,
                 right=True)
            y += 50
        e = entries[self.sel]
        dr = pygame.Rect(rect.x + 20, rect.bottom - 68, rect.w - 40, 50)
        pygame.draw.rect(surf, (14, 10, 22), dr, border_radius=8)
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
            # barrinha de rolagem
            bar = pygame.Rect(rect.right - 14, rect.y + self.TOP, 4, view_h)
            pygame.draw.rect(surf, (60, 50, 80), bar, border_radius=2)
            kh = max(24, int(view_h * view_h / (view_h + self.max_off)))
            ky = bar.y + int((view_h - kh) * self.off / self.max_off)
            pygame.draw.rect(surf, C_ACCENT_2, (bar.x, ky, 4, kh), border_radius=2)
            text(surf, "Setas / roda: rolar", (rect.x + 28, rect.bottom - 34), 16, C_MUTED)
        text(surf, "Esc / E: fechar", (rect.right - 24, rect.bottom - 34), 16, C_MUTED, right=True)


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
        box = pygame.Rect(0, 0, 220, 64)
        box.center = (rect.centerx, rect.y + 120)
        pygame.draw.rect(surf, C_PANEL_2, box, border_radius=10)
        pygame.draw.rect(surf, C_ACCENT_2, box, 2, border_radius=10)
        text(surf, f"{self.n:,}".replace(",", "."), (box.centerx, box.y + 10), 40, C_TEXT, bold=True, center=True)
        for dx, sym in ((-150, "<"), (150, ">")):
            text(surf, sym, (box.centerx + dx, box.y + 14), 32, C_MUTED, bold=True, center=True)
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
            w = font(18).size(msg)[0] + (52 if icon else 28)
            s = pygame.Surface((w, 38), pygame.SRCALPHA)
            pygame.draw.rect(s, (*C_PANEL, int(225 * alpha)), s.get_rect(), border_radius=10)
            pygame.draw.rect(s, (*C_BORDER_DIM, int(255 * alpha)), s.get_rect(), 2, border_radius=10)
            x = 14
            if icon:
                s.blit(art.item_icon(icon, 2), (8, 3))
                x = 44
            img = font(18).render(msg, not PIXEL_FONT, color)
            img.set_alpha(int(255 * alpha))
            s.blit(img, (x, 8))
            surf.blit(s, (16, y))
            y += 44


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

def draw_hud(surf, g):
    # Relógio / data
    r = pygame.Rect(SCREEN_W - 236, 12, 224, 118)
    panel(surf, r, alpha=225)
    text(surf, g.date_label(), (r.x + 16, r.y + 10), 18, C_LILAC, bold=True)
    text(surf, g.time_label(), (r.x + 16, r.y + 34), 34, C_TEXT, bold=True)
    wx, wy = r.right - 44, r.y + 44
    if g.minutes >= 19 * 60 or g.minutes < 6 * 60:
        pygame.draw.circle(surf, (240, 236, 210), (wx, wy), 11)
        pygame.draw.circle(surf, (34, 24, 50), (wx + 6, wy - 4), 10)
        if g.weather == "chuva":
            for i in range(3):
                pygame.draw.line(surf, (120, 170, 255), (wx - 6 + i * 9, wy + 14), (wx - 9 + i * 9, wy + 22), 2)
    elif g.weather == "chuva":
        pygame.draw.ellipse(surf, (170, 176, 196), (wx - 14, wy - 8, 34, 18))
        for i in range(3):
            pygame.draw.line(surf, (120, 170, 255), (wx - 6 + i * 9, wy + 12), (wx - 9 + i * 9, wy + 20), 2)
    else:
        pygame.draw.circle(surf, (255, 210, 90), (wx, wy), 11)
        for a in range(8):
            v = pygame.math.Vector2(1, 0).rotate(a * 45)
            pygame.draw.line(surf, (255, 210, 90), (wx + v.x * 14, wy + v.y * 14), (wx + v.x * 18, wy + v.y * 18), 2)
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
    panel(surf, m, alpha=225, border=(200, 160, 80))
    text(surf, "$", (m.x + 16, m.y + 9), 22, C_GOLD, bold=True)
    text(surf, f"{g.money:,}".replace(",", "."), (m.right - 16, m.y + 9), 22, C_GOLD, bold=True, right=True)
    # Energia (escondida enquanto uma fala está aberta, para não ficar atrás do retrato)
    if any(isinstance(m, Dialog) for m in g.modals):
        text(surf, g.current_map.label, (SCREEN_W - 24, 186), 15, C_MUTED, right=True)
        return
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
    slot = 56
    gap = 4
    w = n * (slot + gap) - gap + 16
    x0 = (SCREEN_W - w) // 2
    y0 = SCREEN_H - slot - 22
    panel(surf, (x0, y0, w, slot + 14), alpha=220, radius=12)
    for i, s in enumerate(g.inventory[:HOTBAR_SIZE]):
        r = pygame.Rect(x0 + 8 + i * (slot + gap), y0 + 7, slot, slot)
        pygame.draw.rect(surf, (16, 12, 24), r, border_radius=8)
        if i == g.selected:
            pygame.draw.rect(surf, C_ACCENT_2, r, 3, border_radius=8)
        else:
            pygame.draw.rect(surf, C_BORDER_DIM, r, 1, border_radius=8)
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
                pygame.draw.rect(surf, C_PANEL_2, r, border_radius=10)
                pygame.draw.rect(surf, C_ACCENT_2, r, 2, border_radius=10)
            self.draw_row(surf, r, rows[i], i == self.sel)
        surf.set_clip(None)
        if max_off:
            bar = pygame.Rect(rect.right - 18, top, 4, view.h)
            pygame.draw.rect(surf, (60, 50, 80), bar, border_radius=2)
            kh = max(24, int(view.h * view.h / total))
            ky = bar.y + int((view.h - kh) * self.off / max_off)
            pygame.draw.rect(surf, C_ACCENT_2, (bar.x, ky, 4, kh), border_radius=2)
            text(surf, f"{self.sel + 1}/{len(rows)}", (rect.x + 30, rect.bottom - 34), 15, C_MUTED)
        text(surf, "Setas / roda: rolar   Esc / E: fechar", (rect.right - 24, rect.bottom - 34), 16, C_MUTED,
             right=True)

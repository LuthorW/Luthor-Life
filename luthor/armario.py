"""Armário da cozinha da cobertura: um baú para guardar coisas (como os baús do Stardew).

- objeto "armario_cozinha" (1x1, alto) ao lado da geladeira, em `SPOT` (world.build_home);
- E abre a tela com a mochila em cima e o armário embaixo (`ARMARIO_SIZE` espaços, pilhas sem limite);
- E/Enter passa a pilha inteira para o outro lado, F passa 1, G guarda tudo da mochila (menos ferramentas),
  Tab pula entre a mochila e o armário, Esc fecha;
- estado em `g.armario["slots"]` (lista de [item, quantidade] ou None), salvo no jogo.
"""
import pygame

from . import art, audio, ui
from .art import new, R, P
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_LILAC, C_GOLD
from .data import ITEMS

SPOT = (24, 4)                      # na cozinha da cobertura, embaixo da geladeira (24,2), com (24,3) livre
ARMARIO_SIZE = 36                   # 3 fileiras de 12
COLS = 12
KIND = "armario_cozinha"


# ---------------------------------------------------------------------------
# Desenho do armário (16x32 px de arte): alto, creme, com a parte de cima de vidro e potes
# ---------------------------------------------------------------------------
def _armario():
    s = new(16, 32)
    line, body, light, dark = (120, 96, 84), (238, 228, 210), (250, 244, 232), (204, 190, 168)
    gold = (214, 172, 84)
    R(s, line, 0, 1, 16, 31)                        # contorno
    R(s, body, 1, 2, 14, 29)
    R(s, line, 0, 0, 16, 2)                         # cornija
    R(s, light, 1, 1, 14, 1)
    # portas de vidro em cima, com prateleira e potinhos
    for x0 in (2, 8):
        R(s, dark, x0, 4, 6, 11)
        R(s, (196, 220, 228), x0 + 1, 5, 4, 9)
        R(s, dark, x0 + 1, 9, 4, 1)                 # prateleira
    for (x, y, c) in ((3, 7, (220, 120, 90)), (5, 7, (240, 210, 120)), (9, 6, (150, 190, 110)),
                      (11, 7, (200, 150, 210)), (3, 12, (190, 150, 110)), (10, 12, (240, 240, 240)),
                      (12, 11, (230, 170, 90))):
        R(s, c, x, y, 1 if x in (5, 12) else 2, 14 - y if y > 9 else 9 - y)
    for x0 in (3, 9):                               # reflexo no vidro
        P(s, (236, 246, 250), x0, 5)
        P(s, (236, 246, 250), x0, 6)
    # gavetão do meio
    R(s, dark, 2, 16, 12, 3)
    R(s, light, 2, 16, 12, 1)
    R(s, gold, 6, 17, 4, 1)
    # portas de baixo
    for x0 in (2, 8):
        R(s, dark, x0, 20, 6, 10)
        R(s, body, x0 + 1, 21, 4, 8)
        R(s, light, x0 + 1, 21, 4, 1)
    R(s, gold, 6, 24, 1, 3); R(s, gold, 9, 24, 1, 3)  # puxadores
    R(s, gold, 6, 11, 1, 2); R(s, gold, 9, 11, 1, 2)
    R(s, line, 1, 30, 14, 1)                        # rodapé
    R(s, (90, 72, 64), 2, 31, 12, 1)
    return s


art.OBJECT_BUILDERS[KIND] = _armario


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def init_state(g):
    g.armario = dict(slots=[None] * ARMARIO_SIZE)


def save_state(g):
    return {"armario": [list(s) if s else None for s in g.armario["slots"]]}


def load_state(g, d):
    slots = []
    for s in (d.get("armario") or [])[:ARMARIO_SIZE]:
        ok = isinstance(s, (list, tuple)) and len(s) == 2 and s[0] in ITEMS and int(s[1]) > 0
        slots.append([s[0], int(s[1])] if ok else None)
    g.armario = dict(slots=slots + [None] * (ARMARIO_SIZE - len(slots)))


def count(g):
    return sum(s[1] for s in g.armario["slots"] if s)


# ---------------------------------------------------------------------------
# Ganchos do Game
# ---------------------------------------------------------------------------
def object_label(g, o):
    if o.kind == KIND:
        return "Abrir o armário"
    return None


def use_object(g, o):
    if o.kind != KIND:
        return False
    audio.sfx("open")
    g.push(Armario(g))
    return True


def _put(slots, item, n):
    """Põe n de item em slots (junta com a pilha igual ou usa um espaço vazio). Devolve se coube."""
    for s in slots:
        if s and s[0] == item:
            s[1] += n
            return True
    for i, s in enumerate(slots):
        if s is None:
            slots[i] = [item, n]
            return True
    return False


class Armario(ui.Modal):
    SLOT, GAP = 52, 6

    def __init__(self, g):
        self.g = g
        self.side = 0                       # 0 = mochila, 1 = armário
        self.cur = [0, 0]
        self.msg, self.msg_t = "", 0.0

    def lists(self):
        return (self.g.inventory, self.g.armario["slots"])

    def flash(self, text):
        self.msg, self.msg_t = text, 2.2

    def move(self, one=False):
        src, dst = self.lists()[self.side], self.lists()[1 - self.side]
        i = self.cur[self.side]
        s = src[i]
        if not s:
            audio.sfx("cancel")
            return
        n = 1 if one else s[1]
        if not _put(dst, s[0], n):
            audio.sfx("cancel")
            self.flash("O armário está cheio." if self.side == 0 else "A mochila está cheia.")
            return
        s[1] -= n
        if s[1] <= 0:
            src[i] = None
        audio.sfx("pickup" if self.side == 1 else "confirm")

    def store_all(self):
        inv, box = self.lists()
        moved = 0
        for i, s in enumerate(inv):
            if s and ITEMS[s[0]]["kind"] != "tool" and _put(box, s[0], s[1]):
                moved += s[1]
                inv[i] = None
        if moved:
            audio.sfx("confirm")
            self.flash(f"{moved} {'item guardado' if moved == 1 else 'itens guardados'}.")
        else:
            audio.sfx("cancel")
            self.flash("Nada para guardar (as ferramentas ficam na mochila).")

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        n = len(self.lists()[self.side])
        c = self.cur[self.side]
        if k in (pygame.K_LEFT, pygame.K_a):
            self.cur[self.side] = (c - 1) % n
        elif k in (pygame.K_RIGHT, pygame.K_d):
            self.cur[self.side] = (c + 1) % n
        elif k in (pygame.K_DOWN, pygame.K_s):
            if c + COLS < n:
                self.cur[self.side] = c + COLS
            elif self.side == 0:                                 # desce da mochila para o armário
                self.side, self.cur[1] = 1, c % COLS
        elif k in (pygame.K_UP, pygame.K_w):
            if c - COLS >= 0:
                self.cur[self.side] = c - COLS
            elif self.side == 1:                                 # sobe do armário para a mochila
                inv = len(self.g.inventory)
                self.side, self.cur[0] = 0, (inv - COLS) + c % COLS
        elif k == pygame.K_TAB:
            self.side = 1 - self.side
        elif k in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
            self.move()
        elif k == pygame.K_f:
            self.move(one=True)
        elif k == pygame.K_g:
            self.store_all()
        elif k in (pygame.K_ESCAPE, pygame.K_i, pygame.K_q):
            audio.sfx("close")
            self.done = True

    def update(self, dt):
        self.msg_t = max(0.0, self.msg_t - dt)

    def _grid(self, surf, x, y, slots, side):
        sl, gap = self.SLOT, self.GAP
        for i, s in enumerate(slots):
            row, col = divmod(i, COLS)
            r = pygame.Rect(x + col * (sl + gap), y + row * (sl + gap), sl, sl)
            ui.slot(surf, r, side == self.side and i == self.cur[side])
            if s:
                surf.blit(art.item_icon(s[0], 3), (r.centerx - 24, r.centery - 24))
                if s[1] > 1:
                    ui.text(surf, str(s[1]), (r.right - 4, r.bottom - 20), 15, C_TEXT, bold=True, right=True)
        rows = (len(slots) + COLS - 1) // COLS
        return y + rows * (sl + gap)

    def draw(self, surf):
        sl, gap = self.SLOT, self.GAP
        w = COLS * (sl + gap) - gap + 48
        rows = (len(self.g.inventory) + COLS - 1) // COLS + (ARMARIO_SIZE + COLS - 1) // COLS
        h = 52 + rows * (sl + gap) + 46 + 70 + 44
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 10)
        ui.panel(surf, rect)
        x = rect.x + 24
        ui.text(surf, "Mochila", (x, rect.y + 16), 24, C_LILAC if self.side == 0 else C_MUTED, bold=True)
        y = self._grid(surf, x, rect.y + 52, self.g.inventory, 0)
        used = sum(1 for s in self.g.armario["slots"] if s)
        ui.text(surf, "Armário da cozinha", (x, y + 10), 24, C_LILAC if self.side == 1 else C_MUTED, bold=True)
        ui.text(surf, f"{used}/{ARMARIO_SIZE} espaços", (rect.right - 24, y + 14), 17, C_MUTED, right=True)
        y = self._grid(surf, x, y + 46, self.g.armario["slots"], 1)
        s = self.lists()[self.side][self.cur[self.side]]
        if self.msg_t > 0:
            ui.text(surf, self.msg, (x, y + 10), 19, C_GOLD, bold=True)
        elif s:
            it = ITEMS[s[0]]
            ui.text(surf, f"{it['name']}  x{s[1]}", (x, y + 8), 19, C_TEXT, bold=True)
            ui.text(surf, it.get("desc", ""), (x, y + 34), 16, C_MUTED)
        dest = "guardar" if self.side == 0 else "pegar"
        ui.text(surf, f"E: {dest} a pilha   F: {dest} 1   G: guardar tudo   Tab: trocar de lado   Esc: fechar",
                (rect.centerx, rect.bottom - 32), 16, C_MUTED, center=True)

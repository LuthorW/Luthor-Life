"""Minigames e telas especiais: pesca, fliperama Meteoro, fogão (cozinhar) e mochila."""
import math
import random

import pygame

from . import art, ui
from .config import (SCREEN_W, SCREEN_H, C_PANEL_2, C_ACCENT, C_ACCENT_2, C_TEXT, C_MUTED, C_LILAC, C_GOLD,
                     C_GREEN, C_RED, C_BORDER_DIM, HOTBAR_SIZE)
from .data import ITEMS, FISH, RECIPES, BOOKS

HOLD_KEYS = (pygame.K_SPACE, pygame.K_e, pygame.K_RETURN, pygame.K_w, pygame.K_UP)


# ---------------------------------------------------------------------------
# Pesca
# ---------------------------------------------------------------------------

class Fishing(ui.Modal):
    TRACK_H = 400

    def __init__(self, fish_id, bar_size, on_done):
        self.fish = fish_id
        self.diff = FISH[fish_id]["diff"] if fish_id in FISH else 8
        self.legendary = FISH.get(fish_id, {}).get("legendary", False)
        self.bar_h = bar_size
        self.bar_y = self.TRACK_H - self.bar_h
        self.bar_v = 0.0
        self.fish_y = self.TRACK_H * 0.55
        self.fish_target = self.fish_y
        self.retarget = 0.0
        self.progress = 0.3
        self.holding = False
        self.result = None
        self.end_t = 0.0
        self.on_done = on_done
        self.t = 0.0
        self.shake = 0.0

    def handle(self, ev):
        if self.result:
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key in HOLD_KEYS:
                self.holding = True
            elif ev.key == pygame.K_ESCAPE:
                self.finish("lose")
        elif ev.type == pygame.KEYUP and ev.key in HOLD_KEYS:
            self.holding = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.holding = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.holding = False

    def finish(self, result):
        self.result = result
        self.end_t = 0.9

    def update(self, dt):
        self.t += dt
        if self.result:
            self.end_t -= dt
            if self.end_t <= 0:
                self.done = True
                self.on_done(self.result)
            return
        acc = -1700 if self.holding else 1150
        self.bar_v = max(-520, min(620, self.bar_v + acc * dt))
        self.bar_y += self.bar_v * dt
        if self.bar_y > self.TRACK_H - self.bar_h:
            self.bar_y = self.TRACK_H - self.bar_h
            self.bar_v *= -0.35
        if self.bar_y < 0:
            self.bar_y = 0
            self.bar_v = 0
        # peixe
        self.retarget -= dt
        d = self.diff / 100.0
        if self.retarget <= 0:
            jump = self.TRACK_H * (0.15 + 0.7 * d) * random.uniform(0.4, 1.0)
            self.fish_target = max(0, min(self.TRACK_H - 24, self.fish_y + random.choice((-1, 1)) * jump))
            self.retarget = random.uniform(0.35, 1.6) * (1.25 - d)
        speed = 1.2 + 7.5 * d
        self.fish_y += (self.fish_target - self.fish_y) * min(1.0, dt * speed)
        self.fish_y += math.sin(self.t * (4 + 10 * d)) * 30 * d * dt
        self.fish_y = max(0, min(self.TRACK_H - 24, self.fish_y))
        center = self.fish_y + 12
        inside = self.bar_y <= center <= self.bar_y + self.bar_h
        if inside:
            self.progress += 0.36 * dt
            self.shake = 0
        else:
            self.progress -= (0.2 + 0.12 * d) * dt
            self.shake = 1
        if self.progress >= 1.0:
            self.progress = 1.0
            self.finish("win")
        elif self.progress <= 0:
            self.progress = 0
            self.finish("lose")

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 250, self.TRACK_H + 120)
        rect.center = (SCREEN_W // 2 + 260, SCREEN_H // 2 - 10)
        ui.panel(surf, rect)
        ui.text(surf, "Pescando!", (rect.centerx, rect.y + 12), 22, C_LILAC, bold=True, center=True)
        track = pygame.Rect(rect.x + 50, rect.y + 52, 70, self.TRACK_H)
        pygame.draw.rect(surf, (20, 40, 70), track, border_radius=10)
        for i in range(0, self.TRACK_H, 26):
            pygame.draw.line(surf, (30, 60, 100), (track.x + 6, track.y + i), (track.right - 6, track.y + i))
        bar = pygame.Rect(track.x + 4, track.y + int(self.bar_y), track.w - 8, int(self.bar_h))
        col = (120, 230, 120) if not self.shake else (90, 190, 100)
        pygame.draw.rect(surf, col, bar, border_radius=8)
        pygame.draw.rect(surf, (200, 255, 200), bar, 2, border_radius=8)
        jitter = random.randint(-2, 2) if self.shake else 0
        if self.fish in ITEMS:
            icon = art.item_icon(self.fish, 2)
        else:
            icon = None
        fy = track.y + int(self.fish_y)
        if self.legendary:
            pygame.draw.circle(surf, (90, 255, 120), (track.centerx, fy + 12), 18, 2)
        if icon:
            surf.blit(icon, (track.centerx - 16 + jitter, fy - 4))
        pr = pygame.Rect(track.right + 26, track.y, 18, self.TRACK_H)
        pygame.draw.rect(surf, (30, 24, 40), pr, border_radius=6)
        fh = int(self.TRACK_H * self.progress)
        pcol = C_GREEN if self.progress > 0.66 else (C_GOLD if self.progress > 0.33 else C_RED)
        pygame.draw.rect(surf, pcol, (pr.x, pr.bottom - fh, pr.w, fh), border_radius=6)
        if self.result == "win":
            ui.text(surf, "Fisgou!", (rect.centerx, rect.bottom - 56), 24, C_GREEN, bold=True, center=True)
        elif self.result == "lose":
            ui.text(surf, "Escapou...", (rect.centerx, rect.bottom - 56), 24, C_RED, bold=True, center=True)
        else:
            ui.text(surf, "Segure ESPAÇO / E", (rect.centerx, rect.bottom - 60), 16, C_TEXT, bold=True, center=True)
            ui.text(surf, "para subir a barra", (rect.centerx, rect.bottom - 38), 15, C_MUTED, center=True)


# ---------------------------------------------------------------------------
# Fliperama "Meteoro"
# ---------------------------------------------------------------------------

class Arcade(ui.Modal):
    W, H = 560, 440

    def __init__(self, on_done, best=0):
        self.on_done = on_done
        self.best = best
        self.x = self.W / 2
        self.left = self.right = False
        self.objs = []
        self.spawn = 0.0
        self.t = 0.0
        self.lives = 3
        self.score = 0
        self.over = False
        self.inv = 0.0
        self.stars = [(random.randrange(self.W), random.randrange(self.H), random.random()) for _ in range(60)]
        self.reported = False

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_a, pygame.K_LEFT):
                self.left = True
            elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                self.right = True
            elif self.over and ev.key in ui.CONFIRM + ui.CANCEL:
                self.done = True
                if not self.reported:
                    self.reported = True
                    self.on_done(self.score)
            elif ev.key == pygame.K_ESCAPE and not self.over:
                self.over = True
        elif ev.type == pygame.KEYUP:
            if ev.key in (pygame.K_a, pygame.K_LEFT):
                self.left = False
            elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                self.right = False

    def update(self, dt):
        if self.over:
            return
        self.t += dt
        self.inv = max(0.0, self.inv - dt)
        speed = 380
        self.x += ((1 if self.right else 0) - (1 if self.left else 0)) * speed * dt
        self.x = max(20, min(self.W - 20, self.x))
        level = 1 + self.t / 12
        self.spawn -= dt
        if self.spawn <= 0:
            self.spawn = max(0.18, 0.75 / level)
            kind = "coin" if random.random() < 0.38 else "rock"
            self.objs.append(dict(kind=kind, x=random.uniform(16, self.W - 16), y=-20.0,
                                  v=random.uniform(150, 230) * (0.8 + level * 0.25),
                                  r=random.randint(10, 18) if kind == "rock" else 10, a=random.uniform(0, 6)))
        keep = []
        for o in self.objs:
            o["y"] += o["v"] * dt
            o["a"] += dt * 3
            if o["y"] > self.H + 30:
                continue
            if abs(o["x"] - self.x) < o["r"] + 14 and abs(o["y"] - (self.H - 36)) < o["r"] + 12:
                if o["kind"] == "coin":
                    self.score += 1
                    continue
                if self.inv <= 0:
                    self.lives -= 1
                    self.inv = 1.2
                    if self.lives <= 0:
                        self.over = True
                continue
            keep.append(o)
        self.objs = keep
        if self.t >= 75:
            self.over = True

    def draw(self, surf):
        outer = pygame.Rect(0, 0, self.W + 40, self.H + 110)
        outer.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, outer, border=(90, 255, 120))
        ui.text(surf, "METEORO", (outer.x + 24, outer.y + 14), 26, (90, 255, 120), bold=True)
        ui.text(surf, f"Pontos: {self.score}   Vidas: {self.lives}   Recorde: {max(self.best, self.score)}",
                (outer.right - 24, outer.y + 20), 18, C_TEXT, right=True)
        area = pygame.Rect(outer.x + 20, outer.y + 56, self.W, self.H)
        game = pygame.Surface((self.W, self.H))
        game.fill((8, 6, 20))
        for (sx, sy, sp) in self.stars:
            yy = (sy + self.t * 40 * (0.3 + sp)) % self.H
            game.set_at((sx, int(yy)), (200, 200, 255) if sp > 0.6 else (110, 110, 160))
        for o in self.objs:
            if o["kind"] == "coin":
                w = abs(math.cos(o["a"])) * 10 + 3
                pygame.draw.ellipse(game, (255, 214, 80), (o["x"] - w, o["y"] - 10, w * 2, 20))
                pygame.draw.ellipse(game, (255, 240, 160), (o["x"] - w / 2, o["y"] - 6, w, 8))
            else:
                pygame.draw.circle(game, (110, 90, 80), (int(o["x"]), int(o["y"])), o["r"])
                pygame.draw.circle(game, (150, 126, 110), (int(o["x"] - 3), int(o["y"] - 3)), o["r"] // 2)
                pygame.draw.circle(game, (90, 255, 120), (int(o["x"]), int(o["y"] - o["r"] - 4)), 3)
        if self.inv <= 0 or int(self.t * 12) % 2 == 0:
            px, py = int(self.x), self.H - 36
            pygame.draw.polygon(game, (184, 76, 255), [(px, py - 18), (px - 16, py + 14), (px + 16, py + 14)])
            pygame.draw.polygon(game, (230, 200, 255), [(px, py - 10), (px - 6, py + 6), (px + 6, py + 6)])
            pygame.draw.rect(game, (255, 160, 60), (px - 5, py + 14, 10, 6))
        if self.over:
            veil = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            veil.fill((0, 0, 0, 160))
            game.blit(veil, (0, 0))
        surf.blit(game, area.topleft)
        pygame.draw.rect(surf, (90, 255, 120), area, 2)
        if self.over:
            ui.text(surf, "FIM DE JOGO", (area.centerx, area.centery - 60), 40, (90, 255, 120), bold=True, center=True)
            ui.text(surf, f"{self.score} pontos  =  $ {self.score * 3}", (area.centerx, area.centery - 6), 24,
                    C_GOLD, bold=True, center=True)
            ui.text(surf, "Aperte E para sair", (area.centerx, area.centery + 40), 18, C_MUTED, center=True)
        else:
            ui.text(surf, "A/D ou setas: mover   Pegue moedas, desvie dos meteoros!", (outer.centerx, outer.bottom - 34),
                    16, C_MUTED, center=True)


# ---------------------------------------------------------------------------
# Fogão
# ---------------------------------------------------------------------------

class Cooking(ui.Modal):
    def __init__(self, game):
        self.g = game
        self.sel = 0
        self.flash = ""
        self.flash_t = 0
        self.flash_ok = True

    def recipes(self):
        return [k for k, r in RECIPES.items() if not r.get("book") or BOOKS[r["book"]]["flag"] in self.g.flags]

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        rs = self.recipes()
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(rs)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(rs)
        elif ev.key in ui.CONFIRM:
            ok, msg = self.g.cook(rs[self.sel])
            self.flash, self.flash_t, self.flash_ok = msg, 2.0, ok
        elif ev.key in ui.CANCEL:
            self.done = True

    def update(self, dt):
        self.flash_t -= dt

    def draw(self, surf):
        rs = self.recipes()
        rect = pygame.Rect(0, 0, 760, 520)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 30)
        ui.panel(surf, rect)
        ui.text(surf, "Fogão", (rect.x + 28, rect.y + 18), 28, C_LILAC, bold=True)
        ui.text(surf, "Escolha uma receita. 'Peixe' = qualquer peixe da mochila.", (rect.x + 30, rect.y + 56), 17,
                C_MUTED)
        y = rect.y + 92
        start = max(0, min(self.sel - 3, len(rs) - 7))
        if start > 0:
            pygame.draw.polygon(surf, C_MUTED, [(rect.right - 40, rect.y + 80), (rect.right - 28, rect.y + 80), (rect.right - 34, rect.y + 72)])
        if start + 7 < len(rs):
            pygame.draw.polygon(surf, C_MUTED, [(rect.right - 40, rect.bottom - 80), (rect.right - 28, rect.bottom - 80), (rect.right - 34, rect.bottom - 72)])
        for i, k in list(enumerate(rs))[start:start + 7]:
            r = RECIPES[k]
            row = pygame.Rect(rect.x + 20, y, rect.w - 40, 44)
            can = self.g.can_cook(k)
            if i == self.sel:
                pygame.draw.rect(surf, C_PANEL_2, row, border_radius=8)
                pygame.draw.rect(surf, C_ACCENT_2, row, 2, border_radius=8)
            surf.blit(art.item_icon(k, 2), (row.x + 8, row.y + 6))
            ui.text(surf, r["name"], (row.x + 54, row.y + 10), 19, C_TEXT if can else C_MUTED, bold=i == self.sel)
            parts = []
            for ing, n in r["needs"].items():
                have = self.g.count_fish() if ing == "fish" else self.g.count_item(ing)
                name = "Peixe" if ing == "fish" else ITEMS[ing]["name"]
                parts.append(f"{name} {min(have, n)}/{n}")
            ui.text(surf, "  ·  ".join(parts), (row.x + 270, row.y + 12), 15, C_GREEN if can else C_MUTED)
            y += 48
        dr = pygame.Rect(rect.x + 20, rect.bottom - 64, rect.w - 40, 46)
        pygame.draw.rect(surf, (14, 10, 22), dr, border_radius=8)
        if self.flash_t > 0:
            ui.text(surf, self.flash, (dr.x + 14, dr.y + 12), 18, C_GREEN if self.flash_ok else C_RED)
        elif rs:
            r = RECIPES[rs[self.sel]]
            ui.text(surf, f"+{r['energy']} de energia · vale ${r['value']} · ótimo presente", (dr.x + 14, dr.y + 12),
                    17, C_MUTED)
        ui.text(surf, "Setas: escolher   E: cozinhar   Esc: sair", (rect.centerx, rect.bottom + 6), 16, C_MUTED,
                center=True)


# ---------------------------------------------------------------------------
# Mochila
# ---------------------------------------------------------------------------

class Inventory(ui.Modal):
    COLS = 12

    def __init__(self, game):
        self.g = game
        self.cur = game.selected
        self.held = None

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        n = len(self.g.inventory)
        if ev.key in (pygame.K_LEFT, pygame.K_a):
            self.cur = (self.cur - 1) % n
        elif ev.key in (pygame.K_RIGHT, pygame.K_d):
            self.cur = (self.cur + 1) % n
        elif ev.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
            self.cur = (self.cur + self.COLS) % n
        elif ev.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
            if self.held is None:
                if self.g.inventory[self.cur]:
                    self.held = self.cur
            else:
                inv = self.g.inventory
                inv[self.held], inv[self.cur] = inv[self.cur], inv[self.held]
                self.held = None
        elif ev.key in (pygame.K_x, pygame.K_DELETE):
            s = self.g.inventory[self.cur]
            if s and ITEMS[s[0]]["kind"] not in ("tool",):
                item = s[0]

                def pick(i, slot=self.cur):
                    if i == 0:
                        self.g.inventory[slot] = None
                self.g.push(ui.Choice(f"Jogar fora {s[1]}x {ITEMS[item]['name']}?", ["Jogar fora", "Cancelar"], pick))
        elif ev.key in (pygame.K_ESCAPE, pygame.K_i, pygame.K_q):
            self.done = True
            if self.cur < HOTBAR_SIZE:
                self.g.select(self.cur)

    def draw(self, surf):
        slot, gap = 58, 6
        w = self.COLS * (slot + gap) + 40
        rect = pygame.Rect(0, 0, w, 360)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2 - 30)
        ui.panel(surf, rect)
        ui.text(surf, "Mochila", (rect.x + 24, rect.y + 16), 26, C_LILAC, bold=True)
        ui.text(surf, f"$ {self.g.money:,}".replace(",", "."), (rect.right - 24, rect.y + 18), 22, C_GOLD, bold=True,
                right=True)
        for i, s in enumerate(self.g.inventory):
            row, col = divmod(i, self.COLS)
            r = pygame.Rect(rect.x + 20 + col * (slot + gap), rect.y + 64 + row * (slot + 22), slot, slot)
            pygame.draw.rect(surf, (16, 12, 24), r, border_radius=8)
            border = C_ACCENT_2 if i == self.cur else (C_GOLD if i == self.held else C_BORDER_DIM)
            pygame.draw.rect(surf, border, r, 3 if i in (self.cur, self.held) else 1, border_radius=8)
            if s:
                icon = art.item_icon(s[0], 3)
                surf.blit(icon, (r.centerx - 24, r.centery - 24))
                if s[1] > 1:
                    ui.text(surf, str(s[1]), (r.right - 5, r.bottom - 22), 16, C_TEXT, bold=True, right=True)
        ui.text(surf, "linha de cima = barra rápida", (rect.x + 22, rect.y + 64 + slot + 2), 13, C_MUTED, shadow=False)
        s = self.g.inventory[self.cur]
        dy = rect.y + 222
        if s:
            it = ITEMS[s[0]]
            ui.text(surf, f"{it['name']}  x{s[1]}", (rect.x + 24, dy), 20, C_TEXT, bold=True)
            ui.text(surf, it.get("desc", ""), (rect.x + 24, dy + 30), 17, C_MUTED)
            if it.get("value"):
                ui.text(surf, f"Vende por $ {it['value']}", (rect.right - 24, dy), 17, C_GOLD, right=True)
        ui.text(surf, "Setas: mover   E: pegar/trocar de lugar   X: jogar fora   Esc/I: fechar",
                (rect.centerx, rect.bottom - 34), 16, C_MUTED, center=True)

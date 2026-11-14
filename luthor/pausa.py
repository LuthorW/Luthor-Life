"""Menu de pausa (Esc): painel no meio da tela com duas abas, como no Stardew.

  Menu           continuar, mochila, objetivos, relacionamentos, conquistas, coleções, rever cenas, álbum,
                 salvar e voltar ao título (ao lado, um resumo do dia)
  Configurações  tela cheia, zoom da câmera, efeitos sonoros (← → mudam na hora) e a lista de controles

Tab troca de aba; na aba Menu, a seta para a direita também vai para Configurações e, nas Configurações, a
seta para a esquerda numa linha sem valor (Controles, Voltar ao menu) volta. Esc fecha. Tudo se grava em
settings.json na hora.
"""
import math

import pygame

from . import ui, audio
from .config import (SCREEN_W, SCREEN_H, ZOOM_LEVELS, C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_ACCENT,
                     C_ACCENT_2, C_BORDER_DIM, C_PINK)

U = ui.U
W, H = 820, 540
TABS = ("Menu", "Configurações")
SFX_STEP = 0.1


def _arrow(surf, x, y, d, col):
    """Setinha em pixel art (d = -1 esquerda, 1 direita, 2 baixo)."""
    if d == 2:
        pygame.draw.polygon(surf, col, [(x - 7, y - 4), (x + 7, y - 4), (x, y + 4)])
    else:
        pygame.draw.polygon(surf, col, [(x - 5 * d, y - 8), (x + 5 * d, y), (x - 5 * d, y + 8)])


class PauseMenu(ui.Modal):
    ROW = 40

    def __init__(self, g, tab=0, sel=0):
        self.g = g
        self.tab = tab
        self.sel = [0, 0]
        self.sel[tab] = sel
        self.t = 0.0

    # ---- opções -------------------------------------------------------
    def menu_items(self):
        g = self.g
        items = [("Continuar", "Volta para o jogo."),
                 ("Mochila", "Itens, comidas e presentes (atalho: I ou Tab)."),
                 ("Objetivos", "Metas da Luthor Corp e benefícios liberados (atalho: O)."),
                 ("Relacionamentos", "Corações com cada personagem (atalho: R)."),
                 ("Conquistas", "Suas medalhas (atalho: K)."),
                 ("Coleções", "Peixes, receitas, coletáveis e livros."),
                 ("Rever cenas", "Assista de novo às cenas que já aconteceram.")]
        if g.album["given"]:
            items.append(("Álbum de fotos", "As fotos das cenas especiais, presente do Barry."))
        items += [("Configurações", "Tela cheia, zoom, som e controles."),
                  ("Salvar e voltar ao título", "Salva o jogo agora e volta para a tela inicial.")]
        return items

    def config_items(self):
        return [("fullscreen", "Tela cheia", "Ocupa o monitor inteiro. Atalho: F11."),
                ("zoom", "Zoom da câmera", "Menor = câmera mais afastada, maior = mais perto. "
                                           "Atalho no jogo: Ctrl + rodinha ou Ctrl + / -."),
                ("sfx", "Efeitos sonoros", "Volume dos sons do jogo (0% = mudo)."),
                ("controls", "Controles", "Todas as teclas do jogo."),
                ("back", "Voltar ao menu", "")]

    def _count(self):
        return len(self.menu_items() if self.tab == 0 else self.config_items())

    # ---- valores ------------------------------------------------------
    def _sfx(self):
        return self.g.settings.get("sfx", 0.7)

    def _change(self, key, d):
        """Muda o valor da linha (d = -1 ou 1). Devolve True se mudou."""
        g = self.g
        if key == "fullscreen":
            g.toggle_fullscreen()
            return True
        if key == "zoom":
            i = ZOOM_LEVELS.index(g.user_zoom())
            j = min(max(i + d, 0), len(ZOOM_LEVELS) - 1)
            if j == i:
                return False
            g.set_zoom(ZOOM_LEVELS[j], toast=False)
            audio.sfx("move")
            return True
        if key == "sfx":
            v = round(min(1.0, max(0.0, self._sfx() + d * SFX_STEP)), 1)
            if v == round(self._sfx(), 1):
                return False
            g.settings["sfx"] = v
            g.save_settings()
            audio.set_volume(sfx_vol=v)
            audio.sfx("confirm")             # para ouvir o volume novo
            return True
        return False

    def _switch(self, tab):
        if tab != self.tab:
            self.tab = tab
            audio.sfx("open")

    def _close(self):
        self.done = True

    def _pick(self):
        g = self.g
        if self.tab == 1:
            key = self.config_items()[self.sel[1]][0]
            if key == "controls":
                audio.sfx("confirm")
                from .game import draw_controls
                g.push(ui.InfoPanel("Controles", draw_controls, scroll=True))
            elif key == "back":
                self._switch(0)
            elif key == "fullscreen":
                self._change(key, 1)
            elif key in ("zoom", "sfx"):        # E avança; no fim volta ao começo
                if not self._change(key, 1):
                    if key == "zoom":
                        g.set_zoom(ZOOM_LEVELS[0], toast=False)
                    else:
                        g.settings["sfx"] = 0.0
                        g.save_settings()
                        audio.set_volume(sfx_vol=0.0)
                    audio.sfx("move")
            return
        label = self.menu_items()[self.sel[0]][0]
        if label == "Configurações":
            self._switch(1)
            return
        audio.sfx("confirm")
        self._close()
        if label == "Mochila":
            from .minigames import Inventory
            g.push(Inventory(g))
        elif label == "Objetivos":
            g.open_goals()
        elif label == "Relacionamentos":
            g.open_relationships()
        elif label == "Conquistas":
            from . import conquistas
            conquistas.open_panel(g)
        elif label == "Coleções":
            g.push(ui.InfoPanel("Coleções", g.draw_collections))
        elif label == "Rever cenas":
            g.open_scene_gallery()
        elif label == "Álbum de fotos":
            from . import album
            album.open_album(g)
        elif label.startswith("Salvar"):
            g.save()
            g.start_fade(lambda: setattr(g, "scene", "title"))

    # ---- entrada ------------------------------------------------------
    def handle(self, ev):
        n = self._count()
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k == pygame.K_TAB:
                self._switch(1 - self.tab)
            elif k in (pygame.K_UP, pygame.K_w):
                self.sel[self.tab] = (self.sel[self.tab] - 1) % n
                audio.sfx("move")
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.sel[self.tab] = (self.sel[self.tab] + 1) % n
                audio.sfx("move")
            elif k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                d = -1 if k in (pygame.K_LEFT, pygame.K_a) else 1
                if self.tab == 0:
                    if d > 0:
                        self._switch(1)
                else:
                    key = self.config_items()[self.sel[1]][0]
                    if key in ("fullscreen", "zoom", "sfx"):
                        self._change(key, d)
                    elif d < 0:
                        self._switch(0)
            elif k in ui.CONFIRM:
                self._pick()
            elif k in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_q):
                audio.sfx("cancel")
                self._close()
        elif ev.type == pygame.MOUSEWHEEL and ev.y:
            self.sel[self.tab] = (self.sel[self.tab] - ev.y) % n
            audio.sfx("move")
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self._pick()

    def update(self, dt):
        self.t += dt

    # ---- desenho ------------------------------------------------------
    def draw(self, surf):
        g = self.g
        shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)   # escurece o jogo atrás do painel
        shade.fill((8, 4, 16, 110))
        surf.blit(shade, (0, 0))
        rect = pygame.Rect(0, 0, W, H)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, "Pausa", (rect.x + 30, rect.y + 20), 30, C_LILAC, bold=True)
        ui.text(surf, f"{g.date_label()}  ·  {g.time_label()}", (rect.right - 30, rect.y + 28), 18, C_MUTED,
                right=True)
        # abas
        tx, ty = rect.x + 26, rect.y + 66
        for i, name in enumerate(TABS):
            w = ui.font(20, True).size(name)[0] + 40
            r = pygame.Rect(tx, ty, w, 36)
            on = i == self.tab
            ui.box(surf, r, C_ACCENT if on else (40, 28, 60), border=C_ACCENT_2 if on else None)
            ui.text(surf, name, (r.centerx, r.y + 5), 20, C_TEXT if on else C_MUTED, bold=True, center=True)
            tx = r.right + 8
        ui.text(surf, "Tab: trocar de aba", (tx + 8, ty + 10), 16, C_MUTED)
        line_y = ty + 36 + 6
        surf.fill(C_BORDER_DIM, (rect.x + 26, line_y, rect.w - 52, U))
        surf.fill((12, 6, 20), (rect.x + 26, line_y + U, rect.w - 52, U))
        body = pygame.Rect(rect.x + 26, line_y + 14, rect.w - 52, rect.bottom - line_y - 70)
        if self.tab == 0:
            desc = self._draw_menu(surf, body)
        else:
            desc = self._draw_config(surf, body)
        # rodapé: o que a opção escolhida faz e as teclas
        fy = rect.bottom - 50
        surf.fill(C_BORDER_DIM, (rect.x + 26, fy - 6, rect.w - 52, U))
        if desc:
            ui.text(surf, desc, (rect.x + 32, fy + 2), 16, C_LILAC)
        keys = ("Setas: escolher  ·  E: confirmar  ·  Esc: voltar ao jogo" if self.tab == 0 else
                "Setas: escolher e mudar  ·  E: confirmar  ·  Esc: voltar ao jogo")
        ui.text(surf, keys, (rect.right - 32, fy + 22), 15, C_MUTED, right=True)

    def _row(self, surf, r, on):
        if on:
            ui.highlight(surf, r)
            bob = int(math.sin(self.t * 7) * 3)
            ax, ay = r.x + 12 + bob, r.centery
            pygame.draw.polygon(surf, C_ACCENT_2, [(ax, ay - 8), (ax + 12, ay), (ax, ay + 8)])

    def _draw_menu(self, surf, body):
        items = self.menu_items()
        self.sel[0] = min(self.sel[0], len(items) - 1)
        lw = 420
        rows = min(len(items), body.h // self.ROW)
        y = body.y
        desc = ""
        for i, (label, d) in enumerate(items[:rows]):
            r = pygame.Rect(body.x, y, lw, self.ROW - 4)
            on = i == self.sel[0]
            self._row(surf, r, on)
            col = C_TEXT if on else C_MUTED
            if label.startswith("Salvar"):
                col = C_PINK if on else (200, 140, 170)
            ui.text(surf, label, (r.x + 36, r.y + 5), 22, col)
            if label == "Configurações":
                _arrow(surf, r.right - 18, r.centery, 1, C_ACCENT_2 if on else C_BORDER_DIM)
            if on:
                desc = d
            y += self.ROW
        self._draw_summary(surf, pygame.Rect(body.x + lw + 20, body.y, body.right - body.x - lw - 20, body.h))
        return desc

    def _draw_summary(self, surf, r):
        """Cartão com o resumo do dia, ao lado do menu."""
        g = self.g
        inner = ui.box(surf, r.inflate(0, -4).move(0, 2), (30, 20, 46), border=(70, 50, 100), cut=2)
        x, y = inner.x + 16, inner.y + 12
        ui.text(surf, "Hoje", (x, y), 20, C_LILAC, bold=True)
        y += 32
        place = g.current_map.label
        rows = [("Dinheiro", f"$ {g.money:,}".replace(",", "."), C_GOLD),
                ("Energia", f"{int(g.energy)}/{g.max_energy}", C_GREEN),
                ("LCORP", f"$ {g.stock:.2f}", C_TEXT)]
        if place:
            rows.insert(0, ("Lugar", place, C_TEXT))
        if g.dating:
            from .characters import NPCS
            who = NPCS[g.partner or g.dating]["short"]
            rows.append(("Coração", ("mora com " if g.partner else "namora ") + who, C_PINK))
        for k, v, col in rows:
            ui.text(surf, k, (x, y), 17, C_MUTED)
            for line in ui.wrap(v, 18, inner.w - 32 - 96)[:2]:
                ui.text(surf, line, (inner.right - 16, y), 18, col, right=True)
                y += 24
            y += 6
        y += 6
        stats = g.stats
        for line in (f"Projetos lançados: {stats.get('launched', 0)}",
                     f"Peixes no aquário: {len(g.aquarium)}",
                     f"Medalhas: {len(g.conquistas.get('got', {}))}"):
            if y > inner.bottom - 26:
                break
            ui.text(surf, line, (x, y), 16, C_MUTED)
            y += 24

    def _draw_config(self, surf, body):
        g = self.g
        items = self.config_items()
        self.sel[1] = min(self.sel[1], len(items) - 1)
        y = body.y + 6
        desc = ""
        vx = body.x + 400                       # coluna dos valores
        vw = body.right - vx - 10
        for i, (key, label, d) in enumerate(items):
            h = 52
            if key == "back":
                y += 10
            r = pygame.Rect(body.x, y, body.w, h - 6)
            on = i == self.sel[1]
            self._row(surf, r, on)
            ui.text(surf, label, (r.x + 36, r.y + 10), 22, C_TEXT if on else C_MUTED)
            cy = r.centery
            col = C_ACCENT_2 if on else C_BORDER_DIM
            if key == "fullscreen":
                fs = bool(g.settings.get("fullscreen"))
                for j, (name, val) in enumerate((("Não", False), ("Sim", True))):
                    br = pygame.Rect(vx + 30 + j * 120, cy - 15, 104, 30)
                    act = fs == val
                    ui.box(surf, br, C_ACCENT if act else (34, 24, 50), border=C_ACCENT_2 if act else None)
                    ui.text(surf, name, (br.centerx, br.y + 4), 19, C_TEXT if act else C_MUTED, bold=act,
                            center=True)
            elif key in ("zoom", "sfx"):
                if key == "zoom":
                    n, cur = len(ZOOM_LEVELS), ZOOM_LEVELS.index(g.user_zoom())
                    val = f"{round(ZOOM_LEVELS[cur] * 100)}%" + (" (padrão)" if ZOOM_LEVELS[cur] == 1.0 else "")
                    frac = cur / (n - 1)
                    ticks = n
                else:
                    v = round(self._sfx(), 1)
                    val = "mudo" if v == 0 else f"{round(v * 100)}%"
                    frac = v
                    ticks = 11
                bar = pygame.Rect(vx + 30, cy - 6, vw - 180, 12)
                _arrow(surf, vx + 12, cy, -1, col)
                _arrow(surf, bar.right + 18, cy, 1, col)
                ui.slot(surf, bar.inflate(4, 4))
                fill = int((bar.w - 4) * frac)
                if fill > 0:
                    surf.fill(C_ACCENT if on else (96, 40, 150), (bar.x + 2, bar.y + 2, fill, bar.h - 4))
                    surf.fill(C_LILAC if on else (140, 110, 180), (bar.x + 2, bar.y + 2, fill, U))
                for t in range(ticks):                       # marquinhas de cada nível
                    tx = bar.x + 2 + int((bar.w - 4) * t / (ticks - 1))
                    surf.fill((20, 10, 30), (min(tx, bar.right - 4), bar.bottom + 4, U, 4))
                kx = bar.x + 2 + fill
                ui.cut_rect(surf, C_GOLD if on else C_MUTED, (min(kx - 5, bar.right - 10), bar.y - 4, 10, bar.h + 8), 1)
                ui.text(surf, val, (vx + vw - 4, r.y + 10), 20, C_TEXT if on else C_MUTED, right=True)
            elif key == "controls":
                ui.text(surf, "ver teclas", (vx + vw - 22, r.y + 12), 18, C_TEXT if on else C_MUTED, right=True)
                _arrow(surf, vx + vw - 6, cy, 1, col)
            if on:
                desc = d
            y += h
        return desc


def open_pause(g, tab=0, sel=0):
    audio.sfx("open")
    g.push(PauseMenu(g, tab, sel))

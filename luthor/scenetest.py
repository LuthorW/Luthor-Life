"""Modo de teste de cenas: assistir qualquer cutscene sem progresso no jogo e sem salvar nada.

  python main.py --cenas            abre a lista com todas as cutscenes
  python main.py --cena lucy_6      toca uma cena direto (depois aparece a lista)

Na lista: setas escolhem, Enter assiste, PgUp/PgDn pulam páginas, Esc fecha.
Durante o jogo, F5 reabre a lista. Cenas novas em cutscenes.SCENES aparecem sozinhas.
"""
import pygame

from . import ui
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_ACCENT, C_GOLD, C_LILAC
from .characters import ROMANCES
from .cutscenes import Cutscene, SCENES, dating_scene, move_in_scene


def all_keys():
    keys = list(SCENES)
    keys += [f"namoro_{k}" for k in ROMANCES] + [f"mudanca_{k}" for k in ROMANCES]
    return keys


def build(key):
    if key.startswith("namoro_"):
        return dating_scene(key.split("_", 1)[1])
    if key.startswith("mudanca_"):
        return move_in_scene(key.split("_", 1)[1])
    return SCENES[key]


class SceneList(ui.Modal):
    ROWS = 11

    def __init__(self, game, keys, sel=0):
        self.g = game
        self.keys = keys
        self.sel = sel
        self.top = max(0, sel - self.ROWS // 2)

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        n = len(self.keys)
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % n
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % n
        elif ev.key == pygame.K_PAGEUP:
            self.sel = max(0, self.sel - self.ROWS)
        elif ev.key == pygame.K_PAGEDOWN:
            self.sel = min(n - 1, self.sel + self.ROWS)
        elif ev.key in ui.CONFIRM:
            self.done = True
            play(self.g, self.keys[self.sel])
            return
        elif ev.key in ui.CANCEL:
            self.done = True
            self.g.toasts.push("Modo de teste de cenas: F5 abre a lista de novo.", C_LILAC)
            return
        if self.sel < self.top:
            self.top = self.sel
        elif self.sel >= self.top + self.ROWS:
            self.top = self.sel - self.ROWS + 1

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 640, 130 + self.ROWS * 40)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, "Teste de cenas", (rect.centerx, rect.y + 16), 26, C_TEXT, bold=True, center=True)
        ui.text(surf, f"{len(self.keys)} cenas · nada é salvo neste modo", (rect.centerx, rect.y + 50), 16, C_MUTED,
                center=True)
        y = rect.y + 80
        for i in range(self.top, min(len(self.keys), self.top + self.ROWS)):
            k = self.keys[i]
            r = pygame.Rect(rect.x + 24, y, rect.w - 48, 34)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            ui.text(surf, self.g.scene_title(k), (r.x + 14, r.y + 6), 20, C_TEXT if i == self.sel else C_MUTED)
            ui.text(surf, k, (r.right - 14, r.y + 8), 15, C_GOLD if i == self.sel else C_MUTED, right=True)
            y += 40
        ui.text(surf, "Setas: escolher   Enter: assistir   PgUp/PgDn: página   Esc: fechar",
                (rect.centerx, rect.bottom - 34), 15, C_MUTED, center=True)


def open_list(g, sel=0):
    keys = all_keys()
    g.push(SceneList(g, keys, min(sel, len(keys) - 1)))


def play(g, key):
    keys = all_keys()
    try:
        scene = build(key)
    except Exception as e:                     # cena com erro: mostra o motivo em vez de fechar o jogo
        g.toasts.push(f"Erro ao montar a cena '{key}': {e}", (248, 113, 113))
        open_list(g, keys.index(key) if key in keys else 0)
        return
    g.play_scene(key, scene=scene, remember=False,
                 on_end=lambda: open_list(g, keys.index(key) if key in keys else 0))


def setup(g, argv):
    """Começa um jogo novo só na memória (sem cena de abertura) e abre a lista ou uma cena."""
    g.save = lambda *a, **k: None              # nunca grava o save
    g.reset_state()
    g.map_name = "home"
    from .world import HOME_BED
    g.player.place_tile(*HOME_BED, "down")
    g.plan_npcs()
    g.scene = "play"
    g.modals = []
    g.cars = []

    orig_handle = g.handle

    def handle(ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F5 and not any(
                isinstance(m, (Cutscene, SceneList)) for m in g.modals):
            open_list(g)
            return
        orig_handle(ev)
    g.handle = handle

    key = None
    if "--cena" in argv:
        i = argv.index("--cena")
        key = argv[i + 1] if i + 1 < len(argv) else None
    if key and key in all_keys():
        play(g, key)
    else:
        if key:
            g.toasts.push(f"Cena '{key}' não encontrada. Escolha na lista.", (248, 113, 113))
        open_list(g)

"""Modo de teste de horário: mudar dia, horário, estação e clima na hora, sem salvar nada.

  python main.py --teste            abre o seu jogo salvo (ou um jogo novo) e o painel de teste
  F6                                abre o painel de novo (funciona também no modo --cenas)

No painel: setas cima/baixo escolhem, esquerda/direita mudam o valor (Shift = passos maiores),
Enter aplica e fecha, Esc fecha sem mudar. Com "Relógio parado", o horário não anda sozinho.
"""
import pygame

from . import ui, seasons
from .config import SCREEN_W, SCREEN_H, C_TEXT, C_MUTED, C_ACCENT, C_GOLD, C_LILAC, DAYS_PER_QUARTER

STATE = {"frozen": False}
WEEK = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def _fmt(minutes):
    m = minutes % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


class TimePanel(ui.Modal):
    ROWS = ["Horário", "Dia", "Estação", "Ano", "Clima", "Relógio parado"]

    def __init__(self, g):
        self.g = g
        self.sel = 0
        self.v = dict(minutes=g.minutes, day=g.day, quarter=g.quarter, year=g.year, weather=g.weather,
                      frozen=STATE["frozen"])

    def handle(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        big = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(self.ROWS)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(self.ROWS)
        elif ev.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            self.change(1 if ev.key in (pygame.K_RIGHT, pygame.K_d) else -1, big)
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e, pygame.K_SPACE):
            self.done = True
            apply(self.g, self.v)
        elif ev.key in (pygame.K_ESCAPE, pygame.K_F6):
            self.done = True

    def change(self, d, big):
        v, row = self.v, self.ROWS[self.sel]
        if row == "Horário":
            # das 6h às 2h da madrugada (o dia do jogo), de 30 em 30 min (Shift: 2 h)
            v["minutes"] = max(6 * 60, min(26 * 60 - 10, v["minutes"] + d * (120 if big else 30)))
        elif row == "Dia":
            v["day"] = (v["day"] - 1 + d * (7 if big else 1)) % DAYS_PER_QUARTER + 1
        elif row == "Estação":
            v["quarter"] = (v["quarter"] - 1 + d) % 4 + 1
        elif row == "Ano":
            v["year"] = max(2034, v["year"] + d)
        elif row == "Clima":
            v["weather"] = "chuva" if v["weather"] == "sol" else "sol"
        elif row == "Relógio parado":
            v["frozen"] = not v["frozen"]

    def label(self, row):
        v = self.v
        season = seasons.of_quarter(v["quarter"])
        return {
            "Horário": _fmt(v["minutes"]),
            "Dia": f"{v['day']}  ({WEEK[(v['day'] - 1) % 7]})",
            "Estação": f"{seasons.NAMES[season]}  (Q{v['quarter']})",
            "Ano": str(v["year"]),
            "Clima": ("neve" if season == "winter" else "chuva") if v["weather"] == "chuva" else "sol",
            "Relógio parado": "sim" if v["frozen"] else "não",
        }[row]

    def draw(self, surf):
        rect = pygame.Rect(0, 0, 560, 120 + len(self.ROWS) * 44 + 40)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, rect)
        ui.text(surf, "Teste de dia e horário", (rect.centerx, rect.y + 16), 26, C_TEXT, bold=True, center=True)
        ui.text(surf, "nada é salvo neste modo", (rect.centerx, rect.y + 50), 16, C_MUTED, center=True)
        y = rect.y + 84
        for i, row in enumerate(self.ROWS):
            r = pygame.Rect(rect.x + 24, y, rect.w - 48, 36)
            if i == self.sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=8)
            ui.text(surf, row, (r.x + 14, r.y + 7), 20, C_TEXT if i == self.sel else C_MUTED)
            val = self.label(row)
            ui.text(surf, f"<  {val}  >" if i == self.sel else val, (r.right - 14, r.y + 7), 20,
                    C_GOLD if i == self.sel else C_TEXT, right=True)
            y += 44
        ui.text(surf, "Cima/baixo: escolher   Esquerda/direita: mudar (Shift = mais)", (rect.centerx, rect.bottom - 62),
                15, C_MUTED, center=True)
        ui.text(surf, "Enter: aplicar   Esc: fechar sem mudar", (rect.centerx, rect.bottom - 38), 15, C_MUTED,
                center=True)


def apply(g, v):
    """Leva o jogo para o dia/horário escolhido: rotinas, figurantes, coletáveis e estação se ajustam."""
    new_day = (v["day"], v["quarter"], v["year"]) != (g.day, g.quarter, g.year)
    g.day, g.quarter, g.year = v["day"], v["quarter"], v["year"]
    g.weather = v["weather"]
    g.minutes = v["minutes"]
    g.time_acc = 0.0
    STATE["frozen"] = v["frozen"]
    g.apply_season()
    if new_day:
        g.crowd.reset_day()
        from . import activities
        activities.spawn_forage(g)
    g.plan_npcs(snap=True)
    g.scene_check_pending = True
    g.toasts.push(f"Teste: {g.date_label()}, {_fmt(g.minutes)}"
                  + ("  (relógio parado)" if STATE["frozen"] else ""), C_LILAC)


def install(g):
    """F6 abre o painel; com o relógio parado, o horário não anda."""
    orig_handle, orig_update = g.handle, g.update

    def handle(ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F6 and g.scene == "play" and not any(
                isinstance(m, TimePanel) for m in g.modals):
            g.push(TimePanel(g))
            return
        orig_handle(ev)

    def update(dt):
        if STATE["frozen"]:
            g.time_acc = 0.0
        orig_update(dt)

    g.handle, g.update = handle, update


def setup(g):
    """Abre o jogo salvo (ou um novo) sem nunca gravar e já mostra o painel."""
    loaded = False
    if g.has_save():
        try:
            g.load()
            loaded = True
        except Exception:
            loaded = False
    if not loaded:
        g.reset_state()
        g.map_name = "home"
        from .world import HOME_BED
        g.player.place_tile(*HOME_BED, "down")
        g.plan_npcs()
    g.save = lambda *a, **k: None                  # nunca grava o save
    g.scene = "play"
    g.modals = []
    install(g)
    g.push(TimePanel(g))

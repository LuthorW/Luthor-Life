"""Vários jogos salvos: 3 espaços escolhidos na tela de título (Continuar, Carregar jogo, Novo jogo).

O espaço 1 é o saves/save.json de sempre (o jogo salvo antigo continua abrindo nele); os outros são save2.json e
save3.json. Cada espaço tem o próprio álbum de fotos (saves/album, album2, album3). O último espaço usado fica em
settings["slot"] e é o que "Continuar" abre.
"""
import json
import math
import os
import time

import pygame

from . import art, ui, audio
from .config import SAVE_DIR, SAVE_PATH, SCREEN_W, SCREEN_H, DAYS_PER_QUARTER, WEEKDAYS, C_TEXT, C_MUTED, \
    C_LILAC, C_GOLD, C_PINK, C_ACCENT, C_ACCENT_2, C_GREEN

SLOTS = 3


def path(slot):
    return SAVE_PATH if slot == 1 else os.path.join(SAVE_DIR, f"save{slot}.json")


def album_dir(slot):
    return os.path.join(SAVE_DIR, "album" if slot == 1 else f"album{slot}")


def exists(slot):
    return os.path.exists(path(slot))


def any_save():
    return any(exists(s) for s in range(1, SLOTS + 1))


def continue_slot(g):
    """Espaço que o "Continuar" abre: o último usado; se ele estiver vazio, o jogo salvo mais recente."""
    last = g.settings.get("slot", 1)
    if exists(last):
        return last
    found = [(os.path.getmtime(path(s)), s) for s in range(1, SLOTS + 1) if exists(s)]
    return max(found)[1] if found else None


_info_cache = {}


def info(slot):
    """Resumo do jogo salvo para o cartão (lido do arquivo; guardado enquanto o arquivo não muda)."""
    p = path(slot)
    if not os.path.exists(p):
        return None
    mt = os.path.getmtime(p)
    hit = _info_cache.get(slot)
    if hit and hit[0] == mt:
        return hit[1]
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = None
    if d is None:
        res = dict(broken=True, saved_at=mt)
    else:
        res = dict(broken=False, day=int(d.get("day", 1)), quarter=int(d.get("quarter", 1)),
                   year=int(d.get("year", 2034)), money=int(d.get("money", 0)), map=d.get("map", "home"),
                   dating=d.get("dating"), partner=d.get("partner"), casadas="casadas" in d.get("flags", []),
                   medals=len(d.get("conquistas", {}).get("got", [])) if isinstance(d.get("conquistas"), dict) else 0,
                   saved_at=d.get("saved_at") or mt, quarter_days=int(d.get("quarter_days", 28)))
    _info_cache[slot] = (mt, res)
    return res


def delete(slot):
    """Apaga o jogo salvo do espaço e as fotos do álbum dele."""
    for p in (path(slot), path(slot) + ".tmp"):
        if os.path.exists(p):
            os.remove(p)
    d = album_dir(slot)
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.lower().endswith(".png"):
                try:
                    os.remove(os.path.join(d, f))
                except OSError:
                    pass
    _info_cache.pop(slot, None)


def use_slot(g, slot):
    """Passa a jogar no espaço (e lembra dele para o próximo "Continuar")."""
    g.slot = slot
    if g.settings.get("slot") != slot:
        g.settings["slot"] = slot
        g.save_settings()


# ---------------------------------------------------------------------------
# Tela de escolha do espaço
# ---------------------------------------------------------------------------
class SlotMenu(ui.Modal):
    """mode "load": abre um jogo salvo; mode "new": escolhe onde começar o jogo novo. X apaga um espaço."""
    W, CARD_H = 820, 132

    def __init__(self, g, mode):
        self.g = g
        self.mode = mode
        slots = list(range(1, SLOTS + 1))
        if mode == "load":
            self.sel = (continue_slot(g) or 1) - 1
        else:                                   # jogo novo: começa no primeiro espaço vazio
            self.sel = next((s - 1 for s in slots if not exists(s)), 0)
        self.t = 0.0

    def _move(self, d):
        self.sel = (self.sel + d) % SLOTS
        audio.sfx("move")

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (4, 5):
            self._move(-1 if ev.button == 4 else 1)
            return
        if ev.type != pygame.KEYDOWN:
            return
        slot = self.sel + 1
        if ev.key in (pygame.K_UP, pygame.K_w):
            self._move(-1)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self._move(1)
        elif ev.key in ui.CANCEL:
            audio.sfx("cancel")
            self.done = True
        elif ev.key in (pygame.K_x, pygame.K_DELETE) and exists(slot):
            audio.sfx("open")
            label = date_text(info(slot))

            def pick(i):
                if i == 0:
                    delete(slot)
                    audio.sfx("cancel")
                    self.g.toasts.push(f"Espaço {slot} apagado.", C_MUTED)
                    if self.mode == "load" and not any_save():
                        self.done = True
            self.g.push(ui.Choice(f"Apagar o jogo do espaço {slot} ({label})? Não dá para desfazer.",
                                  ["Cancelar", "Sim, apagar"], lambda i: pick(1 - i)))
        elif ev.key in ui.CONFIRM:
            self._confirm(slot)

    def _confirm(self, slot):
        g = self.g
        if self.mode == "load":
            if not exists(slot):
                audio.sfx("cancel")
                return
            audio.sfx("confirm")
            self.done = True

            def go():
                old = g.slot
                use_slot(g, slot)
                try:
                    g.load()
                except Exception as e:
                    use_slot(g, old)
                    g.scene = "title"
                    g.toasts.push(f"Não foi possível carregar o jogo salvo ({e}).", (240, 110, 110))
            g.start_fade(go)
            return

        def start():
            self.done = True
            use_slot(g, slot)
            g.start_fade(g.new_game)
        if exists(slot):
            audio.sfx("open")
            g.push(ui.Choice(f"O espaço {slot} já tem um jogo ({date_text(info(slot))}). Ele será substituído "
                             "quando o jogo novo salvar. Começar mesmo assim?", ["Cancelar", "Sim, jogo novo aqui"],
                             lambda i: start() if i == 1 else None))
        else:
            audio.sfx("confirm")
            start()

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((8, 4, 18, 150))
        surf.blit(veil, (0, 0))
        h = 110 + SLOTS * (self.CARD_H + 14) + 40
        outer = pygame.Rect(0, 0, self.W, h)
        outer.center = (SCREEN_W // 2, SCREEN_H // 2)
        ui.panel(surf, outer, alpha=250)
        title = "Carregar jogo" if self.mode == "load" else "Novo jogo: escolha um espaço"
        ui.text(surf, title, (outer.x + 34, outer.y + 22), 30, C_GOLD, bold=True)
        sub = ("O jogo salva sozinho quando a Letícia dorme." if self.mode == "load"
               else "Cada espaço guarda um jogo diferente (com o próprio álbum de fotos).")
        ui.text(surf, sub, (outer.x + 36, outer.y + 60), 17, C_LILAC)
        y = outer.y + 98
        for i in range(SLOTS):
            r = pygame.Rect(outer.x + 30, y, outer.w - 60, self.CARD_H)
            self._card(surf, r, i + 1, i == self.sel)
            y += self.CARD_H + 14
        keys = "Setas: escolher   E: " + ("abrir" if self.mode == "load" else "começar aqui") + \
               "   X: apagar   Esc: voltar"
        ui.text(surf, keys, (outer.centerx, outer.bottom - 34), 16, C_MUTED, center=True)

    def _card(self, surf, r, slot, on):
        g = self.g
        d = info(slot)
        fill = (74, 44, 104) if on else (44, 28, 62)
        surf.fill((14, 8, 22), r.move(0, 4))
        ui.box(surf, r, fill, border=C_ACCENT_2 if on else (92, 64, 124), cut=2)
        if on:                                       # setinha balançando, como na caixa de escolhas
            bob = int(math.sin(self.t * 7) * 3)
            ax, ay = r.x - 22 + bob, r.centery
            pygame.draw.polygon(surf, C_ACCENT_2, [(ax, ay - 10), (ax + 14, ay), (ax, ay + 10)])
        badge = pygame.Rect(r.x + 14, r.y + 14, 44, 44)
        ui.box(surf, badge, C_ACCENT if on else (66, 42, 92), cut=2)
        ui.text(surf, str(slot), (badge.centerx, badge.y + 5), 28, C_TEXT, bold=True, center=True)
        if d is None:
            ui.text(surf, "Espaço vazio", (r.x + 80, r.y + 22), 26, C_TEXT if on else C_MUTED, bold=True)
            msg = "Comece um jogo novo aqui." if self.mode == "new" else "Nenhum jogo salvo neste espaço."
            ui.text(surf, msg, (r.x + 80, r.y + 58), 18, C_MUTED)
            return
        if d.get("broken"):
            ui.text(surf, "Jogo salvo com defeito", (r.x + 80, r.y + 22), 26, (240, 120, 120), bold=True)
            ui.text(surf, "O arquivo não abre. Dá para apagar (X) e usar o espaço de novo.", (r.x + 80, r.y + 58),
                    18, C_MUTED)
            return
        port = art.portrait("leticia_feliz.png" if art.portrait_exists("leticia_feliz.png") else "leticia.png",
                            {}, 104)
        ui.blit_portrait(surf, port, (r.x + 66, r.bottom - 106))
        tx = r.x + 182
        ui.text(surf, date_text(d), (tx, r.y + 14), 26, C_TEXT, bold=True)
        place = g.world[d["map"]].label if d["map"] in g.world else "National City"
        money = f"$ {d['money']:,}".replace(",", ".")
        ui.text(surf, f"{money}   ·   {place}", (tx, r.y + 50), 19, C_GOLD)
        rel = _relationship(d)
        if rel:
            hx = tx
            surf.blit(art.heart(True, 2), (hx, r.y + 88))
            ui.text(surf, rel, (hx + 26, r.y + 82), 19, C_PINK, bold=True)
        if d.get("medals"):
            ui.text(surf, f"{d['medals']} conquista(s)", (r.right - 20, r.y + 50), 17, C_GREEN, right=True)
        when = time.strftime("%d/%m/%Y %H:%M", time.localtime(d["saved_at"]))
        ui.text(surf, f"salvo em {when}", (r.right - 20, r.y + 16), 15, C_MUTED, right=True)
        partner = d.get("partner") or d.get("dating")
        if partner:
            from .characters import NPCS
            npc = NPCS.get(partner)
            if npc:
                fname = art.portrait_file(npc.get("portrait_key", partner), "happy") or npc.get("portrait")
                p = art.portrait(fname, npc["look"], 64)
                ui.blit_portrait(surf, p, (r.right - 84, r.bottom - 66))


def date_text(d):
    if not d or d.get("broken"):
        return "arquivo com defeito"
    from .seasons import NAMES, of_quarter
    day = max(1, min(DAYS_PER_QUARTER, d["day"]))       # saves da estação de 28 dias
    return f"{WEEKDAYS[(day - 1) % 7]}, {day} · {NAMES[of_quarter(d['quarter'])]} {d['year']}"


def _relationship(d):
    from .characters import NPCS
    k = d.get("partner") or d.get("dating")
    if not k or k not in NPCS:
        return ""
    name = NPCS[k]["short"]                                # só a Lucy e a Vittoria namoram
    if d.get("casadas"):
        return f"Casada com a {name}"
    if d.get("partner"):
        return f"Morando com a {name}"
    return f"Namorando a {name}"

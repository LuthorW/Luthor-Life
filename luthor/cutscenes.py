"""Cutscenes: o motor e os roteiros.

Cada cena é um dicionário com "map" (onde acontece), "time" (horário, só para a iluminação),
"npc" (personagem principal, para as escolhas) e "steps" (a lista de comandos).

COMANDOS (cada um é uma tupla):
  ("ator", nome, x, y, direção)      coloca um personagem ("player" = Letícia) num tile
  ("sai", nome)                       tira o personagem de cena
  ("andar", nome, x, y)               anda até o tile (primeiro na horizontal, depois na vertical)
  ("andar_", nome, x, y)              igual, mas a cena não espera ele chegar
  ("virar", nome, direção)            up / down / left / right
  ("pulo", nome)                      pulinho de alegria
  ("emote", nome, tipo)               balão: coracao, exclamacao, pergunta, reticencias, musica,
                                      gota, raiva, brilho, zzz, vergonha
  ("fala", nome, "texto", humor)      fala com retrato (humor: None, "happy", "smile", "love")
  ("narra", "texto")                  narração sem retrato
  ("escolha", "pergunta", [("opção", pontos, "resposta da personagem"), ...])
  ("camera", x, y)                    câmera desliza até o tile
  ("camera_ja", x, y)                 câmera pula direto para o tile
  ("seguir", nome)                    câmera acompanha um personagem
  ("mapa", nome, horário)             troca de lugar no meio da cena (com fade)
  ("hora", minutos)                   muda a iluminação
  ("legenda", "texto", segundos)      texto grande no centro da tela
  ("foto", "arquivo.jpg")             mostra uma foto em tela cheia (assets/portraits)
  ("efeito", tipo, segundos)          coracoes, brilhos, confete, petalas
  ("esperar", segundos)
  ("fade_in",) / ("fade_out",)
"""
import math
import random

import pygame

from . import art, ui
from .config import SCREEN_W, SCREEN_H, TILE, C_TEXT, C_LILAC, C_PINK, C_MUTED, C_GOLD
from .characters import NPCS
from .entities import PLAYER_LOOK, draw_shadow, idle_frame, FOOT
from .config import SCALE

PLAYER_NAME = "Letícia"
PLAYER_PORTRAIT = "leticia.jpg"
BAR_H = 64


# ---------------------------------------------------------------------------
# Atores
# ---------------------------------------------------------------------------

class Actor:
    SPEED = 2.6

    def __init__(self, name, x, y, d):
        self.name = name
        look = PLAYER_LOOK if name == "player" else NPCS[name]["look"]
        self.frames = art.character_frames(look)
        self.fx, self.fy = float(x), float(y)
        self.dir = d
        self.path = []
        self.moving = False
        self.anim = 0.0
        self.hop = 0.0
        self.emote = None
        self.emote_t = 0.0
        self.phase = random.uniform(0, 5)

    @property
    def base_y(self):
        return (self.fy + 1) * TILE - FOOT

    @property
    def center(self):
        return ((self.fx + 0.5) * TILE, (self.fy + 0.5) * TILE)

    def walk_to(self, x, y):
        self.path = []
        if x != round(self.fx):
            self.path.append((float(x), self.fy))
        self.path.append((float(x), float(y)))

    def update(self, dt):
        self.moving = False
        self.hop = max(0.0, self.hop - dt)
        if self.emote_t > 0:
            self.emote_t -= dt
            if self.emote_t <= 0:
                self.emote = None
        if not self.path:
            return
        tx, ty = self.path[0]
        dx, dy = tx - self.fx, ty - self.fy
        dist = math.hypot(dx, dy)
        step = self.SPEED * dt
        if dist <= step:
            self.fx, self.fy = tx, ty
            self.path.pop(0)
        else:
            self.fx += dx / dist * step
            self.fy += dy / dist * step
        if abs(dx) > abs(dy):
            self.dir = "right" if dx > 0 else "left"
        elif dy:
            self.dir = "down" if dy > 0 else "up"
        self.moving = True
        self.anim += dt * 7

    def draw(self, surf, cam):
        img, bob = idle_frame(self.frames, self.dir, self.moving, self.anim, self.phase)
        cx = (self.fx + 0.5) * TILE - cam[0]
        cy = self.base_y - cam[1]
        jump = -int(math.sin(self.hop / 0.45 * math.pi) * 6 * SCALE) if self.hop > 0 else 0
        draw_shadow(surf, int(cx), int(cy) + SCALE, 10 * SCALE if not jump else 8 * SCALE)
        surf.blit(img, (int(cx - img.get_width() // 2), int(cy - img.get_height() + FOOT + bob + jump)))
        if self.emote:
            draw_emote(surf, int(cx), int(cy - img.get_height() - 6 + jump), self.emote, 1 - max(0, self.emote_t - 1.0))


def draw_emote(surf, x, y, kind, k=1.0):
    pop = min(1.0, k * 1.6)
    w, h = int(34 * pop), int(30 * pop)
    if w < 6:
        return
    r = pygame.Rect(x - w // 2, y - h, w, h)
    pygame.draw.rect(surf, (40, 24, 56), r.inflate(4, 4), border_radius=10)
    pygame.draw.rect(surf, (255, 255, 255), r, border_radius=9)
    pygame.draw.polygon(surf, (255, 255, 255), [(x - 5, r.bottom - 1), (x + 5, r.bottom - 1), (x, r.bottom + 6)])
    cx, cy = r.center
    if pop < 1:
        return
    if kind == "coracao":
        surf.blit(art.heart(True, 3), (cx - 10, cy - 9))
    elif kind == "exclamacao":
        pygame.draw.rect(surf, (230, 60, 70), (cx - 2, cy - 10, 5, 13))
        pygame.draw.rect(surf, (230, 60, 70), (cx - 2, cy + 6, 5, 4))
    elif kind == "pergunta":
        ui.text(surf, "?", (cx, cy - 15), 26, (90, 110, 220), center=True, shadow=False)
    elif kind == "reticencias":
        for i in (-8, 0, 8):
            pygame.draw.rect(surf, (90, 80, 110), (cx + i - 2, cy, 4, 4))
    elif kind == "musica":
        pygame.draw.rect(surf, (184, 76, 255), (cx + 2, cy - 10, 3, 14))
        pygame.draw.ellipse(surf, (184, 76, 255), (cx - 5, cy + 1, 9, 7))
        pygame.draw.rect(surf, (184, 76, 255), (cx + 2, cy - 10, 8, 3))
    elif kind == "gota":
        pygame.draw.polygon(surf, (110, 180, 250), [(cx, cy - 10), (cx - 6, cy + 3), (cx + 6, cy + 3)])
        pygame.draw.circle(surf, (110, 180, 250), (cx, cy + 3), 6)
    elif kind == "raiva":
        for a in (0, 90, 180, 270):
            v = pygame.math.Vector2(1, 0).rotate(a + 45)
            pygame.draw.line(surf, (230, 60, 70), (cx + v.x * 3, cy + v.y * 3), (cx + v.x * 10, cy + v.y * 10), 3)
    elif kind == "brilho":
        for a in range(0, 360, 90):
            v = pygame.math.Vector2(1, 0).rotate(a)
            pygame.draw.line(surf, (250, 200, 60), (cx, cy), (cx + v.x * 10, cy + v.y * 10), 3)
        pygame.draw.circle(surf, (255, 240, 150), (cx, cy), 4)
    elif kind == "zzz":
        ui.text(surf, "z", (cx - 6, cy - 6), 18, (120, 120, 200), shadow=False)
        ui.text(surf, "Z", (cx + 2, cy - 15), 22, (120, 120, 200), shadow=False)
    elif kind == "vergonha":
        pygame.draw.ellipse(surf, (255, 140, 170), (cx - 13, cy - 3, 10, 6))
        pygame.draw.ellipse(surf, (255, 140, 170), (cx + 3, cy - 3, 10, 6))
        for i in (-11, -7, 5, 9):
            pygame.draw.line(surf, (230, 90, 130), (cx + i, cy - 2), (cx + i + 2, cy + 2))


# ---------------------------------------------------------------------------
# Efeitos de cena
# ---------------------------------------------------------------------------

class SceneFx:
    def __init__(self):
        self.parts = []
        self.spawners = []

    def add(self, kind, secs, cx, cy):
        self.spawners.append(dict(kind=kind, t=secs, cx=cx, cy=cy))

    def update(self, dt):
        for s in self.spawners:
            s["t"] -= dt
            rate = {"coracoes": 7, "brilhos": 10, "confete": 40, "petalas": 14}.get(s["kind"], 8)
            for _ in range(int(rate * dt + random.random())):
                if s["kind"] == "confete":
                    self.parts.append(dict(k="confete", x=s["cx"] + random.uniform(-300, 300), y=s["cy"] - 320,
                                           vx=random.uniform(-30, 30), vy=random.uniform(80, 160), life=4,
                                           c=random.choice([(255, 120, 170), (255, 220, 90), (120, 200, 255),
                                                            (184, 76, 255), (120, 230, 140)])))
                elif s["kind"] == "petalas":
                    self.parts.append(dict(k="petala", x=s["cx"] + random.uniform(-500, 300), y=s["cy"] - 300,
                                           vx=random.uniform(20, 60), vy=random.uniform(30, 60), life=7,
                                           c=(255, 200, 222)))
                else:
                    self.parts.append(dict(k=s["kind"], x=s["cx"] + random.uniform(-60, 60),
                                           y=s["cy"] + random.uniform(-10, 30), vx=random.uniform(-10, 10),
                                           vy=random.uniform(-60, -35), life=random.uniform(1.4, 2.4), c=None))
        self.spawners = [s for s in self.spawners if s["t"] > 0]
        for p in self.parts:
            p["life"] -= dt
            p["x"] += (p["vx"] + (math.sin(p["life"] * 4) * 20 if p["k"] in ("petala", "confete") else 0)) * dt
            p["y"] += p["vy"] * dt
        self.parts = [p for p in self.parts if p["life"] > 0][-300:]

    def draw(self, surf, cam):
        for p in self.parts:
            x, y = int(p["x"] - cam[0]), int(p["y"] - cam[1])
            if p["k"] == "coracoes":
                img = art.heart(True, 2, (255, 110, 160))
                img.set_alpha(int(255 * min(1, p["life"])))
                surf.blit(img, (x, y))
            elif p["k"] == "brilhos":
                k = 2 + int(2 * abs(math.sin(p["life"] * 6)))
                pygame.draw.line(surf, (255, 240, 170), (x - k, y), (x + k, y))
                pygame.draw.line(surf, (255, 240, 170), (x, y - k), (x, y + k))
            else:
                pygame.draw.rect(surf, p["c"], (x, y, 5 if p["k"] == "confete" else 4, 3))


# ---------------------------------------------------------------------------
# Motor
# ---------------------------------------------------------------------------

class Cutscene(ui.Modal):
    def __init__(self, game, scene, on_end=None):
        self.g = game
        self.scene = scene
        self.steps = list(scene["steps"])
        self.on_end = on_end
        self.npc = scene.get("npc")
        self.i = 0
        self.map = game.world[scene["map"]]
        self.minutes = scene.get("time", game.minutes)
        self.weather = scene.get("weather", "sol")
        self.actors = {}
        self.cam = [0.0, 0.0]
        self.cam_target = None
        self.follow = None
        self.wait_cam = False
        self.bars = 0.0
        self.fade = 1.0
        self.fade_dir = 0
        self.after_fade = None
        self.wait = 0.0
        self.wait_actor = None
        self.sub = None
        self.caption = None
        self.photo = None
        self.fx = SceneFx()
        self.ask_skip = False
        self.finished = False
        self.t = 0.0
        game.ambient.reset()

    # ----- câmera
    def tile_cam(self, x, y):
        vw, vh = self.g.view_size(self.map)
        cx = (x + 0.5) * TILE - vw / 2
        cy = (y + 0.5) * TILE - vh / 2
        return self.clamp(cx, cy)

    def clamp(self, cx, cy):
        vw, vh = self.g.view_size(self.map)
        mw, mh = self.map.w * TILE, self.map.h * TILE
        cx = (mw - vw) / 2 if mw <= vw else min(max(cx, 0), mw - vw)
        cy = (mh - vh) / 2 if mh <= vh else min(max(cy, 0), mh - vh)
        return [cx, cy]

    # ----- execução
    def blocked(self):
        if self.sub or self.wait > 0 or self.fade_dir or self.photo or self.ask_skip:
            return True
        if self.caption and self.caption["t"] > 0:
            return True
        if self.wait_actor and self.wait_actor.path:
            return True
        if self.wait_cam and self.cam_target:
            return True
        return False

    def run_steps(self):
        while not self.blocked() and not self.finished:
            if self.i >= len(self.steps):
                self.finish()
                return
            step = self.steps[self.i]
            self.i += 1
            self.exec(step)

    def speaker(self, name):
        if name == "player":
            return PLAYER_NAME, art.portrait(PLAYER_PORTRAIT, PLAYER_LOOK, 112), "Letícia Luthor"
        d = NPCS[name]
        return d["name"], None, d["role"]

    def exec(self, step):
        cmd, args = step[0], step[1:]
        if cmd == "ator":
            name, x, y, d = args
            self.actors[name] = Actor(name, x, y, d)
        elif cmd == "sai":
            self.actors.pop(args[0], None)
        elif cmd in ("andar", "andar_"):
            a = self.actors.get(args[0])
            if a:
                a.walk_to(args[1], args[2])
                if cmd == "andar":
                    self.wait_actor = a
        elif cmd == "virar":
            a = self.actors.get(args[0])
            if a:
                a.dir = args[1]
        elif cmd == "pulo":
            a = self.actors.get(args[0])
            if a:
                a.hop = 0.45
        elif cmd == "emote":
            a = self.actors.get(args[0])
            if a:
                a.emote, a.emote_t = args[1], 1.8
            self.wait = 0.7
        elif cmd == "fala":
            name, txt = args[0], args[1]
            mood = args[2] if len(args) > 2 else None
            spk, portrait, sub = self.speaker(name)
            if portrait is None:
                portrait = self.g.portrait_for(self.g.npcs[name], mood)
            self.sub = ui.Dialog(spk, [txt], portrait, subtitle=sub)
        elif cmd == "narra":
            self.sub = ui.Dialog("", [args[0]])
        elif cmd == "escolha":
            question, options = args[0], args[1]

            def pick(i, options=options):
                txt, pts, reply = options[i]
                if self.npc and pts:
                    self.g.add_friendship(self.npc, pts)
                if reply and self.npc:
                    mood = "love" if pts >= 50 else ("smile" if pts > 0 else None)
                    self.steps.insert(self.i, ("fala", self.npc, reply, mood))
            self.sub = ui.Choice(question, [o[0] for o in options], pick)
        elif cmd == "camera":
            self.cam_target = self.tile_cam(args[0], args[1])
            self.follow = None
            self.wait_cam = True
        elif cmd == "camera_ja":
            self.cam = self.tile_cam(args[0], args[1])
            self.cam_target = None
            self.follow = None
        elif cmd == "seguir":
            self.follow = args[0]
        elif cmd == "mapa":
            def swap(name=args[0], tm=args[1] if len(args) > 1 else None):
                self.map = self.g.world[name]
                self.actors = {}
                self.follow = None
                self.cam_target = None
                if tm is not None:
                    self.minutes = tm
                self.g.ambient.reset()
            self.fade_dir = 1
            self.after_fade = swap
        elif cmd == "hora":
            self.minutes = args[0]
        elif cmd == "legenda":
            self.caption = dict(text=args[0], t=args[1] if len(args) > 1 else 2.5, total=args[1] if len(args) > 1 else 2.5)
        elif cmd == "foto":
            if art.portrait_exists(args[0]):
                self.photo = art.portrait(args[0], PLAYER_LOOK, 420)
        elif cmd == "efeito":
            kind, secs = args[0], args[1] if len(args) > 1 else 2.5
            if self.actors:
                xs = [a.center[0] for a in self.actors.values()]
                ys = [a.center[1] for a in self.actors.values()]
                cx, cy = sum(xs) / len(xs), sum(ys) / len(ys) - TILE
            else:
                vw, vh = self.g.view_size(self.map)
                cx, cy = self.cam[0] + vw / 2, self.cam[1] + vh / 2
            self.fx.add(kind, secs, cx, cy)
        elif cmd == "esperar":
            self.wait = args[0]
        elif cmd == "fade_in":
            self.fade_dir = -1
        elif cmd == "fade_out":
            self.fade_dir = 1

    def finish(self):
        if self.finished:
            return
        self.finished = True
        self.done = True
        self.g.ambient.reset()
        if self.on_end:
            self.on_end()

    # ----- loop
    def handle(self, ev):
        if self.ask_skip:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE, pygame.K_s):
                    self.finish()
                elif ev.key in (pygame.K_ESCAPE, pygame.K_n, pygame.K_BACKSPACE):
                    self.ask_skip = False
            return
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not isinstance(self.sub, ui.Choice):
            self.ask_skip = True
            return
        if self.photo is not None:
            if ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM:
                self.photo = None
            return
        if self.sub:
            self.sub.handle(ev)
            if self.sub.done:
                self.sub = None
        elif self.caption and ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM:
            self.caption["t"] = min(self.caption["t"], 0.3)

    def update(self, dt):
        self.t += dt
        self.bars = min(1.0, self.bars + dt * 2.5)
        if self.fade_dir == 1:
            self.fade = min(1.0, self.fade + dt * 2.5)
            if self.fade >= 1:
                self.fade_dir = 0
                if self.after_fade:
                    cb, self.after_fade = self.after_fade, None
                    cb()
        elif self.fade_dir == -1:
            self.fade = max(0.0, self.fade - dt * 2.0)
            if self.fade <= 0:
                self.fade_dir = 0
        if self.sub:
            self.sub.update(dt)
        self.wait = max(0.0, self.wait - dt)
        if self.caption:
            self.caption["t"] -= dt
            if self.caption["t"] <= -0.4:
                self.caption = None
        for a in self.actors.values():
            a.update(dt)
        if self.follow and self.follow in self.actors:
            a = self.actors[self.follow]
            self.cam_target = self.tile_cam(a.fx, a.fy)
        if self.cam_target:
            k = min(1.0, dt * 2.2)
            self.cam[0] += (self.cam_target[0] - self.cam[0]) * k
            self.cam[1] += (self.cam_target[1] - self.cam[1]) * k
            if abs(self.cam_target[0] - self.cam[0]) < 2 and abs(self.cam_target[1] - self.cam[1]) < 2:
                self.cam = list(self.cam_target)
                if not self.follow:
                    self.cam_target = None
        self.fx.update(dt)
        self.g.ambient.update(dt, self.map, self.cam, self.minutes, self.weather)
        if not self.blocked():
            self.wait_actor = None
            self.wait_cam = False
        self.run_steps()

    def draw(self, surf):
        cam = (int(self.cam[0]) // 2 * 2, int(self.cam[1]) // 2 * 2)
        self.g.render_map(surf, self.map, cam, minutes=self.minutes, actors=list(self.actors.values()),
                          weather=self.weather, extra=self.fx)
        bh = int(BAR_H * (1 - (1 - self.bars) ** 2))
        if bh:
            pygame.draw.rect(surf, (0, 0, 0), (0, 0, SCREEN_W, bh))
            pygame.draw.rect(surf, (0, 0, 0), (0, SCREEN_H - bh, SCREEN_W, bh))
        if self.caption:
            c = self.caption
            k = min(1.0, max(0.0, min(c["total"] - c["t"], c["t"] + 0.4) / 0.4))
            img = ui.font(40, True).render(c["text"], False, C_TEXT)
            sh = ui.font(40, True).render(c["text"], False, (20, 10, 30))
            img.set_alpha(int(255 * k))
            sh.set_alpha(int(200 * k))
            x = SCREEN_W // 2 - img.get_width() // 2
            surf.blit(sh, (x + 3, SCREEN_H // 2 - 40 + 4))
            surf.blit(img, (x, SCREEN_H // 2 - 40))
        if self.fade > 0:
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.set_alpha(int(255 * self.fade))
            surf.blit(veil, (0, 0))
        if self.sub:
            self.sub.draw(surf)
        if self.photo is not None:
            veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            veil.fill((10, 4, 20, 200))
            surf.blit(veil, (0, 0))
            r = self.photo.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 10))
            pygame.draw.rect(surf, (250, 246, 240), r.inflate(28, 60), border_radius=6)
            surf.blit(self.photo, r)
            hrt = art.heart(True, 4)
            surf.blit(hrt, (r.centerx - hrt.get_width() // 2, r.bottom + 10))
        if bh > 20:
            ui.text(surf, "Esc: pular cena", (SCREEN_W - 20, bh - 26), 15, (120, 110, 140), right=True, shadow=False)
        if self.ask_skip:
            r = pygame.Rect(0, 0, 440, 120)
            r.center = (SCREEN_W // 2, SCREEN_H // 2)
            ui.panel(surf, r)
            ui.text(surf, "Pular esta cena?", (r.centerx, r.y + 22), 24, C_LILAC, bold=True, center=True)
            ui.text(surf, "E = pular     Esc = continuar assistindo", (r.centerx, r.y + 66), 17, C_MUTED, center=True)


# ---------------------------------------------------------------------------
# Roteiros
# ---------------------------------------------------------------------------

SCENES = {
    # ----------------------------------------------------------- abertura
    "intro": dict(map="home", time=7 * 60, steps=[
        ("ator", "player", 3, 4, "down"),
        ("camera_ja", 6, 6),
        ("fade_in",),
        ("legenda", "National City, 2034", 2.6),
        ("emote", "player", "zzz"),
        ("esperar", 0.6),
        ("andar", "player", 3, 6),
        ("andar", "player", 15, 6),
        ("andar", "player", 15, 4),
        ("virar", "player", "up"),
        ("narra", "Da cobertura, dá pra ver a cidade inteira acordando. As torres, o parque, o mar lá no fundo."),
        ("fala", "player", "Primeiro dia como CEO da Luthor Corp. Sem pressão, Letícia. Nenhuma pressão."),
        ("emote", "player", "gota"),
        ("narra", "O celular vibra no bolso."),
        ("emote", "player", "exclamacao"),
        ("fala", "jess", "Bom dia, Srta. Luthor! Aqui é a Jess. Pronta pro primeiro dia?"),
        ("fala", "jess", "Deixei propostas de projeto na sua mochila. É só levar ao laboratório, na torre roxa."),
        ("fala", "jess", "Escolha uma proposta na barra (1 a 9) e aperte E numa bancada livre. Depois, trabalhe nela todo dia."),
        ("fala", "jess", "Quando ficar pronto, o produto vai pra Mesa de Contratos. Os contratos fecham à noite."),
        ("fala", "jess", "Ah, e... a Lucy Williams, da CatCo, voltou pra cidade. Só comentando. Boa sorte, chefe!"),
        ("emote", "player", "reticencias"),
        ("fala", "player", "Lucy Williams. Claro que ela voltou justo agora."),
        ("mapa", "city", 7 * 60),
        ("camera_ja", 8, 15),
        ("fade_in",),
        ("camera", 21, 12),
        ("legenda", "Luthor Corp", 1.8),
        ("camera", 48, 12),
        ("legenda", "CatCo Worldwide Media", 1.8),
        ("camera", 64, 31),
        ("legenda", "Calçadão Bayside", 1.8),
        ("camera", 55, 59),
        ("legenda", "A orla e o píer", 1.8),
        ("camera", 20, 33),
        ("legenda", "Bem-vinda a National City", 2.4),
        ("fade_out",),
    ]),

    # ----------------------------------------------------------- Lucy
    "lucy_2": dict(map="catco", time=19 * 60 + 30, npc="lucy", steps=[
        ("ator", "lucy", 11, 7, "down"),
        ("ator", "player", 11, 13, "up"),
        ("camera_ja", 11, 9),
        ("fade_in",),
        ("legenda", "CatCo, depois do expediente", 1.8),
        ("andar", "player", 11, 9),
        ("emote", "lucy", "exclamacao"),
        ("fala", "lucy", "Letícia Luthor na redação da CatCo depois do expediente. Isso vai dar o que falar.", "smile"),
        ("fala", "player", "Vim sem assessoria, sem gravador. Só... queria conversar."),
        ("emote", "lucy", "reticencias"),
        ("fala", "lucy", "Sabe o que eu percebi? Você me olha igual na faculdade. Como se eu fosse um problema pra resolver."),
        ("escolha", "O que responder?", [
            ("Você sempre foi o melhor problema da minha vida.", 60, "...Ok. Essa foi boa. Não acostuma."),
            ("Eu só queria te entender.", 40, "Muita gente tentou. Pouca gente chegou perto."),
            ("Você está investigando a minha empresa, Lucy.", 0, "Justo. Mas não é só isso, e você sabe."),
        ]),
        ("fala", "lucy", "Eu não sou um problema, Letícia. Eu sou... uma pergunta em aberto.", "smile"),
        ("emote", "lucy", "brilho"),
        ("fala", "lucy", "Me encontra no Noonan's qualquer noite. Sem gravador. Prometo.", "happy"),
        ("andar", "lucy", 15, 7),
        ("andar_", "lucy", 15, 13),
        ("virar", "player", "right"),
        ("emote", "player", "coracao"),
        ("esperar", 1.0),
        ("fade_out",),
    ]),
    "lucy_4": dict(map="books", time=18 * 60 + 30, npc="lucy", steps=[
        ("ator", "lucy", 4, 7, "up"),
        ("ator", "player", 8, 10, "up"),
        ("camera_ja", 6, 7),
        ("fade_in",),
        ("legenda", "Bayside Books", 1.6),
        ("andar", "player", 8, 8),
        ("andar", "player", 5, 8),
        ("virar", "player", "left"),
        ("emote", "lucy", "musica"),
        ("virar", "lucy", "right"),
        ("emote", "lucy", "exclamacao"),
        ("fala", "lucy", "Ah! Você. Eu estava justamente... lendo. Coisas. De repórter.", "smile"),
        ("fala", "lucy", "Toma. Achei isso aqui e lembrei de você. Um mistério sem solução óbvia.", "happy"),
        ("emote", "lucy", "vergonha"),
        ("fala", "lucy", "Tipo a gente, né? Não faz essa cara. Aceita o livro e pronto."),
        ("escolha", "O que dizer?", [
            ("Você lembrou que eu adoro mistério?", 60, "Eu lembro de tudo, Luthor. Esse é exatamente o problema."),
            ("Vou ler hoje mesmo.", 40, "Me conta o final. Mas não me conta quem é o culpado."),
            ("Prefiro relatórios financeiros.", -10, "...Eu desisto de você. (Ela está rindo.)"),
        ]),
        ("pulo", "lucy"),
        ("efeito", "brilhos", 1.5),
        ("esperar", 1.4),
        ("fade_out",),
    ]),
    "lucy_6": dict(map="city", time=21 * 60 + 30, npc="lucy", steps=[
        ("ator", "lucy", 61, 64, "down"),
        ("ator", "player", 60, 56, "down"),
        ("camera_ja", 60, 61),
        ("fade_in",),
        ("legenda", "O píer, à noite", 1.8),
        ("andar", "player", 60, 63),
        ("andar", "player", 60, 64),
        ("virar", "player", "right"),
        ("virar", "lucy", "left"),
        ("fala", "lucy", "Eu terminei a matéria do apagão. Quer saber o final?"),
        ("fala", "player", "Depende. Eu vou precisar de um advogado?"),
        ("emote", "lucy", "musica"),
        ("fala", "lucy", "Não foi a LuthorCorp. Foi uma falha na rede pública. Vocês seguraram a cidade de pé.", "smile"),
        ("fala", "lucy", "Eu precisava saber que você era diferente da sua família. Agora eu sei."),
        ("emote", "lucy", "reticencias"),
        ("fala", "lucy", "E isso me assusta mais do que qualquer pauta."),
        ("escolha", "Como reagir?", [
            ("Pegar a mão dela.", 70, "...Sua mão está gelada. Fica assim mais um pouco."),
            ("Obrigada por acreditar em mim.", 45, "Eu não acreditei. Eu verifiquei. É diferente. E melhor."),
            ("Então a matéria vai elogiar a empresa?", 0, "Vai ser justa. Que é o máximo que eu faço por qualquer um."),
        ]),
        ("efeito", "brilhos", 2.5),
        ("emote", "lucy", "coracao"),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
    "lucy_8": dict(map="city", time=18 * 60 + 25, npc="lucy", steps=[
        ("ator", "lucy", 26, 56, "down"),
        ("ator", "player", 26, 53, "down"),
        ("camera_ja", 26, 56),
        ("fade_in",),
        ("legenda", "Pôr do sol na praia", 1.8),
        ("andar", "player", 25, 53),
        ("andar", "player", 25, 56),
        ("virar", "player", "right"),
        ("virar", "lucy", "left"),
        ("fala", "lucy", "Letícia... eu não sei mais onde termina a repórter e começa eu.", "love"),
        ("fala", "player", "Talvez não precise terminar em lugar nenhum."),
        ("emote", "lucy", "vergonha"),
        ("fala", "lucy", "Se um dia você me der rosas vermelhas, eu vou aceitar. Só pra você saber.", "love"),
        ("narra", "(Rosas vermelhas estão à venda no Mercado Central.)"),
        ("efeito", "coracoes", 3),
        ("esperar", 2.0),
        ("fade_out",),
    ]),
    "lucy_10": dict(map="city", time=22 * 60, npc="lucy", steps=[
        ("ator", "lucy", 23, 33, "left"),
        ("ator", "player", 23, 41, "up"),
        ("camera_ja", 21, 34),
        ("fade_in",),
        ("legenda", "O chafariz do parque, quase meia-noite", 2.0),
        ("andar", "player", 23, 34),
        ("virar", "lucy", "down"),
        ("virar", "player", "up"),
        ("fala", "lucy", "Às vezes eu acordo e penso: como a gente chegou aqui?", "love"),
        ("fala", "lucy", "Anos de silêncio, um apagão, mil cafés... e você.", "love"),
        ("fala", "player", "Eu pensei em você todos esses anos, Lucy. Todos."),
        ("emote", "lucy", "coracao"),
        ("foto", "lucy_apaixonada.jpg"),
        ("fala", "lucy", "Se quiser ir mais longe... você sabe onde me encontrar.", "love"),
        ("efeito", "coracoes", 4),
        ("esperar", 2.5),
        ("fade_out",),
    ]),

    # ----------------------------------------------------------- Vittoria
    "vittoria_2": dict(map="trattoria", time=14 * 60, npc="vittoria", steps=[
        ("ator", "vittoria", 9, 4, "down"),
        ("ator", "player", 10, 11, "up"),
        ("camera_ja", 9, 7),
        ("fade_in",),
        ("legenda", "Ricci Trattoria", 1.6),
        ("andar", "player", 10, 6),
        ("andar", "player", 9, 6),
        ("emote", "vittoria", "exclamacao"),
        ("fala", "vittoria", "Você de novo! Vou começar a reservar sua mesa.", "happy"),
        ("emote", "vittoria", "musica"),
        ("pulo", "vittoria"),
        ("narra", "Ela gira a massa no ar, uma, duas, três vezes. A pizza aterrissa perfeita."),
        ("fala", "vittoria", "Margherita, como em Napoli. Por conta da casa. Não conta pros outros clientes, eh?", "happy"),
        ("escolha", "O que dizer?", [
            ("Você é uma artista, Vittoria.", 60, "Artista? Eu sou italiana. É a mesma coisa. Grazie!"),
            ("Que cheiro incrível!", 40, "É o manjericão. E o forno a lenha. E um pouco de amor."),
            ("Tem versão sem glúten?", -5, "...Vou fingir que não ouvi isso. Mangia!"),
        ]),
        ("efeito", "brilhos", 1.6),
        ("esperar", 1.4),
        ("fade_out",),
    ]),
    "vittoria_4": dict(map="market", time=7 * 60 + 10, npc="vittoria", steps=[
        ("ator", "vittoria", 3, 7, "up"),
        ("ator", "bea", 13, 4, "down"),
        ("ator", "player", 8, 10, "up"),
        ("camera_ja", 7, 7),
        ("fade_in",),
        ("legenda", "Mercado Central, 7h da manhã", 1.8),
        ("andar", "player", 8, 7),
        ("andar", "player", 4, 7),
        ("virar", "player", "left"),
        ("emote", "vittoria", "reticencias"),
        ("fala", "vittoria", "Esse não. Esse também não. Esse... perfetto!"),
        ("virar", "vittoria", "right"),
        ("emote", "vittoria", "exclamacao"),
        ("fala", "vittoria", "Letícia! Acordou cedo pra me ver escolher tomates? Que romântico.", "happy"),
        ("fala", "vittoria", "Sabe, eu decidi uma coisa. Você agora é família Ricci.", "happy"),
        ("fala", "vittoria", "E família Ricci tem 20% de desconto na Trattoria. Regra da nonna. Não se discute."),
        ("fala", "bea", "Ela fala isso pra todo mundo, viu? Mentira. Só pra você."),
        ("emote", "vittoria", "vergonha"),
        ("efeito", "brilhos", 1.6),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
    "vittoria_6": dict(map="trattoria", time=23 * 60 + 10, npc="vittoria", steps=[
        ("ator", "vittoria", 12, 3, "up"),
        ("ator", "player", 10, 11, "up"),
        ("camera_ja", 11, 6),
        ("fade_in",),
        ("legenda", "Depois do último cliente", 1.8),
        ("andar", "player", 12, 11),
        ("andar", "player", 12, 4),
        ("virar", "vittoria", "down"),
        ("fala", "vittoria", "Entra, entra. A cozinha já está fechada, mas pra você... sempre aberta.", "smile"),
        ("fala", "vittoria", "Isto aqui é o caderno de receitas da minha nonna. Eu fiz uma cópia pra você.", "happy"),
        ("fala", "vittoria", "Ninguém fora da família viu isso. Nem o Marco, que implora toda semana."),
        ("escolha", "O que dizer?", [
            ("Vou cozinhar a lasanha pra você.", 70, "Promessa? Então eu provo. E se estiver boa... eu caso. Brincadeira. Talvez."),
            ("É uma honra, Vittoria.", 45, "A honra é minha, tesoro. A nonna ia gostar de você."),
            ("Eu só sei fazer miojo.", 10, "Dio mio. Tudo bem. A gente começa do zero. Amanhã. Aula particular."),
        ]),
        ("efeito", "coracoes", 2),
        ("esperar", 1.6),
        ("fade_out",),
    ]),
    "vittoria_8": dict(map="city", time=15 * 60 + 20, npc="vittoria", steps=[
        ("ator", "vittoria", 17, 39, "down"),
        ("ator", "player", 15, 30, "down"),
        ("camera_ja", 17, 34),
        ("fade_in",),
        ("legenda", "Uma volta no parque", 1.6),
        ("andar", "player", 15, 39),
        ("andar", "player", 16, 39),
        ("virar", "player", "right"),
        ("virar", "vittoria", "left"),
        ("efeito", "petalas", 6),
        ("fala", "vittoria", "Letícia, posso ser sincera? Italiana não sabe ser diferente.", "love"),
        ("fala", "vittoria", "Eu gosto de você. Mais do que de massa fresca. E isso é muito.", "love"),
        ("emote", "vittoria", "vergonha"),
        ("fala", "vittoria", "Se você sentir o mesmo... rosas vermelhas. Do Mercado Central. Eu vou entender."),
        ("emote", "player", "coracao"),
        ("efeito", "coracoes", 3),
        ("esperar", 2.0),
        ("fade_out",),
    ]),
    "vittoria_10": dict(map="city", time=7 * 60 + 30, npc="vittoria", steps=[
        ("ator", "vittoria", 47, 56, "down"),
        ("ator", "player", 47, 53, "down"),
        ("camera_ja", 47, 56),
        ("fade_in",),
        ("legenda", "Manhã na praia", 1.6),
        ("andar", "player", 48, 53),
        ("andar", "player", 48, 56),
        ("virar", "player", "left"),
        ("virar", "vittoria", "right"),
        ("fala", "vittoria", "Fui nadar e pensei em você o tempo todo. Quase engoli o mar.", "love"),
        ("fala", "vittoria", "Fico pensando em como seria acordar com você e fazer café da manhã pra duas.", "love"),
        ("emote", "vittoria", "vergonha"),
        ("fala", "vittoria", "Desculpa, falei alto. Coisa de italiana. ...Mas é verdade."),
        ("efeito", "coracoes", 3),
        ("esperar", 2.0),
        ("fade_out",),
    ]),

    # ----------------------------------------------------------- equipe
    "brainy_3": dict(map="hq", time=20 * 60, npc="brainy", steps=[
        ("ator", "brainy", 11, 5, "right"),
        ("ator", "player", 17, 10, "up"),
        ("camera_ja", 14, 6),
        ("fade_in",),
        ("legenda", "Laboratório, fora do expediente", 1.8),
        ("andar", "player", 17, 6),
        ("andar", "player", 13, 6),
        ("andar", "player", 13, 5),
        ("virar", "player", "left"),
        ("emote", "brainy", "exclamacao"),
        ("fala", "brainy", "CEO. Que bom. Tenho uma confissão: existe um projeto que não está no portfólio."),
        ("fala", "brainy", "O Projeto Hecate. Materiais experimentais, sinais seguros... e 12% de mistério."),
        ("efeito", "brilhos", 2.5),
        ("fala", "brainy", "Acho que você está pronta. As propostas já estão no Terminal P&D."),
        ("emote", "player", "brilho"),
        ("esperar", 1.0),
        ("fade_out",),
    ]),
    "brainy_5": dict(map="hq", time=8 * 60, npc="brainy", steps=[
        ("ator", "brainy", 11, 5, "right"),
        ("ator", "player", 13, 5, "left"),
        ("camera_ja", 14, 6),
        ("fade_in",),
        ("fala", "brainy", "Construí uma coisa pra você. Um drone de laboratório."),
        ("efeito", "brilhos", 3),
        ("narra", "Um drone roxo, do tamanho de uma maçã, flutua entre as bancadas e apita feliz."),
        ("fala", "brainy", "Ele vai trabalhar em todos os projetos ativos toda manhã, antes de você chegar."),
        ("fala", "brainy", "Por favor, não o chame de 'robozinho'. Ele é sensível. Eu o programei assim."),
        ("emote", "player", "musica"),
        ("esperar", 1.0),
        ("fade_out",),
    ]),
    "sam_3": dict(map="hq", time=17 * 60, npc="sam", steps=[
        ("ator", "sam", 21, 11, "down"),
        ("ator", "player", 18, 16, "up"),
        ("camera_ja", 20, 13),
        ("fade_in",),
        ("andar", "player", 18, 13),
        ("andar", "player", 21, 13),
        ("virar", "player", "up"),
        ("fala", "sam", "Letícia, revisei todos os contratos de fornecimento da empresa.", "happy"),
        ("fala", "sam", "A partir de hoje, a Mesa de Contratos paga 10% a mais por tudo."),
        ("emote", "player", "exclamacao"),
        ("fala", "sam", "Considere um presente de amiga. E de CFO. A Ruby mandou um abraço, aliás.", "happy"),
        ("efeito", "brilhos", 1.6),
        ("esperar", 1.2),
        ("fade_out",),
    ]),
}


def dating_scene(key):
    d = NPCS[key]
    steps = [
        ("ator", key, 21, 28, "right"),
        ("ator", "player", 24, 33, "left"),
        ("camera_ja", 22, 33),
        ("fade_in",),
        ("legenda", "Rosas vermelhas", 1.8),
    ]
    for line in d["accept_lines"]:
        steps.append(("fala", key, line, "love"))
    steps += [
        ("pulo", key),
        ("emote", key, "coracao"),
        ("fala", "player", "Então é oficial?"),
        ("fala", key, "Oficialíssimo. Pode contar pra cidade inteira.", "love"),
        ("efeito", "coracoes", 4),
    ]
    if key == "lucy":
        steps.append(("foto", "lucy_apaixonada.jpg"))
    else:
        steps.append(("foto", "vittoria_apaixonada.jpg"))
    steps += [("legenda", "Vocês estão namorando!", 2.2), ("fade_out",)]
    return dict(map="city", time=21 * 60, npc=key, steps=steps)


def move_in_scene(key):
    d = NPCS[key]
    steps = [
        ("ator", "player", 14, 10, "down"),
        ("camera_ja", 14, 11),
        ("fade_in",),
        ("legenda", "Dia da mudança", 1.8),
        ("ator", key, 16, 14, "up"),
        ("andar", key, 16, 12),
        ("andar", key, 14, 12),
        ("andar", key, 14, 11),
        ("virar", key, "up"),
    ]
    for line in d["move_lines"]:
        steps.append(("fala", key, line, "love"))
    steps += [
        ("fala", "player", "Bem-vinda em casa."),
        ("pulo", key), ("pulo", "player"),
        ("efeito", "confete", 3),
        ("emote", key, "coracao"),
        ("legenda", f"{d['short']} agora mora na cobertura!", 2.4),
        ("fade_out",),
    ]
    return dict(map="home", time=18 * 60, npc=key, steps=steps)


PLAYER_DATE_LINES = [
    "Eu ia trazer flores, mas achei que você ia me zoar.",
    "Sabe que eu cancelei uma reunião do conselho pra vir? Valeu cada minuto.",
    "Você fica linda com essa luz.",
]


def date_scene(key, place, game):
    """Cena curta de encontro, montada a partir do lugar marcado."""
    m, x, y, d, desc = place
    gmap = game.world[m]
    px, py, pd = x, y + 1, "up"
    for (dx, dy, face) in ((1, 0, "left"), (-1, 0, "right"), (0, 1, "up"), (0, -1, "down")):
        if not gmap.is_solid(x + dx, y + dy):
            px, py, pd = x + dx, y + dy, face
            break
    lines = NPCS[key]["date_lines"]
    steps = [
        ("ator", key, x, y, d),
        ("ator", "player", px, py, pd),
        ("camera_ja", x, y),
        ("fade_in",),
        ("legenda", desc[0].upper() + desc[1:], 1.8),
        ("virar", key, {"left": "right", "right": "left", "up": "down", "down": "up"}[pd]),
        ("fala", key, lines[0], "love"),
        ("fala", "player", random.choice(PLAYER_DATE_LINES)),
        ("emote", key, "vergonha"),
        ("fala", key, random.choice(lines[1:]), "love"),
        ("efeito", "coracoes", 3),
        ("esperar", 1.5),
        ("legenda", "Mais tarde...", 1.6),
        ("fade_out",),
    ]
    if m == "cinema":
        steps.insert(-3, ("fala", key, "Shh, vai começar! Me passa a pipoca? ...A pipoca inteira, de preferência.", "happy"))
    if m == "trattoria" and key == "vittoria":
        steps.insert(-3, ("fala", key, "E nem pensa em pagar. A casa paga. A dona da casa insiste.", "happy"))
    return dict(map=m, time=20 * 60 + 30, npc=key, steps=steps)

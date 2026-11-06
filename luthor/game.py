"""Luthor Life — núcleo do jogo."""
import json
import math
import os
import random

import pygame

from . import art, ui
from .config import (SCALE, TITLE, SCREEN_W, SCREEN_H, FPS, TILE, SAVE_DIR, SAVE_PATH, SETTINGS_PATH, SAVE_VERSION,
                     DAY_START, DAY_END, SECONDS_PER_10MIN, DAYS_PER_QUARTER, START_YEAR, WEEKDAYS,
                     WEEKDAYS_FULL, BASE_ENERGY, WORK_ENERGY, FISH_ENERGY, ARCADE_ENERGY, WALK_SPEED, RUN_SPEED,
                     HEART_POINTS, MAX_HEARTS, ROMANCE_CAP_HEARTS, TALK_POINTS, GIFT_POINTS, START_STATIONS,
                     MAX_STATIONS, INVENTORY_SIZE, HOTBAR_SIZE, C_TEXT, C_MUTED, C_LILAC, C_GOLD, C_GREEN, C_RED,
                     C_ACCENT, C_ACCENT_2, C_PINK)
from .data import (PROJECTS, ITEMS, FISH, JUNK, RECIPES, BOOKS, SHOPS, SELLABLE, FLAG_LABELS, NEWS, TIPS, GOALS,
                   FORAGE)
from .characters import NPCS, NPC_ORDER, TEAM, ROMANCES
from .entities import Player, NPC, Car, DIRS, draw_shadow, PLAYER_LOOK, FOOT, DRINK_ICONS, draw_drink
from .world import build_world, COUNTERS, WATER_TILES, STATION_SLOTS, HOME_BED, HOSPITAL_BED
from .minigames import Fishing, Arcade, Cooking, Inventory
from .effects import Ambient
from . import dialogue
from . import activities
from . import lighting
from . import marina
from . import audio
from . import seasons
from . import gifts  # presentes extras e falas de "não gostei"
from . import hospital
from .characters import DOCTOR_KEYS, setup_doctor_spots, doctor_schedule
from .crowd import Crowd, thought
from .cutscenes import Cutscene, SCENES, dating_scene, move_in_scene, date_scene, same_scene
from . import scenery
from . import caprichado
from . import festas      # festas das estações, aniversários e calendário
from . import casal       # vida a dois e ciúmes leves
from . import clima       # tempestade com raios e arco-íris
from . import jogos       # sinuca, dardos e xadrez com o Brainy
from . import poses       # sentada de verdade, comendo, bebendo e lendo
from . import closet      # closet da Letícia (looks)
from . import decor       # decorar a cobertura (móveis)
from . import album       # álbum de fotos do Barry
from . import fundacao    # Fundação Luthor (doações e obras na cidade)
from . import momentos    # momentos entre personagens pela cidade
from . import eventos     # eventos de coração novos e bônus de cada amizade
from . import casamento   # anel, pedido e casamento
from . import historia    # história da Luthor Corp (os tios e o conselho)
from . import animacoes   # regar, bancada, vara de pesca, deitar, colo, aceno, gaivotas, gatinho, modo foto
from .world import CITY_LAYOUT, CITY_DOORS, old_city_xy
from .world import APT_OWNER, APT_NAMES, LOBBY_DOORS, SUB_PARENT, BAYSIDE_HOURS, APT_MIN_HEARTS

SHADOW_KINDS = {"tree": 46, "tree2": 46, "tree3": 46, "palm": 30, "bush": 26, "bush2": 26, "bush3": 26,
                "planter": 30, "lamp": 16, "bench": 34, "statue": 30, "hydrant": 18, "umbrella": 40, "umbrella2": 40,
                "kiosk": 120, "signboard": 20, "plant": 26, "plant_big": 30, "sofa": 120, "armchair": 40,
                "table": 34, "table_it": 34, "arcade": 40, "jukebox": 36, "terminal": 36, "station": 40}
SHADOW_KINDS.update(scenery.SHADOWS)
SHADOW_KINDS.update(caprichado.SHADOWS)
SHADOW_KINDS.update(festas.SHADOWS)

NO_GIFT = ("proposal", "tool", "bait", "seed", "treat")
STOCK_PER_800 = 2.5         # quanto a ação LCORP sobe a cada $800 vendidos em produtos numa noite
# humores dos retratos: os nomes em português também valem nas cutscenes
MOOD_ALIASES = {"feliz": "happy", "sorriso": "smile", "sorrindo": "smile", "apaixonada": "love", "apaixonado": "love",
                "ruim": "bad", "triste": "bad", "brava": "bad", "bravo": "bad", "mad": "bad", "angry": "bad",
                "timido": "shy", "tímido": "shy", "timida": "shy", "tímida": "shy"}

HOTBAR_KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
               pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8, pygame.K_0: 9, pygame.K_MINUS: 10,
               pygame.K_EQUALS: 11}

FLAVOR = {
    "nightstand": "Um abajur, um livro de economia e um porta-retrato da equipe.",
    "fridge": "Água com gás, frutas e... só. CEO não tem tempo de ir ao mercado.",
    "fridge2": "Freezers cheios. Os ingredientes são vendidos no balcão da Bea.",
    "kitchen": "Uma bancada impecável.", "kitchen2": "Uma pia de mármore. Brilhando.",
    "island": "A ilha da cozinha. Ótima para tomar café olhando a cidade.",
    "bookshelf": "Livros de física, estratégia, e um exemplar autografado de 'A Arte da Guerra'.",
    "bookshelf2": "Prateleiras cheias de histórias.", "bookshelf3": "Romances, biografias e mangás.",
    "plant": "Uma planta muito bem cuidada. Alguém rega isso? Ninguém sabe.",
    "plant_big": "Uma planta enorme. Dá até sombra.",
    "sofa": "Um sofá roxo. Perigosamente confortável.", "sofa_grey": "Um sofá de espera.",
    "armchair": "Uma poltrona de leitura.", "coffee_table": "Uma mesinha de centro com revistas da CatCo.",
    "statue": "O monumento da Luthor Corp. Dizem que dá sorte tocar no 'L'.",
    "bench": "Um banco. A vista daqui é ótima.", "bench_l": "Um banco encostado na parede. Lugar bom pra ver o movimento.",
    "bench_r": "Um banco encostado na parede. Lugar bom pra ver o movimento.", "lamp": "Iluminação pública patrocinada pela Luthor Corp.",
    "table": "Uma mesinha.", "table_it": "Toalha xadrez, vela acesa. Romântico.",
    "dining": "Mesa de jantar para dois. Ou para quatro, se a Sam trouxer a Ruby.",
    "reception": "A recepção da Luthor Corp. Tudo extremamente organizado.",
    "desk": "A mesa da CFO. Planilhas em três monitores.", "desk_editor": "A sala do editor-chefe. Cheiro de prazo.",
    "desk_news": "Rascunhos de matérias, post-its e três xícaras de café frias.",
    "cafe_shelf": "Grãos de café de seis países diferentes.", "tree": "Uma árvore.", "tree2": "Uma árvore.",
    "tree3": "Uma árvore frondosa.", "palm": "Um coqueiro. Cuidado com a cabeça.",
    "hedge": "Uma sebe perfeitamente aparada.", "planter": "Um canteiro bem cuidado.",
    "hydrant": "Um hidrante. Os cachorros de National City adoram.",
    "busstop": "Ponto de ônibus. Linha 12: Centro — Orla.", "umbrella": "Um guarda-sol.",
    "umbrella2": "Um guarda-sol.", "lifeguard": "Posto de salva-vidas. 'Nade com responsabilidade.'",
    "boat": "Um barco ancorado.", "wardrobe": "Seu guarda-roupa. 70% roxo.",
    "bathtub": "Uma banheira enorme. Um dia você vai ter tempo pra usar.", "sink": "Pia e espelho.",
    "printer": "A impressora da CatCo. Sempre sem papel.", "cooler": "Bebedouro. Fofocas acontecem aqui.",
    "wine_shelf": "Vinhos italianos. A Vittoria conhece cada um pelo nome.",
    "oven": "Forno a lenha. O cheiro de pizza é inacreditável.", "bottle_shelf": "Garrafas e mais garrafas.",
    "pool": "Uma mesa de sinuca. Ninguém lembra a última vez que alguém acertou uma bola.",
    "jukebox": "A jukebox toca rock dos anos 80 sem parar.", "produce": "Frutas e legumes fresquinhos.",
    "produce2": "Tomates lindos. A Vittoria escolhe um por um.", "flowerstand": "Flores do campo, girassóis e rosas.",
    "shop_counter": "O balcão.", "counter_it": "O balcão da cozinha.", "bar_counter": "O balcão do bar.",
    "chair": "Uma cadeira.", "chair_blue": "Sua cadeira de escritório.", "stool": "Um banquinho.",
    "tv_big": "A TV da sala.", "bed": "Uma cama.",
}


class Game:
    def __init__(self, headless=False):
        audio.pre_init()
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.settings = self.load_settings()
        audio.init(self.settings)
        self.headless = headless
        self.screen = self._make_display(self.settings.get("fullscreen", False))
        try:
            pygame.display.set_icon(art.load_logo(32))
        except Exception:
            pass
        self.clock = pygame.time.Clock()
        self.world = build_world()
        jogos.add_props(self.world)
        self.crowd = Crowd(self.world)
        setup_doctor_spots(self.crowd)
        self.player = Player()
        self.npcs = {k: NPC(k, NPCS[k]) for k in NPC_ORDER}
        self.modals = []
        self.toasts = ui.Toasts()
        self.scene = "title"
        self.title_sel = 0
        self.running = True
        self.fade = 0.0
        self.fade_dir = 0
        self.fade_cb = None
        self.t = 0.0
        self.summary = None
        self.particles = []
        self.cars = []
        self.pigeons = caprichado.Pigeons()
        self._glow = self._make_glow(40 * SCALE)
        self._clouds = self._make_clouds()
        self.ambient = Ambient()
        self.reset_state()

    # ------------------------------------------------------------------
    # Tela / opções
    # ------------------------------------------------------------------
    def load_settings(self):
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"fullscreen": False}

    def save_settings(self):
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f)
        except Exception:
            pass

    def _make_display(self, fullscreen):
        """Janela de 1280x720 ou tela cheia na resolução do monitor.

        O jogo sempre desenha num quadro de 1280x720 (self.screen); present() amplia esse quadro para a
        janela e redesenha os retratos na resolução real, para não ficarem serrilhados.
        """
        try:
            if fullscreen:
                self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                self.window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        except Exception:
            self.window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        if getattr(self, "screen", None) is None or self.screen.get_size() != (SCREEN_W, SCREEN_H):
            self.screen = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self._scaled = None
        return self.screen

    def present(self):
        """Mostra o quadro de 1280x720 na janela; em telas maiores, retratos em alta resolução."""
        win = self.window
        ww, wh = win.get_size()
        if (ww, wh) == (SCREEN_W, SCREEN_H):
            win.blit(self.screen, (0, 0))
            return
        k = min(ww / SCREEN_W, wh / SCREEN_H)
        sw, sh = int(SCREEN_W * k), int(SCREEN_H * k)
        ox, oy = (ww - sw) // 2, (wh - sh) // 2
        if self._scaled is None or self._scaled.get_size() != (sw, sh):
            self._scaled = pygame.Surface((sw, sh)).convert()
            win.fill((0, 0, 0))
        pygame.transform.scale(self.screen, (sw, sh), self._scaled)
        win.blit(self._scaled, (ox, oy))
        for src, r, clip, bg, after in ui.HD:
            # se algo foi desenhado por cima do retrato depois (escurecer, aviso...), fica a versão normal
            if pygame.image.tobytes(self.screen.subsurface(clip), "RGB") != pygame.image.tobytes(after, "RGB"):
                continue
            x0, y0 = ox + round(clip.x * k), oy + round(clip.y * k)
            x1, y1 = ox + round(clip.right * k), oy + round(clip.bottom * k)
            win.blit(pygame.transform.scale(bg, (x1 - x0, y1 - y0)), (x0, y0))
            try:
                img = art.portrait_hd(src, (round(r.w * k), round(r.h * k)))
            except Exception:
                continue
            win.set_clip(pygame.Rect(x0, y0, x1 - x0, y1 - y0))
            win.blit(img, (ox + round(r.x * k), oy + round(r.y * k)))
            win.set_clip(None)

    def toggle_fullscreen(self):
        fs = not self.settings.get("fullscreen", False)
        self.settings["fullscreen"] = fs
        self.save_settings()
        self.screen = self._make_display(fs)
        self.toasts.push("Tela cheia ativada (F11 alterna)" if fs else "Modo janela (F11 alterna)", C_LILAC)

    # ------------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------------
    def reset_state(self):
        self.day, self.quarter, self.year = 1, 1, START_YEAR
        self.minutes = DAY_START
        self.time_acc = 0.0
        self.money = 500
        self.energy = BASE_ENERGY
        self.inventory = [None] * INVENTORY_SIZE
        self.selected = 0
        self.hotbar_label_t = 0.0
        self.stations = [dict(unlocked=i < START_STATIONS, project=None, progress=0, worked=False)
                         for i in range(MAX_STATIONS)]
        self.friendship = {k: 0 for k in NPC_ORDER}
        self.talked, self.gifted = set(), set()
        self.kissed = set()
        self.gift_known = {k: {} for k in NPC_ORDER}
        self.flags, self.events_seen = set(), set()
        self.event_hinted = set()
        self.scene_check_pending = False
        self.stats = dict(launched=0, earned=0, hecate=0, fish=0, arcade_best=0, karaoke_best=0, karaoke_s=0,
                          harvest=0, movies=0, forage=0)
        self.fish_caught, self.aquarium, self.cooked = set(), set(), set()
        self.stock = self.stock_prev = 100.0
        self.shares = 0
        self.shipped = []
        self.request = None
        self.weather, self.weather_tomorrow = "sol", "sol"
        self.map_name = "home"
        self.coffee_today = False
        self.ricci_coffee = False
        self.milany_visit = False
        self.warned = set()
        self.dating = None
        self.proposal = None          # pedido de namoro marcado (buquê dado, cena ainda não tocou)
        self.partner = None
        self.date = None
        self.fishing = None
        self.scenes_seen = []
        self.talk_log = set()
        self.lines_seen = {}
        self.request_nag = set()
        activities.init_state(self)
        marina.init_state(self)
        hospital.init_state(self)
        festas.init_state(self)
        clima.init_state(self)
        jogos.init_state(self)
        closet.init_state(self)
        decor.init_state(self)
        album.init_state(self)
        fundacao.init_state(self)
        momentos.init_state(self)
        casamento.init_state(self)
        historia.init_state(self)
        casal.init_state(self)
        animacoes.init(self)
        if hasattr(self, "crowd"):
            self.crowd.reset_day()

    @property
    def max_energy(self):
        return (BASE_ENERGY + (20 if "jess_energy" in self.flags else 0) + (15 if "book_energy" in self.flags else 0)
                + (15 if "cmh_checkup" in self.flags else 0))

    @property
    def current_map(self):
        return self.world[self.map_name]

    @property
    def weekday(self):
        return (self.day - 1) % 7

    def abs_day(self, year=None, quarter=None, day=None):
        year = self.year if year is None else year
        quarter = self.quarter if quarter is None else quarter
        day = self.day if day is None else day
        return (year - START_YEAR) * 4 * DAYS_PER_QUARTER + (quarter - 1) * DAYS_PER_QUARTER + day

    def date_from_abs(self, n):
        n -= 1
        year = START_YEAR + n // (4 * DAYS_PER_QUARTER)
        n %= 4 * DAYS_PER_QUARTER
        return year, n // DAYS_PER_QUARTER + 1, n % DAYS_PER_QUARTER + 1

    def date_label(self, day=None, quarter=None, year=None, short=False):
        day = day or self.day
        season = seasons.NAMES[seasons.of_quarter(quarter or self.quarter)]
        if short:                                  # no quadro do HUD (sem o ano, para caber)
            return f"{WEEKDAYS[(day - 1) % 7]}, {day} · {season}"
        return f"{WEEKDAYS[(day - 1) % 7]}, {day} · {season} {year or self.year}"

    def apply_season(self):
        """Estação do trimestre atual: cenário, efeitos e roupas (chamada sozinha quando o trimestre muda)."""
        from . import characters
        s = seasons.of_quarter(self.quarter)
        characters.SEASON = s
        seasons.set_season(s, self.world)
        self.player.set_look(closet.player_look())

    @property
    def period(self):
        return "manha" if self.minutes < 12 * 60 else ("tarde" if self.minutes < 18 * 60 else "noite")

    PERIOD_NAMES = {"manha": "manhã", "tarde": "tarde", "noite": "noite"}

    def time_label(self):
        h = (self.minutes // 60) % 24
        return f"{h:02d}:{self.minutes % 60:02d}"

    # ------------------------------------------------------------------
    # Inventário
    # ------------------------------------------------------------------
    def add_item(self, item, n=1):
        for s in self.inventory:
            if s and s[0] == item:
                s[1] += n
                return True
        for i, s in enumerate(self.inventory):
            if s is None:
                self.inventory[i] = [item, n]
                return True
        return False

    def count_item(self, item):
        return sum(s[1] for s in self.inventory if s and s[0] == item)

    def count_fish(self):
        return sum(s[1] for s in self.inventory if s and ITEMS[s[0]]["kind"] == "fish")

    def remove_item(self, item, n=1):
        for i, s in enumerate(self.inventory):
            if s and s[0] == item:
                take = min(n, s[1])
                s[1] -= take
                n -= take
                if s[1] <= 0:
                    self.inventory[i] = None
                if n <= 0:
                    return True
        return n <= 0

    def remove_fish(self, n):
        fishes = sorted([s for s in self.inventory if s and ITEMS[s[0]]["kind"] == "fish"],
                        key=lambda s: ITEMS[s[0]]["value"])
        for s in fishes:
            while n > 0 and s[1] > 0:
                self.remove_item(s[0], 1)
                n -= 1

    def selected_item(self):
        s = self.inventory[self.selected]
        return s[0] if s else None

    def select(self, i):
        self.selected = i % HOTBAR_SIZE
        self.hotbar_label_t = 1.6

    # ------------------------------------------------------------------
    # Fluxo
    # ------------------------------------------------------------------
    def new_game(self):
        self.reset_state()
        for item, n in (("prop_relatorio", 5), ("prop_software", 2), ("expresso", 2), ("rosquinha", 1)):
            self.add_item(item, n)
        self.map_name = "home"
        self.player.place_tile(*HOME_BED, "down")
        self.plan_npcs()
        activities.spawn_forage(self)
        self.scene = "play"
        self.modals = []
        self.cars = []
        self.play_scene("intro", on_end=lambda: self.push(ui.Dialog("Dicas", [
            "O Seu Joca, no píer da orla, ensina a pescar. A Ricci Trattoria fica no calçadão.",
            "Esc abre o menu, I abre a mochila e F11 alterna a tela cheia. Boa sorte, chefe!"])))

    def plan_npcs(self, snap=True):
        festas.sync(self)                   # barracas da festa no dia dela
        for key, npc in self.npcs.items():
            date = None
            if self.date and self.date["npc"] == key and not self.date.get("done"):
                date = (self.date["map"], self.date["x"], self.date["y"], self.date["dir"])
            npc.plan_day(self.weekday, self.weather, partner=(key == self.partner), date=date)
            if key in DOCTOR_KEYS:
                npc.schedule = doctor_schedule(key, self.abs_day())
            festas.override(self, npc)          # dia de festa: todo mundo vai
            casal.override(self, npc)           # aniversário de namoro: ela espera no jantar
            if snap:
                npc.snap_to_schedule(self.minutes)

    def push(self, modal):
        self.modals.append(modal)

    def play_scene(self, key, scene=None, on_end=None, remember=True):
        scene = scene or SCENES[key]
        key = same_scene(key)                       # o pedido de namoro tem um nome só
        if remember and key not in self.scenes_seen:
            self.scenes_seen.append(key)
        self.fishing = None
        cs = Cutscene(self, scene, on_end=on_end)
        album.attach(self, key, cs)                 # a cena vira foto no álbum
        self.push(cs)

    def scene_title(self, key):
        titles = {"intro": "Primeiro dia", "lucy_2": "Lucy: depois do expediente", "lucy_4": "Lucy: um mistério",
                  "lucy_6": "Lucy: o píer à noite", "lucy_8": "Lucy: pôr do sol", "lucy_10": "Lucy: o chafariz",
                  "vittoria_4": "Vittoria: família Ricci",
                  "vittoria_6": "Vittoria: o caderno da nonna", "vittoria_8": "Vittoria: no parque",
                  "vittoria_10": "Vittoria: manhã na praia", "brainy_3": "Brainy: Projeto Hecate",
                  "brainy_5": "Brainy: o drone", "sam_3": "Sam: contratos", "sam_0": "Sam: de volta", "sam_2": "Sam: a agenda",
                  "sam_4": "Sam: contratos", "sam_6": "Sam: presente", "sam_8": "Sam: novos acordos",
                  "ian_0": "Ian: a marina", "ian_2": "Ian: os troféus", "ian_4": "Ian: segredo", 
                  "ian_8": "Ian: a revanche", "jess_5": "Jess: a agenda nova", "milany_0": "Milany: reencontro", "milany_2": "Milany: fim de plantão",
                  "milany_4": "Milany: noite de jogos", "milany_6": "Milany: no hospital", "milany_8": "Milany: a foto",
                  "vittoria_1": "Vittoria: a mesa reservada", "vittoria_2": "Vittoria: o escritório", "namoro_lucy": "Namoro com a Lucy",
                  "lucy_pedido": "Lucy: o pedido de namoro", "vittoria_pedido": "Vittoria: o pedido de namoro",
                  "namoro_vittoria": "Namoro com a Vittoria", "mudanca_lucy": "Lucy se muda",
                  "mudanca_vittoria": "Vittoria se muda", "ian_3": "Ian: o relatório da marina",
                  "ian_6": "Ian: as férias no interior", "barry_3": "Barry: as fotos da semana",
                  "barry_6": "Barry: a foto do grupo", "graca_3": "Dona Graça: a moqueca de Salvador"}
        return (titles.get(key) or eventos.TITLES.get(key) or momentos.TITLES.get(key) or casamento.TITLES.get(key)
                or historia.TITLES.get(key) or key)

    def open_scene_gallery(self):
        seen = []
        for k in self.scenes_seen:
            k = same_scene(k)
            if k not in seen:
                seen.append(k)
        if not seen:
            self.say("Nenhuma cena vista ainda. As cenas aparecem nos eventos de coração e momentos especiais.")
            return

        def pick(i):
            if i < len(seen):
                k = seen[i]
                if k.startswith("namoro_"):
                    sc = dating_scene(k.split("_", 1)[1])
                elif k.startswith("mudanca_"):
                    sc = move_in_scene(k.split("_", 1)[1])
                elif k.startswith("casamento"):
                    sc = casamento.replay_scene(self, k)
                else:
                    sc = SCENES[k]
                cs = Cutscene(self, sc)
                album.attach(self, k, cs)           # rever a cena também tira a foto que faltava
                self.push(cs)
        self.push(ui.Choice("Rever cenas", [self.scene_title(k) for k in seen] + ["Voltar"], pick))

    def portrait_for(self, npc, mood=None, size=None):
        d = npc.data
        mood = MOOD_ALIASES.get(mood, mood)
        # retratos pelo padrão de nomes (nome.png, nome_feliz.png...); se não houver, o campo "portrait"
        fname = art.portrait_file(d.get("portrait_key", npc.key), mood) or d.get("portrait")
        return art.portrait(fname, d["look"], size or art.PORTRAIT_SIZE)

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, v):
        old = getattr(self, "_money", None)
        self._money = v
        if old is not None and v != old and getattr(self, "scene", None) == "play" and not getattr(self, "fade_dir", 0):
            audio.sfx("coin" if v > old else "buy")

    def music_mood(self):
        """Música de acordo com o lugar, a hora e o clima (ou a cena/minigame aberto)."""
        if self.scene != "play":
            return "title"
        mapn, minutes, weather = self.map_name, self.minutes, self.weather
        for mo in reversed(self.modals):
            name = type(mo).__name__
            if name == "Karaoke":
                return "bar"
            if name == "Regatta":
                return "marina"
            if name == "MovieScene":
                return "night"
            if isinstance(mo, Cutscene):
                mapn, minutes, weather = mo.map.name, mo.minutes, mo.weather
                break
        hour = (minutes // 60) % 24
        late = hour >= 22 or hour < 5
        if mapn == "hospital":
            return "hospital"
        if mapn in ("marina", "altomar"):
            return "night" if late else "marina"
        if mapn == "bar" or (mapn == "trattoria" and hour >= 18):
            return "bar"
        if mapn in ("hq", "catco", "ricci"):
            return "work"
        if mapn in ("home", "cafe", "books", "market", "cinema", "trattoria"):
            return "night" if late else "indoor"
        if weather == "chuva":
            return "rain"
        if late:
            return "night"
        return "morning" if hour < 12 else ("afternoon" if hour < 18 else "evening")

    def start_fade(self, cb):
        if self.fade_dir:
            return
        self.fade_dir = 1
        self.fade_cb = cb

    def warp(self, target, x, y, d):
        audio.sfx("door")

        def go():
            self.map_name = target
            self.player.place_tile(x, y, d)
            self.fishing = None
            self.scene_check_pending = True
            if target == "hospital" and "milany_care" in self.flags and not self.milany_visit:
                self.milany_visit = True
                self.energy = min(self.max_energy, self.energy + 20)
                self.toasts.push("A Milany deixou recado na recepção: +20 de energia.", C_GREEN)
        self.start_fade(go)

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.step(dt, pygame.event.get())
            self.present()
            pygame.display.flip()
        pygame.quit()

    def step(self, dt, events):
        self.t += dt
        for ev in events:
            self.handle(ev)
        self.update(dt)
        ui.HD.clear()
        self.draw(self.screen)

    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
            return
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            self.toggle_fullscreen()
            return
        if self.fade_dir:
            return
        if self.modals:
            top = self.modals[-1]
            if ev.type == pygame.KEYDOWN and isinstance(top, (ui.Choice, ui.Shop, ui.ScrollPanel)):
                if ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                    audio.sfx("move")
                elif ev.key in ui.CONFIRM:
                    audio.sfx("confirm")
                elif ev.key in ui.CANCEL:
                    audio.sfx("cancel")
            top.handle(ev)
            self.modals = [m for m in self.modals if not m.done]
            return
        if self.scene == "title":
            self.handle_title(ev)
        elif self.scene == "summary":
            if ev.type == pygame.KEYDOWN and ev.key in ui.CONFIRM:
                self.start_fade(self.begin_day)
        elif self.scene == "play":
            self.handle_play(ev)

    def handle_play(self, ev):
        if animacoes.handle_play(self, ev):          # modo foto e ações em andamento
            return
        if self.fishing:
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_e, pygame.K_SPACE, pygame.K_ESCAPE) or \
                    (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1):
                self.fishing_input(ev)
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_e, pygame.K_SPACE):
                self.interact()
            elif ev.key == pygame.K_f:
                self.consume()
            elif ev.key == pygame.K_ESCAPE:
                self.open_pause()
            elif ev.key in (pygame.K_i, pygame.K_TAB):
                self.push(Inventory(self))
            elif ev.key == pygame.K_o:
                self.open_goals()
            elif ev.key == pygame.K_m:
                from .citymap import CityMap
                self.push(CityMap(self))
            elif ev.key == pygame.K_r:
                self.open_relationships()
            elif ev.key == pygame.K_c:
                audio.sfx("open")
                self.push(festas.Calendar(self))
            elif ev.key in HOTBAR_KEYS:
                self.select(HOTBAR_KEYS[ev.key])
        elif ev.type == pygame.MOUSEWHEEL:
            self.select(self.selected - ev.y)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.interact()
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
            self.consume()

    def update(self, dt):
        if seasons.of_quarter(self.quarter) != seasons.CURRENT["season"] or not seasons.CURRENT.get("applied"):
            self.apply_season()
        walking = (self.scene == "play" and not self.modals and not self.fade_dir and self.player.moving
                   and not self.fishing)
        audio.update(dt, walking)
        if self.fade_dir == 1:
            self.fade = min(1.0, self.fade + dt * 4)
            if self.fade >= 1.0:
                cb, self.fade_cb = self.fade_cb, None
                if cb:
                    cb()
                self.fade_dir = -1
        elif self.fade_dir == -1:
            self.fade = max(0.0, self.fade - dt * 4)
            if self.fade <= 0:
                self.fade_dir = 0
                if self.scene_check_pending:        # chegou num lugar novo: tem cena esperando aqui?
                    self.scene_check_pending = False
                    self.check_scene_events()
        self.toasts.update(dt)
        if self.modals:
            self.modals[-1].update(dt)
            self.modals = [m for m in self.modals if not m.done]
        self.particles = [p for p in self.particles if p.update(dt)]
        self.player.tick(dt)
        self.update_eat_fx(dt)
        self.update_kiss_fx(dt)
        animacoes.update_fx(self, dt)
        if self.scene == "title":
            self.update_cars(dt)
            return
        if self.scene != "play":
            return
        self.hotbar_label_t -= dt
        if not any(isinstance(m, Cutscene) for m in self.modals):
            self.ambient.update(dt, self.current_map, self.camera(self.current_map), self.minutes, self.weather)
            cm = self.current_map
            clima.update(self, dt, cm.outdoor or getattr(cm, "open_air", False))
        if self.modals or self.fade_dir:
            return
        self.time_acc += dt * (0.9 if "jess_agenda" in self.flags and 9 * 60 <= self.minutes < 12 * 60 else 1.0)
        while self.time_acc >= SECONDS_PER_10MIN:
            self.time_acc -= SECONDS_PER_10MIN
            self.minutes += 10
            self.on_tick()
            if self.scene != "play" or self.fade_dir:
                return
        if self.map_name == "city":
            self.update_cars(dt)
        for npc in self.npcs.values():
            npc.update(dt, self.world)
            if getattr(npc, "emote_t", 0) > 0:
                npc.emote_t -= dt
                if npc.emote_t <= 0:
                    npc.emote = None
        activities.update(self, dt)
        self.crowd.update(dt)
        self.pigeons.update(dt, self)
        animacoes.update_world(self, dt)
        if self.fishing:
            self.update_fishing(dt)
            return
        keys = pygame.key.get_pressed()
        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        speed = WALK_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else RUN_SPEED
        if "cardiologia" in self.buffs:
            speed *= 1.1
        if self.energy <= 0:
            speed = WALK_SPEED * 0.7
        if getattr(self, "eat_fx", None) or getattr(self, "kiss_fx", None) or self.act:   # comendo, beijando...
            mx = my = 0
        if self.player.seat:
            if mx or my:
                self.stand_up()
            return
        blockers = [n.rect() for n in self.npcs.values() if n.map == self.map_name]
        blockers += [e.rect() for e in self.crowd.on_map(self.map_name)]
        if self.map_name == "city":
            blockers += [c.rect() for c in self.cars]
        self.player.update(dt, (mx, my), self.current_map, blockers, speed)
        door = self.current_map.doors.get(self.player.tile)
        if door:
            if self.door_open(door):
                self.warp(*door)
            else:                                   # porta trancada: volta um passo
                tx, ty = self.player.tile
                self.player.place_tile(tx, ty + 1, "down")

    def update_cars(self, dt):
        city = self.world["city"]
        for lane_y, d in city.car_lanes:
            if random.random() < dt * 0.22 and sum(1 for c in self.cars if c.lane_y == lane_y) < 4:
                start_ok = all(abs(c.x - (-2.5 * TILE if d > 0 else (city.w + 1.5) * TILE)) > 4 * TILE
                               for c in self.cars if c.lane_y == lane_y)
                if start_ok:
                    self.cars.append(Car(lane_y, d, city.w))
        # quem está a pé na cidade: os carros param antes de chegar nelas
        walkers = [(self.player.x, self.player.y)] if self.map_name == "city" else []
        walkers += [((n.fx + 0.5) * TILE, n.base_y) for n in self.npcs.values() if n.map == "city"]
        walkers += [((e.fx + 0.5) * TILE, e.base_y) for e in self.crowd.on_map("city")]
        self.cars = [c for c in self.cars if c.update(dt, self.cars, walkers)]

    def on_tick(self):
        for npc in self.npcs.values():
            npc.check_schedule(self.minutes)
        self.check_scene_events()
        casal.tick(self)
        self.crowd.tick(self)
        if self.date and not self.date.get("done") and self.minutes == 19 * 60 and "date_warn" not in self.warned:
            self.warned.add("date_warn")
            self.toasts.push(f"Encontro com {NPCS[self.date['npc']]['short']} às 20h: {self.date['desc']}.", C_PINK)
        if self.minutes >= 24 * 60 and "midnight" not in self.warned:
            self.warned.add("midnight")
            self.toasts.push("Meia-noite. Melhor ir para casa dormir...", C_GOLD)
        if self.minutes >= 25 * 60 and "late" not in self.warned:
            self.warned.add("late")
            self.toasts.push("1h da manhã! Você vai desmaiar às 2h.", C_RED)
        if self.minutes >= DAY_END:
            self.end_day(passed_out=True)

    # ------------------------------------------------------------------
    # Interação
    # ------------------------------------------------------------------
    def npc_at(self, tx, ty):
        for npc in self.npcs.values():
            if npc.map == self.map_name and abs(npc.fx - tx) < 0.6 and abs(npc.fy - ty) < 0.6:
                return npc
        return None

    def resolve_target(self):
        fx, fy = self.player.facing_tile()
        npc = self.npc_at(fx, fy)
        if npc:
            return ("npc", npc)
        pet = activities.resolve(self, fx, fy)
        if pet:
            return pet
        cat = animacoes.resolve(self, fx, fy)
        if cat:
            return cat
        st = self.crowd.staff_at(self.map_name, fx, fy)
        if st:
            return ("staff", st)
        ex = self.crowd.extra_at(self.map_name, fx, fy)
        if ex:
            return ("extra", ex)
        m = self.current_map
        obj = m.object_at(fx, fy)
        if obj and obj.kind in COUNTERS:
            dx, dy = DIRS[self.player.dir]
            npc = self.npc_at(fx + dx, fy + dy)
            if npc:
                return ("npc", npc)
        if obj:
            return ("obj", obj)
        b = m.building_at(fx, fy)
        if b and not b.target and (fx, fy) == b.door:
            return ("bld", b)
        sel = self.selected_item()
        if sel in ("vara", "vara_fibra") and m.tile_at(fx, fy) in WATER_TILES:
            return ("water", (fx, fy))
        return None

    def target_label(self, target):
        kind, t = target
        if self.player.seat and kind != "npc":
            return "Levantar"
        if kind == "water":
            return "Pescar"
        if kind == "pet":
            return activities.pet_label(self, t)
        if kind == "gato":
            return "Fazer carinho no gatinho"
        if kind == "staff":
            return t.label
        if kind == "extra":
            return "Observar"
        if kind == "bld":
            return t.name
        if kind == "npc":
            sel = self.selected_item()
            short = t.data["short"]
            if t.data.get("shop") and t.data.get("shop_map") == self.map_name:
                return f"Loja / falar com {short}"
            if sel and ITEMS[sel]["kind"] not in NO_GIFT and t.key not in self.gifted:
                return f"Falar / presentear {short}"
            if self.date and self.date["npc"] == t.key and not self.date.get("done") and self.minutes >= 1150:
                return f"Encontro com {short}"
            if f"{t.key}|{self.period}" in self.talk_log:
                return f"{short} (já conversaram)"
            return f"Falar com {short}"
        k = t.kind
        if k in self.SEATS:
            return "Sentar"
        lab = (festas.object_label(self, t) or jogos.object_label(self, t) or closet.object_label(self, t)
               or decor.object_label(self, t) or fundacao.object_label(self, t) or historia.object_label(self, t)
               or activities.object_label(self, t) or hospital.object_label(self, t)
               or marina.target_label(self, t))
        if lab:
            return lab
        if k == "station":
            st = self.stations[t.data]
            if not st["unlocked"]:
                return "Bancada bloqueada"
            if st["project"] is None:
                return "Iniciar projeto" if (self.selected_item() or "").startswith("prop_") else "Bancada livre"
            p = PROJECTS[st["project"]]
            if st["progress"] >= self.project_days(st["project"]):
                return f"Lançar {p['name']}!"
            return "Já trabalhou hoje" if st["worked"] else f"Trabalhar ({p['name']})"
        labels = {"bed2": "Dormir", "bed": "Dormir", "tv": "Assistir ao jornal", "tv_big": "Assistir ao jornal",
                  "ceo_desk": "Computador", "desk_home": "Computador", "terminal": "Terminal P&D",
                  "shipbox": "Mesa de Contratos", "shipbox_pier": "Caixa de coleta", "stove": "Cozinhar",
                  "aquarium": "Aquário", "arcade": "Jogar Meteoro ($10)", "coffee": "Cafeteira",
                  "kiosk": "Barraca do Joca" if t.data == "bait" else "Banca de jornal", "signboard": "Ler placa"}
        return labels.get(k, "Olhar")

    def interact(self):
        if self.player.seat:
            target = self.resolve_target()
            if target and target[0] == "npc":
                self.talk_to(target[1])
            else:
                self.stand_up()
            return
        target = self.resolve_target()
        if not target:
            return
        kind, t = target
        if kind == "npc":
            self.talk_to(t)
        elif kind == "pet":
            activities.pet_interact(self, t)
        elif kind == "gato":
            animacoes.pet_stray(self, t)
        elif kind == "extra":
            self.toasts.push(thought(t), C_MUTED)
        elif kind == "obj":
            self.use_object(t)
        elif kind == "bld":
            self.say(f"{t.name}: fechado ao público.")
        elif kind == "water":
            self.try_fish(t)

    def say(self, msg, speaker=""):
        self.push(ui.Dialog(speaker or "", [msg]))

    APT_LOOK = {"bed2": "A cama de {n}, arrumadinha. Melhor não deitar na casa dos outros.",
                "bed_lucy": "A cama da Lucy: colcha de flanela xadrez e um bloquinho de anotações no travesseiro.",
                "bed_vittoria": "Cabeceira estofada e lençóis de linho italiano. Nem uma ruga na colcha.",
                "bed_sam": "A cama da Sam, feita com capricho. Tem uma agenda da Luthor Corp na mesinha.",
                "bed_brainy": "Uma cama de solteiro com estampa de circuitos. Tem um livro de física no travesseiro.",
                "bed_jess": "Colcha florida e um ursinho de pelúcia. A Jess jura que ele é decoração.",
                "bed_nia": "Colcha cheia de estrelas e uma lua. Tem um caderno de sonhos na mesinha.",
                "bed_barry": "Colcha vermelha com um raio amarelo. Bem a cara do Barry.",
                "bed_ian": "Listras de marinheiro e uma âncora na cabeceira. Cheiro de maresia.",
                "bed_milany": "A cama da Milany, colcha lilás e um bipe do hospital do lado do travesseiro.",
                "hbed": "A cama de {n}. Tem um livro aberto em cima do travesseiro.",
                "kitchen": "A cozinha de {n}. Cheiro de café recém-passado.",
                "stove": "O fogão de {n}. Melhor não cozinhar na casa dos outros sem pedir.",
                "island": "A ilha da cozinha de {n}, com uma fruteira cheia.",
                "dining": "A mesinha de jantar de {n}. Tem um vaso com uma flor só.",
                "kitchen2": "Uma cozinha pequena e organizada. Tem uma caneca com o nome de {n}.",
                "fridge": "A geladeira de {n}, cheia de ímãs e bilhetinhos.",
                "tv_big": "A TV de {n}. Pausada no meio de um filme.",
                "desk_editor": "A mesa de {n}, cheia de anotações de matérias.",
                "desk_home": "A mesa de trabalho de {n}. Melhor não mexer nos papéis.",
                "desk": "A mesa de {n}, coberta de cálculos e circuitos.",
                "terminal": "O computador de {n}. Tem uma senha de 32 caracteres.",
                "monitor": "Um monitor cheio de gráficos que só {n} entende.",
                "bookshelf": "Os livros de {n}. Dá para saber muito sobre alguém pela estante.",
                "bookshelf2": "Os livros de {n}. Dá para saber muito sobre alguém pela estante.",
                "bookshelf3": "Os livros de {n}. Dá para saber muito sobre alguém pela estante.",
                "wine_shelf": "Os vinhos de {n}. Todos italianos, claro.",
                "wardrobe": "O armário de {n}. Fechado, por educação.",
                "trophy": "Troféus de regata de {n}. Muitos.",
                "helm": "Um timão antigo, lembrança de {n} do primeiro barco."}

    # --- Sentar -----------------------------------------------------------
    # altura do assento em pixels de arte (o corpo desce até ali) — as poses ficam em poses.py
    SEATS = poses.SEAT_LIFT
    TABLE_WORDS = ("table", "desk", "dining", "island", "counter", "bar", "kitchen")

    def seat_dir(self, o, tx, ty):
        """Para onde ela fica virada: para a mesa ao lado; bancos de parede, para o lado deles; senão, para baixo."""
        if o.kind == "bench_l":
            return "left"
        if o.kind == "bench_r":
            return "right"
        m = self.current_map
        if o.kind in ("chair", "chair_blue", "hchair", "stool"):
            for d, (dx, dy) in (("up", (0, -1)), ("right", (1, 0)), ("left", (-1, 0)), ("down", (0, 1))):
                n = m.object_at(tx + dx, ty + dy)
                if n and n is not o and n.kind not in self.SEATS and any(w in n.kind for w in self.TABLE_WORDS):
                    return d
        return "down"

    def sit(self, o):
        fx, _ = self.player.facing_tile()
        tx = min(max(fx, o.x), o.x + o.w - 1)            # sofá: senta no lugar que está na frente dela
        ty = o.y + o.h - 1
        if any(n.map == self.map_name and n.tile == (tx, ty) for n in self.npcs.values()):
            self.toasts.push("Esse lugar está ocupado.", C_MUTED)
            return
        back = (self.player.x, self.player.y, self.player.dir)
        self.player.place_tile(tx, ty, self.seat_dir(o, tx, ty))
        self.player.moving = False
        # t/off: ela desliza de onde estava até o assento (entities.Player.draw)
        self.player.seat = dict(lift=self.SEATS[o.kind], sort=o.base_y + 1, back=back, t=0.0,
                                off=(back[0] - self.player.x, back[1] - self.player.y))
        self.player.swinging, self.player.swing_t = 0.0, random.uniform(4, 8)

    def stand_up(self):
        st = self.player.seat
        if not st:
            return
        sx, sy = self.player.x, self.player.y
        self.player.seat = None
        self.player.x, self.player.y, _ = st["back"]
        self.player.rise = dict(t=0.0, off=(sx - self.player.x, sy - self.player.y))

    def use_object(self, o):
        k = o.kind
        if (festas.use_object(self, o) or jogos.use_object(self, o) or closet.use_object(self, o)
                or decor.use_object(self, o) or fundacao.use_object(self, o) or historia.use_object(self, o)):
            return
        if k in self.SEATS:                         # dá para sentar até na casa dos outros
            self.sit(o)
            return
        owner = APT_OWNER.get(self.map_name)
        if owner:                                   # na casa dos outros não se usa nada, só se olha
            n = APT_NAMES[owner]
            self.say(self.APT_LOOK.get(k, "Coisas de {n}. Melhor não mexer.").format(n=n))
            return
        if activities.use_object(self, o) or hospital.use_object(self, o) or marina.use_object(self, o):
            return
        if k == "station":
            self.use_station(o.data)
        elif k in ("bed2", "bed"):
            self.push(ui.Choice("Dormir e encerrar o dia? (o jogo é salvo)", ["Dormir", "Ainda não"],
                                lambda i, o=o: animacoes.go_to_bed(self, o) if i == 0 else None))
        elif k in ("tv", "tv_big"):
            self.watch_tv()
        elif k in ("ceo_desk", "desk_home"):
            self.open_computer()
        elif k == "terminal":
            self.open_terminal()
        elif k in ("shipbox", "shipbox_pier"):
            self.use_shipbox(k == "shipbox_pier")
        elif k == "stove":
            self.push(Cooking(self))
        elif k == "aquarium":
            self.use_aquarium()
        elif k == "arcade":
            self.play_arcade()
        elif k == "kiosk":
            if o.data == "bait":
                joca = self.npcs["joca"]
                if joca.map == "city" and self.minutes < 18 * 60:
                    self.open_shop("bait")
                else:
                    self.say("Barraca fechada. 'Volto amanhã às 6h! — Joca'")
            else:
                self.say("Banca de jornal. Manchete da CatCo: " + random.choice(NEWS))
        elif k == "signboard":
            self.say("Píer de National City. Pesca liberada! Lago do parque: peixes de água doce. "
                     "Mar: peixes maiores. A caixa de coleta vende tudo à noite.")
        elif k == "coffee":
            if self.map_name != "hq":
                self.say("Uma máquina de café profissional.")
            elif "coffee_machine" in self.flags:
                if self.coffee_today:
                    self.toasts.push("Você já pegou seu café de hoje.", C_MUTED)
                elif self.add_item("expresso"):
                    self.coffee_today = True
                    self.toasts.push("+1 Expresso da cafeteira executiva", C_GREEN, "expresso")
            else:
                self.say("Uma cafeteira velha e quebrada. Dá para comprar uma cafeteira executiva no Terminal P&D.")
        elif k in ("tv_wall",):
            self.say("Telas com as manchetes da CatCo.")
        else:
            self.say(FLAVOR.get(k, "Nada de especial aqui."))

    def consume(self):
        item = self.selected_item()
        if not item or getattr(self, "eat_fx", None):      # um de cada vez
            return
        it = ITEMS[item]
        if it["kind"] == "book":
            b = BOOKS[item]
            if b["flag"] in self.flags:
                self.toasts.push("Você já leu este livro.", C_MUTED)
                return
            self.remove_item(item)
            self.flags.add(b["flag"])
            self.toasts.push(f"Leu '{b['name']}': {b['effect']}", C_GOLD, item)
            self.start_eat_fx(item, "read")
            return
        if it["kind"] not in ("food", "dish", "crop", "forage") or not it.get("energy"):
            self.toasts.push(f"{it['name']} não é comestível.", C_MUTED)
            return
        if self.energy >= self.max_energy:
            self.toasts.push("Sua energia já está cheia.", C_MUTED)
            return
        self.remove_item(item)
        gain = int(it["energy"] * (1.3 if "gastro" in self.buffs else 1) * eventos.food_mult(self, item))
        self.energy = min(self.max_energy, self.energy + gain)
        self.toasts.push(f"{it['name']}: +{gain} de energia", C_GREEN, item)
        self.start_eat_fx(item, "drink" if it["icon"] in DRINK_ICONS else "eat")

    # --- animação de comer / beber / ler ---------------------------------------
    # comer: mostra o prato nas mãos, três mordidas (leva à boca, "nhac", mastiga) e carinha feliz
    # beber: leva o copo à boca e vai inclinando (dois goles, olhos fechados); ler: livro aberto, duas páginas viram
    EAT_DUR = {"eat": 1.75, "drink": 1.6, "read": 1.85}
    EAT_BEATS = {"eat": (0.45, 0.85, 1.25), "drink": (0.6, 0.95), "read": (0.5, 1.0)}
    EAT_HAPPY = {"eat": 1.31, "drink": 1.15, "read": 1.4}        # começo da carinha feliz (o item some)
    EAT_EMOTE = {"eat": "feliz", "drink": "feliz", "read": "estrela"}

    def door_open(self, door):
        """Portaria dos Apartamentos Bayside (7h às 23h) e apartamentos (dono em casa + 2 corações)."""
        target = door[0]
        if target == "bayside" and self.map_name == "city":
            a, b = BAYSIDE_HOURS
            if not (a <= self.minutes < b):
                audio.sfx("cancel")
                self.say("A portaria dos Apartamentos Bayside está fechada. Abre às 7h e fecha às 23h.")
                return False
            return True
        owner = APT_OWNER.get(target)
        if not owner:
            return True
        name = APT_NAMES[owner]
        npc = self.npcs.get(owner)
        if self.partner == owner:
            audio.sfx("cancel")
            self.say(f"O apartamento está vazio: {name} mora com você na cobertura agora.")
            return False
        invited = any(ev.get("scene") and SCENES[ev["scene"]]["map"] == target and
                      self.scene_place(ev["scene"])[1] <= self.minutes <= self.scene_place(ev["scene"])[2]
                      for _k, _h, ev in self.pending_scene_events())
        if invited:                                 # evento marcado aqui: a pessoa te espera para a cena
            return True
        if not npc or npc.map != target:
            audio.sfx("cancel")
            self.say(f"Você bate na porta... ninguém atende. {name} não está em casa agora.")
            return False
        if self.hearts(owner) < APT_MIN_HEARTS and self.dating != owner:
            audio.sfx("cancel")
            self.say(f"{name} entreabre a porta: 'Oi, Letícia! Hoje não dá, a casa está uma bagunça.' "
                     f"(É preciso ter {APT_MIN_HEARTS} corações para entrar.)")
            return False
        return True

    def draw_apt_plates(self, surf, cam):
        """Plaquinhas com o nome de cada morador em cima das portas do corredor (e a do elevador da cobertura)."""
        for apt, (x, y) in LOBBY_DOORS.items():
            if SUB_PARENT[apt] != self.map_name:
                continue
            name = "Cobertura" if apt == "home" else APT_NAMES[APT_OWNER[apt]]
            img = ui.font(12, True).render(name, False, (250, 240, 210))
            cx = int((x + 0.5) * TILE - cam[0])
            cy = int(y * TILE + 3 - cam[1])
            r = pygame.Rect(0, 0, img.get_width() + 6, img.get_height() + 2)
            r.midtop = (cx, cy)
            pygame.draw.rect(surf, (120, 92, 52), r.inflate(2, 2), border_radius=2)
            pygame.draw.rect(surf, (60, 44, 30), r, border_radius=2)
            surf.blit(img, (r.x + 3, r.y + 1))

    def start_eat_fx(self, item, kind):
        """A Letícia come/bebe/lê com o item nas mãos (poses.py); sentada, continua virada para a mesa."""
        self.eat_fx = dict(item=item, kind=kind, t=0.0, done=set(), happy=False)
        if not self.player.seat:
            self.player.dir = "down"
        self.player.swinging = 0.0
        self.player.pose = self._eat_pose(self.eat_fx)

    def _eat_pose(self, fx):
        """Pose da Letícia neste instante: braços, rosto, piscada, balanço e onde está o item ("hold"/"mouth")."""
        t, kind = fx["t"], fx["kind"]
        if t >= self.EAT_HAPPY[kind]:
            return dict(arms=None, face="happy", blink=False, bob=0, item=None)
        if kind == "eat":
            for b in self.EAT_BEATS["eat"]:
                if b - 0.14 <= t < b + 0.06:            # levando à boca e mordendo
                    return dict(arms="mouth", face="open" if t < b else None, blink=False,
                                bob=SCALE // 2 if t >= b else 0, item="mouth")
            chew = int(t * 10) % 2 if t > self.EAT_BEATS["eat"][0] else 0       # mastigando
            return dict(arms="hold", face=None, blink=False, bob=chew, item="hold")
        if kind == "drink":
            if t < 0.28:
                return dict(arms="hold", face=None, blink=False, bob=0, item="hold")
            return dict(arms="mouth", face=None, blink=t > 0.42, bob=0, item="mouth")
        return dict(arms="hold", face="read", blink=False, bob=0, item="hold")     # lendo

    def update_eat_fx(self, dt):
        pe = getattr(self, "player_emote", None)
        if pe:
            pe["t"] += dt
            if pe["t"] >= 1.1:
                self.player_emote = None
        fx = getattr(self, "eat_fx", None)
        if not fx:
            return
        fx["t"] += dt
        kind = fx["kind"]
        beats = self.EAT_BEATS[kind]
        for i, b in enumerate(beats):
            if fx["t"] >= b and i not in fx["done"]:
                fx["done"].add(i)
                if kind == "eat":
                    audio.sfx("eat")
                    self._crumbs(fx, 9 if i == len(beats) - 1 else 5)
                elif kind == "drink":
                    audio.sfx("gulp")
                else:
                    audio.sfx("page")
        if fx["t"] >= self.EAT_HAPPY[kind] and not fx["happy"]:
            fx["happy"] = True
            audio.sfx("reward" if kind == "read" else "yum")
            self.player_emote = dict(kind=self.EAT_EMOTE[kind], t=0.0)
        if fx["t"] >= self.EAT_DUR[kind]:
            self.eat_fx = None
            self.player.pose = None
            return
        self.player.pose = self._eat_pose(fx)

    def _item_spot(self, where):
        """Onde está a mão com o item (coordenadas do mundo), de acordo com a pose."""
        pl = self.player
        top = pl.img_top
        if top is None:
            return pl.x, pl.y - 26 * SCALE
        ax, ay = poses.anchor(pl.dir, where, pl.look)
        return top[0] + ax * SCALE, top[1] + ay * SCALE

    def _crumbs(self, fx, n):
        x, y = self._item_spot("mouth")
        col = mix_rgb(ITEMS[fx["item"]]["color"], (236, 204, 150), 0.55)   # farelos claros
        for _ in range(n):
            p = Particle(x + random.uniform(-5, 5), y + random.uniform(0, 6), col, size=3)
            p.vx *= 0.35
            p.vy = random.uniform(-50, 10)
            p.life *= 0.7
            self.particles.append(p)

    def draw_eat_fx(self, surf, cam):
        pe = getattr(self, "player_emote", None)
        pl = self.player
        if pe and pl.img_top:                       # emoji de "que delícia!" / "aprendi!" acima da cabeça
            from .cutscenes import draw_emote
            k = min(1.0, pe["t"] / 0.12) * (1 - max(0.0, pe["t"] - 0.8) / 0.3)
            draw_emote(surf, int(pl.x - cam[0]), int(pl.img_top[1] - cam[1]) - 2, pe["kind"], max(0.0, k))
        fx = getattr(self, "eat_fx", None)
        if not fx or not pl.pose or not pl.pose.get("item"):
            return
        t, kind, where = fx["t"], fx["kind"], pl.pose["item"]
        view = poses.VIEW[pl.dir]
        x, y = self._item_spot(where)
        x, y = x - cam[0], y - cam[1]
        if view == "back":                          # de costas: o item aparece acima da cabeça
            y += math.sin(t * 8) * 2
        if t < 0.12 and where == "hold":            # o item sobe das mãos
            y += (1 - t / 0.12) * 3 * SCALE
        if kind == "read" and view != "back":
            flip = None
            for b in self.EAT_BEATS["read"]:
                if b <= t < b + 0.24:
                    flip = (t - b) / 0.24
            self._draw_book(surf, int(x), int(y), ITEMS[fx["item"]]["color"], view, pl.dir, flip)
            return
        if kind == "drink" and view != "back":      # copo pequeno na mão (o ícone grande tapava o rosto)
            ang = min(35.0, max(0.0, (t - 0.28) / 0.5 * 35.0)) if where == "mouth" else 0.0
            top = pl.img_top
            if top is None:
                return
            rise = (1 - t / 0.12) * 3 * SCALE if (t < 0.12 and where == "hold") else 0
            draw_drink(surf, top[0] - cam[0], top[1] - cam[1] + rise, pl.look, pl.dir, fx["item"], where, ang)
            return
        icon = art.item_icon(fx["item"], 1).copy()
        w, h = icon.get_size()
        if kind == "eat":                           # cada mordida tira um pedaço (arco transparente no canto)
            bites = sum(1 for b in self.EAT_BEATS["eat"] if t >= b)
            for i in range(bites):
                pygame.draw.circle(icon, (0, 0, 0, 0), (w - 2 - i * (w // 4), 2 + i * 3), w // 4 + 1)
        elif kind == "drink" and where == "mouth":  # o copo vai inclinando enquanto ela bebe
            ang = min(55.0, (t - 0.28) / 0.5 * 55.0)
            icon = pygame.transform.rotate(icon, ang if pl.dir == "left" else -ang)
        surf.blit(icon, (int(x - icon.get_width() / 2), int(y - icon.get_height() / 2)))

    def _draw_book(self, surf, cx, cy, color, view, d, flip):
        """Livro aberto nas mãos. De frente aparece a capa (ela lê do outro lado); de lado, as páginas.

        flip: 0..1 enquanto uma página vira (passa por cima do livro, da direita para a esquerda)."""
        S = SCALE
        dark = shade_rgb(color, 0.62)
        paper, line = (246, 238, 214), (196, 184, 160)
        if view == "front":
            w, h = 10, 6
            x0, y0 = cx - w * S // 2, cy - h * S // 2
            pygame.draw.rect(surf, paper, (x0 + S, y0 - S, (w - 2) * S, S))              # beirada das folhas
            pygame.draw.rect(surf, dark, (x0, y0, w * S, h * S))                         # capas
            pygame.draw.rect(surf, color, (x0 + S, y0 + S, 3 * S, (h - 2) * S))
            pygame.draw.rect(surf, color, (x0 + 6 * S, y0 + S, 3 * S, (h - 2) * S))
            pygame.draw.rect(surf, (236, 200, 96), (x0 + 6 * S, y0 + 2 * S, 3 * S, S))    # título dourado
            pygame.draw.rect(surf, shade_rgb(color, 0.45), (x0 + 4 * S, y0, 2 * S, h * S))   # lombada
            if flip is not None:                     # a folha vira por cima
                px = x0 + int((w - 2) * S * (1 - flip))
                ph = int(math.sin(math.pi * flip) * 3 * S) + S
                pygame.draw.rect(surf, paper, (px, y0 - ph, 2 * S, ph))
                pygame.draw.rect(surf, line, (px, y0 - ph, 2 * S, S))
            return
        # de lado: livro em pé na frente dela, com as páginas viradas para o rosto
        w, h = 4, 7
        x0, y0 = cx - w * S // 2, cy - h * S // 2
        pygame.draw.rect(surf, dark, (x0, y0, w * S, h * S))
        inner = x0 + (0 if d == "right" else 2 * S)
        pygame.draw.rect(surf, paper, (inner, y0 + S, 2 * S, (h - 2) * S))
        for k in (2, 4):
            pygame.draw.rect(surf, line, (inner, y0 + k * S, 2 * S, S // 2 or 1))
        pygame.draw.rect(surf, color, (x0 + (2 * S if d == "right" else 0), y0 + S, 2 * S, (h - 2) * S))
        if flip is not None:
            pygame.draw.rect(surf, paper, (inner - S if d == "right" else inner + 2 * S, y0 + S - int(math.sin(
                math.pi * flip) * 2 * S), S, (h - 2) * S))

    # --- Laboratório ---------------------------------------------------
    def use_station(self, idx):
        st = self.stations[idx]
        if not st["unlocked"]:
            self.toasts.push("Bancada bloqueada. Compre a expansão no Terminal P&D.", C_MUTED)
            return
        if st["project"] is None:
            item = self.selected_item()
            if item and ITEMS[item]["kind"] == "proposal":
                p = ITEMS[item]["project"]
                self.remove_item(item)
                st.update(project=p, progress=0, worked=False)
                self.toasts.push(f"{PROJECTS[p]['name']} iniciado!", C_LILAC, item)
                self.burst_at(STATION_SLOTS[idx], PROJECTS[p]["color"])
            else:
                self.toasts.push("Bancada livre: selecione uma proposta na barra e aperte E.", C_MUTED)
            return
        p = PROJECTS[st["project"]]
        if st["progress"] >= self.project_days(st["project"]):
            if self.add_item(st["project"]):
                self.stats["launched"] += 1
                if st["project"] == "hecate":
                    self.stats["hecate"] += 1
                self.toasts.push(f"Lançado: {ITEMS[st['project']]['name']}!", C_GREEN, st["project"])
                self.burst_at(STATION_SLOTS[idx], (255, 230, 120))
                st.update(project=None, progress=0, worked=False)
            else:
                self.toasts.push("Mochila cheia!", C_RED)
            return
        if st["worked"]:
            self.toasts.push(f"Você já trabalhou no {p['name']} hoje.", C_MUTED)
            return
        if self.energy < WORK_ENERGY:
            self.toasts.push("Você está exausta demais. Coma algo ou vá dormir.", C_RED)
            return
        cost = WORK_ENERGY
        self.energy -= cost // 2 if "neurologia" in self.buffs else cost
        st["worked"] = True
        left = self.project_days(st["project"]) - st["progress"] - 1
        msg = ("fica pronto amanhã!" if left == 0 else
               "falta 1 dia depois de hoje" if left == 1 else f"faltam {left} dias depois de hoje")
        self.toasts.push(f"Trabalhou no {p['name']}: {msg}", C_TEXT)
        self.burst_at(STATION_SLOTS[idx], p["color"])
        animacoes.start_act(self, "bancada", tile=STATION_SLOTS[idx])

    def burst_at(self, tile, color):
        sx, sy = tile
        for _ in range(14):
            self.particles.append(Particle((sx + 0.5) * TILE, sy * TILE + 10, color))

    def use_shipbox(self, pier=False):
        item = self.selected_item()
        total = sum(n for _, n in self.shipped)
        name = "Caixa de coleta" if pier else "Mesa de Contratos"
        if not item:
            self.say(f"{name}: selecione um produto, peixe ou prato na barra e aperte E. Hoje já são {total} "
                     f"item(ns) para vender à noite.")
            return
        if ITEMS[item]["kind"] not in SELLABLE:
            self.toasts.push("Só produtos, peixes e pratos podem ser vendidos aqui.", C_MUTED)
            return
        n = self.inventory[self.selected][1]
        self.inventory[self.selected] = None
        self.shipped.append([item, n])
        value = self.sell_value(item) * n
        self.toasts.push(f"Venda: {n}x {ITEMS[item]['name']} (+${value} esta noite)", C_GOLD, item)

    def project_days(self, key):
        """Dias de um projeto (com as bancadas do Brainy, 1 dia a menos)."""
        return max(1, PROJECTS[key]["days"] - (1 if "brainy_fast" in self.flags else 0))

    def sell_value(self, item):
        v = ITEMS[item].get("value", 0)
        bonus = (0.10 if "sam_bonus" in self.flags else 0) + (0.25 if "sam_bonus2" in self.flags else 0)
        if bonus:                                   # contratos renegociados pela Sam (eventos de 4 e 8 corações)
            v = int(v * (1 + bonus))
        if "ian_deepfish" in self.flags and item in FISH and FISH[item].get("where") == "deep":
            v = int(v * 1.15)
        if "luthor_livre" in self.flags:            # fim da história: a Luthor Corp sem os tios
            v = int(v * historia.sell_mult(self, item))
        if ITEMS[item]["kind"] == "fish" and fundacao.fish_mult(self) > 1:     # Peixaria do Píer
            v = int(v * fundacao.fish_mult(self))
        if "endocrino" in self.buffs and ITEMS[item]["kind"] == "dish":
            v = int(v * 1.2)
        return v

    # --- Pesca ---------------------------------------------------------
    def try_fish(self, tile):
        where = WATER_TILES.get(self.current_map.tile_at(*tile))
        if not where:
            return
        cost = 0 if "ortopedia" in self.buffs else FISH_ENERGY
        if self.energy < cost:
            self.toasts.push("Sem energia para pescar.", C_RED)
            return
        self.energy -= cost
        bait = self.count_item("isca") > 0
        if bait:
            self.remove_item("isca")
        wait = random.uniform(2.0, 6.5) * (0.4 if bait else 1.0)
        self.fishing = dict(phase="wait", t=wait, where=where, tile=tile, bait=bait)

    def fishing_input(self, ev):
        f = self.fishing
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.fishing = None
            return
        if f["phase"] == "bite":
            fish = self.choose_fish(f["where"])
            self.fishing = None
            if fish in JUNK:
                self.add_item(fish)
                self.toasts.push(f"Pescou... {ITEMS[fish]['name']}. Pelo menos limpou a água.", C_MUTED, fish)
                animacoes.start_act(self, "pegou", item=fish)
                return
            rod = self.selected_item()
            bar = 132 if rod == "vara_fibra" else 92
            if "book_fish" in self.flags:
                bar = int(bar * 1.3)
            audio.sfx("splash")
            self.reel = dict(tile=f["tile"])           # a vara fica envergada e a carretilha gira no minigame
            self.push(Fishing(fish, bar, lambda res, fish=fish: self.fish_result(fish, res)))
        else:
            self.fishing = None
            self.toasts.push("Você recolheu a linha.", C_MUTED)

    def update_fishing(self, dt):
        f = self.fishing
        f["t"] -= dt
        if f["phase"] == "wait" and f["t"] <= 0:
            audio.sfx("bite")
            f["phase"] = "bite"
            f["t"] = 1.1
        elif f["phase"] == "bite" and f["t"] <= 0:
            self.fishing = None
            self.toasts.push("O peixe mordeu e fugiu! Aperte E mais rápido quando aparecer o '!'.", C_MUTED)

    def choose_fish(self, where):
        if random.random() < 0.07:
            return random.choice(list(JUNK))
        cands, weights = [], []
        for k, f in FISH.items():
            if f["where"] != where or self.quarter not in f["quarters"]:
                continue
            a, b = f["hours"]
            if not (a <= self.minutes <= b):
                continue
            if f.get("weather") and f["weather"] != self.weather:
                continue
            w = 100.0 / (f["value"] ** 0.75)
            if f.get("legendary"):
                w *= 0.25
            if "joca_spot" in self.flags and f["value"] >= 100:
                w *= 2
            cands.append(k)
            weights.append(w)
        if not cands:
            return "sardinha" if where == "sea" else "tilapia"
        return random.choices(cands, weights)[0]

    def fish_result(self, fish, res):
        audio.sfx("catch" if res == "win" else "lose")
        got = False
        if res == "win":
            if self.add_item(fish):
                got = True
                first = fish not in self.fish_caught
                self.fish_caught.add(fish)
                self.stats["fish"] += 1
                extra = " (nova espécie!)" if first else ""
                self.toasts.push(f"Pescou: {ITEMS[fish]['name']}{extra}", C_GREEN, fish)
                if first:
                    eventos.new_fish(self, fish)            # fotos do Barry para a CatCo
                if FISH[fish].get("legendary"):
                    self.toasts.push("LENDÁRIO! O Joca não vai acreditar.", C_GOLD)
            else:
                self.toasts.push("Mochila cheia! O peixe voltou pro mar.", C_RED)
        else:
            self.toasts.push("O peixe escapou...", C_MUTED)
        animacoes.fish_done(self, fish, "win" if got else "lose")

    # --- Aquário, cozinha, fliperama ----------------------------------------
    def use_aquarium(self):
        item = self.selected_item()
        if item and ITEMS[item]["kind"] == "fish" and item not in self.aquarium:
            def pick(i):
                if i == 0:
                    self.remove_item(item)
                    self.aquarium.add(item)
                    self.toasts.push(f"{ITEMS[item]['name']} agora mora no aquário! ({len(self.aquarium)}/{len(FISH)})",
                                     C_LILAC, item)
            self.push(ui.Choice(f"Colocar {ITEMS[item]['name']} no aquário?", ["Sim", "Não"], pick))
            return

        def draw(surf, rect):
            ui.text(surf, f"Espécies no aquário: {len(self.aquarium)}/{len(FISH)}   ·   já pescadas: "
                          f"{len(self.fish_caught)}/{len(FISH)}", (rect.x + 30, rect.y + 64), 18, C_MUTED)
            for i, (k, f) in enumerate(FISH.items()):
                col, row = i % 2, i // 2
                x, y = rect.x + 30 + col * 340, rect.y + 100 + row * 50
                have = k in self.aquarium
                if have or k in self.fish_caught:
                    surf.blit(art.item_icon(k, 2), (x, y))
                else:
                    pygame.draw.rect(surf, (40, 30, 56), (x, y, 32, 32), border_radius=6)
                    ui.text(surf, "?", (x + 16, y + 4), 20, C_MUTED, center=True)
                name = f["name"] if (have or k in self.fish_caught) else "???"
                where = "mar" if f["where"] == "sea" else "lago"
                ui.text(surf, name, (x + 42, y), 17, C_GREEN if have else C_TEXT, bold=have)
                ui.text(surf, f"{where} · " + ("o ano todo" if len(f['quarters']) >= 4 else ', '.join(seasons.NAMES[seasons.of_quarter(q)] for q in f['quarters'])) + (" · chuva" if f.get("weather") else ""),
                        (x + 42, y + 20), 13, C_MUTED)
        self.push(ui.InfoPanel("Aquário", draw))

    def can_cook(self, rid):
        for ing, n in RECIPES[rid]["needs"].items():
            have = self.count_fish() if ing == "fish" else self.count_item(ing)
            if have < n:
                return False
        return True

    def cook(self, rid):
        if not self.can_cook(rid):
            return False, "Faltam ingredientes. O Mercado Central vende quase tudo."
        for ing, n in RECIPES[rid]["needs"].items():
            if ing == "fish":
                self.remove_fish(n)
            else:
                self.remove_item(ing, n)
        if not self.add_item(rid):
            return False, "Mochila cheia!"
        self.cooked.add(rid)
        return True, f"Você cozinhou {RECIPES[rid]['name']}!"

    def play_arcade(self):
        if self.money < 10:
            self.say("Você precisa de $10 para jogar.")
            return

        def pick(i):
            if i != 0:
                return
            self.money -= 10

            def done(score):
                prize = score * 3
                self.money += prize
                self.energy = max(0, self.energy - ARCADE_ENERGY)
                if score > self.stats["arcade_best"]:
                    self.stats["arcade_best"] = score
                    self.toasts.push(f"Novo recorde no Meteoro: {score}!", C_GOLD)
                self.toasts.push(f"Meteoro: {score} pontos (+${prize})", C_GREEN)
            self.push(Arcade(done, self.stats["arcade_best"]))
        self.push(ui.Choice("Jogar METEORO por $10? Cada moeda pega vale $3.", ["Jogar!", "Agora não"], pick))

    # --- Lojas ---------------------------------------------------------
    def _buy_item(self, item, price):
        def buy():
            if self.money < price:
                return False, "Dinheiro insuficiente."
            if item == "rosas" and not any(self.hearts(k) >= ROMANCE_CAP_HEARTS for k in ROMANCES):
                return False, "Bea: 'Rosas vermelhas são pra quando o coração já decidiu.' (8 corações)"
            if item == "pingente" and not self.dating:
                return False, "Bea: 'Pingente de compromisso? Primeiro namora, querida!'"
            if item == "anel":
                ok, why = casamento.can_buy_ring(self)
                if not ok:
                    return False, why
            if ITEMS[item]["kind"] == "book" and (BOOKS[item]["flag"] in self.flags or self.count_item(item)):
                return False, "Você já tem este livro."
            if not self.add_item(item):
                return False, "Mochila cheia."
            self.money -= price
            return True, f"Comprou {ITEMS[item]['name']}."
        return buy

    def open_shop(self, shop_id):
        shop = SHOPS[shop_id]
        disc = 0.8 if shop.get("discount_flag") in self.flags else 1.0
        disc *= fundacao.shop_mult(self, shop_id) * eventos.shop_mult(self, shop_id)   # Biblioteca, Bea, Marco

        def entries():
            out = []
            for item in shop["stock"]:
                price = int(round(ITEMS[item]["price"] * disc))
                out.append(dict(label=ITEMS[item]["name"], price=price, desc=ITEMS[item]["desc"], item=item,
                                buy=self._buy_item(item, price), enabled=lambda p=price: self.money >= p))
            return out
        if shop_id == "trattoria" and "vittoria_coffee" in self.flags:
            base = entries

            def free_coffee():
                if self.ricci_coffee:
                    return False, "Você já tomou o café de hoje. Volte amanhã!"
                if not self.add_item("cappuccino"):
                    return False, "Mochila cheia."
                self.ricci_coffee = True
                return True, "Cappuccino por conta da Vittoria. Grazie!"

            def entries():
                return [dict(label="Café por conta da Vittoria" + (" (amanhã tem mais)" if self.ricci_coffee else ""),
                             price=0, desc="Um cappuccino por dia, por conta da casa.", item="cappuccino",
                             buy=free_coffee, enabled=lambda: not self.ricci_coffee)] + base()
        sub = shop["subtitle"] + ("  (20% de desconto)" if disc < 1 else "")
        self.push(ui.Shop(shop["title"], sub, entries, self))

    def shop_open(self, npc):
        if not npc.data.get("shop") or npc.data.get("shop_map") != self.map_name:
            return False
        return npc.arrived and npc.goal and npc.goal[0] == self.map_name

    def open_terminal(self):
        def entries():
            out = []
            props = [k for k, p in PROJECTS.items() if self.quarter in p["quarters"]
                     and (not p.get("locked_flag") or p["locked_flag"] in self.flags)]
            props.sort(key=lambda k: PROJECTS[k]["cost"])
            for k in props:
                item = "prop_" + k
                price = PROJECTS[k]["cost"]
                out.append(dict(label=ITEMS[item]["name"], price=price, desc=ITEMS[item]["desc"], item=item,
                                buy=self._buy_item(item, price), enabled=lambda p=price: self.money >= p))
            unlocked = sum(1 for s in self.stations if s["unlocked"])
            if unlocked < MAX_STATIONS:
                price = 300 + 150 * (unlocked - START_STATIONS)

                def buy_station(price=price):
                    if self.money < price:
                        return False, "Dinheiro insuficiente."
                    for s in self.stations:
                        if not s["unlocked"]:
                            s["unlocked"] = True
                            break
                    self.money -= price
                    return True, "Nova bancada instalada no laboratório!"
                out.append(dict(label=f"Nova bancada ({unlocked}/{MAX_STATIONS})", price=price,
                                desc="Mais um projeto rodando ao mesmo tempo.", buy=buy_station,
                                enabled=lambda p=price: self.money >= p))
            if "coffee_machine" not in self.flags:
                def buy_coffee():
                    if self.money < 800:
                        return False, "Dinheiro insuficiente."
                    self.money -= 800
                    self.flags.add("coffee_machine")
                    return True, "Cafeteira executiva instalada na sua sala!"
                out.append(dict(label="Cafeteira executiva", price=800,
                                desc="Um expresso grátis por dia, na sua sala.", buy=buy_coffee,
                                enabled=lambda: self.money >= 800))
            return out
        self.push(ui.Shop("Terminal P&D", f"Propostas do Q{self.quarter} e melhorias do laboratório.",
                          entries, self))

    # --- Computador: e-mails e investimentos -----------------------------
    def open_computer(self):
        opts = ["Ler e-mails"]
        if self.map_name == "home":
            opts.append("Decorar a cobertura")
        if "book_stocks" in self.flags:
            opts.append("Investimentos (ações LCORP)")
        opts.append("Sair")

        def pick(i):
            if opts[i] == "Ler e-mails":
                self.open_emails()
            elif opts[i] == "Decorar a cobertura":
                decor.open_editor(self)
            elif opts[i].startswith("Investimentos"):
                self.open_stocks()
        if len(opts) == 2:
            self.open_emails()
        else:
            self.push(ui.Choice("Computador", opts, pick))

    def open_stocks(self):
        p = self.stock
        trend = self.stock - self.stock_prev
        info = (f"Cotação: $ {p:.2f} ({'+' if trend >= 0 else ''}{trend:.2f} ontem) · Você tem {self.shares} ações "
                f"(valem $ {int(p * self.shares):,})").replace(",", "X").replace(".", ",").replace("X", ".")

        def buy(n):
            cost = int(round(p * n))
            if self.money < cost:
                self.toasts.push("Dinheiro insuficiente.", C_RED)
                return
            self.money -= cost
            self.shares += n
            self.toasts.push(f"Comprou {n} ações por $ {cost:,}. Agora você tem {self.shares}.".replace(",", "."), C_GREEN)

        def sell(n):
            k = min(n, self.shares)
            if k <= 0:
                self.toasts.push("Você não tem ações.", C_MUTED)
                return
            val = int(round(p * k))
            self.shares -= k
            self.money += val
            self.toasts.push(f"Vendeu {k} ações por $ {val:,}. Restam {self.shares}.".replace(",", "."), C_GOLD)

        def pick(i):
            o = opts[i]
            if o.startswith("Comprar"):
                self.push(ui.NumberPrompt("Comprar ações LCORP", p, int(self.money // p) if p else 0, buy,
                                          "comprar", f"Cotação $ {p:.2f} · Saldo $ {self.money:,}".replace(",", "X")
                                          .replace(".", ",").replace("X", "."),
                                          C_GREEN))
            elif o.startswith("Vender todas"):
                if self.shares:
                    self.push(ui.Choice(f"Vender todas as {self.shares} ações por $ {int(round(p * self.shares)):,}?"
                                        .replace(",", "."), ["Vender todas", "Cancelar"],
                                        lambda j: sell(self.shares) if j == 0 else None))
                else:
                    self.toasts.push("Você não tem ações.", C_MUTED)
            elif o.startswith("Vender"):
                if not self.shares:
                    self.toasts.push("Você não tem ações.", C_MUTED)
                    return
                self.push(ui.NumberPrompt("Vender ações LCORP", p, self.shares, sell, "vender",
                                          f"Cotação $ {p:.2f} · Você tem {self.shares} ações".replace(".", ","), C_GOLD))
        opts = ["Comprar ações", "Vender ações", f"Vender todas ({self.shares})", "Voltar"]
        self.push(ui.Choice(f"Investimentos — {info}", opts, pick))

    # --- Conversas -----------------------------------------------------
    def hearts(self, key):
        return self.friendship[key] // HEART_POINTS

    def heart_cap(self, key):
        if key in ROMANCES and key != self.dating:
            return ROMANCE_CAP_HEARTS
        return MAX_HEARTS

    def add_friendship(self, key, pts):
        old = self.hearts(key)
        cap = self.heart_cap(key) * HEART_POINTS
        self.friendship[key] = max(0, min(cap, self.friendship[key] + pts))
        new = self.hearts(key)
        if new > old:
            audio.sfx("heart")
            self.toasts.push(f"{NPCS[key]['short']}: {new} coração(ões)!", C_PINK)

    def talk_to(self, npc):
        npc.face_toward(self.player.x, self.player.y)
        key = npc.key
        # encontro marcado
        if (self.date and self.date["npc"] == key and not self.date.get("done") and 1150 <= self.minutes <= 1320
                and npc.goal and npc.goal[0] == self.date["map"] and npc.arrived):
            self.do_date(npc)
            return
        # vara de pesca do Joca
        if key == "joca" and "got_rod" not in self.flags:
            self.flags.add("got_rod")
            self.add_item("vara")
            self.add_item("isca", 5)
            self.push(ui.Dialog(npc.name, ["Ô, moça! Primeira vez no píer? Toma, uma vara velha minha. E umas iscas.",
                                           "Escolhe a vara na barra, fica de frente pra água e aperta E.",
                                           "Quando aparecer o '!', aperta E rápido. Depois segura ESPAÇO pra manter "
                                           "o peixe dentro da barra verde. Boa pescaria!"],
                                self.portrait_for(npc), subtitle=npc.data["role"]))
            self.toasts.push("Ganhou: Vara de Pesca e 5 iscas!", C_GREEN, "vara")
            return
        req = self.request
        if req and req["npc"] == key and self.count_item(req["item"]) >= req["qty"]:
            self.remove_item(req["item"], req["qty"])
            self.money += req["reward"]
            self.request = None
            self.add_friendship(key, 150)
            self.toasts.push(f"Pedido entregue: +${req['reward']}", C_GOLD)
            self.push(ui.Dialog(npc.name, ["Perfeito, era exatamente isso! Você salvou o meu dia.",
                                           f"Aqui está o combinado: ${req['reward']}. Obrigada!"],
                                self.portrait_for(npc, "happy"), on_close=lambda: self.check_events(key),
                                subtitle=npc.data["role"]))
            return
        if req and req["npc"] == key and key not in self.request_nag:
            self.request_nag.add(key)
            have = self.count_item(req["item"])
            self.push(ui.Dialog(npc.name, [f"Ainda preciso de {req['qty']}x {ITEMS[req['item']]['name']}. "
                                           f"Você tem {have}. {self.item_hint(req['item'])}"],
                                self.portrait_for(npc), subtitle="pedido"))
            return
        if casal.talk(self, npc):                   # pedido do dia a dia (morando junto)
            return
        item = self.selected_item()
        can_gift = bool(item) and ITEMS[item]["kind"] not in NO_GIFT and key not in self.gifted
        blocked = f"{key}|{self.period}" in self.talk_log
        opts, acts = [], []
        if self.shop_open(npc):
            opts.append("Ver loja"); acts.append(lambda: self.open_shop(npc.data["shop"]))
        elif npc.data.get("shop") == "bait" and self.map_name == "city" and self.minutes < 18 * 60:
            opts.append("Ver iscas e varas"); acts.append(lambda: self.open_shop("bait"))
        if can_gift:
            opts.append(f"Dar {ITEMS[item]['name']}"); acts.append(lambda: self.give_gift(npc, item))
        if key in (self.dating, self.partner):
            opts.append("Beijar"); acts.append(lambda: self.kiss(npc))
        if key in (self.dating, self.partner) and not self.date and self.minutes < 19 * 60 and not festas.evening_busy(self):
            opts.append("Convidar para um encontro hoje às 20h"); acts.append(lambda: self.invite_date(npc))
        marina.talk_options(self, npc, opts, acts)
        jogos.talk_options(self, npc, opts, acts)
        if not opts:
            if blocked:
                self.say_busy(npc)
            else:
                self.chat(npc)
            return
        if not blocked:
            opts.insert(0, "Conversar"); acts.insert(0, lambda: self.chat(npc))
        opts.append("Tchau"); acts.append(lambda: None)
        self.push(ui.Choice(f"{npc.data['short']}", opts, lambda i: acts[i]()))

    def say_busy(self, npc):
        pool = dialogue.BUSY.get(npc.key, []) + dialogue.BUSY["default"]
        self.npc_emote(npc, "coracao" if npc.key in (self.dating, self.partner) else "reticencias")
        nxt = {"manha": "à tarde", "tarde": "à noite", "noite": "amanhã"}[self.period]
        self.toasts.push(f"{npc.data['short']}: \"{random.choice(pool)}\"", C_LILAC)
        self.toasts.push(f"Vocês já conversaram nesta {self.PERIOD_NAMES[self.period]}. Tente {nxt}.", C_MUTED)

    def pick_line(self, npc):
        """Escolhe uma fala que ainda não foi dita, considerando hora, clima, lugar e amizade."""
        key = npc.key
        base = npc.data["lines"]
        extra = dialogue.LINES.get(key, {})
        h = self.hearts(key)
        pools = []

        def add(lines, w):
            for ln in lines or []:
                pools.append((ln, w))
        for (who, cond, ln) in dialogue.REACTIVE:
            if who == key:
                try:
                    if cond(self):
                        pools.append((ln, 6))
                except Exception:
                    pass
        if key == self.partner:
            add(base.get("partner"), 4); add(extra.get("partner"), 4)
        elif key == self.dating:
            add(base.get("dating"), 3); add(extra.get("dating"), 3)
        if npc.map:
            add(extra.get(npc.map), 2)
        add(extra.get(self.period), 2)
        if self.period == "noite":
            add(base.get("evening"), 2)
        if self.weather == "chuva":
            add(base.get("rain"), 2); add(extra.get("chuva"), 2)
        if self.weekday >= 5:
            add(base.get("weekend"), 2); add(extra.get("fds"), 2)
        add(base.get("low"), 1); add(extra.get("t0"), 1)
        if h >= 3:
            add(base.get("mid"), 1.5); add(extra.get("t3"), 1.5)
        if h >= 6:
            add(base.get("high"), 2); add(extra.get("t6"), 2)
        seen = self.lines_seen.setdefault(key, [])
        fresh = [(ln, w) for ln, w in pools if ln not in seen]
        if not fresh:
            recent = seen[-3:]
            seen.clear()
            seen.extend(recent)
            fresh = [(ln, w) for ln, w in pools if ln not in seen] or pools
        line = random.choices([p[0] for p in fresh], [p[1] for p in fresh])[0]
        seen.append(line)
        return line

    # --- Beijo (namorando ou morando junto) -----------------------------
    KISS_T = (0.45, 0.8, 2.0, 2.6, 3.0)            # chegando, mãos dadas, beijo, sorriso corado, voltando
    KISS_DUR = 3.0
    KISS_POINTS = 30                                # amizade extra, uma vez por dia
    HEART_PX = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]

    def kiss(self, npc):
        """As duas ficam frente a frente (a 1 tile), dão as mãos, fecham os olhos e se inclinam até os lábios
        se encostarem (poses.kiss_pose); quem é mais baixa fica na ponta dos pés. Depois sorriem coradas."""
        if getattr(self, "kiss_fx", None) or getattr(self, "eat_fx", None) or self.act:
            return
        if self.player.seat:
            self.stand_up()
            self.player.rise = None
        pl = self.player
        nx, ny = (npc.fx + 0.5) * TILE, npc.base_y
        right = nx > pl.x if abs(nx - pl.x) > 2 else pl.dir != "left"
        mid = (int((pl.x + nx) / 2 // TILE), int(((pl.y + ny) / 2 - FOOT) // TILE))
        if self.current_map.is_solid(*mid):         # balcão ou mesa no meio: manda um beijo
            npc.face_toward(pl.x, pl.y)
            self.npc_emote(npc, "beijo")
            self.player_emote = dict(kind="beijo", t=0.0)
            audio.sfx("kiss")
            casal.note(self, npc.key, 1)
            kissed = self.__dict__.setdefault("kissed", set())
            if npc.key not in kissed:
                kissed.add(npc.key)
                self.add_friendship(npc.key, self.KISS_POINTS)
                self.toasts.push(f"Um beijo por cima do balcão. {npc.data['short']} riu e mandou outro de volta.", C_PINK)
            return
        npc.face_toward(pl.x, pl.y)
        npc.paused = self.KISS_DUR + 0.8
        npc.current_frames()                        # garante a roupa certa (npc._look_cur)
        casal.note(self, npc.key, 1)
        self.kiss_fx = dict(npc=npc, t=0.0, ox=pl.x, oy=pl.y, nfx=npc.fx, nfy=npc.fy, s=1 if right else -1,
                            mx=(pl.x + nx) / 2, my=(pl.y + ny) / 2, smack=False, hearts=[])

    def update_kiss_fx(self, dt):
        fx = getattr(self, "kiss_fx", None)
        if not fx:
            return
        fx["t"] += dt
        t, npc, pl = fx["t"], fx["npc"], self.player
        A, C, K, F, E = self.KISS_T
        if fx.get("ended"):                         # só esperando os últimos corações sumirem
            self._kiss_hearts(fx, dt)
            if not fx["hearts"]:
                self.kiss_fx = None
            return
        stage, walk = None, False
        if t < A:                                   # andam até ficar frente a frente
            k, walk = 1 - (1 - t / A) ** 2, True
        elif t < C:                                 # mãos dadas, olhos fechando
            k, stage = 1.0, "close"
        elif t < K:                                 # se inclinam: o beijo
            k, stage = 1.0, "kiss"
        elif t < F:                                 # sorriem coradas
            k, stage = 1.0, "after"
        else:                                       # cada uma volta para o seu lugar
            q = min(1.0, (t - F) / (E - F))
            k, walk = 1 - q * q * (3 - 2 * q), True
        half = poses.KISS_DIST * SCALE / 2
        sgn = fx["s"]
        n0x, n0y = (fx["nfx"] + 0.5) * TILE, (fx["nfy"] + 1) * TILE - FOOT
        px_t, nx_t, y_t = fx["mx"] - sgn * half, fx["mx"] + sgn * half, fx["my"]
        pl.x = fx["ox"] + (px_t - fx["ox"]) * k
        pl.y = fx["oy"] + (y_t - fx["oy"]) * k
        nx = n0x + (nx_t - n0x) * k
        ny = n0y + (y_t - 0.05 - n0y) * k          # um tiquinho atrás: a Letícia fica na frente
        npc.fx, npc.fy = nx / TILE - 0.5, (ny + FOOT) / TILE - 1
        pl.dir = "right" if sgn > 0 else "left"
        npc.dir = "left" if sgn > 0 else "right"
        look = getattr(npc, "_look_cur", None) or npc.data["look"]
        far = abs(px_t - fx["ox"]) + abs(y_t - fx["oy"]) > 3 or abs(nx_t - n0x) + abs(y_t - n0y) > 3
        if stage:
            pl.pose = dict(poses.kiss_pose(stage, pl.look, look, True), src="kiss")
            npc.pose = poses.kiss_pose(stage, look, pl.look, False)
        elif walk and far:
            w = 4 + int(t * 10) % 4
            pl.pose = dict(arms=None, face=None, walk=w, bob=1 if w % 2 else 0, blink=False, src="kiss")
            npc.pose = dict(arms=None, face=None, walk=w, bob=1 if w % 2 else 0, blink=False)
        else:
            pl.pose = dict(arms=None, face="love" if t > F else None, blink=False, bob=0, src="kiss")
            npc.pose = dict(arms=None, face="love" if t > F else None, blink=False, bob=0)
        mx, my = fx["mx"], fx["my"] - 32 * SCALE
        if not fx["smack"] and t >= C:
            fx["smack"] = True
            audio.sfx("kiss")
            fx["hearts"].append(dict(x=mx, y=my, vy=-14, life=1.4, big=True, sway=0.0))
        if fx["smack"] and t < K and random.random() < dt * 7:
            fx["hearts"].append(dict(x=mx + random.uniform(-14, 14), y=my + random.uniform(-4, 6),
                                     vy=random.uniform(-40, -24), life=random.uniform(0.7, 1.1), big=False,
                                     sway=random.uniform(0, 6)))
        self._kiss_hearts(fx, dt)
        if t >= E:
            fx["ended"] = True
            pl.x, pl.y = fx["ox"], fx["oy"]
            npc.fx, npc.fy = fx["nfx"], fx["nfy"]
            npc.pose = None
            if pl.pose and pl.pose.get("src") == "kiss":
                pl.pose = None
            npc.face_toward(pl.x, pl.y)
            self.npc_emote(npc, "coracao")
            kissed = self.__dict__.setdefault("kissed", set())
            if npc.key not in kissed:
                kissed.add(npc.key)
                self.add_friendship(npc.key, self.KISS_POINTS)
                self.toasts.push(f"{npc.data['short']} ficou toda boba com o beijo.", C_PINK)

    @staticmethod
    def _kiss_hearts(fx, dt):
        for h in fx["hearts"]:
            h["life"] -= dt
            h["y"] += h["vy"] * dt
        fx["hearts"] = [h for h in fx["hearts"] if h["life"] > 0]

    def _heart_img(self, k):
        key = ("kiss_heart", k)
        img = self.__dict__.setdefault("_heart_cache", {}).get(key)
        if img is None:
            img = pygame.Surface((9 * k, 8 * k), pygame.SRCALPHA)
            for yy, row in enumerate(self.HEART_PX):                 # contorno escuro
                for xx, c in enumerate(row):
                    if c == "X":
                        img.fill((120, 30, 70), (xx * k, yy * k, 3 * k, 3 * k))
            for yy, row in enumerate(self.HEART_PX):                 # coração rosa
                for xx, c in enumerate(row):
                    if c == "X":
                        img.fill((255, 96, 150), ((xx + 1) * k, (yy + 1) * k, k, k))
            img.fill((255, 214, 228), (2 * k, 2 * k, k, k))          # brilho
            self._heart_cache[key] = img
        return img

    def draw_kiss_fx(self, surf, cam):
        fx = getattr(self, "kiss_fx", None)
        if not fx:
            return
        for h in fx["hearts"]:
            k = 3 if h["big"] else 2
            img = self._heart_img(k).copy()
            img.set_alpha(int(255 * min(1.0, h["life"] / 0.35)))
            sway = 0 if h["big"] else math.sin(fx["t"] * 6 + h["sway"]) * 3
            surf.blit(img, (int(h["x"] - cam[0] + sway - img.get_width() / 2),
                            int(h["y"] - cam[1] - img.get_height() / 2)))

    def npc_emote(self, npc, kind):
        npc.emote, npc.emote_t = kind, 1.8

    def chat(self, npc):
        key = npc.key
        self.talk_log.add(f"{key}|{self.period}")
        mult = (1.5 if "psiquiatria" in self.buffs else 1) * fundacao.talk_mult(self)
        if key not in self.talked:
            self.talked.add(key)
            self.add_friendship(key, int(TALK_POINTS * mult))
        else:
            self.add_friendship(key, int(8 * mult))
        if casal.jealous_chat(self, npc):           # ciúmes leves (só comentários, nunca castigo)
            casal.note(self, key, 1)
            return
        casal.note(self, key, 1)
        mood = "smile" if self.hearts(key) >= 4 else None
        if key in (self.dating, self.partner):
            mood = "love"
        line = (festas.chat_line(self, npc) or casamento.chat_line(self, npc) or closet.chat_line(self, npc)
                or clima.chat_line(self, npc))
        if line and mood is None:
            mood = "happy"
        self.push(ui.Dialog(npc.name, [line or self.pick_line(npc)], self.portrait_for(npc, mood),
                            on_close=lambda: self.check_events(key), subtitle=npc.data["role"]))

    def give_gift(self, npc, item):
        key = npc.key
        d = npc.data
        if item == "rosas" and key in ROMANCES:
            if self.dating == key:
                pass
            elif self.dating:
                self.push(ui.Dialog(npc.name, ["Letícia... você já está com outra pessoa. Eu não quero ser segunda opção.",
                                               "Fica com as rosas. Elas merecem alguém que diga sim de verdade."],
                                    self.portrait_for(npc), subtitle=d["role"]))
                return
            elif self.proposal:
                who = NPCS[self.proposal]["short"]
                self.say(f"Você já combinou de pedir a {who} em namoro. Guarde as rosas para depois."
                         if self.proposal != key else
                         f"O pedido já está marcado: {self.proposal_text()}.")
                return
            elif self.hearts(key) < ROMANCE_CAP_HEARTS:
                self.push(ui.Dialog(npc.name, ["Rosas vermelhas? Isso é... muito pra agora.",
                                               "Vamos com calma, tá? Guarda pra quando a gente se conhecer melhor."],
                                    self.portrait_for(npc), subtitle=d["role"]))
                return
            elif f"{key}_pedido" in SCENES:
                # como no pedido do Stardew, mas marcado: nada acontece com ela agora; a cena do pedido
                # toca no lugar e na hora dela (linha rosa no HUD)
                self.remove_item(item)
                self.proposal = key
                audio.sfx("love")
                self.push(ui.Dialog("", [f"Você guarda o buquê com cuidado. Hoje não é o momento certo...",
                                         f"Você vai pedir a {d['short']} em namoro: {self.proposal_text()}."]))
                self.toasts.push(f"Pedido de namoro: {self.proposal_text()}", C_PINK)
                return
            else:
                self.remove_item(item)
                self.dating = key
                self.gifted.add(key)
                self.talked.add(key)
                self.add_friendship(key, 200)
                self.toasts.push(f"Você e {d['short']} estão namorando!", C_PINK)
                casal.start_dating(self, key)
                self.play_scene(f"namoro_{key}", dating_scene(key))
                return
        if item == "anel" and casamento.give_ring(self, npc):
            return
        if item == "pingente" and key in ROMANCES:
            if self.dating != key or self.partner:
                self.push(ui.Dialog(npc.name, ["Isso é lindo... mas é sério demais pra nós agora."],
                                    self.portrait_for(npc), subtitle=d["role"]))
                return
            if self.hearts(key) < MAX_HEARTS:
                self.push(ui.Dialog(npc.name, ["Um pingente de compromisso? Eu... ainda preciso de um tempo.",
                                               "Me pergunta de novo daqui a pouco? (10 corações)"],
                                    self.portrait_for(npc, "smile"), subtitle=d["role"]))
                return
            self.remove_item(item)
            self.partner = key
            casamento.moved_in(self)
            self.gifted.add(key)
            self.talked.add(key)
            self.toasts.push(f"{d['short']} vai morar com você na cobertura!", C_PINK)
            self.play_scene(f"mudanca_{key}", move_in_scene(key), on_end=lambda: self.plan_npcs(snap=False))
            return
        g = d["gifts"]
        taste = "neutral"
        for t in ("love", "like", "dislike"):
            if item in g.get(t, []):
                taste = t
        self.remove_item(item)
        self.gifted.add(key)
        self.talked.add(key)
        self.gift_known[key][item] = taste
        pts = GIFT_POINTS[taste] * (2 if key in (self.dating, self.partner) and taste != "dislike" else 1)
        if "ginecologia" in self.buffs and taste != "dislike":
            pts = int(pts * 1.25)
        pts = int(pts * eventos.gift_mult(self, taste))          # embrulho da Addison
        mult, bonus_line, bonus_toast = festas.gift_bonus(self, key, item, taste)
        if mult == 1:
            mult, bonus_line, bonus_toast = casal.gift_bonus(self, key, taste)
        if mult != 1 and pts > 0:
            pts *= mult
        if bonus_toast:
            self.toasts.push(bonus_toast, C_GOLD)
        casal.note(self, key, 3 if taste == "love" else 2)
        self.add_friendship(key, pts)
        # presente amado: retrato tímido (se a personagem tiver); presente ruim: retrato "ruim"
        if taste == "love" and art.portrait_file(d.get("portrait_key", key), "shy") not in (
                None, art.portrait_file(d.get("portrait_key", key))):
            mood = "shy"
        else:
            mood = {"love": "love" if key in ROMANCES and self.hearts(key) >= 6 else "happy", "like": "happy",
                    "dislike": "bad"}.get(taste)
        audio.sfx({"love": "love", "dislike": "bad"}.get(taste, "gift"))
        text = d["reactions"][taste]
        if taste == "dislike":
            text = gifts.dislike_line(key, item) or text

        def after():
            festas.after_gift(self, key)            # amigo secreto: agora é a vez da Letícia ganhar
            self.check_events(key)
        self.push(ui.Dialog(npc.name, [text] + ([bonus_line] if bonus_line else []), self.portrait_for(npc, mood),
                            on_close=after, subtitle=d["role"]))

    def _event_done(self, ev):
        if ev.get("flag") or ev.get("gift"):
            audio.sfx("reward")
        if ev.get("flag"):
            self.flags.add(ev["flag"])
            if ev["flag"] in FLAG_LABELS:
                self.toasts.push(FLAG_LABELS[ev["flag"]], C_GOLD)
            if ev["flag"] == "jess_energy":
                self.energy += 20
        if ev.get("gift"):
            self.add_item(ev["gift"])
            self.toasts.push(f"Ganhou: {ITEMS[ev['gift']]['name']}", C_GREEN, ev["gift"])

    def next_event(self, key):
        """Próximo evento de coração liberado e ainda não visto (um de cada vez, em ordem)."""
        for h, ev in sorted(NPCS[key].get("events", {}).items()):
            tag = f"{key}:{h}"
            if tag in self.events_seen:
                continue
            if self.hearts(key) < h or (h == 10 and key in ROMANCES and self.dating != key):
                return None
            return h, ev
        return None

    def check_events(self, key):
        """Chamado depois de conversas e presentes. Eventos sem cena aparecem na hora; eventos com cena
        ficam pendentes até a jogadora ir ao lugar da cena no horário certo (como no Stardew Valley)."""
        nxt = self.next_event(key)
        if not nxt:
            return
        h, ev = nxt
        npc = self.npcs[key]
        if ev.get("scene") in SCENES:
            tag = f"{key}:{h}"
            if tag not in self.event_hinted and h > 0:      # eventos de 0 corações são surpresa: sem aviso
                self.event_hinted.add(tag)
                where, a, b = self.scene_place(ev["scene"])
                self.toasts.push(f"Novo evento com {NPCS[key]['short']}: {where}, entre {self.fmt_hour(a)} e {self.fmt_hour(b)}.",
                                 C_PINK)
            self.check_scene_events()
            return
        self.events_seen.add(f"{key}:{h}")
        self.push(ui.Dialog(npc.name, ev["lines"], self.portrait_for(npc, ev.get("mood")),
                            on_close=lambda ev=ev: self._event_done(ev), subtitle=f"evento de {h} corações"))

    SCENE_TRIGGER_MAP = {"altomar": "marina"}       # cenas no barco começam na marina
    SCENE_WINDOW = 180                              # minutos antes e depois do horário da cena

    def scene_place(self, scene_key):
        """(onde, das, até) em que um evento com cena pode acontecer."""
        sc = SCENES[scene_key]
        mapn = self.SCENE_TRIGGER_MAP.get(sc["map"], sc["map"])
        t = sc.get("time", 12 * 60)
        a = max(DAY_START, t - self.SCENE_WINDOW)
        b = min(DAY_END - 30, t + self.SCENE_WINDOW)
        if mapn == "city":
            legend = next((s[1] for s in sc["steps"] if s[0] == "legenda"), "na cidade")
            where = legend[0].lower() + legend[1:]
        else:
            where = self.world[mapn].label
        return where, a, b

    def _scene_anchor(self, scene_key):
        sc = SCENES[scene_key]
        for s in sc["steps"]:
            if s[0] == "ator" and s[1] == sc.get("npc"):
                return s[2], s[3]
        for s in sc["steps"]:
            if s[0] in ("camera_ja", "camera"):
                return s[1], s[2]
        return None

    @staticmethod
    def fmt_hour(m):
        m %= 24 * 60
        return f"{m // 60}h{m % 60:02d}" if m % 60 else f"{m // 60}h"

    def pending_scene_events(self):
        out = []
        for key in NPC_ORDER:
            nxt = self.next_event(key)
            if nxt and nxt[1].get("scene") in SCENES:
                out.append((key, nxt[0], nxt[1]))
        return out

    def proposal_text(self):
        where, a, b = self.scene_place(f"{self.proposal}_pedido")
        return f"{where}, entre {self.fmt_hour(a)} e {self.fmt_hour(b)}"

    def accept_proposal(self, key):
        """Fim da cena do pedido: agora é namoro."""
        self.proposal = None
        self.dating = key
        casal.start_dating(self, key)
        self.talked.add(key)
        self.add_friendship(key, 200)
        self.toasts.push(f"Você e {NPCS[key]['short']} estão namorando!", C_PINK)
        self.plan_npcs(snap=False)

    def scene_ready(self, scene_key):
        """A jogadora está no mapa da cena, no horário (e, na cidade, perto do lugar)?"""
        sc = SCENES[scene_key]
        mapn = self.SCENE_TRIGGER_MAP.get(sc["map"], sc["map"])
        _, a, b = self.scene_place(scene_key)
        if self.map_name != mapn or not (a <= self.minutes <= b):
            return False
        if mapn == "city":
            anchor = self._scene_anchor(scene_key)
            if anchor:
                tx, ty = self.player.tile
                if abs(tx - anchor[0]) + abs(ty - anchor[1]) > 14:
                    return False
        return True

    def check_scene_events(self):
        """Toca a cena de um evento pendente quando a jogadora está no lugar e no horário da cena."""
        if self.scene != "play" or self.modals or self.fishing or self.fade_dir:
            return
        if (festas.check(self) or casamento.check(self) or casal.check(self) or fundacao.check(self)
                or historia.check(self)):
            return
        if self.proposal and not self.dating and self.scene_ready(f"{self.proposal}_pedido"):
            key = self.proposal
            self.play_scene(f"{key}_pedido", on_end=lambda: self.accept_proposal(key))
            return
        for key, h, ev in self.pending_scene_events():
            if not self.scene_ready(ev["scene"]):
                continue
            self.events_seen.add(f"{key}:{h}")
            self.play_scene(ev["scene"], on_end=lambda ev=ev: self._event_done(ev))
            return
        momentos.check(self)                        # duas personagens conversando pela cidade

    # --- Encontros -----------------------------------------------------
    def invite_date(self, npc):
        places = npc.data["date_places"]

        def pick(i):
            if i >= len(places):
                return
            m, x, y, d, desc = places[i]
            self.date = dict(npc=npc.key, map=m, x=x, y=y, dir=d, desc=desc, done=False)
            npc.plan_day(self.weekday, self.weather, partner=(npc.key == self.partner), date=(m, x, y, d))
            npc.check_schedule(self.minutes)
            self.toasts.push(f"Encontro marcado às 20h: {desc}!", C_PINK)
            self.push(ui.Dialog(npc.name, ["Combinado! Não se atrasa, hein?"], self.portrait_for(npc, "smile"),
                                subtitle=npc.data["role"]))
        self.push(ui.Choice(f"Para onde convidar {npc.data['short']}?", [p[4][0].upper() + p[4][1:] for p in places] + ["Deixa pra lá"],
                            pick))

    def do_date(self, npc):
        self.date["done"] = True
        casal.note(self, npc.key, 3)
        self.add_friendship(npc.key, 140)
        self.energy = min(self.max_energy, self.energy + 30)
        place = next((p for p in npc.data["date_places"] if p[0] == self.date["map"] and p[1] == self.date["x"]),
                     npc.data["date_places"][0])

        def after():
            self.minutes = max(self.minutes, 21 * 60 + 30)
            for n in self.npcs.values():
                n.check_schedule(self.minutes)
            self.toasts.push(f"Encontro com {npc.data['short']}: +energia, +amizade", C_PINK)
        self.play_scene(f"encontro_{npc.key}", date_scene(npc.key, place, self), on_end=after, remember=False)

    # --- Informações ---------------------------------------------------
    def item_hint(self, item):
        if item in FISH:
            f = FISH[item]
            where = {"sea": "no mar (píer/praia)", "deep": "em alto-mar (passeio de pesca na Marina Luthor)"}.get(
                f["where"], "nos lagos do parque e do bosque")
            a, b = f["hours"]
            when = "" if (a, b) == (360, 1560) else f", das {a // 60 % 24}h às {b // 60 % 24}h"
            return f"Peixe: pesque {where}{when}{', só com chuva' if f.get('weather') else ''}."
        if item in PROJECTS:
            return "Produto do laboratório: inicie o projeto numa bancada."
        return ""

    def request_text(self, req):
        y, q, d = self.date_from_abs(req["deadline"])
        return (f"{NPCS[req['npc']]['short']} precisa de {req['qty']}x {ITEMS[req['item']]['name']} "
                f"até {WEEKDAYS_FULL[(d - 1) % 7]} (dia {d}, Q{q}). Recompensa: ${req['reward']} + amizade. "
                f"{self.item_hint(req['item'])} Para entregar, tenha os itens na mochila e fale com "
                f"{NPCS[req['npc']]['short']}.")

    def watch_tv(self):
        prev = clima.forecast(self)
        self.push(ui.Dialog("Jornal de National City", [
            f"Previsão para amanhã: {prev}.",
            f"Mercado: a ação LCORP está cotada a $ {self.stock:.2f}.".replace(".", ",", 1),
            random.choice(NEWS)]))

    def open_emails(self):
        tip = random.choice(TIPS)
        news = random.choice(NEWS)

        def draw(surf, rect):
            y = rect.y + 70
            ui.text(surf, f"Caixa de entrada  —  {self.date_label()}", (rect.x + 30, y), 18, C_MUTED)
            y += 36
            blocks = []
            if self.request:
                blocks.append(("Pedido", self.request_text(self.request), C_GOLD))
            else:
                blocks.append(("Pedido", "Nenhum pedido em aberto hoje.", C_MUTED))
            active = sum(1 for s in self.stations if s["project"])
            ready = sum(1 for s in self.stations if s["project"] and s["progress"] >= self.project_days(s["project"]))
            blocks.append(("Laboratório", f"{active} projeto(s) em andamento, {ready} pronto(s) para lançar. "
                                          f"Projetos lançados até hoje: {self.stats['launched']}.", C_TEXT))
            blocks.append(("Mercado", f"LCORP a $ {self.stock:.2f}. Receita total: ${self.stats['earned']:,}. "
                                      f"Suas ações: {self.shares}.".replace(",", "."), C_TEXT))
            if self.date and not self.date.get("done"):
                blocks.append(("Agenda", f"Encontro hoje às 20h com {NPCS[self.date['npc']]['short']}: "
                                         f"{self.date['desc']}.", C_PINK))
            blocks.append(("CatCo", news, C_TEXT))
            blocks.append(("Jess", tip, C_LILAC))
            for title, body, col in blocks:
                ui.text(surf, title, (rect.x + 30, y), 19, col, bold=True)
                y += 25
                for line in ui.wrap(body, 17, rect.w - 70):
                    ui.text(surf, line, (rect.x + 30, y), 17, C_MUTED)
                    y += 22
                y += 8
        self.push(ui.InfoPanel("E-mails da CEO", draw))

    # --- Menu de pausa ------------------------------------------------
    def open_pause(self, sel=0):
        fs = "Sim" if self.settings.get("fullscreen") else "Não"
        sv = int(round(self.settings.get("sfx", 0.7) * 100))
        opts = ["Continuar", "Mochila", "Objetivos", "Relacionamentos", "Coleções", "Rever cenas"]
        if self.album["given"]:
            opts.append("Álbum de fotos")
        opts += [f"Tela cheia: {fs}", f"Efeitos sonoros: {sv}%", "Controles", "Salvar e voltar ao título"]

        def step_volume(key):
            # cada E sobe 20%; depois de 100% volta a 0% (mudo)
            v = round(self.settings.get(key, 0.6 if key == "music" else 0.7) + 0.2, 1)
            v = 0.0 if v > 1.0 else v
            self.settings[key] = v
            self.save_settings()
            audio.set_volume(**{("music_vol" if key == "music" else "sfx_vol"): v})
            if key == "sfx":
                audio.sfx("confirm")

        def pick(i):
            o = opts[i]
            if o == "Mochila":
                self.push(Inventory(self))
            elif o == "Objetivos":
                self.open_goals()
            elif o == "Relacionamentos":
                self.open_relationships()
            elif o == "Coleções":
                self.push(ui.InfoPanel("Coleções", self.draw_collections))
            elif o == "Rever cenas":
                self.open_scene_gallery()
            elif o == "Álbum de fotos":
                album.open_album(self)
            elif o.startswith("Tela cheia"):
                self.toggle_fullscreen()
            elif o.startswith("Efeitos"):
                step_volume("sfx")
                self.open_pause(i)
            elif o == "Controles":
                self.push(ui.InfoPanel("Controles", draw_controls))
            elif o.startswith("Salvar"):
                self.save()
                self.start_fade(lambda: setattr(self, "scene", "title"))
        ch = ui.Choice(f"Pausa  —  {self.date_label()}, {self.time_label()}", opts, pick)
        ch.sel = sel
        self.push(ch)

    def goal_status(self, key):
        unlocked = sum(1 for s in self.stations if s["unlocked"])
        f3 = sum(1 for k in TEAM if self.hearts(k) >= 3)
        return {
            "launch10": (self.stats["launched"] >= 10, f"{min(10, self.stats['launched'])}/10"),
            "money10k": (self.money >= 10000, f"$ {self.money:,}/10.000".replace(",", ".")),
            "stock150": (self.stock >= 150, f"$ {self.stock:.2f}"),
            "friends3": (f3 == len(TEAM), f"{f3}/{len(TEAM)}"),
            "stations12": (unlocked >= MAX_STATIONS, f"{unlocked}/{MAX_STATIONS}"),
            "hecate": (self.stats["hecate"] >= 1, "liberado" if "hecate" in self.flags else "bloqueado"),
            "fish10": (len(self.fish_caught) >= 10, f"{len(self.fish_caught)}/10"),
            "aquarium": (len(self.aquarium) >= len(FISH), f"{len(self.aquarium)}/{len(FISH)}"),
            "cook5": (len(self.cooked) >= 5, f"{len(self.cooked)}/5"),
            "romance": (bool(self.dating), NPCS[self.dating]["short"] if self.dating else "-"),
            "partner": (bool(self.partner), NPCS[self.partner]["short"] if self.partner else "-"),
            "arcade": (self.stats["arcade_best"] >= 40, f"recorde {self.stats['arcade_best']}"),
            "garden": (self.stats["harvest"] >= 15, f"{min(15, self.stats['harvest'])}/15"),
            "forage": (len(self.forage_found) >= len(FORAGE), f"{len(self.forage_found)}/{len(FORAGE)}"),
            "pet": (self.pet is not None, self.pet.name if self.pet else "-"),
            "karaoke": (bool(self.stats["karaoke_s"]), f"melhor {self.stats['karaoke_best']}%"),
            "cinema": (self.stats["movies"] >= 5, f"{min(5, self.stats['movies'])}/5"),
            "checkup": (len(self.checkups) >= 12, f"{len(self.checkups)}/12"),
        }[key]

    def draw_goals(self, surf, rect):
        y = rect.y + 66
        # contagens que mudam conforme o jogo cresce (peixes de alto-mar, coletáveis novos)
        names = {"aquarium": f"Completar o aquário ({len(FISH)} peixes)",
                 "forage": f"Encontrar todos os {len(FORAGE)} coletáveis"}
        for key, label in GOALS:
            label = names.get(key, label)
            ok, prog = self.goal_status(key)
            box = pygame.Rect(rect.x + 30, y + 3, 18, 18)
            pygame.draw.rect(surf, C_GREEN if ok else (60, 50, 80), box, border_radius=5)
            if ok:
                pygame.draw.lines(surf, (10, 40, 20), False, [(box.x + 4, box.y + 9), (box.x + 7, box.y + 13),
                                                               (box.x + 14, box.y + 5)], 3)
            ui.text(surf, label, (rect.x + 58, y), 17, C_GREEN if ok else C_TEXT, bold=True)
            ui.text(surf, prog, (rect.right - 34, y), 16, C_MUTED, right=True)
            y += 29
        y += 6
        ui.text(surf, "Benefícios", (rect.x + 30, y), 18, C_LILAC, bold=True)
        y += 26
        perks = [FLAG_LABELS[f] for f in FLAG_LABELS if f in self.flags]
        if not perks:
            perks = ["Nenhum ainda. Amizades (3 corações) e livros desbloqueiam benefícios."]
        for p in perks:                  # com rolagem, cabem todos
            for line in ui.wrap("- " + p, 15, rect.w - 80):
                ui.text(surf, line, (rect.x + 34, y), 15, C_MUTED)
                y += 21
        return y

    def open_goals(self):
        self.push(ui.InfoPanel("Objetivos", self.draw_goals, scroll=True, close_keys=(pygame.K_o,)))

    def draw_collections(self, surf, rect):
        y = rect.y + 70
        ui.text(surf, f"Peixes pescados: {len(self.fish_caught)}/{len(FISH)}   ·   no aquário: {len(self.aquarium)}",
                (rect.x + 30, y), 18, C_TEXT, bold=True)
        y += 34
        x = rect.x + 30
        for k in FISH:
            if k in self.fish_caught:
                surf.blit(art.item_icon(k, 2), (x, y))
            else:
                pygame.draw.rect(surf, (40, 30, 56), (x, y, 32, 32), border_radius=6)
            x += 40
        y += 60
        ui.text(surf, f"Receitas cozinhadas: {len(self.cooked)}/{len(RECIPES)}", (rect.x + 30, y), 18, C_TEXT, bold=True)
        y += 34
        x = rect.x + 30
        for k in RECIPES:
            if k in self.cooked:
                surf.blit(art.item_icon(k, 2), (x, y))
            else:
                pygame.draw.rect(surf, (40, 30, 56), (x, y, 32, 32), border_radius=6)
            x += 40
        y += 60
        ui.text(surf, "Livros lidos:", (rect.x + 30, y), 18, C_TEXT, bold=True)
        y += 30
        for k, b in BOOKS.items():
            ok = b["flag"] in self.flags
            ui.text(surf, ("+ " if ok else "· ") + b["name"], (rect.x + 34, y), 16, C_GREEN if ok else C_MUTED)
            y += 22
        ui.text(surf, f"Recorde no Meteoro: {self.stats['arcade_best']}   ·   Peixes pescados no total: "
                      f"{self.stats['fish']}", (rect.x + 30, y + 10), 16, C_MUTED)

    def open_relationships(self):
        def rows():
            return [k for k in NPC_ORDER]

        def draw_row(surf, r, key, sel):
            npc = self.npcs[key]
            p = self.portrait_for(npc, size=70)
            pygame.draw.rect(surf, C_PINK if key in ROMANCES else C_ACCENT, (r.x + 8, r.y + 8, 74, 74), border_radius=6)
            ui.blit_portrait(surf, p, (r.x + 10, r.y + 10))     # nítido também na tela cheia
            ui.text(surf, npc.name, (r.x + 96, r.y + 8), 19, C_TEXT, bold=True)
            role = npc.data["role"]
            if key == self.partner:
                role += "  ·  " + (casamento.status(self, key) or "mora com você")
            elif key == self.dating:
                role += "  ·  namorando"
            elif key in ROMANCES:
                role += "  ·  romance"
            ui.text(surf, role, (r.x + 96 + ui.font(19, True).size(npc.name)[0] + 10, r.y + 11), 14,
                    C_PINK if key in ROMANCES else C_MUTED)
            ui.hearts_row(surf, r.x + 96, r.y + 36, self.friendship[key], 2)
            cap = self.heart_cap(key)
            if cap < MAX_HEARTS:
                ui.text(surf, f"(máx. {cap} até namorar)", (r.x + 96 + 10 * 24, r.y + 36), 13, C_MUTED)
            known = self.gift_known[key]
            names = {"love": "ama", "like": "gosta", "neutral": "ok", "dislike": "não gosta"}
            txt = ", ".join(f"{ITEMS[i]['name']} ({names[t]})" for i, t in known.items()) or "nenhum presente ainda"
            ui.text(surf, f"Presentes: {txt}"[:92], (r.x + 96, r.y + 60), 13, C_MUTED)
            done = "conversou hoje" if key in self.talked else "ainda não conversou hoje"
            ui.text(surf, done, (r.right - 14, r.y + 10), 13, C_GREEN if key in self.talked else C_MUTED, right=True)
            bday = festas.is_birthday(self, key)
            ui.text(surf, ("Aniversário HOJE!" if bday else f"Aniversário: {festas.birthday_label(key)}"),
                    (r.right - 14, r.y + 36), 13, C_PINK if bday else C_MUTED, right=True)
        self.push(ui.ScrollPanel("Relacionamentos", rows, draw_row, 96,
                                 "Converse todo dia e dê presentes. Romances: rosas aos 8 corações, pingente aos 10.",
                                 close_keys=(pygame.K_r,)))

    # ------------------------------------------------------------------
    # Fim do dia
    # ------------------------------------------------------------------
    def end_day(self, passed_out=False):
        audio.sfx("sleep")

        def go():
            self.summary = self.process_night(passed_out)
            self.modals = []
            self.fishing = None
            self.scene = "summary"
        self.start_fade(go)

    def process_night(self, passed_out):
        ended = (self.day, self.quarter, self.year)
        rows, earnings = {}, 0
        for item, n in self.shipped:
            rows[item] = rows.get(item, 0) + n
        table = []
        for item, n in rows.items():
            val = self.sell_value(item) * n
            earnings += val
            table.append((item, n, val))
        self.money += earnings
        self.stats["earned"] += earnings
        notes = []
        if passed_out:
            penalty = 0 if ("urologia" in self.buffs or "cmh_care" in self.flags) else min(800, int(self.money * 0.08))
            self.money -= penalty
            conta = f"conta do hospital: ${penalty}" if penalty else "a consulta de hoje cobriu a conta"
            notes.append((f"Você desmaiou de cansaço e acordou no Conti Moretti ({conta}).", C_RED))
        if self.date and not self.date.get("done"):
            k = self.date["npc"]
            self.friendship[k] = max(0, self.friendship[k] - 150)
            notes.append((f"Você deu um bolo em {NPCS[k]['short']}... Ela ficou bem chateada.", C_RED))
        self.date = None
        for st in self.stations:
            if st["project"] and st["worked"]:
                st["progress"] += 1
            st["worked"] = False
        ready = sum(1 for s in self.stations if s["project"] and s["progress"] >= self.project_days(s["project"]))
        if ready:
            notes.append((f"{ready} projeto(s) pronto(s) para lançar no laboratório!", C_GREEN))
        self.stock_prev = self.stock
        product_earn = sum(v for i, n, v in table if ITEMS[i]["kind"] == "product")
        change = (random.gauss(0.05, 1.0) + product_earn / 800.0 * STOCK_PER_800
                  + (0.25 if "nia_scoop" in self.flags else 0))
        self.stock = round(max(20.0, self.stock + change), 2)
        self.day += 1
        new_quarter = False
        if self.day > DAYS_PER_QUARTER:
            self.day = 1
            self.quarter += 1
            new_quarter = True
            if self.quarter > 4:
                self.quarter = 1
                self.year += 1
        if "cmh_contract" in self.flags and self.weekday == 0:
            self.money += 200
            notes.append(("Contrato de manutenção do Conti Moretti: +$200 nesta segunda.", C_GOLD))
        if new_quarter:
            name = seasons.NAMES[seasons.of_quarter(self.quarter)]
            art_ = "a" if name == "Primavera" else "o"
            notes.append((f"Chegou {art_} {name}! Novo trimestre (Q{self.quarter}): roupas novas na cidade, "
                          f"novas propostas, novos peixes e coletáveis.", C_LILAC))
        if self.request and self.abs_day() > self.request["deadline"]:
            k = self.request["npc"]
            self.friendship[k] = max(0, self.friendship[k] - 40)
            notes.append((f"O pedido de {NPCS[k]['short']} venceu. Ficou um clima chato...", C_RED))
            self.request = None
        if not self.request and random.random() < 0.55:
            self.gen_request()
            notes.append(("Novo pedido na sua caixa de e-mails.", C_GOLD))
        self.minutes = DAY_START
        self.time_acc = 0
        self.energy = self.max_energy if not passed_out else self.max_energy // 2
        self.talked, self.gifted = set(), set()
        self.kissed = set()
        self.talk_log = set()
        self.request_nag = set()
        self.coffee_today = False
        self.ricci_coffee = False
        self.milany_visit = False
        self.shipped = []
        self.warned = set()
        was_rain = self.weather == "chuva"
        self.weather = self.weather_tomorrow
        # chance de chuva de cada estação (no inverno vira neve)
        rain = {"spring": 0.25, "summer": 0.12, "autumn": 0.32, "winter": 0.35}[seasons.of_quarter(self.quarter)]
        self.weather_tomorrow = "chuva" if random.random() < rain else "sol"
        festas.night(self, notes)                   # festa (com tempo bom), aniversários e amigo secreto
        casal.night(self, notes, passed_out)        # pedido do dia, café da manhã e aniversário de namoro
        clima.night(self, notes, was_rain)          # tempestade e arco-íris
        closet.night(self, notes)                   # roupas de presente (Lucy, Vittoria, Ian)
        album.night(self, notes)                    # o Barry entrega o álbum de fotos
        fundacao.night(self, notes)                 # obras da Fundação ficam prontas
        casamento.night(self, notes)                # aviso na véspera do casamento
        if "drone" in self.flags:
            n = 0
            for st in self.stations:
                if st["project"] and st["progress"] < self.project_days(st["project"]):
                    st["worked"] = True
                    n += 1
            if n:
                notes.append((f"O drone do Brainy já trabalhou em {n} projeto(s) hoje cedo.", C_LILAC))
        if self.partner:
            gift = random.choice(NPCS[self.partner]["morning_gift"])
            if self.add_item(gift):
                notes.append((f"{NPCS[self.partner]['short']} deixou {ITEMS[gift]['name']} pra você. <3", C_PINK))
            self.add_friendship(self.partner, 10)
        activities.night(self, notes)
        marina.night(self, notes)
        hospital.night(self)
        if "cmh_donation_pending" in self.flags:
            self.flags.discard("cmh_donation_pending")
            self.stock = round(self.stock + 2.5, 2)
            notes.append(("A doação ao Conti Moretti saiu na CatCo. LCORP +2,50!", C_GOLD))
        self.crowd.reset_day()
        self.plan_npcs()
        self.map_name = "home"
        self.player.place_tile(*HOME_BED, "down")
        if passed_out:
            self.map_name = "hospital"
            self.player.place_tile(*HOSPITAL_BED, "down")
        self._act_last_map = self.map_name
        self.cars = []
        self.save()
        return dict(date=ended, table=table, earnings=earnings, notes=notes, stock=(self.stock_prev, self.stock))

    def gen_request(self):
        key = random.choice(TEAM + ["lucy", "vittoria", "nia", "marco", "joca"])
        if key in TEAM:
            avail = [k for k, p in PROJECTS.items() if self.quarter in p["quarters"] and not p.get("locked_flag")]
            avail.sort(key=lambda k: PROJECTS[k]["days"])
            item = random.choice(avail[:3])
            days = PROJECTS[item]["days"]
            qty = 1 if days >= 5 else random.choice([1, 2, 2, 3])
            reward = int(PROJECTS[item]["value"] * qty * 1.6)
            deadline = self.abs_day() + days + 3
        else:
            avail = [k for k, f in FISH.items() if self.quarter in f["quarters"] and f["value"] <= 110
                     and not f.get("weather")]
            item = random.choice(avail)
            qty = random.choice([1, 1, 2])
            reward = int(FISH[item]["value"] * qty * 2.2)
            deadline = self.abs_day() + 4
        self.request = dict(npc=key, item=item, qty=qty, reward=reward, deadline=deadline)

    def begin_day(self):
        self.scene = "play"
        self.summary = None
        if self.map_name == "hospital":
            L = hospital.LEADERS["meredith"]
            self.push(ui.Dialog(L["name"], ["Bom dia. Exaustão. Você apagou no meio da rua e te trouxeram pra cá.",
                                            "Você está bem. Mas, CEO: durma antes das duas. É uma ordem médica."],
                                self.portrait_for(self.npcs["meredith"]), subtitle=L["role"]))
        if self.weather == "chuva" and not self.storm:
            self.toasts.push("Está nevando em National City." if seasons.of_quarter(self.quarter) == "winter"
                             else "Está chovendo em National City.", (150, 190, 255))
        if self.weekday >= 5:
            self.toasts.push("Fim de semana! A cidade tem outra rotina hoje.", C_LILAC)
        f = festas.today(self)
        if f:
            self.toasts.push(f"Hoje: {f['name']} {f['place']}, {self.fmt_hour(f['start'])} às {self.fmt_hour(f['end'])}!", C_GOLD)
        for k in festas.birthday_today(self):
            self.toasts.push(f"Hoje é aniversário de {NPCS[k]['short']}!", C_PINK)
        clima.morning(self)                         # aviso de tempestade ou de arco-íris
        fundacao.morning(self)                      # obras novas na cidade, cesta da horta, inauguração
        eventos.morning(self)                       # livro do Theo (sábado) e marmita da Dona Graça (sexta)
        casamento.morning(self)                     # dia do casamento / anel no bolso
        casal.morning(self)                         # café da manhã juntas e o pedido do dia

    # ------------------------------------------------------------------
    # Salvar / carregar
    # ------------------------------------------------------------------
    def save(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        data = dict(
            version=SAVE_VERSION, city_layout=CITY_LAYOUT, quarter_days=DAYS_PER_QUARTER, day=self.day, quarter=self.quarter, year=self.year, minutes=self.minutes,
            money=self.money, energy=self.energy, inventory=self.inventory, selected=self.selected,
            stations=self.stations, friendship=self.friendship, talked=list(self.talked),
            gifted=list(self.gifted), gift_known=self.gift_known, flags=list(self.flags),
            events_seen=list(self.events_seen), stats=self.stats, stock=self.stock, stock_prev=self.stock_prev,
            shares=self.shares, shipped=self.shipped, request=self.request, weather=self.weather,
            weather_tomorrow=self.weather_tomorrow, map=self.map_name,
            player=(list(self.player.seat["back"]) if self.player.seat else
                    [self.player.x, self.player.y, self.player.dir]), coffee_today=self.coffee_today,
            fish_caught=list(self.fish_caught), aquarium=list(self.aquarium), cooked=list(self.cooked),
            dating=self.dating, partner=self.partner, proposal=self.proposal, ricci_coffee=self.ricci_coffee, milany_visit=self.milany_visit, date=self.date, scenes_seen=self.scenes_seen,
            talk_log=list(self.talk_log), lines_seen=self.lines_seen,
        )
        data.update(activities.save_state(self))
        data.update(marina.save_state(self))
        data.update(hospital.save_state(self))
        data.update(festas.save_state(self))
        data.update(casal.save_state(self))
        data.update(clima.save_state(self))
        data.update(jogos.save_state(self))
        data.update(closet.save_state(self))
        data.update(decor.save_state(self))
        data.update(album.save_state(self))
        data.update(fundacao.save_state(self))
        data.update(momentos.save_state(self))
        data.update(casamento.save_state(self))
        data.update(historia.save_state(self))
        data["crowd"] = self.crowd.to_save()
        tmp = SAVE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, SAVE_PATH)

    def has_save(self):
        return os.path.exists(SAVE_PATH)

    def load(self):
        with open(SAVE_PATH, encoding="utf-8") as f:
            d = json.load(f)
        self.reset_state()
        for k in ("day", "quarter", "year", "minutes", "money", "energy", "selected", "stock", "stock_prev",
                  "request", "weather", "weather_tomorrow", "coffee_today", "shares", "dating", "partner", "date", "proposal", "ricci_coffee", "milany_visit"):
            if k in d:
                setattr(self, k, d[k])
        inv = [list(s) if s and s[0] in ITEMS else None for s in d.get("inventory", [])]
        self.inventory = (inv + [None] * INVENTORY_SIZE)[:INVENTORY_SIZE]
        for i, s in enumerate(d.get("stations", [])[:MAX_STATIONS]):
            self.stations[i].update(s)
        for k, v in d.get("friendship", {}).items():
            if k in self.friendship:
                self.friendship[k] = v
        self.talked, self.gifted = set(d.get("talked", [])), set(d.get("gifted", []))
        for k, v in d.get("gift_known", {}).items():
            if k in self.gift_known:
                self.gift_known[k] = {i: t for i, t in v.items() if i in ITEMS}
        self.flags, self.events_seen = set(d.get("flags", [])), set(d.get("events_seen", []))
        self.event_hinted = set()
        self.stats.update(d.get("stats", {}))
        self.fish_caught = set(d.get("fish_caught", []))
        self.aquarium = set(d.get("aquarium", []))
        self.cooked = set(d.get("cooked", []))
        self.scenes_seen = []
        for k in d.get("scenes_seen", []):          # saves antigos: "namoro_x" e "x_pedido" eram a mesma cena
            k = same_scene(k)
            if k not in self.scenes_seen:
                self.scenes_seen.append(k)
        self.talk_log = set(d.get("talk_log", []))
        self.lines_seen = dict(d.get("lines_seen", {}))
        activities.load_state(self, d)
        marina.load_state(self, d)
        hospital.load_state(self, d)
        festas.load_state(self, d)
        casal.load_state(self, d)
        clima.load_state(self, d)
        jogos.load_state(self, d)
        closet.load_state(self, d)
        decor.load_state(self, d)
        album.load_state(self, d)
        fundacao.load_state(self, d)
        momentos.load_state(self, d)
        casamento.load_state(self, d)
        historia.load_state(self, d)
        self.fix_quarter_len(d.get("quarter_days", 28))
        self.crowd.reset_day()
        self.crowd.load(d.get("crowd", {}))
        self.shipped = [s for s in d.get("shipped", []) if s[0] in ITEMS]
        self.map_name = d.get("map", "home")
        if self.map_name not in self.world:
            self.map_name = "home"
        px, py, pd = d.get("player", [None, None, "down"])
        if px is None or d.get("version", 1) < SAVE_VERSION:
            self.map_name = "home"
            self.player.place_tile(*HOME_BED, "down")
        else:
            self.player.x, self.player.y, self.player.dir = px, py, pd
        if d.get("city_layout", 1) < CITY_LAYOUT:
            self.migrate_city()
        self.plan_npcs()
        self.scene = "play"
        self.modals = []
        self.cars = []
        self.toasts.push(f"Bem-vinda de volta! {self.date_label()}", C_LILAC)
        if d.get("version", 1) < SAVE_VERSION:
            self.toasts.push("National City cresceu! Novos lugares e pessoas para conhecer.", C_GOLD)

    def fix_quarter_len(self, old):
        """Save de quando a estação tinha outro tamanho (28 dias): o dia passa a caber na estação de agora
        e os prazos guardados como "dia absoluto" andam junto."""
        if old == DAYS_PER_QUARTER:
            return
        old_abs = (self.year - START_YEAR) * 4 * old + (self.quarter - 1) * old + self.day
        self.day = max(1, min(DAYS_PER_QUARTER, self.day))
        delta = self.abs_day() - old_abs
        if self.request and "deadline" in self.request:
            self.request["deadline"] += delta
        mar = getattr(self, "marina", None) or {}
        if mar.get("order") and "deadline" in mar["order"]:
            mar["order"]["deadline"] += delta
        for k in ("sunset_day", "regatta_day"):
            if isinstance(mar.get(k), int):
                mar[k] += delta

    def migrate_city(self):
        """Save do mapa antigo (72x56): leva posições da cidade para o mapa ampliado."""
        city = self.world["city"]
        if self.map_name == "city":
            tx, ty = self.player.tile
            nx, ny = old_city_xy(tx, ty)
            self.player.x += (nx - tx) * TILE
            self.player.y += (ny - ty) * TILE
            if city.is_solid(*self.player.tile):
                self.player.place_tile(*CITY_DOORS["residencial"], "down")
                self.player.y += TILE
        moved = []
        for f in self.forage:
            if f[0] == "city":
                x, y = old_city_xy(f[1], f[2])
                if city.is_solid(x, y) or city.object_at(x, y):
                    continue
                f = [f[0], x, y, f[3]]
            moved.append(f)
        self.forage = moved
        self.toasts.push("National City ficou maior: conheça o Bosque Bayside e o Jardim do Mirante!", C_GOLD)

    # ------------------------------------------------------------------
    # Tela de título
    # ------------------------------------------------------------------
    def title_options(self):
        opts = ["Novo jogo"]
        if self.has_save():
            opts.insert(0, "Continuar")
        fs = "Sim" if self.settings.get("fullscreen") else "Não"
        return opts + [f"Tela cheia: {fs}", "Controles", "Sair"]

    def handle_title(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        opts = self.title_options()
        if ev.key in (pygame.K_UP, pygame.K_w):
            self.title_sel = (self.title_sel - 1) % len(opts)
        elif ev.key in (pygame.K_DOWN, pygame.K_s):
            self.title_sel = (self.title_sel + 1) % len(opts)
        elif ev.key in ui.CONFIRM:
            choice = opts[self.title_sel % len(opts)]
            if choice == "Continuar":
                def go():
                    try:
                        self.load()
                    except Exception as e:
                        self.scene = "title"
                        self.toasts.push(f"Não foi possível carregar o jogo salvo ({e}).", C_RED)
                self.start_fade(go)
            elif choice == "Novo jogo":
                if self.has_save():
                    self.push(ui.Choice("Começar um novo jogo? O jogo salvo atual será substituído na próxima noite.",
                                        ["Sim, novo jogo", "Cancelar"],
                                        lambda i: self.start_fade(self.new_game) if i == 0 else None))
                else:
                    self.start_fade(self.new_game)
            elif choice.startswith("Tela cheia"):
                self.toggle_fullscreen()
            elif choice == "Controles":
                self.push(ui.InfoPanel("Controles", draw_controls))
            elif choice == "Sair":
                self.running = False
        elif ev.key == pygame.K_ESCAPE:
            self.running = False

    def draw_title(self, surf):
        m = self.world["city"]
        mw = m.w * TILE
        cx = (math.sin(self.t * 0.04) * 0.5 + 0.5) * (mw - SCREEN_W)
        cam = (int(cx), int(4.2 * TILE))
        self.draw_world(surf, m, cam, with_player=False, minutes=20 * 60 + 30)
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((8, 4, 18, 140))
        surf.blit(veil, (0, 0))
        logo = art.load_logo(112)
        surf.blit(logo, (SCREEN_W // 2 - logo.get_width() // 2, 60))
        ui.text(surf, "LUTHOR LIFE", (SCREEN_W // 2, 178), 68, C_TEXT, bold=True, center=True)
        ui.text(surf, "Uma vida executiva em National City", (SCREEN_W // 2, 262), 22, C_LILAC, center=True)
        opts = self.title_options()
        self.title_sel %= len(opts)
        y = 320
        for i, o in enumerate(opts):
            r = pygame.Rect(SCREEN_W // 2 - 160, y, 320, 44)
            if i == self.title_sel:
                pygame.draw.rect(surf, C_ACCENT, r, border_radius=22)
                pygame.draw.rect(surf, C_ACCENT_2, r, 2, border_radius=22)
            ui.text(surf, o, (r.centerx, r.y + 9), 22, C_TEXT if i == self.title_sel else C_MUTED, bold=True,
                    center=True)
            y += 52
        ui.text(surf, "Setas: escolher   Enter: confirmar   F11: tela cheia", (SCREEN_W // 2, SCREEN_H - 36), 16,
                C_MUTED, center=True)

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def zoom_for(self, m):
        return 1.0 if m.outdoor else 1.5

    def view_size(self, m):
        z = self.zoom_for(m)
        return int(SCREEN_W / z) // 2 * 2, int(SCREEN_H / z) // 2 * 2

    def camera(self, m):
        vw, vh = self.view_size(m)
        mw, mh = m.w * TILE, m.h * TILE
        if mw <= vw:
            cx = (mw - vw) // 2
        else:
            cx = int(min(max(self.player.x - vw / 2, 0), mw - vw))
        if mh <= vh - 40:
            cy = (mh - vh) // 2 + 20
        else:
            cy = int(min(max(self.player.y - 20 - vh / 2, 0), mh - vh))
        return cx // 2 * 2, cy // 2 * 2

    def render_map(self, surf, m, cam, **kw):
        """Desenha o mapa. Interiores usam zoom 1,5x (pixels continuam nítidos)."""
        z = self.zoom_for(m)
        if z == 1.0:
            self.draw_world(surf, m, cam, **kw)
            return
        vw, vh = self.view_size(m)
        if getattr(self, "_view", None) is None or self._view.get_size() != (vw, vh):
            self._view = pygame.Surface((vw, vh))
        self.draw_world(self._view, m, cam, **kw)
        big = pygame.transform.scale(self._view, (int(vw * z), int(vh * z)))
        surf.fill((6, 4, 10))
        surf.blit(big, ((SCREEN_W - big.get_width()) // 2, (SCREEN_H - big.get_height()) // 2))

    def darkness(self, minutes):
        if minutes < 7 * 60:
            return 0.35 * (7 * 60 - minutes) / 60
        if minutes < 18 * 60:
            return 0.0
        if minutes < 21 * 60:
            return 0.7 * (minutes - 18 * 60) / 180
        return 0.7

    def sunset(self, minutes):
        if 16 * 60 + 30 <= minutes <= 20 * 60:
            peak = 18 * 60 + 30
            return max(0.0, 1 - abs(minutes - peak) / 90.0)
        return 0.0

    def _make_glow(self, r):
        s = pygame.Surface((r * 2, r * 2))
        s.fill((0, 0, 0))
        for i in range(r, 0, -2):
            k = (1 - i / r) ** 1.8 * 0.55
            pygame.draw.circle(s, (int(255 * k), int(200 * k), int(120 * k)), (r, r), i)
        return s

    def _make_clouds(self):
        s = pygame.Surface((520, 260), pygame.SRCALPHA)
        for (x, y, w, h) in [(40, 60, 260, 120), (180, 30, 240, 140), (300, 90, 200, 110), (110, 120, 220, 100)]:
            pygame.draw.ellipse(s, (0, 0, 30, 14), (x, y, w, h))
        return s

    def draw_world(self, surf, m, cam, with_player=True, minutes=None, actors=None, weather=None, extra=None):
        minutes = self.minutes if minutes is None else minutes
        weather = self.weather if weather is None else weather
        SW, SH = surf.get_size()
        open_air = m.outdoor or getattr(m, "open_air", False)
        if getattr(m, "open_air", False):
            activities.draw_backdrop(self, surf, m, minutes)
        else:
            surf.fill((6, 4, 10))
        surf.blit(m.floor_surface, (-cam[0], -cam[1]))
        wf = int(self.t * 3) % 3
        x0, y0 = cam[0] // TILE - 1, cam[1] // TILE - 1
        x1, y1 = x0 + SW // TILE + 3, y0 + SH // TILE + 3
        for (x, y, t) in m.anim_tiles:
            if x0 <= x <= x1 and y0 <= y <= y1:
                name = "water" if t == "fountain" else t
                surf.blit(art.tile(name, (wf + x + y) % 3), (x * TILE - cam[0], y * TILE - cam[1]))
        wf2 = int(self.t * 2) % 2
        for (x, y, side) in m.water_edges:
            if x0 <= x <= x1 and y0 <= y <= y1:
                surf.blit(art.water_edge(side, wf2), (x * TILE - cam[0], y * TILE - cam[1]))
        dark = self.darkness(minutes)
        night = dark > 0.3
        for o in m.wall_decor:
            spr = (hospital.sign_sprite(o.data) if o.kind == "hsign"
                   else album.wall_image(self, o) or art.object_sprite(o.kind, night))
            surf.blit(spr, (o.x * TILE - cam[0], (o.y + o.h) * TILE - spr.get_height() - cam[1]))
        self.ambient.draw_window_light(surf, m, cam, minutes)
        activities.draw_ground(self, surf, m, cam)
        if m.name == "city":
            self.pigeons.draw(surf, cam, False)
        animacoes.draw_ground(self, surf, m, cam)
        items = []
        for o in m.objects:
            if o.layer == "obj":
                items.append((o.base_y - (14 if not o.solid else 0), 0, "obj", o))
        for b in m.buildings:
            items.append((b.base_y, 0, "bld", b))
        if actors is not None:
            for a in actors:
                items.append((a.base_y + getattr(a, "zbias", 0), 1, "actor", a))
        elif with_player:
            for npc in self.npcs.values():
                if npc.map == m.name:
                    items.append((npc.base_y, 1, "npc", npc))
            items.append((self.player.seat["sort"] if self.player.seat else self.player.y, 1, "player", self.player))
            items.extend(activities.world_items(self, m))
            items.extend(animacoes.world_items(self, m))
            for e in self.crowd.on_map(m.name):
                items.append((e.base_y, 1, "extra", e))
        if m.name == "city":
            for c in self.cars:
                items.append((c.base_y, 1, "car", c))
        items.sort(key=lambda it: (it[0], it[1]))
        near_staff, nd = None, TILE * 2.6
        for _, _, kind, e in items:
            if kind == "extra" and e.label:
                d = math.hypot(self.player.x - (e.fx + 0.5) * TILE, self.player.y - e.base_y)
                if d < nd:
                    near_staff, nd = e, d
        lamps = []
        windows = []        # prédios com janelas acesas (viram luz no escuro)
        neon = []           # prédios com letreiro luminoso (redesenhados depois de escurecer)
        behind = None       # a jogadora atrás de uma árvore deixa a copa transparente
        if with_player and actors is None and m.outdoor:
            pr = self.player
            behind = pygame.Rect(int(pr.x - cam[0]) - 8 * SCALE, int(pr.y - cam[1]) - 30 * SCALE, 16 * SCALE, 30 * SCALE)
        for _, _, kind, e in items:
            if kind == "obj":
                spr = self.object_image(e)
                x = e.x * TILE + (e.w * TILE - spr.get_width()) // 2 - cam[0]
                y = e.base_y - spr.get_height() - cam[1]
                if x > SW or y > SH or x + spr.get_width() < 0 or y + spr.get_height() < 0:
                    continue
                if e.kind in SHADOW_KINDS:
                    draw_shadow(surf, x + spr.get_width() // 2, e.base_y - cam[1] - 2, SHADOW_KINDS[e.kind] * SCALE // 3)
                if e.kind in scenery.TREE_KINDS and behind is not None and self.player.y < e.base_y and behind.colliderect(
                        (x + 4 * SCALE, y, spr.get_width() - 8 * SCALE, spr.get_height() - 14 * SCALE)):
                    spr = scenery.faded(e.kind)
                surf.blit(spr, (x, y))
                if e.kind == "lamp":
                    lamps.append((x + spr.get_width() // 2, y + 7 * SCALE))
                elif e.kind == "lighthouse":
                    lamps.append((x + spr.get_width() // 2, y + 18 * SCALE))
                elif e.kind == "aquarium":
                    self.draw_aquarium_fish(surf, x, y)
                elif e.kind == "station":
                    st = self.stations[e.data]
                    if st["project"] and st["progress"] >= self.project_days(st["project"]):
                        bob = math.sin(self.t * 4 + e.data) * 4
                        ic = art.item_icon(st["project"], 2)
                        bx, by = x + TILE // 2, int(y - TILE * 0.4 + bob)
                        pygame.draw.circle(surf, (255, 255, 255), (bx, by), 20)
                        pygame.draw.circle(surf, C_ACCENT_2, (bx, by), 20, 2)
                        surf.blit(ic, (bx - 16, by - 16))
            elif kind == "bld":
                drawn = self.draw_building(surf, e, cam, night)
                if drawn and night:
                    windows.append(drawn)
                    if e.style in lighting.NEON_STYLES:
                        neon.append(e)
            elif kind == "car":
                e.draw(surf, cam)
            else:
                e.draw(surf, cam)
                bkey = e.key if kind == "npc" else (e.name if kind == "actor" else None)
                if bkey and festas.is_birthday(self, bkey):
                    festas.draw_npc_extra(self, surf, e, cam, bkey)
                if kind == "npc" and getattr(e, "emote", None):
                    from .cutscenes import draw_emote
                    img_h = e.frames[("down", 0)].get_height()
                    draw_emote(surf, int((e.fx + 0.5) * TILE - cam[0]), int(e.base_y - img_h - 4 - cam[1]), e.emote,
                               1 - max(0, e.emote_t - 1.0))
                if kind == "npc":
                    d = math.hypot(self.player.x - (e.fx + 0.5) * TILE, self.player.y - e.base_y)
                    if d < TILE * 2.6:
                        col = C_PINK if e.key in ROMANCES else C_LILAC
                        ui.text(surf, e.data["short"], (int((e.fx + 0.5) * TILE - cam[0]),
                                                        int(e.base_y - 34 * SCALE - cam[1])), 15, col, bold=True, center=True)
                elif kind == "extra" and e.label and e is near_staff:
                    if True:
                        ui.text(surf, e.label, (int((e.fx + 0.5) * TILE - cam[0]), int(e.base_y - 34 * SCALE - cam[1])),
                                14, hospital.CMH_GREEN, bold=True, center=True)
                elif kind == "player":
                    animacoes.draw_player_extra(self, surf, cam)     # vara de pesca, regador, peixe erguido
                    if self.fishing:
                        self.draw_fishing(surf, cam)
        for p in self.particles:
            p.draw(surf, cam)
        festas.lights(self, m, cam, lamps)
        if m.name == self.map_name and with_player:
            self.draw_eat_fx(surf, cam)
            self.draw_kiss_fx(surf, cam)
        if m.name in ("bayside", "residencial"):
            self.draw_apt_plates(surf, cam)
        if m.name == "city":
            self.pigeons.draw(surf, cam, True)
        animacoes.draw_sky(self, surf, m, cam)
        self.ambient.draw_world(surf, cam)
        if extra is not None:
            extra.draw(surf, cam)
        rain = weather == "chuva" and open_air and (with_player or actors is not None)
        if rain and actors is None and self.storm and seasons.CURRENT["season"] != "winter":
            rain = "storm"
        sun = self.sunset(minutes) if open_air else 0
        lighting.apply(self, surf, m, cam, dark, sun, rain, open_air, lamps, windows,
                       self.player if with_player and actors is None else None,
                       self.cars if m.name == "city" else [])
        for b in neon:
            self.draw_building(surf, b, cam, True, signs_only=True)
        self.ambient.draw_glow(surf, cam)
        if open_air and seasons.CURRENT["season"] == "winter" and (with_player or actors is not None):
            self.ambient.draw_snow(surf)
        elif rain:
            clima.draw_rain(surf, self.t, rain == "storm")
        if with_player and actors is None and m.name == self.map_name:
            if open_air and weather != "chuva":
                clima.draw_rainbow(self, surf, minutes)
            clima.draw_flash(self, surf, open_air)

    def draw_aquarium_fish(self, surf, x, y):
        for i, k in enumerate(sorted(self.aquarium)):
            fx = x + 4 * SCALE + (math.sin(self.t * (0.6 + i * 0.13) + i * 1.7) * 0.5 + 0.5) * 34 * SCALE
            fy = y + 5 * SCALE + (i * 11) % (12 * SCALE)
            c = FISH[k]["color"]
            pygame.draw.ellipse(surf, c, (int(fx), int(fy), 12, 6))
            pygame.draw.polygon(surf, c, [(int(fx) - 4, int(fy)), (int(fx), int(fy) + 3), (int(fx) - 4, int(fy) + 6)])

    def draw_fishing(self, surf, cam):
        """O "!" da mordida (a vara, a linha e a boia ficam em animacoes.draw_rod)."""
        f = self.fishing
        if f["phase"] == "bite":
            py = self.player.y - cam[1] - 14 * SCALE
            r = pygame.Rect(int(self.player.x - cam[0]) - 16, int(py) - 22 * SCALE, 32, 36)
            pygame.draw.rect(surf, (255, 255, 255), r, border_radius=8)
            pygame.draw.rect(surf, C_RED, r, 3, border_radius=8)
            ui.text(surf, "!", (r.centerx, r.y + 2), 28, C_RED, bold=True, center=True, shadow=False)

    def object_image(self, o):
        img = album.object_image(self, o) or festas.object_image(self, o) or scenery.object_image(self, o)
        if img is not None:
            return img
        if o.kind == "plot":
            return activities.plot_image(self, o)
        if o.kind == "station":
            st = self.stations[o.data]
            if not st["unlocked"]:
                return art.station_sprite("locked")
            if st["project"] is None:
                return art.station_sprite("empty")
            p = PROJECTS[st["project"]]
            prog = min(1.0, (st["progress"] + (1 if st["worked"] else 0)) / self.project_days(st["project"]))
            state = "ready" if st["progress"] >= self.project_days(st["project"]) else "active"
            return art.station_sprite(state, p["color"], st["worked"] or state == "ready", prog)
        return art.object_sprite(o.kind)

    def draw_building(self, surf, b, cam, night, signs_only=False):
        spr = art.building_sprite(b.style, b.w, b.h, b.extra, night)
        x = b.x * TILE - cam[0]
        y = b.base_y - spr.get_height() - cam[1]
        if x > SCREEN_W or x + spr.get_width() < 0 or y > SCREEN_H or y + spr.get_height() < 0:
            return None
        if not signs_only:
            surf.blit(spr, (x, y))
        if caprichado.draw_label(self, surf, b, spr, x, y, night):
            return spr, x, y
        cx = x + spr.get_width() // 2
        H = spr.get_height()
        if b.style == "tower":
            ui.text(surf, "LUTHOR CORP", (cx, y + H - 48 * SCALE + 7), 26, C_LILAC, bold=True, center=True)
        elif b.style == "catco":
            logo = art.load_image("catco.png", (28 * SCALE, 28 * SCALE))
            if logo:
                surf.blit(logo, (cx - 14 * SCALE, y - 6 * SCALE))
            ui.text(surf, "CATCO", (cx, y + H - 44 * SCALE + 6), 24, (30, 60, 104), bold=True, center=True, shadow=False)
        elif b.style == "cafe":
            ui.text(surf, "GRÃO NOBRE", (cx, y + 8 * SCALE + 1), 16, (250, 236, 210), bold=True, center=True)
        elif b.style == "home":
            ui.text(surf, "RESIDENCIAL LUTHOR", (cx, y + 5 * SCALE + 1), 15, (250, 230, 220), bold=True, center=True)
        elif b.style == "books":
            ui.text(surf, "BAYSIDE BOOKS", (cx, y + 6 * SCALE + 1), 16, (250, 236, 200), bold=True, center=True)
        elif b.style == "market":
            ui.text(surf, "MERCADO CENTRAL", (cx, y + 6 * SCALE + 1), 15, (250, 250, 230), bold=True, center=True)
        elif b.style == "trattoria":
            ui.text(surf, "RICCI TRATTORIA", (cx, y + 4 * SCALE + 2), 16, (255, 246, 230), bold=True, center=True)
        elif b.style == "bar":
            col = (255, 90, 150) if night or int(self.t * 2) % 7 else (120, 60, 90)
            ui.text(surf, "NOONAN'S", (cx, y + H - 44 * SCALE + 5), 24, col, bold=True, center=True)
        elif b.style == "cinema":
            ui.text(surf, "CINE NATIONAL", (cx, y + H - 52 * SCALE + 6), 20, (255, 230, 140), bold=True, center=True)
        elif b.style == "bank":
            ui.text(surf, "BANCO", (cx, y + 13 * SCALE), 15, (90, 80, 60), bold=True, center=True, shadow=False)
        elif b.style == "marina":
            ui.text(surf, "MARINA LUTHOR", (cx, y + 41 * SCALE - 1), 16, (240, 214, 140), bold=True, center=True,
                    shadow=False)
        elif b.style == "ricci":
            ui.text(surf, "GRUPPO RICCI", (cx, y + H - 44 * SCALE + 1), 16, (240, 214, 140), bold=True, center=True,
                    shadow=False)
        elif b.style == "hospital":
            logo = art.load_image("cmh.png", (18 * SCALE, 18 * SCALE))
            if logo:
                surf.blit(logo, (cx - 9 * SCALE, y + H - 56 * SCALE - 9 * SCALE))
            ui.text(surf, "CONTI MORETTI HOSPITAIS", (cx, y + 3 * SCALE + 3), 17, (246, 243, 236), bold=True, center=True)
            ui.text(surf, "CONTI MORETTI", (cx, y + H - 40 * SCALE + 1), 19, (246, 243, 236), bold=True, center=True)
        return spr, x, y

    def draw(self, surf):
        cut = next((i for i, mo in enumerate(self.modals) if isinstance(mo, Cutscene)), None)
        if cut is not None and self.scene == "play":
            for mo in self.modals[cut:]:
                mo.draw(surf)
            self.toasts.draw(surf)
            return
        if self.scene == "title":
            self.draw_title(surf)
        elif self.scene == "summary":
            self.draw_summary(surf)
        else:
            m = self.current_map
            cam = self.camera(m)
            self.render_map(surf, m, cam)
            if self.photo_mode:                     # modo foto: nada de interface por cima
                animacoes.draw_photo(self, surf)
                for mo in self.modals:
                    mo.draw(surf)
                if self.fade > 0:
                    veil = pygame.Surface((SCREEN_W, SCREEN_H))
                    veil.fill((0, 0, 0))
                    veil.set_alpha(int(255 * self.fade))
                    surf.blit(veil, (0, 0))
                return
            dialog_open = any(isinstance(x, ui.Dialog) for x in self.modals)
            ui.draw_hud(surf, self)
            hy = 206
            if self.date and not self.date.get("done"):
                ui.text(surf, f"Encontro 20h: {NPCS[self.date['npc']]['short']}", (SCREEN_W - 24, hy), 15, C_PINK,
                        bold=True, right=True)
                hy += 22
            if self.request:
                rq = self.request
                have = min(self.count_item(rq["item"]), rq["qty"])
                ok = have >= rq["qty"]
                ui.text(surf, f"Pedido {NPCS[rq['npc']]['short']}: {ITEMS[rq['item']]['name']} {have}/{rq['qty']}",
                        (SCREEN_W - 24, hy), 15, C_GREEN if ok else C_GOLD, bold=True, right=True)
                hy += 20
            mo = self.marina.get("order")
            if mo:
                ok = self.count_item(mo["item"]) >= mo["qty"]
                ui.text(surf, marina.order_text(self), (SCREEN_W - 24, hy), 15, C_GREEN if ok else (120, 190, 240),
                        bold=True, right=True)
                hy += 20
            if self.proposal and not self.dating:
                ui.text(surf, f"Pedido {NPCS[self.proposal]['short']}: {self.proposal_text()}",
                        (SCREEN_W - 24, hy), 15, C_PINK, bold=True, right=True)
                hy += 20
            for txt, col in (festas.hud_lines(self) + casamento.hud_lines(self) + casal.hud_lines(self)
                             + fundacao.hud_lines(self) + historia.hud_lines(self)):
                ui.text(surf, txt, (SCREEN_W - 24, hy), 15, col, bold=True, right=True)
                hy += 20
            for key, h, ev in [e for e in self.pending_scene_events() if e[1] > 0][:2]:   # 0 corações: escondido
                where, a, b = self.scene_place(ev["scene"])
                ui.text(surf, f"Evento {NPCS[key]['short']}: {where} ({self.fmt_hour(a)} a {self.fmt_hour(b)})",
                        (SCREEN_W - 24, hy), 15, C_PINK, bold=True, right=True)
                hy += 20
            if not dialog_open:
                ui.draw_hotbar(surf, self)
                if not self.modals and not self.fade_dir and not self.fishing:
                    target = self.resolve_target() or (("seat", None) if self.player.seat else None)
                    if target:
                        label = self.target_label(target)
                        w = ui.font(17, True).size(label)[0] + 50
                        ry = SCREEN_H - (170 if self.hotbar_label_t > 0 else 128)
                        r = pygame.Rect(SCREEN_W // 2 - w // 2, ry, w, 32)
                        ui.panel(surf, r, alpha=210, radius=16)
                        key = pygame.Rect(r.x + 8, r.y + 5, 22, 22)
                        pygame.draw.rect(surf, C_ACCENT, key, border_radius=5)
                        ui.text(surf, "E", (key.centerx, key.y + 1), 16, C_TEXT, bold=True, center=True, shadow=False)
                        ui.text(surf, label, (r.x + 38, r.y + 5), 17, C_TEXT, bold=True)
                elif self.fishing and not self.modals:
                    msg = "Aperte E AGORA!" if self.fishing["phase"] == "bite" else "Esperando o peixe morder... (E recolhe)"
                    w = ui.font(17, True).size(msg)[0] + 30
                    r = pygame.Rect(SCREEN_W // 2 - w // 2, SCREEN_H - 128, w, 32)
                    ui.panel(surf, r, alpha=210, radius=16, border=C_RED if self.fishing["phase"] == "bite" else None
                             or (150, 90, 230))
                    ui.text(surf, msg, (r.centerx, r.y + 5), 17, C_TEXT, bold=True, center=True)
        self.toasts.draw(surf)
        for mo in self.modals:
            mo.draw(surf)
        if self.fade > 0:
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.fill((0, 0, 0))
            veil.set_alpha(int(255 * self.fade))
            surf.blit(veil, (0, 0))

    def draw_summary(self, surf):
        surf.fill((10, 6, 18))
        s = self.summary
        d, q, y = s["date"]
        ui.text(surf, "Fim do dia", (SCREEN_W // 2, 34), 40, C_TEXT, bold=True, center=True)
        ui.text(surf, self.date_label(d, q, y), (SCREEN_W // 2, 88), 20, C_LILAC, center=True)
        r = pygame.Rect(260, 130, SCREEN_W - 520, 330)
        ui.panel(surf, r)
        ui.text(surf, "Vendas da noite", (r.x + 24, r.y + 16), 20, C_LILAC, bold=True)
        yy = r.y + 52
        if not s["table"]:
            ui.text(surf, "Nada vendido hoje.", (r.x + 24, yy), 18, C_MUTED)
        for item, n, val in s["table"][:6]:
            surf.blit(art.item_icon(item, 2), (r.x + 22, yy - 4))
            ui.text(surf, f"{n}x {ITEMS[item]['name']}", (r.x + 64, yy), 18)
            ui.text(surf, f"$ {val:,}".replace(",", "."), (r.right - 24, yy), 18, C_GOLD, right=True)
            yy += 34
        if len(s["table"]) > 6:
            ui.text(surf, f"+ {len(s['table']) - 6} outros itens", (r.x + 64, yy), 16, C_MUTED)
        pygame.draw.line(surf, (80, 60, 110), (r.x + 20, r.bottom - 60), (r.right - 20, r.bottom - 60))
        ui.text(surf, "Total", (r.x + 24, r.bottom - 46), 22, C_TEXT, bold=True)
        ui.text(surf, f"$ {s['earnings']:,}".replace(",", "."), (r.right - 24, r.bottom - 46), 22, C_GOLD,
                bold=True, right=True)
        a, b = s["stock"]
        col = C_GREEN if b >= a else C_RED
        sign = "+" if b >= a else ""
        ui.text(surf, f"LCORP: $ {a:.2f}  ->  $ {b:.2f}  ({sign}{b - a:.2f})".replace(".", ","), (SCREEN_W // 2, 478),
                19, col, bold=True, center=True)
        yy = 514
        for msg, color in s["notes"][:5]:
            ui.text(surf, msg, (SCREEN_W // 2, yy), 17, color, center=True)
            yy += 26
        if int(self.t * 2) % 2 == 0:
            ui.text(surf, "Jogo salvo. Pressione Enter para começar o novo dia.", (SCREEN_W // 2, SCREEN_H - 34),
                    17, C_MUTED, center=True)


def mix_rgb(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade_rgb(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


class Particle:
    def __init__(self, x, y, color, size=5):
        a = random.uniform(0, math.tau)
        sp = random.uniform(40, 140)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp - 120
        self.life = random.uniform(0.5, 0.9)
        self.color = color
        self.size = size

    def update(self, dt):
        self.life -= dt
        self.vy += 300 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.life > 0

    def draw(self, surf, cam):
        pygame.draw.rect(surf, self.color, (int(self.x - cam[0]), int(self.y - cam[1]), self.size, self.size))


def draw_controls(surf, rect):
    rows = [
        ("WASD / setas", "Andar (segure Shift para andar devagar)"),
        ("E / Espaço / clique", "Interagir, conversar, trabalhar, pescar"),
        ("1-9, 0, -, =", "Escolher item da barra"),
        ("Roda do mouse", "Trocar item da barra"),
        ("I / Tab", "Abrir a mochila (24 espaços)"),
        ("O / R", "Objetivos / relacionamentos"),
        ("M / C", "Mapa da cidade / calendário (festas e aniversários)"),
        ("F / botão direito", "Comer, beber ou ler o item escolhido"),
        ("P", "Modo foto (sem interface; Enter tira a foto)"),
        ("Esc", "Menu: objetivos, relacionamentos, coleções, opções"),
        ("F11", "Tela cheia"),
        ("Setas / D F J K", "Karaokê no Noonan's (à noite, na jukebox)"),
    ]
    y = rect.y + 70
    for k, v in rows:
        ui.text(surf, k, (rect.x + 34, y), 18, C_LILAC, bold=True)
        ui.text(surf, v, (rect.x + 260, y), 18, C_TEXT)
        y += 34
    y += 6
    for line in ui.wrap("Pesca: com a vara selecionada, fique de frente para a água e aperte E. Quando aparecer o '!', "
                        "aperte E. No minigame, segure Espaço para manter o peixe dentro da barra verde.", 16,
                        rect.w - 70):
        ui.text(surf, line, (rect.x + 34, y), 16, C_MUTED)
        y += 22

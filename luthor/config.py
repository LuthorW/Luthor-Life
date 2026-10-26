"""Constantes globais do Luthor Life."""
import os

TITLE = "Luthor Life"
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

TS = 16          # tamanho do tile em pixels de arte
SCALE = 2        # fator de ampliação (pixel art)  — 2 = câmera mais afastada
TILE = TS * SCALE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE_DIR, "assets")
SAVE_DIR = os.path.join(BASE_DIR, "saves")
SAVE_PATH = os.path.join(SAVE_DIR, "save.json")
SETTINGS_PATH = os.path.join(SAVE_DIR, "settings.json")
SAVE_VERSION = 2

# Tempo
DAY_START = 6 * 60          # 06:00
DAY_END = 26 * 60           # 02:00 do dia seguinte
SECONDS_PER_10MIN = 7.0     # segundos reais para 10 minutos de jogo
DAYS_PER_QUARTER = 28
START_YEAR = 2034
WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
WEEKDAYS_FULL = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]

# Jogadora
BASE_ENERGY = 100
FISH_ENERGY = 4
ARCADE_ENERGY = 6
INVENTORY_SIZE = 24
HOTBAR_SIZE = 12
WORK_ENERGY = 5
WALK_SPEED = 3.6 * TILE     # px/s
RUN_SPEED = 5.2 * TILE

# Amizade
HEART_POINTS = 250
MAX_HEARTS = 10
ROMANCE_CAP_HEARTS = 8      # sem namorar, o romance trava em 8 corações
TALK_POINTS = 20
GIFT_POINTS = {"love": 80, "like": 45, "neutral": 20, "dislike": -20}

# Laboratório
START_STATIONS = 4
MAX_STATIONS = 12

# Paleta da interface (identidade Luthor Corp)
C_BG = (7, 5, 11)
C_PANEL = (22, 16, 32)
C_PANEL_2 = (34, 24, 50)
C_BORDER = (150, 90, 230)
C_BORDER_DIM = (80, 56, 112)
C_ACCENT = (138, 0, 230)
C_ACCENT_2 = (184, 76, 255)
C_TEXT = (246, 240, 255)
C_MUTED = (182, 169, 197)
C_LILAC = (223, 197, 255)
C_GOLD = (255, 214, 102)
C_GREEN = (110, 231, 140)
C_RED = (248, 113, 113)
C_ENERGY = (124, 222, 120)
C_PINK = (255, 140, 190)

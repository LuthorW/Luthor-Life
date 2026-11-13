"""Escritórios: o da Letícia na sede da Luthor Corp (sala de carpete roxo, no canto de cima à esquerda).

Móveis novos, todos em pixel art procedural:
- mesa de CEO em nogueira com friso dourado, o "L" roxo na frente, o monitor (de costas) e um abajur de banqueiro;
- cadeira executiva de couro roxo (`cadeira_ceo`), atrás da mesa;
- cadeiras de couro com pés cromados (`cadeira_reuniao`) para visitas e para a mesa de reuniões;
- retrato do pai dela, Alexander Luthor (`quadro_alexander`), na parede;
- aparador com porta-retrato, orquídea, troféu e livros; globo; carrinho de bar; tapete roxo com borda dourada;
Sala de reuniões própria, à direita do laboratório (`furnish_reunioes`): mesa grande (`mesa_reuniao`, 5x2) com dez
cadeiras e a cadeira da CEO na cabeceira, telão com o gráfico da LCORP e um cavalete. É lá que acontece a reunião do
conselho da história da Luthor Corp.

Gruppo Ricci (`furnish_ricci`): o escritório da Vittoria (mesa de mármore com o "R" dourado, cadeira de veludo verde,
foto da primeira Trattoria, oliveira) e a sala de projetos das casas novas no lugar da antiga cozinha de testes
(planta, painel de amostras, prancheta, maquete).

`furnish`, `furnish_reunioes` e `furnish_ricci` são chamados por `world.build_hq` / `world.build_ricci`.
"""
import pygame

from . import art, world, poses, assentos, lighting
from .art import new, R, P, shade, mix

WALNUT = (104, 62, 42)
GOLD = (214, 172, 82)
PURPLE = (124, 52, 188)
LEATHER = (92, 42, 126)          # couro roxo da cadeira da CEO
DARK_LEATHER = (58, 50, 70)      # couro das cadeiras de reunião
CHROME = (176, 178, 190)


# ---------------------------------------------------------------------------
# Mesa de CEO (3x1)
# ---------------------------------------------------------------------------
def _ceo_desk():
    s = new(48, 30)
    wood, top = WALNUT, shade(WALNUT, 1.25)
    # tampo
    R(s, top, 0, 11, 48, 4)
    R(s, shade(top, 1.18), 0, 11, 48, 1)
    R(s, shade(wood, 0.7), 0, 15, 48, 1)
    R(s, GOLD, 1, 16, 46, 1)                                      # friso dourado
    # gaveteiros dos lados e painel do meio, mais fundo
    R(s, wood, 1, 17, 46, 11)
    R(s, shade(wood, 0.78), 15, 17, 18, 11)
    for x0 in (2, 34):
        for y0 in (18, 23):
            R(s, shade(wood, 1.08), x0, y0, 12, 4)
            R(s, shade(wood, 0.82), x0, y0 + 4, 12, 1)
            R(s, GOLD, x0 + 5, y0 + 1, 2, 1)                       # puxador
    # placa com o "L" roxo
    R(s, GOLD, 20, 18, 8, 8)
    R(s, (46, 22, 64), 21, 19, 6, 6)
    R(s, (200, 140, 255), 22, 20, 1, 4); R(s, (200, 140, 255), 22, 23, 3, 1)
    R(s, shade(wood, 0.5), 0, 28, 48, 2)                          # rodapé
    R(s, shade(wood, 0.4), 1, 28, 2, 2); R(s, shade(wood, 0.4), 45, 28, 2, 2)
    # monitor (de costas para cá: a tela fica virada para a cadeira)
    R(s, (38, 38, 48), 6, 1, 17, 10)
    R(s, (58, 58, 72), 7, 2, 15, 8)
    R(s, (70, 70, 86), 7, 2, 15, 1)
    R(s, (150, 90, 220), 13, 5, 3, 2)                             # logo atrás do monitor
    R(s, (44, 44, 54), 13, 10, 3, 2)
    R(s, (90, 90, 106), 11, 12, 7, 1)
    # placa de mesa e porta-canetas
    R(s, (30, 26, 34), 25, 10, 8, 3)
    R(s, GOLD, 26, 11, 6, 1)
    R(s, (60, 60, 70), 34, 9, 2, 4); P(s, (230, 60, 60), 34, 8); P(s, (60, 120, 230), 35, 7)
    # abajur de banqueiro
    R(s, GOLD, 41, 6, 1, 6)
    R(s, shade(GOLD, 0.8), 38, 12, 7, 1)
    R(s, (34, 110, 74), 37, 3, 9, 3)
    R(s, (60, 150, 100), 38, 3, 7, 1)
    R(s, (255, 236, 160), 38, 6, 7, 1)                            # luz por baixo da cúpula
    return s


# ---------------------------------------------------------------------------
# Cadeira da CEO (couro roxo, encosto alto, rodinhas)
# ---------------------------------------------------------------------------
def _cadeira_ceo():
    s = new(16, 26)
    c = LEATHER
    R(s, shade(c, 0.8), 3, 1, 10, 16)                              # encosto alto
    R(s, c, 4, 0, 8, 16)
    R(s, shade(c, 1.2), 4, 0, 8, 1)
    for y in (4, 8, 12):                                            # capitonê
        for x in (6, 9):
            P(s, shade(c, 0.6), x, y)
    R(s, shade(c, 0.7), 1, 13, 3, 6); R(s, shade(c, 0.7), 12, 13, 3, 6)   # braços
    R(s, shade(c, 0.95), 1, 13, 3, 1); R(s, shade(c, 0.95), 12, 13, 3, 1)
    R(s, shade(c, 1.22), 4, 15, 8, 4)                              # assento
    R(s, shade(c, 1.4), 4, 15, 8, 1)
    R(s, CHROME, 7, 19, 2, 3)                                      # coluna e base em estrela
    R(s, shade(CHROME, 0.8), 3, 22, 10, 1)
    for x in (3, 7, 12):
        R(s, (40, 40, 46), x, 23, 2, 2)
    return s


def _ceo_up(part):
    """De costas: o encosto fica na frente de quem senta (mais baixo, para a cabeça aparecer)."""
    c = LEATHER
    s = new(16, 26)
    if part == "base":
        R(s, shade(c, 0.7), 1, 15, 3, 5); R(s, shade(c, 0.7), 12, 15, 3, 5)
        R(s, shade(c, 1.1), 4, 16, 8, 3)
        R(s, CHROME, 7, 19, 2, 3)
        R(s, shade(CHROME, 0.8), 3, 22, 10, 1)
        for x in (3, 7, 12):
            R(s, (40, 40, 46), x, 23, 2, 2)
        return s
    R(s, shade(c, 0.62), 3, 8, 10, 12)
    R(s, shade(c, 0.78), 4, 9, 8, 9)
    R(s, shade(c, 0.95), 3, 8, 10, 1)
    R(s, shade(c, 0.5), 7, 10, 2, 8)                                # costura
    return s


def _ceo_side(part):
    if part == "front":
        return None
    c = LEATHER
    s = new(16, 26)
    R(s, shade(c, 0.8), 2, 2, 4, 16)
    R(s, shade(c, 1.1), 2, 2, 4, 1)
    R(s, shade(c, 1.15), 3, 15, 10, 4)
    R(s, shade(c, 1.35), 3, 15, 10, 1)
    R(s, shade(c, 0.7), 5, 12, 7, 2)                               # braço
    R(s, CHROME, 7, 19, 2, 3)
    R(s, shade(CHROME, 0.8), 3, 22, 10, 1)
    for x in (3, 12):
        R(s, (40, 40, 46), x, 23, 2, 2)
    return s


# ---------------------------------------------------------------------------
# Cadeira de reunião (couro escuro, pés cromados)
# ---------------------------------------------------------------------------
def _cadeira_reuniao():
    s = new(16, 18)
    c = DARK_LEATHER
    R(s, shade(c, 0.85), 4, 2, 8, 9)
    R(s, c, 5, 2, 6, 8)
    R(s, shade(c, 1.25), 4, 2, 8, 1)
    R(s, shade(c, 1.3), 4, 9, 8, 3)
    R(s, shade(c, 1.5), 4, 9, 8, 1)
    R(s, CHROME, 4, 12, 1, 6); R(s, CHROME, 11, 12, 1, 6)
    R(s, shade(CHROME, 0.75), 5, 15, 6, 1)
    return s


# ---------------------------------------------------------------------------
# Retrato do Alexander Luthor (parede)
# ---------------------------------------------------------------------------
def _quadro_alexander():
    s = new(16, 20)
    R(s, shade(GOLD, 0.7), 1, 0, 14, 19)
    R(s, GOLD, 2, 1, 12, 17)
    R(s, shade(GOLD, 1.15), 2, 1, 12, 1)
    R(s, (40, 46, 52), 3, 2, 10, 15)                                # fundo escuro
    R(s, (54, 62, 70), 3, 2, 10, 4)
    R(s, (34, 34, 44), 3, 12, 10, 5)                                # terno
    R(s, (236, 236, 240), 7, 12, 2, 3)                              # camisa
    R(s, PURPLE, 7, 13, 2, 4)                                       # gravata roxa
    R(s, (224, 188, 160), 6, 6, 4, 6)                               # rosto
    R(s, (200, 164, 138), 6, 11, 4, 1)
    R(s, (184, 184, 192), 5, 4, 6, 3)                               # cabelo grisalho
    R(s, (184, 184, 192), 5, 6, 1, 3); R(s, (184, 184, 192), 10, 6, 1, 3)
    P(s, (40, 70, 50), 7, 8); P(s, (40, 70, 50), 9, 8)             # olhos verdes, como os dela
    P(s, (170, 120, 110), 8, 10)
    R(s, shade(GOLD, 0.55), 6, 18, 4, 1)                            # plaquinha
    return s


# ---------------------------------------------------------------------------
# Aparador (3x1): porta-retrato, orquídea, troféu e livros
# ---------------------------------------------------------------------------
def _aparador():
    s = new(48, 24)
    wood = WALNUT
    R(s, shade(wood, 1.3), 0, 9, 48, 3)
    R(s, shade(wood, 1.45), 0, 9, 48, 1)
    R(s, wood, 1, 12, 46, 10)
    for i in range(3):
        x0 = 2 + i * 15
        R(s, shade(wood, 1.1), x0, 13, 14, 8)
        R(s, shade(wood, 0.8), x0, 20, 14, 1)
        R(s, GOLD, x0 + 6, 16, 2, 1)
    R(s, shade(wood, 0.5), 2, 22, 2, 2); R(s, shade(wood, 0.5), 44, 22, 2, 2)
    # porta-retrato (a equipe)
    R(s, GOLD, 4, 2, 8, 7)
    R(s, (150, 196, 230), 5, 3, 6, 5)
    R(s, (90, 150, 90), 5, 6, 6, 2)
    P(s, (60, 40, 40), 6, 5); P(s, (230, 190, 90), 8, 5); P(s, (140, 90, 60), 10, 5)
    # orquídea branca num vaso branco
    R(s, (240, 240, 246), 19, 6, 6, 3)
    R(s, (60, 130, 70), 21, 1, 1, 5); R(s, (60, 130, 70), 18, 5, 3, 1)
    for (x, y) in ((22, 1), (23, 2), (20, 0), (24, 4)):
        R(s, (250, 236, 250), x, y, 2, 2)
        P(s, (210, 120, 200), x, y + 1)
    # troféu
    R(s, GOLD, 30, 2, 5, 3)
    R(s, shade(GOLD, 1.2), 30, 2, 5, 1)
    R(s, GOLD, 32, 5, 1, 2)
    R(s, (40, 36, 44), 30, 7, 5, 2)
    # livros deitados
    R(s, (130, 40, 60), 38, 7, 8, 2)
    R(s, (40, 70, 130), 39, 5, 7, 2)
    R(s, (60, 110, 80), 38, 3, 8, 2)
    R(s, (240, 230, 200), 45, 3, 1, 6)
    return s


# ---------------------------------------------------------------------------
# Globo, carrinho de bar e tapete
# ---------------------------------------------------------------------------
def _globo():
    s = new(16, 26)
    sea, land = (60, 112, 170), (96, 160, 92)
    pygame.draw.circle(s, shade(sea, 0.8), (8, 8), 6)
    pygame.draw.circle(s, sea, (7, 7), 5)
    R(s, land, 4, 5, 3, 3); R(s, land, 8, 9, 3, 2); R(s, land, 9, 4, 2, 2)
    P(s, (170, 210, 240), 5, 4)
    pygame.draw.arc(s, GOLD, (1, 1, 14, 15), 0.6, 4.6, 1)          # meridiano dourado
    R(s, shade(WALNUT, 1.2), 7, 15, 2, 5)                          # pé de madeira
    R(s, WALNUT, 3, 20, 10, 2)
    R(s, shade(WALNUT, 0.7), 3, 22, 2, 3); R(s, shade(WALNUT, 0.7), 11, 22, 2, 3)
    R(s, shade(WALNUT, 0.7), 7, 22, 2, 2)
    return s


def _carrinho_bar():
    s = new(16, 24)
    frame = GOLD
    R(s, frame, 1, 6, 1, 16); R(s, frame, 14, 6, 1, 16)
    R(s, (200, 220, 230), 1, 11, 14, 1)                            # tampo de vidro
    R(s, (200, 220, 230), 1, 18, 14, 1)
    R(s, frame, 1, 12, 14, 1); R(s, frame, 1, 19, 14, 1)
    R(s, frame, 13, 3, 3, 1); R(s, frame, 15, 3, 1, 4)             # alça
    # garrafas e copos
    R(s, (40, 110, 60), 3, 4, 3, 7); R(s, (40, 110, 60), 4, 2, 1, 2)
    R(s, (190, 120, 40), 7, 5, 3, 6); R(s, (190, 120, 40), 8, 3, 1, 2)
    R(s, (230, 230, 236), 7, 7, 3, 2)
    R(s, (220, 236, 246), 11, 8, 2, 3)
    R(s, (120, 40, 190), 3, 14, 4, 4)                              # caixa de charutos (presente de um cliente)
    R(s, (220, 236, 246), 9, 15, 2, 3); R(s, (220, 236, 246), 12, 15, 2, 3)
    R(s, (40, 40, 46), 1, 22, 2, 2); R(s, (40, 40, 46), 13, 22, 2, 2)
    return s


def _tapete(w, h, medal=True, field=(88, 38, 126), edge=(70, 30, 100), line=(150, 96, 210), trim=GOLD):
    """Tapete com borda dourada (w x h em px de arte)."""
    s = new(w, h)
    R(s, edge, 0, 0, w, h)
    R(s, trim, 2, 2, w - 4, h - 4)
    R(s, field, 3, 3, w - 6, h - 6)
    R(s, line, 6, 6, w - 12, 1); R(s, line, 6, h - 7, w - 12, 1)
    R(s, line, 6, 6, 1, h - 12); R(s, line, w - 7, 6, 1, h - 12)
    for (x, y) in ((9, 9), (w - 12, 9), (9, h - 12), (w - 12, h - 12)):    # cantos
        R(s, trim, x, y, 3, 3)
    if medal:
        cx, cy = w // 2, h // 2                                    # medalhão com o "L"
        for r, col in ((9, trim), (8, edge), (6, shade(field, 1.25))):
            pygame.draw.circle(s, col, (cx, cy), r)
        R(s, (230, 200, 120), cx - 2, cy - 4, 2, 8); R(s, (230, 200, 120), cx - 2, cy + 2, 6, 2)
    for x in range(0, w, 4):                                       # franjas
        P(s, (220, 200, 160), x, 0); P(s, (220, 200, 160), x, h - 1)
    return s


def _tapete_ceo():
    return _tapete(80, 48)


# ---------------------------------------------------------------------------
# Sala de reuniões da sede (mesa grande 5x2, telão, cavalete com gráfico)
# ---------------------------------------------------------------------------
def _mesa_reuniao():
    w, h = 80, 40
    s = new(w, h)
    top = (70, 44, 36)
    R(s, shade(top, 0.75), 0, 2, w, 28)
    R(s, top, 1, 2, w - 2, 26)
    R(s, shade(top, 1.3), 1, 2, w - 2, 1)
    for x in range(6, w - 4, 11):                                   # brilho do verniz
        R(s, shade(top, 1.18), x, 5, 5, 1)
        R(s, shade(top, 1.12), x + 3, 22, 4, 1)
    R(s, (96, 40, 140), 4, 13, w - 8, 4)                            # passadeira roxa no meio
    R(s, (130, 70, 186), 4, 13, w - 8, 1)
    R(s, GOLD, 0, 28, w, 1)
    R(s, shade(top, 0.55), 2, 29, w - 4, 4)
    for x in (5, w - 9):
        R(s, shade(top, 0.45), x, 33, 4, 7)
    R(s, shade(top, 0.6), w // 2 - 4, 33, 8, 6)
    # um lugar para cada cadeira: pasta e copo d'água (em cima e embaixo)
    for i in range(5):
        x = i * 16 + 4
        R(s, (240, 240, 246), x, 4, 7, 5)
        R(s, (150, 150, 170), x + 1, 5, 5, 1)
        R(s, (200, 228, 246), x + 9, 5, 2, 3)
        R(s, (240, 240, 246), x + 3, 20, 7, 5)
        R(s, (120, 40, 190), x + 4, 21, 5, 1)
        R(s, (200, 228, 246), x, 21, 2, 3)
    # centro de mesa: orquídea roxa
    R(s, (240, 240, 246), w // 2 - 3, 13, 6, 4)
    for (x, y) in ((-2, 9), (1, 8), (3, 10), (-1, 11)):
        R(s, (200, 120, 230), w // 2 + x, y, 2, 2)
    # notebook na cabeceira (lado da CEO)
    R(s, (60, 60, 72), w - 12, 8, 9, 7)
    R(s, (150, 90, 220), w - 9, 10, 3, 2)
    return s


def _telao():
    s = new(48, 22)
    R(s, (36, 34, 44), 0, 0, 48, 22)
    R(s, (244, 244, 250), 2, 2, 44, 17)
    R(s, (220, 220, 232), 2, 17, 44, 2)
    for i, hgt in enumerate((4, 6, 5, 8, 10, 13)):                  # barras de faturamento
        R(s, (170, 140, 220), 6 + i * 6, 16 - hgt, 4, hgt)
    pts = [(6, 14), (12, 12), (18, 13), (24, 9), (30, 7), (36, 4), (42, 3)]   # LCORP subindo
    pygame.draw.lines(s, (110, 200, 120), False, pts, 1)
    R(s, (120, 40, 190), 4, 3, 10, 2)
    R(s, (80, 80, 96), 22, 20, 4, 2)
    return s


def _cavalete_grafico():
    s = new(16, 30)
    wood = (150, 108, 70)
    R(s, wood, 3, 4, 1, 24); R(s, wood, 12, 4, 1, 24)
    R(s, shade(wood, 0.8), 7, 10, 2, 18)
    R(s, (246, 246, 250), 2, 2, 12, 15)
    R(s, (220, 220, 230), 2, 16, 12, 1)
    R(s, (60, 60, 70), 2, 1, 12, 2)
    pygame.draw.lines(s, (120, 40, 190), False, [(4, 13), (7, 10), (9, 11), (12, 5)], 1)
    R(s, (230, 80, 80), 4, 5, 4, 1); R(s, (60, 60, 70), 4, 7, 6, 1)
    R(s, shade(wood, 0.6), 2, 27, 3, 2); R(s, shade(wood, 0.6), 11, 27, 3, 2)
    return s


# ---------------------------------------------------------------------------
# Gruppo Ricci: escritório da Vittoria e sala de projetos (cores da casa: vinho, verde e dourado)
# ---------------------------------------------------------------------------
WINE = (134, 42, 58)
VELVET = (44, 104, 76)           # veludo verde da cadeira da Vittoria
CREAM = (238, 228, 210)


def _mesa_vittoria():
    s = new(48, 30)
    green = (40, 76, 58)
    R(s, CREAM, 0, 11, 48, 4)                                       # tampo de mármore
    R(s, (250, 244, 232), 0, 11, 48, 1)
    for x in (6, 19, 33):
        R(s, (214, 204, 190), x, 12, 5, 1)                          # veios
    R(s, shade(CREAM, 0.7), 0, 15, 48, 1)
    R(s, GOLD, 1, 16, 46, 1)
    R(s, green, 2, 17, 44, 10)
    for x0 in (4, 32):                                              # painéis com moldura dourada
        R(s, shade(green, 1.2), x0, 18, 12, 8)
        R(s, shade(GOLD, 0.8), x0, 18, 12, 1); R(s, shade(GOLD, 0.8), x0, 25, 12, 1)
    R(s, GOLD, 20, 18, 8, 8)                                        # "R" dourado
    R(s, WINE, 21, 19, 6, 6)
    R(s, (250, 220, 140), 22, 20, 1, 4); R(s, (250, 220, 140), 23, 20, 2, 1)
    R(s, (250, 220, 140), 24, 21, 1, 1); R(s, (250, 220, 140), 23, 22, 1, 1); R(s, (250, 220, 140), 24, 23, 1, 1)
    for x in (2, 44):                                               # pés torneados
        R(s, shade(GOLD, 0.7), x, 27, 2, 3)
    # notebook aberto (de costas), vaso de rosas, xícara de expresso e cardápios
    R(s, (190, 192, 200), 8, 3, 13, 8)
    R(s, (160, 162, 172), 9, 4, 11, 6)
    R(s, (236, 236, 240), 13, 6, 3, 2)
    R(s, (210, 230, 240), 26, 7, 4, 4)                              # vaso
    for (x, y) in ((25, 4), (27, 3), (29, 5), (28, 5)):
        R(s, (200, 40, 60), x, y, 2, 2)
    P(s, (60, 130, 70), 27, 6); P(s, (60, 130, 70), 29, 7)
    R(s, (246, 246, 246), 33, 9, 4, 2); R(s, (90, 50, 30), 34, 9, 2, 1)     # expresso no pires
    R(s, WINE, 39, 8, 7, 3); R(s, (240, 230, 210), 39, 7, 7, 1)
    return s


def _poltrona_alta(c, legs):
    """Cadeira de encosto alto de frente (desenho de sempre, virada para baixo)."""
    s = new(16, 26)
    R(s, shade(c, 0.8), 3, 1, 10, 16)
    R(s, c, 4, 0, 8, 16)
    R(s, shade(c, 1.2), 4, 0, 8, 1)
    for y in (4, 8, 12):
        for x in (6, 9):
            P(s, shade(c, 0.6), x, y)
    R(s, shade(c, 0.7), 1, 13, 3, 6); R(s, shade(c, 0.7), 12, 13, 3, 6)
    R(s, shade(c, 0.95), 1, 13, 3, 1); R(s, shade(c, 0.95), 12, 13, 3, 1)
    R(s, shade(c, 1.22), 4, 15, 8, 4)
    R(s, shade(c, 1.4), 4, 15, 8, 1)
    R(s, legs, 2, 19, 2, 6); R(s, legs, 12, 19, 2, 6)
    R(s, shade(legs, 0.8), 5, 19, 1, 4); R(s, shade(legs, 0.8), 10, 19, 1, 4)
    return s


def _poltrona_alta_up(part, c, legs):
    s = new(16, 26)
    if part == "base":
        R(s, shade(c, 0.7), 1, 15, 3, 5); R(s, shade(c, 0.7), 12, 15, 3, 5)
        R(s, shade(c, 1.1), 4, 16, 8, 3)
        R(s, shade(legs, 0.8), 5, 19, 1, 4); R(s, shade(legs, 0.8), 10, 19, 1, 4)
        return s
    R(s, shade(c, 0.62), 3, 8, 10, 12)
    R(s, shade(c, 0.78), 4, 9, 8, 9)
    R(s, shade(c, 0.95), 3, 8, 10, 1)
    R(s, legs, 2, 19, 2, 6); R(s, legs, 12, 19, 2, 6)
    return s


def _poltrona_alta_side(part, c, legs):
    if part == "front":
        return None
    s = new(16, 26)
    R(s, shade(c, 0.8), 2, 2, 4, 16)
    R(s, shade(c, 1.1), 2, 2, 4, 1)
    R(s, shade(c, 1.15), 3, 15, 10, 4)
    R(s, shade(c, 1.35), 3, 15, 10, 1)
    R(s, shade(c, 0.7), 5, 12, 7, 2)
    R(s, legs, 3, 19, 2, 6); R(s, legs, 11, 19, 2, 6)
    return s


def _quadro_trattoria():
    s = new(16, 18)
    R(s, shade(GOLD, 0.7), 1, 0, 14, 17)
    R(s, GOLD, 2, 1, 12, 15)
    R(s, (210, 196, 170), 3, 2, 10, 13)                             # foto antiga, cor de sépia
    R(s, (150, 110, 80), 3, 6, 10, 9)                               # fachada
    R(s, WINE, 3, 5, 10, 2)                                         # toldo
    for x in (3, 7, 11):
        R(s, (240, 220, 200), x, 5, 2, 2)
    R(s, (252, 222, 136), 4, 9, 3, 3)                               # vitrine acesa
    R(s, (60, 40, 30), 9, 9, 3, 6)                                  # porta
    P(s, (60, 40, 30), 7, 13); P(s, (230, 190, 170), 7, 12)         # a Vittoria na porta, anos atrás
    R(s, shade(GOLD, 0.55), 6, 16, 4, 1)
    return s


def _oliveira():
    s = new(16, 30)
    pot = (184, 98, 62)
    for (x, y, r) in ((8, 8, 6), (4, 11, 4), (12, 11, 4), (8, 4, 4)):
        pygame.draw.circle(s, (96, 120, 84), (x, y), r)
    for (x, y, r) in ((7, 7, 4), (10, 5, 3), (4, 10, 2)):
        pygame.draw.circle(s, (130, 154, 112), (x, y), r)
    for (x, y) in ((5, 6), (11, 9), (8, 12), (3, 12), (12, 4)):
        P(s, (70, 60, 80), x, y)                                    # azeitonas
    R(s, (110, 90, 70), 7, 14, 2, 7)
    R(s, (100, 80, 60), 6, 17, 1, 2)
    R(s, pot, 3, 21, 10, 8)
    R(s, shade(pot, 1.2), 2, 20, 12, 2)
    R(s, shade(pot, 0.8), 4, 27, 8, 2)
    return s


def _planta_baixa():
    s = new(16, 18)
    R(s, (60, 54, 50), 1, 0, 14, 17)
    R(s, (40, 86, 150), 2, 1, 12, 15)                               # papel azul de planta
    line = (200, 226, 250)
    R(s, line, 4, 3, 8, 1); R(s, line, 4, 3, 1, 10); R(s, line, 11, 3, 1, 10); R(s, line, 4, 12, 8, 1)
    R(s, line, 4, 8, 4, 1); R(s, line, 8, 6, 1, 3)
    P(s, line, 6, 5); P(s, line, 10, 10); P(s, line, 6, 10)
    R(s, (250, 220, 140), 10, 13, 3, 2)
    return s


def _painel_amostras():
    s = new(16, 18)
    R(s, (196, 164, 120), 1, 0, 14, 17)                             # cortiça
    R(s, (210, 180, 136), 2, 1, 12, 15)
    for (x, y, c) in ((3, 2, WINE), (8, 2, (60, 120, 90)), (3, 7, (230, 200, 120)), (8, 8, CREAM),
                      (4, 12, (110, 70, 50)), (9, 12, (200, 120, 90))):
        R(s, c, x, y, 4, 4)
        P(s, (220, 40, 40), x + 1, y)                               # alfinetes
    return s


def _prancheta():
    s = new(16, 24)
    wood = (150, 108, 70)
    R(s, (230, 236, 244), 1, 5, 14, 8)                              # tampo inclinado com o projeto
    R(s, (40, 86, 150), 3, 6, 9, 5)
    R(s, (200, 226, 250), 4, 7, 5, 1); R(s, (200, 226, 250), 4, 9, 7, 1)
    R(s, shade(wood, 0.8), 1, 13, 14, 2)
    R(s, (250, 220, 140), 12, 3, 2, 3); R(s, (60, 60, 70), 13, 2, 1, 1)     # luminária
    R(s, wood, 3, 15, 2, 9); R(s, wood, 11, 15, 2, 9)
    R(s, shade(wood, 0.7), 3, 19, 10, 1)
    return s


def _amostras():
    s = new(32, 30)
    wood = (120, 80, 56)
    R(s, wood, 0, 2, 32, 28)
    R(s, shade(wood, 1.25), 0, 2, 32, 1)
    for y in (10, 19):
        R(s, shade(wood, 0.7), 1, y, 30, 1)
    R(s, shade(wood, 0.6), 1, 3, 30, 7); R(s, shade(wood, 0.6), 1, 11, 30, 8); R(s, shade(wood, 0.6), 1, 20, 30, 8)
    for i, c in enumerate((WINE, (60, 120, 90), CREAM, (200, 150, 80), (90, 60, 110))):   # rolos de tecido
        R(s, c, 2 + i * 6, 4, 5, 6)
        R(s, shade(c, 1.2), 2 + i * 6, 4, 5, 1)
    for i, c in enumerate(((236, 236, 240), (90, 150, 170), (200, 110, 80), (236, 236, 240), (220, 190, 120))):
        R(s, c, 2 + i * 6, 13, 5, 5)                                # azulejos e pratos
        P(s, shade(c, 0.7), 4 + i * 6, 15)
    for i in range(4):                                              # pastas de fornecedores
        R(s, (WINE, (60, 120, 90), (60, 70, 120), (200, 150, 80))[i], 3 + i * 7, 21, 5, 7)
    return s


def _mesa_maquete():
    s = new(32, 26)
    wood = (150, 108, 70)
    R(s, (236, 232, 222), 0, 9, 32, 5)
    R(s, (250, 248, 240), 0, 9, 32, 1)
    R(s, shade(wood, 0.8), 0, 14, 32, 3)
    R(s, wood, 2, 17, 2, 9); R(s, wood, 28, 17, 2, 9)
    # maquete do próximo restaurante: prédio branco com toldo vinho e arvorezinhas
    R(s, (246, 244, 238), 8, 2, 16, 9)
    R(s, (220, 216, 206), 8, 9, 16, 2)
    R(s, WINE, 7, 5, 18, 2)
    for x in (10, 15, 20):
        R(s, (252, 222, 136), x, 7, 2, 2)
    R(s, (60, 40, 30), 15, 8, 2, 3)
    for x in (4, 27):
        pygame.draw.circle(s, (96, 140, 84), (x, 8), 2)
        P(s, (110, 90, 70), x, 11)
    R(s, (240, 240, 246), 25, 11, 5, 2)                             # papelzinho com o nome
    return s


art.OBJECT_BUILDERS.update({
    "ceo_desk": _ceo_desk, "cadeira_ceo": _cadeira_ceo, "cadeira_reuniao": _cadeira_reuniao,
    "quadro_alexander": _quadro_alexander, "aparador": _aparador, "globo": _globo, "carrinho_bar": _carrinho_bar,
    "tapete_ceo": _tapete_ceo, "mesa_reuniao": _mesa_reuniao, "telao": _telao, "cavalete_grafico": _cavalete_grafico,
    "tapete_reuniao": lambda: _tapete(112, 64, medal=False),
    "tapete_saguao": lambda: _tapete(80, 64),       # saguão da sede: no eixo da porta e da recepção
    "mesa_vittoria": _mesa_vittoria, "cadeira_vittoria": lambda: _poltrona_alta(VELVET, GOLD),
    "quadro_trattoria": _quadro_trattoria, "oliveira": _oliveira, "planta_baixa": _planta_baixa,
    "painel_amostras": _painel_amostras, "prancheta": _prancheta, "amostras": _amostras, "mesa_maquete": _mesa_maquete,
    "tapete_ricci": lambda: _tapete(64, 48, medal=False, field=(110, 36, 52), edge=(70, 24, 34),
                                     line=(176, 80, 92)),
})
world.OBJECT_DEFS.update({
    "cadeira_ceo": (1, 1, True, "obj"), "cadeira_reuniao": (1, 1, True, "obj"),
    "quadro_alexander": (1, 1, False, "wall"), "aparador": (3, 1, True, "obj"), "globo": (1, 1, True, "obj"),
    "carrinho_bar": (1, 1, True, "obj"), "tapete_ceo": (5, 3, False, "decal"), "mesa_reuniao": (5, 2, True, "obj"),
    "telao": (3, 1, False, "wall"), "cavalete_grafico": (1, 1, True, "obj"), "tapete_reuniao": (7, 4, False, "decal"), "tapete_saguao": (5, 4, False, "decal"),
    "mesa_vittoria": (3, 1, True, "obj"), "cadeira_vittoria": (1, 1, True, "obj"),
    "quadro_trattoria": (1, 1, False, "wall"), "oliveira": (1, 1, True, "obj"), "planta_baixa": (1, 1, False, "wall"),
    "painel_amostras": (1, 1, False, "wall"), "prancheta": (1, 1, True, "obj"), "amostras": (2, 1, True, "obj"),
    "mesa_maquete": (2, 1, True, "obj"), "tapete_ricci": (4, 3, False, "decal"),
})
for _seats in (poses.SEAT_LIFT, poses.NPC_SEATS):
    _seats.update({"cadeira_ceo": 8, "cadeira_reuniao": 7, "cadeira_vittoria": 8})
assentos.BUILDERS.update({
    ("cadeira_ceo", "up"): _ceo_up,
    ("cadeira_ceo", "right"): _ceo_side,
    ("cadeira_reuniao", "up"): lambda p: assentos._chair_up(p, DARK_LEATHER, CHROME),
    ("cadeira_reuniao", "right"): lambda p: assentos._chair_side(p, DARK_LEATHER, CHROME),
    ("cadeira_vittoria", "up"): lambda p: _poltrona_alta_up(p, VELVET, GOLD),
    ("cadeira_vittoria", "right"): lambda p: _poltrona_alta_side(p, VELVET, GOLD),
})
lighting.EMITTERS["ceo_desk"] = ((230, 196, 120), 1.6)       # abajur de banqueiro, luz quente
lighting.EMITTERS["telao"] = ((200, 200, 255), 1.4)
for _k in ("cadeira_ceo", "aparador", "globo", "carrinho_bar", "mesa_reuniao"):
    world.HITBOXES.pop(_k, None)

FLAVOR = {
    "quadro_alexander": "Alexander Luthor. O retrato foi pintado no ano em que ele fundou o laboratório. "
                        "Os olhos verdes são os mesmos dela.",
    "aparador": "Uma foto da equipe no primeiro lançamento, uma orquídea que a Jess rega toda segunda e o primeiro "
                "prêmio de inovação da Luthor Corp.",
    "globo": "Um globo antigo do escritório do pai. Tem um adesivo de National City colado à mão.",
    "carrinho_bar": "Uísque para os investidores, água com gás para a CEO. A caixa roxa foi presente da Sam.",
    "cadeira_ceo": "A cadeira da presidência.",
    "telao": "O gráfico da LCORP do último trimestre. A Jess colocou uma setinha escrito \"isso aqui é você\".",
    "cavalete_grafico": "Um gráfico desenhado à mão pelo Brainy. As unidades estão em \"lançamentos por café\".",
    "mesa_vittoria": "Relatórios das doze casas, um vaso de rosas e um expresso esquecido, já frio.",
    "cadeira_vittoria": "Veludo verde. A Vittoria diz que é a única cadeira em que consegue pensar.",
    "quadro_trattoria": "A primeira Ricci Trattoria, anos atrás. Na porta, uma Vittoria bem mais nova, de avental "
                        "emprestado.",
    "oliveira": "Uma oliveira de verdade, trazida da Itália. Dá três azeitonas por ano e a Vittoria conta todas.",
    "planta_baixa": "A planta da próxima casa do Gruppo Ricci. Tem um espaço marcado: \"mesa da Letícia?\".",
    "painel_amostras": "Tecidos, azulejos e guardanapos presos com alfinete. Nada entra num restaurante sem passar aqui.",
    "prancheta": "O projeto do salão novo, com anotações em italiano na margem.",
    "amostras": "Rolos de tecido, pratos de prova e as pastas dos fornecedores, em ordem de cor.",
    "mesa_maquete": "A maquete do próximo restaurante. As arvorezinhas são de brócolis seco.",
}


def furnish(m):
    """Escritório da Letícia na sede (x 1..8, y 2..8): mesa de CEO, retrato do pai e um cantinho de estar.

    Corredores livres: a coluna 5 (da porta até o fundo) e a coluna 1, para todos os móveis terem acesso."""
    m.add("tapete_ceo", 1, 3)
    m.add("window", 1, 1); m.add("quadro_alexander", 3, 1); m.add("window", 6, 1)
    m.add("plant", 1, 2)
    m.add("aparador", 2, 2)
    m.add("globo", 5, 2)
    m.add("coffee", 6, 2)
    m.add("bookshelf", 7, 2)
    m.add("cadeira_ceo", 3, 3)
    m.add("ceo_desk", 2, 4)
    m.add("cadeira_reuniao", 2, 5); m.add("cadeira_reuniao", 4, 5)      # visitas, de frente para a mesa
    # cantinho de estar: sofá, poltrona e mesinha de centro
    m.add("rug_red", 6, 6)
    m.add("coffee_table", 6, 6)
    m.add("poltrona_roxa", 8, 6)
    m.add("sofa", 6, 8)
    m.add("plant_big", 8, 4)
    m.add("carrinho_bar", 1, 7)
    m.add("plant", 1, 8)


def furnish_reunioes(m):
    """Sala de reuniões da sede (x 26..32, y 2..8, entrada pelo saguão em 29-30,9).

    Mesa grande 5x2 com 10 cadeiras e a cadeira da CEO na cabeceira. A coluna 26 e as fileiras 3 e 8 ficam livres."""
    m.add("tapete_reuniao", 26, 4)
    m.add("window", 26, 1); m.add("telao", 28, 1); m.add("window", 32, 1)
    m.add("plant_big", 26, 2)
    m.add("coffee", 27, 2)
    m.add("cavalete_grafico", 31, 2)
    m.add("plant_big", 32, 2)
    m.add("mesa_reuniao", 27, 5)
    for x in range(27, 32):
        m.add("cadeira_reuniao", x, 4)
        m.add("cadeira_reuniao", x, 7)
    m.add("cadeira_ceo", 32, 5)


def furnish_ricci(m):
    """Sede do Gruppo Ricci: escritório da Vittoria (x 1..7, y 2..6) e sala de projetos (x 14..18, y 2..6)."""
    # escritório da Vittoria
    m.add("quadro_trattoria", 4, 1); m.add("window_big", 5, 1)
    m.add("oliveira", 1, 2)
    m.add("bookshelf3", 2, 2)
    m.add("cadeira_vittoria", 4, 2)
    m.add("coffee", 7, 2)
    m.add("mesa_vittoria", 3, 3)
    m.add("chair", 3, 4); m.add("chair", 5, 4)                         # visitas
    m.add("tapete_ricci", 2, 4)
    m.add("coffee_table", 3, 6)
    m.add("armchair", 2, 6); m.add("armchair", 5, 6)
    m.add("plant", 1, 6); m.add("plant_big", 7, 6)
    # sala de projetos (no lugar da antiga cozinha de testes)
    m.add("planta_baixa", 15, 1); m.add("painel_amostras", 17, 1)
    m.add("prancheta", 14, 2)
    m.add("amostras", 17, 2)
    m.add("mesa_maquete", 15, 4)
    m.add("chair", 15, 5); m.add("chair", 16, 5)
    m.add("plant", 14, 6); m.add("plant", 18, 6)


# ---------------------------------------------------------------------------
# Salinha da Sam (embaixo da sala de reuniões): mesa branca com azul-marinho, dois monitores, arquivo e lousa
# ---------------------------------------------------------------------------
NAVY = (44, 62, 110)


def _mesa_sam():
    s = new(48, 30)
    white = (236, 236, 242)
    R(s, white, 0, 11, 48, 4)
    R(s, (250, 250, 254), 0, 11, 48, 1)
    R(s, shade(white, 0.75), 0, 15, 48, 1)
    R(s, CHROME, 1, 16, 46, 1)
    R(s, NAVY, 2, 17, 44, 10)
    R(s, shade(NAVY, 1.25), 2, 17, 44, 1)
    for x0 in (4, 32):
        R(s, shade(NAVY, 1.15), x0, 19, 12, 6)
        R(s, CHROME, x0 + 5, 21, 2, 1)
    R(s, CHROME, 20, 19, 8, 6)                                       # plaquinha "CFO"
    R(s, (30, 34, 50), 21, 20, 6, 4)
    R(s, (150, 200, 255), 22, 21, 4, 1); R(s, (150, 200, 255), 22, 23, 3, 1)
    R(s, CHROME, 3, 27, 2, 3); R(s, CHROME, 43, 27, 2, 3)
    # dois monitores (de costas), calculadora, caneca e porta-retrato com a Letícia
    for x in (6, 19):
        R(s, (38, 38, 48), x, 2, 12, 9)
        R(s, (58, 58, 72), x + 1, 3, 10, 7)
        R(s, (44, 44, 54), x + 5, 11, 2, 1)
    R(s, (60, 60, 70), 33, 9, 6, 3); R(s, (150, 210, 160), 34, 9, 4, 1)
    R(s, (240, 240, 246), 40, 7, 4, 4); R(s, (240, 240, 246), 44, 8, 1, 2)
    R(s, (120, 40, 190), 41, 8, 2, 1)
    R(s, GOLD, 32, 3, 6, 5); R(s, (150, 196, 230), 33, 4, 4, 3)
    P(s, (40, 30, 30), 34, 5); P(s, (180, 120, 70), 36, 5)
    return s


def _arquivo():
    s = new(16, 26)
    metal = (150, 156, 170)
    R(s, shade(metal, 0.8), 1, 2, 14, 24)
    R(s, metal, 2, 2, 12, 23)
    R(s, shade(metal, 1.2), 2, 2, 12, 1)
    for y in (4, 11, 18):
        R(s, shade(metal, 1.08), 3, y, 10, 6)
        R(s, shade(metal, 0.7), 3, y + 6, 10, 1)
        R(s, (240, 240, 246), 5, y + 1, 6, 2)                       # etiqueta
        R(s, (60, 60, 70), 6, y + 4, 4, 1)                           # puxador
    R(s, (230, 60, 60), 11, 1, 3, 2)                                 # pasta vermelha: "URGENTE"
    return s


def _lousa_sam():
    s = new(16, 30)
    R(s, CHROME, 2, 4, 1, 24); R(s, CHROME, 13, 4, 1, 24)
    R(s, (60, 60, 70), 1, 1, 14, 15)
    R(s, (248, 248, 252), 2, 2, 12, 13)
    pygame.draw.lines(s, (60, 170, 90), False, [(3, 12), (6, 10), (8, 11), (12, 4)], 1)
    P(s, (60, 170, 90), 11, 4); P(s, (60, 170, 90), 12, 5)
    R(s, NAVY, 3, 3, 5, 1); R(s, (120, 40, 190), 3, 5, 3, 1)
    R(s, (90, 90, 100), 2, 16, 12, 1)
    R(s, (230, 60, 60), 5, 15, 2, 1); R(s, (40, 90, 200), 8, 15, 2, 1)
    R(s, shade(CHROME, 0.7), 1, 27, 4, 2); R(s, shade(CHROME, 0.7), 11, 27, 4, 2)
    return s


art.OBJECT_BUILDERS.update({
    "mesa_sam": _mesa_sam, "cadeira_sam": lambda: _poltrona_alta(NAVY, CHROME), "arquivo": _arquivo,
    "lousa_sam": _lousa_sam,
    "tapete_sam": lambda: _tapete(64, 48, medal=False, field=(54, 74, 126), edge=(34, 46, 84), line=(110, 140, 200),
                                  trim=CHROME),
})
world.OBJECT_DEFS.update({
    "mesa_sam": (3, 1, True, "obj"), "cadeira_sam": (1, 1, True, "obj"), "arquivo": (1, 1, True, "obj"),
    "lousa_sam": (1, 1, True, "obj"), "tapete_sam": (4, 3, False, "decal"),
})
for _seats in (poses.SEAT_LIFT, poses.NPC_SEATS):
    _seats["cadeira_sam"] = 8
assentos.BUILDERS.update({
    ("cadeira_sam", "up"): lambda p: _poltrona_alta_up(p, NAVY, CHROME),
    ("cadeira_sam", "right"): lambda p: _poltrona_alta_side(p, NAVY, CHROME),
})
FLAVOR.update({
    "mesa_sam": "Dois monitores de planilhas, uma calculadora que já viu de tudo e um porta-retrato: a Sam e a Letícia "
                "na faculdade.",
    "cadeira_sam": "A cadeira da diretora financeira. Ninguém senta nela. Nem a CEO.",
    "arquivo": "Contratos em ordem alfabética, por data e por cor. A pasta vermelha diz \"URGENTE (de verdade)\".",
    "lousa_sam": "Metas do trimestre. Embaixo, com a letra da Sam: \"Luthor, almoce.\"",
})


def furnish_sam(m):
    """Salinha da Sam (x 26..32, y 12..16, porta em 25,14 pela área de madeira do saguão).

    A Sam senta na cadeira (29,12), atrás da mesa (28..30,13), de frente para quem entra."""
    m.add("tapete_sam", 27, 12)
    m.add("bookshelf2", 26, 12)
    m.add("plant", 28, 12)
    m.add("cadeira_sam", 29, 12)
    m.add("plant_big", 32, 12)
    m.add("mesa_sam", 28, 13)
    m.add("arquivo", 32, 13)
    m.add("cadeira_reuniao", 28, 14); m.add("cadeira_reuniao", 30, 14)     # visitas
    m.add("lousa_sam", 32, 15)
    m.add("plant", 26, 16)

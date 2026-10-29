"""Limpa o fundo dos retratos em PNG, sem mudar a resolução.

Uso (na pasta do jogo):   py limpar_retratos.py

Para cada PNG em assets/portraits que ainda tenha fundo (branco liso ou xadrez de "transparente" desenhado na
imagem), apaga esse fundo, inclusive os pedaços presos entre mechas de cabelo e a franjinha clara em volta do
desenho. Retratos que já têm transparência ficam como estão. A imagem continua com o mesmo tamanho e a mesma
qualidade (o jogo reduz sozinho, em etapas, na hora de mostrar).
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
PORTRAITS = os.path.join(BASE, "assets", "portraits")


def _shift(a, dx, dy):
    """Desloca uma matriz (largura x altura) sem dar a volta nas bordas."""
    import numpy as np
    out = np.zeros_like(a)
    w, h = a.shape
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[xd, yd] = a[xs, ys]
    return out


def _dilate(a, r):
    for _ in range(r):
        a = a | _shift(a, 1, 0) | _shift(a, -1, 0) | _shift(a, 0, 1) | _shift(a, 0, -1)
    return a


def clean_background(img):
    """Fundo falso -> transparência. Usa numpy (só neste script; o jogo não precisa dele).

    Fundo branco liso: tudo o que é branco e encosta nas bordas.
    Xadrez de "transparente": um pixel é fundo se tem a cor de um quadradinho do xadrez e, a um quadradinho de
    distância, a cor do outro (o vaivém regular do xadrez). Cabelo grisalho, bordados e blusas brancas não têm
    esse padrão. As bordas suavizadas entre os quadradinhos entram por estarem coladas nele.
    """
    import numpy as np
    w, h = img.get_size()
    rgb = pygame.surfarray.array3d(img).astype(np.int16)          # (w, h, 3)
    alpha = pygame.surfarray.array_alpha(img).copy()
    if alpha[0, 0] < 20 and alpha[-1, 0] < 20:
        return img                                                # já tem transparência de verdade
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    v = rgb.mean(axis=2)
    grey = (mx - mn) <= 18
    white = grey & (mn >= 236)
    # cor escura do xadrez e tamanho do quadradinho, lidos na borda de cima
    row_grey = grey[:, 0] & (mn[:, 0] >= 120) & (mn[:, 0] < 232)
    low = float(np.median(v[row_grey, 0])) if row_grey.sum() > w // 10 else None
    s = None
    if low is not None:
        tones = np.where(white[:, 0], 1, np.where(grey[:, 0] & (np.abs(v[:, 0] - low) <= 16), 2, 0))
        runs, cur, n = [], tones[0], 0
        for t in tones:
            if t == cur:
                n += 1
            else:
                if cur and n >= 4:
                    runs.append(n)
                cur, n = t, 1
        s = int(round(float(np.median(runs)))) if len(runs) >= 6 else None
    if s:
        darkt = grey & (np.abs(v - low) <= 16)
        core = np.zeros((w, h), bool)
        for d in (s, -s):
            for (dx, dy) in ((d, 0), (0, d)):
                core |= (white & _shift(darkt, dx, dy)) | (darkt & _shift(white, dx, dy))
        bg = _dilate(core, 2) & grey & (mn >= low - 16)
        light = grey & (mn >= min(low - 16, 214))
    else:
        bg = white                                                # fundo branco liso
        light = grey & (mn >= 228)

    def to_mask(arr):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pa = pygame.surfarray.pixels_alpha(surf)
        pa[:] = np.where(arr, 255, 0).astype(np.uint8)
        del pa
        return pygame.mask.from_surface(surf, 127)

    def to_arr(mask):
        return pygame.surfarray.array_alpha(mask.to_surface(setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))) > 0

    bm = to_mask(bg)
    hole = np.zeros((w, h), bool)
    for (x, y) in [(0, 0), (w - 1, 0), (w // 4, 0), (w // 2, 0), (3 * w // 4, 0),
                   (0, h // 4), (w - 1, h // 4), (0, h // 2), (w - 1, h // 2)]:
        if bm.get_at((x, y)) and not hole[x, y]:
            hole |= to_arr(bm.connected_component((x, y)))
    if s:
        # xadrez cortado por fios soltos: avança pelo padrão do xadrez pulando fios finos (até 2 px)
        for _ in range(40):
            grown = hole | (_dilate(hole, 3) & bg)
            if (grown == hole).all():
                break
            hole = grown
        # pedaços de xadrez presos entre mechas (seguem o padrão do xadrez, então são fundo)
        # no xadrez o branco forma blocos cheios; num bordado ou num brilho, são linhas finas
        half = max(2, s // 2)
        for comp in bm.connected_components(minimum=2 * s * s):
            area = to_arr(comp)
            if (area & hole).any():
                continue
            wa = white & area
            if wa.sum() < s * s // 2:
                continue
            same_x = _shift(white, -half, 0)[wa].mean()
            same_y = _shift(white, 0, -half)[wa].mean()
            if same_x >= 0.42 and same_y >= 0.42:
                hole |= area
    # franjinha clara em volta do desenho (contorno branco de "adesivo" e bordas suavizadas)
    for _ in range(3):
        hole |= _dilate(hole, 1) & light
    # fios soltos desenhados por cima do fundo: tons claros quase sem cor, colados no fundo apagado
    pale = ((mx - mn) <= 40) & (mn >= ((low - 20) if s else 210))
    for _ in range(5):
        hole |= _dilate(hole, 1) & pale
    alpha[hole] = 0
    out = img.copy()
    pa = pygame.surfarray.pixels_alpha(out)
    pa[:] = alpha
    del pa
    return out


def _load(path, tries=5):
    """Abre a imagem; se o Windows estiver com o arquivo ocupado, tenta de novo."""
    import time
    for _ in range(tries):
        try:
            return pygame.image.load(path)
        except (pygame.error, OSError):
            time.sleep(0.5)
    return None


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    n = 0
    for name in sorted(os.listdir(PORTRAITS)):
        if not name.lower().endswith(".png"):
            continue
        path = os.path.join(PORTRAITS, name)
        img = _load(path)
        if img is None:
            print(f"  {name}: não consegui abrir (arquivo em uso?), pulei")
            continue
        img = img.convert_alpha()
        clean = clean_background(img)
        if clean is img:
            continue                     # já tinha fundo transparente
        import time
        for _ in range(8):               # o Windows às vezes segura o arquivo por um instante
            try:
                pygame.image.save(clean, path)
                break
            except (pygame.error, OSError):
                time.sleep(0.6)
        else:
            print(f"  {name}: não consegui salvar (arquivo em uso?), pulei")
            continue
        n += 1
        print(f"  {name}")
    print(f"{n} retrato(s) com o fundo limpo." if n else "Nenhum retrato com fundo para limpar.")


if __name__ == "__main__":
    main()

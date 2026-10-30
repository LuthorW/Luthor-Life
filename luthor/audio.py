"""Som do Luthor Life: efeitos e músicas chiptune gerados por código (nenhum arquivo de áudio de terceiros).

- Efeitos (sfx): curtinhos, gerados ao abrir o jogo.
- Músicas: uma por clima ("mood"), compostas por regras (acordes, baixo, arpejo, melodia e bateria) a partir de
  uma semente fixa, então soam sempre iguais. Cada uma é gerada uma única vez, em segundo plano, e guardada em
  saves/audio/<mood>_v<versão>.wav; nas próximas vezes abre na hora.
- Volume: settings["music"] e settings["sfx"] (0 a 1), ajustados no menu de pausa.

Uso: audio.pre_init() antes de pygame.init(); audio.init(settings); audio.sfx("door"); audio.music("morning");
audio.update(dt) a cada quadro. Tudo falha em silêncio se não houver placa de som.
"""
import io
import math
import os
import queue
import random
import threading
import wave
from array import array

import pygame

from .config import SAVE_DIR

RATE = 22050
VERSION = 1
MUSIC_ENABLED = False     # a dona não gostou das músicas geradas: ficam desligadas (código guardado para o futuro)
STEPS_ENABLED = False     # passos testados duas vezes e retirados a pedido da dona
CACHE = os.path.join(SAVE_DIR, "audio")
TABLE = 1024
_SINE = [math.sin(2 * math.pi * i / TABLE) for i in range(TABLE)]
_TRI = [1 - 4 * abs(i / TABLE - 0.5) for i in range(TABLE)]

state = dict(ok=False, music_vol=0.6, sfx_vol=0.7, mood=None, playing=None, chan=None, sounds={}, tracks={},
             step_t=0.0, blip_t=0.0)
_jobs = queue.Queue()
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Síntese
# ---------------------------------------------------------------------------
def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _wave_value(kind, phase, duty=0.5):
    p = phase % TABLE
    if kind == "sine":
        return _SINE[int(p)]
    if kind == "tri":
        return _TRI[int(p)]
    return 1.0 if p < TABLE * duty else -1.0           # pulso / quadrada


def add_note(buf, start, dur, freq, kind="square", vol=0.2, attack=0.01, release=0.08, duty=0.5, wrap=False,
             slide=0.0, vibrato=0.0):
    """Soma uma nota no buffer (lista de floats). wrap=True: o que passar do fim volta ao começo (loop)."""
    n = len(buf)
    s0 = int(start * RATE)
    total = int((dur + release) * RATE)
    a = max(1, int(attack * RATE))
    sustain_end = int(dur * RATE)
    r = max(1, int(release * RATE))
    phase = 0.0
    step = freq * TABLE / RATE
    rnd = random.Random(int(freq * 1000) ^ s0)
    for i in range(total):
        if i < a:
            env = i / a
        elif i < sustain_end:
            env = 1.0
        else:
            env = max(0.0, 1.0 - (i - sustain_end) / r)
        if kind == "noise":
            v = rnd.uniform(-1, 1)
        else:
            v = _wave_value(kind, phase, duty)
            inc = step * (1 + slide * i / max(1, total))
            if vibrato:
                inc *= 1 + vibrato * _SINE[int((i * 5.5 * TABLE / RATE)) % TABLE]
            phase += inc
        j = s0 + i
        if j >= n:
            if not wrap:
                break
            j %= n
        buf[j] += v * vol * env


def to_bytes(buf, peak=0.85):
    m = max(1e-6, max(abs(v) for v in buf))
    k = 32767 * peak / m if m > peak else 32767
    return array("h", (int(max(-1.0, min(1.0, v)) * k) for v in buf)).tobytes()


def wav_bytes(buf, peak=0.85):
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(to_bytes(buf, peak))
    return out.getvalue()


# ---------------------------------------------------------------------------
# Efeitos
# ---------------------------------------------------------------------------
def _sfx_defs():
    def mk(dur):
        return [0.0] * int(dur * RATE)

    out = {}
    # passos discretos: "tuc" abafado (ruído suavizado + um grave curtinho), em duas versões que se alternam
    for i, (pitch, seed) in enumerate(((150, 3), (128, 8))):
        b = mk(0.07)
        rnd = random.Random(seed)
        n = int(0.035 * RATE)
        last = 0.0
        for k in range(n):
            last = last * 0.86 + rnd.uniform(-1, 1) * 0.14       # ruído abafado (passa-baixa)
            b[k] += last * 0.9 * (1 - k / n) ** 2
        add_note(b, 0, 0.012, pitch, "sine", 0.35, 0.001, 0.03, slide=-0.4)
        out[f"step{i}"] = b
    b = mk(0.35)
    add_note(b, 0, 0.06, midi(55), "square", 0.22, 0.003, 0.06, 0.25)
    add_note(b, 0.08, 0.1, midi(62), "square", 0.22, 0.003, 0.12, 0.25)
    add_note(b, 0, 0.05, 200, "noise", 0.12, 0.002, 0.05); out["door"] = b
    b = mk(0.06); add_note(b, 0, 0.02, midi(84), "square", 0.12, 0.002, 0.02, 0.25); out["blip"] = b
    b = mk(0.08); add_note(b, 0, 0.03, midi(79), "square", 0.16, 0.002, 0.03, 0.25); out["move"] = b
    b = mk(0.2)
    add_note(b, 0, 0.05, midi(76), "square", 0.18, 0.002, 0.04, 0.25)
    add_note(b, 0.06, 0.07, midi(83), "square", 0.18, 0.002, 0.06, 0.25); out["confirm"] = b
    b = mk(0.2)
    add_note(b, 0, 0.05, midi(71), "square", 0.16, 0.002, 0.04, 0.25)
    add_note(b, 0.06, 0.07, midi(64), "square", 0.16, 0.002, 0.06, 0.25); out["cancel"] = b
    b = mk(0.35)
    add_note(b, 0, 0.06, midi(88), "square", 0.16, 0.002, 0.05, 0.5)
    add_note(b, 0.07, 0.16, midi(93), "square", 0.16, 0.002, 0.12, 0.5); out["coin"] = b
    b = mk(0.3)
    add_note(b, 0, 0.05, midi(81), "tri", 0.3, 0.002, 0.05)
    add_note(b, 0.05, 0.05, midi(76), "tri", 0.3, 0.002, 0.08); out["buy"] = b
    b = mk(0.3)
    for i, n in enumerate((72, 76, 79, 84)):
        add_note(b, i * 0.045, 0.05, midi(n), "square", 0.13, 0.002, 0.06, 0.25)
    out["pickup"] = b
    b = mk(0.8)
    for i, n in enumerate((76, 81, 84, 88)):
        add_note(b, i * 0.09, 0.12, midi(n), "tri", 0.28, 0.005, 0.25)
    add_note(b, 0.36, 0.2, midi(93), "sine", 0.18, 0.01, 0.3); out["heart"] = b
    b = mk(0.7)
    for i, n in enumerate((72, 76, 79)):
        add_note(b, i * 0.08, 0.1, midi(n), "tri", 0.26, 0.004, 0.2)
    add_note(b, 0.26, 0.25, midi(84), "tri", 0.26, 0.004, 0.3); out["gift"] = b
    b = mk(0.9)
    for i, n in enumerate((79, 84, 88, 91)):
        add_note(b, i * 0.1, 0.16, midi(n), "sine", 0.3, 0.01, 0.3)
    out["love"] = b
    b = mk(0.5)
    add_note(b, 0, 0.12, midi(62), "square", 0.18, 0.004, 0.08, 0.5, slide=-0.15)
    add_note(b, 0.16, 0.2, midi(58), "square", 0.18, 0.004, 0.15, 0.5, slide=-0.2); out["bad"] = b
    b = mk(0.35)
    add_note(b, 0, 0.12, 900, "noise", 0.25, 0.002, 0.15)
    add_note(b, 0, 0.08, midi(88), "square", 0.14, 0.002, 0.05, 0.25); out["bite"] = b
    b = mk(1.0)
    for i, n in enumerate((67, 72, 76, 79, 84)):
        add_note(b, i * 0.08, 0.1 if i < 4 else 0.35, midi(n), "square", 0.14, 0.003, 0.2, 0.25)
    out["catch"] = b
    b = mk(0.7)
    for i, n in enumerate((67, 63, 60)):
        add_note(b, i * 0.14, 0.12, midi(n), "tri", 0.26, 0.004, 0.12)
    out["lose"] = b
    b = mk(0.6)
    for i, n in enumerate((79, 83, 86)):
        add_note(b, i * 0.07, 0.08, midi(n), "square", 0.12, 0.002, 0.1, 0.25)
    add_note(b, 0.21, 0.2, midi(91), "tri", 0.2, 0.004, 0.25); out["reward"] = b
    b = mk(2.2)
    for i, n in enumerate((72, 67, 64, 60, 64, 55)):
        add_note(b, i * 0.3, 0.28, midi(n), "sine", 0.3, 0.02, 0.35)
    out["sleep"] = b
    b = mk(0.25); add_note(b, 0, 0.06, 2600, "noise", 0.12, 0.002, 0.12); add_note(b, 0, 0.05, midi(96), "sine", 0.1, 0.002, 0.1)
    out["splash"] = b
    return out


# ---------------------------------------------------------------------------
# Músicas (uma por clima)
# ---------------------------------------------------------------------------
MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
DORIAN = [0, 2, 3, 5, 7, 9, 10]

MOODS = {
    # bpm, tônica (midi), escala, progressão (graus), estilo
    "title": dict(bpm=84, root=58, scale=MAJOR, prog=[0, 4, 5, 3], drums=False, lead="tri", arp=True, pad=True, seed=1),
    "morning": dict(bpm=112, root=60, scale=MAJOR, prog=[0, 3, 4, 0, 5, 3, 1, 4], drums=True, lead="square", arp=True,
                    pad=False, seed=2),
    "afternoon": dict(bpm=98, root=55, scale=MAJOR, prog=[0, 5, 3, 4], drums=True, lead="tri", arp=True, pad=True,
                      seed=3),
    "evening": dict(bpm=86, root=57, scale=MINOR, prog=[0, 5, 2, 6], drums=True, lead="tri", arp=True, pad=True,
                    soft_drums=True, seed=4),
    "night": dict(bpm=68, root=53, scale=MAJOR, prog=[0, 5, 3, 4], drums=False, lead="sine", arp=False, pad=True,
                  sparse=True, seed=5),
    "rain": dict(bpm=74, root=57, scale=MINOR, prog=[0, 3, 5, 4], drums=False, lead="sine", arp=True, pad=True,
                 sparse=True, seed=6),
    "indoor": dict(bpm=90, root=53, scale=MAJOR, prog=[0, 3, 1, 4], drums=False, lead="tri", arp=True, pad=True,
                   seed=7),
    "work": dict(bpm=104, root=62, scale=DORIAN, prog=[0, 3, 0, 4], drums=True, lead="square", arp=True, pad=False,
                 soft_drums=True, seed=8),
    "bar": dict(bpm=96, root=50, scale=DORIAN, prog=[0, 3, 6, 4], drums=True, lead="tri", arp=False, pad=True,
                walking=True, swing=True, seed=9),
    "hospital": dict(bpm=70, root=64, scale=MAJOR, prog=[0, 3, 5, 4], drums=False, lead="sine", arp=True, pad=True,
                     sparse=True, seed=10),
    "marina": dict(bpm=100, root=62, scale=MAJOR, prog=[0, 4, 5, 3], drums=True, lead="square", arp=True, pad=True,
                   soft_drums=True, seed=11),
}


def _chord(cfg, degree, octave=0):
    sc, root = cfg["scale"], cfg["root"] + 12 * octave
    out = []
    for k in (0, 2, 4):
        d = degree + k
        out.append(root + sc[d % 7] + 12 * (d // 7))
    return out


def compose(mood):
    """Compõe a música de um clima: 16 compassos que voltam ao começo sem emenda."""
    cfg = MOODS[mood]
    rnd = random.Random(cfg["seed"] * 7919)
    beat = 60.0 / cfg["bpm"]
    prog = cfg["prog"] * (16 // len(cfg["prog"]))
    bars = len(prog)
    buf = [0.0] * int(bars * 4 * beat * RATE)
    sc = cfg["scale"]
    scale_notes = [cfg["root"] + 12 + sc[i % 7] + 12 * (i // 7) for i in range(-3, 12)]
    swing = 0.12 * beat if cfg.get("swing") else 0.0
    motif = None
    for bar, deg in enumerate(prog):
        t0 = bar * 4 * beat
        ch = _chord(cfg, deg)
        # baixo
        if cfg.get("walking"):
            walk = [ch[0], ch[1], ch[2], ch[1] + 1]
            for b4 in range(4):
                add_note(buf, t0 + b4 * beat, beat * 0.8, midi(walk[b4] - 24), "tri", 0.34, 0.005, 0.05, wrap=True)
        else:
            for b4 in (0, 2):
                add_note(buf, t0 + b4 * beat, beat * 1.6, midi(ch[0] - 24), "tri", 0.32, 0.01, 0.1, wrap=True)
        # acordes sustentados
        if cfg.get("pad"):
            for n in ch:
                add_note(buf, t0, 4 * beat * 0.97, midi(n - 12), "sine", 0.06, 0.25, 0.4, wrap=True)
        # arpejo em colcheias
        if cfg.get("arp"):
            seq = [ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12, ch[2]]
            for k in range(8):
                if cfg.get("sparse") and k % 2:
                    continue
                st = t0 + k * beat / 2 + (swing if k % 2 else 0)
                add_note(buf, st, beat * 0.35, midi(seq[k]), "square", 0.045, 0.004, 0.08, duty=0.25, wrap=True)
        # bateria
        if cfg.get("drums"):
            soft = 0.6 if cfg.get("soft_drums") else 1.0
            for b4 in range(4):
                st = t0 + b4 * beat
                if b4 in (0, 2):
                    add_note(buf, st, 0.06, 70, "sine", 0.5 * soft, 0.001, 0.08, slide=-0.6, wrap=True)
                else:
                    add_note(buf, st, 0.05, 0, "noise", 0.12 * soft, 0.001, 0.09, wrap=True)
                for h in (0, 1):
                    add_note(buf, st + h * beat / 2 + (swing if h else 0), 0.01, 0, "noise", 0.035 * soft, 0.001,
                             0.025, wrap=True)
        # melodia: motivo de 2 compassos que se repete com variações
        if bar % 2 == 0 and (motif is None or rnd.random() < 0.45):
            motif = []
            t = 0.0
            idx = rnd.randrange(4, 9)
            while t < 8 - 0.01:
                dur = rnd.choice([0.5, 0.5, 1.0, 1.0, 1.5, 2.0] if not cfg.get("sparse") else [1.0, 2.0, 2.0, 3.0])
                dur = min(dur, 8 - t)
                rest = rnd.random() < (0.35 if cfg.get("sparse") else 0.18)
                idx = max(0, min(len(scale_notes) - 1, idx + rnd.choice([-2, -1, -1, 1, 1, 2, 0])))
                motif.append((t, dur, None if rest else idx))
                t += dur
        for (t, dur, idx) in motif:
            local = t - (bar % 2) * 4
            if not (0 <= local < 4) or idx is None:
                continue
            note = scale_notes[idx]
            if local in (0.0, 2.0):            # tempo forte: puxa para uma nota do acorde
                pcs = [(c - note) % 12 for c in ch]
                if 0 not in pcs:
                    note = min((c + 12 * k for c in ch for k in (0, 1, 2)), key=lambda x: abs(x - note))
            add_note(buf, t0 + local * beat, dur * beat * 0.9, midi(note), cfg["lead"], 0.13, 0.01, 0.12,
                     duty=0.5, wrap=True, vibrato=0.004 if cfg["lead"] != "square" else 0.0)
    return buf


def _track_path(mood):
    return os.path.join(CACHE, f"{mood}_v{VERSION}.wav")


def _worker():
    while True:
        mood = _jobs.get()
        try:
            path = _track_path(mood)
            if not os.path.exists(path):
                data = wav_bytes(compose(mood), 0.8)
                os.makedirs(CACHE, exist_ok=True)
                tmp = path + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, path)
            snd = pygame.mixer.Sound(path)
            with _lock:
                state["tracks"][mood] = snd
        except Exception:
            with _lock:
                state["tracks"][mood] = None
        finally:
            with _lock:
                state["pending"].discard(mood)


# ---------------------------------------------------------------------------
# Interface usada pelo jogo
# ---------------------------------------------------------------------------
def pre_init():
    try:
        pygame.mixer.pre_init(RATE, -16, 1, 512)
    except Exception:
        pass


def init(settings):
    state["music_vol"] = float(settings.get("music", 0.6))
    state["sfx_vol"] = float(settings.get("sfx", 0.7))
    state["pending"] = set()
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(RATE, -16, 1, 512)
        pygame.mixer.set_num_channels(16)
        pygame.mixer.set_reserved(2)
        state["chan"] = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
        for name, buf in _sfx_defs().items():
            state["sounds"][name] = pygame.mixer.Sound(file=io.BytesIO(wav_bytes(buf, 0.9)))
        threading.Thread(target=_worker, daemon=True).start()
        state["ok"] = True
    except Exception:
        state["ok"] = False


SFX_LEVEL = {"step0": 0.14, "step1": 0.14, "blip": 0.5, "move": 0.6}


def sfx(name):
    if not state["ok"] or state["sfx_vol"] <= 0:
        return
    s = state["sounds"].get(name)
    if s:
        s.set_volume(state["sfx_vol"] * SFX_LEVEL.get(name, 1.0))
        s.play()


def music(mood):
    """Pede a música de um clima; troca com fade quando ela estiver pronta."""
    if not state["ok"] or not MUSIC_ENABLED:
        return
    state["mood"] = mood


def set_volume(music_vol=None, sfx_vol=None):
    if music_vol is not None:
        state["music_vol"] = music_vol
        for c in state.get("chan") or []:
            c.set_volume(music_vol)
    if sfx_vol is not None:
        state["sfx_vol"] = sfx_vol


def update(dt, walking=False):
    if not state["ok"]:
        return
    if walking and STEPS_ENABLED:         # passos (desligados)
        state["step_t"] -= dt
        if state["step_t"] <= 0:
            state["step_t"] = 0.4
            state["step_n"] = 1 - state.get("step_n", 0)
            sfx(f"step{state['step_n']}")
    else:
        state["step_t"] = 0.12
    want = state["mood"]
    if want is None or want == state["playing"]:
        return
    with _lock:
        snd = state["tracks"].get(want, False)
        if snd is False and want not in state["pending"]:
            state["pending"].add(want)
            _jobs.put(want)
    if snd is False:
        return
    a, b = state["chan"]
    old, new = (a, b) if a.get_busy() and not b.get_busy() else (b, a)
    old.fadeout(1400)
    if snd is not None:
        new.set_volume(state["music_vol"])
        new.play(snd, loops=-1, fade_ms=1600)
    state["playing"] = want


def blip():
    """Som curtinho das letras aparecendo na caixa de fala (no máximo ~12 por segundo)."""
    now = pygame.time.get_ticks()
    if now - state["blip_t"] > 80:
        state["blip_t"] = now
        sfx("blip")

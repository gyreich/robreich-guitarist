"""
Psychedelic mandala Short for an energetic passage (Rob approved the look on
Moon Pie). Same frame as the soft-light Wake Up Shorts: opens on a photo of Rob
that dissolves into the visual, title fixed at the top, music fading under the
closing card. Petals pulse with 48 frequency bands in 8-fold symmetry.

    python3 mandala_short.py moon-pie
"""
import colorsys
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import soft_light_visualizer as sl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS, SR = 1080, 1920, 30, 22050
SCALE = 2                      # draw at half size, scale up (the glow hides it; 4x faster)
INTRO_HOLD, INTRO_FADE, XF = 2.5, 2.0, 1.5

PIECES = {
    "moon-pie": {
        "audio": os.path.join(ROOT, "Album Wake Up Rob Reich", "02 Moon Pie.mp3"),
        "start": 222.0, "end": 258.2,          # the build to the song's peak; it drops away at 4:18
        "tail": 261.2,                         # music fades out under the card by here
        "head": ("ROB REICH", "MOON PIE", "FROM THE ALBUM WAKE UP"),
        "intro_photo": "Ellen-raimondo-pic-rr.jpg",       # photo by Ellen Raimondo
        "bg": (7, 6, 15),
        "out": "rob-reich-moon-pie-mandala-short.mp4",
    },
    "citi": {
        "audio": os.path.join(ROOT, "Album Wake Up Rob Reich", "04 Citi.mp3"),
        "start": 149.5, "end": 202.3,          # the build to the peak; it drops nearly silent at 3:22
        "tail": 205.0,                         # last hit rings out under the card
        "head": ("ROB REICH", "CITI", "FROM THE ALBUM WAKE UP"),
        "intro_photo": "site-sunglasses-suit-sunburst-strat.jpg",
        "bg": (5, 7, 16),
        "hues": (0.47, 0.55),                  # city lights: cyan through magenta to gold
        "out": "rob-reich-citi-mandala-short.mp4",
    },
}


def spectrum(src, start, dur):
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", src,
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(float) / 32768
    N, hop, nb = 4096, SR // FPS, 48
    edges = np.geomspace(60, 8000, nb + 1)
    freqs = np.fft.rfftfreq(N, 1 / SR)
    bands = [(freqs >= a) & (freqs < b) for a, b in zip(edges, edges[1:])]
    win = np.hanning(N)
    out = []
    for f in range(int(dur * FPS)):
        seg = x[f * hop:f * hop + N]
        if len(seg) < N:
            seg = np.pad(seg, (0, N - len(seg)))
        m = np.abs(np.fft.rfft(seg * win))
        out.append([m[b].mean() if b.any() else 0 for b in bands])
    spec = np.log1p(np.array(out) * 4)
    spec = np.clip(spec / (np.percentile(spec, 99) + 1e-9), 0, 1.2)
    for f in range(1, len(spec)):              # fast attack, slow release
        spec[f] = np.maximum(spec[f], spec[f - 1] * 0.86)
    return spec


def mandala(levels, t, prev, bg, hues=(0.0, 0.8)):
    w, h = W // SCALE, H // SCALE
    cx, cy = w / 2, 1150 / SCALE
    layer = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    nb, sym, rot = len(levels), 8, t * 9
    for k, v in enumerate(levels):
        r0, r1 = 90 / SCALE, (90 + 420 * v) / SCALE
        hue = (hues[0] + k / nb * hues[1] + 0.06 * math.sin(t / 3)) % 1 if hues != (0.0, 0.8) else (k / nb * 0.8 + t / 12) % 1
        col = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.85, 0.55 + 0.45 * min(v, 1)))
        for s in range(sym):
            for sign in (1, -1):
                a = math.radians(rot + s * 360 / sym + sign * (k + 0.5) * (180 / sym) / nb)
                d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                        (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], fill=col, width=3)
    rc = (60 + 40 * float(np.mean(levels))) / SCALE
    ring = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((t / 12 + 0.5) % 1, 0.7, 1))
    d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), outline=ring, width=2)
    if prev is not None:                       # light trails
        layer = Image.fromarray(np.maximum(np.asarray(layer), (np.asarray(prev) * 0.82).astype(np.uint8)))
    glow = layer.filter(ImageFilter.GaussianBlur(7))
    base = np.zeros((h, w, 3)) + np.array(bg, float)
    im = Image.fromarray(np.clip(base + np.asarray(glow, float) * 0.9 + np.asarray(layer, float), 0, 255).astype(np.uint8))
    return im.resize((W, H), Image.BICUBIC), layer


def build(key):
    p = PIECES[key]
    sl.CUR.clear(); sl.CUR.update(p)
    music = p["end"] - p["start"]
    total = music + 3.0
    spec = spectrum(p["audio"], p["start"], total)
    title = sl.title_layer(p["head"])
    card = sl.end_card(p["head"])
    intro = sl.intro_image(p)
    frames = os.path.join(HERE, "originals", f".work-{key}-frames")
    os.makedirs(frames, exist_ok=True)
    prev = None
    for f in range(int(total * FPS)):
        t = f / FPS
        lv = spec[min(f, len(spec) - 1)] * (1.0 if t < music else max(0.0, 1 - (t - music) / 2))
        im, prev = mandala(lv, t, prev, p["bg"], p.get("hues", (0.0, 0.8)))
        if t < INTRO_HOLD + INTRO_FADE:
            a = 1.0 if t < INTRO_HOLD else 1 - (t - INTRO_HOLD) / INTRO_FADE
            im = Image.blend(im, intro, a * a * (3 - 2 * a))
        im = im.convert("RGBA"); im.alpha_composite(title); im = im.convert("RGB")
        if t < 0.6:
            im = Image.blend(Image.new("RGB", (W, H)), im, t / 0.6)
        if t > music - XF:
            im = Image.blend(im, card, min(1.0, (t - (music - XF)) / XF))
        im.save(os.path.join(frames, f"{f:05d}.jpg"), quality=92)
    fade_d = p["tail"] - p["start"] - (music - XF)
    final = os.path.join(HERE, "originals", p["out"])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS),
                    "-i", os.path.join(frames, "%05d.jpg"),
                    "-ss", str(p["start"]), "-t", f"{total:.3f}", "-i", p["audio"],
                    "-filter_complex", f"[1:a]afade=t=in:d=0.6,afade=t=out:st={music - XF:.3f}:d={fade_d:.3f},apad[a]",
                    "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final], check=True)
    print("done:", final, f"({total:.1f}s)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or PIECES):
        build(k)

import subprocess, sys, colorsys, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, start, dur, title, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
W, H, FPS, SR = 1080, 1920, 30, 22050
pcm = subprocess.run(["ffmpeg","-loglevel","error","-ss",str(start),"-t",str(dur),"-i",src,"-ac","1","-ar",str(SR),"-f","s16le","-"],capture_output=True).stdout
x = np.frombuffer(pcm, np.int16).astype(float) / 32768
N = 4096; hop = SR // FPS; nb = 48
edges = np.geomspace(60, 8000, nb + 1)
freqs = np.fft.rfftfreq(N, 1 / SR)
win = np.hanning(N)
frames = int(dur * FPS)
spec = []
for f in range(frames):
    i = f * hop
    seg = x[i:i + N]
    if len(seg) < N: seg = np.pad(seg, (0, N - len(seg)))
    m = np.abs(np.fft.rfft(seg * win))
    spec.append([m[(freqs >= a) & (freqs < b)].mean() if np.any((freqs >= a) & (freqs < b)) else 0 for a, b in zip(edges, edges[1:])])
spec = np.log1p(np.array(spec) * 4)
spec /= np.percentile(spec, 99) + 1e-9
spec = np.clip(spec, 0, 1.2)
smooth = np.copy(spec)
for f in range(1, frames):            # fast attack, slow release, like a VU meter
    smooth[f] = np.maximum(spec[f], smooth[f - 1] * 0.86)
title_png = Image.open(title).convert("RGBA")
os.makedirs(out + ".frames", exist_ok=True)
cx, cy = W / 2, 1150
prev = None
for f in range(frames):
    t = f / FPS
    im = Image.new("RGB", (W, H), (7, 6, 15))
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    rot = t * 9
    sym = 8                                            # 8-fold symmetry: each band repeats 8 times, mirrored
    for k in range(nb):
        v = smooth[f, k]
        r0, r1 = 90, 90 + 420 * v
        hue = (k / nb * 0.8 + t / 12) % 1
        col = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.85, 0.55 + 0.45 * min(v, 1)))
        for s in range(sym):
            for sign in (1, -1):
                a = math.radians(rot + s * 360 / sym + sign * (k + 0.5) * (180 / sym) / nb)
                d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                       fill=col, width=5)
    lvl = smooth[f].mean()
    rc = 60 + 40 * lvl
    hue = (t / 12 + 0.5) % 1
    d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), outline=tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.7, 1)), width=4)
    if prev is not None:                               # trails
        layer = Image.blend(layer, prev, 0.0)
        layer = Image.fromarray(np.maximum(np.asarray(layer), (np.asarray(prev) * 0.82).astype(np.uint8)))
    prev = layer
    glow = layer.filter(ImageFilter.GaussianBlur(14))
    im = Image.fromarray(np.clip(np.asarray(im, float) + np.asarray(glow, float) * 0.9 + np.asarray(layer, float), 0, 255).astype(np.uint8))
    im = im.convert("RGBA"); im.alpha_composite(title_png)
    im.convert("RGB").save(f"{out}.frames/{f:05d}.jpg", quality=92)
subprocess.run(["ffmpeg","-loglevel","error","-y","-framerate",str(FPS),"-i",f"{out}.frames/%05d.jpg","-ss",str(start),"-t",str(dur),"-i",src,
                "-map","0:v","-map","1:a","-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-c:a","aac","-shortest",out], check=True)
print("done", out)

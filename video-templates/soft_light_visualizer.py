"""
"Soft light" visualizer Short for a quiet, expressive passage: warm out-of-focus
circles of light drift upward, a central glow breathes with the music (heavily
smoothed so nothing flickers), colors drift amber -> rose -> lavender. Fades in
from black; dissolves into a closing card.

    python3 soft_light_visualizer.py badfinger grateful
"""
import colorsys
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from brand import fraunces, mono, TEXT, GOLD, GOLD_STRONG, TEXT_SOFT, draw_tracked

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
SW, SH = 270, 480            # light is drawn small and scaled up: soft by nature, fast to render
FADE_IN, END_LEN, XF = 3.0, 5.0, 1.5

PIECES = {
    # Track names fixed Nov 2026: the CD import had every title shifted by one track
    "badfinger": {
        "audio": os.path.join(ROOT, "Album Wake Up Rob Reich", "08 Badfinger.mp3"),
        "start": 450.0, "end": 528.0,
        # the studio headphones photo from the site gallery, warmed to rose/peach
        "intro_photo": "site-headphones-acoustic-studio-pink.jpg", "intro_framed": True,
        "head": ("ROB REICH", "BADFINGER", "FROM THE ALBUM WAKE UP"),
        "out": "rob-reich-badfinger-soft-light-short.mp4",
    },
    "grateful": {
        "audio": os.path.join(ROOT, "Album Wake Up Rob Reich", "09 Grateful.mp3"),
        "start": 90.0, "end": 142.0,
        "tail": 143.8,      # last notes ring out; a loud new phrase starts at 143.9, so silent by then
        "end_len": 3.0,
        # Rob's photo opens the Short (a frame to pick as the Shorts cover), then dissolves into the light
        "intro_photo": "about-section-photo.jpg",          # the About-section portrait
        "head": ("ROB REICH", "GRATEFUL", "FROM THE ALBUM WAKE UP"),
        # cool and electric: sapphire, teal, ice, violet on midnight blue
        "palette": [(70, 120, 255), (40, 210, 200), (190, 230, 255), (150, 100, 255)],
        "bg": (6, 10, 22),
        "out": "rob-reich-grateful-soft-light-short.mp4",
    },
}

PALETTE = [(255, 190, 110), (255, 150, 150), (200, 160, 255), (255, 210, 160)]   # amber, rose, lavender, peach


def loudness(src, start, dur):
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", src,
                          "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(float)
    hop = 16000 // FPS
    r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    r /= np.percentile(r, 98) + 1e-9
    s = np.copy(r)
    for i in range(1, len(s)):                  # slow, rounded response
        s[i] = s[i - 1] + (r[i] - s[i - 1]) * 0.06
    return np.clip(s, 0, 1.2)


def color_at(t, offset):
    pal = CUR.get("palette", PALETTE)
    p = (t / 20 + offset) % 1 * len(pal)
    a, b = pal[int(p) % len(pal)], pal[(int(p) + 1) % len(pal)]
    f = p - int(p)
    f = f * f * (3 - 2 * f)
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def title_layer(head):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    small, big, sub = head
    draw_tracked(d, W / 2, 150, small, fraunces(52, 560), TEXT, 10)
    d.rectangle((W / 2 - 50, 228, W / 2 + 50, 230), fill=GOLD)
    size = 118
    while d.textlength(big, font=fraunces(size, 800)) + 2 * len(big) > W - 100:
        size -= 4
    draw_tracked(d, W / 2, 252 + (118 - size) // 2, big, fraunces(size, 800), (247, 240, 226), 2)
    draw_tracked(d, W / 2, 400, sub, mono(30), GOLD, 3)
    return im


def end_card(head):
    im = Image.new("RGB", (W, H), CUR.get("bg", (14, 10, 16)))
    d = ImageDraw.Draw(im)
    small, big, sub = head
    draw_tracked(d, W / 2, 640, small, fraunces(64, 600), TEXT, 10)
    size = 110
    while d.textlength(big, font=fraunces(size, 800)) + 2 * len(big) > W - 100:
        size -= 4
    draw_tracked(d, W / 2, 740, big, fraunces(size, 800), (247, 240, 226), 2)
    d.rectangle((W / 2 - 70, 900, W / 2 + 70, 902), fill=GOLD)
    d.text((W / 2, 980), "from the album Wake Up", font=fraunces(52, 500), fill=TEXT_SOFT, anchor="mm")
    d.text((W / 2, 1080), "robreichguitar.com", font=mono(44, True), fill=GOLD_STRONG, anchor="mm")
    return im


CUR = {}
INTRO_HOLD, INTRO_FADE = 3.0, 2.0     # photo fully visible, then dissolving into the light


def intro_image(p):
    """The photo filling the frame below the title, edges melting into the background."""
    src = Image.open(os.path.join(ROOT, "Gallery Images", p["intro_photo"])).convert("RGB")
    ph, top = H - 470, 470
    if src.height > src.width or p.get("intro_framed"):   # shown whole and centered, edges melting away
        s = min((ph - 80) / src.height, (W - 120) / src.width)
        src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
        im = Image.new("RGB", (W, H), p.get("bg", (14, 10, 16)))
        mask = Image.new("L", src.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((40, 40, src.width - 40, src.height - 40), 80, fill=255)
        im.paste(src, ((W - src.width) // 2, top + (ph - src.height) // 2), mask.filter(ImageFilter.GaussianBlur(40)))
        return im
    s = max(ph / src.height, W / src.width)
    src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    x = min(max(0, round(src.width * p.get("intro_x", 0.5) - W / 2)), src.width - W)
    photo = src.crop((x, 0, x + W, ph))
    im = Image.new("RGB", (W, H), p.get("bg", (14, 10, 16)))
    mask = Image.new("L", (W, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((60, 60, W - 60, ph - 60), 120, fill=255)
    im.paste(photo, (0, top), mask.filter(ImageFilter.GaussianBlur(60)))
    return im


def build(key):
    p = PIECES[key]
    CUR.clear()
    CUR.update(p)
    music = p["end"] - p["start"]
    total = music + p.get("end_len", END_LEN)
    lv = loudness(p["audio"], p["start"], music)
    rnd = random.Random(3)
    orbs = [dict(x=rnd.uniform(0, SW), y=rnd.uniform(0, SH), r=rnd.uniform(10, 34),
                 v=rnd.uniform(1.5, 5.0), sway=rnd.uniform(4, 14), ph=rnd.uniform(0, 6.28),
                 c=rnd.uniform(0, 1), a=rnd.uniform(60, 140)) for _ in range(34)]
    title = title_layer(p["head"])
    intro = intro_image(p) if "intro_photo" in p else None
    card = end_card(p["head"])
    out_dir = os.path.join(HERE, "originals")
    frames = os.path.join(out_dir, f".work-{key}-frames")
    os.makedirs(frames, exist_ok=True)
    n = int(total * FPS)
    global XX, YY
    YY, XX = np.mgrid[0:SH, 0:SW].astype(float)
    for f in range(n):
        t = f / FPS
        level = lv[min(f, len(lv) - 1)] if t < music else 0.0
        # light adds up like real light: soft gaussian orbs on a dark plum background
        acc = np.zeros((SH, SW, 3)) + np.array(CUR.get("bg", (14, 10, 16)), float)
        for o in orbs:                                       # drifting bokeh
            y = (o["y"] - o["v"] * t) % (SH + 80) - 40
            x = o["x"] + o["sway"] * math.sin(t * 0.25 + o["ph"])
            r = o["r"] * (0.85 + 0.35 * level)
            g = np.exp(-((XX - x) ** 2 + (YY - y) ** 2) / (r * r))
            acc += g[..., None] * np.array(color_at(t, o["c"]), float) * (o["a"] / 255) * (0.45 + 0.4 * level)
        cr = 38 + 34 * level                                 # the central glow breathes with the music
        g = np.exp(-((XX - SW / 2) ** 2 + (YY - SH * 0.58) ** 2) / (cr * cr))
        acc += g[..., None] * np.array(color_at(t, 0.5), float) * (0.35 + 0.55 * level)
        bg = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8))
        im = bg.convert("RGB").resize((W, H), Image.BICUBIC)
        if intro is not None and t < INTRO_HOLD + INTRO_FADE:
            a = 1.0 if t < INTRO_HOLD else 1 - (t - INTRO_HOLD) / INTRO_FADE
            im = Image.blend(im, intro, a * a * (3 - 2 * a))
        im = im.convert("RGBA")
        ta = 1.0 if intro is not None else min(1.0, max(0.0, (t - 1.0) / 2.0))   # title fades in after the light
        if ta > 0:
            tl = title.copy()
            tl.putalpha(tl.getchannel("A").point(lambda v: int(v * ta)))
            im.alpha_composite(tl)
        im = im.convert("RGB")
        if t < (0.8 if intro is not None else FADE_IN):      # from black
            fade = 0.8 if intro is not None else FADE_IN
            im = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), im, t / fade)
        if t > music - XF:                                   # dissolve into the closing card
            im = Image.blend(im, card, min(1.0, (t - (music - XF)) / XF))
        im.save(os.path.join(frames, f"{f:05d}.jpg"), quality=92)
    final = os.path.join(out_dir, p["out"])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS),
                    "-i", os.path.join(frames, "%05d.jpg"),
                    "-ss", str(p["start"]), "-t", str(total), "-i", p["audio"],
                    # the music keeps playing under the closing card, fading over its last seconds;
                    # with a "tail", it fades from the card's dissolve to silence at that moment
                    "-filter_complex", "[1:a]afade=t=in:d=1.5," + (
                        f"afade=t=out:st={music - XF:.3f}:d={p['tail'] - p['start'] - (music - XF):.3f},apad[a]"
                        if "tail" in p else f"afade=t=out:st={total - 2.5:.3f}:d=2.5,apad[a]"),
                    "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final], check=True)
    print("done:", final, f"({total:.1f}s)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or PIECES):
        build(k)

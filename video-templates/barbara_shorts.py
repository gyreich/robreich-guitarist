"""
Draft social shorts cut from the live "Barbara" trio video.

  1_peak    1:12-1:40  4:5 crop on Rob   (feed / Reels)
  2_finish  1:40-2:01  4:5 crop on Rob   (feed / Reels)
  3_trio    0:16-0:40  9:16, full wide shot framed on a dark brand canvas

Overlays are rendered with PIL in the site's brand fonts/colors, then
composited onto the video with ffmpeg.

    python3 barbara_shorts.py
"""
import os
import subprocess
from PIL import Image, ImageDraw

from brand import fraunces, mono, draw_tracked, GOLD, TEXT, TEXT_SOFT, PAPER_DARK
from portrait_frame import dark_canvas
from brand import vignette

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "Rob Reich,Eliot Zigmund, Rene Hart -Barbara.MOV.mp4")
OUT = os.path.join(HERE, "barbara-shorts")

# Lift the very dark club footage a bit without flattening it.
GRADE = "eq=brightness=0.04:contrast=1.06:saturation=0.92:gamma=1.18"

CREDIT = "ELIOT ZIGMUND · DRUMS    RENE HART · BASS"


def gradient_band(im, y0, y1, max_alpha, fade_down=True):
    """Dark fade so overlay text stays readable over the footage."""
    w, _ = im.size
    band = Image.new("RGBA", (w, y1 - y0))
    d = ImageDraw.Draw(band)
    h = y1 - y0
    for y in range(h):
        t = y / h if fade_down else 1 - y / h
        a = int(max_alpha * (t ** 1.3))
        d.line([(0, y), (w, y)], fill=(10, 7, 4, a))
    im.alpha_composite(band, (0, y0))


def feed_overlay(path, hook_path, hook_line1, hook_line2):
    """1080x1350 overlay (transparent) + separate timed hook card."""
    W, H = 1080, 1350
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gradient_band(im, 0, 170, 170, fade_down=False)
    gradient_band(im, H - 430, H, 235, fade_down=True)
    d = ImageDraw.Draw(im)
    draw_tracked(d, W / 2, 46, "ROB REICH TRIO  ·  LIVE", mono(28, True), GOLD, 4)
    draw_tracked(d, W / 2, H - 300, "Barbara", fraunces(118, 600), TEXT, 1)
    d.line([(W / 2 - 60, H - 150), (W / 2 + 60, H - 150)], fill=GOLD, width=2)
    draw_tracked(d, W / 2, H - 122, CREDIT, mono(25), TEXT_SOFT, 2)
    im.save(path)

    hook = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hook)
    box_w, box_h = 900, 190
    bx, by = (W - box_w) // 2, H - 570
    hd.rounded_rectangle((bx, by, bx + box_w, by + box_h), 18,
                         fill=PAPER_DARK + (225,), outline=GOLD + (255,), width=2)
    draw_tracked(hd, W / 2, by + 34, hook_line1, fraunces(54, 600), TEXT, 0)
    draw_tracked(hd, W / 2, by + 112, hook_line2, mono(26, True), GOLD, 3)
    hook.save(hook_path)


def vertical_background(path):
    """1080x1920 opaque brand canvas with titles; the video sits in a framed box."""
    W, H = 1080, 1920
    canvas = vignette(dark_canvas(W, H), strength=0.35).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    vy0, vy1 = 640, 640 + 563          # video box (1000x563) top/bottom
    vx0, vx1 = 40, 1040
    draw_tracked(d, W / 2, 300, "ROB REICH TRIO  ·  LIVE", mono(30, True), GOLD, 5)
    draw_tracked(d, W / 2, 380, "Barbara", fraunces(150, 600), TEXT, 1)
    # gold hairline frame, matching portrait_frame.py
    d.rectangle((vx0 - 1, vy0 - 1, vx1, vy1), outline=GOLD, width=1)
    faint = tuple(int(c * 0.55) for c in GOLD)
    d.rectangle((vx0 - 7, vy0 - 7, vx1 + 6, vy1 + 6), outline=faint, width=1)
    y = vy1 + 110
    for name, role in [("ROB REICH", "GUITAR"), ("ELIOT ZIGMUND", "DRUMS"), ("RENE HART", "BASS")]:
        draw_tracked(d, W / 2, y, name, mono(40, True), TEXT, 5)
        draw_tracked(d, W / 2, y + 56, role, mono(24), TEXT_SOFT, 6)
        y += 150
    canvas.convert("RGB").save(path)


def vertical_hook(path):
    W, H = 1080, 1920
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_tracked(d, W / 2, 560, "with Bill Evans' drummer, Eliot Zigmund", mono(30, True), GOLD, 1)
    im.save(path)


def run(args):
    print(" ".join(a if " " not in a else repr(a) for a in args[-1:]))
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def fades(dur):
    v = f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.8:.2f}:d=0.8"
    a = f"afade=t=in:st=0:d=0.3,afade=t=out:st={dur - 1.0:.2f}:d=1.0"
    return v, a


ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
       "-r", "30", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]


def feed_short(name, start, dur, hook1, hook2):
    ov, hk = os.path.join(OUT, f".{name}_ov.png"), os.path.join(OUT, f".{name}_hook.png")
    feed_overlay(ov, hk, hook1, hook2)
    vf, af = fades(dur)
    fc = (f"[0:v]crop=576:720:40:0,scale=1080:1350:flags=lanczos,{GRADE}[v];"
          f"[v][1:v]overlay=0:0[v1];"
          f"[2:v]format=rgba,fade=t=in:st=0.3:d=0.4:alpha=1,fade=t=out:st=3.6:d=0.5:alpha=1[h];"
          f"[v1][h]overlay=0:0:enable='lt(t,4.2)',{vf}[out];[0:a]{af}[a]")
    run(["-ss", str(start), "-t", str(dur), "-i", SRC,
         "-i", ov, "-loop", "1", "-t", str(dur), "-i", hk,
         "-filter_complex", fc, "-map", "[out]", "-map", "[a]", "-t", str(dur)]
        + ENC + [os.path.join(OUT, f"{name}.mp4")])


def vertical_short(name, start, dur):
    bg, hk = os.path.join(OUT, f".{name}_bg.png"), os.path.join(OUT, f".{name}_hook.png")
    vertical_background(bg)
    vertical_hook(hk)
    vf, af = fades(dur)
    fc = (f"[0:v]scale=1000:563:flags=lanczos,{GRADE}[v];"
          f"[1:v][v]overlay=40:640[c];"
          f"[2:v]format=rgba,fade=t=in:st=0.8:d=0.6:alpha=1[h];"
          f"[c][h]overlay=0:0,{vf}[out];[0:a]{af}[a]")
    run(["-ss", str(start), "-t", str(dur), "-i", SRC,
         "-loop", "1", "-t", str(dur), "-i", bg,
         "-loop", "1", "-t", str(dur), "-i", hk,
         "-filter_complex", fc, "-map", "[out]", "-map", "[a]", "-t", str(dur)]
        + ENC + [os.path.join(OUT, f"{name}.mp4")])


def youtube_version(name):
    """9:16 for YouTube Shorts: the 4:5 render sits high on the dark brand canvas,
    so its titles clear YouTube's bottom caption/channel overlay."""
    bg = os.path.join(OUT, f".{name}_ytbg.png")
    vignette(dark_canvas(1080, 1920), strength=0.35).save(bg)
    run(["-loop", "1", "-i", bg, "-i", os.path.join(OUT, f"{name}.mp4"),
         "-filter_complex", "[0:v][1:v]overlay=0:180:shortest=1[out]",
         "-map", "[out]", "-map", "1:a"] + ENC + [os.path.join(OUT, f"{name}_youtube.mp4")])


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    feed_short("1_peak", 72, 28, "Bill Evans' drummer on the kit", "ELIOT ZIGMUND · ROB REICH TRIO")
    feed_short("2_finish", 100, 21, "Rob Reich – live", "WITH ELIOT ZIGMUND & RENE HART")
    vertical_short("3_trio", 16, 24)
    youtube_version("1_peak")
    youtube_version("2_finish")
    for f in sorted(os.listdir(OUT)):
        if f.startswith("."):
            os.remove(os.path.join(OUT, f))
    print("done:", OUT)

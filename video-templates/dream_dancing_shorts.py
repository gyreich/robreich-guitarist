"""
YouTube Shorts (9:16) cut from the live "Dream Dancing (pt 2)" trio video.

Cooler look than the Barbara set: the footage gets a split grade (brown
paneling pushed toward navy in the shadows, skin kept warm in the highlights)
and sits on a deep-blue "stage light" backdrop, following the New Day short.

  dd_1_peak   1:08-1:34  4:5 crop on Rob, framed
  dd_2_trio   0:20-0:46  full wide shot, framed
  dd_3_close  1:46-end   4:5 crop on Rob, framed

    python3 dream_dancing_shorts.py
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

from brand import fraunces, mono, draw_tracked, GOLD, TEXT
from barbara_shorts import run, fades, ENC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "Rob Reich, Eliot Zigmund, Rene Hart.MOV Dream Dancing pt 2 (1).mp4")
OUT = os.path.join(HERE, "dream-dancing-shorts")

W, H = 1080, 1920
NAVY_DEEP = (7, 11, 24)
NAVY = (14, 24, 52)
STAGE_BLUE = (46, 86, 170)
ICE = (172, 190, 222)      # soft secondary text on navy
PANEL = (12, 20, 42)       # hook card fill

GRADE = ("eq=brightness=0.05:contrast=1.06:gamma=1.24,"
         "huesaturation=saturation=-0.75:colors=r+y,"
         "colorbalance=rs=-0.16:gs=-0.02:bs=0.22:rm=-0.05:bm=0.07:rh=0.05:gh=0.02:bh=-0.03,"
         "eq=contrast=1.1:saturation=1.1")

TITLE = "Dream Dancing"


def stage_canvas(seed=7, size=None):
    """Deep navy with a soft overhead stage-light glow and faint bokeh."""
    w, h = size or (W, H)
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), NAVY_DEEP)
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(255 * max(0.0, 1 - abs(y - h * 0.42) / (h * 0.62)) ** 1.6))
    im = Image.composite(Image.new("RGB", (w, h), NAVY), im, grad.resize((w, h)))

    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((w * 0.05, -h * 0.12, w * 0.95, h * 0.42), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    im = Image.composite(Image.new("RGB", (w, h), STAGE_BLUE), im, glow)

    bokeh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bokeh)
    for _ in range(46):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(4, 22)
        col = rnd.choice([(120, 160, 255), (150, 130, 255), (90, 140, 230), GOLD])
        bd.ellipse((x - r, y - r, x + r, y + r), fill=col + (rnd.randint(25, 70),))
    bokeh = bokeh.filter(ImageFilter.GaussianBlur(6))
    im = im.convert("RGBA")
    im.alpha_composite(bokeh)
    return im


def hairline(d, box):
    x0, y0, x1, y1 = box
    d.rectangle((x0 - 1, y0 - 1, x1, y1), outline=GOLD, width=1)
    faint = tuple(int(c * 0.5) for c in GOLD)
    d.rectangle((x0 - 7, y0 - 7, x1 + 6, y1 + 6), outline=faint, width=1)


def background(path, box, credits_y, stacked_credits, tagline=None):
    im = stage_canvas()
    d = ImageDraw.Draw(im)
    if tagline:
        draw_tracked(d, W / 2, box[1] - 80, tagline, mono(30, True), GOLD, 1)
    draw_tracked(d, W / 2, box[1] - 300, "ROB REICH TRIO  ·  LIVE", mono(30, True), GOLD, 5)
    draw_tracked(d, W / 2, box[1] - 240, TITLE, fraunces(110, 600), TEXT, 0)
    hairline(d, box)
    if stacked_credits:
        y = credits_y
        for name, role in [("ROB REICH", "GUITAR"), ("ELIOT ZIGMUND", "DRUMS"), ("RENE HART", "BASS")]:
            draw_tracked(d, W / 2, y, name, mono(40, True), TEXT, 5)
            draw_tracked(d, W / 2, y + 56, role, mono(24), ICE, 6)
            y += 150
    else:
        draw_tracked(d, W / 2, credits_y, "ELIOT ZIGMUND · DRUMS    RENE HART · BASS", mono(26), ICE, 2)
    im.convert("RGB").save(path)


def hook_card(path, cy, line1, line2):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bw, bh = 880, 180
    bx, by = (W - bw) // 2, cy - bh // 2
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 18, fill=PANEL + (225,), outline=GOLD + (255,), width=2)
    draw_tracked(d, W / 2, by + 32, line1, fraunces(52, 600), TEXT, 0)
    draw_tracked(d, W / 2, by + 106, line2, mono(25, True), GOLD, 3)
    im.save(path)


def render(name, start, dur, crop, box, credits_y, stacked, hook=None, tagline=None):
    """hook: (line1, line2) card shown over the video for the first 4s."""
    bg = os.path.join(OUT, f".{name}_bg.png")
    hk = os.path.join(OUT, f".{name}_hook.png")
    background(bg, box, credits_y, stacked, tagline)
    if hook:
        hook_card(hk, box[3] - 190, *hook)
    else:
        Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(hk)
    x0, y0, x1, y1 = box
    vf, af = fades(dur)
    fc = (f"[0:v]{crop}scale={x1 - x0}:{y1 - y0}:flags=lanczos,{GRADE}[v];"
          f"[1:v][v]overlay={x0}:{y0}[c];"
          f"[2:v]format=rgba,fade=t=in:st=0.3:d=0.4:alpha=1,fade=t=out:st=3.8:d=0.5:alpha=1[h];"
          f"[c][h]overlay=0:0:enable='lt(t,4.4)',{vf}[out];[0:a]{af}[a]")
    run(["-ss", str(start), "-t", str(dur), "-i", SRC,
         "-loop", "1", "-t", str(dur), "-i", bg,
         "-loop", "1", "-t", str(dur), "-i", hk,
         "-filter_complex", fc, "-map", "[out]", "-map", "[a]", "-t", str(dur)]
        + ENC + [os.path.join(OUT, f"{name}.mp4")])


# Rob's framing: a 576-wide window starting at x=60 holds him and the guitar
# neck from ~0:15 onward (the camera drifts right before that).
CROP_ROB = "crop=576:720:60:0,"
BOX_ROB = (60, 420, 1020, 1620)          # 960x1200, 4:5
BOX_WIDE = (40, 640, 1040, 1203)         # 1000x563, 16:9

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    render("dd_1_peak", 68, 26, CROP_ROB, BOX_ROB, 1665, False,
           ("Rob Reich – live", "WITH ELIOT ZIGMUND & RENE HART"))
    render("dd_2_trio", 20, 26, "", BOX_WIDE, 1313, True,
           tagline="with Bill Evans' drummer, Eliot Zigmund")
    render("dd_3_close", 106, 27.4, CROP_ROB, BOX_ROB, 1665, False,
           ("Cole Porter, live", "ROB REICH · GUITAR"))
    for f in os.listdir(OUT):
        if f.startswith("."):
            os.remove(os.path.join(OUT, f))
    print("done:", OUT)

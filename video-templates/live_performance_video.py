"""
Polished full-length upload of a live performance clip:
  - the Dream Dancing shorts' cool grade (less brown paneling)
  - a lower-third title with the players' names over the first seconds
  - a small robreichguitar.com credit in the corner while the band plays
  - a 15s closing card (brand style), its right half left clear for
    YouTube's end-screen buttons

    python3 live_performance_video.py
"""
import os
import subprocess
from PIL import Image, ImageDraw

from brand import fraunces, mono, draw_tracked, GOLD, TEXT, TEXT_SOFT
from dream_dancing_shorts import GRADE
from portrait_frame import dark_canvas
from brand import vignette

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS = 1920, 1080, 30
END_LEN = 15.0

PERFORMANCES = {
    "dream-dancing-part2": {
        "src": "Rob Reich, Eliot Zigmund, Rene Hart.MOV Dream Dancing pt 2 (1).mp4",
        "song": "Dream Dancing",
        "kicker": "ROB REICH TRIO  ·  COLE PORTER  ·  LIVE",
        "players": "ROB REICH guitar   ·   ELIOT ZIGMUND drums   ·   RENE HART bass",
    },
    "barbara": {
        "src": "Rob Reich,Eliot Zigmund, Rene Hart -Barbara.MOV.mp4",
        "song": "Barbara",
        "kicker": "ROB REICH TRIO  ·  HORACE SILVER  ·  LIVE",
        "players": "ROB REICH guitar   ·   ELIOT ZIGMUND drums   ·   RENE HART bass",
    },
}


def lower_third(path, song, kicker, players):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    band = Image.new("RGBA", (W, 300))
    bd = ImageDraw.Draw(band)
    for y in range(300):                       # dark fade so the text reads over footage
        bd.line([(0, y), (W, y)], fill=(8, 10, 22, int(215 * (y / 300) ** 1.2)))
    im.alpha_composite(band, (0, H - 300))
    d = ImageDraw.Draw(im)
    d.text((96, H - 228), kicker, font=mono(26, True), fill=GOLD)
    d.text((92, H - 190), song, font=fraunces(84, 600), fill=TEXT)
    d.rectangle((96, H - 86, 96 + 120, H - 84), fill=GOLD)
    d.text((96, H - 66), players, font=mono(25), fill=(205, 212, 230))
    im.save(path)


def corner_credit(path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W - 48, H - 40), "robreichguitar.com", font=mono(24, True),
           fill=(236, 230, 214, 150), anchor="rs")
    im.save(path)


def end_card(path):
    im = vignette(dark_canvas(W, H), strength=0.4)
    d = ImageDraw.Draw(im)
    cx = 520
    draw_tracked(d, cx, 300, "ROB REICH", fraunces(96, 700), TEXT, 8)
    d.rectangle((cx - 90, 432, cx + 90, 434), fill=GOLD)
    draw_tracked(d, cx, 462, "JAZZ  ·  R&B  ·  ROCK  ·  POP", mono(26), GOLD, 5)
    draw_tracked(d, cx, 540, "robreichguitar.com", fraunces(44, 520), (230, 222, 205), 1)
    draw_tracked(d, cx, 650, "FREE COURSE: MASTER THE MODES WITH ROB", mono(24, True), TEXT_SOFT, 2)
    draw_tracked(d, cx, 694, "on the website", fraunces(30, 400), TEXT_SOFT, 0)
    im.convert("RGB").save(path)


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def duration(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def build(key):
    p = PERFORMANCES[key]
    out_dir = os.path.join(HERE, "live-videos")
    tmp = os.path.join(out_dir, ".work")
    os.makedirs(tmp, exist_ok=True)
    lt, cc, ec = (os.path.join(tmp, f"{key}-{n}.png") for n in ("lower", "corner", "end"))
    lower_third(lt, p["song"], p["kicker"], p["players"])
    corner_credit(cc)
    end_card(ec)

    src = os.path.join(ROOT, p["src"])
    dur = duration(src)
    xf = 1.0                                   # performance dissolves into the end card
    total = dur + END_LEN - xf
    fc = (
        f"[0:v]scale={W}:{H}:flags=lanczos,{GRADE},fps={FPS},format=yuv420p,setsar=1[perf];"
        f"[1:v]format=rgba,fade=t=in:st=1.0:d=0.7:alpha=1,fade=t=out:st=8.0:d=0.8:alpha=1[lt];"
        f"[2:v]format=rgba,fade=t=in:st=10:d=1:alpha=1[cc];"
        f"[perf][lt]overlay=0:0:enable='lt(t,9)'[a];"
        f"[a][cc]overlay=0:0:enable='gte(t,10)'[b];"
        f"[3:v]fps={FPS},format=yuv420p,setsar=1[end];"
        f"[b][end]xfade=transition=fade:duration={xf}:offset={dur - xf:.3f}[v];"
        f"[0:a]afade=t=in:d=0.3,afade=t=out:st={dur - 2.0:.3f}:d=2.0,apad=pad_dur={END_LEN}[aud]"
    )
    final = os.path.join(out_dir, f"rob-reich-trio-{key}.mp4")
    run(["-i", src,
         "-loop", "1", "-t", f"{dur:.3f}", "-i", lt,
         "-loop", "1", "-t", f"{dur:.3f}", "-i", cc,
         "-loop", "1", "-framerate", str(FPS), "-t", f"{END_LEN:.3f}", "-i", ec,
         "-filter_complex", fc, "-map", "[v]", "-map", "[aud]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", final])
    print(f"done: {final} ({total:.1f}s; end card from {dur - xf:.1f}s)")


if __name__ == "__main__":
    import sys
    for k in (sys.argv[1:] or PERFORMANCES):   # e.g. python3 live_performance_video.py barbara
        build(k)

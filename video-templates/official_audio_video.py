"""
"Official Audio" video for one of Rob's original recordings: an opening title
card over a photo, a few photos of Rob playing (each with a slow push-in,
dissolving into the next), a small robreichguitar.com credit, and the closing
card (left half kept clear of photos for YouTube's end-screen elements).

    python3 official_audio_video.py new-swing
"""
import os
import subprocess
import sys
from PIL import Image

from brand import W, H, mono, vignette
from opening_card import make_opening_card
from closing_card import make_closing_card
from portrait_frame import dark_canvas, place_portrait
from PIL import ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAL = os.path.join(ROOT, "Gallery Images")
FPS = 30
OPEN_LEN = 8.0          # title card
CLOSE_LEAD = 12.0       # closing card starts this long before the music ends
TAIL = 6.0              # closing card holds after the music (end screen needs >= 5s)
XF = 1.5                # dissolve between photos

# photos: (file in Gallery Images, "full" = fill the frame, "framed" = whole photo in a gold frame,
#          vertical anchor for "full" crops: 0 keeps the top, 0.5 the middle)
TRACKS = {
    "new-swing": {
        "audio": os.path.join(ROOT, "recordings", "new-swing.mp3"),
        "title": "NEW SWING",
        "album": None,
        "photos": [
            ("walter-smith-photo-rob-pleasantdale-chateau-natural.jpg", "full", 0.0),
            ("rr-jazz-brunch-falcon.jpg", "framed", 0.5),
            ("rr-Elliot-zigmund-john-richmond.jpg", "full", 0.3),
            ("SanDiegoYachtRockFestivalwith.jpg", "full", 0.3),
        ],
        "close_photo": "Rob-listen-headphone-guitar.png",
        "out": "rob-reich-new-swing-official-audio.mp4",
    },
}


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def duration(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def fill_crop(im, anchor_y):
    """Scale to fill 16:9, cropping the overflow; anchor_y picks which band of a tall photo stays."""
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = round((im.height - H) * anchor_y)
    return im.crop((x, y, x + W, y + H))


def still(photo, mode, anchor_y, path):
    """A 2x-size still (3840x2160) so the slow push-in stays smooth."""
    src = os.path.join(GAL, photo)
    if mode == "full":
        im = vignette(fill_crop(Image.open(src).convert("RGB"), anchor_y), strength=0.3)
    else:
        im, _ = place_portrait(vignette(dark_canvas(), strength=0.4), src, (260, 70, W - 260, H - 70),
                               glow_strength=0.3)
    d = ImageDraw.Draw(im)
    d.text((W - 48, H - 40), "robreichguitar.com", font=mono(24, True),
           fill=(236, 230, 214), anchor="rs")
    im.resize((W * 2, H * 2), Image.LANCZOS).save(path)


def push_in(png, seconds, out):
    n = int(round(seconds * FPS))
    run(["-loop", "1", "-framerate", str(FPS), "-t", f"{seconds:.3f}", "-i", png,
         "-vf", f"zoompan=z='1+0.05*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={W}x{H}:fps={FPS},format=yuv420p",
         "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])


def hold(png, seconds, out):
    run(["-loop", "1", "-framerate", str(FPS), "-t", f"{seconds:.3f}", "-i", png,
         "-vf", f"scale={W}:{H},format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])


def build(key):
    t = TRACKS[key]
    out_dir = os.path.join(HERE, "originals")
    tmp = os.path.join(out_dir, f".work-{key}")
    os.makedirs(tmp, exist_ok=True)
    music = duration(t["audio"])
    total = music + TAIL

    # timeline: opening card, photos sharing the middle, closing card
    close_start = music - CLOSE_LEAD
    n = len(t["photos"])
    each = (close_start - OPEN_LEN + n * XF) / n   # each clip overlaps the next by XF
    clips = []

    op = os.path.join(tmp, "open.png")
    bg = os.path.join(tmp, "open-bg.png")    # same anchored crop as the first photo
    photo, _mode, anchor_y = t["photos"][0]
    fill_crop(Image.open(os.path.join(GAL, photo)).convert("RGB"), anchor_y).save(bg)
    make_opening_card(bg, op, track=t["title"], album_name=t["album"])
    clips.append((op, OPEN_LEN + XF, "hold"))
    for k, (photo, mode, anchor_y) in enumerate(t["photos"]):
        png = os.path.join(tmp, f"photo{k}.png")
        still(photo, mode, anchor_y, png)
        clips.append((png, each, "push"))
    cl = os.path.join(tmp, "close.png")
    make_closing_card(os.path.join(GAL, t["close_photo"]), cl)
    clips.append((cl, total - close_start, "hold"))

    parts = []
    for k, (png, secs, kind) in enumerate(clips):
        mp4 = os.path.join(tmp, f"clip{k}.mp4")
        (push_in if kind == "push" else hold)(png, secs, mp4)
        parts.append((mp4, secs))

    inputs, fc, label, off = [], [], "[0:v]", 0.0
    for mp4, _ in parts:
        inputs += ["-i", mp4]
    for k in range(1, len(parts)):
        off += parts[k - 1][1] - XF
        nxt = f"[v{k}]"
        fc.append(f"{label}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{nxt}")
        label = nxt
    fc.append(f"[{len(parts)}:a]afade=t=out:st={music - 1.5:.3f}:d=1.5,apad=pad_dur={TAIL}[a]")

    final = os.path.join(out_dir, t["out"])
    run(inputs + ["-i", t["audio"], "-filter_complex", ";".join(fc),
                  "-map", label, "-map", "[a]", "-t", f"{total:.3f}",
                  "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                  "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", final])
    print(f"done: {final} ({total:.1f}s; closing card from {close_start:.1f}s)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or TRACKS):
        build(k)

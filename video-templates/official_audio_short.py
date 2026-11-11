"""
Vertical Short (1080x1920) for an "Official Audio" track: the strongest ~40s of
the song over vertical crops of the same photos (slow push-in, dissolves), the
title at the top, and a closing card pointing to the full track (YouTube's
Related video link) and the website.

    python3 official_audio_short.py lift-off
"""
import os
import sys
from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD, GOLD_STRONG, TEXT_SOFT, draw_tracked, vignette
from portrait_frame import dark_canvas, place_portrait
from official_audio_video import GAL, FPS, run, smooth_push

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H = 1080, 1920
XF = 0.8
TOP = 470          # title band height on photo slides
END_LEN = 4.0

# photos: (file, "full" crop centered on x (0-1 across the photo) | "framed")
SHORTS = {
    "lift-off": {          # was "New Swing"
        "audio": os.path.join(ROOT, "recordings", "lift-off.mp3"),
        "title": "LIFT OFF",
        "head": ("ROB REICH", "LIFT OFF", "FROM THE ALBUM HOMEWARD"),
        "start": 113.0, "end": 152.3,      # the build to the loudest stretch
        "photos": [
            ("walter-smith-photo-rob-pleasantdale-chateau-natural.jpg", "full", 0.36),
            ("sylvain-durand-rob.jpg", "framed", None),
            ("rob-club-hollowbody-trio.png", "full", 0.30),
            ("rr-Elliot-zigmund-john-richmond.jpg", "full", 0.16),
        ],
        "out": "rob-reich-lift-off-short.mp4",
    },
    # Rob's solo on a 1994 band album: credits from the CD jacket
    "mohegan-everythings-fried": {
        "audio": os.path.join(ROOT, "Album Mohegan Fried", "02 Everything's Fried.mp3"),
        "head": ("ROB REICH", "GUITAR SOLO", "MOHEGAN  \u00b7  EVERYTHING'S FRIED  \u00b7  1994"),
        "card": ("ROB REICH", "on electric guitar", "Mohegan, Fried (1994)", "More of Rob's music:"),
        "start": 154.5, "end": 181.8,
        "photos": [
            ("mohegan-fried-cover.jpg", "framed", None),
            ("Rob-many-years-ago.png", "framed", None),           # younger Rob, closer to 1994
            ("rr-shared-by-peter-salo.jpg", "framed", None),      # Peter Salo photo
            ("rob-hilltop-action-closeup.png", "full", 0.5),      # ZeeZee Shots Photography
        ],
        "out": "rob-reich-mohegan-everythings-fried-solo-short.mp4",
    },
}


def vertical(photo, mode, cx, path):
    src = Image.open(os.path.join(GAL, photo)).convert("RGB")
    if mode == "full":
        # photo fills the frame below the title band, so the title never covers a face
        ph = H - TOP
        s = max(ph / src.height, W / src.width)
        im = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
        x = min(max(0, round(im.width * cx - W / 2)), im.width - W)
        photo_part = im.crop((x, 0, x + W, ph))
        im = vignette(dark_canvas(W, H), strength=0.4)
        im.paste(photo_part, (0, TOP))
        fade = Image.new("L", (1, 160))       # blend the photo's top edge into the dark band
        for y in range(160):
            fade.putpixel((0, y), int(255 * y / 159))
        top = im.crop((0, TOP, W, TOP + 160))
        im.paste(Image.composite(top, Image.new("RGB", (W, 160), im.getpixel((W // 2, TOP - 4))),
                                 fade.resize((W, 160))), (0, TOP))
    else:
        im, _ = place_portrait(vignette(dark_canvas(W, H), strength=0.4), os.path.join(GAL, photo),
                               (70, TOP + 30, W - 70, 1600), glow_strength=0.3)
    # title band at the top, over a soft dark fade so it reads on any photo
    band = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for y in range(520):
        bd.line([(0, y), (W, y)], fill=(8, 8, 12, int(200 * (1 - y / 520) ** 1.3)))
    im = im.convert("RGBA")
    im.alpha_composite(band)
    im.convert("RGB").resize((W * 2, H * 2), Image.LANCZOS).save(path)


def title_layer(path):
    """The title, drawn once and laid over every photo so it stays put through the dissolves."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    small, big, sub = SPEC[0].get("head", ("ROB REICH", SPEC[0].get("title", ""), "OFFICIAL AUDIO"))
    draw_tracked(d, W / 2, 150, small, fraunces(52, 560), TEXT, 10)
    d.rectangle((W / 2 - 50, 228, W / 2 + 50, 230), fill=GOLD)
    draw_tracked(d, W / 2, 252, big, fraunces(118, 800), (247, 240, 226), 2)
    draw_tracked(d, W / 2, 400, sub, mono(30), GOLD, 9 if len(sub) < 20 else 3)
    im.save(path)


def end_card(path):
    im = vignette(dark_canvas(W, H), strength=0.4)
    d = ImageDraw.Draw(im)
    if "card" in SPEC[0]:
        name, role, where, more = SPEC[0]["card"]
        draw_tracked(d, W / 2, 620, name, fraunces(96, 800), (247, 240, 226), 6)
        d.text((W / 2, 790), role, font=fraunces(56, 500), fill=TEXT, anchor="mm")
        d.text((W / 2, 862), where, font=fraunces(48, 400), fill=TEXT_SOFT, anchor="mm")
        d.rectangle((W / 2 - 70, 930, W / 2 + 70, 932), fill=GOLD)
        d.text((W / 2, 1034), more, font=fraunces(56, 600), fill=TEXT, anchor="mm")
    else:
        draw_tracked(d, W / 2, 620, "ROB REICH", fraunces(64, 600), TEXT, 10)
        draw_tracked(d, W / 2, 720, SPEC[0]["title"], fraunces(110, 800), (247, 240, 226), 2)
        d.rectangle((W / 2 - 70, 880, W / 2 + 70, 882), fill=GOLD)
        d.text((W / 2, 960), "Hear the full track:", font=fraunces(56, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1034), "tap the video link below", font=fraunces(56, 600), fill=TEXT, anchor="mm")
    d.text((W / 2, 1140), "robreichguitar.com", font=mono(44, True), fill=GOLD_STRONG, anchor="mm")
    im.resize((W * 2, H * 2), Image.LANCZOS).save(path)


def push_in(png, seconds, out):
    smooth_push(png, seconds, out, W, H, 0.07)


SPEC = [{}]


def build(key):
    t = SHORTS[key]
    SPEC[0] = t
    out_dir = os.path.join(HERE, "originals")
    tmp = os.path.join(out_dir, f".work-{key}-short")
    os.makedirs(tmp, exist_ok=True)
    music = t["end"] - t["start"]
    total = music + END_LEN
    n = len(t["photos"])
    each = (music + n * XF) / n                  # photos fill the music; the end card follows
    tl = os.path.join(tmp, "title.png")
    title_layer(tl)
    clips = []
    for k, (photo, mode, cx) in enumerate(t["photos"]):
        png = os.path.join(tmp, f"v{k}.png")
        vertical(photo, mode, cx, png)
        clips.append((png, each))
    ec = os.path.join(tmp, "end.png")
    end_card(ec)
    clips.append((ec, END_LEN + XF))
    parts = []
    for k, (png, secs) in enumerate(clips):
        mp4 = os.path.join(tmp, f"c{k}.mp4")
        push_in(png, secs, mp4)
        parts.append((mp4, secs))

    inputs, fc, label, off = [], [], "[0:v]", 0.0
    for mp4, _ in parts:
        inputs += ["-i", mp4]
    for k in range(1, len(parts)):
        off += parts[k - 1][1] - XF
        fc.append(f"{label}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]")
        label = f"[v{k}]"
    # title on top of the photos, fading out as the end card dissolves in
    fc.append(f"[{len(parts) + 1}:v]format=rgba,fade=t=out:st={music - XF:.3f}:d={XF}:alpha=1[tl];"
              f"{label}[tl]overlay=0:0:shortest=0[vt]")
    label = "[vt]"
    fc.append(f"[{len(parts)}:a]atrim=start={t['start']}:end={t['end']},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.4,afade=t=out:st={music - 2.5:.3f}:d=2.5,apad=pad_dur={END_LEN}[a]")
    final = os.path.join(out_dir, t["out"])
    run(inputs + ["-i", t["audio"], "-loop", "1", "-framerate", str(FPS), "-t", f"{total:.3f}", "-i", tl,
                  "-filter_complex", ";".join(fc), "-map", label, "-map", "[a]",
                  "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
                  "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                  "-movflags", "+faststart", final])
    print(f"done: {final} ({total:.1f}s)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or SHORTS):
        build(k)

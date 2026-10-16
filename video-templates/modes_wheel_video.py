"""
"Hear the 7 Modes" -- a 16:9 YouTube video built from the Master the Modes
Intro Tracks, using the same brightest-to-darkest wheel as the website.

Each mode: Rob plays the Intro Track (25s), then his guitar drops out and
the backing keeps going (9s) -- the site's "your turn" switch, shown on
screen. Ends on a "try it yourself" card with the website address.

    python3 modes_wheel_video.py          # renders modes-video/ (video, thumbnail, chapters)
    python3 modes_wheel_video.py --stills # just the preview frames
"""
import math
import os
import subprocess
import sys
from PIL import Image, ImageDraw

from brand import fraunces, mono, draw_tracked, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, NAVY, ICE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODES_DIR = os.path.join(ROOT, "modes")
OUT = os.path.join(HERE, "modes-video")

W, H = 1920, 1080
FPS = 30
XF = 0.8                     # crossfade between sections (video and audio)
TITLE_LEN, ON_LEN, OFF_LEN, OUTRO_LEN = 5.0, 25.0, 9.0, 12.0

# Site palette (index.html dark theme)
GOLD_STRONG = (240, 185, 92)
GOLD_MID = (224, 163, 68)
INDIGO = (139, 152, 232)
INDIGO_STRONG = (163, 175, 242)
DARK = (28, 23, 15)
LINE = (58, 70, 104)

# Same order, formulas and wording as the website's wheel. `lag` = seconds the
# "with guitar" take runs behind the backing-only take (measured).
MODES = [
    ("Lydian", "1 2 3 #4 5 6 7", "C D E F# G A B", 0.049,
     "Major, but the raised 4th makes it float — bright, open, a little unresolved."),
    ("Ionian", "1 2 3 4 5 6 7", "C D E F G A B", 0.052,
     "The major scale itself. The baseline everything else is measured against."),
    ("Mixolydian", "1 2 3 4 5 6 b7", "C D E F G A Bb", 0.017,
     "Major with a flatted 7th — the sound under a lot of classic rock and blues-rock."),
    ("Dorian", "1 2 b3 4 5 6 b7", "C D Eb F G A Bb", 0.096,
     "Minor with a natural 6th — a minor-key groove that never quite turns sad."),
    ("Aeolian", "1 2 b3 4 5 b6 b7", "C D Eb F G Ab Bb", 0.018,
     "The natural minor scale. Straightforwardly melancholy, no surprises."),
    ("Phrygian", "1 b2 b3 4 5 b6 b7", "C Db Eb F G Ab Bb", 0.315,
     "Minor with a flatted 2nd — dark, tense, a half-step away from home."),
    ("Locrian", "1 b2 b3 4 b5 b6 b7", "C Db Eb F Gb Ab Bb", 0.005,
     "Even the 5th is flat. Unstable by design — rarely a home key, mostly a passing color."),
]

# Each Intro Track opens with ~3s of count-in; start on the band's downbeat (measured).
DOWNBEAT = {"Lydian": 3.27, "Ionian": 3.27, "Mixolydian": 3.06, "Dorian": 3.40,
            "Aeolian": 3.03, "Phrygian": 3.22, "Locrian": 3.34}


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def wedge_colors(n):
    anchors = [GOLD_STRONG, GOLD_MID, INDIGO, INDIGO_STRONG]
    out = []
    for i in range(n):
        pos = i / (n - 1) * (len(anchors) - 1)
        k = min(int(pos), len(anchors) - 2)
        out.append(lerp(anchors[k], anchors[k + 1], pos - k))
    return out


COLORS = wedge_colors(len(MODES))


def draw_wheel(active=None, all_lit=False):
    """The mode wheel as an RGBA layer, drawn at 2x and downsampled for smooth edges.
    `active` is one mode index, or a tuple of them to light several at once."""
    lit_set = set(active) if isinstance(active, (tuple, list, set)) else {active}
    S = 2
    size = 860 * S
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size / 2
    r_out, r_in = 380 * S, 140 * S
    n = len(MODES)
    for i, (name, *_rest) in enumerate(MODES):
        a0, a1 = 360 / n * i - 90, 360 / n * (i + 1) - 90
        mid = math.radians((a0 + a1) / 2)
        lit = all_lit or active is None or i in lit_set
        col = COLORS[i] if lit else lerp(COLORS[i], NAVY, 0.62)
        if active is None and not all_lit:
            col = lerp(COLORS[i], NAVY, 0.25)
        off = 18 * S if i in lit_set else 0
        ox, oy = off * math.cos(mid), off * math.sin(mid)
        pts = []
        for k in range(41):
            a = math.radians(a0 + (a1 - a0) * k / 40)
            pts.append((c + ox + r_out * math.cos(a), c + oy + r_out * math.sin(a)))
        for k in range(40, -1, -1):
            a = math.radians(a0 + (a1 - a0) * k / 40)
            pts.append((c + ox + r_in * math.cos(a), c + oy + r_in * math.sin(a)))
        d.polygon(pts, fill=col + (255,))
        d.line(pts + [pts[0]], fill=(10, 14, 30, 255), width=5 * S)
        lr = (r_out + r_in) / 2
        lx, ly = c + ox + lr * math.cos(mid), c + oy + lr * math.sin(mid)
        f = mono(23 * S, semibold=True)
        txt_col = DARK if lit else lerp(COLORS[i], NAVY, 0.15)
        d.text((lx, ly), name.upper(), font=f, fill=txt_col + (255,), anchor="mm")
    d.text((c, c - 34 * S), "KEY OF", font=mono(22 * S, semibold=True), fill=ICE + (255,), anchor="mm")
    d.text((c, c + 30 * S), "C", font=fraunces(110 * S, 600), fill=TEXT + (255,), anchor="mm")
    return layer.resize((860, 860), Image.LANCZOS)


def base_frame(active=None, all_lit=False, footer=True):
    im = stage_canvas(size=(W, H)).convert("RGBA")
    im.alpha_composite(draw_wheel(active, all_lit), (140, 105))
    d = ImageDraw.Draw(im)
    if footer:
        d.text((80, 1030), "ROB REICH  ·  MASTER THE MODES", font=mono(22, True), fill=ICE, anchor="ls")
        d.text((1840, 1030), "robreichguitar.com", font=mono(26, True), fill=GOLD, anchor="rs")
    return im, d


PX = 1090      # right panel left edge
PW = 740       # right panel width


def wrap(d, x, y, text, font, fill, width_px, leading):
    words, line, lines = text.split(), "", []
    for w in words:
        test = (line + " " + w).strip()
        if d.textlength(test, font=font) > width_px and line:
            lines.append(line)
            line = w
        else:
            line = test
    lines.append(line)
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)
    return y + len(lines) * leading


def mode_frame(i, guitar_on):
    name, formula, notes, _lag, feel = MODES[i]
    im, d = base_frame(active=i)
    d.text((PX, 150), f"MODE {i + 1} OF 7  ·  BRIGHTEST TO DARKEST", font=mono(24, True), fill=GOLD)
    d.text((PX - 4, 190), name, font=fraunces(118, 600), fill=TEXT)
    # interval chips: degrees that differ from the major scale are filled gold
    degs, nts = formula.split(), notes.split()
    cw, gap, cy = 92, 14, 375
    for k, (deg, note) in enumerate(zip(degs, nts)):
        x = PX + k * (cw + gap)
        altered = deg[0] in "#b"
        if altered:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, outline=LINE, width=2)
        d.text((x + cw / 2, cy + cw / 2 + 2), deg, font=fraunces(44, 600),
               fill=DARK if altered else TEXT, anchor="mm")
        d.text((x + cw / 2, cy + cw + 34), note, font=mono(26, True),
               fill=GOLD_STRONG if altered else ICE, anchor="mm")
    wrap(d, PX, 560, feel, fraunces(36, 400), ICE, PW, 50)
    # Rob's guitar switch, as on the website
    sy = 752
    d.text((PX, sy + 26), "ROB'S GUITAR", font=mono(22, True), fill=ICE, anchor="lm")
    x = PX + 210
    for label, on in (("ON", True), ("OFF · YOUR TURN", False)):
        f = mono(24, True)
        tw = d.textlength(label, font=f)
        box = (x, sy, x + tw + 44, sy + 52)
        if on == guitar_on:
            d.rounded_rectangle(box, 26, fill=GOLD_STRONG)
            d.text((x + 22, sy + 27), label, font=f, fill=DARK, anchor="lm")
        else:
            d.rounded_rectangle(box, 26, outline=LINE, width=2)
            d.text((x + 22, sy + 27), label, font=f, fill=TEXT, anchor="lm")
        x = box[2] + 14
    # progress-bar track (the moving fill is drawn by ffmpeg)
    d.rounded_rectangle((PX, 978, PX + PW, 982), 2, fill=LINE)
    return im


def title_frame():
    im, d = base_frame()
    d.text((PX, 230), "MASTER THE MODES", font=mono(26, True), fill=GOLD)
    d.text((PX - 4, 275), "Hear the", font=fraunces(110, 600), fill=TEXT)
    d.text((PX - 4, 395), "7 Modes", font=fraunces(110, 600), fill=TEXT)
    d.text((PX, 560), "Brightest to darkest  ·  all in the key of C", font=mono(26, True), fill=GOLD)
    wrap(d, PX, 640, "Rob Reich plays each mode. Then his guitar drops out, and it's your turn.",
         fraunces(36, 400), ICE, PW, 50)
    d.rounded_rectangle((PX, 978, PX + PW, 982), 2, fill=LINE)
    return im


def outro_frame():
    im, d = base_frame(all_lit=True, footer=False)
    d.text((PX, 250), "TRY IT YOURSELF", font=mono(26, True), fill=GOLD)
    d.text((PX - 4, 300), "Play along", font=fraunces(104, 600), fill=TEXT)
    d.text((PX - 4, 415), "with Rob", font=fraunces(104, 600), fill=TEXT)
    d.text((PX, 600), "robreichguitar.com", font=mono(56, True), fill=GOLD_STRONG)
    wrap(d, PX, 700, "Click a mode on the wheel, hear Rob play it, then switch his guitar off and take the solo.",
         fraunces(34, 400), ICE, PW, 48)
    d.text((PX, 900), "Master the Modes by Rob Reich & Doug Glener", font=mono(22, True), fill=ICE)
    return im


def thumbnail():
    im = stage_canvas(size=(W, H)).convert("RGBA")
    im.alpha_composite(draw_wheel(all_lit=True).resize((940, 940), Image.LANCZOS), (40, 70))
    d = ImageDraw.Draw(im)
    x, max_w = 1050, 820
    size = 200
    while d.textlength("7 Modes", font=fraunces(size, 700)) > max_w:
        size -= 4
    d.text((x, 250), "HEAR THE", font=mono(64, True), fill=GOLD)
    d.text((x - 6, 320), "7 Modes", font=fraunces(size, 700), fill=TEXT)
    d.text((x, 600), "Brightest to darkest", font=fraunces(76, 600), fill=ICE)
    d.text((x, 720), "ROB REICH · GUITAR", font=mono(48, True), fill=GOLD_STRONG)
    return im.convert("RGB").resize((1280, 720), Image.LANCZOS)


# ---------------------------------------------------------------- rendering

def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def still_clip(parts, out, progress=True):
    """parts: [(png, seconds)] dissolved into one clip; a gold progress bar fills over it."""
    inputs, fc, total = [], [], sum(d for _, d in parts)
    ext = [d + (0.3 if k < len(parts) - 1 else 0) for k, (_, d) in enumerate(parts)]
    for (png, _), dur in zip(parts, ext):
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", png]
    label, t = "[0:v]", ext[0]
    for k in range(1, len(parts)):
        nxt = f"[x{k}]"
        fc.append(f"{label}[{k}:v]xfade=transition=fade:duration=0.3:offset={t - 0.3:.3f}{nxt}")
        label, t = nxt, t + ext[k] - 0.3
    if progress:
        # a gold strip slides in from the left, clipped to the bar's track
        # (drawbox can't animate its width in this ffmpeg build)
        fc.append(f"{label}format=yuv420p,split[base][s]")
        fc.append(f"[s]crop={PW}:6:{PX}:977[strip]")
        fc.append(f"color=c=0xF0B95C:s={PW}x6:r={FPS}[bar]")
        fc.append(f"[strip][bar]overlay=x='-{PW}+{PW}*t/{total:.3f}':y=0:eval=frame:shortest=1[fill]")
        fc.append(f"[base][fill]overlay={PX}:977[v]")
    else:
        fc.append(f"{label}format=yuv420p[v]")
    run(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-t", f"{total:.3f}",
                  "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "16", out])


def audio_clip(i, out, lead=0.0):
    """Mode i: with-guitar take for ON_LEN (+ lead), then the backing-only take, time-aligned."""
    slug, lag = MODES[i][0].lower(), MODES[i][3]
    st = DOWNBEAT[MODES[i][0]] - 0.05
    on = lead + ON_LEN
    w = os.path.join(MODES_DIR, f"intro-{slug}-with.mp3")
    wo = os.path.join(MODES_DIR, f"intro-{slug}-without.mp3")
    fc = (f"[0:a]atrim=start={st + lag:.3f}:duration={on:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05[a];"
          f"[1:a]atrim=start={st + on:.3f}:duration={OFF_LEN:.3f},asetpts=PTS-STARTPTS[b];"
          f"[a][b]concat=n=2:v=0:a=1[o]")
    run(["-i", w, "-i", wo, "-filter_complex", fc, "-map", "[o]", "-ar", "48000", "-ac", "2", out])


def main(stills_only=False):
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, ".work")
    os.makedirs(tmp, exist_ok=True)
    P = lambda name: os.path.join(tmp, name)

    title_frame().convert("RGB").save(P("title.png"))
    outro_frame().convert("RGB").save(P("outro.png"))
    for i in range(len(MODES)):
        mode_frame(i, True).convert("RGB").save(P(f"m{i}_on.png"))
        mode_frame(i, False).convert("RGB").save(P(f"m{i}_off.png"))
    thumbnail().save(os.path.join(OUT, "thumbnail.jpg"), quality=92)
    if stills_only:
        print("stills in", tmp)
        return

    # sections: (video parts, audio builder)
    vclips, aclips, lengths = [], [], []
    for i in range(len(MODES)):
        lead = TITLE_LEN if i == 0 else 0.0
        parts = ([(P("title.png"), TITLE_LEN)] if i == 0 else []) + \
                [(P(f"m{i}_on.png"), ON_LEN), (P(f"m{i}_off.png"), OFF_LEN)]
        v, a = P(f"s{i}.mp4"), P(f"s{i}.wav")
        still_clip(parts, v)
        audio_clip(i, a, lead)
        vclips.append(v); aclips.append(a); lengths.append(lead + ON_LEN + OFF_LEN)
        print("section", MODES[i][0])
    v, a = P("outro.mp4"), P("outro.wav")
    still_clip([(P("outro.png"), OUTRO_LEN)], v, progress=False)
    # outro music: the end of the Ionian take -- back home to plain major, fading out
    ion = os.path.join(MODES_DIR, "intro-ionian-with.mp3")
    run(["-sseof", f"-{OUTRO_LEN:.3f}", "-i", ion, "-af",
         f"afade=t=out:st={OUTRO_LEN - 3:.3f}:d=3", "-ar", "48000", "-ac", "2", a])
    vclips.append(v); aclips.append(a); lengths.append(OUTRO_LEN)

    # join with crossfades; chapter starts sit in the middle of each fade
    inputs = []
    for c in vclips:
        inputs += ["-i", c]
    for c in aclips:
        inputs += ["-i", c]
    n = len(vclips)
    fc, vl, al, t, starts = [], "[0:v]", f"[{n}:a]", lengths[0], [0.0]
    for k in range(1, n):
        fc.append(f"{vl}[{k}:v]xfade=transition=fade:duration={XF}:offset={t - XF:.3f}[v{k}]")
        fc.append(f"{al}[{n + k}:a]acrossfade=d={XF}:c1=tri:c2=tri[a{k}]")
        starts.append(t - XF / 2)
        vl, al, t = f"[v{k}]", f"[a{k}]", t + lengths[k] - XF
    outro_start = starts[-1]
    # a live waveform of the music under the mode panel (not on the outro card)
    fc.append(f"{al}asplit[aout][awave]")
    # drawn white, then used as the mask for a gold layer (showwaves' own
    # colors come out green once alpha is involved)
    fc.append(f"[awave]showwaves=s={PW}x90:mode=cline:rate={FPS}:scale=sqrt:colors=white,format=gray[wmask]")
    fc.append(f"color=c=0xF0B95C:s={PW}x90:r={FPS}:d={t:.3f},format=rgba[wgold]")
    fc.append("[wgold][wmask]alphamerge,colorchannelmixer=aa=0.85[wave]")
    fc.append(f"{vl}[wave]overlay={PX}:858:enable='lt(t,{outro_start:.2f})'[vout]")
    final = os.path.join(OUT, "hear-the-7-modes.mp4")
    run(inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
                  "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                  "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])

    fmt = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"
    names = ["Intro & Lydian"] + [m[0] for m in MODES[1:]] + ["Try it yourself"]
    chapters = [f"0:00 Intro"] + [f"{fmt(TITLE_LEN)} Lydian"] + \
               [f"{fmt(s)} {nm}" for s, nm in zip(starts[1:], names[1:])]
    with open(os.path.join(OUT, "chapters.txt"), "w") as f:
        f.write("\n".join(chapters) + "\n")
    print("\n".join(chapters))
    print("done:", final, f"({t:.1f}s)")


if __name__ == "__main__":
    main(stills_only="--stills" in sys.argv)

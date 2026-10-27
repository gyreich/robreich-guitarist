"""
Challenge series: one vertical Short per mode. Rob plays the mode's Intro
Track for 8s, then his guitar drops out and the viewer gets 45s to solo over
the backing track, with a countdown, then a closing card. Its own look (wine
background, gold MODES CHALLENGE banner, question headline) so a challenge
never reads as one of the Master Class lesson Shorts.

    python3 modes_challenge_shorts.py            # all seven
    python3 modes_challenge_shorts.py Dorian     # just one
"""
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFilter

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, ICE
from modes_wheel_video import (MODES, DOWNBEAT, GOLD_STRONG, DARK, LINE, OUT, MODES_DIR,
                               draw_wheel, run, FPS)
from modes_wheel_short import draw_chips

W, H = 1080, 1920
ROB_LEN, TURN_LEN, END_LEN, FADE = 8.0, 45.0, 4.0, 3.0   # music fades under the end card
SERIES = os.path.join(OUT, "challenge")


def guitar_switch(d, on, y):
    f = mono(26, True)
    items = [("ROB'S GUITAR", None), ("ON", True), ("OFF · YOUR TURN", False)]
    widths = [d.textlength(t, font=f) + (0 if s is None else 44) for t, s in items]
    x = (W - (sum(widths) + 2 * 14 + 10)) / 2
    for (label, state), w in zip(items, widths):
        if state is None:
            d.text((x, y + 27), label, font=f, fill=ICE, anchor="lm")
            x += w + 24
            continue
        box = (x, y, x + w, y + 54)
        if state == on:
            d.rounded_rectangle(box, 27, fill=GOLD_STRONG)
            d.text((x + 22, y + 28), label, font=f, fill=DARK, anchor="lm")
        else:
            d.rounded_rectangle(box, 27, outline=LINE, width=2)
            d.text((x + 22, y + 28), label, font=f, fill=TEXT, anchor="lm")
        x += w + 14


WINE_DEEP, WINE, WINE_GLOW = (20, 6, 14), (48, 12, 28), (128, 34, 58)


def challenge_canvas(seed=11):
    """Like stage_canvas, but deep wine instead of navy: the challenge series' own color."""
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), WINE_DEEP)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(255 * max(0.0, 1 - abs(y - H * 0.42) / (H * 0.62)) ** 1.6))
    im = Image.composite(Image.new("RGB", (W, H), WINE), im, grad.resize((W, H)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.05, -H * 0.12, W * 0.95, H * 0.42), fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    im = Image.composite(Image.new("RGB", (W, H), WINE_GLOW), im, glow)
    bokeh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bokeh)
    for _ in range(46):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(4, 22)
        col = rnd.choice([(255, 150, 170), (230, 120, 140), GOLD, GOLD])
        bd.ellipse((x - r, y - r, x + r, y + r), fill=col + (rnd.randint(25, 60),))
    im = im.convert("RGBA")
    im.alpha_composite(bokeh.filter(ImageFilter.GaussianBlur(6)))
    return im


def banner(d):
    f = mono(34, True)
    label = "MODES  CHALLENGE"
    w = d.textlength(label, font=f) + 80
    d.rounded_rectangle(((W - w) / 2, 70, (W + w) / 2, 136), 33, fill=GOLD_STRONG)
    d.text((W / 2, 104), label, font=f, fill=DARK, anchor="mm")


def frame(i, your_turn, left=None):
    """`left`: seconds remaining in the viewer's turn, shown as a countdown."""
    name = MODES[i][0]
    im = challenge_canvas()
    d = ImageDraw.Draw(im)
    banner(d)
    if your_turn:
        d.text((W / 2, 230), "Your turn!", font=fraunces(104, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 322), f"SOLO OVER C {name.upper()}  ·  0:{left:02d}", font=mono(42, True),
               fill=GOLD, anchor="mm")
    else:
        d.text((W / 2, 205), "Can you solo over", font=fraunces(64, 500), fill=TEXT, anchor="mm")
        d.text((W / 2, 292), f"C {name}?", font=fraunces(104, 600), fill=TEXT, anchor="mm")
    wheel = draw_wheel(i).resize((740, 740), Image.LANCZOS)
    im.alpha_composite(wheel, ((W - 740) // 2, 390))
    label = "USE THESE NOTES" if your_turn else "ROB PLAYS IT FIRST"
    d.text((W / 2, 1195), label, font=mono(32, True), fill=GOLD, anchor="mm")
    draw_chips(d, i, 1245)
    guitar_switch(d, not your_turn, 1445)
    return im.convert("RGB")


def end_frame(i):
    name = MODES[i][0]
    im = challenge_canvas()
    d = ImageDraw.Draw(im)
    banner(d)
    d.text((W / 2, 250), "Nice playing!", font=fraunces(104, 600), fill=TEXT, anchor="mm")
    wheel = draw_wheel(i).resize((560, 560), Image.LANCZOS)
    im.alpha_composite(wheel, ((W - 560) // 2, 380))
    d.text((W / 2, 1040), f"Want the full C {name} track,", font=fraunces(54, 600), fill=TEXT, anchor="mm")
    d.text((W / 2, 1112), "with Rob's guitar on or off?", font=fraunces(54, 600), fill=TEXT, anchor="mm")
    d.text((W / 2, 1200), "Free at robreichguitar.com", font=mono(42, True), fill=GOLD_STRONG, anchor="mm")
    d.text((W / 2, 1265), "TAP ROB'S WEBSITE LINK IN THE CHANNEL PROFILE", font=mono(24, True),
           fill=ICE, anchor="mm")
    return im.convert("RGB")


def render(i):
    name, _f, _n, lag, _feel = MODES[i]
    slug = name.lower()
    tmp = os.path.join(SERIES, ".work")
    os.makedirs(tmp, exist_ok=True)
    P = lambda n: os.path.join(tmp, f"{slug}-{n}")
    # stills joined by the concat demuxer: Rob's part, one frame per second of countdown, end card
    frame(i, False).save(P("rob.png"))
    parts = [(P("rob.png"), ROB_LEN)]
    for left in range(int(TURN_LEN), 0, -1):
        png = P(f"turn-{left:02d}.png")
        frame(i, True, left).save(png)
        parts.append((png, 1.0))
    end_frame(i).save(P("end.png"))
    parts.append((P("end.png"), END_LEN))
    total = ROB_LEN + TURN_LEN + END_LEN
    lst = P("frames.txt")
    open(lst, "w").write("".join(f"file '{p}'\nduration {d:.3f}\n" for p, d in parts)
                         + f"file '{parts[-1][0]}'\n")
    run(["-f", "concat", "-safe", "0", "-i", lst, "-vf", f"fps={FPS},format=yuv420p",
         "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "16", P("v.mp4")])

    st = DOWNBEAT[name] - 0.05
    w = os.path.join(MODES_DIR, f"intro-{slug}-with.mp3")
    wo = os.path.join(MODES_DIR, f"intro-{slug}-without.mp3")
    pw = 760
    fc = (f"[1:a]atrim=start={st + lag:.3f}:duration={ROB_LEN:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05[a];"
          f"[2:a]atrim=start={st + ROB_LEN:.3f}:duration={TURN_LEN + END_LEN:.3f},asetpts=PTS-STARTPTS[b];"
          f"[a][b]concat=n=2:v=0:a=1,afade=t=out:st={total - FADE:.3f}:d={FADE},"
          f"aresample=48000,asplit[aout][aw];"
          f"[aw]showwaves=s={pw}x80:mode=cline:rate={FPS}:scale=sqrt:colors=white,format=gray[m];"
          f"color=c=0xF0B95C:s={pw}x80:r={FPS}:d={total:.3f},format=rgba[g];"
          f"[g][m]alphamerge,colorchannelmixer=aa=0.85[wave];"
          f"[0:v][wave]overlay={(W - pw) // 2}:1560:enable='lt(t,{ROB_LEN + TURN_LEN:.3f})'[vout]")
    final = os.path.join(SERIES, f"{i + 1:02d}-{slug}-challenge.mp4")
    run(["-i", P("v.mp4"), "-i", w, "-i", wo, "-filter_complex", fc,
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", final])
    print("done:", final)


if __name__ == "__main__":
    wanted = [a.lower() for a in sys.argv[1:]]
    for i, m in enumerate(MODES):
        if not wanted or m[0].lower() in wanted:
            render(i)

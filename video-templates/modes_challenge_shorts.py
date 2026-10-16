"""
Challenge series: one vertical Short per mode. Rob plays the mode's Intro
Track for 8s, then his guitar drops out and the viewer is invited to solo
over the backing track ("Now it's your turn: solo over C Dorian").

    python3 modes_challenge_shorts.py            # all seven
    python3 modes_challenge_shorts.py Dorian     # just one
"""
import os
import sys
from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, ICE
from modes_wheel_video import (MODES, DOWNBEAT, GOLD_STRONG, DARK, LINE, OUT, MODES_DIR,
                               draw_wheel, still_clip, run, FPS)
from modes_wheel_short import draw_chips

W, H = 1080, 1920
ROB_LEN, TURN_LEN, FADE = 8.0, 17.0, 2.5
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


def frame(i, your_turn):
    name = MODES[i][0]
    im = stage_canvas(size=(W, H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    if your_turn:
        d.text((W / 2, 200), "Now it's your turn:", font=fraunces(84, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 295), f"SOLO OVER C {name.upper()}", font=mono(46, True), fill=GOLD, anchor="mm")
    else:
        d.text((W / 2, 200), f"C {name}", font=fraunces(96, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 295), "ROB PLAYS IT FIRST", font=mono(38, True), fill=GOLD, anchor="mm")
    wheel = draw_wheel(i).resize((780, 780), Image.LANCZOS)
    im.alpha_composite(wheel, ((W - 780) // 2, 360))
    label = "USE THESE NOTES" if your_turn else f"MODE {i + 1} OF 7  ·  BRIGHTEST TO DARKEST"
    d.text((W / 2, 1195), label, font=mono(32, True), fill=GOLD, anchor="mm")
    draw_chips(d, i, 1245)
    guitar_switch(d, not your_turn, 1445)
    return im.convert("RGB")


def render(i):
    name, _f, _n, lag, _feel = MODES[i]
    slug = name.lower()
    tmp = os.path.join(SERIES, ".work")
    os.makedirs(tmp, exist_ok=True)
    P = lambda n: os.path.join(tmp, f"{slug}-{n}")
    frame(i, False).save(P("rob.png"))
    frame(i, True).save(P("turn.png"))
    total = ROB_LEN + TURN_LEN
    still_clip([(P("rob.png"), ROB_LEN), (P("turn.png"), TURN_LEN)], P("v.mp4"), progress=False)

    st = DOWNBEAT[name] - 0.05
    w = os.path.join(MODES_DIR, f"intro-{slug}-with.mp3")
    wo = os.path.join(MODES_DIR, f"intro-{slug}-without.mp3")
    pw = 760
    fc = (f"[1:a]atrim=start={st + lag:.3f}:duration={ROB_LEN:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.05[a];"
          f"[2:a]atrim=start={st + ROB_LEN:.3f}:duration={TURN_LEN:.3f},asetpts=PTS-STARTPTS[b];"
          f"[a][b]concat=n=2:v=0:a=1,afade=t=out:st={total - FADE:.3f}:d={FADE},"
          f"aresample=48000,asplit[aout][aw];"
          f"[aw]showwaves=s={pw}x80:mode=cline:rate={FPS}:scale=sqrt:colors=white,format=gray[m];"
          f"color=c=0xF0B95C:s={pw}x80:r={FPS}:d={total:.3f},format=rgba[g];"
          f"[g][m]alphamerge,colorchannelmixer=aa=0.85[wave];"
          f"[0:v][wave]overlay={(W - pw) // 2}:1560[vout]")
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

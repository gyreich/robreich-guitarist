"""
"Brightest vs. darkest" -- a ~30s vertical YouTube Short from the modes video:
Rob plays C Lydian, then C Locrian, the two ends of the wheel, then a card
pointing to the website link in the channel profile.

    python3 modes_wheel_short.py
"""
import os
from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, ICE
from modes_wheel_video import (MODES, DOWNBEAT, GOLD_STRONG, DARK, LINE, OUT, MODES_DIR,
                               draw_wheel, still_clip, run, FPS)

W, H = 1080, 1920
LYDIAN, LOCRIAN = 0, 6
A_LEN, B_LEN, END_LEN, XA = 14.0, 12.5, 5.5, 0.4    # section lengths, audio crossfade


def frame(active=None, label=None, all_lit=False, end=False):
    im = stage_canvas(size=(W, H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    # hook stays up the whole time (clear of YouTube's top bar)
    d.text((W / 2, 205), "Same key. Same root.", font=fraunces(76, 600), fill=TEXT, anchor="mm")
    d.text((W / 2, 290), "COMPLETELY DIFFERENT MOOD", font=mono(34, True), fill=GOLD, anchor="mm")
    wheel = draw_wheel(active, all_lit).resize((780, 780), Image.LANCZOS)
    im.alpha_composite(wheel, ((W - 780) // 2, 360))
    if end:
        d.text((W / 2, 1230), "Try all 7 yourself", font=fraunces(92, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1330), "robreichguitar.com", font=mono(48, True), fill=GOLD_STRONG, anchor="mm")
        d.text((W / 2, 1405), "TAP ROB'S WEBSITE LINK", font=mono(30, True), fill=ICE, anchor="mm")
        d.text((W / 2, 1450), "IN THE CHANNEL PROFILE", font=mono(30, True), fill=ICE, anchor="mm")
        return im.convert("RGB")
    d.text((W / 2, 1185), label, font=mono(34, True), fill=GOLD, anchor="mm")
    d.text((W / 2, 1265), MODES[active][0], font=fraunces(104, 600), fill=TEXT, anchor="mm")
    draw_chips(d, active, 1340)
    return im.convert("RGB")


def draw_chips(d, i, cy):
    """The mode's seven scale degrees, centered; ones that differ from major are gold."""
    _name, formula, notes, *_ = MODES[i]
    degs, nts = formula.split(), notes.split()
    cw, gap = 116, 20
    x0 = (W - (7 * cw + 6 * gap)) // 2
    for k, (deg, note) in enumerate(zip(degs, nts)):
        x = x0 + k * (cw + gap)
        altered = deg[0] in "#b"
        if altered:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 14, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 14, outline=LINE, width=2)
        d.text((x + cw / 2, cy + cw / 2 + 2), deg, font=fraunces(54, 600),
               fill=DARK if altered else TEXT, anchor="mm")
        d.text((x + cw / 2, cy + cw + 40), note, font=mono(30, True),
               fill=GOLD_STRONG if altered else ICE, anchor="mm")


def with_take(i, dur, out, fade_out=0.0):
    name, *_rest = MODES[i]
    lag = MODES[i][3]
    src = os.path.join(MODES_DIR, f"intro-{name.lower()}-with.mp3")
    af = f"atrim=start={DOWNBEAT[name] - 0.05 + lag:.3f}:duration={dur:.3f},asetpts=PTS-STARTPTS"
    if fade_out:
        af += f",afade=t=out:st={dur - fade_out:.3f}:d={fade_out:.3f}"
    run(["-i", src, "-af", af, "-ar", "48000", "-ac", "2", out])


def main():
    tmp = os.path.join(OUT, ".work-short")
    os.makedirs(tmp, exist_ok=True)
    P = lambda n: os.path.join(tmp, n)
    frame(LYDIAN, "BRIGHTEST").save(P("a.png"))
    frame(LOCRIAN, "DARKEST").save(P("b.png"))
    frame(all_lit=True, end=True).save(P("end.png"))

    total = A_LEN + B_LEN + END_LEN
    still_clip([(P("a.png"), A_LEN), (P("b.png"), B_LEN), (P("end.png"), END_LEN)],
               P("v.mp4"), progress=False)
    with_take(LYDIAN, A_LEN + XA / 2, P("a.wav"))
    with_take(LOCRIAN, total - A_LEN + XA / 2, P("b.wav"), fade_out=3.0)

    pw = 760
    fc = (f"[1:a][2:a]acrossfade=d={XA}:c1=tri:c2=tri,asplit[aout][aw];"
          f"[aw]showwaves=s={pw}x80:mode=cline:rate={FPS}:scale=sqrt:colors=white,format=gray[m];"
          f"color=c=0xF0B95C:s={pw}x80:r={FPS}:d={total:.3f},format=rgba[g];"
          f"[g][m]alphamerge,colorchannelmixer=aa=0.85[wave];"
          f"[0:v][wave]overlay={(W - pw) // 2}:1560:enable='lt(t,{A_LEN + B_LEN:.2f})'[vout]")
    final = os.path.join(OUT, "brightest-vs-darkest-short.mp4")
    run(["-i", P("v.mp4"), "-i", P("a.wav"), "-i", P("b.wav"), "-filter_complex", fc,
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
    print("done:", final, f"({total:.1f}s)")


if __name__ == "__main__":
    main()

"""
Master Class excerpt as a vertical Short: "All 7 modes from one note"
(Master Class 0:36-3:08). Rob introduces the idea and plays each mode from C;
the wheel lights the mode he is playing, captions follow his words, and it
ends on his question "what makes them different?" -- answered in the full
Master Class.

Captions and timings come from an automatic transcript, corrected by hand.

    python3 master_class_clip.py
"""
import os
from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, ICE
from modes_wheel_video import MODES, GOLD_STRONG, DARK, LINE, OUT, ROOT, draw_wheel, run, FPS

W, H = 1080, 1920
SRC = os.path.join(ROOT, "Master Class with Rob.mp3")
START, END, TAIL = 36.0, 188.15, 2.5      # seconds in the Master Class; end card after
IDX = {m[0]: i for i, m in enumerate(MODES)}

# (start, end, text) in Master Class time; gaps are Rob playing
CAPTIONS = [
    (36.1, 37.9, "So I'm going to play a little bit of"),
    (37.9, 40.0, "what a mode sounds like, just in general."),
    (46.3, 47.4, "That's the Ionian mode,"),
    (47.4, 48.6, "the first mode in our system."),
    (53.0, 56.2, "In the Master the Modes system,"),
    (58.1, 60.4, "we discovered that the best way"),
    (60.4, 61.4, "to work on the modes"),
    (61.4, 63.2, "is to play them all from one note."),
    (63.2, 66.7, "And the note we've chosen is C,"),
    (66.7, 68.3, "the key of C being the easiest"),
    (68.3, 72.0, "and most clear key to understand,"),
    (72.0, 74.7, "because there are no sharps, no flats."),
    (74.7, 76.8, "So as we go through the modes,"),
    (76.8, 80.1, "you can much more easily see"),
    (80.1, 81.3, "the differences between them,"),
    (81.3, 82.4, "and you can hear the difference"),
    (82.4, 84.2, "much more clearly."),
    (84.2, 85.3, "So that was C Ionian,"),
    (85.3, 86.6, "and here's C Dorian."),
    (94.1, 95.7, "So now I'll play C Ionian"),
    (95.7, 96.7, "and then C Dorian."),
    (96.7, 99.8, "Just listen for the clear difference"),
    (99.8, 100.8, "between the two."),
    (112.7, 114.0, "So you can easily hear"),
    (114.0, 115.3, "there's a distinctive difference"),
    (115.3, 116.9, "between the two modes."),
    (116.9, 119.7, "So here's the third mode"),
    (119.7, 121.7, "in any major key."),
    (121.7, 123.3, "The third mode would be Phrygian."),
    (123.3, 124.6, "Sounds like this:"),
    (133.3, 135.9, "The fourth mode will be C Lydian."),
    (135.9, 136.9, "Sounds like this:"),
    (145.7, 147.7, "This mode is called Mixolydian."),
    (147.7, 148.7, "Sounds like this:"),
    (155.6, 157.2, "The sixth mode is called Aeolian,"),
    (157.2, 158.4, "and sounds like this:"),
    (165.1, 166.3, "Finally, the seventh mode"),
    (166.3, 167.4, "is called Locrian."),
    (167.4, 168.6, "That sounds like this:"),
    (176.6, 178.2, "So we're playing all the modes"),
    (178.2, 179.5, "from the same starting note,"),
    (179.5, 181.7, "the note being C."),
    (181.7, 183.6, "In this way we can very easily"),
    (183.6, 185.9, "hear the differences between the modes."),
    (185.9, 186.9, "But the question is:"),
    (186.9, END + TAIL, "what makes them different?"),
]

# which wedge(s) are lit, in Master Class time
WHEEL = [
    (START, 39.4, None),
    (39.4, 48.6, "Ionian"),
    (48.6, 84.2, None),
    (84.2, 85.3, "Ionian"),
    (85.3, 94.1, "Dorian"),
    (94.1, 112.7, ("Ionian", "Dorian")),
    (112.7, 121.7, None),
    (121.7, 133.3, "Phrygian"),
    (133.3, 145.7, "Lydian"),
    (145.7, 155.6, "Mixolydian"),
    (155.6, 165.1, "Aeolian"),
    (165.1, 176.6, "Locrian"),
    (176.6, END + TAIL, "all"),
]


def chips(d, i, cy, cw=100, gap=16):
    _name, formula, notes, *_ = MODES[i]
    x0 = (W - (7 * cw + 6 * gap)) // 2
    for k, (deg, note) in enumerate(zip(formula.split(), notes.split())):
        x = x0 + k * (cw + gap)
        altered = deg[0] in "#b"
        if altered:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, outline=LINE, width=2)
        d.text((x + cw / 2, cy + cw / 2 + 2), deg, font=fraunces(46, 600),
               fill=DARK if altered else TEXT, anchor="mm")
        d.text((x + cw / 2, cy + cw + 34), note, font=mono(27, True),
               fill=GOLD_STRONG if altered else ICE, anchor="mm")


def wrap_center(d, y, text, font, fill, max_w, leading):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if d.textlength(t, font=font) > max_w and line:
            lines.append(line)
            line = w
        else:
            line = t
    lines.append(line)
    if len(lines) == 2:   # balance two-line captions instead of leaving one word alone
        best = min(range(1, len(words)),
                   key=lambda k: abs(d.textlength(" ".join(words[:k]), font=font)
                                     - d.textlength(" ".join(words[k:]), font=font)))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    for k, ln in enumerate(lines):
        d.text((W / 2, y + k * leading), ln, font=font, fill=fill, anchor="mm")


def frame(wheel_state, caption, end_card):
    im = stage_canvas(size=(W, H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((W / 2, 190), "All 7 modes from one note", font=fraunces(70, 600), fill=TEXT, anchor="mm")
    d.text((W / 2, 268), "ROB REICH  ·  MASTER CLASS", font=mono(32, True), fill=GOLD, anchor="mm")

    if wheel_state == "all":
        wheel = draw_wheel(all_lit=True)
    elif wheel_state is None:
        wheel = draw_wheel()
    elif isinstance(wheel_state, tuple):
        wheel = draw_wheel(tuple(IDX[m] for m in wheel_state))
    else:
        wheel = draw_wheel(IDX[wheel_state])
    im.alpha_composite(wheel.resize((660, 660), Image.LANCZOS), ((W - 660) // 2, 320))

    if end_card:
        d.text((W / 2, 1060), "Hear the answer in the", font=fraunces(52, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1130), "full Master Class, free", font=fraunces(52, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1215), "robreichguitar.com", font=mono(44, True), fill=GOLD_STRONG, anchor="mm")
        d.text((W / 2, 1280), "TAP ROB'S WEBSITE LINK IN THE CHANNEL PROFILE", font=mono(24, True),
               fill=ICE, anchor="mm")
    elif isinstance(wheel_state, str) and wheel_state != "all":
        d.text((W / 2, 1020), f"C {wheel_state.upper()}", font=mono(34, True), fill=GOLD, anchor="mm")
        chips(d, IDX[wheel_state], 1060)
    elif isinstance(wheel_state, tuple):
        d.text((W / 2, 1080), "C IONIAN  vs  C DORIAN", font=mono(40, True), fill=GOLD, anchor="mm")
        d.text((W / 2, 1140), "only the 3rd and 7th change", font=fraunces(40, 400), fill=ICE, anchor="mm")
    else:
        d.text((W / 2, 1090), "Every mode starts on C", font=fraunces(48, 400), fill=ICE, anchor="mm")

    if caption:
        # caption panel, kept above YouTube's bottom overlay
        d.rounded_rectangle((60, 1330, W - 60, 1490), 24, fill=(8, 12, 28, 215))
        wrap_center(d, 1380 if len(caption) > 34 else 1410, caption, fraunces(50, 600), TEXT, W - 180, 62)
    return im.convert("RGB")


def state_at(t):
    wheel = next(s for a, b, s in WHEEL if a <= t < b)
    cap = next((c for a, b, c in CAPTIONS if a <= t < b), None)
    return wheel, cap, t >= END


def main():
    tmp = os.path.join(OUT, ".work-mc")
    os.makedirs(tmp, exist_ok=True)
    bounds = sorted({START, END, END + TAIL} |
                    {x for a, b, _ in CAPTIONS for x in (a, b)} |
                    {x for a, b, _ in WHEEL for x in (a, b)})
    bounds = [b for b in bounds if START <= b <= END + TAIL]
    lines, cache = [], {}
    for a, b in zip(bounds, bounds[1:]):
        if b - a < 1 / FPS:
            continue
        key = state_at((a + b) / 2)
        if key not in cache:
            png = os.path.join(tmp, f"f{len(cache):03d}.png")
            frame(*key).save(png)
            cache[key] = png
        lines.append(f"file '{cache[key]}'\nduration {b - a:.3f}")
    lines.append(f"file '{cache[key]}'")      # concat demuxer needs the last file repeated
    lst = os.path.join(tmp, "frames.txt")
    open(lst, "w").write("\n".join(lines) + "\n")

    dur = END - START
    final = os.path.join(OUT, "all-7-modes-from-one-note-short.mp4")
    af = (f"atrim=start={START}:end={END},asetpts=PTS-STARTPTS,"
          f"afade=t=in:d=0.2,afade=t=out:st={dur - 0.25:.3f}:d=0.25,apad=pad_dur={TAIL}")
    run(["-f", "concat", "-safe", "0", "-i", lst, "-i", SRC,
         "-filter_complex", f"[0:v]fps={FPS},format=yuv420p[v];[1:a]{af}[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{dur + TAIL:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000", "-movflags", "+faststart", final])
    print(f"done: {final} ({dur + TAIL:.1f}s, {len(cache)} distinct frames)")


if __name__ == "__main__":
    main()

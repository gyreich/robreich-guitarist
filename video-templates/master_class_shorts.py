"""
More vertical Shorts from the Master Class, in the style of master_class_clip.py
(wheel, captions following Rob's words, end card pointing to the free course):

  why-modes-sound-alike   7:28-8:27   the usual way (C Ionian, D Dorian, E Phrygian)
                                      vs. all three from C
  mechanical-vs-musical   37:35-38:31 + 40:03-40:14
                                      C Ionian played like an exercise, then phrased;
                                      ends on "music is not patterns, music is expression"
  aeolian-king-of-metal   58:52-59:10, 58:34-58:52, 59:12-59:58
                                      reordered so it opens on the "king mode" line

A Short can be several pieces of the Master Class joined in order; all times
below are Master Class time. Captions are from an automatic transcript,
corrected by hand.

    python3 master_class_shorts.py                  # all three
    python3 master_class_shorts.py mechanical-vs-musical
"""
import os
import subprocess
import sys
from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import stage_canvas, ICE
from modes_wheel_video import MODES, GOLD_STRONG, LINE, OUT, ROOT, draw_wheel, run, FPS
from master_class_clip import chips, wrap_center, W, H

SRC = os.path.join(ROOT, "Master Class with Rob.mp3")
TAIL = 3.0                # end card after the last piece
GAP = 0.35                # silence between pieces
IDX = {m[0]: i for i, m in enumerate(MODES)}
C_MAJOR = "C D E F G A B".split()

# Panels under the wheel:
#   ("chips", mode)          C-based formula and notes, altered degrees in gold
#   ("row", k, label)        the C major notes started from degree k (the usual way)
#   ("tag", big, small)      a label and a line under it
SHORTS = {
    "why-modes-sound-alike": {
        "title": "Why the modes sound alike",
        "pieces": [(448.6, 506.9)],
        "captions": [
            (448.6, 450.5, "Typically, the way modes are taught"),
            (450.6, 453.9, "is that you play them within a scale."),
            (454.0, 456.6, "So you would play a C major scale."),
            (456.7, 458.4, "You'd play C Ionian,"),
            (458.5, 461.8, "then D Dorian, E Phrygian,"),
            (461.9, 464.9, "F Lydian, and so on."),
            (465.0, 466.6, "And it's a fine way to learn"),
            (466.7, 468.4, "the concept of modal theory."),
            (468.5, 470.6, "The problem is that each mode"),
            (470.7, 472.6, "winds up sounding very similar"),
            (472.6, 473.3, "to the last one,"),
            (473.3, 475.7, "because they're all derived from the same key."),
            (475.8, 478.4, "So for example, I'm going to play C Ionian,"),
            (478.4, 481.2, "D Dorian and E Phrygian."),
            (490.2, 491.7, "Now I'm going to play all three"),
            (491.7, 493.5, "starting from the same note: C."),
            (502.5, 504.8, "To my ear, the differences are much more apparent"),
            (504.8, 506.9, "when we start the modes from the same note."),
        ],
        "states": [
            (448.6, 456.7, None, ("tag", "THE USUAL WAY", "modes taught inside one scale")),
            (456.7, 458.5, "Ionian", ("row", 0, "C IONIAN")),
            (458.5, 460.6, "Dorian", ("row", 1, "D DORIAN")),
            (460.6, 461.9, "Phrygian", ("row", 2, "E PHRYGIAN")),
            (461.9, 465.0, "Lydian", ("row", 3, "F LYDIAN")),
            (465.0, 481.5, None, ("tag", "THE USUAL WAY", "the same 7 notes every time")),
            (481.5, 484.3, "Ionian", ("row", 0, "C IONIAN")),
            (484.3, 487.0, "Dorian", ("row", 1, "D DORIAN")),
            (487.0, 490.2, "Phrygian", ("row", 2, "E PHRYGIAN")),
            (490.2, 493.5, None, ("tag", "THE FIX", "every mode starts on C")),
            (493.5, 496.15, "Ionian", ("chips", "Ionian")),
            (496.15, 499.0, "Dorian", ("chips", "Dorian")),
            (499.0, 502.5, "Phrygian", ("chips", "Phrygian")),
            (502.5, 506.9, ("Ionian", "Dorian", "Phrygian"),
             ("tag", "THE FIX", "now you can hear the difference")),
        ],
        "end": ("Learn all 7 modes from C", "in Rob's free course"),
    },
    "mechanical-vs-musical": {
        "title": "Mechanical vs. musical",
        "pieces": [(2255.3, 2310.7), (2403.32, 2414.0)],
        "captions": [
            (2255.4, 2257.7, "If we look at C Ionian,"),
            (2257.7, 2259.2, "and I play C Ionian"),
            (2259.2, 2261.4, "in sort of a mechanical way,"),
            (2261.5, 2263.4, "forward and backwards, like this:"),
            (2268.8, 2271.8, "That's a scale played forward and then backwards."),
            (2271.9, 2274.1, "Now here's the same scale"),
            (2274.2, 2277.3, "in what I would call a phrasing kind of way,"),
            (2277.4, 2280.3, "which is being a little bit more creative with it,"),
            (2280.4, 2282.6, "and trying to be more expressive with it."),
            (2290.7, 2292.3, "So even that already sounds"),
            (2292.3, 2294.2, "much more musical than the first example."),
            (2294.7, 2296.6, "So as we're playing and exploring the modes"),
            (2296.6, 2300.1, "and exploring the patterns we talked about,"),
            (2300.1, 2302.9, "we want to keep this idea of being musical"),
            (2303.0, 2304.9, "in our minds at all times,"),
            (2305.0, 2307.9, "so we can steer clear of playing in a way"),
            (2308.0, 2310.7, "that's more mechanical and sort of unmusical."),
            (2403.32, 2405.2, "Music is not patterns."),
            (2405.3, 2407.2, "Music is expression."),
            (2407.3, 2409.3, "If you play the pattern the right way,"),
            (2409.4, 2410.8, "it will sound like music."),
            (2410.9, 2412.6, "If you play it the wrong way,"),
            (2412.7, 2414.0, "it won't sound like music."),
        ],
        "states": [
            (2255.3, 2263.9, "Ionian", ("chips", "Ionian")),
            (2263.9, 2268.6, "Ionian", ("tag", "MECHANICAL", "up and back, like an exercise")),
            (2268.6, 2282.8, "Ionian", ("chips", "Ionian")),
            (2282.8, 2290.7, "Ionian", ("tag", "MUSICAL", "the same notes, phrased")),
            (2290.7, 2310.7, "Ionian", ("tag", "SAME 7 NOTES", "the difference is the phrasing")),
            (2403.32, 2414.0, "all", ("tag", "ROB REICH", "on practicing the modes")),
        ],
        "end": ("Practice the modes musically", "in Rob's free course"),
    },
    "aeolian-king-of-metal": {
        "title": "The king mode of metal",
        "pieces": [(3532.1, 3549.5), (3513.84, 3532.05), (3552.1, 3597.8)],
        "captions": [
            (3532.1, 3534.0, "Aeolian mode is like"),
            (3534.1, 3536.9, "the king mode for a lot of heavy metal music"),
            (3537.0, 3537.9, "and heavy rock music."),
            (3538.0, 3540.9, "They favor the Aeolian mode, for whatever reason."),
            (3541.0, 3543.9, "It has sort of a dark minor kind of sound."),
            (3544.0, 3545.6, "A lot of classical music"),
            (3545.7, 3549.5, "also has overtones of the Aeolian mode."),
            (3513.84, 3516.1, "Dorian has a major 6th degree."),
            (3516.2, 3518.4, "Aeolian has a minor 6th degree."),
            (3518.5, 3520.1, "It would be spelled in the key of C:"),
            (3520.2, 3525.6, "C, D, E-flat, F, G, A-flat, B-flat,"),
            (3525.7, 3526.6, "sounding like this:"),
            (3552.1, 3554.8, "As we play the Aeolian mode,"),
            (3554.9, 3556.0, "we can play a chord progression"),
            (3556.0, 3557.7, "that highlights that 6th degree."),
            (3557.8, 3560.0, "So if we play C minor,"),
            (3561.4, 3563.4, "and then an A-flat major chord,"),
            (3565.0, 3567.3, "A-flat is the 6th degree"),
            (3567.4, 3569.4, "of C Aeolian."),
            (3570.0, 3573.4, "One, two, three, four, five, six:"),
            (3573.5, 3575.2, "A-flat. C up to A-flat."),
            (3577.2, 3578.6, "So this kind of chord progression"),
            (3578.6, 3580.0, "will highlight the Aeolian sound."),
        ],
        "states": [
            (3532.1, 3549.5, "Aeolian", ("tag", "C AEOLIAN", "the natural minor scale")),
            (3513.84, 3518.5, "Aeolian", ("tag", "DORIAN vs AEOLIAN", "only the 6th degree changes")),
            (3518.5, 3532.05, "Aeolian", ("chips", "Aeolian")),
            (3552.1, 3557.8, "Aeolian", ("chips", "Aeolian")),
            (3557.8, 3561.4, "Aeolian", ("tag", "C MINOR", "the home chord")),
            (3561.4, 3597.8, "Aeolian", ("tag", "C MINOR  TO  Ab MAJOR", "Ab is the b6 of C Aeolian")),
        ],
        "end": ("Learn all 7 modes", "in Rob's free course"),
    },
    "mechanical-vs-musical-2": {
        "title": "Mechanical vs. musical, Part 2",
        "pieces": [(2414.05, 2450.15), (2459.4, 2468.7)],
        "captions": [
            (2414.1, 2416.2, "So here's an example of how to play"),
            (2416.3, 2418.2, "the groups of three"),
            (2418.3, 2420.8, "in an unmusical, sort of mechanical way:"),
            (2426.8, 2429.7, "Here it is more in an expressive way,"),
            (2429.8, 2430.8, "thinking of phrasing."),
            (2435.6, 2437.4, "Adding techniques,"),
            (2437.5, 2441.3, "which are sort of very guitar-like techniques."),
            (2441.4, 2444.0, "Sometimes I'll play in a staccato way,"),
            (2444.0, 2447.1, "sometimes I play more hammer-ons and pull-offs."),
            (2447.2, 2450.15, "But again, this is to express what I'm playing."),
            (2459.4, 2462.6, "We also want to grow in the area of expression,"),
            (2463.3, 2465.2, "because when you think of your favorite players,"),
            (2465.3, 2468.7, "they're all very great at expressing the music they're playing."),
        ],
        "states": [
            (2414.05, 2421.3, "Ionian", ("tag", "GROUPS OF THREE", "C D E  ·  D E F  ·  E F G  ...")),
            (2421.3, 2426.6, "Ionian", ("tag", "MECHANICAL", "even, like an exercise")),
            (2426.6, 2430.8, "Ionian", ("tag", "GROUPS OF THREE", "same pattern, same notes")),
            (2430.8, 2435.4, "Ionian", ("tag", "EXPRESSIVE", "phrased, with feel")),
            (2435.4, 2450.15, "Ionian", ("tag", "GUITAR TECHNIQUES", "staccato  ·  hammer-ons  ·  pull-offs")),
            (2459.4, 2468.7, "all", ("tag", "EXPRESSION", "what great players share")),
        ],
        "end": ("Practice the modes musically", "in Rob's free course"),
    },
    "mechanical-vs-musical-3": {
        "title": "Classroom vs. the real thing",
        "pieces": [(2483.45, 2509.6), (2546.65, 2555.6)],
        "captions": [
            (2483.5, 2486.1, "As guitar players, the first thing we typically learn"),
            (2486.1, 2488.5, "is what's known as the minor pentatonic scale,"),
            (2488.5, 2489.8, "which I'll play from C:"),
            (2494.7, 2496.9, "Now that sounds a little bit like a classroom."),
            (2497.0, 2498.3, "But if you hear something like this:"),
            (2502.0, 2505.1, "That's C minor pentatonic played in a way"),
            (2505.2, 2509.6, "you've probably heard many times by players over the years."),
            (2546.7, 2547.4, "Here's C Dorian,"),
            (2550.3, 2551.4, "here's C minor pentatonic:"),
            (2553.7, 2555.6, "the same thing, with just a little less color."),
        ],
        "states": [
            (2483.45, 2489.8, None, ("notes", (("C", 0), ("Eb", 1), ("F", 0), ("G", 0), ("Bb", 1)),
                                      "C MINOR PENTATONIC", "five notes")),
            (2489.8, 2494.7, None, ("tag", "CLASSROOM", "up and down, by the book")),
            (2494.7, 2498.3, None, ("notes", (("C", 0), ("Eb", 1), ("F", 0), ("G", 0), ("Bb", 1)),
                                    "C MINOR PENTATONIC", "the same five notes")),
            (2498.3, 2502.0, None, ("tag", "THE REAL THING", "how great players use it")),
            (2502.0, 2509.6, None, ("tag", "SAME FIVE NOTES", "the difference is the phrasing")),
            (2546.65, 2550.3, "Dorian", ("chips", "Dorian")),
            (2550.3, 2555.6, "Dorian", ("notes", (("C", 0), ("Eb", 1), ("F", 0), ("G", 0), ("Bb", 1)),
                                         "C MINOR PENTATONIC", "Dorian, minus two notes")),
        ],
        "end": ("Play the modes musically", "in Rob's free course"),
    },
    "major-vs-minor": {
        "title": "Major vs. minor",
        "pieces": [(185.6, 280.6)],      # opens on Rob's question; starts in the silence before "But"
        "captions": [
            (185.6, 188.4, "But the question is: what makes them different?"),
            (188.4, 192.2, "And the answer is what you call intervals."),
            (192.3, 194.6, "Intervals are distances between notes."),
            (195.9, 198.4, "On a guitar, if we play from C to D,"),
            (198.5, 200.3, "it's called the interval of a major second."),
            (204.6, 207.6, "So if we play from C to D-flat,"),
            (210.7, 212.1, "that's what's called a minor second."),
            (212.8, 216.8, "When you change the intervals in any given scale or mode,"),
            (216.8, 219.1, "you change the color of it."),
            (219.2, 222.0, "So for example, the first three notes of C Ionian"),
            (222.0, 227.1, "are C, D and E."),
            (227.2, 229.3, "When we play C Dorian, the first three notes"),
            (229.4, 234.0, "are C, D and E-flat."),
            (234.3, 236.0, "That's a key difference right off the bat."),
            (236.6, 240.9, "The third degree of that mode is E-flat,"),
            (241.1, 244.4, "where the third degree of Ionian is E natural."),
            (245.7, 248.8, "In terms of intervals, the E is called the major third,"),
            (250.9, 252.7, "and it gives you the color of a major sound."),
            (252.8, 254.2, "So if I play a C major chord,"),
            (255.9, 257.5, "the first three notes of C Ionian,"),
            (259.4, 260.5, "it works."),
            (260.6, 263.2, "Now if I play the first three notes of C Dorian,"),
            (263.2, 266.0, "C, D, E-flat,"),
            (266.7, 268.1, "and play a C minor chord:"),
            (272.9, 274.7, "All we've done is change one note."),
            (275.3, 277.1, "But this is what happens in the modes themselves:"),
            (277.2, 280.6, "each mode has a different interval construction."),
        ],
        "states": [
            (185.6, 188.4, "all", ("tag", "WHAT MAKES THEM DIFFERENT?", "")),
            (188.4, 195.9, None, ("tag", "INTERVALS", "the distance between two notes")),
            (195.9, 204.6, "Ionian", ("notes", (("C", 0), ("D", 0),), "MAJOR 2ND", "two frets apart")),
            (204.6, 212.8, None, ("notes", (("C", 0), ("Db", 1),), "MINOR 2ND", "one fret apart")),
            (212.8, 219.2, None, ("tag", "CHANGE AN INTERVAL", "and you change the color")),
            (219.2, 227.2, "Ionian", ("notes", (("C", 0), ("D", 0), ("E", 0),), "C IONIAN", "first three notes")),
            (227.2, 234.3, "Dorian", ("notes", (("C", 0), ("D", 0), ("Eb", 1),), "C DORIAN", "first three notes")),
            (234.3, 245.7, ("Ionian", "Dorian"), ("notes", (("E", 0), ("Eb", 1),), "THE 3RD", "E natural vs. E-flat")),
            (245.7, 252.8, "Ionian", ("notes", (("C", 0), ("E", 0),), "MAJOR 3RD", "the color of a major sound")),
            (252.8, 260.6, "Ionian", ("notes", (("C", 0), ("E", 0), ("G", 0),), "C MAJOR CHORD", "major 3rd: E")),
            (260.6, 272.9, "Dorian", ("notes", (("C", 0), ("Eb", 1), ("G", 0),), "C MINOR CHORD", "minor 3rd: E-flat")),
            (272.9, 280.6, ("Ionian", "Dorian"), ("tag", "ONE NOTE", "turns major into minor")),
        ],
        "end": ("Hear how all 7 modes differ", "in Rob's free course"),
    },
}


def notes(d, items, label, sub, cy=1070, cw=130, gap=26):
    """A few big note chips; altered (flat) notes in gold."""
    d.text((W / 2, cy - 50), label, font=mono(38, True), fill=GOLD, anchor="mm")
    x0 = (W - (len(items) * cw + (len(items) - 1) * gap)) // 2
    for j, (n, alt) in enumerate(items):
        x = x0 + j * (cw + gap)
        if alt:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 16, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 16, outline=LINE, width=3)
        d.text((x + cw / 2, cy + cw / 2 + 2), n.replace("b", "\u266d") if False else n, font=fraunces(62, 600),
               fill=(10, 14, 30) if alt else TEXT, anchor="mm")
    d.text((W / 2, cy + cw + 46), sub, font=fraunces(38, 400), fill=ICE, anchor="mm")


def row(d, k, label, cy, cw=100, gap=16):
    """The C major scale started from degree k: the usual way of teaching modes."""
    notes = C_MAJOR[k:] + C_MAJOR[:k]
    d.text((W / 2, cy - 40), label, font=mono(34, True), fill=GOLD, anchor="mm")
    x0 = (W - (7 * cw + 6 * gap)) // 2
    for j, note in enumerate(notes):
        x = x0 + j * (cw + gap)
        first = j == 0
        if first:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, cy, x + cw, cy + cw), 12, outline=LINE, width=2)
        d.text((x + cw / 2, cy + cw / 2 + 2), note, font=fraunces(46, 600),
               fill=(10, 14, 30) if first else TEXT, anchor="mm")
    d.text((W / 2, cy + cw + 40), "same notes as C major", font=fraunces(36, 400), fill=ICE, anchor="mm")


def frame(spec, wheel_state, panel, caption, end_card):
    im = stage_canvas(size=(W, H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    title = spec["title"]
    size = 70
    while d.textlength(title, font=fraunces(size, 600)) > W - 120:
        size -= 2
    d.text((W / 2, 190), title, font=fraunces(size, 600), fill=TEXT, anchor="mm")
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
        line1, line2 = spec["end"]
        d.text((W / 2, 1060), line1, font=fraunces(52, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1130), line2, font=fraunces(52, 600), fill=TEXT, anchor="mm")
        d.text((W / 2, 1215), "robreichguitar.com", font=mono(44, True), fill=GOLD_STRONG, anchor="mm")
        d.text((W / 2, 1280), "TAP ROB'S WEBSITE LINK IN THE CHANNEL PROFILE", font=mono(24, True),
               fill=ICE, anchor="mm")
    elif panel[0] == "chips":
        d.text((W / 2, 1020), f"C {panel[1].upper()}", font=mono(34, True), fill=GOLD, anchor="mm")
        chips(d, IDX[panel[1]], 1060)
    elif panel[0] == "row":
        row(d, panel[1], panel[2], 1080)
    elif panel[0] == "notes":
        notes(d, panel[1], panel[2], panel[3])
    else:
        d.text((W / 2, 1080), panel[1], font=mono(40, True), fill=GOLD, anchor="mm")
        d.text((W / 2, 1140), panel[2], font=fraunces(40, 400), fill=ICE, anchor="mm")

    if caption:
        # caption panel, kept above YouTube's bottom overlay
        d.rounded_rectangle((60, 1330, W - 60, 1490), 24, fill=(8, 12, 28, 215))
        wrap_center(d, 1380 if len(caption) > 34 else 1410, caption, fraunces(50, 600), TEXT, W - 180, 62)
    return im.convert("RGB")


def build(key):
    spec = SHORTS[key]
    tmp = os.path.join(OUT, f".work-{key}")
    os.makedirs(tmp, exist_ok=True)

    # output timeline: (output start, source start, source end) per piece
    timeline, t = [], 0.0
    for a, b in spec["pieces"]:
        timeline.append((t, a, b))
        t += b - a + GAP
    music_end = t - GAP
    total = music_end + TAIL

    def state_at(src_t):
        wheel, panel = next((w, p) for a, b, w, p in spec["states"] if a <= src_t < b)
        cap = next((c for a, b, c in spec["captions"] if a <= src_t < b), None)
        return wheel, panel, cap, False

    # frame changes in output time
    segs = []
    for out0, a, b in timeline:
        cuts = sorted({a, b} | {x for s, e, *_ in spec["captions"] + spec["states"]
                                for x in (s, e) if a < x < b})
        for s, e in zip(cuts, cuts[1:]):
            if e - s >= 1 / FPS:
                segs.append((out0 + s - a, out0 + e - a, state_at((s + e) / 2)))
        segs.append((out0 + b - a, out0 + b - a + GAP, segs[-1][2]))   # hold through the gap
    segs[-1] = (segs[-1][0], music_end, segs[-1][2])
    segs.append((music_end, total, (None, None, None, True)))

    lines, cache = [], {}
    for s, e, key_state in segs:
        if e - s < 1 / FPS:
            continue
        if key_state not in cache:
            png = os.path.join(tmp, f"f{len(cache):03d}.png")
            frame(spec, *key_state).save(png)
            cache[key_state] = png
        lines.append(f"file '{cache[key_state]}'\nduration {e - s:.3f}")
    lines.append(f"file '{cache[key_state]}'")      # concat demuxer needs the last file repeated
    lst = os.path.join(tmp, "frames.txt")
    open(lst, "w").write("\n".join(lines) + "\n")

    # audio: each piece trimmed with short fades, joined with a little silence
    parts, labels = [], []
    for i, (_o, a, b) in enumerate(timeline):
        d = b - a
        pad = GAP if i < len(timeline) - 1 else TAIL
        fade_out = 0.6 if i == len(timeline) - 1 else 0.25
        parts.append(f"[1:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.08,afade=t=out:st={d - fade_out:.3f}:d={fade_out},"
                     f"apad=pad_dur={pad}[p{i}]")
        labels.append(f"[p{i}]")
    af = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=0:a=1[a]"

    final = os.path.join(OUT, f"{key}-short.mp4")
    run(["-f", "concat", "-safe", "0", "-i", lst, "-i", SRC,
         "-filter_complex", f"[0:v]fps={FPS},format=yuv420p[v];{af}",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000", "-movflags", "+faststart", final])
    print(f"done: {final} ({total:.1f}s, {len(cache)} distinct frames)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or SHORTS):
        build(k)

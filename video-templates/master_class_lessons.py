"""
Long-form (16:9) lessons from the Master Class, in the look of "Hear the 7 Modes":
wheel at left, a panel at right showing what Rob is explaining, a live waveform,
chapters, and a closing card pointing to the free course (right half kept clear
for YouTube's end-screen elements).

Teasers by design (agreed with Gail): complete lessons of a few minutes each; the
full Master Class, jam tracks and guide stay in the free course.

    python3 master_class_lessons.py modes-in-10            # one lesson
    python3 master_class_lessons.py                         # all
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

from brand import fraunces, mono, TEXT, GOLD
from dream_dancing_shorts import ICE, stage_canvas
from modes_wheel_video import (MODES, DOWNBEAT, GOLD_STRONG, DARK, LINE, OUT, ROOT, MODES_DIR,
                               base_frame, wrap, run, FPS, W, H, PX, PW)
from master_class_clip import WHEEL as ALL7_WHEEL
from master_class_shorts import SHORTS

MC = os.path.join(ROOT, "Master Class with Rob.mp3")
IDX = {m[0]: i for i, m in enumerate(MODES)}
C_MAJOR = "C D E F G A B".split()
GAP, END_LEN = 0.35, 15.0
PENT = (("C", 1), ("Eb", 1), ("F", 1), ("G", 1), ("Bb", 1))


# ------------------------------------------------------------------ panels

def chips_row(d, items, y, cw=92, gap=14):
    """items: [(top, bottom, gold)]"""
    for k, (top, bottom, gold) in enumerate(items):
        x = PX + k * (cw + gap)
        if gold:
            d.rounded_rectangle((x, y, x + cw, y + cw), 12, fill=GOLD_STRONG)
        else:
            d.rounded_rectangle((x, y, x + cw, y + cw), 12, outline=LINE, width=2)
        d.text((x + cw / 2, y + cw / 2 + 2), top, font=fraunces(42 if len(top) < 3 else 34, 600),
               fill=DARK if gold else TEXT, anchor="mm")
        if bottom:
            d.text((x + cw / 2, y + cw + 32), bottom, font=mono(25, True),
                   fill=GOLD_STRONG if gold else ICE, anchor="mm")


def mode_items(name):
    _n, formula, notes, *_ = MODES[IDX[name]]
    return [(deg, note, deg[0] in "#b") for deg, note in zip(formula.split(), notes.split())]


def panel(d, p):
    kind = p[0]
    if kind == "title":
        _, kicker, l1, l2, sub, body = p
        d.text((PX, 200), kicker, font=mono(26, True), fill=GOLD)
        d.text((PX - 4, 245), l1, font=fraunces(104, 600), fill=TEXT)
        d.text((PX - 4, 360), l2, font=fraunces(104, 600), fill=TEXT)
        d.text((PX, 520), sub, font=mono(26, True), fill=GOLD)
        wrap(d, PX, 590, body, fraunces(36, 400), ICE, PW, 50)
    elif kind == "mode":
        _, name, kicker, body = p
        d.text((PX, 170), kicker, font=mono(24, True), fill=GOLD)
        d.text((PX - 4, 210), f"C {name}", font=fraunces(100, 600), fill=TEXT)
        chips_row(d, mode_items(name), 370)
        if body:
            wrap(d, PX, 560, body, fraunces(36, 400), ICE, PW, 50)
    elif kind == "compare":
        _, a, b, body = p
        for k, name in enumerate((a, b)):
            y = 170 + k * 250
            d.text((PX, y), f"C {name.upper()}", font=mono(26, True), fill=GOLD)
            chips_row(d, mode_items(name), y + 45)
        wrap(d, PX, 700, body, fraunces(36, 400), ICE, PW, 50)
    elif kind == "notes":
        _, items, label, body = p
        d.text((PX, 200), label, font=mono(26, True), fill=GOLD)
        big = len(items) <= 5
        chips_row(d, [(n, "", g) for n, g in items], 260, cw=112 if big else 92, gap=18 if big else 14)
        if body:
            wrap(d, PX, 430, body, fraunces(38, 400), ICE, PW, 52)
    elif kind == "row":
        _, k, label = p
        d.text((PX, 200), "THE USUAL WAY", font=mono(26, True), fill=GOLD)
        d.text((PX - 4, 240), label, font=fraunces(84, 600), fill=TEXT)
        notes = C_MAJOR[k:] + C_MAJOR[:k]
        chips_row(d, [(n, "", j == 0) for j, n in enumerate(notes)], 380)
        wrap(d, PX, 540, "The same seven notes as C major, just a new starting note.",
             fraunces(36, 400), ICE, PW, 50)
    elif kind == "tag":
        _, label, big, body = p
        d.text((PX, 230), label, font=mono(26, True), fill=GOLD)
        y = wrap(d, PX - 4, 275, big, fraunces(70, 600), TEXT, PW, 84)
        if body:
            wrap(d, PX, y + 30, body, fraunces(36, 400), ICE, PW, 50)
    elif kind == "turn":
        _, name, on = p
        d.text((PX, 170), "PLAY ALONG" if on else "YOUR TURN", font=mono(26, True), fill=GOLD)
        d.text((PX - 4, 210), f"C {name}", font=fraunces(100, 600), fill=TEXT)
        chips_row(d, mode_items(name), 370)
        wrap(d, PX, 560, "Rob plays it first..." if on else "Rob's guitar is out. Solo over the band using these notes.",
             fraunces(36, 400), ICE, PW, 50)
        sy = 740
        d.text((PX, sy + 26), "ROB'S GUITAR", font=mono(22, True), fill=ICE, anchor="lm")
        x = PX + 210
        for lab, state in (("ON", True), ("OFF · YOUR TURN", False)):
            f = mono(24, True)
            box = (x, sy, x + d.textlength(lab, font=f) + 44, sy + 52)
            if state == on:
                d.rounded_rectangle(box, 26, fill=GOLD_STRONG)
                d.text((x + 22, sy + 27), lab, font=f, fill=DARK, anchor="lm")
            else:
                d.rounded_rectangle(box, 26, outline=LINE, width=2)
                d.text((x + 22, sy + 27), lab, font=f, fill=TEXT, anchor="lm")
            x = box[2] + 14


def frame(wheel, p):
    if wheel == "all":
        im, d = base_frame(all_lit=True)
    elif wheel is None:
        im, d = base_frame()
    elif isinstance(wheel, tuple):
        im, d = base_frame(active=tuple(IDX[m] for m in wheel))
    else:
        im, d = base_frame(active=IDX[wheel])
    panel(d, p)
    return im.convert("RGB")


def end_frame(lines):
    im = stage_canvas(size=(W, H)).convert("RGBA")
    d = ImageDraw.Draw(im)
    x = 120
    d.text((x, 250), "MASTER THE MODES", font=mono(28, True), fill=GOLD)
    y = 300
    for ln in lines:
        d.text((x - 4, y), ln, font=fraunces(84, 600), fill=TEXT)
        y += 104
    d.text((x, y + 40), "Free at robreichguitar.com", font=mono(44, True), fill=GOLD_STRONG)
    wrap(d, x, y + 130, "The full Master Class with Rob, all 14 backing tracks with his guitar on or off, "
         "and the illustrated guide.", fraunces(34, 400), ICE, 820, 48)
    d.text((x, 1000), "Master the Modes by Rob Reich & Doug Glener", font=mono(22, True), fill=ICE)
    return im.convert("RGB")


# ------------------------------------------------------------------ lessons

def from_shorts(key, lo=None, hi=None):
    """Reuse a Short's (start, end, wheel, panel) states, adapted to the wide panels."""
    out = []
    for a, b, w, p in SHORTS[key]["states"]:
        if lo is not None and b <= lo or hi is not None and a >= hi:
            continue
        a, b = max(a, lo or a), min(b, hi or b)
        if p[0] == "tag":
            p = ("tag", p[1], p[2].capitalize() if p[2] else p[1].capitalize(), "")
        elif p[0] == "chips":
            p = ("mode", p[1], f"C {p[1].upper()}", "")
        elif p[0] == "notes":
            p = ("notes", p[1], p[2], p[3])
        elif p[0] == "row":
            p = ("row", p[1], p[2].title())
        out.append((a, b, w, p))
    return out


def all7_states():
    """0:36-3:08: Rob plays all seven modes from C (wheel timings from the Short)."""
    out = []
    for a, b, w in ALL7_WHEEL:
        if w is None:
            p = ("tag", "ONE STARTING NOTE", "Every mode from C", "No sharps, no flats, so the differences stand out.")
        elif w == "all":
            p = ("tag", "ALL SEVEN", "Same starting note: C", "")
        elif isinstance(w, tuple):
            p = ("compare", w[0], w[1], "Only the 3rd and the 7th change.")
        else:
            p = ("mode", w, "LISTEN", "")
        out.append((max(a, 36.1), min(b, 185.6), w, p))
    return [s for s in out if s[1] > s[0]]


LESSONS = {
    "modes-in-10": {
        "title": "The 7 Modes Explained",
        "pieces": [(MC, 0.0, 506.9)],
        "states": [[(0.0, 36.1, None, ("title", "MASTER THE MODES", "The 7 Modes", "Explained",
                                         "WITH ROB REICH",
                                         "Why the modes confuse so many players, and a simpler way to hear them."))]
                   + all7_states()
                   + from_shorts("major-vs-minor", 185.6, 280.6)
                   + [(280.6, 302.0, None, ("tag", "THE FORMULA", "Learn every mode in any key",
                                            "Look at the formula, not the note names.")),
                      (302.0, 340.6, "Ionian", ("mode", "Ionian", "THE FORMULA", "No alterations at all.")),
                      (340.6, 368.5, "Dorian", ("mode", "Dorian", "THE FORMULA", "Flat 3rd, flat 7th.")),
                      (368.5, 385.0, ("Ionian", "Dorian"), ("compare", "Ionian", "Dorian",
                                                            "Two notes, a world of difference in color.")),
                      (385.0, 396.1, None, ("tag", "WITH CHORDS", "Chord first, then the mode",
                                            "C major + C Ionian, then C minor + C Dorian.")),
                      (396.1, 404.3, "Ionian", ("mode", "Ionian", "C MAJOR CHORD + C IONIAN", "")),
                      (404.3, 413.0, "Dorian", ("mode", "Dorian", "C MINOR CHORD + C DORIAN", "")),
                      (413.0, 434.4, "Locrian", ("mode", "Locrian", "Cm7b5 CHORD + C LOCRIAN",
                                                 "The other extreme.")),
                      (434.4, 448.6, "all", ("tag", "THE KEY DISCOVERY", "Play every mode from one note",
                                             "So you can really hear the difference."))]
                   + from_shorts("why-modes-sound-alike")],
        "chapters": [(0, 0.0, "Welcome"), (0, 36.1, "What a mode sounds like"),
                     (0, 53.0, "Why play every mode from C"), (0, 84.2, "C Ionian vs. C Dorian"),
                     (0, 116.9, "Phrygian, Lydian, Mixolydian, Aeolian, Locrian"),
                     (0, 185.6, "What makes them different: intervals"),
                     (0, 245.7, "Major vs. minor: one note"), (0, 282.8, "The formula for each mode"),
                     (0, 385.0, "Hearing the difference with chords"),
                     (0, 448.6, "Why modes usually sound alike (and the fix)")],
        "end_lines": ["Get the full", "Master Class, free"],
        "end_music": "ionian",
        "out": "lesson-the-7-modes-explained.mp4",
    },
    "dorian": {
        "title": "How to Play Over C Dorian",
        "pieces": [("TITLE", 0.0, 5.0), (MC, 340.6, 414.2), (MC, 1904.3, 1927.4),
                   (MC, 3299.8, 3332.0), (MC, 812.0, 852.4), (MC, 2510.4, 2555.6), ("PLAYALONG", 0.0, 52.0)],
        "states": [
            [(0.0, 5.0, "Dorian", ("title", "MASTER THE MODES", "How to Play", "Over C Dorian",
                                   "WITH ROB REICH", "The formula, the color notes, the chord, two practice "
                                   "patterns, and a play-along."))],
            [(340.6, 368.5, "Dorian", ("mode", "Dorian", "THE FORMULA", "Minor 3rd, flat 7th. The 6th stays natural.")),
             (368.5, 385.0, ("Ionian", "Dorian"), ("compare", "Ionian", "Dorian",
                                                   "Only the 3rd and the 7th change.")),
             (385.0, 396.1, None, ("tag", "WITH CHORDS", "Chord first, then the mode",
                                   "C major + C Ionian, then C minor + C Dorian.")),
             (396.1, 404.3, "Ionian", ("mode", "Ionian", "C MAJOR CHORD + C IONIAN", "")),
             (404.3, 414.2, "Dorian", ("mode", "Dorian", "C MINOR CHORD + C DORIAN", ""))],
            [(1904.3, 1919.8, "Dorian", ("mode", "Dorian", "THE COLOR NOTES",
                                         "Flat 3rd, natural 6th, flat 7th: that's what gives Dorian its color.")),
             (1919.8, 1927.4, ("Dorian", "Aeolian"), ("compare", "Dorian", "Aeolian",
                                                      "Aeolian is the same, except for a flat 6th."))],
            [(3299.8, 3312.5, "Dorian", ("mode", "Dorian", "THE DORIAN CHORD",
                                         "Basically C minor, plus the key note: the major 6th.")),
             (3312.5, 3316.9, "Dorian", ("notes", (("C", 0), ("Eb", 0), ("G", 0), ("A", 1)),
                                         "C MINOR + THE 6TH (A)", "Count up six: C D Eb F G A.")),
             (3316.9, 3332.0, "Dorian", ("notes", (("C", 0), ("Eb", 0), ("G", 0), ("A", 1)),
                                         "THE SOUND OF DORIAN", "C minor with the major 6th in it."))],
            [(812.0, 829.4, "Dorian", ("tag", "PRACTICE PATTERN", "Groups of three in C Dorian",
                                       "C D Eb  ·  D Eb F  ·  Eb F G  ...")),
             (829.4, 841.7, "Dorian", ("mode", "Dorian", "THREE-NOTE PATTERN", "Forward, then backwards.")),
             (841.7, 852.4, "Dorian", ("mode", "Dorian", "FOUR-NOTE PATTERN", "Same idea, four notes."))],
            [(2510.4, 2523.0, None, ("notes", PENT, "C MINOR PENTATONIC", "Five notes: the first scale most "
                                                                           "guitarists learn.")),
             (2523.0, 2546.7, "Dorian", ("notes", (("C", 1), ("D", 0), ("Eb", 1), ("F", 1), ("G", 1), ("A", 0),
                                                   ("Bb", 1)), "C DORIAN CONTAINS IT",
                                         "Gold: the five pentatonic notes inside C Dorian.")),
             (2546.7, 2550.3, "Dorian", ("mode", "Dorian", "C DORIAN", "")),
             (2550.3, 2555.6, "Dorian", ("notes", PENT, "C MINOR PENTATONIC",
                                         "The same thing, with a little less color."))],
            [(0.0, 12.0, "Dorian", ("turn", "Dorian", True)),
             (12.0, 52.0, "Dorian", ("turn", "Dorian", False))],
        ],
        "chapters": [(1, 340.6, "The Dorian formula"), (1, 385.0, "Hearing it with chords"),
                     (2, 1904.3, "The color notes"), (3, 3299.8, "The Dorian chord"),
                     (4, 812.0, "Practice patterns in C Dorian"), (5, 2510.4, "Dorian and the minor pentatonic"),
                     (6, 0.0, "Play along")],
        "end_lines": ["Jam over the full", "Dorian track, free"],
        "end_music": "dorian",
        "out": "lesson-how-to-play-over-c-dorian.mp4",
    },
}


def mode_take(name, with_len, without_len, out):
    slug, lag = name.lower(), MODES[IDX[name]][3]
    st = DOWNBEAT[name] - 0.05
    w = os.path.join(MODES_DIR, f"intro-{slug}-with.mp3")
    wo = os.path.join(MODES_DIR, f"intro-{slug}-without.mp3")
    parts, fc = [], []
    if with_len:
        fc.append(f"[0:a]atrim=start={st + lag:.3f}:duration={with_len:.3f},asetpts=PTS-STARTPTS[a]")
        parts.append("[a]")
    if without_len:
        fc.append(f"[1:a]atrim=start={st + with_len:.3f}:duration={without_len:.3f},asetpts=PTS-STARTPTS[b]")
        parts.append("[b]")
    fc.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000[o]")
    run(["-i", w, "-i", wo, "-filter_complex", ";".join(fc), "-map", "[o]", "-ac", "2", out])


def build(key):
    L = LESSONS[key]
    tmp = os.path.join(OUT, f".work-{key}")
    os.makedirs(tmp, exist_ok=True)
    dor = "Dorian"
    srcs = {"TITLE": os.path.join(tmp, "title.wav"), "PLAYALONG": os.path.join(tmp, "playalong.wav")}
    if any(p[0] == "TITLE" for p in L["pieces"]):
        mode_take(dor, 5.0, 0, srcs["TITLE"])
    if any(p[0] == "PLAYALONG" for p in L["pieces"]):
        mode_take(dor, 12.0, 40.0, srcs["PLAYALONG"])

    # output timeline per piece
    starts, t = [], 0.0
    for src, a, b in L["pieces"]:
        starts.append(t)
        t += b - a + GAP
    music_end = t - GAP
    total = music_end + END_LEN

    # frames
    segs, cache = [], {}
    states = L["states"] if isinstance(L["states"][0], list) else [L["states"]]
    if len(states) == 1 and len(L["pieces"]) == 1:
        states = [sum(states, [])]
    for k, (src, a, b) in enumerate(L["pieces"]):
        for sa, sb, w, p in sorted(states[k], key=lambda s: s[0]):
            sa, sb = max(sa, a), min(sb, b)
            if sb - sa < 1 / FPS:
                continue
            segs.append((starts[k] + sa - a, starts[k] + sb - a, (w, p)))
        segs.append((starts[k] + b - a, starts[k] + b - a + GAP, segs[-1][2]))
    segs[-1] = (segs[-1][0], music_end, segs[-1][2])
    endp = os.path.join(tmp, "end.png")
    end_frame(L["end_lines"]).save(endp)
    lines = []
    for s, e, st in segs:
        if st not in cache:
            png = os.path.join(tmp, f"f{len(cache):03d}.png")
            frame(*st).save(png)
            cache[st] = png
        lines.append(f"file '{cache[st]}'\nduration {e - s:.3f}")
    lines.append(f"file '{endp}'\nduration {END_LEN:.3f}")
    lines.append(f"file '{endp}'")
    lst = os.path.join(tmp, "frames.txt")
    open(lst, "w").write("\n".join(lines) + "\n")

    # audio: pieces with short fades and gaps, then soft backing under the end card
    inputs, parts = [], []
    files = []
    for k, (src, a, b) in enumerate(L["pieces"]):
        path = srcs.get(src, src)
        if path not in files:
            files.append(path)
        i = files.index(path) + 1
        parts.append(f"[{i}:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,"
                     f"aformat=channel_layouts=stereo,afade=t=in:d=0.08,"
                     f"afade=t=out:st={b - a - 0.2:.3f}:d=0.2,apad=pad_dur={GAP if k < len(L['pieces']) - 1 else 0}[p{k}]")
    endm = os.path.join(tmp, "endmusic.wav")
    mode_take(L["end_music"].capitalize(), 0, END_LEN, endm)
    files.append(endm)
    ei = len(files)
    parts.append(f"[{ei}:a]volume=0.45,afade=t=in:d=1.5,afade=t=out:st={END_LEN - 3:.3f}:d=3[pe]")
    labels = "".join(f"[p{k}]" for k in range(len(L["pieces"]))) + "[pe]"
    for f in files:
        inputs += ["-i", f]
    af = ";".join(parts) + f";{labels}concat=n={len(L['pieces']) + 1}:v=0:a=1,asplit[aout][aw]"
    wave = (f";[aw]showwaves=s={PW}x90:mode=cline:rate={FPS}:scale=sqrt:colors=white,format=gray[wm];"
            f"color=c=0xF0B95C:s={PW}x90:r={FPS}:d={total:.3f},format=rgba[wg];"
            f"[wg][wm]alphamerge,colorchannelmixer=aa=0.8[wave];"
            f"[0:v]fps={FPS},format=yuv420p[base];[base][wave]overlay={PX}:900:enable='lt(t,{music_end:.2f})'[v]")
    final = os.path.join(OUT, L["out"])
    run(["-f", "concat", "-safe", "0", "-i", lst] + inputs +
        ["-filter_complex", af + wave, "-map", "[v]", "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "stillimage", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])

    fmt = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"
    ch = ["0:00 Intro"] if L["chapters"][0][1] != 0.0 or L["chapters"][0][0] != 0 else []
    for k, srct, name in L["chapters"]:
        ch.append(f"{fmt(starts[k] + srct - L['pieces'][k][1])} {name}")
    ch.append(f"{fmt(music_end)} The free course")
    txt = os.path.join(OUT, L["out"].replace(".mp4", "-chapters.txt"))
    open(txt, "w").write("\n".join(ch) + "\n")
    print("\n".join(ch))
    print("done:", final, f"({total:.1f}s)")


if __name__ == "__main__":
    for k in (sys.argv[1:] or LESSONS):
        build(k)

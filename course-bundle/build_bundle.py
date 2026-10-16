"""
Builds the free "Master the Modes" download bundle (the email signup gift).

  Master the Modes/
    Master the Modes - Guide.pdf     original guide + a "Start Here" page + a closing page
    Master Class with Rob.mp3
    1 Intro Trax/   7 modes x (w-gtr, w-out gtr), in the guide's order
    2 Jam Traxs/    7 tunes x (w-gtr, w-out gtr)
  Master the Modes.zip

File names follow the guide's own wording ("Dorian w/gtr" -> "Dorian w-gtr"),
and the MP3 tags are set to Rob Reich / Master the Modes with track numbers.

    python3 build_bundle.py
"""
import os
import shutil
import subprocess
import zipfile

import PyPDF2
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "Master the Modes")
ALBUM, ARTIST = "Master the Modes", "Rob Reich"
SITE, YOUTUBE = "https://robreichguitar.com", "https://www.youtube.com/@RobReichGuitar"

# The guide's order, and each mode's Jam Track (source file stem)
MODES = [
    ("Ionian", "Traveling South"),
    ("Dorian", "Jamming At The Palladium"),
    ("Aeolian", "Ode To Jimi And Jimmy"),
    ("Phrygian", "Marakesh"),
    ("Locrian", "Saturn"),
    ("Lydian", "Manhattan Reggae"),
    ("Mixolydian", "Wah-Wah Man"),
]
SOURCE_OVERRIDES = {  # source files whose names don't follow the pattern
    "Manhattan Reggae (Lydian with guitar).mp3": "Manhattan Reggae (Lydian with guitar) 2.mp3",
}

INK = HexColor("#1C1C1C")
SOFT = HexColor("#555555")
GOLD = HexColor("#B07A2A")
W, H = letter


def tag_copy(src, dst, title, track, total):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src,
                    "-map", "0:a", "-c", "copy", "-map_metadata", "-1",
                    "-metadata", f"title={title}", "-metadata", f"artist={ARTIST}",
                    "-metadata", f"album_artist={ARTIST}", "-metadata", f"album={ALBUM}",
                    "-metadata", f"track={track}/{total}", "-id3v2_version", "3", dst], check=True)


def text_block(c, x, y, lines, size=12, leading=17, color=INK, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


def paragraph(c, x, y, text, width, size=12, leading=16, color=INK, font="Helvetica"):
    """Word-wrapped paragraph; returns the y below it."""
    return text_block(c, x, y, simpleSplit(text, font, size, width), size, leading, color, font)


def link(c, x, y, label, url, size=12):
    c.setFont("Helvetica-Bold", size)
    c.setFillColor(GOLD)
    c.drawString(x, y, label)
    w = c.stringWidth(label, "Helvetica-Bold", size)
    c.linkURL(url, (x, y - 3, x + w, y + size), relative=0)


def heading(c, y, title):
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(INK)
    c.drawString(72, y, title)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(72, y - 12, 160, y - 12)


def start_here_page(path):
    c = canvas.Canvas(path, pagesize=letter)
    heading(c, H - 96, "Start Here")
    y = text_block(c, 72, H - 140, [
        "Welcome to Master the Modes, the ear-first course by Rob Reich and Doug Glener.",
        "Everything is in the key of C, so you hear what each mode itself sounds like.",
    ], size=12.5)
    y -= 14
    c.setFont("Helvetica-Bold", 14); c.setFillColor(INK); c.drawString(72, y, "What's in your folder"); y -= 24
    items = [
        ("This guide", "the modes explained, one page each, plus practice tips."),
        ("Master Class with Rob", "a one-hour audio lesson that walks through the whole idea."),
        ("1 Intro Trax", "a short, simple track for each mode. \"w-gtr\" has Rob playing;"),
        ("", "\"w-out gtr\" is the same track without him, for you to play over."),
        ("2 Jam Traxs", "a full tune for each mode in a real style (funk, reggae, rock,"),
        ("", "fusion), again with and without Rob's guitar."),
    ]
    for name, desc in items:
        if name:
            c.setFont("Helvetica-Bold", 12); c.setFillColor(INK); c.drawString(84, y, name)
        c.setFont("Helvetica", 12); c.setFillColor(SOFT); c.drawString(250, y, desc)
        y -= 18
    y -= 14
    c.setFont("Helvetica-Bold", 14); c.setFillColor(INK); c.drawString(72, y, "How to use it"); y -= 24
    steps = [
        ["Listen to the start of the Master Class. In the first few minutes Rob plays all",
         "seven modes from C, and you hear how different they are."],
        ["Work through the modes in this guide's order. For each one, read its page, listen",
         "to Rob on the Intro Trax (w-gtr), then play along with the w-out gtr version."],
        ["When a mode feels comfortable, move on to its Jam Trax: hear what Rob does",
         "with it, then take your own solo over the version without guitar."],
    ]
    for k, lines in enumerate(steps, 1):
        c.setFont("Helvetica-Bold", 12); c.setFillColor(GOLD); c.drawString(84, y, f"{k}.")
        y = text_block(c, 104, y, lines, size=12, leading=16) - 8
    y -= 6
    c.setFont("Helvetica-Bold", 14); c.setFillColor(INK)
    c.drawString(72, y, "Why the modes are in this order"); y -= 22
    y = paragraph(c, 72, y,
        "The lessons and tracks follow a learning order. Start with the major scale (Ionian). "
        "Dorian flattens its 3rd and 7th, and each minor mode after that flattens one more note: "
        "Aeolian adds a flat 6th, Phrygian a flat 2nd, Locrian a flat 5th. Each step darkens the "
        "sound, so you hear exactly what one altered note does. Lydian (sharp 4th) and Mixolydian "
        "(flat 7th) each change just one note of the major scale.", W - 144) - 6
    y = paragraph(c, 72, y,
        "The charts and the Master Class use the traditional order: Ionian, Dorian, Phrygian, "
        "Lydian, Mixolydian, Aeolian, Locrian.", W - 144) - 12
    y = paragraph(c, 72, y,
        "The tracks are named the way this guide refers to them: \"Dorian w/gtr\" in the text "
        "is the file \"Dorian w-gtr\".", W - 144, size=11, leading=15, color=SOFT) - 14
    c.setFont("Helvetica", 12); c.setFillColor(INK)
    c.drawString(72, y, "Try the interactive mode wheel, with Rob's guitar on or off, at")
    link(c, 72, y - 18, "robreichguitar.com", SITE + "/#woodshed")
    c.showPage(); c.save()


def closing_page(path):
    c = canvas.Canvas(path, pagesize=letter)
    heading(c, H - 96, "Keep Going with Rob")
    y = text_block(c, 72, H - 140, [
        "Rob Reich is a jazz fusion guitarist and composer in the New York area. He teaches",
        "privately, and he played every solo on these tracks live, in one take.",
    ], size=12.5)
    y -= 20
    rows = [
        ("Lessons, gigs and booking", "robreichguitar.com", SITE),
        ("The mode wheel (play along online)", "robreichguitar.com/#woodshed", SITE + "/#woodshed"),
        ("Videos, including the modes challenge series", "youtube.com/@RobReichGuitar", YOUTUBE),
    ]
    for label, shown, url in rows:
        c.setFont("Helvetica-Bold", 12); c.setFillColor(INK); c.drawString(72, y, label)
        link(c, 72, y - 18, shown, url)
        y -= 50
    y -= 6
    text_block(c, 72, y, [
        "You're receiving this because you signed up at robreichguitar.com. Rob sends an",
        "occasional email about new videos, gigs and lesson openings; you can unsubscribe",
        "from any of them in one click.",
    ], size=11, leading=15, color=SOFT)
    c.setFont("Helvetica", 10); c.setFillColor(SOFT)
    c.drawString(72, 72, "Master the Modes by Rob Reich & Doug Glener.")
    c.showPage(); c.save()


def build_guide(dst, tmp):
    start, close = os.path.join(tmp, "start.pdf"), os.path.join(tmp, "close.pdf")
    start_here_page(start)
    closing_page(close)
    orig = PyPDF2.PdfReader(os.path.join(ROOT, "Master the Modes.pdf"))
    w = PyPDF2.PdfWriter()
    w.add_page(orig.pages[0])                                   # cover
    w.add_page(PyPDF2.PdfReader(start).pages[0])                # Start Here
    for p in orig.pages[1:]:
        w.add_page(p)
    w.add_page(PyPDF2.PdfReader(close).pages[0])                # Keep Going with Rob
    w.add_metadata({"/Title": "Master the Modes", "/Author": "Rob Reich & Doug Glener"})
    with open(dst, "wb") as f:
        w.write(f)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    intro, jam = os.path.join(OUT, "1 Intro Trax"), os.path.join(OUT, "2 Jam Traxs")
    for d in (intro, jam):
        os.makedirs(d)
    tmp = os.path.join(HERE, ".work")
    os.makedirs(tmp, exist_ok=True)

    build_guide(os.path.join(OUT, "Master the Modes - Guide.pdf"), tmp)
    total = 1 + 2 * len(MODES) * 2
    tag_copy(os.path.join(ROOT, "Master Class with Rob.mp3"),
             os.path.join(OUT, "Master Class with Rob.mp3"), "Master Class with Rob", 1, total)
    track = 2
    for k, (mode, _tune) in enumerate(MODES, 1):
        for src_suffix, name_suffix in (("with guitar", "w-gtr"), ("without guitar", "w-out gtr")):
            title = f"{mode} {name_suffix}"
            tag_copy(os.path.join(ROOT, f"IntroTrack ({mode} {src_suffix}).mp3"),
                     os.path.join(intro, f"{k} {title}.mp3"), f"Intro Trax: {title}", track, total)
            track += 1
    for k, (mode, tune) in enumerate(MODES, 1):
        for src_suffix, name_suffix in (("with guitar", "w-gtr"), ("without guitar", "w-out gtr")):
            src = f"{tune} ({mode} {src_suffix}).mp3"
            src = SOURCE_OVERRIDES.get(src, src)
            title = f"{tune} ({mode}) {name_suffix}"
            tag_copy(os.path.join(ROOT, src), os.path.join(jam, f"{k} {title}.mp3"),
                     f"Jam Trax: {title}", track, total)
            track += 1

    zpath = os.path.join(HERE, "Master the Modes.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:     # MP3s don't compress further
        for dirpath, _dirs, files in os.walk(OUT):
            for fn in sorted(files):
                if fn.startswith("."):
                    continue
                full = os.path.join(dirpath, fn)
                z.write(full, os.path.relpath(full, HERE))
    shutil.rmtree(tmp)
    print("done:", OUT, "and", zpath, f"({os.path.getsize(zpath) / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()

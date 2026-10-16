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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from guide_links import add_links

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

# Gill Sans, to match the original guide (macOS's copy allows preview & print embedding)
GILL = "/System/Library/Fonts/Supplemental/GillSans.ttc"
pdfmetrics.registerFont(TTFont("GillSans", GILL, subfontIndex=0))
pdfmetrics.registerFont(TTFont("GillSans-Bold", GILL, subfontIndex=1))
pdfmetrics.registerFont(TTFont("GillSans-SemiBold", GILL, subfontIndex=4))

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


def text_block(c, x, y, lines, size=12, leading=17, color=INK, font="GillSans"):
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


def paragraph(c, x, y, text, width, size=12, leading=16, color=INK, font="GillSans"):
    """Word-wrapped paragraph; returns the y below it."""
    return text_block(c, x, y, simpleSplit(text, font, size, width), size, leading, color, font)


def link(c, x, y, label, url, size=12):
    c.setFont("GillSans-Bold", size)
    c.setFillColor(GOLD)
    c.drawString(x, y, label)
    w = c.stringWidth(label, "GillSans-Bold", size)
    c.linkURL(url, (x, y - 3, x + w, y + size), relative=0)


# Layout matching the original guide: Gill Sans, ~0.55in margins, 14pt body
LEFT, RIGHT = 40, W - 40
BODY, LEAD = 14, 19.5


class Page:
    """Top-down writer for one letter page; refuses to run off the bottom."""

    def __init__(self, path, title):
        self.c = canvas.Canvas(path, pagesize=letter)
        self.c.setFillColor(INK)
        self.c.setFont("GillSans-SemiBold", 24)
        self.c.drawString(LEFT, H - 70, title)
        self.c.setStrokeColor(GOLD)
        self.c.setLineWidth(1.5)
        self.c.line(LEFT, H - 82, LEFT + 90, H - 82)
        self.y = H - 116

    def _room(self, need):
        if self.y - need < 46:
            raise ValueError("page content runs off the bottom; shorten the text")

    def gap(self, pts):
        self.y -= pts

    def subhead(self, text):
        self.gap(8)
        self._room(24)
        self.c.setFont("GillSans-Bold", 16); self.c.setFillColor(INK)
        self.c.drawString(LEFT, self.y, text)
        self.y -= 23

    def para(self, text, x=LEFT, size=BODY, lead=LEAD, color=INK, font="GillSans", after=6):
        lines = simpleSplit(text, font, size, RIGHT - x)
        self._room(lead * len(lines))
        self.y = text_block(self.c, x, self.y, lines, size, lead, color, font) - after

    def row(self, label, text, label_w=170):
        """Bold label with a wrapped description beside it."""
        lines = simpleSplit(text, "GillSans", BODY, RIGHT - LEFT - label_w)
        self._room(LEAD * len(lines))
        self.c.setFont("GillSans-Bold", BODY); self.c.setFillColor(INK)
        self.c.drawString(LEFT, self.y, label)
        self.y = text_block(self.c, LEFT + label_w, self.y, lines, BODY, LEAD) - 4

    def numbered(self, k, text):
        self.c.setFont("GillSans-Bold", BODY); self.c.setFillColor(GOLD)
        self.c.drawString(LEFT, self.y, f"{k}.")
        self.para(text, x=LEFT + 20, after=5)

    def link_line(self, label, shown, url):
        self._room(48)
        self.c.setFont("GillSans-Bold", BODY); self.c.setFillColor(INK)
        self.c.drawString(LEFT, self.y, label)
        link(self.c, LEFT, self.y - 20, shown, url, size=BODY)
        self.y -= 52

    def save(self):
        self.c.showPage()
        self.c.save()


def start_here_page(path):
    pg = Page(path, "Start Here")
    pg.para("Welcome to Master the Modes, the ear-first course by Rob Reich and Doug Glener. "
            "Everything is in the key of C, so you hear what each mode itself sounds like.")
    pg.subhead("What's in your folder")
    pg.row("This guide", "the modes explained, one page each, plus practice tips.")
    pg.row("Master Class with Rob", "a one-hour audio lesson that walks through the whole idea.")
    pg.row("1 Intro Trax", "a short, simple track for each mode. \"w-gtr\" has Rob playing; "
                           "\"w-out gtr\" is the same track without him, for you to play over.")
    pg.row("2 Jam Traxs", "a full tune for each mode in a real style (funk, reggae, rock, "
                          "fusion), again with and without Rob's guitar.")
    pg.subhead("How to use it")
    pg.numbered(1, "Listen to the start of the Master Class. In the first few minutes Rob plays "
                   "all seven modes from C, and you hear how different they are.")
    pg.numbered(2, "Work through the modes in this guide's order. For each one, read its page, "
                   "listen to Rob on the Intro Trax (w-gtr), then play along with the w-out gtr version.")
    pg.numbered(3, "When a mode feels comfortable, move on to its Jam Trax: hear what Rob does "
                   "with it, then take your own solo over the version without guitar.")
    pg.subhead("Why the modes are in this order")
    pg.para("The lessons and tracks follow a learning order. Start with the major scale (Ionian). "
            "Dorian flattens its 3rd and 7th, and each minor mode after that flattens one more note: "
            "Aeolian adds a flat 6th, Phrygian a flat 2nd, Locrian a flat 5th. Each step darkens the "
            "sound, so you hear exactly what one altered note does. Lydian (sharp 4th) and Mixolydian "
            "(flat 7th) each change just one note of the major scale.")
    pg.para("The charts and the Master Class use the traditional order: Ionian, Dorian, Phrygian, "
            "Lydian, Mixolydian, Aeolian, Locrian.", after=10)
    pg.para("Tap any underlined track name or speaker icon to play it. In the text, \"Dorian w/gtr\" "
            "is the file \"Dorian w-gtr\".", size=12, lead=16, color=SOFT, after=10)
    pg.para("Try the interactive mode wheel, with Rob's guitar on or off, at", after=2)
    link(pg.c, LEFT, pg.y, "robreichguitar.com", SITE + "/#woodshed", size=BODY)
    pg.save()


def closing_page(path):
    pg = Page(path, "Keep Going with Rob")
    pg.para("Rob Reich is a jazz fusion guitarist and composer in the New York area. He teaches "
            "privately, and he played every solo on these tracks live, in one take.", after=18)
    pg.link_line("Lessons, gigs and booking", "robreichguitar.com", SITE)
    pg.link_line("The mode wheel (play along online)", "robreichguitar.com/#woodshed", SITE + "/#woodshed")
    pg.link_line("Videos, including the modes challenge series", "youtube.com/@RobReichGuitar", YOUTUBE)
    pg.gap(6)
    pg.para("You're receiving this because you signed up at robreichguitar.com. Rob sends an "
            "occasional email about new videos, gigs and lesson openings; you can unsubscribe "
            "from any of them in one click.", size=12, lead=16, color=SOFT)
    pg.c.setFont("GillSans", 11); pg.c.setFillColor(SOFT)
    pg.c.drawString(LEFT, 52, "Master the Modes by Rob Reich & Doug Glener.")
    pg.save()


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
    # clickable audio mentions (Start Here sits after the cover, shifting later pages by one)
    add_links(w, os.path.join(ROOT, "Master the Modes.pdf"), lambda p: 0 if p == 1 else p)
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

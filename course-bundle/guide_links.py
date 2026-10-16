"""
Makes the guide's audio references clickable ("Listen to Dorian w/gtr",
"play along with Saturn", "the Master Class audio track"...).

Each mention gets an invisible link over its exact words, pointing at that
track's Google Drive file. Drive URLs live in drive_links.json (kept out of
git: they open the course to anyone who has them).

Used by build_bundle.py; run on its own to list what it found:
    python3 guide_links.py
"""
import json
import os

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer, LTTextLine

HERE = os.path.dirname(os.path.abspath(__file__))
LINKS_FILE = os.path.join(HERE, "drive_links.json")

# (page in the ORIGINAL guide, approx line y, words to link, target key).
# A mention that wraps onto a second line is listed once per line.
MENTIONS = [
    (4, 126, "Master Class audio track", "master_class"),
    (6, 529, "IntroTraxs", "folder_intro"),
    (8, 716, "Ionian w/gtr", "intro_ionian_w"),
    (8, 694, "Ionian", "intro_ionian_wo"),
    (8, 673, "w/out gtr", "intro_ionian_wo"),
    (8, 630, "Traveling South", "jam_ionian_w"),
    (8, 608, "w/gtr", "jam_ionian_w"),
    (9, 299, "Dorian w/gtr", "intro_dorian_w"),
    (9, 283, "Dorian w/out gtr", "intro_dorian_wo"),
    (9, 249, "Jamming at the Palla-", "jam_dorian_w"),
    (9, 232, "dium w/gtr", "jam_dorian_w"),
    (9, 215, "Jamming at the Palladium without lead guitar", "jam_dorian_wo"),
    (10, 290, "Aeolian w/gtr", "intro_aeolian_w"),
    (10, 271, "Aeolian w/out gtr", "intro_aeolian_wo"),
    (10, 241, "Ode to", "jam_aeolian_w"),
    (10, 223, "Jimi and Jimmy w/gtr", "jam_aeolian_w"),
    (10, 204, "Ode", "jam_aeolian_wo"),
    (10, 185, "to Jimi and Jimmy", "jam_aeolian_wo"),
    (11, 285, "Phrygian w/gtr", "intro_phrygian_w"),
    (11, 266, "Phrygian w/out gtr", "intro_phrygian_wo"),
    (11, 228, "Marrakesh w/gtr", "jam_phrygian_w"),
    (11, 208, "Marrakesh without guitar", "jam_phrygian_wo"),
    (12, 182, "Locrian w/gtr", "intro_locrian_w"),
    (12, 160, "Locrian", "intro_locrian_wo"),
    (12, 139, "w/out gtr", "intro_locrian_wo"),
    (12, 96, "Saturn w/gtr", "jam_locrian_w"),
    (12, 74, "Saturn", "jam_locrian_wo"),
    (13, 255, "Lydian w/gtr", "intro_lydian_w"),
    (13, 233, "Lydian w/out gtr", "intro_lydian_wo"),
    (13, 190, "Manhattan Reggae w/gtr", "jam_lydian_w"),
    (13, 168, "the version without guitar", "jam_lydian_wo"),
    (14, 292, "Mixolydian w/gtr", "intro_mixolydian_w"),
    (14, 273, "C Mixolydian w/out gtr", "intro_mixolydian_wo"),
    (14, 234, "Wah-wah man w/gtr", "jam_mixolydian_w"),
    (14, 215, "Wah-wah man", "jam_mixolydian_wo"),
    (19, 147, "The Master Class audio track", "master_class"),
    (20, 562, "The Master Class audio track", "master_class"),
    (20, 433, "The Master Class audio track", "master_class"),
]


def _lines(pdf_path):
    """{page number: [(y0, chars, text)]} for every text line."""
    out = {}
    for pno, page in enumerate(extract_pages(pdf_path), 1):
        rows = []
        for el in page:
            if isinstance(el, LTTextContainer):
                for line in el:
                    if isinstance(line, LTTextLine):
                        chars = [c for c in line if isinstance(c, LTChar)]
                        rows.append((line.y0, chars, "".join(c.get_text() for c in chars)))
        out[pno] = rows
    return out


def _speaker_icons(pdf_path):
    """{page: [(x0, y0, x1, y1)]} for the ~26pt speaker icons beside "Listen to ..." lines."""
    from pdfminer.layout import LTImage

    def walk(o):
        yield o
        if hasattr(o, "__iter__"):
            for c in o:
                yield from walk(c)

    out = {}
    for pno, page in enumerate(extract_pages(pdf_path), 1):
        boxes = {(round(o.x0), round(o.y0), round(o.x1), round(o.y1))
                 for el in page for o in walk(el)
                 if isinstance(o, LTImage) and 22 <= o.x1 - o.x0 <= 32 and 22 <= o.y1 - o.y0 <= 32}
        if boxes:
            out[pno] = sorted(boxes)
    return out


def _with_icon(rect, icons):
    """Grow a mention's link leftward over the speaker icon on its line, so clicking
    the icon (or "Listen to") plays the same track."""
    x0, y0, x1, y1 = rect
    for ix0, iy0, ix1, iy1 in icons:
        overlap = min(y1, iy1) - max(y0, iy0)
        if overlap > 0.5 * (y1 - y0) and 0 <= x0 - ix1 < 120:
            return (ix0 - 2, min(y0, iy0 - 1), x1, max(y1, iy1 + 1))
    return rect


def locate(pdf_path):
    """[(original page, (x0, y0, x1, y1), key, words)] for every mention."""
    lines = _lines(pdf_path)
    icons = _speaker_icons(pdf_path)
    found = []
    for page, y, words, key in MENTIONS:
        hit = None
        target = words.replace(" ", "")
        for y0, chars, text in lines.get(page, []):
            # match ignoring spaces: the PDF sometimes stores two words with no space between
            solid = [c for c in chars if not c.get_text().isspace()]
            squashed = "".join(c.get_text() for c in solid)
            if abs(y0 - y) < 4 and target in squashed:
                i = squashed.rindex(target)   # last match: "C Ionian ... the IntroTrack, Ionian"
                cs = solid[i:i + len(target)]
                hit = (min(c.x0 for c in cs) - 1, min(c.y0 for c in cs) - 2,
                       max(c.x1 for c in cs) + 1, max(c.y1 for c in cs) + 2)
                break
        if not hit:
            raise ValueError(f"guide page {page}: couldn't find {words!r} near y={y}")
        found.append((page, _with_icon(hit, icons.get(page, [])), key, words))
    return found


def _add_uri(writer, page_index, url, rect):
    """A standard invisible web link. (PyPDF2 2.x's add_uri writes /Type /Annots
    instead of /Annot, which Google Drive's and Apple's PDF viewers ignore.)"""
    from PyPDF2.generic import (ArrayObject, DictionaryObject, FloatObject,
                                NameObject, NumberObject, TextStringObject)
    link = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Link"),
        NameObject("/Rect"): ArrayObject([FloatObject(round(v, 2)) for v in rect]),
        NameObject("/Border"): ArrayObject([NumberObject(0)] * 3),
        NameObject("/A"): DictionaryObject({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject(url),
        }),
    })
    page = writer.pages[page_index]
    if "/Annots" not in page:
        page[NameObject("/Annots")] = ArrayObject()
    page["/Annots"].append(writer._add_object(link))


def add_links(writer, original_pdf, page_offset):
    """Add link annotations to `writer` (a PyPDF2.PdfWriter holding the bundle guide).
    `page_offset(original_page)` gives the 0-based page index in the new guide."""
    if not os.path.exists(LINKS_FILE):
        print("no drive_links.json: guide built without audio links")
        return 0
    urls = json.load(open(LINKS_FILE))
    n = 0
    for page, rect, key, _words in locate(original_pdf):
        if key in urls:
            _add_uri(writer, page_offset(page), urls[key], rect)
            n += 1
    print(f"added {n} audio links to the guide")
    return n


if __name__ == "__main__":
    src = os.path.join(os.path.dirname(HERE), "Master the Modes.pdf")
    for page, rect, key, words in locate(src):
        print(f"p{page:02d} {key:22s} {words}")

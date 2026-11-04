"""
Clean Wake Up album covers from Rob's drafts:
  front: square, title only (no URL/logo, as streaming services require), 3000x3000
  back:  confirmed track order, credits, Winwood credit, website

The draft text is baked into the images, so it's painted out (diffusion fill) and
redrawn crisp at full size.

    python3 wake_up_covers.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ALBUM = os.path.join(os.path.dirname(HERE), "Album Wake Up Rob Reich")
OUT = os.path.join(ALBUM, "Covers")
FONTS = os.path.join(HERE, "fonts")
S = 3000
CREAM, GOLD = (250, 240, 214), (244, 205, 120)

NOTE = "All songs composed by Rob Reich except *Can't Find My Way Home (Steve Winwood)"
TRACKS = ["Wake Up", "Moon Pie", "Grateful", "Citi", "R.V.W.", "New Day",
          "Can't Find My Way Home*", "Strut (Live)", "Badfinger"]   # Rob's corrected order


def serif(size, weight=600):
    f = ImageFont.truetype(os.path.join(FONTS, "Fraunces-Variable.ttf"), size)
    try:
        f.set_variation_by_axes([weight, 144, 0, 0][:len(f.get_variation_axes())])
    except Exception:
        pass
    return f


def italic(size):
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Italic.ttf", size)


def fill_holes(im, mask, iters=600):
    """Paint out masked pixels by repeatedly averaging their neighbours, then add matching grain."""
    a = np.asarray(im, float)
    m = np.asarray(mask) > 0
    out = a.copy()
    out[m] = 0
    known = (~m).astype(float)
    acc = out * known[..., None]
    w = known.copy()
    for _ in range(iters):
        acc_s = (np.roll(acc, 1, 0) + np.roll(acc, -1, 0) + np.roll(acc, 1, 1) + np.roll(acc, -1, 1))
        w_s = (np.roll(w, 1, 0) + np.roll(w, -1, 0) + np.roll(w, 1, 1) + np.roll(w, -1, 1))
        fill = acc_s / np.maximum(w_s, 1e-6)[..., None]
        newly = m & (w_s > 0)
        acc[newly] = fill[newly] * np.minimum(w_s[newly], 1)[..., None]
        w[newly] = np.minimum(w_s[newly], 1)
    out[m] = acc[m] / np.maximum(w[m], 1e-6)[..., None]
    rnd = np.random.default_rng(1).normal(0, 5, out.shape)
    out[m] += rnd[m]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def text_mask(im, boxes, grow=7):
    """Bright, low-saturation pixels (the old cream lettering) inside the given boxes."""
    a = np.asarray(im).astype(int)
    lum = a.mean(2); sat = a.max(2) - a.min(2)
    m = np.zeros(lum.shape, bool)
    for x0, y0, x1, y1 in boxes:
        sub = (lum[y0:y1, x0:x1] > 150) & (sat[y0:y1, x0:x1] < 120)
        m[y0:y1, x0:x1] |= sub
    mk = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(grow))
    return mk


def centered(d, y, text, font, fill, tracking=0, shadow=True):
    w = sum(d.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)
    x = (S - w) / 2
    for ch in text:
        if shadow:
            d.text((x + 6, y + 6), ch, font=font, fill=(10, 8, 20, 150))
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking
    return w


def title(im, y_name=560, y_wake=930):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    centered(d, y_name, "Rob Reich Group", serif(300, 600), CREAM)
    w = d.textlength("Wake Up", font=italic(270))
    centered(d, y_wake, "Wake Up", italic(270), GOLD)
    cy = y_wake + 175
    for x0, x1 in ((S / 2 - w / 2 - 520, S / 2 - w / 2 - 80), (S / 2 + w / 2 + 80, S / 2 + w / 2 + 520)):
        d.rectangle((x0, cy - 4, x1, cy + 4), fill=GOLD + (230,))
    glow = layer.filter(ImageFilter.GaussianBlur(18))
    base = im.convert("RGBA")
    shade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).ellipse((250, y_name - 200, S - 250, y_wake + 420), fill=(20, 10, 40, 90))
    base.alpha_composite(shade.filter(ImageFilter.GaussianBlur(160)))
    base.alpha_composite(layer)
    return base


def upscale(im):
    big = im.resize((S, S), Image.LANCZOS)
    return big.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))


def front():
    src = Image.open(os.path.join(ALBUM, "Rob Reich Group_ Wake Up-2.png")).convert("RGB")
    art = src.crop((184, 76, 1226, 1118))           # inside the jewel case, clear of its clips
    # old title and the logo/URL in the lower right
    m = text_mask(art, [(30, 120, 1030, 500)], 11)
    logo = Image.new("L", art.size, 0)
    lm = np.asarray(text_mask(art, [(560, 840, art.width, art.height)], 11))
    m = Image.fromarray(np.maximum(np.asarray(m), lm))
    clean = fill_holes(art, m)
    big = title(upscale(clean))
    return big.convert("RGB")


def back():
    src = Image.open(os.path.join(ALBUM, "Sunset Roads_ Wake Up-1.png")).convert("RGB")
    m = text_mask(src, [(120, 150, 1140, 530), (180, 800, 1080, 1210)], 11)
    clean = fill_holes(src, m)
    big = upscale(clean).convert("RGBA")
    # soft dark panel over the road, sized to the widest line of text plus margins
    f, small, note = serif(86, 500), serif(62, 400), italic(54)
    probe = ImageDraw.Draw(big)
    rows = [TRACKS[:3], TRACKS[3:6], TRACKS[6:]]
    lines = ["     ".join(f"{TRACKS.index(t) + 1}. {t}" for t in r) for r in rows]
    widest = max([probe.textlength(l, font=f) for l in lines] +
                 [probe.textlength(NOTE, font=note)])
    half = widest / 2 + 120
    panel = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle((S / 2 - half, 1560, S / 2 + half, 2700), 80, fill=(16, 10, 34, 180))
    big.alpha_composite(panel.filter(ImageFilter.GaussianBlur(24)))
    big = title(big.convert("RGB"), 300, 620)
    d = ImageDraw.Draw(big)
    y = 1660
    for line in lines:
        centered(d, y, line, f, CREAM, shadow=False)
        y += 140
    centered(d, y + 50, "Rob Reich: guitar  ·  Matt King: keyboards", small, GOLD, shadow=False)
    centered(d, y + 140, "Stephan Crump: bass  ·  Aaron Comess: drums", small, GOLD, shadow=False)
    centered(d, y + 270, NOTE, note, (225, 215, 200), shadow=False)
    centered(d, y + 390, "© 2026 Rob Reich  ·  robreichguitar.com", serif(60, 400), (225, 215, 200), shadow=False)
    return big.convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    f = front(); f.save(os.path.join(OUT, "Wake Up - front cover 3000.jpg"), quality=95)
    b = back(); b.save(os.path.join(OUT, "Wake Up - back cover 3000.jpg"), quality=95)
    print("done:", OUT)

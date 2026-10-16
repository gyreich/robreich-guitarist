"""
Shared brand constants and helpers for Rob Reich "Official Audio" video cards.
Colors are pulled directly from index.html's dark-theme CSS custom properties.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

FRAUNCES = os.path.join(FONT_DIR, "Fraunces-Variable.ttf")
MONO_MED = os.path.join(FONT_DIR, "IBMPlexMono-Medium.ttf")
MONO_SEMI = os.path.join(FONT_DIR, "IBMPlexMono-SemiBold.ttf")

# Dark-theme palette (index.html :root[data-theme=dark] / prefers-color-scheme: dark)
INK = (16, 12, 7)          # --ink
PAPER_DARK = (28, 23, 15)  # --paper (dark)
TEXT = (237, 230, 214)     # --text
TEXT_SOFT = (179, 168, 144)  # --text-soft
GOLD = (224, 163, 68)      # --gold
GOLD_STRONG = (240, 185, 92)  # --gold-strong

W, H = 1920, 1080


def fraunces(size, weight=600):
    f = ImageFont.truetype(FRAUNCES, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def mono(size, semibold=False):
    return ImageFont.truetype(MONO_SEMI if semibold else MONO_MED, size)


def tracked_width(draw, text, font, tracking):
    w = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        w += (bbox[2] - bbox[0]) + tracking
    return w - tracking if text else 0


def draw_tracked(draw, center_x, y, text, font, fill, tracking, anchor="la"):
    total_w = tracked_width(draw, text, font, tracking)
    x = center_x - total_w / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, anchor=anchor)
        bbox = draw.textbbox((0, 0), ch, font=font)
        x += (bbox[2] - bbox[0]) + tracking
    return total_w


def draw_tracked_mixed(draw, center_x, y, spans, tracking, anchor="la"):
    """spans: list of (text, font, fill). Renders as one centered line, tracked per-char."""
    total_w = 0
    for text, font, _ in spans:
        total_w += tracked_width(draw, text, font, tracking)
    x = center_x - total_w / 2
    for text, font, fill in spans:
        for ch in text:
            draw.text((x, y), ch, font=font, fill=fill, anchor=anchor)
            bbox = draw.textbbox((0, 0), ch, font=font)
            x += (bbox[2] - bbox[0]) + tracking


def cover_crop(im, w, h):
    im = im.convert("RGB")
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - w) // 2
    y0 = (nh - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def vignette(im, strength=0.55):
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((-w * 0.25, -h * 0.35, w * 1.25, h * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.12))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    darkened = Image.composite(im, dark, mask)
    return Image.blend(im, darkened, strength)


def grade_dark_warm(im, brightness=0.5, saturation=0.82, warm_mix=0.22):
    im = ImageEnhance.Color(im).enhance(saturation)
    im = ImageEnhance.Brightness(im).enhance(brightness)
    warm = Image.new("RGB", im.size, INK)
    im = Image.blend(im, warm, warm_mix)
    return im


def top_bottom_gradient(im, top_frac=0.40, bottom_frac=0.48, top_strength=0.95, bottom_strength=0.95):
    w, h = im.size
    grad = Image.new("L", (1, h), 0)
    for y in range(h):
        v = 0.0
        ty = h * top_frac
        by = h * (1 - bottom_frac)
        if y < ty:
            v = top_strength * (1 - y / ty)
        elif y > by:
            v = bottom_strength * ((y - by) / (h - by))
        grad.putpixel((0, y), int(max(0, min(1, v)) * 255))
    grad = grad.resize((w, h))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(black, im, ImageOps_invert_L(grad))


def ImageOps_invert_L(mask_l):
    from PIL import ImageOps
    return ImageOps.invert(mask_l)


def text_scrim(im, center, size, strength=0.55, feather=0.5):
    """Soft dark halo behind a text block, so the photo stays visible
    everywhere else instead of being darkened globally."""
    w, h = im.size
    cx, cy = center
    bw, bh = size
    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(bw, bh) * feather)))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    darkened = Image.composite(dark, im, mask)
    return Image.blend(im, darkened, strength)

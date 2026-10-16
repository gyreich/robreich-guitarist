"""
Elegant, archival-style placement for portrait-oriented photos.
Places the full, uncropped image inside a box on a dark warm canvas,
with a soft glow and a thin gold hairline frame -- no blurred/stretched
background fill.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from brand import INK, PAPER_DARK, GOLD, W, H, vignette


def dark_canvas(w=W, h=H):
    im = Image.new("RGB", (w, h), PAPER_DARK)
    # subtle vertical warm gradient, slightly lighter center
    top = tuple(int(c * 0.7) for c in PAPER_DARK)
    grad = Image.new("L", (1, h), 0)
    for y in range(h):
        t = abs(y - h / 2) / (h / 2)
        grad.putpixel((0, y), int(255 * (t ** 1.4)))
    grad = grad.resize((w, h))
    dark = Image.new("RGB", (w, h), top)
    im = Image.composite(dark, im, grad)
    return im


def place_portrait(canvas, img_path, box, border_color=GOLD, glow_strength=0.35):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    im = Image.open(img_path)
    im = ImageOps.exif_transpose(im).convert("RGB")
    iw, ih = im.size
    scale = min(bw / iw, bh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.LANCZOS)

    px = x0 + (bw - nw) // 2
    py = y0 + (bh - nh) // 2

    # soft gold glow behind the image
    glow = Image.new("RGB", canvas.size, (0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    pad = 26
    gdraw.rectangle((px - pad, py - pad, px + nw + pad, py + nh + pad), fill=GOLD)
    glow = glow.filter(ImageFilter.GaussianBlur(46))
    glow_mask = glow.convert("L").point(lambda v: int(v * glow_strength))
    canvas = Image.composite(
        Image.blend(canvas, Image.new("RGB", canvas.size, GOLD), 1.0),
        canvas,
        glow_mask,
    )

    # drop shadow
    shadow = Image.new("L", canvas.size, 0)
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rectangle((px - 4, py + 10, px + nw + 4, py + nh + 18), fill=140)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    black = Image.new("RGB", canvas.size, (0, 0, 0))
    canvas = Image.composite(black, canvas, ImageOps.invert(shadow))

    canvas.paste(im, (px, py))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((px - 1, py - 1, px + nw, py + nh), outline=border_color, width=1)
    inset = 6
    faint = tuple(int(c * 0.55) for c in border_color)
    draw.rectangle((px - inset, py - inset, px + nw + inset, py + nh + inset),
                    outline=faint, width=1)
    return canvas, (px, py, px + nw, py + nh)


def make_portrait_card(img_path, out_path):
    canvas = dark_canvas()
    canvas = vignette(canvas, strength=0.35)
    box = (620, 70, 1300, 1010)
    canvas, _ = place_portrait(canvas, img_path, box)
    canvas.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    import sys
    make_portrait_card(sys.argv[1], sys.argv[2])
    print("wrote", sys.argv[2])

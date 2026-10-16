#!/usr/bin/env python3
"""
Reusable closing-card template for Rob Reich "Official Audio" videos.

Usage:
    python3 closing_card.py --bg photo.png --out close.png
"""
import argparse
from PIL import Image, ImageDraw
from brand import (
    W, H, TEXT, GOLD, GOLD_STRONG, TEXT_SOFT,
    fraunces, mono, draw_tracked, vignette,
)
from portrait_frame import dark_canvas, place_portrait


def make_closing_card(bg_path, out_path, artist="ROB REICH",
                       tagline="GUITAR  •  VOICE  •  MUSICIANSHIP",
                       url="robreichguitar.com"):
    canvas = dark_canvas()
    canvas = vignette(canvas, strength=0.4)

    box = (1180, 60, 1860, 1020)
    canvas, _ = place_portrait(canvas, bg_path, box, glow_strength=0.3)

    draw = ImageDraw.Draw(canvas)
    cx = 560

    f_artist = fraunces(84, weight=720)
    f_tagline = mono(26, semibold=False)
    f_url = fraunces(40, weight=520)

    y = 430
    draw_tracked(draw, cx, y, artist, f_artist, TEXT, tracking=8)

    line_y = y + 108
    draw.rectangle((cx - 90, line_y, cx + 90, line_y + 2), fill=GOLD)

    y2 = line_y + 34
    draw_tracked(draw, cx, y2, tagline, f_tagline, GOLD, tracking=4)

    y3 = y2 + 70
    draw_tracked(draw, cx, y3, url, f_url, (230, 222, 205), tracking=1)

    canvas.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--artist", default="ROB REICH")
    ap.add_argument("--tagline", default="GUITAR  •  VOICE  •  MUSICIANSHIP")
    ap.add_argument("--url", default="robreichguitar.com")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    make_closing_card(args.bg, args.out, artist=args.artist,
                       tagline=args.tagline, url=args.url)
    print("wrote", args.out)

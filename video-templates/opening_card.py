#!/usr/bin/env python3
"""
Reusable opening-card template for Rob Reich "Official Audio" videos.

Usage:
    python3 opening_card.py --bg photo.png --track "NEW DAY" \
        --album "WAKE UP" --out open.png

All text is rendered as live overlays (never baked into the source photo),
so future tracks/albums/images can be substituted without redesigning
anything.
"""
import argparse
from PIL import Image, ImageDraw
from brand import (
    W, H, TEXT, GOLD, GOLD_STRONG, TEXT_SOFT,
    fraunces, mono, draw_tracked, draw_tracked_mixed, tracked_width,
    cover_crop, vignette, grade_dark_warm, text_scrim,
)


def make_opening_card(bg_path, out_path, artist="ROB REICH", track="NEW DAY",
                       format_label="OFFICIAL AUDIO", album_prefix="FROM THE ALBUM",
                       album_name="WAKE UP"):
    im = Image.open(bg_path)
    im = cover_crop(im, W, H)
    # Light grade only -- keep the photo clearly visible/recognizable.
    im = grade_dark_warm(im, brightness=0.78, saturation=0.92, warm_mix=0.10)
    im = vignette(im, strength=0.28)

    draw = ImageDraw.Draw(im)
    cx = W // 2

    f_artist = fraunces(58, weight=560)
    f_track = fraunces(190, weight=800)
    f_format = mono(36, semibold=False)
    f_album_dim = mono(28, semibold=False)
    f_album_bright = mono(32, semibold=True)

    line_gap = 3
    gap_artist_to_track = 46
    gap_track_to_format = 44
    gap_format_to_album = 40

    def line_h(font, sample="ROB REICH Qy"):
        bbox = draw.textbbox((0, 0), sample, font=font)
        return bbox[3] - bbox[1]

    h_artist = line_h(f_artist)
    h_line1 = 3
    h_track = line_h(f_track, track + " Qy")
    h_format = line_h(f_format)
    h_line2 = 3
    h_album = line_h(f_album_bright, (album_name or "") + " Qy") if album_name else 0

    total_h = (h_artist + 28 + h_line1 + gap_artist_to_track + h_track +
               gap_track_to_format + h_format)
    if album_name:   # no album row for a single that isn't on an album yet
        total_h += 30 + h_line2 + gap_format_to_album + h_album

    y = (H - total_h) // 2 - 20

    # Soft dark halo behind the whole text block so it reads clearly
    # while the rest of the photo stays visible.
    scrim_w = max(1500, tracked_width(draw, track, f_track, 2) + 300)
    im = text_scrim(im, (cx, H // 2 - 10), (scrim_w, total_h + 260),
                     strength=0.5, feather=0.55)
    draw = ImageDraw.Draw(im)

    draw_tracked(draw, cx, y, artist, f_artist, TEXT, tracking=12)
    y += h_artist + 28

    draw.rectangle((cx - 60, y, cx + 60, y + 3), fill=GOLD)
    y += h_line1 + gap_artist_to_track

    draw_tracked(draw, cx, y, track, f_track, (247, 240, 226), tracking=2)
    y += h_track + gap_track_to_format

    draw_tracked(draw, cx, y, format_label, f_format, GOLD, tracking=11)
    if not album_name:
        im.save(out_path, "PNG")
        return out_path
    y += h_format + 30

    draw.rectangle((cx - 60, y, cx + 60, y + 3), fill=GOLD)
    y += h_line2 + gap_format_to_album

    spans = [
        (album_prefix + "   ", f_album_dim, TEXT_SOFT),
        (album_name, f_album_bright, GOLD_STRONG),
    ]
    draw_tracked_mixed(draw, cx, y, spans, tracking=7)

    im.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--track", required=True)
    ap.add_argument("--album", required=True)
    ap.add_argument("--artist", default="ROB REICH")
    ap.add_argument("--format-label", default="OFFICIAL AUDIO")
    ap.add_argument("--album-prefix", default="FROM THE ALBUM")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    make_opening_card(args.bg, args.out, artist=args.artist, track=args.track,
                       format_label=args.format_label,
                       album_prefix=args.album_prefix, album_name=args.album)
    print("wrote", args.out)

#!/usr/bin/env python3
"""Generate Happy_Birthday.png for Model Y 2025 Premium UV template.

Layout intent (see Siamese_Cat.png reference):
- top_mid upper ~80% reads as plain / frunk in that wrap; the lower band has the main
  hood graphic. Frunk billboard = left/right halves of that upper top_mid band only —
  not fender_L / fender_R (those map like the Siamese "eye" panels).
- Front-facing islands (top_strip, top_mid frunk band) render with UV flipped vs PNG Y in
  the game viewer: stacked frunk text + bumper line are pasted rotated 180° so they read upright.
- Approach / park: top_strip + frunk + doors + spines.
- Chase / driving: bottom_mid + rear quarters + spines + lower top_mid (cake).
- Template has extra small white islands (corners, sill, mirrors): fill rear-related ones with
  the same mint–cyan gradient as bottom_mid so chase view is not bare black.
"""

from __future__ import annotations

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, "template.png")

# Panel bboxes in template pixel space (from white-island analysis).
BBOXES: dict[str, tuple[int, int, int, int]] = {
    "top_mid": (376, 111, 644, 337),
    "top_strip": (245, 9, 776, 116),
    "door_L": (83, 349, 258, 594),
    "door_R": (763, 350, 936, 595),
    "rear_L": (69, 570, 233, 791),
    "rear_R": (785, 573, 949, 794),
    "spine_L": (343, 347, 387, 810),
    "spine_R": (633, 348, 678, 811),
    "bottom_mid": (396, 940, 629, 1012),
    "fender_L": (111, 115, 330, 365),
    "fender_R": (695, 115, 910, 366),
    # Small islands around the rear / lower body (same template; game may map these to visible black panels).
    "rear_corner_ll": (56, 886, 172, 1013),
    "rear_corner_lr": (854, 888, 967, 1015),
    "rear_lower_strip": (357, 874, 662, 928),
    "rear_side_ll": (124, 780, 263, 948),
    "rear_side_lr": (758, 783, 897, 952),
    "rear_sliver_l": (302, 815, 355, 960),
    "rear_sliver_r": (667, 816, 718, 963),
    "mirror_l": (272, 368, 340, 406),
    "mirror_r": (680, 368, 747, 405),
}

# Same palette as bottom_mid — filled so the rear reads as one continuous party surface.
REAR_CONTINUITY_KEYS = (
    "rear_L",
    "rear_R",
    "bottom_mid",
    "rear_corner_ll",
    "rear_corner_lr",
    "rear_lower_strip",
    "rear_side_ll",
    "rear_side_lr",
    "rear_sliver_l",
    "rear_sliver_r",
)


def load_mask(path: str) -> Image.Image:
    tpl = Image.open(path).convert("RGB")
    w, h = tpl.size
    mask = Image.new("L", (w, h), 0)
    md = mask.load()
    px = tpl.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r >= 250 and g >= 250 and b >= 250:
                md[x, y] = 255
    return mask


def fill_masked_gradient(
    img: Image.Image,
    mask: Image.Image,
    bbox: tuple[int, int, int, int],
    c1: tuple[int, int, int],
    c2: tuple[int, int, int],
    diagonal: bool = True,
) -> None:
    x0, y0, x1, y1 = bbox
    mw, mh = mask.size
    pix = img.load()
    mk = mask.load()
    denom = max(1, (x1 - x0) + (y1 - y0))
    vdenom = max(1, (y1 - y0))
    for y in range(max(0, y0), min(mh - 1, y1 + 1)):
        for x in range(max(0, x0), min(mw - 1, x1 + 1)):
            if mk[x, y] < 128:
                continue
            if diagonal:
                t = ((x - x0) + (y - y0)) / denom
            else:
                t = (y - y0) / vdenom
            t = max(0.0, min(1.0, t))
            r = int(c1[0] * (1 - t) + c2[0] * t)
            g = int(c1[1] * (1 - t) + c2[1] * t)
            b = int(c1[2] * (1 - t) + c2[2] * t)
            pix[x, y] = (r, g, b)


def composite_rgba_under_mask(
    base_rgb: Image.Image,
    overlay_rgba: Image.Image,
    mask: Image.Image,
) -> None:
    """Alpha-composite overlay onto base; only where mask is white."""
    w, h = base_rgb.size
    bp = base_rgb.load()
    op = overlay_rgba.load()
    mk = mask.load()
    for y in range(h):
        for x in range(w):
            if mk[x, y] < 128:
                continue
            r, g, b, a = op[x, y]
            if a < 8:
                continue
            if a >= 254:
                bp[x, y] = (r, g, b)
            else:
                br, bg, bb = bp[x, y]
                ia = a / 255.0
                bp[x, y] = (
                    int(br * (1 - ia) + r * ia),
                    int(bg * (1 - ia) + g * ia),
                    int(bb * (1 - ia) + b * ia),
                )


def clear_rgba(img: Image.Image) -> None:
    w, h = img.size
    img.paste((0, 0, 0, 0), (0, 0, w, h))


def draw_top_down_cake(d: ImageDraw.ImageDraw, cx: float, cy: float, scale: float) -> None:
    """Top-down birthday cake: stacked rounds + candles."""
    r0 = 55 * scale
    d.ellipse(
        [cx - r0, cy - r0, cx + r0, cy + r0],
        fill=(255, 235, 200),
        outline=(210, 170, 130),
        width=2,
    )
    r1 = 40 * scale
    d.ellipse(
        [cx - r1, cy - 20 * scale - r1, cx + r1, cy - 20 * scale + r1],
        fill=(255, 192, 203),
        outline=(220, 120, 150),
        width=2,
    )
    r2 = 26 * scale
    d.ellipse(
        [cx - r2, cy - 42 * scale - r2, cx + r2, cy - 42 * scale + r2],
        fill=(173, 216, 230),
        outline=(100, 140, 200),
        width=2,
    )
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        bx = cx + math.cos(rad) * r0 * 0.85
        by = cy + math.sin(rad) * r0 * 0.85
        d.ellipse(
            [bx - 6 * scale, by - 6 * scale, bx + 6 * scale, by + 6 * scale],
            fill=(255, 255, 255),
        )
    for i, dx in enumerate([-10 * scale, 0.0, 10 * scale]):
        px_, py_ = cx + dx, cy - 42 * scale
        d.rectangle(
            [px_ - 2 * scale, py_ - 14 * scale, px_ + 2 * scale, py_],
            fill=(255, 240, 200),
        )
        d.polygon(
            [
                (px_, py_ - 16 * scale),
                (px_ - 3 * scale, py_ - 22 * scale),
                (px_ + 3 * scale, py_ - 22 * scale),
            ],
            fill=(255, 140 + i * 20, 60),
        )


def draw_strawberry_scoop(d: ImageDraw.ImageDraw, cx: float, cy: float, scale: float) -> None:
    d.ellipse(
        [cx - 38 * scale, cy - 45 * scale, cx + 38 * scale, cy + 25 * scale],
        fill=(255, 105, 140),
        outline=(200, 50, 90),
        width=2,
    )
    for i in range(8):
        sx = cx + (i % 4 - 1.5) * 12 * scale
        sy = cy - 15 * scale + (i // 4) * 14 * scale
        d.ellipse([sx - 2, sy - 3, sx + 2, sy + 3], fill=(255, 220, 200))
    cone = [
        (cx, cy + 28 * scale),
        (cx - 25 * scale, cy + 75 * scale),
        (cx + 25 * scale, cy + 75 * scale),
    ]
    d.polygon(cone, fill=(235, 185, 120), outline=(180, 120, 70))
    for i in range(5):
        oy = i * 10 * scale
        d.line(
            [
                cx - 20 * scale + i * 3,
                cy + 32 * scale + oy,
                cx + 20 * scale - i * 3,
                cy + 32 * scale + oy,
            ],
            fill=(200, 140, 80),
            width=1,
        )
    d.ellipse(
        [cx - 8 * scale, cy - 52 * scale, cx + 8 * scale, cy - 38 * scale],
        fill=(220, 40, 60),
    )
    d.rectangle(
        [cx - 2 * scale, cy - 58 * scale, cx + 2 * scale, cy - 50 * scale],
        fill=(34, 120, 34),
    )


def draw_quindim(d: ImageDraw.ImageDraw, cx: float, cy: float, scale: float) -> None:
    d.ellipse(
        [cx - 35 * scale, cy + 10 * scale, cx + 35 * scale, cy + 38 * scale],
        fill=(240, 220, 170),
        outline=(160, 120, 80),
        width=2,
    )
    d.ellipse(
        [cx - 32 * scale, cy - 32 * scale, cx + 32 * scale, cy + 18 * scale],
        fill=(255, 214, 70),
        outline=(220, 160, 30),
        width=2,
    )
    d.arc(
        [cx - 20 * scale, cy - 28 * scale, cx + 5 * scale, cy - 8 * scale],
        start=200,
        end=320,
        fill=(255, 250, 200),
        width=3,
    )
    for i in range(12):
        ang = math.radians(i * 29 + 10)
        fx = cx + math.cos(ang) * 14 * scale
        fy = cy - 18 * scale + math.sin(ang) * 8 * scale
        d.ellipse([fx - 2, fy - 2, fx + 4, fy + 4], fill=(255, 255, 255))


def draw_party_flags_vertical(
    d: ImageDraw.ImageDraw,
    x0: float,
    y0: float,
    y1: float,
    width: float,
    seed: int,
) -> None:
    """Vertical bunting: party triangles + simplified US and Brazil flags."""
    rng = random.Random(seed)
    n = 9
    party_colors = [
        (255, 99, 132),
        (255, 159, 64),
        (255, 205, 86),
        (75, 192, 192),
        (54, 162, 235),
        (153, 102, 255),
    ]
    ys = [y0 + (y1 - y0) * i / (n - 1) for i in range(n)]
    tw = width * 0.88
    for i, y in enumerate(ys):
        if i == 3:
            # Simplified USA
            d.rectangle([x0, y - 9, x0 + tw, y + 9], fill=(178, 34, 52), outline=(90, 20, 30))
            d.rectangle([x0, y - 9, x0 + tw * 0.4, y], fill=(30, 50, 120), outline=(20, 20, 80))
            for sx in range(3):
                for sy in range(2):
                    px_ = x0 + 4 + sx * 5
                    py_ = y - 7 + sy * 3
                    d.ellipse([px_, py_, px_ + 2, py_ + 2], fill=(255, 255, 255))
        elif i == 5:
            # Simplified Brazil
            d.rectangle([x0, y - 9, x0 + tw, y + 9], fill=(0, 120, 60), outline=(0, 80, 30))
            d.polygon(
                [
                    (x0 + tw * 0.5, y - 5),
                    (x0 + tw * 0.15, y),
                    (x0 + tw * 0.5, y + 5),
                    (x0 + tw * 0.85, y),
                ],
                fill=(255, 204, 0),
            )
            d.ellipse([x0 + tw * 0.42, y - 3, x0 + tw * 0.58, y + 3], fill=(0, 60, 180))
        else:
            col = party_colors[rng.randrange(len(party_colors))]
            d.polygon(
                [(x0, y - 10), (x0 + width, y), (x0, y + 10)],
                fill=col,
                outline=(40, 40, 40),
            )


def draw_banner_in_bbox_rgba(
    d: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int, int] = (255, 255, 255, 255),
    stroke: tuple[int, int, int, int] = (120, 30, 85, 255),
    stroke_w: int = 2,
) -> None:
    """Large horizontal text centered in panel (front / rear readability)."""
    x0, y0, x1, y1 = bbox
    tw, th = x1 - x0, y1 - y0
    tbb = d.textbbox((0, 0), text, font=font)
    bw, bh = tbb[2] - tbb[0], tbb[3] - tbb[1]
    tx = x0 + (tw - bw) / 2
    ty = y0 + (th - bh) / 2 - tbb[1]
    d.text((tx, ty), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)


def render_stacked_lines_image_rgba(
    lines: list[str],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int],
    stroke_w: int = 2,
    line_gap: int = 4,
    pad: int = 8,
) -> Image.Image:
    """Build an RGBA image of vertically stacked centered lines (caller may rotate 180° for front-facing UV)."""
    tmp = Image.new("RGBA", (600, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    max_w = 0
    bbs: list[tuple[int, int, int, int]] = []
    for line in lines:
        bb = d.textbbox((0, 0), line, font=font)
        bbs.append(bb)
        max_w = max(max_w, bb[2] - bb[0])
    total_h = sum(bb[3] - bb[1] for bb in bbs) + line_gap * max(len(lines) - 1, 0)
    img = Image.new("RGBA", (max_w + pad * 2, total_h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y_cursor = float(pad)
    for line, bb in zip(lines, bbs):
        w = bb[2] - bb[0]
        tx = pad + (max_w - w) / 2 - bb[0]
        ty = y_cursor - bb[1]
        d.text((tx, ty), line, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
        y_cursor += (bb[3] - bb[1]) + line_gap
    return img


def render_single_line_image_rgba(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke: tuple[int, int, int, int],
    stroke_w: int = 2,
    pad: int = 8,
) -> Image.Image:
    tmp = Image.new("RGBA", (900, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
    return img


def draw_door_spanning_ribbon(
    d: ImageDraw.ImageDraw,
    door_l: tuple[int, int, int, int],
    door_r: tuple[int, int, int, int],
    mask: Image.Image,
) -> None:
    """Wavy band + confetti across both door islands (continuity at the cabin seam)."""
    lx0, ly0, lx1, ly1 = door_l
    rx0, ry0, rx1, ry1 = door_r
    y0 = max(ly0, ry0)
    y1 = min(ly1, ry1)
    mid_y = (y0 + y1) / 2
    band_half = min(14, (y1 - y0) / 4)
    mk = mask.load()
    # Upper and lower edges of band follow a gentle sine across x
    for x in range(lx0, rx1 + 1):
        t = (x - lx0) / max(1, (rx1 - lx0))
        wave = 5 * math.sin(t * math.pi * 2.2)
        y_center = mid_y + wave
        y_top = max(y0, int(y_center - band_half))
        y_bot = min(y1, int(y_center + band_half))
        for y in range(y_top, y_bot + 1):
            if 0 <= x < mask.size[0] and 0 <= y < mask.size[1] and mk[x, y] >= 128:
                d.point((x, y), fill=(180, 255, 220, 120))
    # Sparse bright dots on the band
    rng = random.Random(33)
    for _ in range(140):
        x = rng.randint(lx0, rx1)
        t = (x - lx0) / max(1, (rx1 - lx0))
        wave = 5 * math.sin(t * math.pi * 2.2)
        y = int(mid_y + wave + rng.uniform(-band_half, band_half))
        if x < mask.size[0] and 0 <= y < mask.size[1] and mk[x, y] >= 128:
            d.rectangle(
                [x, y, x + rng.choice([2, 3]), y + rng.choice([2, 3])],
                fill=(
                    rng.randint(240, 255),
                    rng.randint(140, 220),
                    rng.randint(160, 240),
                    200,
                ),
            )


def draw_hood_sunburst_rgba(
    d: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    n_rays: int = 16,
    seed: int = 99,
) -> None:
    """Subtle rays on front hood band — reads through windshield without clutter."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    r_max = min(x1 - x0, y1 - y0) / 2 * 0.95
    for i in range(n_rays):
        ang = math.radians(i * (360 / n_rays))
        x2 = cx + math.cos(ang) * r_max
        y2 = cy + math.sin(ang) * r_max
        alpha = rng.randint(35, 70)
        col = (255, rng.randint(200, 240), rng.randint(180, 220), alpha)
        d.line([(cx, cy), (x2, y2)], fill=col, width=2)


def paste_subimage_rotated_180(
    layer: Image.Image,
    bbox: tuple[int, int, int, int],
    sub: Image.Image,
) -> None:
    """Paste `sub` into `bbox`, rotated 180° so it reads correctly when the panel is flipped in-game."""
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    sub180 = sub.rotate(180)
    sw, sh = sub180.size
    px = x0 + max(0, (bw - sw) // 2)
    py = y0 + max(0, (bh - sh) // 2)
    layer.paste(sub180, (px, py), sub180)


def draw_star_polygon(
    d: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float,
    fill: tuple[int, int, int, int],
    rotation_deg: float = 0.0,
) -> None:
    pts: list[tuple[float, float]] = []
    for i in range(10):
        ang = math.radians(rotation_deg + i * 36 - 90)
        rad = outer_r if i % 2 == 0 else outer_r * 0.42
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    d.polygon([(int(p[0]), int(p[1])) for p in pts], fill=fill)


def draw_rear_party_markers(
    d: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    seed: int,
) -> None:
    """Large stars for rear quarter visibility in chase cam."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    for _ in range(16):
        px = cx + rng.uniform(-(x1 - x0) * 0.38, (x1 - x0) * 0.38)
        py = cy + rng.uniform(-(y1 - y0) * 0.38, (y1 - y0) * 0.38)
        col = (
            rng.randrange(200, 255),
            rng.randrange(120, 220),
            rng.randrange(120, 220),
            235,
        )
        draw_star_polygon(d, px, py, rng.uniform(5.0, 11.0), col, rng.uniform(0, 360))


def main() -> None:
    bb = BBOXES
    mask = load_mask(TEMPLATE)
    w, h = mask.size
    img = Image.new("RGB", (w, h), (0, 0, 0))
    mk = mask.load()

    # Split top_mid: upper band ≈ frunk (Siamese leaves this mostly empty cream); lower = roof/cake.
    tm_x0, tm_y0, tm_x1, tm_y1 = bb["top_mid"]
    tm_h = tm_y1 - tm_y0
    # Siamese_Cat: only the bottom ~25–30% of top_mid has the busy hood graphic; the rest reads as frunk.
    frunk_h = max(int(0.72 * tm_h), 28)
    frunk_y1 = tm_y0 + frunk_h
    top_mid_frunk = (tm_x0, tm_y0, tm_x1, frunk_y1)
    top_mid_roof = (tm_x0, frunk_y1 + 1, tm_x1, tm_y1)

    fill_masked_gradient(img, mask, bb["top_strip"], (255, 120, 160), (255, 200, 100), True)
    fill_masked_gradient(img, mask, bb["fender_L"], (120, 200, 255), (200, 140, 255), True)
    fill_masked_gradient(img, mask, bb["fender_R"], (120, 200, 255), (200, 140, 255), True)
    fill_masked_gradient(img, mask, bb["mirror_l"], (120, 200, 255), (200, 140, 255), True)
    fill_masked_gradient(img, mask, bb["mirror_r"], (120, 200, 255), (200, 140, 255), True)
    fill_masked_gradient(img, mask, bb["top_mid"], (255, 248, 220), (255, 230, 180), True)
    fill_masked_gradient(img, mask, bb["door_L"], (255, 240, 245), (255, 210, 230), False)
    fill_masked_gradient(img, mask, bb["door_R"], (240, 255, 248), (200, 240, 255), False)
    rear_c1, rear_c2 = (180, 255, 200), (120, 220, 255)
    for key in REAR_CONTINUITY_KEYS:
        fill_masked_gradient(img, mask, bb[key], rear_c1, rear_c2, True)
    fill_masked_gradient(img, mask, bb["spine_L"], (40, 30, 55), (80, 50, 100), False)
    fill_masked_gradient(img, mask, bb["spine_R"], (40, 30, 55), (80, 50, 100), False)

    def in_bbox(x: int, y: int, b: tuple[int, int, int, int]) -> bool:
        bx0, by0, bx1, by1 = b
        return bx0 <= x <= bx1 and by0 <= y <= by1

    chase_zones = tuple(bb[k] for k in REAR_CONTINUITY_KEYS)
    confetti = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(confetti)
    rng = random.Random(42)

    def rand_in_bbox(b: tuple[int, int, int, int]) -> tuple[int, int]:
        bx0, by0, bx1, by1 = b
        for _ in range(80):
            x = rng.randrange(bx0, bx1 + 1)
            y = rng.randrange(by0, by1 + 1)
            if mk[x, y] >= 128:
                return x, y
        return rng.randrange(w), rng.randrange(h)

    for _ in range(380):
        x, y = rng.randrange(w), rng.randrange(h)
        if mk[x, y] < 128:
            continue
        if any(in_bbox(x, y, z) for z in chase_zones):
            continue
        sz = rng.choice([2, 3, 4])
        cd.rectangle(
            [x, y, x + sz, y + sz],
            fill=(
                rng.randrange(100, 255),
                rng.randrange(100, 255),
                rng.randrange(100, 255),
                rng.randrange(140, 220),
            ),
        )
    for _ in range(420):
        z = chase_zones[rng.randrange(len(chase_zones))]
        x, y = rand_in_bbox(z)
        if mk[x, y] < 128:
            continue
        sz = rng.choice([3, 5, 6])
        cd.rectangle(
            [x, y, x + sz, y + sz],
            fill=(
                rng.randrange(120, 255),
                rng.randrange(120, 255),
                rng.randrange(120, 255),
                rng.randrange(180, 245),
            ),
        )
    composite_rgba_under_mask(img, confetti, mask)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Roof deck (center): top-down cake — reads from above + chase-glance to roof.
    rx0_, ry0_, rx1_, ry1_ = top_mid_roof
    cx_cake = (rx0_ + rx1_) / 2
    cy_cake = (ry0_ + ry1_) / 2 + 2
    roof_h = max(1, ry1_ - ry0_)
    cake_scale = min(0.92, roof_h / 145.0)
    draw_top_down_cake(ld, cx_cake, cy_cake, cake_scale)
    composite_rgba_under_mask(img, layer, mask)

    try:
        # Front-facing islands in-game render upside-down vs PNG Y — text is drawn then rotated 180°.
        font_frunk = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
        font_strip = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 23)
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 27)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 23)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
    except OSError:
        font_frunk = font_strip = font_big = ImageFont.load_default()
        font_med = font_sm = font_big

    # Frunk (upper top_mid): sunburst + EN/PT — pasted flipped 180° for correct windshield read.
    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    fx0, fy0, fx1, fy1 = top_mid_frunk
    draw_hood_sunburst_rgba(ld, (fx0 + 10, fy0 + 6, fx1 - 10, fy1 - 4), n_rays=14, seed=88)
    composite_rgba_under_mask(img, layer, mask)

    mid_x = (fx0 + fx1) / 2
    pad = 16
    en_img = render_stacked_lines_image_rgba(
        ["Happy", "Birthday!"],
        font_frunk,
        fill=(255, 255, 255, 255),
        stroke=(180, 40, 110, 255),
        stroke_w=2,
        line_gap=4,
    )
    pt_img = render_stacked_lines_image_rgba(
        ["Feliz", "Aniversário!"],
        font_frunk,
        fill=(255, 255, 255, 255),
        stroke=(0, 95, 70, 255),
        stroke_w=2,
        line_gap=4,
    )
    clear_rgba(layer)
    paste_subimage_rotated_180(layer, (fx0 + pad, fy0 + 10, int(mid_x - 8), fy1 - 10), en_img)
    paste_subimage_rotated_180(layer, (int(mid_x + 8), fy0 + 10, fx1 - pad, fy1 - 10), pt_img)
    composite_rgba_under_mask(img, layer, mask)

    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    x0L, y0L, x1L, y1L = bb["spine_L"]
    draw_party_flags_vertical(
        ld, float(x0L + 2), float(y0L + 28), float(y1L - 28), float(x1L - x0L - 4), seed=11
    )
    x0R, y0R, x1R, y1R = bb["spine_R"]
    draw_party_flags_vertical(
        ld, float(x0R + 2), float(y0R + 28), float(y1R - 28), float(x1R - x0R - 4), seed=17
    )
    composite_rgba_under_mask(img, layer, mask)

    lx0, ly0, lx1, ly1 = bb["door_L"]
    rx0, ry0, rx1, ry1 = bb["door_R"]

    # Wavy ribbon + sprinkles across both doors (reads across the cabin split).
    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    draw_door_spanning_ribbon(ld, bb["door_L"], bb["door_R"], mask)
    composite_rgba_under_mask(img, layer, mask)

    # Treats centered on each door island.
    scoop_cx = (lx0 + lx1) / 2
    scoop_cy = (ly0 + ly1) / 2 + 6
    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    draw_strawberry_scoop(ld, scoop_cx, scoop_cy, 1.0)
    composite_rgba_under_mask(img, layer, mask)

    quindim_cx = (rx0 + rx1) / 2
    quindim_cy = (ry0 + ry1) / 2 + 6
    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    draw_quindim(ld, quindim_cx, quindim_cy, 1.0)
    composite_rgba_under_mask(img, layer, mask)

    # Front lip (top_strip): single line, flipped 180° — was upside-down in screenshots.
    strip_img = render_single_line_image_rgba(
        "Happy Birthday!",
        font_strip,
        fill=(255, 255, 255, 255),
        stroke=(160, 40, 100, 255),
        stroke_w=2,
    )
    clear_rgba(layer)
    sx0, sy0, sx1, sy1 = bb["top_strip"]
    paste_subimage_rotated_180(layer, (sx0 + 10, sy0 + 6, sx1 - 10, sy1 - 6), strip_img)
    composite_rgba_under_mask(img, layer, mask)

    # Chase cam: rear bumper message + big stars on rear quarters.
    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    bx0, by0, bx1, by1 = bb["bottom_mid"]
    draw_banner_in_bbox_rgba(
        ld,
        (bx0 + 6, by0 + 4, bx1 - 6, by1 - 4),
        "Feliz Aniversário!",
        font_med,
        fill=(255, 255, 240, 255),
        stroke=(20, 90, 70, 255),
        stroke_w=2,
    )
    composite_rgba_under_mask(img, layer, mask)

    clear_rgba(layer)
    ld = ImageDraw.Draw(layer)
    draw_rear_party_markers(ld, bb["rear_L"], seed=101)
    draw_rear_party_markers(ld, bb["rear_R"], seed=107)
    composite_rgba_under_mask(img, layer, mask)

    final = Image.new("RGB", (w, h), (0, 0, 0))
    fp = final.load()
    ip = img.load()
    for y in range(h):
        for x in range(w):
            if mk[x, y] >= 128:
                fp[x, y] = ip[x, y]

    out_path = os.path.join(DIR, "Happy_Birthday.png")
    final.save(out_path, optimize=True)
    sz = os.path.getsize(out_path)
    print("Wrote", out_path, f"({sz // 1024} KB)")


if __name__ == "__main__":
    main()

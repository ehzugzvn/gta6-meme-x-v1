#!/usr/bin/env python3
"""Compose meme.png (1080x1080) for the gta6-meme-x-01 v1 entry.

Scene: "Sick Note" — the make.fun ghost, in a Vice City / Leonida office at
sunset, hands its boss a big doctor's note diagnosing LEONIDA FEVER and
prescribing two weeks in Vice City for GTA 6 launch week. The ghost holds
its magenta star coin in its other hand.

Everything is drawn with PIL shapes so the file is fully reproducible:
    python3 tools/make_meme.py
writes meme.png at the repository root.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "meme.png")

BLACK = (18, 16, 24)
WHITE = (255, 255, 255)
MAGENTA = (236, 0, 140)
DARK_PURPLE = (46, 26, 71)
FRAME = (59, 43, 79)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FALLBACK_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size, fallback="DejaVuSans.ttf"):
    """Load a Liberation font, falling back to DejaVu if it is missing."""
    path = os.path.join(FONT_DIR, name)
    if not os.path.exists(path):
        path = os.path.join(FALLBACK_DIR, fallback)
    return ImageFont.truetype(path, size)


def bold(size):
    return font("LiberationSans-Bold.ttf", size, "DejaVuSans-Bold.ttf")


def regular(size):
    return font("LiberationSans-Regular.ttf", size, "DejaVuSans.ttf")


def italic(size):
    return font("LiberationSans-Italic.ttf", size, "DejaVuSans-Oblique.ttf")


def sparkle(draw, cx, cy, r, fill):
    """A four-pointed sparkle: tall star with concave sides (the ghost's eye)."""
    inner = r * 0.20
    pts = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rad = r if i % 2 == 0 else inner
        # Stretch vertically so the sparkle reads tall like the logo's eyes.
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang) * 1.25))
    draw.polygon(pts, fill=fill)


def star(draw, cx, cy, r, fill):
    """A classic five-pointed star (for the coin)."""
    inner = r * 0.45
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def vertical_gradient(img, top, bottom, y0, y1):
    """Paint a vertical colour gradient over rows y0..y1."""
    draw = ImageDraw.Draw(img)
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / span
        # Ease through a pink middle stop for a Vice City sunset feel.
        if t < 0.5:
            u = t * 2
            c = tuple(int(top[i] + (MAGENTA[i] - top[i]) * u * 0.55) for i in range(3))
            c = tuple(int(top[i] + ((255, 110, 160)[i] - top[i]) * u) for i in range(3))
        else:
            u = (t - 0.5) * 2
            c = tuple(int((255, 110, 160)[i] + (bottom[i] - (255, 110, 160)[i]) * u) for i in range(3))
        draw.line([(0, y), (SIZE, y)], fill=c)


def draw_palm(draw, base_x, base_y, height, lean, colour, width=13):
    """A simple palm silhouette: curved trunk plus arcing fronds."""
    top_x = base_x + lean
    top_y = base_y - height
    steps = 24
    prev = (base_x, base_y)
    for i in range(1, steps + 1):
        t = i / steps
        x = base_x + lean * t * t
        y = base_y - height * t
        draw.line([prev, (x, y)], fill=colour, width=width)
        prev = (x, y)
    for ang in (-160, -120, -80, -40, -5):
        rad = math.radians(ang)
        length = height * 0.42
        mid = (top_x + length * 0.55 * math.cos(rad),
               top_y + length * 0.35 * math.sin(rad) - height * 0.05)
        end = (top_x + length * math.cos(rad),
               top_y + length * 0.75 * math.sin(rad) + height * 0.16)
        draw.line([(top_x, top_y), mid], fill=colour, width=width - 3)
        draw.line([mid, end], fill=colour, width=width - 4)


def draw_background(img):
    """Sunset sky, office window frame, sun, sea band and palm silhouettes."""
    draw = ImageDraw.Draw(img)
    vertical_gradient(img, (255, 158, 94), (123, 75, 148), 185, SIZE)
    draw = ImageDraw.Draw(img)

    # Sea band low in the window.
    draw.rectangle([0, 520, SIZE, 640], fill=(64, 90, 160))

    # Sun low over the sea.
    draw.ellipse([700, 300, 900, 500], fill=(255, 224, 138))
    draw.ellipse([722, 322, 878, 478], fill=(255, 236, 170))

    # Palms silhouetted against the sunset.
    draw_palm(draw, 150, 660, 330, 60, DARK_PURPLE)
    draw_palm(draw, 965, 670, 360, -70, DARK_PURPLE)

    # Window frame with mullions over the whole scene.
    draw.rectangle([52, 208, 1028, 636], outline=FRAME, width=16)
    draw.line([(373, 208), (373, 636)], fill=FRAME, width=12)
    draw.line([(707, 208), (707, 636)], fill=FRAME, width=12)
    draw.line([(52, 422), (1028, 422)], fill=FRAME, width=12)

    # Warm interior floor below the window.
    draw.rectangle([0, 636, SIZE, SIZE], fill=(250, 214, 165))
    draw.rectangle([0, 636, SIZE, 652], fill=(233, 183, 120))


def draw_coin(draw, cx, cy, r):
    """The make.fun coin: magenta disc, black outline, white star."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAGENTA, outline=BLACK, width=8)
    star(draw, cx, cy, r * 0.52, WHITE)


def draw_ghost(img):
    """The make.fun ghost: white body, thick black outline, sparkle eyes,
    one round hand handing over the note, the other holding its coin."""
    draw = ImageDraw.Draw(img)
    gx0, gy0, gx1 = 168, 438, 472  # body box: left, dome top, right
    dome_bottom = 742
    body_bottom = 818

    # Filled body: dome + straight sides + three scallop bumps.
    draw.ellipse([gx0, gy0, gx1, dome_bottom], fill=WHITE)
    draw.rectangle([gx0, (gy0 + dome_bottom) // 2, gx1, body_bottom], fill=WHITE)
    for cx in (219, 320, 421):
        draw.ellipse([cx - 51, body_bottom - 51, cx + 51, body_bottom + 51], fill=WHITE)

    # Thick black outline: dome arc, side lines, scalloped bottom arcs.
    draw.arc([gx0, gy0, gx1, dome_bottom], start=180, end=360, fill=BLACK, width=11)
    draw.line([(gx0, (gy0 + dome_bottom) // 2), (gx0, body_bottom)], fill=BLACK, width=11)
    draw.line([(gx1, (gy0 + dome_bottom) // 2), (gx1, body_bottom)], fill=BLACK, width=11)
    for cx in (219, 320, 421):
        draw.arc([cx - 51, body_bottom - 51, cx + 51, body_bottom + 51],
                 start=0, end=180, fill=BLACK, width=11)

    # Sparkle eyes and a small worried-sick mouth.
    sparkle(draw, 264, 586, 34, BLACK)
    sparkle(draw, 376, 586, 34, BLACK)
    draw.arc([294, 622, 346, 668], start=20, end=160, fill=BLACK, width=7)
    # Fever cheeks.
    draw.ellipse([206, 628, 240, 656], fill=(255, 150, 170))
    draw.ellipse([400, 628, 434, 656], fill=(255, 150, 170))
    # A little thermometer poking from the mouth corner.
    draw.line([(346, 648), (392, 676)], fill=(200, 30, 40), width=9)
    draw.ellipse([384, 664, 404, 684], fill=(200, 30, 40), outline=BLACK, width=3)

    # Coin in the ghost's left hand (viewer's left), hand circle over it.
    draw_coin(draw, 128, 690, 56)
    draw.ellipse([150, 716, 206, 772], fill=WHITE, outline=BLACK, width=8)

    # Right hand reaching out to hand over the note card, gripping its
    # left edge halfway down so it never covers the card's title.
    draw.ellipse([420, 712, 488, 780], fill=WHITE, outline=BLACK, width=8)


def draw_boss(draw):
    """A stern boss silhouette at the right edge, arms-crossed energy."""
    colour = (36, 20, 51)
    draw.ellipse([952, 452, 1052, 552], fill=colour)               # head
    draw.rectangle([918, 540, 1080, 730], fill=colour)             # shoulders
    # Stern eyebrows.
    draw.line([(968, 492), (992, 500)], fill=WHITE, width=5)
    draw.line([(1036, 492), (1012, 500)], fill=WHITE, width=5)


def draw_note_card(img):
    """The big doctor's note the ghost is handing over."""
    # Slight rotation for a hand-held feel: draw on a layer, rotate, paste.
    layer = Image.new("RGBA", (560, 470), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([14, 14, 546, 456], fill=(0, 0, 0, 70))            # shadow
    d.rectangle([0, 0, 532, 442], fill=WHITE, outline=BLACK, width=6)
    d.line([(28, 84), (504, 84)], fill=MAGENTA, width=5)

    def text(x, y, s, fnt, fill=BLACK, anchor="la"):
        d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)

    text(280, 16, "DOCTOR'S NOTE", bold(52), MAGENTA, "ma")
    text(30, 104, "Patient: a loyal GTA fan", regular(37))
    text(30, 158, "Diagnosis:", bold(40))
    text(30, 204, "LEONIDA FEVER", bold(56), (200, 30, 40))
    text(30, 280, "Prescription: 2 weeks in", regular(36))
    text(30, 328, "Vice City. No work. No emails.", regular(36))
    text(502, 384, "— Dr. Ghost", italic(38), (90, 90, 90), "ra")

    layer = layer.rotate(2.5, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (470, 552), layer)


def draw_caption(draw):
    """Black band on top with the big Impact-style caption."""
    draw.rectangle([0, 0, SIZE, 185], fill=(10, 10, 14))
    draw.rectangle([0, 185, SIZE, 193], fill=MAGENTA)
    fnt = bold(63)
    draw.text((SIZE // 2, 14), "MY DOCTOR'S NOTE FOR", font=fnt, fill=WHITE,
              anchor="ma", stroke_width=2, stroke_fill=BLACK)
    draw.text((SIZE // 2, 94), "GTA 6 LAUNCH WEEK", font=fnt, fill=(255, 214, 64),
              anchor="ma", stroke_width=2, stroke_fill=BLACK)


def draw_desk(draw):
    """Desk front along the bottom, branded make.fun in the scene."""
    draw.rectangle([0, 1018, SIZE, SIZE], fill=(59, 43, 79))
    draw.rectangle([0, 1018, SIZE, 1026], fill=MAGENTA)
    draw.text((36, 1032), "make.fun", font=bold(38), fill=WHITE)
    draw.text((1044, 1036), "EST. LEONIDA", font=bold(26),
              fill=(255, 214, 64), anchor="ra")


def main():
    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    draw_background(img)
    draw = ImageDraw.Draw(img)
    draw_boss(draw)
    draw_note_card(img)
    draw_ghost(img)
    draw = ImageDraw.Draw(img)
    draw_desk(draw)
    draw_caption(draw)
    img.save(OUT)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()


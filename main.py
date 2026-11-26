#!/usr/bin/env python3
"""News-image entry for 25 November 2026.

Draws a 1024x1024 newspaper front page that sums up the world's news of
Wednesday 25 November 2026: six verified stories, each readable from the
image alone. Pure Python 3 standard library, no network, no randomness,
no clock: two runs write byte-identical files.

Run:  python3 main.py        -> writes entry.png next to this file.
"""

import binascii
import math
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
CARD = (255, 255, 255)
INK = (22, 32, 52)
NAVY = (18, 28, 48)
RED = (178, 34, 24)
BLUE = (29, 78, 137)
TEAL = (14, 124, 123)
GOLD = (154, 123, 30)
GREEN = (46, 125, 50)
CREAM = (250, 246, 236)
GREY = (74, 82, 100)
LIGHT = (238, 232, 216)
ORANGE = (214, 106, 24)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 bits, '#' = ink. Written from scratch for this
# entry; only capitals, digits and the punctuation the copy needs.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10011", "10101", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ")": ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    "%": ("11001", "11010", "00100", "01000", "01011", "10011", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
}

GLYPH_W, GLYPH_H = 5, 7


def text_width(text, scale):
    """Pixel width of text at the given scale (1px tracking per glyph)."""
    return len(text) * (GLYPH_W * scale + scale) - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    advance = GLYPH_W * scale + scale
    limit = max_width // advance
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self._set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self._set(x, y, color)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self._set(xx, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            for xx in range(cx - dx, cx + dx + 1):
                self._set(xx, yy, color)

    def triangle(self, pts, color):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self._set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(GLYPH_H):
                bits = glyph[row]
                for col in range(GLYPH_W):
                    if bits[col] == "1":
                        self.rect(x + col * scale, y + row * scale,
                                  scale, scale, color)
            x += (GLYPH_W + 1) * scale

    def text_center(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)

    def write_png(self, path):
        def chunk(kind, data):
            body = kind + data
            return (struct.pack(">I", len(data)) + body +
                    struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF))

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
               chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
               chunk(b"IEND", b""))
        Path(path).write_bytes(png)


# ------------------------------------------------------------------- icons
# Each icon is drawn in white/cream inside a 72x72 coloured square whose
# top-left corner is (bx, by). Simple flat shapes, one per story.

def icon_tower(c, bx, by):
    c.rect(bx + 28, by + 16, 16, 44, CREAM)          # tower slab
    c.rect(bx + 34, by + 8, 4, 8, CREAM)            # antenna
    c.disc(bx + 36, by + 6, 3, ORANGE)              # beacon
    for wy in (24, 32, 40, 48):
        c.rect(bx + 32, by + wy, 8, 3, RED)         # lit windows
    c.triangle([(bx + 52, by + 10), (bx + 60, by + 18), (bx + 52, by + 26)],
               ORANGE)                              # blast flare
    c.disc(bx + 56, by + 18, 4, CREAM)


def icon_drone(c, bx, by):
    c.rect(bx + 26, by + 30, 20, 12, CREAM)         # body
    c.disc(bx + 36, by + 36, 4, RED)                # camera eye
    for (rx, ry) in ((14, 20), (50, 20), (14, 48), (50, 48)):
        c.rect(bx + rx, by + ry, 12, 3, CREAM)      # rotors
        c.line(bx + 30, by + 34, bx + rx + 6, by + ry + 1, CREAM)
    c.line(bx + 36, by + 42, bx + 36, by + 58, CREAM)
    c.triangle([(bx + 30, by + 52), (bx + 42, by + 52), (bx + 36, by + 62)],
               ORANGE)                              # falling


def icon_chip(c, bx, by):
    c.rect(bx + 20, by + 20, 32, 32, CREAM)         # die
    c.rect(bx + 29, by + 29, 14, 14, TEAL)          # core
    for i in range(3):                              # pins
        c.rect(bx + 24 + i * 10, by + 12, 5, 8, CREAM)
        c.rect(bx + 24 + i * 10, by + 52, 5, 8, CREAM)
        c.rect(bx + 12, by + 24 + i * 10, 8, 5, CREAM)
        c.rect(bx + 52, by + 24 + i * 10, 8, 5, CREAM)


def icon_rocket(c, bx, by):
    c.triangle([(bx + 36, by + 8), (bx + 27, by + 26), (bx + 45, by + 26)],
               CREAM)                               # nose + body top
    c.rect(bx + 27, by + 26, 18, 22, CREAM)         # body
    c.triangle([(bx + 27, by + 34), (bx + 16, by + 52), (bx + 27, by + 48)],
               CREAM)                               # left fin
    c.triangle([(bx + 45, by + 34), (bx + 56, by + 52), (bx + 45, by + 48)],
               CREAM)                               # right fin
    c.disc(bx + 36, by + 34, 4, GOLD)               # window
    c.triangle([(bx + 30, by + 48), (bx + 42, by + 48), (bx + 36, by + 62)],
               ORANGE)                              # flame
    c.disc(bx + 14, by + 14, 2, CREAM)              # stars
    c.disc(bx + 58, by + 20, 2, CREAM)


def icon_blast(c, bx, by):
    cx, cy = bx + 36, by + 36
    for k in range(8):                              # 8 spikes
        ang = k * 0.785398
        tx, ty = int(cx + 30 * math.cos(ang)), int(cy + 30 * math.sin(ang))
        px, py = int(cx + 8 * math.cos(ang + 0.4)), int(cy + 8 * math.sin(ang + 0.4))
        qx, qy = int(cx + 8 * math.cos(ang - 0.4)), int(cy + 8 * math.sin(ang - 0.4))
        c.triangle([(cx, cy), (tx, ty), (px, py)], ORANGE)
        c.triangle([(cx, cy), (tx, ty), (qx, qy)], ORANGE)
    c.disc(cx, cy, 12, CREAM)
    c.disc(cx, cy, 6, RED)


def icon_balloon(c, bx, by):
    c.ellipse(bx + 36, by + 26, 18, 17, CREAM)      # balloon
    c.line(bx + 26, by + 40, bx + 32, by + 54, CREAM)
    c.line(bx + 46, by + 40, bx + 40, by + 54, CREAM)
    c.rect(bx + 30, by + 54, 12, 10, ORANGE)        # basket
    c.triangle([(bx + 36, by + 6), (bx + 36, by + 12), (bx + 44, by + 9)],
               ORANGE)                              # pennant
    c.disc(bx + 14, by + 16, 2, CREAM)
    c.disc(bx + 58, by + 44, 2, CREAM)


# ------------------------------------------------------------------ stories
# Six stories from Wednesday 25 November 2026, each verified against a
# real news source dated that day (see NEWS.md for the sources).
STORIES = [
    dict(kicker="MIDDLE EAST", color=RED, icon=icon_tower,
         headline="HOUTHIS STRIKE RIYADH TOWER",
         body="Houthi attack hits Riyadh's tallest tower, wounding 11. "
              "Saudi-led coalition hits back at Hodeidah port."),
    dict(kicker="MIDDLE EAST", color=BLUE, icon=icon_drone,
         headline="IRAN CLAIMS TWO US DRONES DOWN",
         body="Iran says it shot down a US MQ-9 and a Lucas drone over "
              "the Strait of Hormuz."),
    dict(kicker="TECH", color=TEAL, icon=icon_chip,
         headline="HUAWEI CONVICTED IN US TRIAL",
         body="Chinese tech giant found guilty of fraud in a sprawling US "
              "criminal case over its Iran business."),
    dict(kicker="SPACE", color=GOLD, icon=icon_rocket,
         headline="PAKISTAN'S FIRST ASTRONAUT",
         body="China's Shenzhou-24 carries Pakistan's first astronaut to "
              "its space station."),
    dict(kicker="USA", color=NAVY, icon=icon_blast,
         headline="ARMY BLOWS UP 5 TONS OF EXPLOSIVES",
         body="US Army detonates its entire lead-azide stockpile in Iowa; "
              "a town evacuated, blast declared a success."),
    dict(kicker="USA", color=GREEN, icon=icon_balloon,
         headline="MACY'S PARADE POSTPONED",
         body="Thanksgiving parade delayed for the first time ever as a "
              "huge storm bears down on the US East Coast."),
]


def draw_panel(c, x, y, story):
    w, h = 480, 240
    c.rect(x, y, w, h, CARD)
    c.rect(x, y, w, 6, story["color"])              # colour bar
    # thin ink frame
    c.hline(x, y + h - 1, w, INK)
    c.vline(x, y, h, INK)
    c.vline(x + w - 1, y, h, INK)
    # icon square, top right
    ix, iy = x + w - 18 - 72, y + 16
    c.rect(ix, iy, 72, 72, story["color"])
    story["icon"](c, ix, iy)
    # kicker
    c.text(x + 18, y + 22, story["kicker"], 2, story["color"])
    c.hline(x + 18, y + 44, text_width(story["kicker"], 2), story["color"])
    # headline, two lines max
    lines = wrap_text(story["headline"], w - 36, 3)[:2]
    hy = y + 100
    for line in lines:
        c.text(x + 18, hy, line, 3, INK)
        hy += 27
    # summary, three lines max (font holds capitals only: normalise here)
    blines = wrap_text(story["body"].upper(), w - 36, 2)[:3]
    by = hy + 10
    for line in blines:
        c.text(x + 18, by, line, 2, GREY)
        by += 19


def main():
    c = Canvas(W, H, PAPER)
    # masthead
    c.rect(0, 0, W, 140, NAVY)
    c.text_center(28, "THE WORLD IN ONE IMAGE", 6, CREAM)
    c.text_center(88, "WEDNESDAY, 25 NOVEMBER 2026", 3, (212, 175, 55))
    c.rect(0, 140, W, 6, RED)
    # six story panels, 2 columns x 3 rows
    for i, story in enumerate(STORIES):
        px = 24 + (i % 2) * (480 + 16)
        py = 164 + (i // 2) * (240 + 16)
        draw_panel(c, px, py, story)
    # footer strip
    c.rect(0, 932, W, 92, NAVY)
    c.text_center(946,
                  "MARKETS: BITCOIN BELOW $58,000 | US INFLATION 3.8% | "
                  "NVIDIA ON DOWNGRADE WATCH", 2, CREAM)
    c.text_center(976,
                  "SOURCES: REUTERS - AP - NYT - BBC - THE GUARDIAN",
                  2, (212, 175, 55))
    out = Path(__file__).resolve().parent / "entry.png"
    c.write_png(out)
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render the news-image-20261120 entry: one front-page image summing up the
world news of Friday 20 November 2026.

Deterministic by construction: fixed layout, fixed strings, fixed fonts, no
randomness, no timestamps, no network. Run twice and the PNG bytes are
identical. Output: entry.png, 1024x1024, well under the 1 MiB cap.

Stories (all reported on Friday 20 November 2026, verified against live
news digests that day):
  1. ICJ rules Myanmar committed genocide against the Rohingya (9-6 vote,
     first such finding against a state; Gambia case, 2017 crackdown).
  2. Trump, Xi and Putin hold their first three-way summit in Shenzhen and
     sign a four-point joint declaration (Ukraine and Iran unmentioned).
  3. Markets tumble: S&P 500 -2% for a fifth straight day, Nikkei -4.8%,
     gold -4.2%.
  4. Houthi missile damages the PIF tower in Riyadh's financial district;
     no injuries reported.
  5. Russian barrage hits Kyiv, damaging embassies and a cathedral; Ukraine
     strikes the Kerch Bridge again.
  6. COP31 draft in Antalya drops the fossil-fuel phase-out and net-zero
     dates on the talks' final day.
  7. GTA 6 tops $2.3 billion in sales, the biggest entertainment launch ever.
  8. Voyager 1 reaches one light-day from Earth; BepiColombo enters
     Mercury orbit.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (250, 246, 236)
INK = (27, 42, 74)
NAVY = (20, 33, 61)
NAVY_LT = (38, 56, 96)
RED = (179, 39, 30)
GOLD = (201, 162, 39)
MUTED = (90, 100, 114)
PANEL = (255, 255, 255)
BORDER = (216, 210, 192)
TEAL = (14, 124, 123)
ICON_BG = (238, 240, 243)

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, f, max_w, fill, leading=None):
    lh = leading or int(f.size * 1.22)
    lines = wrap(draw, text, f, max_w)
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y, len(lines)


def kicker(draw, x, y, text, color=RED, size=19):
    """Small red bar + letterspaced kicker."""
    draw.rectangle([x, y + 2, x + 30, y + 8], fill=color)
    draw.text((x + 38, y - 2), text, font=font(DEJAVU_B, size), fill=color)
    return y + 26


# ---------------- pictograms (flat, geometric, two colours max) -------------

def icon_scales(d, cx, cy, s, c):
    # scales of justice: post, beam, two pans
    d.line([cx, cy - s, cx, cy + s], fill=c, width=max(3, s // 12))
    d.line([cx - s, cy - s + 8, cx + s, cy - s + 8], fill=c, width=max(3, s // 12))
    d.ellipse([cx - 4, cy - s - 4, cx + 4, cy - s + 4], fill=c)
    for sx in (-s, s):
        d.line([sx + cx, cy - s + 8, sx + cx, cy - s + s // 2], fill=c, width=3)
        d.polygon([(sx + cx - s // 2, cy - s + s // 2),
                   (sx + cx + s // 2, cy - s + s // 2),
                   (sx + cx, cy + s // 3)], fill=c)
    d.rectangle([cx - s // 2, cy + s - 4, cx + s // 2, cy + s], fill=c)


def icon_flags(d, cx, cy, s, c):
    # three small flags on poles
    cols = [RED, NAVY_LT, GOLD]
    for i, col in enumerate(cols):
        x0 = cx - s + i * (2 * s // 3)
        d.line([x0, cy - s, x0, cy + s], fill=c, width=3)
        d.rectangle([x0, cy - s, x0 + s // 2 + 6, cy - s // 3], fill=col)


def icon_chart(d, cx, cy, s, c):
    d.line([cx - s, cy + s, cx + s, cy + s], fill=c, width=3)
    d.line([cx - s, cy + s, cx - s, cy - s], fill=c, width=3)
    pts = [(cx - s + 4, cy - s // 2), (cx - s // 3, cy - s // 6),
           (cx + s // 6, cy + s // 6), (cx + s - 6, cy + s - 8)]
    d.line(pts, fill=RED, width=5, joint="curve")
    d.polygon([(cx + s - 6, cy + s - 8), (cx + s - 18, cy + s - 2),
               (cx + s - 2, cy + s - 20)], fill=RED)


def icon_tower(d, cx, cy, s, c):
    d.rectangle([cx - s // 2, cy - s, cx + s // 2, cy + s], fill=c)
    for r in range(4):
        for col in range(2):
            d.rectangle([cx - s // 2 + 6 + col * (s // 2 - 2),
                         cy - s + 10 + r * (s // 2 - 4),
                         cx - s // 2 + 6 + col * (s // 2 - 2) + 8,
                         cy - s + 10 + r * (s // 2 - 4) + 8], fill=PAPER)
    for dx, dy, r in ((-s // 2, -s - 6, 7), (0, -s - 12, 9), (s // 2, -s - 4, 6)):
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                  fill=(150, 150, 150))


def icon_dome(d, cx, cy, s, c):
    d.arc([cx - s, cy - s, cx + s, cy + s // 2], 180, 360, fill=c, width=5)
    d.line([cx, cy - s - 12, cx, cy - s + 2], fill=c, width=4)
    d.line([cx - 8, cy - s - 6, cx + 8, cy - s - 6], fill=c, width=4)
    d.rectangle([cx - s, cy + s // 2 - 4, cx + s, cy + s], fill=c)
    d.rectangle([cx - 8, cy + s // 2 + 8, cx + 8, cy + s], fill=PAPER)


def icon_globe(d, cx, cy, s, c):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=c, width=4)
    d.ellipse([cx - s // 2, cy - s, cx + s // 2, cy + s], outline=c, width=3)
    d.line([cx - s, cy, cx + s, cy], fill=c, width=3)
    d.arc([cx - s, cy - s // 2, cx + s, cy + s // 2], 200, 340, fill=TEAL, width=5)


def icon_controller(d, cx, cy, s, c):
    d.rounded_rectangle([cx - s, cy - s // 2, cx + s, cy + s // 2],
                        radius=12, fill=c)
    d.rectangle([cx - s + 10, cy - 4, cx - s + 26, cy + 4], fill=PAPER)
    d.rectangle([cx - s + 14, cy - 8, cx - s + 22, cy + 8], fill=PAPER)
    for dx, dy in ((s - 22, -8), (s - 12, 6)):
        d.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5],
                  fill=GOLD)


def icon_space(d, cx, cy, s, c):
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=c)
    d.line([cx, cy - 8, cx, cy - s], fill=c, width=3)
    d.ellipse([cx - 3, cy - s - 3, cx + 3, cy - s + 3], fill=RED)
    d.rectangle([cx - s, cy - 4, cx - 12, cy + 4], fill=NAVY_LT)
    d.rectangle([cx + 12, cy - 4, cx + s, cy + 4], fill=NAVY_LT)
    for dx, dy in ((-s + 4, -s + 8), (s - 6, -s + 14), (s - 16, s - 10)):
        d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                  fill=GOLD)


def icon_box(d, x, y, size, fn, color):
    d.rounded_rectangle([x, y, x + size, y + size], radius=10, fill=ICON_BG)
    fn(d, x + size // 2, y + size // 2, size // 3, color)


# ---------------- layout ----------------------------------------------------

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 148], fill=NAVY)
    f_small = font(DEJAVU_B, 24)
    t = "THE WORLD IN ONE DAY"
    d.text(((W - text_w(d, t, f_small)) / 2, 14), t, font=f_small, fill=GOLD)
    f_date = font(DEJAVU_B, 58)
    t = "FRIDAY 20 NOVEMBER 2026"
    d.text(((W - text_w(d, t, f_date)) / 2, 44), t, font=f_date, fill=(255, 255, 255))
    d.rectangle([232, 126, 792, 130], fill=GOLD)

    def panel(x0, y0, x1, y1):
        d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=PANEL,
                            outline=BORDER, width=2)

    # ---- Lead row ----
    LY, LH = 164, 322
    # Lead 1: ICJ genocide ruling
    panel(20, LY, 616, LY + LH)
    x, y = 44, LY + 22
    icon_box(d, 616 - 24 - 64, LY + 22, 64, icon_scales, INK)
    y = kicker(d, x, y, "THE HAGUE  ·  JUSTICE")
    y, _ = draw_wrapped(d, x, y + 8, "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
                        font(DEJAVU_B, 34), 596 - 48 - 88, INK, leading=42)
    draw_wrapped(d, x, y + 10,
                 "The Hague rules 9–6: the first genocide verdict against "
                 "a state, over the 2017 Rohingya crackdown.",
                 font(DEJAVU, 24), 596 - 48, MUTED, leading=30)

    # Lead 2: Shenzhen summit
    panel(632, LY, 1004, LY + LH)
    x, y = 656, LY + 22
    icon_box(d, 1004 - 24 - 64, LY + 22, 64, icon_flags, INK)
    y = kicker(d, x, y, "SHENZHEN  ·  SUMMIT", size=18)
    y, _ = draw_wrapped(d, x, y + 8, "TRUMP, XI, PUTIN SIGN PEACE PACT",
                        font(DEJAVU_B, 34), 372 - 48 - 88, INK, leading=42)
    draw_wrapped(d, x, y + 10,
                 "First three-way summit ends in a four-point declaration. "
                 "Ukraine and Iran go unmentioned.",
                 font(DEJAVU, 25), 372 - 48, MUTED, leading=32)

    # ---- Middle row: three panels ----
    MY, MH = 502, 236
    mids = [
        (20, 346, "NEW YORK  ·  MARKETS", "MARKETS TUMBLE WORLDWIDE",
         "S&P 500 −2% for a fifth day; Nikkei −4.8%; gold −4.2%.",
         icon_chart, RED),
        (356, 668, "RIYADH  ·  CONFLICT", "MISSILE HITS RIYADH TOWER",
         "Houthi strike damages the PIF tower; no injuries.",
         icon_tower, INK),
        (678, 1004, "KYIV  ·  UKRAINE WAR", "RUSSIAN BARRAGE HITS KYIV",
         "Embassies and a cathedral damaged; Ukraine hits the Kerch "
         "Bridge again.", icon_dome, INK),
    ]
    for x0, x1, kick, head, deck, icon, icol in mids:
        panel(x0, MY, x1, MY + MH)
        x, y = x0 + 22, MY + 18
        y = kicker(d, x, y, kick)
        icon_box(d, x, y + 6, 56, icon, icol)
        hy, _ = draw_wrapped(d, x + 68, y + 6, head, font(DEJAVU_B, 26),
                             x1 - x0 - 44 - 68, INK, leading=30)
        draw_wrapped(d, x, max(hy, y + 6 + 56) + 8, deck, font(DEJAVU, 19),
                     x1 - x0 - 44, MUTED, leading=24)

    # ---- Bottom row: three panels ----
    BY, BH = 754, 202
    bots = [
        (20, 346, "ANTALYA  ·  CLIMATE", "CLIMATE DEAL DROPS FOSSIL-FUEL PHASE-OUT",
         "Draft omits net-zero dates on the final day.",
         icon_globe, TEAL),
        (356, 668, "WORLDWIDE  ·  CULTURE", "GTA 6 TOPS $2.3 BILLION",
         "Biggest entertainment launch ever, after 13 years.",
         icon_controller, INK),
        (678, 1004, "DEEP SPACE  ·  SCIENCE", "VOYAGER 1: ONE LIGHT-DAY OUT",
         "26 billion km from Earth; BepiColombo reaches Mercury.",
         icon_space, INK),
    ]
    for x0, x1, kick, head, deck, icon, icol in bots:
        panel(x0, BY, x1, BY + BH)
        x, y = x0 + 22, BY + 16
        y = kicker(d, x, y, kick, size=17)
        y, _ = draw_wrapped(d, x, y + 4, head, font(DEJAVU_B, 24),
                            x1 - x0 - 44, INK, leading=29)
        draw_wrapped(d, x, y + 6, deck, font(DEJAVU, 21),
                     x1 - x0 - 44, MUTED, leading=25)

    # ---- Footer ----
    f_foot = font(DEJAVU_B, 21)
    t = "All stories reported on Friday 20 November 2026"
    d.text(((W - text_w(d, t, f_foot)) / 2, 972), t, font=f_foot, fill=INK)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()

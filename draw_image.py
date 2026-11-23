#!/usr/bin/env python3
"""Render the 22 November 2026 world-news broadsheet (1024x1024, deterministic).

Dense newspaper layout: masthead, ticker, lead row (Bahrain hero + COP31),
two 3-cell grid rows for the locked core 7, an "also on Sunday" strip of
12 verified additions, a UTC timeline, and a footer. Every story is a
verified 22 November 2026 event; no casualty/missing numbers anywhere.

Writes /output/entry.png directly (no temp file), chmod 0644, then reads it
back and prints the sha256. Deterministic: same input -> byte-identical PNG.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

OUT = "/output/entry.png"
W = H = 1024
MARGIN = 24

PAPER = (245, 240, 225)
INK = (24, 24, 24)
FAINT = (105, 100, 88)
RED = (150, 24, 24)
BLUE = (28, 68, 110)
GREEN = (32, 92, 52)
GOLD = (146, 106, 28)
DARK = (32, 32, 32)
RULE = (150, 142, 122)
CELL = (250, 246, 234)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, f):
    return draw.textlength(text, font=f)


def fit(draw, text, path, size, max_w):
    """Largest font size <= `size` that fits `max_w` (deterministic)."""
    while size > 8 and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(draw, text, f, max_w):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, y, text, f, fill=INK, x0=0, x1=W):
    w = text_w(draw, text, f)
    draw.text(((x0 + x1 - w) / 2, y), text, font=f, fill=fill)


def rule(draw, y, x0=MARGIN, x1=W - MARGIN, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag_chip(draw, x, y, text, fill):
    """Small uppercase region tag chip; returns width used."""
    f = font(SANS_B, 13)
    tw = text_w(draw, text, f)
    pad = 7
    draw.rectangle([x, y, x + tw + 2 * pad, y + 20], fill=fill)
    draw.text((x + pad, y + 3), text, font=f, fill=(255, 255, 255))
    return tw + 2 * pad


def panel(draw, x, y, w, h, tag, tag_fill, label, label_size, sub, sub_size,
          icon=None):
    """One story cell: border, tag chip, bold label, sub-line, optional icon."""
    draw.rectangle([x, y, x + w, y + h], fill=CELL, outline=RULE, width=1)
    tag_chip(draw, x + 10, y + 9, tag, tag_fill)
    lx, lw = x + 10, w - 20
    lf = fit(draw, label, SANS_B, label_size, lw)
    lines = wrap(draw, label, lf, lw)
    ly = y + 38
    for line in lines:
        draw.text((lx, ly), line, font=lf, fill=INK)
        ly += lf.size + 3
    sf = fit(draw, sub, SANS, sub_size, lw)
    for line in wrap(draw, sub, sf, lw):
        draw.text((lx, ly), line, font=sf, fill=(58, 58, 58))
        ly += sf.size + 3
    if icon:
        icon(draw, x + w - 52, y + h - 46)


def flame(draw, x, y):
    """Small flame pictogram."""
    draw.polygon([(x + 14, y + 34), (x + 4, y + 18), (x + 12, y + 14),
                  (x + 10, y + 4), (x + 20, y + 12), (x + 26, y + 6),
                  (x + 26, y + 18), (x + 32, y + 14), (x + 24, y + 34)],
                 fill=(196, 64, 16))
    draw.polygon([(x + 14, y + 34), (x + 12, y + 24), (x + 18, y + 18),
                  (x + 22, y + 26)], fill=(232, 164, 32))


def planet(draw, x, y):
    """Small ringed planet pictogram."""
    draw.ellipse([x + 6, y + 6, x + 30, y + 30], fill=(120, 110, 96),
                 outline=INK, width=1)
    draw.ellipse([x + 2, y + 14, x + 34, y + 22], outline=GOLD, width=2)


def ship(draw, x, y):
    """Small tanker silhouette pictogram."""
    draw.polygon([(x, y + 22), (x + 40, y + 22), (x + 34, y + 32),
                  (x + 6, y + 32)], fill=DARK)
    draw.rectangle([x + 24, y + 12, x + 32, y + 22], fill=DARK)
    draw.rectangle([x + 8, y + 16, x + 14, y + 22], fill=DARK)
    draw.polygon([(x + 12, y + 12), (x + 16, y + 2), (x + 20, y + 12)],
                 fill=(196, 64, 16))


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    draw_centered(d, 14, "T H E   W O R L D   I N   O N E   D A Y",
                  font(SANS_B, 15), fill=FAINT)
    draw_centered(d, 34, "Sunday 22 November 2026",
                  font(SERIF, 58), fill=INK)
    draw_centered(d, 98, "20 STORIES  •  9 REGIONS  •  EVERY ONE DATED "
                  "SUNDAY 22 NOVEMBER 2026", font(SANS_B, 14), fill=FAINT)
    rule(d, 118, width=2)

    # ---- Ticker ----
    d.rectangle([MARGIN, 124, W - MARGIN, 148], fill=DARK)
    ticker = ("IRAN STRIKES BAHRAIN   •   COP31 COLLAPSES   •   "
              "DRONES HIT KHARTOUM   •   BEPICOLOMBO ORBITS MERCURY")
    tf = fit(d, ticker, SANS_B, 15, W - 2 * MARGIN - 16)
    draw_centered(d, 129, ticker, tf, fill=(245, 240, 225),
                  x0=MARGIN, x1=W - MARGIN)

    # ---- Lead row: Bahrain hero + COP31 ----
    y0 = 156
    hero_w, cop_w = 612, 352
    hx, cx = MARGIN, MARGIN + hero_w + 12
    # Hero
    d.rectangle([hx, y0, hx + hero_w, y0 + 200], fill=CELL,
                outline=RULE, width=1)
    tag_chip(d, hx + 12, y0 + 10, "MIDDLE EAST  •  GULF  •  CONFLICT", RED)
    hf = fit(d, "IRAN STRIKES BAHRAIN", SANS_B, 46, hero_w - 24)
    ly = y0 + 40
    for line in wrap(d, "IRAN STRIKES BAHRAIN", hf, hero_w - 24):
        d.text((hx + 12, ly), line, font=hf, fill=INK)
        ly += hf.size + 4
    sf = fit(d, "Iran claims radars hit — factory burns", SANS, 21,
             hero_w - 24)
    for line in wrap(d, "Iran claims radars hit — factory burns", sf,
                     hero_w - 24):
        d.text((hx + 12, ly), line, font=sf, fill=(58, 58, 58))
        ly += sf.size + 4
    d.text((hx + 12, y0 + 162),
           "Bahrain reports an attack on an industrial site",
           font=font(SANS, 15), fill=FAINT)
    ship(d, hx + hero_w - 96, y0 + 146)
    # COP31
    d.rectangle([cx, y0, cx + cop_w, y0 + 200], fill=CELL,
                outline=RULE, width=1)
    tag_chip(d, cx + 10, y0 + 10, "GLOBAL  •  CLIMATE", GREEN)
    cf = fit(d, "COP31 COLLAPSES", SANS_B, 34, cop_w - 20)
    ly = y0 + 40
    for line in wrap(d, "COP31 COLLAPSES", cf, cop_w - 20):
        d.text((cx + 10, ly), line, font=cf, fill=INK)
        ly += cf.size + 4
    sf2 = fit(d, "EU rejects pact — no deal", SANS, 19, cop_w - 20)
    for line in wrap(d, "EU rejects pact — no deal", sf2, cop_w - 20):
        d.text((cx + 10, ly), line, font=sf2, fill=(58, 58, 58))
        ly += sf2.size + 4
    d.text((cx + 10, y0 + 162), "Longest COP ever — no deal since 2009",
           font=font(SANS, 15), fill=FAINT)

    # ---- Grid rows: core 7 (rows of 3) ----
    gw = (W - 2 * MARGIN - 24) // 3
    gy1, gh = 366, 172
    cells_a = [
        ("EUROPE  •  UKRAINE", BLUE, "DRONE HITS KYIV FLATS",
         "Block collapses — rescuers search rubble", None),
        ("MIDDLE EAST", RED, "SETTLERS TORCH WEST BANK",
         "12 cars burned — Eisenkot condemns", flame),
        ("AFRICA  •  SUDAN", (96, 64, 32), "DRONES HIT KHARTOUM",
         "UN building damaged — staff inside", None),
    ]
    cells_b = [
        ("SPACE  •  ESA", BLUE, "BEPICOLOMBO ORBITS MERCURY",
         "ESA confirms — 8-year trip ends", planet),
        ("SPORT  •  CRICKET", GREEN, "INDIA POSTS RECORD 720",
         "Pant 128 — NZ trail by 233", None),
        ("LIBYA  •  MEDITERRANEAN", (96, 64, 32),
         "BLAST SINKS RUSSIAN SHIP", "Drone suspected — Benghazi port",
         ship),
    ]
    for i, (tag, tc, label, sub, icon) in enumerate(cells_a):
        panel(d, MARGIN + i * (gw + 12), gy1, gw, gh, tag, tc, label, 25,
              sub, 16, icon)
    for i, (tag, tc, label, sub, icon) in enumerate(cells_b):
        panel(d, MARGIN + i * (gw + 12), gy1 + gh + 12, gw, gh, tag, tc,
              label, 25, sub, 16, icon)

    # ---- "Also on Sunday" strip: 12 verified additions ----
    sy = gy1 + 2 * gh + 24
    d.text((MARGIN, sy), "ALSO ON SUNDAY 22 NOVEMBER 2026",
           font=font(SANS_B, 15), fill=INK)
    rule(d, sy + 22, width=2)
    strip = [
        ("IRAN RATIONS POWER", "Silent economic war"),
        ("FACTORY FIRE SEARCH", "Workers missing — rescuers dig on"),
        ("MYANMAR SHAKEN", "Quake 4.1 — no damage"),
        ("VERSTAPPEN WINS VEGAS", "Third win in four years"),
        ("AI WEAPONS TALKS FAIL", "No binding rules agreed"),
        ("TURKEY SEIZES TV CHANNEL", "Last independent outlet taken"),
        ("SEATTLE ARRESTS PROTESTED", "Airport detentions draw outcry"),
        ("NIGERIA BOAT SINKS", "Mourners lost on river"),
        ("BASRA PLANT FIRE", "Blaze hits power station"),
        ("CRISPR CUTS CHOLESTEROL", "One shot — down 52%"),
        ("KOREA MINISTER QUITS", "AI cheating chaos — Lee accepts"),
        ("NEPAL PM IN DELHI", "First trip abroad — Modi talks Monday"),
    ]
    col_w = (W - 2 * MARGIN - 24) // 2
    row_h = 28
    bf = font(SANS_B, 15)
    for i, (label, sub) in enumerate(strip):
        col, row = i % 2, i // 2
        x = MARGIN + col * (col_w + 24)
        y = sy + 30 + row * row_h
        # Width-aware: shrink the sub font, then drop trailing sub words,
        # so the line never crosses the column edge.
        sub_f = font(SANS, 15)
        words = sub.split()
        while True:
            total = (14 + text_w(d, label, bf) + 6 +
                     text_w(d, "— " + " ".join(words), sub_f))
            if total <= col_w or (sub_f.size <= 12 and len(words) <= 1):
                break
            if sub_f.size > 12:
                sub_f = font(SANS, sub_f.size - 1)
            else:
                words = words[:-1]
        d.text((x, y), "•", font=bf, fill=RED)
        d.text((x + 14, y), label, font=bf, fill=INK)
        lw = text_w(d, label, bf)
        d.text((x + 14 + lw + 6, y), "— " + " ".join(words), font=sub_f,
               fill=(58, 58, 58))

    # ---- UTC timeline ----
    ty = sy + 30 + 6 * row_h + 10
    rule(d, ty, width=1)
    d.text((MARGIN, ty + 8), "THE DAY IN UTC", font=font(SANS_B, 13),
           fill=FAINT)
    tl = ("02:00  WEST BANK ATTACKS      02:00  KHARTOUM DRONES      "
          "02:35  MYANMAR QUAKE      DAWN  BENGHAZI BLAST      "
          "SUNDAY  COP31 COLLAPSES")
    tf2 = fit(d, tl, SANS_B, 13, W - 2 * MARGIN - 150)
    d.text((MARGIN + 132, ty + 8), tl, font=tf2, fill=INK)

    # ---- Footer ----
    fy = ty + 30
    rule(d, fy, width=2)
    draw_centered(d, fy + 8,
                  "Reported on Sunday 22 November 2026 (UTC), as the named "
                  "outlets reported it. All drawings are original vector work.",
                  font(SANS, 12), fill=FAINT)
    draw_centered(d, fy + 26,
                  "Sources: Reuters, AP, AFP, CNN, UN News, The Times, "
                  "Le Monde, IPS, WWF.",
                  font(SANS, 12), fill=FAINT)

    img.save(OUT, format="PNG")
    os.chmod(OUT, 0o644)
    with open(OUT, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    size = os.path.getsize(OUT)
    print("wrote %s  %d bytes  sha256 %s" % (OUT, size, digest))


if __name__ == "__main__":
    render()

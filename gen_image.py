#!/usr/bin/env python3
"""Render a dense newspaper front page summing up 24 November 2026.

Deterministic: no randomness, no network, no clock. Output is a fixed
1024x1024 PNG. Stories are short paraphrases of real 24 Nov 2026 wire
headlines; no invented quotes and no invented casualty figures.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (20, 20, 20)
RED = (138, 26, 26)
GREEN = (26, 107, 46)
MUTED = (90, 86, 76)
RULE = (40, 40, 40)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, lines, fnt, fill=INK, lh=None):
    if lh is None:
        lh = int(fnt.size * 1.32)
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def rule(d, x0, x1, y, width=1):
    d.line([(x0, y), (x1, y)], fill=RULE, width=width)


def double_rule(d, x0, x1, y):
    rule(d, x0, x1, y, 2)
    rule(d, x0, x1, y + 4, 1)


def story(d, x, y, w, kicker, headline, body, head_size=13, body_size=11,
          max_body=2):
    d.text((x, y), kicker, font=SANS_B(10), fill=RED)
    y += 12
    hl = wrap(d, headline, SERIF_B(head_size), w)
    y = text_block(d, x, y, hl, SERIF_B(head_size), lh=int(head_size * 1.25))
    y += 2
    bl = wrap(d, body, SERIF(body_size), w)[:max_body]
    y = text_block(d, x, y, bl, SERIF(body_size), lh=int(body_size * 1.32))
    return y + 6


def headline_only(d, x, y, w, kicker, headline, head_size=13):
    d.text((x, y), kicker, font=SANS_B(10), fill=RED)
    y += 12
    hl = wrap(d, headline, SERIF_B(head_size), w)
    y = text_block(d, x, y, hl, SERIF_B(head_size), lh=int(head_size * 1.25))
    return y + 5


def draw_scales(d, x0, y0, x1, y1):
    """A small line drawing of the scales of justice inside a box."""
    d.rectangle([x0, y0, x1, y1], outline=RULE, width=1)
    cx = (x0 + x1) // 2
    top = y0 + 14
    base = y1 - 16
    d.ellipse([cx - 4, top - 4, cx + 4, top + 4], outline=INK, width=2)
    d.line([(cx, top + 4), (cx, base)], fill=INK, width=2)
    d.line([(cx - 26, base), (cx + 26, base)], fill=INK, width=2)
    bar_y = top + 16
    d.line([(cx - 62, bar_y), (cx + 62, bar_y)], fill=INK, width=2)
    for sgn in (-1, 1):
        px = cx + sgn * 62
        d.line([(px, bar_y), (px - 14, bar_y + 26)], fill=INK, width=1)
        d.line([(px, bar_y), (px + 14, bar_y + 26)], fill=INK, width=1)
        d.arc([px - 16, bar_y + 20, px + 16, bar_y + 36], 0, 180, fill=INK, width=2)
    d.text((cx, y1 - 13), "THE HAGUE", font=SANS_B(9), fill=MUTED, anchor="ma")


def draw_markets(d, x0, y0, w):
    d.text((x0, y0), "MARKETS  —  TUESDAY CLOSE", font=SANS_B(11), fill=RED)
    data = [
        ("Nasdaq", 6.51), ("S&P 500", 4.73), ("Nikkei 225", 3.91),
        ("DAX", 2.15), ("FTSE 100", 1.30), ("Brent crude", -2.99),
    ]
    zero_x = x0 + 150
    max_px = 130
    y = y0 + 20
    row_h = 15
    for label, pct in data:
        d.text((x0, y), label, font=SANS(10), fill=INK)
        d.line([(zero_x, y - 1), (zero_x, y + row_h - 4)], fill=MUTED, width=1)
        bar_len = int(abs(pct) / 6.51 * max_px)
        col = GREEN if pct >= 0 else RED
        if pct >= 0:
            d.rectangle([zero_x, y + 1, zero_x + bar_len, y + row_h - 5], fill=col)
        else:
            d.rectangle([zero_x - bar_len, y + 1, zero_x, y + row_h - 5], fill=col)
        sign = "+" if pct >= 0 else ""
        d.text((zero_x + max_px + 8, y), f"{sign}{pct:.2f}%",
               font=SANS_B(10), fill=col)
        y += row_h
    return y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    L, R = 26, 998
    CW = R - L

    # ---- Masthead ----
    rule(d, L, R, 14, 1)
    d.text((W // 2, 22), "THE WORLD IN ONE DAY", font=SERIF_B(44),
           fill=INK, anchor="ma")
    d.text((L, 74), "TUESDAY, 24 NOVEMBER 2026", font=SANS_B(11), fill=INK)
    d.text((W // 2, 74), "THE WORLD IN ONE PAGE", font=SANS_B(11),
           fill=INK, anchor="ma")
    d.text((R, 74), "PRICE $2.50", font=SANS_B(11), fill=INK, anchor="ra")
    double_rule(d, L, R, 94)

    # ---- Headline ----
    d.text((W // 2, 106), "COURT FINDS MYANMAR", font=SERIF_B(38),
           fill=INK, anchor="ma")
    d.text((W // 2, 148), "GUILTY OF GENOCIDE", font=SERIF_B(38),
           fill=INK, anchor="ma")
    deck = ("Fourteen nations affirm the Hague ruling on the Rohingya — "
            "the first time the court has found a state responsible")
    dl = wrap(d, deck, SERIF(15), CW - 60)
    text_block(d, (W - CW) // 2 + 30, 196, dl, SERIF(15),
               fill=MUTED, lh=19)
    rule(d, L, R, 240, 1)

    # ---- Lead story + scales illustration ----
    lead = (
        "THE HAGUE — The International Court of Justice ruled that "
        "Myanmar's armed forces committed genocide against the Rohingya "
        "during the 2017 operations in Rakhine State, in a 9–6 decision. "
        "It is the first time the court has found a state responsible "
        "for genocide. Fourteen countries, among them Britain, Spain, "
        "Canada and Australia, said on Monday they recognise the ruling, "
        "and London announced fresh sanctions on senior figures. The "
        "ruling sets a precedent for South Africa's Gaza case, lawyers "
        "said.")
    ll = wrap(d, lead, SERIF(13), 660)
    text_block(d, L, 250, ll, SERIF(13), lh=17)
    draw_scales(d, 706, 250, R, 354)
    rule(d, L, R, 362, 1)

    # ---- Three-column story grid ----
    cols = [
        (L, 314, [
            ("NATO", "NATO VOWS TO DEFEND SPACE",
             "The alliance will defend against threats in orbit after "
             "reports of a Russian nuclear-armed satellite."),
            ("UNITED NATIONS", "UN CHIEF SEEKS AI RULES WITHIN A YEAR",
             "Guterres called on states to build a framework to manage "
             "the risks of artificial intelligence."),
            ("CHINA", "CHINA SENTENCES OFFICIAL TO DEATH",
             "An official surnamed Ma was sentenced to death for spying "
             "for an unnamed foreign country."),
            ("KOREA", "RUSSIAN JETS ENTER KOREAN AIR ZONE",
             "Seoul said Russian aircraft flew inside its air defence "
             "identification zone near Japan."),
        ]),
        (356, 312, [
            ("MEXICO", "DRONE HELPED CATCH EL CHAPO ISIDRO",
             "A US drone helped capture Fausto Isidro Meza Flores in "
             "Sinaloa; Mexico will try him itself."),
            ("TRADE", "TRUMP ANNOUNCES JAPAN TRADE DEAL",
             "Tokyo's Nikkei led an Asian rally after the deal; Japan "
             "hosts the US Treasury secretary."),
            ("TARIFFS", "INDONESIA DEAL, EU TARIFF WARNING",
             "Washington announced a deal with Jakarta while the EU "
             "prepared tariffs on $84bn of US goods."),
            ("HEALTH", "MEASLES DEATH IN PENNSYLVANIA",
             "The state reported another death linked to the measles "
             "epidemic spreading across 46 counties."),
        ]),
        (684, 314, [
            ("NEPAL", "QUAKE OF 5.6 SHAKES NEPAL BORDER",
             "A 5.6-magnitude quake struck Koshi province near the "
             "border with China, monitors said."),
            ("GAZA", "OXFAM CALLS GAZA A 'TOXIC LAND'",
             "The aid group described a territory transformed by war, "
             "as strikes continued and aid gaps grew."),
            ("YEMEN", "HOUTHIS REPORT DEADLY SAUDI STRIKES",
             "The group reported deadly airstrikes in Hodeida as "
             "regional tensions simmered."),
            ("PHILIPPINES", "MAYON ERUPTION FEARS GROW",
             "Mount Mayon's activity raised fears of a larger volcanic "
             "event, officials said."),
        ]),
    ]
    for x, w, stories in cols:
        y = 374
        for kicker, head, body in stories:
            y = story(d, x, y, w, kicker, head, body)
    rule(d, L, R, 640, 1)

    # ---- Markets + briefs ----
    draw_markets(d, L, 652, 470)
    bx, bw = 516, R - 516
    d.text((bx, 652), "THE WORLD IN BRIEF", font=SANS_B(11), fill=RED)
    briefs = [
        "France: students prepare nationwide protests over education reforms.",
        "EU and Canada plan closer collaboration on artificial intelligence.",
        "Trump warns Iran as a second US carrier sails toward the Strait of Hormuz.",
        "SoftBank plans a $2bn investment in Intel, reports say.",
        "Bangladesh begins a drive to vaccinate 50m children against typhoid.",
        "Somalia and Uganda step up operations against al-Shabaab.",
        "Ukrainian sea drones sink the Russian corvette Merkury in Benghazi port.",
        "European states prepare evacuations after the coup in Niger.",
        "Pentagon rebukes Canada over defence spending and its F-35 review.",
        "US blacklists Megaspeed, the firm at the centre of the Nvidia case.",
        "Zelensky urges Ukraine, Russia, US and Europe to hold talks soon.",
        "China opens its Tiangong station to a first foreign astronaut.",
        "Fighting pauses on the Thai-Cambodia border after a truce.",
        "Nvidia reinstates Jensen Huang as chief after Trump intervenes.",
    ]
    y = 670
    for b in briefs:
        lines = wrap(d, "•  " + b, SANS(10), bw)
        y = text_block(d, bx, y, lines, SANS(10), lh=13)
        y += 1
    rule(d, L, R, 874, 1)

    # ---- Bottom headline-only stories ----
    bottom = [
        ("CLIMATE", "COP31 FAILURE REVEALS A DIVIDED WORLD"),
        ("TECH", "STATES SUE SPACEX OVER GROK IMAGES"),
        ("UNITED STATES", "DEMOCRATS TAKE HISTORIC MAJORITIES"),
        ("CHIPS", "GOLD HOLDS $3,620 AS BRENT SLIDES"),
    ]
    for i, (kicker, head) in enumerate(bottom):
        x = L if i % 2 == 0 else 524
        y = 886 + (i // 2) * 40
        headline_only(d, x, y, 448, kicker, head)
    rule(d, L, R, 968, 1)
    d.text((W // 2, 976),
           "THE WORLD IN ONE DAY  •  TUESDAY, 24 NOVEMBER 2026  •  "
           "COMPILED FROM WIRE REPORTS  •  PAGE 1 OF 1",
           font=SANS(10), fill=MUTED, anchor="ma")

    img.save(out, "PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

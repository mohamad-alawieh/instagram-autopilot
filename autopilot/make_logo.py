#!/usr/bin/env python3
"""Logo helper.

Create a simple logo (monogram badge + name) for brands without one:
    python3 autopilot/make_logo.py create "Brightside Bakery" --accent "#ffc46b" --button "#e0892b" [--tagline "bakery"]
  Writes autopilot/assets/logo.png (white text, transparent, for dark backgrounds)
  and autopilot/assets/logo-dark.png (dark text, for light backgrounds).

Suggest brand colors from an existing logo:
    python3 autopilot/make_logo.py colors path/to/logo.png
  Prints a JSON "colors" block you can paste into brand.json.

Prepare an uploaded logo for dark backgrounds (trim, max 900px wide):
    python3 autopilot/make_logo.py prepare path/to/logo.png
"""
import colorsys, json, sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "autopilot" / "assets"


def initials(name):
    words = [w for w in name.replace("-", " ").split() if w[0].isalnum()]
    return (words[0][0] + (words[1][0] if len(words) > 1 else "")).upper() if words else "?"


def create(name, accent, button, tagline=""):
    from playwright.sync_api import sync_playwright
    ASSETS.mkdir(parents=True, exist_ok=True)
    for fname, text_color in (("logo.png", "#ffffff"), ("logo-dark.png", "#111111")):
        html = f"""<html><head><style>*{{margin:0}}body{{background:transparent;font-family:Poppins,Inter,sans-serif}}
        .w{{display:inline-flex;align-items:center;gap:26px;padding:20px}}
        .b{{width:150px;height:150px;border-radius:38px;background:linear-gradient(135deg,{accent},{button});display:flex;align-items:center;justify-content:center;
            color:#fff;font-weight:800;font-size:68px;letter-spacing:-2px;box-shadow:inset 0 -6px 0 rgba(0,0,0,.15)}}
        .n{{color:{text_color};font-size:76px;font-weight:700;line-height:1;letter-spacing:-1px}}
        .t{{color:{text_color};opacity:.75;font-size:26px;letter-spacing:9px;text-transform:lowercase;margin-top:10px}}</style></head>
        <body><div class="w" id="w"><div class="b">{escape(initials(name))}</div><div><div class="n">{escape(name)}</div>
        {f'<div class="t">{escape(tagline)}</div>' if tagline else ''}</div></div></body></html>"""
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1800, "height": 400})
            pg.set_content(html)
            pg.wait_for_timeout(150)
            pg.locator("#w").screenshot(path=str(ASSETS / fname), omit_background=True)
            b.close()
    print(str(ASSETS / "logo.png"))


def colors(path):
    from PIL import Image
    im = Image.open(path).convert("RGBA").resize((160, 160))
    px = [(r, g, b) for r, g, b, a in im.getdata() if a > 200]
    # keep saturated, non-grey pixels
    vivid = [c for c in px if (max(c) - min(c)) > 40]
    pool = vivid or px
    q = Image.new("RGB", (len(pool), 1)); q.putdata(pool)
    pal = q.quantize(colors=4).getpalette()[:12]
    main = tuple(pal[0:3])
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in main))
    def hx(hh, ll, ss):
        r, g, b = colorsys.hls_to_rgb(hh, max(0, min(1, ll)), max(0, min(1, ss)))
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    out = {"bg1": hx(h, 0.08, s * .8), "bg2": hx(h, 0.15, s * .8), "bg3": hx(h, 0.28, s * .85),
           "accent": hx(h, 0.68, max(s, .6)), "button": hx(h, 0.5, max(s, .65)), "text": "#ffffff"}
    print(json.dumps({"colors": out, "detected": "#%02x%02x%02x" % main}, indent=2))


def prepare(path):
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    if im.width > 900:
        im = im.resize((900, int(im.height * 900 / im.width)))
    ASSETS.mkdir(parents=True, exist_ok=True)
    im.save(ASSETS / "logo.png")
    # warn if the logo is mostly dark (would vanish on dark backgrounds)
    lum = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b, a in im.getdata() if a > 200]
    if lum and sum(lum) / len(lum) < 70:
        print("warning: this logo is mostly dark and may be hard to see on the dark post background. "
              "Ask for a white/light version, or set lighter brand colors.", file=sys.stderr)
    print(str(ASSETS / "logo.png"))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "create":
        opts = dict(zip(a[2::2], a[3::2]))
        create(a[1], opts.get("--accent", "#5fb2ff"), opts.get("--button", "#2f6bff"), opts.get("--tagline", ""))
    elif a[0] == "colors":
        colors(a[1])
    elif a[0] == "prepare":
        prepare(a[1])
    else:
        sys.exit(__doc__)

#!/usr/bin/env python3
"""Show every theme in the owner's brand, side by side, so they can pick one.

Usage:  python3 autopilot/preview_themes.py [output.jpg]
Renders a cover slide and a checklist slide per theme using autopilot/brand.json
(name, logo, colors) and writes one comparison image (default: theme-preview.jpg).
Nothing is saved into docs/media.
"""
import copy, io, sys
from PIL import Image, ImageDraw, ImageFont
from common import load_brand, THEMES
from render_post import slide_html, W, H, FIT


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "theme-preview.jpg"
    brand = load_brand()
    pillar = (brand.get("pillars") or ["What we do"])[0]
    cover = {"layout": "cover", "title": f"{brand['name']}: <span class='acc'>a sample</span> headline",
             "sub": f"This is how a post about “{pillar}” would look."}
    lst = {"layout": "list", "title": "What you get", "items": ["Your logo and colors", "Clear, readable text", "Consistent every week"]}
    from playwright.sync_api import sync_playwright
    tw, th, pad, label = 360, 450, 24, 60
    sheet = Image.new("RGB", (len(THEMES) * (tw * 2 + pad) + pad, th + label + pad * 2), "#e9e9e9")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("Poppins-Bold.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, name in enumerate(THEMES):
            br = copy.deepcopy(brand); br["theme"] = name
            x = pad + i * (tw * 2 + pad)
            for j, s in enumerate((cover, lst)):
                pg.set_content(slide_html(br, s, j, 2)); pg.wait_for_timeout(100); pg.evaluate(FIT)
                im = Image.open(io.BytesIO(pg.screenshot(type="jpeg", quality=85))).resize((tw, th))
                sheet.paste(im, (x + j * tw, label + pad))
            draw.text((x, pad // 2 + 4), f"{i + 1}. {name}", fill="#111111", font=font)
        b.close()
    sheet.save(out, quality=88)
    print(out)
    for i, (k, v) in enumerate(THEMES.items(), 1):
        print(f"{i}. {k}: {v}")


if __name__ == "__main__":
    main()

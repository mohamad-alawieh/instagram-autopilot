#!/usr/bin/env python3
"""Render an Instagram post (single image or carousel) in the brand's style.

Usage:  python3 autopilot/render_post.py post.json
post.json:
{
  "id": "2026-11-02-why-fresh-bread",      # unique, used in file names
  "folder": "2026-11-w1",                   # docs/media/<folder>/
  "slides": [
    {"layout": "cover", "title": "Why our bread <span class='acc'>sells out</span> by 11am", "sub": "Swipe to see"},
    {"layout": "point", "num": "01", "title": "Short title", "body": "One or two sentences."},
    {"layout": "list",  "title": "Signs you need X", "items": ["one", "two", "three"]},
    {"layout": "cta",   "title": "Closing line", "body": "optional", "button": "DM us to order"},
    {"layout": "offer", "title": "OFFER TITLE", "sub": "optional", "plans": [
        {"name": "Basic", "note": "short note", "price": "$35", "items": ["a", "b"]}], "note": "Free delivery this week"}
  ]
}
Use <span class='acc'>…</span> to highlight words in the accent color.
Prints one public URL per slide (from brand.json media_base_url), in order.
Text that would overflow is shrunk automatically; the output is still worth a look.
"""
import json, sys
from html import escape
from common import ROOT, MEDIA, load_brand, css, header, footer

W, H, LIMIT = 1080, 1350, 1350 - 150


def chk(items):
    return "".join(f'<div class="li"><div class="ck">✓</div><div>{escape(i)}</div></div>' for i in items)


def slide_html(brand, s, idx, total):
    lay = s.get("layout", "point")
    orbs = ('<div class="orb" style="width:90px;height:90px;right:70px;top:190px"></div>'
            '<div class="orb" style="width:180px;height:180px;left:-90px;top:980px;opacity:.55"></div>')
    swipe = '<div class="swipe">Swipe →</div>' if total > 1 and idx < total - 1 else ""
    pg = f'<div class="page">{idx + 1} / {total}</div>' if total > 2 and 0 < idx < total - 1 else ""
    if lay == "cover":
        body = f'<div class="content" style="margin-top:120px"><h1>{s["title"]}</h1>' + (f'<p>{s["sub"]}</p>' if s.get("sub") else "") + "</div>"
        extra = ""
    elif lay == "point":
        body = (f'<div class="content" style="margin-top:80px">' + (f'<div class="num">{escape(s["num"])}</div>' if s.get("num") else "")
                + f'<h2>{s["title"]}</h2>' + (f'<p>{s["body"]}</p>' if s.get("body") else "") + "</div>")
        extra = ""
    elif lay == "list":
        body = f'<div class="content" style="margin-top:80px"><h2>{s["title"]}</h2><div class="card">{chk(s["items"])}</div></div>'
        extra = ""
    elif lay == "cta":
        body = (f'<div class="content" style="margin-top:110px"><h2>{s["title"]}</h2>' + (f'<p>{s["body"]}</p>' if s.get("body") else "")
                + (f'<div class="btn">{escape(s["button"])}</div>' if s.get("button") else "") + "</div>")
        extra = footer(brand)
        swipe = ""
    elif lay == "offer":
        plans = s.get("plans", [])
        cards = "".join(
            f'<div class="card" style="flex:1;margin:0"><div style="font-size:calc(var(--s)*38px);font-weight:700">{escape(p["name"])}</div>'
            f'<div style="font-size:calc(var(--s)*24px);opacity:.75">{escape(p.get("note", ""))}</div>'
            f'<div class="price">{escape(p["price"])}</div><div style="--s:.85">{chk(p.get("items", []))}</div></div>' for p in plans)
        body = (f'<div class="content" style="margin-top:10px;text-align:center"><h1 style="font-size:calc(var(--s)*76px)">{s["title"]}</h1>'
                + (f'<p style="margin-top:14px">{s["sub"]}</p>' if s.get("sub") else "")
                + f'<div style="display:flex;gap:26px;margin-top:36px;text-align:left">{cards}</div>'
                + (f'<div class="acc" style="margin-top:30px;font-size:calc(var(--s)*30px);font-weight:700">{s["note"]}</div>' if s.get("note") else "")
                + "</div>")
        extra = footer(brand)
        orbs = ""
    else:
        raise SystemExit(f"Unknown layout {lay!r}")
    return (f'<html><head><meta charset="utf-8"><style>{css(brand, W, H)}</style></head><body>{orbs}{header(brand)}'
            f'{body}{extra}{swipe}{pg}</body></html>')


FIT = f"""() => {{ const c=document.querySelector('.content'); let s=1;
  while (c && c.getBoundingClientRect().bottom > {LIMIT} && s > 0.55) {{ s -= 0.04; document.documentElement.style.setProperty('--s', s); }}
  return s; }}"""


def main():
    spec = json.loads(open(sys.argv[1]).read())
    brand = load_brand()
    out = MEDIA / spec["folder"]
    out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    urls, slides = [], spec["slides"]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides):
            pg.set_content(slide_html(brand, s, i, len(slides)))
            pg.wait_for_timeout(120)
            scale = pg.evaluate(FIT)
            name = f'{spec["id"]}_{i + 1}.jpg' if len(slides) > 1 else f'{spec["id"]}.jpg'
            pg.screenshot(path=str(out / name), type="jpeg", quality=92)
            if scale < 0.99:
                print(f"note: slide {i + 1} text shrunk to {scale:.0%} to fit; consider shorter copy", file=sys.stderr)
            urls.append(brand["media_base_url"].rstrip("/") + f'/{spec["folder"]}/{name}')
        b.close()
    print(json.dumps(urls, indent=2))


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "autopilot"))
    main()

"""Shared helpers: repo paths, brand loading, themes, HTML/CSS for posts and reels, scheduling helpers."""
import base64, json, mimetypes
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
AP = ROOT / "autopilot"
MEDIA = ROOT / "docs" / "media"

# ── Themes ─────────────────────────────────────────────────────────────────────
# Each theme turns the brand colors into a full look. brand.json "theme" picks one.
THEMES = {
    "midnight": "Dark gradient in your brand colors, glowing accents. Modern and techy.",
    "clean":    "Light off-white background, dark text, brand-color highlights. Friendly and airy.",
    "bold":     "Solid brand-color background, big white type, highlighter accents. Loud and punchy.",
    "minimal":  "Pure white, black type, thin lines, one accent color. Calm and premium.",
    "elegant":  "Warm cream background, serif headlines, refined accents. Boutique and classic.",
}


def theme_name(brand):
    t = brand.get("theme", "midnight")
    if t not in THEMES:
        raise SystemExit(f"Unknown theme {t!r}. Choose one of: {', '.join(THEMES)}")
    return t


def tokens(brand):
    """Design tokens for the brand's theme."""
    c, t = brand["colors"], theme_name(brand)
    base = dict(head_font="'Poppins'", body_font="'Poppins'", head_weight=800, orbs=False, light=False,
                acc_css=f"color:{c['accent']}", button=c["button"], button_text="#ffffff",
                check=c["button"], check_text="#ffffff", num=c["button"], num_opacity=.6,
                radius=28, btn_radius=60)
    if t == "midnight":
        base.update(text=c.get("text", "#ffffff"), orbs=True, card_bg="rgba(255,255,255,.08)",
                    card_border="rgba(255,255,255,.18)",
                    bg=(f"radial-gradient(circle at 85% 90%,{c['button']} 0,transparent 45%),"
                        f"radial-gradient(circle at 0% 18%,{c['bg3']} 0,transparent 40%),"
                        f"linear-gradient(160deg,{c['bg1']},{c['bg2']} 55%,{c['bg3']})"))
    elif t == "clean":
        base.update(text="#14161a", light=True, body_font="'Inter'", head_font="'Poppins'", head_weight=700,
                    acc_css=f"color:{c['button']}", card_bg="#ffffff", card_border="rgba(20,22,26,.08)",
                    bg=(f"radial-gradient(circle at 100% 0%,{c['accent']}55 0,transparent 38%),"
                        f"radial-gradient(circle at 0% 100%,{c['button']}33 0,transparent 42%),#f7f7f4"))
    elif t == "bold":
        base.update(text="#ffffff", card_bg="rgba(255,255,255,.14)", card_border="rgba(255,255,255,.28)",
                    acc_css=f"background:#ffffff;color:{c['button']};padding:0 .14em;border-radius:.12em;"
                            "box-decoration-break:clone;-webkit-box-decoration-break:clone",
                    button="#ffffff", button_text=c["button"], check="#ffffff", check_text=c["button"],
                    num="#ffffff", num_opacity=.35,
                    bg=f"linear-gradient(170deg,{c['button']},{c['bg3']})")
    elif t == "minimal":
        base.update(text="#0b0b0b", light=True, head_font="'Inter'", body_font="'Inter'", head_weight=700,
                    acc_css=f"color:{c['button']}", card_bg="transparent", card_border="#0b0b0b",
                    check="#0b0b0b", num="#0b0b0b", num_opacity=.12, radius=0, btn_radius=0,
                    button="#0b0b0b", bg="#ffffff")
    elif t == "elegant":
        base.update(text="#2b2118", light=True, head_font="'Lora'", body_font="'Inter'", head_weight=600,
                    acc_css=f"color:{c['button']};font-style:italic", card_bg="rgba(255,255,255,.55)",
                    card_border="rgba(43,33,24,.14)", num=c["button"], num_opacity=.45, radius=6, btn_radius=4,
                    bg=f"radial-gradient(circle at 90% 8%,{c['accent']}40 0,transparent 35%),#f5efe4")
    return base


def load_brand():
    p = AP / "brand.json"
    if not p.exists():
        raise SystemExit("autopilot/brand.json is missing. Run the setup wizard (or copy brand.example.json).")
    return json.loads(p.read_text())


def logo_path(brand):
    """The logo version that suits the theme: light themes use "logo_on_light" if set."""
    key = "logo_on_light" if tokens(brand)["light"] and brand.get("logo_on_light") else "logo"
    p = ROOT / brand.get(key, "autopilot/assets/logo.png")
    return p if p.exists() else None


def logo_uri(brand):
    """Logo as an embedded data URI (pages rendered from memory can't load local files)."""
    p = logo_path(brand)
    if not p:
        return ""
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def post_time(brand, day: date, hhmm: str | None = None) -> str:
    """ISO 8601 time with the correct UTC offset for that date (handles daylight saving)."""
    hhmm = hhmm or brand["schedule"]["time"]
    h, m = map(int, hhmm.split(":"))
    tz = ZoneInfo(brand["schedule"]["timezone"])
    return datetime(day.year, day.month, day.day, h, m, tzinfo=tz).isoformat()


def base_css(brand, w, h):
    """CSS shared by posts and reels."""
    k = tokens(brand)
    return f"""*{{margin:0;box-sizing:border-box}}
:root{{--s:1}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:{k['body_font']},Poppins,Inter,sans-serif;color:{k['text']};position:relative;background:{k['bg']}}}
h1,h2,.price,.num,.wordmark{{font-family:{k['head_font']},Poppins,serif}}
.acc{{{k['acc_css']}}}
.orb{{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 35%,{brand['colors']['accent']},{brand['colors']['button']} 65%);opacity:.85}}
.tag{{display:inline-block;background:{k['button']};color:{k['button_text']};border-radius:{k['btn_radius']}px;padding:14px 34px;font-size:38px;font-weight:600}}
.btn{{display:inline-block;background:{k['button']};color:{k['button_text']};border-radius:{k['btn_radius']}px;font-weight:700}}"""


def css(brand, w, h):
    k = tokens(brand)
    minimal_rule = ".content{border-left:4px solid #0b0b0b;padding-left:56px;margin-left:80px}" if theme_name(brand) == "minimal" else ""
    return base_css(brand, w, h) + f"""
.top{{display:flex;justify-content:space-between;align-items:center;padding:56px 64px}}
.logo{{height:70px;max-width:420px;object-fit:contain}}
.wordmark{{font-size:40px;font-weight:700}}
.handle{{font-size:24px;opacity:.8}}
.content{{padding:0 80px}}{minimal_rule}
h1{{font-size:calc(var(--s)*92px);line-height:1.06;font-weight:{k['head_weight']};letter-spacing:-1px}}
h2{{font-size:calc(var(--s)*68px);line-height:1.12;font-weight:{k['head_weight']}}}
p{{font-size:calc(var(--s)*36px);line-height:1.45;opacity:.88;margin-top:30px}}
.num{{font-size:calc(var(--s)*140px);font-weight:800;color:{k['num']};opacity:{k['num_opacity']};line-height:1}}
.card{{background:{k['card_bg']};border:{'2px' if theme_name(brand) == 'minimal' else '1px'} solid {k['card_border']};border-radius:{k['radius']}px;padding:36px 42px;margin-top:28px{';box-shadow:0 10px 40px rgba(0,0,0,.06)' if k['light'] and theme_name(brand) != 'minimal' else ''}}}
.li{{display:flex;gap:22px;font-size:calc(var(--s)*33px);margin:20px 0;align-items:flex-start}}
.ck{{flex:none;width:44px;height:44px;border-radius:{'0' if theme_name(brand) == 'minimal' else '50%'};background:{k['check']};color:{k['check_text']};display:flex;align-items:center;justify-content:center;font-size:26px;margin-top:2px}}
.btn{{margin-top:46px;padding:24px 50px;font-size:calc(var(--s)*34px)}}
.price{{font-size:calc(var(--s)*84px);font-weight:800}}
.foot{{position:absolute;bottom:52px;left:80px;right:80px;display:flex;justify-content:space-between;gap:20px;font-size:24px;opacity:.85}}
.swipe{{position:absolute;bottom:56px;right:80px;font-size:30px;font-weight:600;{k['acc_css'] if theme_name(brand) != 'bold' else 'color:#ffffff'}}}
.page{{position:absolute;bottom:60px;left:80px;font-size:24px;opacity:.55}}"""


def orbs_html(brand, kind="post"):
    if not tokens(brand)["orbs"]:
        return ""
    if kind == "reel":
        return ('<div class="orb" id="o1" style="width:120px;height:120px;right:90px;top:300px"></div>'
                '<div class="orb" id="o2" style="width:240px;height:240px;left:-100px;top:1400px;opacity:.7"></div>')
    return ('<div class="orb" style="width:90px;height:90px;right:70px;top:190px"></div>'
            '<div class="orb" style="width:180px;height:180px;left:-90px;top:980px;opacity:.55"></div>')


def header(brand):
    uri = logo_uri(brand)
    mark = f'<img class="logo" src="{uri}">' if uri else f'<div class="wordmark">{brand["name"]}</div>'
    return f'<div class="top">{mark}<div class="handle">@{brand["handle"]}</div></div>'


def footer(brand):
    ct = brand.get("contact", {})
    bits = [x for x in (ct.get("phone"), ct.get("email") or ct.get("website")) if x]
    return '<div class="foot">' + "".join(f"<span>{b}</span>" for b in bits) + "</div>" if bits else ""

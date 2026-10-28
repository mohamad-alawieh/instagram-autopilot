"""Shared helpers: repo paths, brand loading, HTML/CSS for the brand look, scheduling helpers."""
import json
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
AP = ROOT / "autopilot"
MEDIA = ROOT / "docs" / "media"


def load_brand():
    p = AP / "brand.json"
    if not p.exists():
        raise SystemExit("autopilot/brand.json is missing. Run the setup wizard (or copy brand.example.json).")
    return json.loads(p.read_text())


def logo_uri(brand):
    """Logo as an embedded data URI (pages rendered from memory can't load local files)."""
    import base64, mimetypes
    p = ROOT / brand.get("logo", "autopilot/assets/logo.png")
    if not p.exists():
        return ""
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def post_time(brand, day: date, hhmm: str | None = None) -> str:
    """ISO 8601 time with the correct UTC offset for that date (handles daylight saving)."""
    hhmm = hhmm or brand["schedule"]["time"]
    h, m = map(int, hhmm.split(":"))
    tz = ZoneInfo(brand["schedule"]["timezone"])
    return datetime(day.year, day.month, day.day, h, m, tzinfo=tz).isoformat()


def css(brand, w, h):
    c = brand["colors"]
    font = brand.get("font", "Poppins")
    return f"""*{{margin:0;box-sizing:border-box}}
:root{{--s:1}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:'{font}',Poppins,Inter,sans-serif;color:{c['text']};position:relative;
background:radial-gradient(circle at 85% 90%,{c['button']} 0,transparent 45%),radial-gradient(circle at 0% 18%,{c['bg3']} 0,transparent 40%),linear-gradient(160deg,{c['bg1']},{c['bg2']} 55%,{c['bg3']})}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:56px 64px}}
.logo{{height:70px;max-width:420px;object-fit:contain}}
.wordmark{{font-size:40px;font-weight:700}}
.handle{{font-size:24px;opacity:.85}}
.orb{{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 35%,{c['accent']},{c['button']} 65%);opacity:.85}}
.acc{{color:{c['accent']}}}
.content{{padding:0 80px}}
h1{{font-size:calc(var(--s)*92px);line-height:1.04;font-weight:800;letter-spacing:-1px}}
h2{{font-size:calc(var(--s)*68px);line-height:1.1;font-weight:700}}
p{{font-size:calc(var(--s)*36px);line-height:1.45;opacity:.92;margin-top:30px}}
.num{{font-size:calc(var(--s)*140px);font-weight:800;color:{c['button']};opacity:.6;line-height:1}}
.card{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:28px;padding:36px 42px;margin-top:28px}}
.li{{display:flex;gap:22px;font-size:calc(var(--s)*33px);margin:20px 0;align-items:flex-start}}
.ck{{flex:none;width:44px;height:44px;border-radius:50%;background:{c['button']};display:flex;align-items:center;justify-content:center;font-size:26px;margin-top:2px}}
.btn{{display:inline-block;margin-top:46px;background:{c['button']};padding:24px 50px;border-radius:60px;font-size:calc(var(--s)*34px);font-weight:700}}
.price{{font-size:calc(var(--s)*84px);font-weight:800}}
.foot{{position:absolute;bottom:52px;left:80px;right:80px;display:flex;justify-content:space-between;gap:20px;font-size:24px;opacity:.9}}
.swipe{{position:absolute;bottom:56px;right:80px;font-size:30px;font-weight:600;color:{c['accent']}}}
.page{{position:absolute;bottom:60px;left:80px;font-size:24px;opacity:.6}}"""


def header(brand):
    uri = logo_uri(brand)
    mark = f'<img class="logo" src="{uri}">' if uri else f'<div class="wordmark">{brand["name"]}</div>'
    return f'<div class="top">{mark}<div class="handle">@{brand["handle"]}</div></div>'


def footer(brand):
    ct = brand.get("contact", {})
    bits = [x for x in (ct.get("phone"), ct.get("email") or ct.get("website")) if x]
    return '<div class="foot">' + "".join(f"<span>{b}</span>" for b in bits) + "</div>" if bits else ""

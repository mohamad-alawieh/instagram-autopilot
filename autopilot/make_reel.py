#!/usr/bin/env python3
"""Build a branded voiceover reel (1080x1920 MP4) from a JSON spec.

Usage:  python3 autopilot/make_reel.py spec.json
Spec:   {"id": "2026-11-05-reel-topic",   # file name in docs/media/reels/
         "scenes": [{"tag": "Mistake #1", "title": "It's <span class='acc'>slow.</span>",
                     "body": "optional smaller text", "say": "what the voice reads"}, ...],
         "cta": {"title": "We fix <span class='acc'>all three.</span>",
                 "button": "DM us to order",
                 "say": "..."}}
Optional: "voice": "en_US-ryan-high" style names are not needed; set brand.json "voice" to one of VOICES below.
Writes docs/media/reels/<id>.mp4 and <id>-cover.jpg, and prints their public URLs.
Needs: ffmpeg, playwright (chromium), piper-tts (pip). Downloads the free Piper voice from GitHub once.
"""
import json, os, subprocess, sys, tarfile, urllib.request, wave, shutil, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, MEDIA, load_brand

BRAND = load_brand()
OUT = MEDIA / "reels"
LOGO = ROOT / BRAND.get("logo", "autopilot/assets/logo.png")
# Free Piper voices published on GitHub (no account needed). Pick one in brand.json "voice".
VOICES = {
    "ryan": "voice-en-us-ryan-high",          # US male, clear
    "amy": "voice-en-us-amy-low",             # US female
    "lessac": "voice-en-us-lessac-medium",    # US female, warm
    "alan": "voice-en-gb-alan-low",           # UK male
}
VOICE_KEY = BRAND.get("voice", "ryan")
VOICE_DIR = Path.home() / ".cache/piper"
VOICE_URL = f"https://github.com/rhasspy/piper/releases/download/v0.0.2/{VOICES[VOICE_KEY]}.tar.gz"
VOICE = None  # resolved by ensure_voice()
BASE_URL = BRAND["media_base_url"].rstrip("/") + "/reels/"
FPS, GAP = 30, 0.7  # silence after each spoken line


def sh(*cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def ensure_voice():
    global VOICE
    d = VOICE_DIR / VOICE_KEY
    found = list(d.glob("*.onnx")) if d.exists() else []
    if not found:
        d.mkdir(parents=True, exist_ok=True)
        tgz = d / "voice.tar.gz"
        urllib.request.urlretrieve(VOICE_URL, tgz)
        with tarfile.open(tgz) as t:
            for m in t.getmembers():
                if m.name.endswith((".onnx", ".onnx.json")):
                    m.name = os.path.basename(m.name)
                    t.extract(m, d, filter="data")
        tgz.unlink()
        found = list(d.glob("*.onnx"))
    VOICE = found[0]


def speak(text, path):
    subprocess.run([sys.executable, "-m", "piper", "-m", str(VOICE), "-f", str(path), "--length-scale", "0.95"],
                   input=text.encode(), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


CSS_T = """*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;font-family:Poppins,sans-serif;color:#fff;position:relative;
background:radial-gradient(circle at 85% 88%,#2f6bff 0,rgba(47,107,255,0) 45%),radial-gradient(circle at 0% 15%,#14408a 0,rgba(20,64,138,0) 40%),linear-gradient(160deg,#081a3a,#0c2a5c 55%,#123a86)}
.logo{position:absolute;top:90px;left:80px;height:80px}.handle{position:absolute;top:112px;right:80px;font-size:28px;opacity:.85}
.orb{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 35%,#7cc0ff,#2f6bff 60%,#1b3f9e)}
.el{position:absolute;left:80px;right:80px;opacity:0}.acc{color:#5fb2ff}
h1{font-size:104px;line-height:1.05;font-weight:800;letter-spacing:-1px}
.sub{font-size:48px;line-height:1.4;opacity:.92}
.tag{display:inline-block;background:#2f6bff;border-radius:60px;padding:16px 38px;font-size:40px;font-weight:600}
.btn{display:inline-block;background:#2f6bff;border-radius:80px;padding:30px 60px;font-size:46px;font-weight:700}
.prog{position:absolute;bottom:0;left:0;height:10px;background:#5fb2ff}"""
_c = BRAND["colors"]
CSS = (CSS_T.replace("#081a3a", _c["bg1"]).replace("#0c2a5c", _c["bg2"]).replace("#123a86", _c["bg3"])
       .replace("#14408a", _c["bg3"]).replace("#5fb2ff", _c["accent"]).replace("#7cc0ff", _c["accent"])
       .replace("#2f6bff", _c["button"]).replace("#1b3f9e", _c["bg3"]).replace("color:#fff", "color:" + _c["text"])
       .replace("font-family:Poppins", f"font-family:'{BRAND.get('font', 'Poppins')}',Poppins"))

JS = """const els=[...document.querySelectorAll('.el')].map(e=>({e,i:+e.dataset.in,o:+e.dataset.out}));
const ease=x=>1-Math.pow(1-Math.min(Math.max(x,0),1),3);
window.render=function(t){for(const {e,i,o} of els){const a=ease((t-i)/0.5),z=ease((o-t)/0.35),v=Math.min(a,z);
e.style.opacity=v;e.style.transform=`translateY(${(1-a)*60-(1-z)*40}px)`;}
document.getElementById('o1').style.transform=`translate(${Math.sin(t*.6)*30}px,${Math.cos(t*.5)*40}px)`;
document.getElementById('o2').style.transform=`translate(${Math.cos(t*.4)*30}px,${Math.sin(t*.45)*50}px)`;
document.getElementById('prog').style.width=(t/DUR*100)+'%';};"""


def build_html(spec, starts, ends, dur):
    parts = []
    scenes = spec["scenes"] + [dict(spec["cta"], tag=None)]
    for k, (s, a, b) in enumerate(zip(scenes, starts, ends)):
        if k == len(scenes) - 1:
            b = dur + 1  # closing scene stays on screen to the end
        top = 420 if s.get("tag") else 560
        if s.get("tag"):
            parts.append(f'<div class="el" data-in="{a+.1:.2f}" data-out="{b:.2f}" style="top:420px"><div class="tag">{s["tag"]}</div></div>')
            top = 560
        parts.append(f'<div class="el" data-in="{a+.3:.2f}" data-out="{b:.2f}" style="top:{top}px"><h1>{s["title"]}</h1></div>')
        if s.get("body"):
            parts.append(f'<div class="el" data-in="{a+1.0:.2f}" data-out="{b:.2f}" style="top:{top + 300}px"><div class="sub">{s["body"]}</div></div>')
        if s.get("button"):
            parts.append(f'<div class="el" data-in="{a+1.2:.2f}" data-out="{b:.2f}" style="top:1000px"><div class="btn">{s["button"]}</div></div>')
            parts.append(f'<div class="el" data-in="{a+2.0:.2f}" data-out="{b:.2f}" style="top:1230px"><div class="sub" style="font-size:40px">Follow @{BRAND["handle"]}</div></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            '<div class="orb" id="o1" style="width:120px;height:120px;right:90px;top:300px"></div>'
            '<div class="orb" id="o2" style="width:240px;height:240px;left:-100px;top:1400px;opacity:.7"></div>'
            + (f'<img class="logo" src="{LOGO.as_uri()}">' if LOGO.exists() else f'<div class="logo" style="font-size:44px;font-weight:700">{BRAND["name"]}</div>')
            + f'<div class="handle">@{BRAND["handle"]}</div>'
            + "".join(parts) + f'<div class="prog" id="prog"></div><script>const DUR={dur:.2f};{JS}render(0);</script></body></html>')


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    ensure_voice()
    tmp = Path(tempfile.mkdtemp())
    lines = [s["say"] for s in spec["scenes"]] + [spec["cta"]["say"]]
    starts, ends, t = [], [], 0.3
    for i, line in enumerate(lines):
        d = speak(line, tmp / f"vo{i}.wav")
        starts.append(t); ends.append(t + d + GAP * 0.6); t += d + GAP
    dur = t + 1.5
    if dur > 90:
        sys.exit(f"Reel is {dur:.1f}s; Instagram reels via API should stay under 90s. Shorten the script.")
    html = tmp / "reel.html"; html.write_text(build_html(spec, starts, ends, dur))

    from playwright.sync_api import sync_playwright
    frames = tmp / "frames"; frames.mkdir()
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(f"file://{html}"); pg.wait_for_timeout(300)
        for f in range(int(dur * FPS)):
            pg.evaluate(f"render({f / FPS})")
            pg.screenshot(path=str(frames / f"{f:05d}.jpg"), type="jpeg", quality=90)
        pg.evaluate(f"render({starts[0] + 1.5})"); pg.screenshot(path=str(tmp / "cover.jpg"), type="jpeg", quality=92)
        b.close()

    pad = ("0.10*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.08*sin(2*PI*277.18*t)*(0.6+0.4*sin(2*PI*0.2*t+1))"
           "+0.07*sin(2*PI*329.63*t)*(0.6+0.4*sin(2*PI*0.3*t+2))+0.05*sin(2*PI*110*t)+0.12*sin(2*PI*55*t)*exp(-8*mod(t,0.5))")
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc='{pad}':s=44100:d={dur:.2f}",
       "-af", f"lowpass=f=1800,afade=t=in:d=1.5,afade=t=out:st={dur-2:.2f}:d=2,volume=0.35", str(tmp / "pad.wav"))
    inputs, labels, chains = ["-i", str(tmp / "pad.wav")], [], []
    for i, s in enumerate(starts):
        inputs += ["-i", str(tmp / f"vo{i}.wav")]
        ms = int(s * 1000); chains.append(f"[{i+1}]adelay={ms}|{ms}[v{i}]"); labels.append(f"[v{i}]")
    fc = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,highpass=f=80," \
         "acompressor=threshold=0.1:ratio=3,volume=1.6[v];[0][v]amix=inputs=2:normalize=0,alimiter=limit=0.95[out]"
    sh("ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "44100", "-t", f"{dur:.2f}", str(tmp / "mix.wav"))

    OUT.mkdir(parents=True, exist_ok=True)
    mp4, cover = OUT / f"{spec['id']}.mp4", OUT / f"{spec['id']}-cover.jpg"
    sh("ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames / "%05d.jpg"), "-i", str(tmp / "mix.wav"),
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(mp4))
    shutil.copy(tmp / "cover.jpg", cover)
    shutil.rmtree(tmp)
    print(json.dumps({"video": BASE_URL + mp4.name, "cover": BASE_URL + cover.name, "seconds": round(dur, 1)}))


if __name__ == "__main__":
    main()

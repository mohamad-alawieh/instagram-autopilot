# Weekly run

This is what the agent does every week (by itself on a schedule, or when someone runs
`/instagram-autopilot:weekly`). All paths are relative to the repo root.
Nothing here costs money: content is made in the Claude session, publishing is GitHub Actions + the Instagram API.

## 0. Get ready

- Work in a clone of this repo with push access to `main`.
- Install tools if missing: `pip install --break-system-packages piper-tts playwright pillow`
  and `python3 -m playwright install chromium` (skip what is already installed).
- Read, in order: `autopilot/brand.json`, `autopilot/voice.md`, `autopilot/history.md`,
  `autopilot/QUALITY.md`, then the SKILL.md files it names in `autopilot/ig-skills/`.

## 1. Health check (always report this first)

- Every entry in `autopilot/schedule.json` whose `time` has passed must appear in `autopilot/published.json`.
  If one is missing, the publisher is failing. Say so at the top of the summary and suggest:
  open the repo's Actions tab → Instagram publisher → the red run → read the error.
  Common causes: the `IG_ACCESS_TOKEN` secret expired or is missing; GitHub Pages is off; the image URL is wrong.
- If you can read the repo's workflow runs (GitHub API or `gh run list`), check the latest
  `refresh-token` job. If it failed, the `GH_PAT` secret has probably expired: tell the owner to make a
  new fine-grained token (Secrets: read and write, this repo only) and update `GH_PAT`, or posting will
  stop when the Instagram token expires.

## 2. Plan next week

- "Next week" is the next Monday–Sunday after today.
- Use `brand.json → schedule.days` for which days get which format (`carousel`, `single`, `reel`, `offer`).
  Post time is `schedule.time` in `schedule.timezone`.
- Use the ig-plan skill with voice.md's pillars. Rotate pillars; never repeat a topic in history.md.
  Use timely topics for the brand's industry where useful (a short web search is fine).
- Offers: use ONLY offers and prices from brand.json. If there are none, make the "offer" day a
  soft call-to-action post about the main product or service, with no price.
- Never invent statistics, reviews, client names or results.

## 3. Make each post

- **carousel** (5 slides) / **single** (1 slide) / **offer** (1 slide, layout `offer`):
  write a post spec and run `python3 autopilot/render_post.py spec.json`. It prints the public URLs.
  The look comes from `brand.json → theme`; never change it unless the owner asks.
  Folder name: `<yyyy>-<mm>-w<week-of-month>`. Look at every image; fix copy that was shrunk or looks crowded.
- **reel**: follow the reel steps in QUALITY.md (hook score, beats), then
  `python3 autopilot/make_reel.py spec.json`. It prints `video` and `cover` URLs. Look at a few frames
  (`ffmpeg -i docs/media/reels/<id>.mp4 -vf "select='eq(n\,90)+eq(n\,300)',scale=360:-1,tile=2x1" -frames:v 1 check.jpg`).
- Every caption passes the caption steps in QUALITY.md. Always include `brand.json → hashtags_always`,
  at most 5 hashtags in total.

## 4. Schedule

- Post times: `python3 -c "import sys; sys.path.insert(0,'autopilot'); from common import *; from datetime import date; print(post_time(load_brand(), date(2026,11,2)))"`
  (this handles daylight saving correctly).
- Append one entry per post to `autopilot/schedule.json`:
  - image post: `{"id": "...", "time": "...", "images": ["url", ...], "caption": "..."}`
  - reel: `{"id": "...", "time": "...", "video": "url", "cover": "url", "caption": "..."}`
  - `id` = `<date>-<topic-slug>`, unique.
- Validate: `python3 -c "import json; json.load(open('autopilot/schedule.json'))"`.

## 5. Record and push

- Append the week to `autopilot/history.md`: date, format, topic, hook score (reels), human score (captions).
- Commit everything in ONE commit and push to `main`. GitHub Pages republishes the media within a minute or two;
  the hourly publisher posts each entry when its time comes.
- First week of each month: also run the ig-audit skill over last month's posts in published.json and add 3 short lessons to history.md.

## 6. Summary for the owner

A short table: day, time, format, topic. Then the reel hook and its score, the caption human scores,
and the health check result. If anything failed and could not be fixed after 3 tries, say exactly what,
and schedule only what passed.

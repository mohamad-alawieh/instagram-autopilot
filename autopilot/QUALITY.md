# Quality gate for every post and reel

Run these from the repo root before anything goes into autopilot/schedule.json.
All tools are in autopilot/ig-skills (MIT, see README there). Read the matching
SKILL.md the first time you use a skill. Brand voice: autopilot/voice.md.

## Captions (every post and reel)

1. Write the caption following ig-caption/SKILL.md (Job A for reels, Job B for image posts).
2. Clean it:   `python3 -I autopilot/ig-skills/ig-human/humanize.py caption.txt --out caption.txt --report`
3. Lint it:    `python3 -I autopilot/ig-skills/ig-caption/caption.py caption.txt`
   Required: VERDICT READY (no FAIL lines). Exactly one ask. Max 5 hashtags.
4. Score it:   `python3 -I autopilot/ig-skills/ig-human/detect.py caption.txt`
   Target: HUMAN SCORE 65 or higher. If lower, fix the weakest signal it names and re-run (max 3 rounds).

## Reel scripts

1. Write 3 hook options per ig-reel/SKILL.md and rank them:
   `python3 -I autopilot/ig-skills/ig-reel/hookscore.py hooks.txt`
   Use the top hook. It must score 60 or higher, or write new options.
2. Time the script (one spoken line per line):
   `python3 -I autopilot/ig-skills/ig-reel/beats.py script.txt --target 25 --wpm 200   # Piper voices read at about 200 wpm`
   Required: hook under 3s, no beat over 4s, total 15–35s, the last line repeats a word from the hook.
3. Build it: write a spec JSON (see the docstring in autopilot/make_reel.py), one scene per
   beat, then `python3 autopilot/make_reel.py spec.json`. It prints the video and cover URLs.
   Look at a few frames before scheduling (ffmpeg can extract them).

## Carousels

Follow ig-carousel/SKILL.md for the cover and slide copy. Design with
`python3 autopilot/render_post.py post.json` (layouts are documented at the top of that file).
It prints a note when it had to shrink text: shorten that copy. Clean the slide text with humanize.py too.

## Planning and review

- Plan each week with ig-plan/SKILL.md, using voice.md and history.md.
- Once a month, review what was posted with ig-audit/SKILL.md (use the posts in autopilot/published.json).

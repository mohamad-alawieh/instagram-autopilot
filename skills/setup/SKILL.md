---
name: setup
description: >-
  Set up Instagram Autopilot for a business page: ask about the page, its industry, logo, topics and
  posting schedule, build the brand files, then walk the owner step by step through GitHub, a free
  Meta developer app, connecting Instagram and adding the repo secrets, run a live test post, and
  start the weekly schedule. Use when someone says "set up instagram autopilot", "set up my
  instagram agent", "connect my instagram page", or runs /instagram-autopilot:setup.
---

# Instagram Autopilot: setup wizard

You are setting up a free, automatic Instagram manager for a business. When you finish:

- the owner's **own GitHub repo** (copied from the template) holds their brand, post queue and media;
- **GitHub Pages** hosts the images and reels at public links (free);
- a **GitHub Actions** workflow publishes each post on time through Meta's **Instagram API** (free);
- a **weekly scheduled task** in Claude writes and designs next week's posts (or the owner runs
  `/instagram-autopilot:weekly` by hand).

Nothing in this setup costs money. Never suggest a paid tool unless the owner asks for one.

## How to run this wizard

- Talk to a non-technical business owner. Short messages, one step at a time, plain words.
- Ask questions in small groups (use a multiple-choice question tool if one is available).
- **Never ask the owner to paste a password or access token into the chat.** Tokens go straight
  into GitHub secrets. If they paste one anyway, tell them to generate a new one and not to share it.
- After each setup step, ask them to confirm it's done (or send a screenshot) before moving on.
  If a screen looks different, ask for a screenshot and adapt. Meta renames menus often.
- Keep a checklist (task list tool if available) so they can see progress.
- The full click-by-click guide is in `guide/SETUP_GUIDE.md` of this repo. Give the owner the steps
  in the chat. They can also open that file.

---

## Part 1. Learn about the page (questions)

Ask these, then read back a short summary and confirm it:

1. **Page:** business name, and Instagram handle (without @).
2. **What the business does** (its industry or "major"), and **who it's for**
   (specific: "parents in Beirut ordering birthday cakes", not "everyone").
3. **Location, and language** for posts (default: English).
4. **Products, services and offers.** Prices are optional, and only real ones:
   these are the only prices ever used in posts.
5. **Contact:** phone, email or website, and the link in bio (all optional).
6. **Logo:** "Do you have a logo?"
   - **Yes:** ask them to upload it (PNG with a transparent background is best).
   - **No:** offer to create a simple one (a monogram badge with the name).
7. **Brand colors:** "Use colors from your logo, or pick your own?" (default: from the logo).
8. **Tone:** e.g. warm and friendly / bold and fun / calm and expert / premium.
9. **Theme** (the visual style of every post and reel). There are 5:
   - **midnight**: a dark gradient in their colors with glowing accents. Modern and techy.
   - **clean**: a light off-white background, dark text and brand-color highlights. Friendly and airy.
   - **bold**: a solid brand-color background, big white type and highlighter accents. Loud and punchy.
   - **minimal**: pure white, black type, thin lines and one accent color. Calm and premium.
   - **elegant**: a warm cream background, serif headlines and refined accents. Boutique and classic.
   Once their logo and colors are ready (Part 3, steps 1–2), show them the real thing in their own brand:
   `python3 autopilot/preview_themes.py theme-preview.jpg` makes one image with all 5 themes side by side.
   Send it and ask them to pick a number. Don't commit the preview image.
   Suggest one based on the business: food, kids or retail → clean or bold; tech → midnight;
   law, clinics or finance → minimal; fashion, beauty or hospitality → elegant.
10. **Topics** (content pillars). Propose 4 pillars that fit the business, each with 2 example
   post ideas. Let the owner edit. Example for a bakery: "Behind the scenes", "Tips and how-tos",
   "Seasonal specials", "Offers and ordering".
11. **Things never to post:** default is politics, religion, competitors by name, and invented
    numbers or reviews. Ask if they want to add anything.
12. **Schedule:** posts per week (recommend **3 posts + 1 reel**; 2–7 is fine), which days,
    what time, and their time zone (IANA name, e.g. `Asia/Beirut`).
    Formats per day: `carousel` (5 slides), `single` (1 image), `reel` (voiceover video), `offer`.
13. **Reel voice:** free AI voices: `ryan` (US male), `lessac` (US female, warm), `amy` (US female),
    `alan` (UK male). Offer to make a 5-second sample of each.

Then show **sample topics for the first week** (a table: day, format, topic) and ask for approval.
Explain that the weekly run picks fresh topics every week from their pillars and never repeats one.

## Part 2. Create their repo (GitHub)

Walk them through, one step at a time:

1. **GitHub account:** if they don't have one, sign up free at github.com/signup and verify the email.
2. **Copy the template:** open the template repo page (the repo this plugin came from), click
   **Use this template → Create a new repository**. Set the owner to their account, name it
   (e.g. `instagram-autopilot`), choose **Public**, and click **Create repository**.
   - Public is required: free GitHub Pages and unlimited free Actions minutes need a public repo.
     Their posts are public anyway. Secrets stay private.
3. **Turn on GitHub Pages:** in their new repo, go to **Settings → Pages**. Under
   "Build and deployment", set **Source: Deploy from a branch**, **Branch: main**, folder **/docs**,
   and click **Save**. Their media link will be `https://<username>.github.io/<repo>/media/`.
4. **Make sure Actions are on:** open the **Actions** tab. If it asks, click
   **"I understand my workflows, go ahead and enable them"**.

Now get access to their repo so you can write files:
- If you have a tool to attach or add a GitHub repo (e.g. `add_repo`), use it with push access.
- Otherwise, if you have a shell with git and they are signed in to GitHub, clone it.
- If neither works, prepare the files and have them upload: repo → **Add file → Upload files**.

## Part 3. Build their brand files

In their repo:

1. **Logo:**
   - Uploaded: `python3 autopilot/make_logo.py prepare <their-file>`. It trims the logo and warns
     if it's too dark for dark backgrounds; if so, ask for a light/white version.
   - Created: `python3 autopilot/make_logo.py create "<Name>" --accent "<hex>" --button "<hex>" --tagline "<short word>"`.
   - Show them the logo and get approval.
2. **Colors:** `python3 autopilot/make_logo.py colors autopilot/assets/logo.png` suggests a palette
   (6-digit hex colors only). For midnight and bold, the background colors must be dark or strong enough
   for white text. Adjust if needed.
   - **Logo versions:** dark themes (midnight, bold) use `logo`; light themes (clean, minimal, elegant)
     use `logo_on_light`. A created logo has both (`logo.png` white, `logo-dark.png` dark). For an
     uploaded logo, check it reads on the chosen theme. If it doesn't, ask for the other version.
   - **Theme:** now make the theme preview (Part 1, question 9) and let them pick.
3. **`autopilot/brand.json`:** copy `brand.example.json` and fill in every field from Part 1:
   name, handle, industry, audience, contact, offers (only real ones), pillars, avoid list, colors,
   `theme`, `logo` and `logo_on_light` paths, `voice`, schedule (`timezone`, `time`, `days` map, `plan_day`), `hashtags_always`
   (their brand tag plus their city), `media_base_url` = `https://<username>.github.io/<repo>/media/`,
   and `repo` = `<username>/<repo>`.
4. **`autopilot/voice.md`:** fill in `voice.template.md` from the answers. Delete the template braces.
5. **Preview:** render one cover slide and one offer or CTA slide in their chosen theme with
   `autopilot/render_post.py`, and show them. Adjust the theme, colors, logo or tone until they're happy.
   They can change the theme any time later: just ask, or edit `theme` in brand.json.
6. Commit everything and push to `main`.

## Part 4. Connect Instagram (Meta developer app, free)

Requirements: the Instagram account must be **Professional (Business or Creator)**.
If it's personal: Instagram app → **Settings → Account type and tools → Switch to professional account**.

Walk them through:

1. **Meta developer account:** go to **developers.facebook.com**, click **Get Started** (or
   **Log in**) with their Facebook account, accept the terms, verify with a phone or email if asked,
   and choose a role (e.g. "Developer").
2. **Create the app:** **My Apps → Create App**. Name it (e.g. "<Business> Publisher"), add a
   contact email, then choose the use case **"Manage messaging & content on Instagram"**. If asked
   about a business portfolio, either is fine. Click **Create app**.
3. **Open the Instagram setup:** on the app **Dashboard**, click
   **"Customize the Manage messaging & content on Instagram use case"**, then
   **API setup with Instagram business login**.
4. **Permissions:** make sure `instagram_business_basic` and
   **`instagram_business_content_publish`** are listed. Add the second one if it's missing.
5. **Add the Instagram account as a tester** (needed because the app stays in development mode):
   **App roles → Roles → Add People → Instagram Tester**, type their Instagram username, click **Add**.
   Then on instagram.com, logged into that account: **Settings → Apps and websites → Tester invites → Accept**
   (direct link: instagram.com/accounts/manage_access/). Invites can take a minute to show.
6. **Generate the token:** back in **API setup with Instagram business login → Generate access tokens**,
   the account should be listed (if not, click **Add account** and log in). Click **Generate token**,
   log in or approve, tick the agreement box, and **copy the token**. Do NOT paste it in the chat.
   The app can stay **Unpublished**. Development mode works for their own account without app review.

## Part 5. Add the secrets to their repo

1. **Instagram token:** their repo → **Settings → Secrets and variables → Actions →
   New repository secret**. Name: `IG_ACCESS_TOKEN`. Secret: paste the token. Click **Add secret**.
2. **Auto-renewal key** (keeps the 60-day Instagram token alive):
   github.com → profile picture → **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token**. Name it "autopilot token refresh", set expiration to the
   longest allowed, **Repository access: Only select repositories → their repo**,
   **Permissions → Repository permissions → Secrets: Read and write**. Generate it, copy it, and add
   it as a second repository secret named `GH_PAT`.
   - Remind them the GitHub token itself expires on the date they picked. Before then they need to
     make a new one and update `GH_PAT` (the weekly run warns them).

## Part 6. Live test

1. Create a "welcome" post with `render_post.py` (single image: who they are and what's coming),
   write its caption (run the caption checks in `autopilot/QUALITY.md`), and add it to
   `autopilot/schedule.json` with `time` set to now (`post_time()` in `autopilot/common.py`) and
   `id` `welcome`. Commit and push.
2. Wait about 2 minutes for GitHub Pages to publish the image. Then the owner (or you, if you can call
   the GitHub API) runs it: **Actions → Instagram publisher → Run workflow**, type `welcome`
   in the box, and click **Run workflow**.
3. A green check means it's live. Ask them to look at their Instagram.
   A red X: open the run → **publish** step and read the error (a screenshot is fine). Common fixes:
   - "Invalid OAuth access token": the secret is wrong or missing. Generate a new token and update the secret.
   - "Media ID is not available" or an image URL error: Pages isn't on, or hasn't published yet.
     Check Settings → Pages, wait 2 minutes, and run it again.
   - "Application does not have permission": add `instagram_business_content_publish` (Part 4, step 4).
   - "The user is not an Instagram Business": switch the account to Professional.

## Part 7. Turn on the weekly run

1. Make the **first week** now: follow `autopilot/RUNBOOK.md` steps 2–5.
2. **Weekly scheduled task:** if you have a tool to create scheduled or recurring tasks, create one
   that runs every `plan_day` at midday in their time zone (a few minutes before the hour), with this
   prompt (fill in the repo):
   > Attach and clone the GitHub repo `<username>/<repo>` with push access. Follow
   > `autopilot/RUNBOOK.md` exactly to plan, design, check and schedule next week's Instagram posts,
   > then give me the summary it describes. Nothing paid. Never invent numbers or reviews.
   If you can't create scheduled tasks, tell them to run `/instagram-autopilot:weekly` once a week,
   on their plan day.

## Part 8. Confirmation

Finish with a clear confirmation:

- A table of the first week: **day, date, time, format, topic**.
- Their **theme**, colors and reel voice.
- **Posts per week**: N posts + M reels, at HH:MM their time, on which days.
- When the weekly planning runs, and what they'll receive (a summary with the new topics).
- What still needs them: replying to comments and DMs; telling the agent about new offers or prices
  (edit `brand.json` or just ask); and renewing `GH_PAT` before it expires.
- How to pause: in their repo, Actions → Instagram publisher → **⋯ → Disable workflow**.

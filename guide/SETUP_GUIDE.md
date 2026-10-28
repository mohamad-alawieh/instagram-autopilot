# Setup guide (step by step)

This guide sets up Instagram Autopilot for one Instagram page. It takes about 30 minutes, once.
Everything here is **free**.

The easiest way is to let Claude walk you through it: install the plugin (see the README) and run
**`/instagram-autopilot:setup`**. Claude asks about your page, makes your brand files, and guides
you through each step below. This page is the same steps, written out in full.

**What you'll end up with**

| Piece | What it does | Cost |
|---|---|---|
| Your GitHub repo | Holds your brand, logo, post queue, images and reels | Free |
| GitHub Pages | Gives each image and video a public link Instagram can read | Free |
| GitHub Actions | Checks every hour and publishes posts when their time comes | Free (public repo) |
| Meta developer app | Gives your repo permission to post to your Instagram | Free |
| Claude, weekly | Writes, designs and schedules next week's posts | Your existing Claude plan |

**Before you start, you need:**
- an Instagram account set to **Professional** (Business or Creator). To switch: Instagram app →
  profile → ☰ → **Settings and activity → Account type and tools → Switch to professional account**;
- a Facebook account (for the Meta developer account);
- a computer with a web browser.

---

## Step 1. Create a free GitHub account

1. Go to **github.com/signup**.
2. Enter your email, a password and a username. Your username appears in your media links
   (`https://<username>.github.io/...`).
3. Verify your email with the code GitHub sends.

## Step 2. Copy the template into your own repo

1. Open the Instagram Autopilot template on GitHub (the repo this guide is in).
2. Click the green **Use this template** button → **Create a new repository**.
3. **Owner:** your account. **Repository name:** e.g. `instagram-autopilot`.
4. Choose **Public**. This is required for free GitHub Pages and free unlimited Actions.
   Your posts are public on Instagram anyway, and your secrets (step 5) stay private.
5. Click **Create repository**.

## Step 3. Turn on GitHub Pages (free image hosting)

1. In your new repo, click **Settings** (top bar) → **Pages** (left sidebar).
2. Under **Build and deployment**: set **Source** to **Deploy from a branch**, **Branch** to **main**,
   and the folder to **/docs**. Click **Save**.
3. After a minute, the page shows "Your site is live at `https://<username>.github.io/<repo>/`".
   Your media link is that address plus `media/`.
4. Open the **Actions** tab. If you see "Workflows aren't being run on this repository", click
   **I understand my workflows, go ahead and enable them**.

## Step 4. Connect Instagram through a free Meta developer app

### 4a. Create your Meta developer account
1. Go to **developers.facebook.com** and click **Get Started** (or **Log in**).
2. Log in with Facebook, accept the developer terms, and verify your phone or email if asked.
3. Pick a role such as **Developer**, and finish.

### 4b. Create the app
1. Click **My Apps → Create App**.
2. **App name:** e.g. "Brightside Publisher". **Contact email:** yours. Click **Next**.
3. **Use case:** choose **Manage messaging & content on Instagram**. Click **Next**.
4. If asked about a business portfolio, choose either option. Click **Next**, then **Create app**.
   Re-enter your Facebook password if asked.

### 4c. Open the Instagram API setup
1. On the app **Dashboard**, click **Customize the Manage messaging & content on Instagram use case**.
2. Open **API setup with Instagram business login**.
3. Under **permissions**, make sure these two are listed. If one is missing, click **Add**:
   - `instagram_business_basic`
   - `instagram_business_content_publish`

### 4d. Add your Instagram account as a tester
The app stays in development mode, which is fine for your own page, but the account must be a tester.
1. In the left menu: **App roles → Roles → Add People**.
2. Choose **Instagram Tester**, type your Instagram username, select it, and click **Add**.
3. Open **instagram.com** on a computer, logged in as that page. Go to **Settings → Apps and websites →
   Tester invites** (direct link: `instagram.com/accounts/manage_access/`) and click **Accept**.
   If the invite isn't there yet, wait a minute and refresh.

### 4e. Generate the access token
1. Go back to **Use cases → Manage messaging & content on Instagram → API setup with Instagram business login**.
2. Under **Generate access tokens**, your account is listed. If it isn't, click **Add account** and log in.
3. Click **Generate token**, approve the permissions, tick the agreement box, and **copy the token**.
   It's a long string, often starting with `IG`.
4. **Keep it private.** Don't paste it in a chat or an email. It goes only into GitHub in the next step.

You don't need to publish the app or submit it for review.

## Step 5. Add the secrets to your repo

### 5a. The Instagram token
1. Your repo → **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. **Name:** `IG_ACCESS_TOKEN`. **Secret:** paste the token. Click **Add secret**.

### 5b. The auto-renewal key (recommended)
Instagram tokens last 60 days. This key lets the workflow renew yours on the 1st and 15th of every month.
1. On GitHub: your profile picture → **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token**.
2. **Name:** "autopilot token refresh". **Expiration:** the longest allowed. Note the date.
3. **Repository access:** **Only select repositories** → your autopilot repo.
4. **Permissions → Repository permissions → Secrets:** **Read and write**.
5. Click **Generate token** and copy it.
6. Add it to your repo exactly like 5a, with the name **`GH_PAT`**.
7. Before the expiration date, make a new one and update `GH_PAT`.

## Step 6. Fill in your brand

If you're using the Claude wizard, it does this for you. To do it by hand:

1. Copy `autopilot/brand.example.json` to `autopilot/brand.json` and edit every field: your name,
   handle, industry, audience, contact, real offers and prices, topics ("pillars"), colors, time zone,
   which days get which format, and
   `media_base_url` = `https://<username>.github.io/<repo>/media/`.
2. Put your logo at `autopilot/assets/logo.png`. A light or white logo works best on the dark post
   background. No logo? Run `python3 autopilot/make_logo.py create "Your Name"`.
3. Copy `autopilot/voice.template.md` to `autopilot/voice.md` and fill it in.

## Step 7. Test it

1. Add a test post to `autopilot/schedule.json` (Claude can make one), with `"id": "welcome"`, and
   push it. Wait 2 minutes for Pages to publish the image.
2. Repo → **Actions → Instagram publisher → Run workflow**. Type `welcome` in the box and click
   **Run workflow**.
3. **Green check:** the post is on your Instagram. **Red X:** click the run → **publish** to see the error.

| Error says | Fix |
|---|---|
| Invalid OAuth access token | The `IG_ACCESS_TOKEN` secret is wrong. Generate a new token (4e) and update the secret (5a). |
| IG_ACCESS_TOKEN secret is not set | Do step 5a. |
| Media / image URL errors | Pages isn't on (step 3), or hasn't published yet. Wait 2 minutes and run it again. |
| Application does not have permission | Add `instagram_business_content_publish` (4c). |
| Not an Instagram Business / professional account | Switch the account to Professional. |

## Step 8. Weekly posts

- **With a Claude scheduled task:** the setup wizard creates one that runs on your planning day.
  It writes and designs next week's posts, checks them, adds them to the queue, and sends you a summary.
- **By hand:** once a week, run **`/instagram-autopilot:weekly`** in Claude.

The workflow publishes each post at its time, checking every hour, so a post can go out up to an
hour after its scheduled time.

**To pause everything:** Actions → Instagram publisher → **⋯ → Disable workflow**.

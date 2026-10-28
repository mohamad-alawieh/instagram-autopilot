#!/usr/bin/env python3
"""Publish due Instagram posts and reels from autopilot/schedule.json.

Uses the Instagram API with Instagram Login (graph.instagram.com).
Env: IG_ACCESS_TOKEN (required). Optional: FORCE_ID=<post id> publishes that post now.
Each published post is recorded in autopilot/published.json so it never posts twice.
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

API = "https://graph.instagram.com/v23.0"
HERE = Path(__file__).resolve().parent
SCHEDULE = HERE / "schedule.json"
PUBLISHED = HERE / "published.json"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()


def call(method, path, params):
    params = dict(params, access_token=TOKEN)
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} failed: {e.code} {e.read().decode()[:500]}")


def wait_ready(container_id, tries=20):
    for _ in range(tries):
        status = call("GET", container_id, {"fields": "status_code"}).get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container_id} status {status}")
        time.sleep(10)
    raise RuntimeError(f"container {container_id} not ready after {tries * 10}s")


def publish(ig_id, post):
    caption = post.get("caption", "")
    if post.get("video"):  # Reel
        params = {"media_type": "REELS", "video_url": post["video"], "caption": caption, "share_to_feed": "true"}
        if post.get("cover"):
            params["cover_url"] = post["cover"]
        c = call("POST", f"{ig_id}/media", params)["id"]
        wait_ready(c, tries=50)
        return call("POST", f"{ig_id}/media_publish", {"creation_id": c})["id"]
    images = post["images"]
    if len(images) == 1:
        c = call("POST", f"{ig_id}/media", {"image_url": images[0], "caption": caption})["id"]
    else:
        children = []
        for url in images:
            child = call("POST", f"{ig_id}/media", {"image_url": url, "is_carousel_item": "true"})["id"]
            wait_ready(child)
            children.append(child)
        c = call("POST", f"{ig_id}/media",
                 {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})["id"]
    wait_ready(c)
    return call("POST", f"{ig_id}/media_publish", {"creation_id": c})["id"]


def main():
    posts = json.loads(SCHEDULE.read_text())
    done = json.loads(PUBLISHED.read_text()) if PUBLISHED.exists() else {}
    force = os.environ.get("FORCE_ID", "").strip()
    now = datetime.now(timezone.utc)

    due = [p for p in posts if p["id"] not in done and
           (p["id"] == force or (not force and datetime.fromisoformat(p["time"]) <= now))]
    if not due:
        print("Nothing due.")
        return
    if not TOKEN:
        sys.exit("::error::IG_ACCESS_TOKEN secret is not set. See guide/SETUP_GUIDE.md, step 5.")

    me = call("GET", "me", {"fields": "user_id,username"})
    ig_id = me.get("user_id") or me["id"]
    print(f"Publishing as @{me.get('username')}")

    failed = False
    for p in sorted(due, key=lambda p: p["time"]):
        try:
            media_id = publish(ig_id, p)
            done[p["id"]] = {"media_id": media_id, "published_at": now.isoformat()}
            print(f"OK   {p['id']} -> {media_id}")
        except Exception as e:  # keep going, report at the end
            failed = True
            msg = str(e).replace("\n", " ")[:900]
            print(f"FAIL {p['id']}: {msg}")
            print(f"::error title=Instagram publish failed ({p['id']})::{msg}")
        PUBLISHED.write_text(json.dumps(done, indent=2) + "\n")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

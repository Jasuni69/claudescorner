"""
reddit_brief.py — fetch top posts from subreddits via Reddit JSON API, write markdown brief
Output: E:\\2026\\ClaudesCorner\\memory\\reddit-brief.md

Changes vs RSS version:
- Uses /r/<sub>/hot.json instead of .rss — returns score + num_comments in one call
- --min-karma N  filter out posts below N upvotes (default 5)
- --fetch-comments  fetch top comment preview for each post (slow: 1 HTTP call per post)
- --dry-run  print to stdout only, do not write file
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import urllib.request

SUBREDDITS = [
    "claudexplorers",
    "ClaudeAI",
    "MicrosoftFabric",
]

OUTPUT = Path(r"E:\2026\ClaudesCorner\memory\reddit-brief.md")
TOP_N = 8
DEFAULT_MIN_KARMA = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}


def fetch_listing(subreddit: str, limit: int = TOP_N * 3) -> list[dict]:
    """Fetch posts from hot listing. Returns raw post dicts with score/num_comments."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    posts = []
    for child in data["data"]["children"]:
        p = child["data"]
        if p.get("stickied"):
            continue  # skip mod posts
        posts.append({
            "title": p["title"],
            "link": f"https://www.reddit.com{p['permalink']}",
            "author": p.get("author", ""),
            "score": p.get("score", 0),
            "num_comments": p.get("num_comments", 0),
            "url": p.get("url", ""),
        })
    return posts


def fetch_top_comment(post_link: str) -> str | None:
    """Fetch the top comment body for a post. Returns first 120 chars or None."""
    try:
        post_id = post_link.rstrip("/").split("/comments/")[1].split("/")[0]
        sub = post_link.split("/r/")[1].split("/")[0]
        api_url = f"https://www.reddit.com/r/{sub}/comments/{post_id}.json?limit=5"
        req = urllib.request.Request(api_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        for child in data[1]["data"]["children"]:
            if child["kind"] == "t1":
                body = child["data"].get("body", "").replace("\n", " ").strip()
                if body and body != "[deleted]":
                    return body[:120] + ("…" if len(body) > 120 else "")
    except Exception:
        pass
    return None


def build_brief(min_karma: int, fetch_comments: bool) -> str:
    lines = [f"# Reddit Brief — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for sub in SUBREDDITS:
        lines.append(f"## r/{sub}")
        try:
            all_posts = fetch_listing(sub)
            posts = [p for p in all_posts if p["score"] >= min_karma][:TOP_N]
            if not posts:
                lines.append(f"- (no posts above {min_karma} karma)")
            for p in posts:
                author = p["author"].lstrip("/u/").lstrip("u/")
                score_str = f"↑{p['score']:,}"
                comment_str = f"💬{p['num_comments']:,}"
                lines.append(f"- [{p['title']}]({p['link']}) — u/{author} {score_str} {comment_str}")
                if fetch_comments:
                    top = fetch_top_comment(p["link"])
                    if top:
                        lines.append(f"  > {top}")
        except Exception as e:
            lines.append(f"- ERROR: {e}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Reddit brief and write markdown")
    parser.add_argument(
        "--min-karma", type=int, default=DEFAULT_MIN_KARMA,
        help=f"Filter out posts below this score (default: {DEFAULT_MIN_KARMA})"
    )
    parser.add_argument(
        "--fetch-comments", action="store_true",
        help="Fetch top comment preview for each post (slow: 1 HTTP call per post)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print to stdout only, do not write file"
    )
    args = parser.parse_args()

    brief = build_brief(min_karma=args.min_karma, fetch_comments=args.fetch_comments)

    if args.dry_run:
        print(brief)
    else:
        OUTPUT.write_text(brief, encoding="utf-8")
        print(f"Written to {OUTPUT}")
        print(brief.encode("ascii", errors="replace").decode("ascii"))

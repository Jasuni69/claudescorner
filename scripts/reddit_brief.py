"""
reddit_brief.py — fetch top posts from subreddits via RSS, write markdown brief
Output: E:\\2026\\ClaudesCorner\\memory\\reddit-brief.md
"""

import json
import xml.etree.ElementTree as ET
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}

NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_post(url: str) -> dict:
    """Fetch full post body + top comments from a Reddit post URL."""
    post_id = url.rstrip("/").split("/comments/")[1].split("/")[0]
    sub = url.split("/r/")[1].split("/")[0]
    api_url = f"https://www.reddit.com/r/{sub}/comments/{post_id}.json?limit=10"
    req = urllib.request.Request(api_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    post = data[0]["data"]["children"][0]["data"]
    comments = [
        c["data"]["body"]
        for c in data[1]["data"]["children"]
        if c["kind"] == "t1" and c["data"].get("body")
    ]
    return {"title": post["title"], "body": post.get("selftext", ""), "comments": comments}


def fetch_rss(subreddit: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/.rss"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)
    posts = []
    for entry in root.findall("atom:entry", NS)[:TOP_N]:
        title = entry.findtext("atom:title", default="", namespaces=NS).strip()
        link_el = entry.find("atom:link", NS)
        link = link_el.attrib.get("href", "") if link_el is not None else ""
        author = entry.findtext("atom:author/atom:name", default="", namespaces=NS).strip()
        posts.append({"title": title, "link": link, "author": author})
    return posts


def build_brief() -> str:
    lines = [f"# Reddit Brief — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for sub in SUBREDDITS:
        lines.append(f"## r/{sub}")
        try:
            posts = fetch_rss(sub)
            for p in posts:
                author = p['author'].lstrip("/u/").lstrip("u/")
                lines.append(f"- [{p['title']}]({p['link']}) - u/{author}")
        except Exception as e:
            lines.append(f"- ERROR: {e}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    brief = build_brief()
    OUTPUT.write_text(brief, encoding="utf-8")
    print(f"Written to {OUTPUT}")
    print(brief.encode("ascii", errors="replace").decode("ascii"))

"""
x_brief.py — fetch recent tweets by scraping X profiles via Playwright
Output: E:\\2026\\ClaudesCorner\\memory\\x-brief.md

Uses the existing Chrome user profile (already logged in as @engramzero).
Chrome must NOT be running when this script runs (profile lock conflict).
Run headlessly via Windows Task Scheduler.
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

ACCOUNTS = [
    "AnthropicAI",
    "karpathy",
    "ylecun",
    "fchollet",
    "demishassabis",
    "lexfridman",
    "paulg",
    "sama",
    "lilianweng",
    "NASA",
]

OUTPUT = Path(r"E:\2026\ClaudesCorner\memory\x-brief.md")
CHROME_PROFILE = Path(r"C:\Users\JasonNicolini\AppData\Local\Google\Chrome\User Data")
TOP_N = 5


async def fetch_tweets(page, username: str) -> list[str]:
    await page.goto(f"https://x.com/{username}", wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(3000)
    articles = await page.query_selector_all("article")
    tweets = []
    for art in articles[:TOP_N]:
        text = await art.inner_text()
        line = " ".join(text.split()).strip()[:280]
        if line:
            tweets.append(line)
    return tweets


async def build_brief() -> str:
    lines = [f"# X Brief — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        page = await browser.new_page()
        for account in ACCOUNTS:
            lines.append(f"## @{account}")
            try:
                tweets = await fetch_tweets(page, account)
                if not tweets:
                    lines.append("- (no recent tweets)")
                for t in tweets:
                    lines.append(f"- {t}")
            except Exception as e:
                lines.append(f"- ERROR: {e}")
            lines.append("")
        await browser.close()
    return "\n".join(lines)


if __name__ == "__main__":
    brief = asyncio.run(build_brief())
    OUTPUT.write_text(brief, encoding="utf-8")
    print(f"Written to {OUTPUT}")
    print(brief.encode("ascii", errors="replace").decode("ascii"))

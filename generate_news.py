#!/usr/bin/env python3
"""
Daily AI News Generator
Fetches AI news from RSS feeds and generates a markdown summary using Claude.

Usage:
  python generate_news.py              # generates for today
  python generate_news.py 2026-03-24   # generates for a specific date

Required environment variables:
  ANTHROPIC_API_KEY   - Your Anthropic API key
  GITHUB_TOKEN        - GitHub personal access token (for git push)

Optional environment variables:
  REPO_PATH           - Path to the repo (defaults to script directory)
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from datetime import date
from xml.etree import ElementTree as ET

# ── Configuration ─────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_PATH = os.environ.get("REPO_PATH", os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR = os.path.join(REPO_PATH, "news")

# AI-focused RSS feeds (no API key required)
RSS_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Wired AI", "https://www.wired.com/feed/category/artificial-intelligence/latest/rss"),
    ("Ars Technica Tech", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
]

# Hacker News search for AI stories (free, no key needed)
HN_API = "https://hn.algolia.com/api/v1/search?query=AI+LLM+artificial+intelligence&tags=story&numericFilters=points>50&hitsPerPage=10"


# ── Fetch News ─────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=10):
    """Fetch a URL and return the response body as bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_rss(source_name, url):
    """Parse an RSS feed and return a list of article dicts."""
    articles = []
    try:
        data = fetch_url(url)
        root = ET.fromstring(data)
        for item in root.findall(".//item")[:6]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            # Strip HTML tags from description
            desc = _strip_tags(desc)[:400]
            if title and link:
                articles.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "description": desc,
                })
    except Exception as e:
        print(f"  [warn] {source_name}: {e}")
    return articles


def fetch_hn():
    """Fetch top AI stories from Hacker News."""
    articles = []
    try:
        data = fetch_url(HN_API)
        hits = json.loads(data).get("hits", [])
        for h in hits[:8]:
            title = h.get("title", "").strip()
            url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            points = h.get("points", 0)
            comments = h.get("num_comments", 0)
            if title:
                articles.append({
                    "source": "Hacker News",
                    "title": title,
                    "link": url,
                    "description": f"{points} points, {comments} comments on Hacker News",
                })
    except Exception as e:
        print(f"  [warn] Hacker News: {e}")
    return articles


def _strip_tags(text):
    """Remove HTML tags from a string."""
    import re
    return re.sub(r"<[^>]+>", "", text).strip()


def gather_articles():
    """Collect articles from all sources."""
    print("Fetching news sources…")
    articles = []
    for name, url in RSS_FEEDS:
        found = fetch_rss(name, url)
        print(f"  {name}: {len(found)} articles")
        articles.extend(found)
    hn = fetch_hn()
    print(f"  Hacker News: {len(hn)} articles")
    articles.extend(hn)
    print(f"Total: {len(articles)} articles collected")
    return articles


# ── Generate Summary with Claude ───────────────────────────────────────────────

def generate_summary(articles, target_date):
    """Call Claude API to produce a formatted markdown news digest."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    articles_text = "\n\n".join(
        f"[{a['source']}] {a['title']}\nURL: {a['link']}\n{a['description']}"
        for a in articles
    )

    # Format date nicely for the header
    y, m, d = target_date.split("-")
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    nice_date = f"{months[int(m)-1]} {int(d)}, {y}"

    prompt = f"""You are the editor of "AI News Daily", a concise, high-quality AI news digest.

Today is {nice_date}. Based on the articles below, write a markdown news digest following this exact format:

---

# AI News Digest — {nice_date}

*Your daily briefing on artificial intelligence*

---

## Top Stories

[Write 3-5 of the most significant stories as short paragraphs. Each story should have:
- A ### heading with a descriptive title (not just the article title)
- 2-3 sentences explaining what happened and why it matters
- A [Read more →](URL) link using the actual source URL]

---

## Quick Hits

[8-12 bullet points covering additional stories. Format: **Company/Topic** brief one-sentence update]

---

## Trend Watch

[1-2 paragraphs analyzing the broader trends and patterns visible in today's news. Be insightful and forward-looking.]

---

*Generated by AI News Daily · [View Archive](#)*

---

SOURCE ARTICLES:

{articles_text}

Write the complete digest now. Be concise, informative, and engaging. Use the actual URLs from the source articles."""

    print("Generating summary with Claude…")
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── Save & Publish ─────────────────────────────────────────────────────────────

def save_news(content, target_date):
    """Write the markdown file and update news/index.json."""
    os.makedirs(NEWS_DIR, exist_ok=True)

    filepath = os.path.join(NEWS_DIR, f"{target_date}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filepath}")

    # Update index.json
    index_path = os.path.join(NEWS_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"dates": []}

    if target_date not in index["dates"]:
        index["dates"].insert(0, target_date)
        # Keep only the last 90 days in the index
        index["dates"] = index["dates"][:90]

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Updated: {index_path}")

    return filepath


def git_push(target_date):
    """Stage, commit, and push the new news files."""
    def run(cmd):
        result = subprocess.run(cmd, cwd=REPO_PATH, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [warn] {' '.join(cmd)}: {result.stderr.strip()}")
        return result

    print("Pushing to GitHub…")
    run(["git", "config", "user.email", "ai-news-bot@users.noreply.github.com"])
    run(["git", "config", "user.name", "AI News Bot"])
    run(["git", "add", os.path.join("news", f"{target_date}.md"), os.path.join("news", "index.json")])
    result = run(["git", "commit", "-m", f"news: add AI digest for {target_date}"])
    if "nothing to commit" in result.stdout + result.stderr:
        print("  Nothing new to commit.")
        return
    # Use token in push URL so it never gets stored in .git/config
    remote_url = f"https://{GITHUB_TOKEN}@github.com/danhedrick1/ai-news.git"
    run(["git", "push", remote_url, "main"])
    print("  Done.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

    # Basic date validation
    try:
        date.fromisoformat(target_date)
    except ValueError:
        print(f"ERROR: Invalid date format '{target_date}'. Use YYYY-MM-DD.")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  AI News Generator — {target_date}")
    print(f"{'='*50}\n")

    articles = gather_articles()

    if not articles:
        print("ERROR: No articles fetched. Check your internet connection.")
        sys.exit(1)

    content = generate_summary(articles, target_date)
    save_news(content, target_date)

    if GITHUB_TOKEN:
        git_push(target_date)
    else:
        print("\nNote: GITHUB_TOKEN not set — skipping git push.")
        print("Run manually: git add news/ && git commit -m 'news: add digest' && git push")

    print(f"\nDone! View at: https://danhedrick1.github.io/ai-news\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Daily AI News Generator — Enhanced Edition
Multi-tier source coverage with impact-based ranking.

Sources are grouped by trust/signal tier. Stories are scored by:
  - Source tier weight (primary lab blogs > curated analysis > industry trade press)
  - Hacker News engagement (points + comments from last 24h)
  - Cross-source signal (same story appearing in multiple outlets = higher impact)

Usage:
  python generate_news.py              # today
  python generate_news.py 2026-03-24   # specific date

Required env vars (in .env):
  ANTHROPIC_API_KEY
  GITHUB_TOKEN
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.error
from datetime import date, datetime, timezone, timedelta
from xml.etree import ElementTree as ET

# ── Config ─────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
REPO_PATH         = os.environ.get("REPO_PATH", os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR          = os.path.join(REPO_PATH, "news")

# ── Sources by tier ────────────────────────────────────────────────────────────
#
# Tier weights determine base impact score for ranking.
# primary   = direct from labs, highest trust
# analysis  = curated expert voices, low hype
# research  = raw arXiv papers
# industry  = trade press, higher volume, used selectively
#
SOURCES = {
    "primary": [
        # Anthropic has no public RSS — covered via HN + industry sources
        ("OpenAI Blog",         "https://openai.com/blog/rss.xml"),
        ("Google DeepMind",     "https://deepmind.google/blog/rss.xml"),
        ("Google AI Blog",      "https://blog.google/technology/ai/rss/"),
        ("Meta AI Research",    "https://research.facebook.com/feed/"),
        ("Microsoft AI Blog",   "https://blogs.microsoft.com/ai/feed/"),
        ("Hugging Face Blog",   "https://huggingface.co/blog/feed.xml"),
    ],
    "analysis": [
        ("Import AI (Jack Clark)",        "https://importai.substack.com/feed"),
        ("The Batch (DeepLearning.AI)",   "https://www.deeplearning.ai/the-batch/feed/"),
        ("MIT Technology Review",         "https://www.technologyreview.com/feed/"),
        ("One Useful Thing (Mollick)",    "https://www.oneusefulthing.org/feed"),
        ("Zvi Mowshowitz",                "https://thezvi.substack.com/feed"),
        ("Nathan Benaich / Air Street",   "https://nathanbenaich.substack.com/feed"),
        ("The Neuron",                    "https://www.theneurondaily.com/rss"),
        ("The Neuron (Substack)",         "https://theneurondaily.substack.com/feed"),
        ("Interconnects (Hadsell)",       "https://www.interconnects.ai/feed"),
    ],
    "research": [
        ("arXiv cs.AI",  "http://rss.arxiv.org/rss/cs.AI"),
        ("arXiv cs.LG",  "http://rss.arxiv.org/rss/cs.LG"),
        ("arXiv cs.CL",  "http://rss.arxiv.org/rss/cs.CL"),   # NLP / LLMs
    ],
    "industry": [
        ("Ars Technica",    "https://feeds.arstechnica.com/arstechnica/technology-lab"),
        ("VentureBeat AI",  "https://venturebeat.com/ai/feed/"),
        ("AI News",         "https://www.artificialintelligence-news.com/feed/"),
        ("The Verge AI",    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("Wired AI",        "https://www.wired.com/feed/category/artificial-intelligence/latest/rss"),
    ],
}

TIER_WEIGHT = {
    "primary":  10,
    "analysis":  8,
    "research":  5,
    "industry":  3,
}

# HN: top AI stories from last 48h (wider window, lower threshold for reliability)
HN_SEARCH = (
    "https://hn.algolia.com/api/v1/search"
    "?query=AI+LLM+GPT+language+model+machine+learning"
    "&tags=story"
    "&numericFilters=points>10"
    "&hitsPerPage=30"
)


# ── Fetching ───────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Bot/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def parse_rss(data):
    """Parse an RSS/Atom feed, return list of (title, link, description) tuples."""
    items = []
    try:
        root = ET.fromstring(data)
        # RSS 2.0
        for item in root.findall(".//item"):
            title = strip_html(item.findtext("title") or "")
            link  = (item.findtext("link") or "").strip()
            desc  = strip_html(item.findtext("description") or "")[:500]
            if title and link:
                items.append((title, link, desc))
        # Atom
        if not items:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//a:entry", ns):
                title = strip_html(entry.findtext("a:title", namespaces=ns) or "")
                link_el = entry.find("a:link", ns)
                link  = (link_el.get("href", "") if link_el is not None else "").strip()
                desc  = strip_html(entry.findtext("a:summary", namespaces=ns) or "")[:500]
                if title and link:
                    items.append((title, link, desc))
    except ET.ParseError:
        pass
    return items


def fetch_rss_sources():
    """Fetch all RSS sources and return a list of article dicts with metadata."""
    articles = []
    seen_links = set()

    for tier, feeds in SOURCES.items():
        weight = TIER_WEIGHT[tier]
        # arXiv is very high volume — cap at 10 most recent papers per feed
        limit = 10 if tier == "research" else 8

        for source_name, url in feeds:
            try:
                data = fetch_url(url)
                items = parse_rss(data)[:limit]
                added = 0
                for title, link, desc in items:
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    articles.append({
                        "source":  source_name,
                        "tier":    tier,
                        "weight":  weight,
                        "title":   title,
                        "link":    link,
                        "desc":    desc,
                        "hn_points":   0,
                        "hn_comments": 0,
                        "cross_sources": 1,  # starts at 1 (this source)
                        "score":   weight,
                    })
                    added += 1
                print(f"  [{tier:8}] {source_name}: {added} articles")
            except Exception as e:
                print(f"  [{tier:8}] {source_name}: SKIP ({type(e).__name__})")

    return articles


def fetch_hacker_news():
    """Fetch AI stories from HN with engagement metrics (last 24h)."""
    url = HN_SEARCH
    try:
        data = fetch_url(url)
        hits = json.loads(data).get("hits", [])
        stories = []
        for h in hits:
            title    = (h.get("title") or "").strip()
            link     = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            points   = int(h.get("points") or 0)
            comments = int(h.get("num_comments") or 0)
            if title:
                stories.append({
                    "title":    title,
                    "link":     link,
                    "points":   points,
                    "comments": comments,
                })
        print(f"  [hacker_news] Hacker News: {len(stories)} stories")
        return stories
    except Exception as e:
        print(f"  [hacker_news] Hacker News: SKIP ({e})")
        return []


# ── Scoring ────────────────────────────────────────────────────────────────────

def normalize(s):
    """Lowercase, strip punctuation — for fuzzy title matching."""
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def key_words(title):
    """Extract significant words (4+ chars) from a title."""
    stop = {"that", "with", "from", "this", "have", "will", "been", "more",
            "than", "what", "when", "your", "about", "into", "over", "also",
            "after", "their", "they", "says", "says", "gets", "just"}
    return {w for w in normalize(title).split() if len(w) >= 4 and w not in stop}


def titles_overlap(a, b, threshold=0.35):
    """True if two titles share enough significant keywords."""
    ka, kb = key_words(a), key_words(b)
    if not ka or not kb:
        return False
    return len(ka & kb) / min(len(ka), len(kb)) >= threshold


def score_articles(articles, hn_stories):
    """
    Boost article scores based on:
      1. HN engagement (points + comments)
      2. Cross-source coverage (same story in multiple outlets)
    """
    # --- HN cross-reference ---
    for article in articles:
        for hn in hn_stories:
            if titles_overlap(article["title"], hn["title"]):
                article["hn_points"]   = max(article["hn_points"],   hn["points"])
                article["hn_comments"] = max(article["hn_comments"], hn["comments"])

    # --- Cross-source deduplication & boosting ---
    for i, a in enumerate(articles):
        for j, b in enumerate(articles):
            if i >= j:
                continue
            if titles_overlap(a["title"], b["title"]):
                a["cross_sources"] += 1
                b["cross_sources"] += 1

    # --- Final score ---
    for a in articles:
        hn_boost     = min(10, a["hn_points"] // 50 + a["hn_comments"] // 20)
        cross_boost  = (a["cross_sources"] - 1) * 5
        a["score"]   = a["weight"] + hn_boost + cross_boost

    # Sort descending by score
    articles.sort(key=lambda x: x["score"], reverse=True)

    # Add HN stories not already in articles (community-sourced signal)
    covered_links = {a["link"] for a in articles}
    extra_hn = []
    for hn in sorted(hn_stories, key=lambda x: x["points"] + x["comments"], reverse=True):
        if hn["link"] not in covered_links:
            extra_hn.append({
                "source":        "Hacker News",
                "tier":          "community",
                "weight":        4,
                "title":         hn["title"],
                "link":          hn["link"],
                "desc":          f"{hn['points']} pts · {hn['comments']} comments on HN",
                "hn_points":     hn["points"],
                "hn_comments":   hn["comments"],
                "cross_sources": 1,
                "score":         4 + min(10, hn["points"] // 50),
            })
    articles.extend(sorted(extra_hn, key=lambda x: x["score"], reverse=True)[:10])

    return articles


# ── Generate with Claude ───────────────────────────────────────────────────────

def generate_summary(articles, target_date):
    try:
        import anthropic
    except ImportError:
        print("ERROR: run: pip install anthropic")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    y, m, d = target_date.split("-")
    months   = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"]
    nice_date = f"{months[int(m)-1]} {int(d)}, {y}"

    # Format articles with their scoring signals for Claude
    def fmt(a):
        signals = []
        if a["hn_points"] > 0:
            signals.append(f"HN: {a['hn_points']}pts/{a['hn_comments']}cmts")
        if a["cross_sources"] > 1:
            signals.append(f"covered by {a['cross_sources']} sources")
        sig_str = f"  [{', '.join(signals)}]" if signals else ""
        return (
            f"[SCORE:{a['score']} | {a['tier'].upper()} | {a['source']}]{sig_str}\n"
            f"Title: {a['title']}\n"
            f"URL: {a['link']}\n"
            f"Summary: {a['desc']}"
        )

    articles_text = "\n\n".join(fmt(a) for a in articles[:60])

    prompt = f"""You are the editor of "AI News Daily" — a high signal-to-noise AI digest trusted by researchers and engineers.

Today is {nice_date}. Below is a scored list of articles collected from {len(articles)} sources across multiple tiers (PRIMARY lab blogs, ANALYSIS from trusted experts, RESEARCH from arXiv, INDUSTRY trade press, COMMUNITY from Hacker News).

Each article has a SCORE computed from:
- Source tier weight (PRIMARY=10, ANALYSIS=8, RESEARCH=5, INDUSTRY=3, COMMUNITY=4)
- Hacker News engagement bonus (points + comments)
- Cross-source bonus (+5 for each additional outlet covering the same story)

Your job: produce a comprehensive, ranked markdown digest. Rules:
1. **Order strictly by impact** — highest-scored / most-discussed stories first
2. **Merge duplicate stories** — if multiple sources cover the same event, write one unified entry and cite all sources
3. **Label the splash** — for top stories, note if it's trending on HN (with point counts) or covered by multiple outlets
4. **Separate research from news** — arXiv papers get their own section
5. **Be honest about hype** — flag stories that are low-signal PR vs genuine news
6. **Skip obvious noise** — no listicles, job posts, or pure opinion unless it's from a high-signal voice (Mollick, Zvi, Clark)
7. Use the actual source URLs in all links

Format exactly:

---

# AI News Daily — {nice_date}

*Ranked by impact · {len(articles)} sources monitored*

---

## 🔥 Top Stories
[5-7 most significant stories. Each has a ### heading, 2-3 sentence summary, source attribution, and a [Read more →](URL) link. For widely-covered stories, note "Covered by X sources" or "🔴 Trending on HN: Xpts".]

---

## ⚡ Quick Hits
[10-15 bullet points of notable but shorter items. Format: **Bold topic** — one sentence. [Source](URL)]

---

## 🔬 Research Radar
[3-6 notable arXiv papers or research announcements. Each: **Paper title** — one sentence on why it matters. [arXiv](URL)]

---

## 📊 Trend Watch
[2-3 paragraphs. Synthesize the week's signal — what themes are emerging, what's worth watching, what's hype. Be direct and opinionated.]

---

*AI News Daily · {nice_date} · Sources: {len(set(a["source"] for a in articles))} outlets*

---

SCORED ARTICLES (ordered by score, use this ordering as your primary signal):

{articles_text}"""

    print("Generating digest with Claude…")
    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Save & Push ────────────────────────────────────────────────────────────────

def save_news(content, target_date):
    os.makedirs(NEWS_DIR, exist_ok=True)

    filepath = os.path.join(NEWS_DIR, f"{target_date}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filepath}")

    index_path = os.path.join(NEWS_DIR, "index.json")
    index = {"dates": []}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)

    if target_date not in index["dates"]:
        index["dates"].insert(0, target_date)
        index["dates"] = index["dates"][:90]

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Updated index: {index_path}")

    return filepath


def git_push(target_date):
    def run(cmd):
        r = subprocess.run(cmd, cwd=REPO_PATH, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  [warn] {' '.join(cmd)}: {r.stderr.strip()}")
        return r

    print("Pushing to GitHub…")
    run(["git", "config", "user.email", "ai-news-bot@users.noreply.github.com"])
    run(["git", "config", "user.name",  "AI News Bot"])
    run(["git", "add",
         os.path.join("news", f"{target_date}.md"),
         os.path.join("news", "index.json")])
    r = run(["git", "commit", "-m", f"news: AI digest for {target_date}"])
    if "nothing to commit" in r.stdout + r.stderr:
        print("  Nothing new to commit.")
        return
    remote = f"https://{GITHUB_TOKEN}@github.com/danhedrick1/ai-news.git"
    run(["git", "push", remote, "main"])
    print("  Pushed.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    try:
        date.fromisoformat(target_date)
    except ValueError:
        print(f"ERROR: bad date '{target_date}', use YYYY-MM-DD")
        sys.exit(1)

    print(f"\n{'='*55}")
    print(f"  AI News Daily — {target_date}")
    print(f"{'='*55}\n")

    print("Fetching RSS sources…")
    articles = fetch_rss_sources()

    print("\nFetching Hacker News…")
    hn_stories = fetch_hacker_news()

    print("\nScoring and ranking…")
    articles = score_articles(articles, hn_stories)
    print(f"Total scored: {len(articles)} articles")

    content = generate_summary(articles, target_date)
    save_news(content, target_date)

    if GITHUB_TOKEN:
        git_push(target_date)
    else:
        print("\nNote: GITHUB_TOKEN not set — skipping push.")

    print(f"\nDone. View at: https://danhedrick1.github.io/ai-news\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Daily AI News Generator — Enhanced Edition
Multi-tier source coverage with impact-based ranking.

Stories are filtered to 24h freshness (tier-adjusted), scored by source tier +
HN engagement + cross-source signal, and deduplicated against previous issues.

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
from datetime import date, datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

# ── Config ─────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
REPO_PATH         = os.environ.get("REPO_PATH", os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR          = os.path.join(REPO_PATH, "news")
COVERED_PATH      = os.path.join(NEWS_DIR, "covered.json")

# ── Sources by tier ────────────────────────────────────────────────────────────
#
# max_age_hours: how old an article can be before it's dropped.
#   Daily news (primary/industry/community): 28h
#   Weekly newsletters (analysis): 7 days — digests, not breaking news
#   arXiv (research): 48h — submission-to-publish pipeline lag
#
# NOTE: X/Twitter is not supported without a paid API. HN is used as a proxy
# for real-time X signal — viral tweets and researcher posts reliably surface
# there within hours. Reddit subreddits provide developer/community discourse.
#
SOURCES = {
    "primary": {
        # Direct from the labs — highest trust, always include
        "weight": 10,
        "max_age_hours": 28,
        "feeds": [
            ("Anthropic Blog",     "https://www.anthropic.com/rss.xml"),
            ("OpenAI Blog",        "https://openai.com/blog/rss.xml"),
            ("Google DeepMind",    "https://deepmind.google/blog/rss.xml"),
            ("Google AI Blog",     "https://blog.google/technology/ai/rss/"),
            ("Meta AI Research",   "https://research.facebook.com/feed/"),
            ("Microsoft AI Blog",  "https://blogs.microsoft.com/ai/feed/"),
            ("Hugging Face Blog",  "https://huggingface.co/blog/feed.xml"),
            ("Mistral AI News",    "https://mistral.ai/news/rss/"),
        ],
    },
    "analysis": {
        # Curated newsletters and research-backed takes — low hype, high signal
        "weight": 8,
        "max_age_hours": 168,   # 7 days — weekly newsletters
        "feeds": [
            ("Import AI (Jack Clark)",       "https://importai.substack.com/feed"),
            ("The Batch (DeepLearning.AI)",  "https://www.deeplearning.ai/the-batch/feed/"),
            ("MIT Technology Review",        "https://www.technologyreview.com/feed/"),
            ("One Useful Thing (Mollick)",   "https://www.oneusefulthing.org/feed"),
            ("Zvi Mowshowitz",               "https://thezvi.substack.com/feed"),
            ("Nathan Benaich / Air Street",  "https://nathanbenaich.substack.com/feed"),
            ("The Neuron",                   "https://www.theneurondaily.com/rss"),
            ("The Neuron (Substack)",        "https://theneurondaily.substack.com/feed"),
            ("Interconnects",                "https://www.interconnects.ai/feed"),
            ("HBR AI",                       "https://hbr.org/rss/topic/ai"),
        ],
    },
    "research": {
        # arXiv — raw research before media filters it
        "weight": 5,
        "max_age_hours": 48,
        "feeds": [
            ("arXiv cs.AI", "http://rss.arxiv.org/rss/cs.AI"),
            ("arXiv cs.LG", "http://rss.arxiv.org/rss/cs.LG"),
            ("arXiv cs.CL", "http://rss.arxiv.org/rss/cs.CL"),
        ],
    },
    "industry": {
        # Broad news coverage — higher volume, use score to filter
        "weight": 3,
        "max_age_hours": 28,
        "feeds": [
            ("Reuters Technology",  "https://feeds.reuters.com/reuters/technologyNews"),
            ("TechCrunch",          "https://techcrunch.com/feed/"),
            ("Axios Tech",          "https://www.axios.com/feeds/feed.rss"),
            ("Ars Technica",        "https://feeds.arstechnica.com/arstechnica/technology-lab"),
            ("VentureBeat AI",      "https://venturebeat.com/ai/feed/"),
            ("The Verge AI",        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
            ("Wired AI",            "https://www.wired.com/feed/category/artificial-intelligence/latest/rss"),
            ("Bloomberg Tech",      "https://feeds.bloomberg.com/technology/news.rss"),
            ("The Guardian AI",     "https://www.theguardian.com/technology/artificialintelligenceai/rss"),
            ("GeekWire",            "https://www.geekwire.com/feed/"),
            ("Gizmodo AI",          "https://gizmodo.com/tag/artificial-intelligence/rss"),
            ("MacRumors",           "https://feeds.macrumors.com/MacRumors-All"),
            ("9to5Mac",             "https://9to5mac.com/feed/"),
            ("Stat News",           "https://www.statnews.com/feed/"),
            ("Japan Times Tech",    "https://www.japantimes.co.jp/rss/tech"),
            ("Business Insider",    "https://www.businessinsider.com/rss"),
            ("AI News",             "https://www.artificialintelligence-news.com/feed/"),
        ],
    },
    "community": {
        # Reddit developer/researcher discourse — surface viral moments + dev reactions
        "weight": 4,
        "max_age_hours": 28,
        "feeds": [
            ("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
            ("Reddit r/LocalLLaMA",      "https://www.reddit.com/r/LocalLLaMA/.rss"),
            ("Reddit r/artificial",      "https://www.reddit.com/r/artificial/.rss"),
            ("Reddit r/singularity",     "https://www.reddit.com/r/singularity/.rss"),
        ],
    },
}

PAYWALLED_DOMAINS = {
    "theinformation.com",
    "technologyreview.com",
    "wsj.com",
    "ft.com",
    "bloomberg.com",
    "economist.com",
    "nytimes.com",
    "theathletic.com",
    "theverge.com",
    "businessinsider.com",
    "japantimes.co.jp",
    "hbr.org",
}

HN_SEARCH = (
    "https://hn.algolia.com/api/v1/search"
    "?query=AI+LLM+GPT+language+model+machine+learning"
    "&tags=story"
    "&numericFilters=points>10"
    "&hitsPerPage=30"
)


# ── Date parsing ───────────────────────────────────────────────────────────────

def parse_pub_date(s):
    """Parse RSS/Atom date strings into an aware UTC datetime, or None."""
    if not s:
        return None
    s = s.strip()
    # RFC 2822 (standard RSS)
    try:
        dt = parsedate_to_datetime(s)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    # ISO 8601 variants
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            raw = s[:len(fmt)]
            dt  = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
    return None


def is_fresh(pub_date, max_age_hours):
    """True if pub_date is within max_age_hours of now (or unknown)."""
    if pub_date is None:
        return True   # no date = don't reject, let Claude judge
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    return pub_date >= cutoff


# ── Fetching ───────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=12):
    # Reddit blocks bots; use a browser UA for .rss endpoints
    ua = ("Mozilla/5.0 (compatible; AI-News-Bot/2.0; +https://github.com/danhedrick1/ai-news)"
          if "reddit.com" not in url else
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def parse_rss(data):
    """Return list of (title, link, desc, pub_date_str) from RSS or Atom."""
    items = []
    try:
        root = ET.fromstring(data)
        ns_dc = "http://purl.org/dc/elements/1.1/"
        # RSS 2.0
        for item in root.findall(".//item"):
            title = strip_html(item.findtext("title") or "")
            link  = (item.findtext("link") or "").strip()
            desc  = strip_html(item.findtext("description") or "")[:500]
            pub   = (item.findtext("pubDate")
                     or item.findtext(f"{{{ns_dc}}}date"))
            if title and link:
                items.append((title, link, desc, pub))
        # Atom
        if not items:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for entry in root.findall(".//a:entry", ns):
                title   = strip_html(entry.findtext("a:title", namespaces=ns) or "")
                link_el = entry.find("a:link", ns)
                link    = (link_el.get("href", "") if link_el is not None else "").strip()
                desc    = strip_html(entry.findtext("a:summary", namespaces=ns) or "")[:500]
                pub     = (entry.findtext("a:published", namespaces=ns)
                           or entry.findtext("a:updated",   namespaces=ns))
                if title and link:
                    items.append((title, link, desc, pub))
    except ET.ParseError:
        pass
    return items


def fetch_rss_sources():
    """Fetch all sources, apply freshness filter, return scored article dicts."""
    articles  = []
    seen_links = set()
    now        = datetime.now(timezone.utc)
    totals     = {"fetched": 0, "stale": 0, "added": 0}

    for tier, cfg in SOURCES.items():
        weight       = cfg["weight"]
        max_age      = cfg["max_age_hours"]
        limit        = 10 if tier == "research" else 8

        for source_name, url in cfg["feeds"]:
            try:
                data  = fetch_url(url)
                items = parse_rss(data)[:limit]
                added = stale = 0

                for title, link, desc, pub_str in items:
                    totals["fetched"] += 1
                    if link in seen_links:
                        continue
                    pub_dt = parse_pub_date(pub_str)
                    if not is_fresh(pub_dt, max_age):
                        stale += 1
                        totals["stale"] += 1
                        continue
                    seen_links.add(link)
                    age_str = ""
                    if pub_dt:
                        age_h = (now - pub_dt).total_seconds() / 3600
                        age_str = f"{age_h:.0f}h ago"
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(link).netloc.lower().lstrip("www.")
                        is_paywalled = any(d in domain for d in PAYWALLED_DOMAINS)
                    except Exception:
                        is_paywalled = False
                    articles.append({
                        "source":        source_name,
                        "tier":          tier,
                        "weight":        weight,
                        "title":         title,
                        "link":          link,
                        "desc":          desc,
                        "pub_dt":        pub_dt.isoformat() if pub_dt else None,
                        "age_str":       age_str,
                        "hn_points":     0,
                        "hn_comments":   0,
                        "cross_sources": 1,
                        "prev_covered":  False,
                        "paywalled":     is_paywalled,
                        "score":         weight,
                    })
                    added += 1
                    totals["added"] += 1

                label = f"{added} added" + (f", {stale} stale" if stale else "")
                print(f"  [{tier:8}] {source_name}: {label}")
            except Exception as e:
                print(f"  [{tier:8}] {source_name}: SKIP ({type(e).__name__}: {e})")

    print(f"  -> {totals['added']} fresh / {totals['stale']} stale filtered / {totals['fetched']} total")
    return articles


def fetch_hacker_news():
    """Fetch trending AI stories from HN."""
    try:
        data    = fetch_url(HN_SEARCH)
        hits    = json.loads(data).get("hits", [])
        stories = []
        for h in hits:
            title    = (h.get("title") or "").strip()
            link     = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
            points   = int(h.get("points") or 0)
            comments = int(h.get("num_comments") or 0)
            created  = h.get("created_at", "")
            pub_dt   = parse_pub_date(created)
            # Only HN stories from last 36h
            if pub_dt and not is_fresh(pub_dt, 36):
                continue
            if title:
                stories.append({"title": title, "link": link,
                                 "points": points, "comments": comments})
        print(f"  [community ] Hacker News: {len(stories)} stories")
        return stories
    except Exception as e:
        print(f"  [community ] Hacker News: SKIP ({e})")
        return []


# ── Previously-covered deduplication ──────────────────────────────────────────

def key_words(title):
    """Significant words (4+ chars) for fuzzy fingerprinting."""
    stop = {"that", "with", "from", "this", "have", "will", "been", "more",
            "than", "what", "when", "your", "about", "into", "over", "also",
            "after", "their", "they", "says", "gets", "just", "here", "using",
            "could", "would", "make", "made", "show", "shows", "found", "find"}
    return {w for w in re.sub(r"[^a-z0-9 ]", "", title.lower()).split()
            if len(w) >= 4 and w not in stop}


def titles_overlap(a, b, threshold=0.40):
    ka, kb = key_words(a), key_words(b)
    if not ka or not kb:
        return False
    return len(ka & kb) / min(len(ka), len(kb)) >= threshold


def load_covered():
    """Load story fingerprints from the last 7 days."""
    if not os.path.exists(COVERED_PATH):
        return []
    with open(COVERED_PATH, encoding="utf-8") as f:
        data = json.load(f)
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    return [s for s in data.get("stories", []) if s.get("date", "") >= cutoff]


def save_covered(articles, target_date):
    """Append today's article fingerprints to covered.json (rolling 7-day window)."""
    existing     = load_covered()
    existing_fps = {s["fingerprint"] for s in existing}
    for a in articles:
        fp = " ".join(sorted(key_words(a["title"])))
        if fp and fp not in existing_fps:
            existing.append({
                "date":        target_date,
                "fingerprint": fp,
                "title":       a["title"][:120],
            })
            existing_fps.add(fp)
    os.makedirs(NEWS_DIR, exist_ok=True)
    with open(COVERED_PATH, "w", encoding="utf-8") as f:
        json.dump({"stories": existing}, f, indent=2)


def mark_previously_covered(articles):
    """Flag articles whose topic was already in a recent issue."""
    covered   = load_covered()
    cov_words = [set(s["fingerprint"].split()) for s in covered]
    marked    = 0
    for a in articles:
        aw = key_words(a["title"])
        for cw in cov_words:
            if aw and cw and len(aw & cw) / min(len(aw), len(cw)) >= 0.50:
                a["prev_covered"] = True
                marked += 1
                break
    if marked:
        print(f"  -> {marked} articles flagged as previously covered (will need new angle)")
    return articles


# ── Scoring ────────────────────────────────────────────────────────────────────

def score_articles(articles, hn_stories):
    # HN cross-reference
    for a in articles:
        for hn in hn_stories:
            if titles_overlap(a["title"], hn["title"]):
                a["hn_points"]   = max(a["hn_points"],   hn["points"])
                a["hn_comments"] = max(a["hn_comments"], hn["comments"])

    # Cross-source boost
    for i, a in enumerate(articles):
        for j, b in enumerate(articles):
            if i >= j:
                continue
            if titles_overlap(a["title"], b["title"]):
                a["cross_sources"] += 1
                b["cross_sources"] += 1

    # Final score (previously-covered stories get a -6 penalty — still included
    # if there's strong new signal, but deprioritised by default)
    for a in articles:
        hn_boost    = min(10, a["hn_points"] // 50 + a["hn_comments"] // 20)
        cross_boost = (a["cross_sources"] - 1) * 5
        prev_penalty = -6 if a["prev_covered"] else 0
        a["score"]  = a["weight"] + hn_boost + cross_boost + prev_penalty

    articles.sort(key=lambda x: x["score"], reverse=True)

    # Append HN-only stories not already in any feed
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
                "pub_dt":        None,
                "age_str":       "",
                "hn_points":     hn["points"],
                "hn_comments":   hn["comments"],
                "cross_sources": 1,
                "prev_covered":  False,
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

    y, m, d   = target_date.split("-")
    months    = ["January","February","March","April","May","June",
                 "July","August","September","October","November","December"]
    nice_date = f"{months[int(m)-1]} {int(d)}, {y}"

    def fmt(a):
        signals = []
        if a["hn_points"] > 0:
            signals.append(f"[HN] HN {a['hn_points']}pts/{a['hn_comments']}cmts")
        if a["cross_sources"] > 1:
            signals.append(f"x{a['cross_sources']} sources")
        if a["age_str"]:
            signals.append(a["age_str"])
        if a["prev_covered"]:
            signals.append("[!] PREVIOUSLY COVERED")
        if a.get("paywalled"):
            signals.append("[PAYWALL]")
        sig = f"  [{', '.join(signals)}]" if signals else ""
        return (
            f"[SCORE:{a['score']} | {a['tier'].upper()} | {a['source']}]{sig}\n"
            f"Title: {a['title']}\n"
            f"URL: {a['link']}\n"
            f"Summary: {a['desc']}"
        )

    articles_text = "\n\n".join(fmt(a) for a in articles[:65])
    n_sources     = len(set(a["source"] for a in articles))
    n_prev        = sum(1 for a in articles if a["prev_covered"])

    prompt = f"""You are the editor of "AI News Daily" — a high signal-to-noise AI digest for researchers and engineers.

Today is {nice_date}. You have {len(articles)} scored articles from {n_sources} sources across labs (Anthropic, OpenAI, Google, Meta, Mistral), journalism (Reuters, TechCrunch, Bloomberg, Axios, Guardian), analysis (Import AI, The Batch, Mollick, Zvi), research (arXiv), Apple/consumer (MacRumors, 9to5Mac), healthcare AI (Stat News), and community (Reddit r/MachineLearning, r/LocalLLaMA). {n_prev} are flagged [!] PREVIOUSLY COVERED.

SCORING SIGNALS ON EACH ARTICLE:
- SCORE = tier weight + HN engagement bonus + cross-source bonus − previously-covered penalty
- Tier weights: PRIMARY=10, ANALYSIS=8, RESEARCH=5, INDUSTRY=3, COMMUNITY=4
- [HN] HN Xpts = trending on Hacker News right now
- x2/x3 sources = same story confirmed by multiple outlets
- [!] PREVIOUSLY COVERED = this topic appeared in a recent issue

RULES:
1. **Freshness first** — only include [!] PREVIOUSLY COVERED stories if there is a genuinely new development, new data, or a meaningful shift in the story. If including one, start the entry with "**Update:**" and clearly state what's new.
2. **Order strictly by impact** — score is your primary signal; use your editorial judgment as a tiebreaker.
3. **Merge duplicates** — same event from multiple sources = one unified entry, cite all sources.
4. **Splash labeling** — note "[HN] Trending on HN: Xpts" or "Covered by X outlets" on top stories.
5. **No noise** — skip listicles, job posts, or pure puff pieces. Flag borderline items as "(Low signal)" if you include them.
6. **Research gets its own section** — arXiv papers go in Research Radar only.
7. Use the actual source URLs in every link.
8. **Paywalled sources** — if an article is flagged [PAYWALL]:
   - Append ` [PAYWALL]` to the ### headline (e.g. `### Story Title [PAYWALL]`)
   - Write a longer, more complete summary (4-5 sentences + key bullet points) since readers cannot access the full article
   - Still link to the source so readers can verify / subscribe

FORMAT:

---

# AI News Daily — {nice_date}

*Ranked by impact · {n_sources} sources · stories from the last 24h*

---

## 🔥 Top Stories

[5-7 entries. Each story uses this exact structure — keep the summary concise (2-3 sentences) since the UI collapses stories by default and users expand to read more:

### Descriptive Headline
2-3 sentence summary of what happened and why it matters. For [PAYWALL] stories write 4-5 sentences plus **Key details:** bullets.
**Source:** [Publication](URL) · Score signal if notable
[Read more →](URL)]

---

## ⚡ Quick Hits

[10-15 bullets. Format: **Topic** — one sentence. [Source](URL)]

---

## 🔬 Research Radar

[3-6 arXiv papers. Format: **Short paper title** — one sentence on significance. [arXiv](URL)]

---

## 📊 Trend Watch

[2-3 paragraphs of synthesis. What's the signal vs noise this week? What should readers actually pay attention to? Be direct and opinionated.]

---

*AI News Daily · {nice_date} · {n_sources} outlets monitored*

---

ARTICLES (ranked by score — use this order as primary signal):

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
    print(f"Updated index")
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
    run(["git", "add", "news/"])
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

    print("\nChecking previously covered stories…")
    articles = mark_previously_covered(articles)

    print("\nScoring and ranking…")
    articles = score_articles(articles, hn_stories)
    print(f"Total scored: {len(articles)} articles")

    content = generate_summary(articles, target_date)
    save_news(content, target_date)

    print("\nUpdating covered-stories fingerprints…")
    save_covered(articles, target_date)

    if GITHUB_TOKEN:
        git_push(target_date)
    else:
        print("\nNote: GITHUB_TOKEN not set — skipping push.")

    print(f"\nDone. View at: https://danhedrick1.github.io/ai-news\n")


if __name__ == "__main__":
    main()

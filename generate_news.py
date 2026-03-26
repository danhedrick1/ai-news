#!/usr/bin/env python3
"""
The Bash — Daily Digest Generator
Multi-tier source coverage with impact-based ranking.

Stories are filtered to 24h freshness (tier-adjusted), scored by source tier +
HN engagement + cross-source signal, and deduplicated against previous issues.

Usage:
  python generate_news.py              # today
  python generate_news.py 2026-03-24   # specific date
  python generate_news.py --weekly     # weekly recap for current ET date

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
WEEKLY_INDEX_PATH = os.path.join(NEWS_DIR, "weekly-index.json")

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
        # Direct from the labs — highest signal
        "weight": 10,
        "max_age_hours": 28,
        "feeds": [
            ("OpenAI Blog",              "https://openai.com/blog/rss.xml"),
            ("Google DeepMind",          "https://deepmind.google/blog/rss.xml"),
            ("Google AI Blog",           "https://blog.google/technology/ai/rss/"),
            ("Meta AI Research",         "https://research.facebook.com/feed/"),
            ("Microsoft AI Blog",        "https://blogs.microsoft.com/ai/feed/"),
            ("Hugging Face Blog",        "https://huggingface.co/blog/feed.xml"),
            ("NVIDIA AI Blog",           "https://blogs.nvidia.com/blog/category/deep-learning/feed/"),
            ("Cohere Blog",              "https://txt.cohere.com/rss/"),
            ("Stability AI",             "https://stability.ai/news/rss.xml"),
            ("TechCrunch — Anthropic",   "https://techcrunch.com/tag/anthropic/feed/"),
            ("TechCrunch — OpenAI",      "https://techcrunch.com/tag/openai/feed/"),
            ("TechCrunch — Google AI",   "https://techcrunch.com/tag/google-ai/feed/"),
        ],
    },
    "analysis": {
        # Curated newsletters and research-backed takes — low hype, high signal
        "weight": 8,
        "max_age_hours": 168,   # 7 days — weekly newsletters
        "feeds": [
            ("Import AI (Jack Clark)",      "https://importai.substack.com/feed"),
            ("MIT Technology Review",       "https://www.technologyreview.com/feed/"),
            ("One Useful Thing (Mollick)",  "https://www.oneusefulthing.org/feed"),
            ("Zvi Mowshowitz",              "https://thezvi.substack.com/feed"),
            ("Nathan Benaich / Air Street", "https://nathanbenaich.substack.com/feed"),
            ("The Neuron",                  "https://theneuron.ai/feed"),
            ("Interconnects",               "https://www.interconnects.ai/feed"),
            ("Latent Space",                "https://www.latent.space/feed"),
            ("Ben's Bites",                 "https://www.bensbites.co/feed"),
            ("The Batch (deeplearning.ai)", "https://www.deeplearning.ai/the-batch/feed/"),
            ("Pragmatic Engineer",          "https://newsletter.pragmaticengineer.com/feed"),
            ("Turing Post",                 "https://www.turingpost.com/feed"),
            ("Semianalysis",                "https://www.semianalysis.com/feed"),
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
        # Broad news coverage — higher volume, Claude filters by relevance + score
        "weight": 3,
        "max_age_hours": 28,
        "feeds": [
            ("TechCrunch AI",       "https://techcrunch.com/tag/artificial-intelligence/feed/"),
            ("Axios Tech",          "https://api.axios.com/feed/"),
            ("Ars Technica",        "https://feeds.arstechnica.com/arstechnica/technology-lab"),
            ("VentureBeat AI",      "https://venturebeat.com/category/ai/feed"),
            ("The Verge AI",        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
            ("Wired",               "https://www.wired.com/feed/rss"),
            ("Bloomberg Tech",      "https://feeds.bloomberg.com/technology/news.rss"),
            ("Reuters AI",          "https://www.reuters.com/technology/rss"),
            ("The Guardian AI",     "https://www.theguardian.com/technology/artificialintelligenceai/rss"),
            ("CNBC AI",             "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=48812682"),
            ("GeekWire",            "https://www.geekwire.com/feed/"),
            ("Gizmodo AI",          "https://gizmodo.com/tag/artificial-intelligence/rss"),
            ("MacRumors",           "https://feeds.macrumors.com/MacRumors-All"),
            ("9to5Mac",             "https://9to5mac.com/feed/"),
            ("Stat News AI",        "https://www.statnews.com/topic/artificial-intelligence/feed/"),
            ("Japan Times Tech",    "https://www.japantimes.co.jp/rss/tech"),
            ("Business Insider",    "https://www.businessinsider.com/rss"),
            ("AI News",             "https://www.artificialintelligence-news.com/feed/"),
            ("FT Technology",       "https://www.ft.com/technology?format=rss"),
        ],
    },
    "community": {
        # Developer/hacker community — surface viral moments + dev reactions
        "weight": 4,
        "max_age_hours": 28,
        "feeds": [
            ("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
            ("Reddit r/LocalLLaMA",      "https://www.reddit.com/r/LocalLLaMA/.rss"),
            ("Reddit r/artificial",      "https://www.reddit.com/r/artificial/.rss"),
            ("Reddit r/singularity",     "https://www.reddit.com/r/singularity/.rss"),
            ("Lobste.rs",                "https://lobste.rs/rss"),
            ("dev.to AI",               "https://dev.to/feed/tag/ai"),
            ("StackOverflow Blog",       "https://stackoverflow.blog/feed/"),
        ],
    },
    "policy": {
        # AI policy and governance — macro-level signal
        "weight": 4,
        "max_age_hours": 72,
        "feeds": [
            ("Stanford HAI",             "https://hai.stanford.edu/news/rss.xml"),
            ("Brookings AI",             "https://www.brookings.edu/topic/artificial-intelligence/feed/"),
            ("OECD AI",                  "https://www.oecd.org/topics/artificial-intelligence/rss/"),
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

# High-signal keywords that boost scoring
BOOST_KEYWORDS = {
    "agi", "open-source", "open source", "opensource", "jailbreak",
    "model release", "benchmark", "state-of-the-art", "sota",
    "gpt-5", "gpt5", "claude", "gemini", "llama", "mistral",
    "diffusion", "transformer", "fine-tune", "finetune",
    "reasoning", "chain-of-thought", "agent", "agentic",
    "multimodal", "vision", "text-to-video", "text-to-image",
    "embedding", "rag", "retrieval", "context window",
    "inference", "quantization", "distillation",
    "regulation", "executive order", "lawsuit", "copyright",
    "acquisition", "funding", "valuation", "billion",
    "replace", "obsolete", "breakthrough", "dangerous",
}

# Classification categories for articles
CLASSIFICATIONS = [
    "breakthrough",   # major capability jump or new paradigm
    "tool",           # new tool, library, or platform
    "funding",        # fundraising, acquisition, valuation
    "controversy",    # lawsuit, safety concern, ethical debate
    "dev_insight",    # practical dev knowledge, benchmarks, how-tos
    "research",       # academic paper, novel technique
    "policy",         # regulation, governance, standards
]


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
    ua = ("Mozilla/5.0 (compatible; TheBash-Bot/1.0; +https://thebash.dev)"
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
        if tier == "research":
            limit = 14
        elif tier in ("analysis", "industry", "community"):
            limit = 10
        else:
            limit = 8

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


def fetch_github_trending():
    """Fetch trending AI/ML repositories from GitHub."""
    try:
        # Use GitHub's search API to find recently-created/updated repos with many stars
        url = (
            "https://api.github.com/search/repositories"
            "?q=topic:machine-learning+topic:ai+pushed:>="
            + (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
            + "&sort=stars&order=desc&per_page=15"
        )
        headers = {"User-Agent": "AI-News-Bot/2.0"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        repos = []
        for r in data.get("items", [])[:15]:
            repos.append({
                "name":        r["full_name"],
                "url":         r["html_url"],
                "description": (r.get("description") or "")[:300],
                "stars":       r.get("stargazers_count", 0),
                "language":    r.get("language", ""),
                "created":     r.get("created_at", ""),
            })
        print(f"  [community ] GitHub Trending: {len(repos)} repos")
        return repos
    except Exception as e:
        print(f"  [community ] GitHub Trending: SKIP ({e})")
        return []


def fetch_huggingface_papers():
    """Fetch recent papers from HuggingFace daily papers API."""
    try:
        url = "https://huggingface.co/api/daily_papers?limit=10"
        data = fetch_url(url)
        papers = json.loads(data)
        results = []
        for p in papers:
            paper = p.get("paper", p)
            title = paper.get("title", "")
            paper_id = paper.get("id", "")
            summary = paper.get("summary", "")[:500]
            upvotes = p.get("numUpvotes", paper.get("upvotes", 0))
            if title:
                results.append({
                    "title":   title,
                    "url":     f"https://huggingface.co/papers/{paper_id}" if paper_id else "",
                    "summary": summary,
                    "upvotes": upvotes,
                })
        print(f"  [research  ] HuggingFace Papers: {len(results)} papers")
        return results
    except Exception as e:
        print(f"  [research  ] HuggingFace Papers: SKIP ({e})")
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


def week_window(target):
    """Return Monday-Sunday date window for the week containing target."""
    start = target - timedelta(days=target.weekday())
    end = start + timedelta(days=6)
    return start, end


def week_id(target):
    """ISO week id like 2026-W13."""
    iso_year, iso_week, _ = target.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def read_digest_markdown(day):
    """Return markdown for a saved daily digest, or None if missing."""
    path = os.path.join(NEWS_DIR, f"{day.isoformat()}.md")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_weekly_digest_context(markdown):
    """Pull headlines and synthesis paragraphs from a daily digest."""
    headlines = []
    trend_lines = []
    quick_hits = []
    current_section = ""

    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("## "):
            current_section = line[3:].lower()
            continue
        if line.startswith("### "):
            headlines.append(line[4:].strip())
            continue
        if line.startswith("- **"):
            quick_hits.append(line)
            continue
        if "trend watch" in current_section or "crontab -l" in current_section:
            if not line.startswith("---"):
                trend_lines.append(line)

    return {
        "headlines": headlines[:6],
        "quick_hits": quick_hits[:6],
        "trend_watch": trend_lines[:3],
    }


def fallback_weekly_recap(digests, week_label):
    """Simple weekly recap when Anthropic is unavailable."""
    lines = [
        "---",
        "",
        f"# The Bash Weekly - {week_label}",
        "",
        f"*{len(digests)} daily digests stitched into one weekly recap*",
        "",
        "---",
        "",
        "## Week in One Screen",
        "",
        "This recap was assembled from the daily issues already published during the week. Use it as a fast catch-up, then jump into the linked daily digests for the full signal.",
        "",
        "## Daily Signal Log",
        "",
    ]

    for digest in digests:
        lines.append(
            f"### {digest['nice_date']} - [open digest](https://thebash.dev/{digest['date']})"
        )
        for headline in digest["context"]["headlines"][:4]:
            lines.append(f"- {headline}")
        if digest["context"]["trend_watch"]:
            lines.append(f"- Trend watch: {digest['context']['trend_watch'][0]}")
        lines.append("")

    lines.extend([
        "## What to Watch Next",
        "",
        "- The labs are still shipping faster than the media cycle can digest them.",
        "- Tooling and distribution continue to matter more than benchmark theater.",
        "- The next weekly recap should call out what moved from demo to production.",
        "",
        "---",
        "",
        "*The Bash Weekly - built for builders*",
        "",
        "---",
    ])

    return "\n".join(lines)


# ── Scoring ────────────────────────────────────────────────────────────────────

def keyword_boost(title, desc=""):
    """Return a score boost based on high-signal keyword matches."""
    text = f"{title} {desc}".lower()
    matches = sum(1 for kw in BOOST_KEYWORDS if kw in text)
    return min(4, matches)  # cap at +4


def score_articles(articles, hn_stories, gh_repos=None, hf_papers=None):
    gh_repos = gh_repos or []
    hf_papers = hf_papers or []

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

    # Final score with keyword boost
    for a in articles:
        hn_boost     = min(10, a["hn_points"] // 50 + a["hn_comments"] // 20)
        cross_boost  = (a["cross_sources"] - 1) * 5
        kw_boost     = keyword_boost(a["title"], a["desc"])
        prev_penalty = -6 if a["prev_covered"] else 0
        a["score"]   = a["weight"] + hn_boost + cross_boost + kw_boost + prev_penalty

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
                "paywalled":     False,
                "score":         4 + min(10, hn["points"] // 50) + keyword_boost(hn["title"]),
            })
    articles.extend(sorted(extra_hn, key=lambda x: x["score"], reverse=True)[:14])

    # Append GitHub trending repos as articles
    for repo in gh_repos[:12]:
        if repo["url"] not in covered_links:
            articles.append({
                "source":        "GitHub Trending",
                "tier":          "community",
                "weight":        4,
                "title":         f"{repo['name']}: {repo['description'][:100]}",
                "link":          repo["url"],
                "desc":          f"⭐ {repo['stars']} stars · {repo['language']} · {repo['description']}",
                "pub_dt":        None,
                "age_str":       "",
                "hn_points":     0,
                "hn_comments":   0,
                "cross_sources": 1,
                "prev_covered":  False,
                "paywalled":     False,
                "score":         4 + min(6, repo["stars"] // 500) + keyword_boost(repo["name"], repo["description"]),
            })

    # Append HuggingFace papers
    for paper in hf_papers[:8]:
        if paper["url"] and paper["url"] not in covered_links:
            articles.append({
                "source":        "HuggingFace Papers",
                "tier":          "research",
                "weight":        5,
                "title":         paper["title"],
                "link":          paper["url"],
                "desc":          paper["summary"],
                "pub_dt":        None,
                "age_str":       "",
                "hn_points":     0,
                "hn_comments":   0,
                "cross_sources": 1,
                "prev_covered":  False,
                "paywalled":     False,
                "score":         5 + min(5, paper["upvotes"] // 10) + keyword_boost(paper["title"], paper["summary"]),
            })

    # Re-sort after adding extra sources
    articles.sort(key=lambda x: x["score"], reverse=True)
    return articles


# ── Generate with Claude ───────────────────────────────────────────────────────

def digest_quality_stats(content):
    """Estimate whether the generated digest is materially complete."""
    top_stories = len(re.findall(r"^### ", content, flags=re.MULTILINE))
    quick_hit_bullets = 0
    in_quick_hits = False
    in_tools = False
    in_research = False
    research_entries = 0
    tool_entries = 0

    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            lower = line.lower()
            in_quick_hits = "quick hits" in lower or "stderr" in lower
            in_research = "research radar" in lower or "bash-research" in lower
            in_tools = "tools & repos" in lower or "pkg ls" in lower
            continue
        if line.startswith("---"):
            in_quick_hits = in_research = in_tools = False
            continue
        if in_quick_hits and line.startswith("- "):
            quick_hit_bullets += 1
        if in_research and line.startswith("**"):
            research_entries += 1
        if in_tools and line.startswith("**"):
            tool_entries += 1

    return {
        "top_stories": top_stories,
        "quick_hits": quick_hit_bullets,
        "research_entries": research_entries,
        "tool_entries": tool_entries,
    }

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

    articles_text = "\n\n".join(fmt(a) for a in articles[:95])
    n_sources     = len(set(a["source"] for a in articles))
    n_prev        = sum(1 for a in articles if a["prev_covered"])
    tier_counts   = {}
    for a in articles:
        tier_counts[a["tier"]] = tier_counts.get(a["tier"], 0) + 1
    tier_summary = ", ".join(
        f"{tier.upper()}={count}" for tier, count in sorted(tier_counts.items())
    )

    prompt = f"""You are the editor of The Bash — a high signal-to-noise AI & tech digest for hackers, developers, and engineers. Your voice is direct, technically sharp, and developer-friendly. No hype, no fluff — just what matters for builders.

Today is {nice_date}. You have {len(articles)} scored articles from {n_sources} sources across labs (Anthropic, OpenAI, Google, Meta, Mistral, NVIDIA, Cohere, Stability), journalism (Reuters, TechCrunch, Bloomberg, Axios, Guardian), analysis (Import AI, Latent Space, Semianalysis, Mollick, Zvi, Ben's Bites), research (arXiv, HuggingFace Papers), developer community (GitHub Trending, Reddit r/MachineLearning, r/LocalLLaMA, Lobste.rs, HN), and policy (Stanford HAI, Brookings). {n_prev} are flagged [!] PREVIOUSLY COVERED.
Tier mix available right now: {tier_summary}.

SCORING SIGNALS ON EACH ARTICLE:
- SCORE = tier weight + HN engagement + cross-source + keyword boost − previously-covered penalty
- Tier weights: PRIMARY=10, ANALYSIS=8, RESEARCH=5, COMMUNITY=4, POLICY=4, INDUSTRY=3
- [HN] HN Xpts = trending on Hacker News right now
- x2/x3 sources = same story confirmed by multiple outlets
- [!] PREVIOUSLY COVERED = this topic appeared in a recent issue

CLASSIFICATION — mentally classify each story you include as one of:
breakthrough | tool | funding | controversy | dev_insight | research | policy

VIRAL FILTER — before including any story, ask: "Is this surprising, useful, or new to a technical reader?" Reject if:
- obvious/expected news everyone already knows
- no actionable insight for builders
- pure PR / puff piece with no substance

RULES:
1. **Freshness first** — only include [!] PREVIOUSLY COVERED stories if there is a genuinely new development. If including one, start with "**Update:**".
2. **Order strictly by impact** — score is your primary signal; editorial judgment as tiebreaker.
3. **Merge duplicates** — same event from multiple sources = one unified entry, cite all.
4. **Splash labeling** — note "[HN] Trending on HN: Xpts" or "Covered by X outlets" on top stories.
5. **No noise** — skip listicles, job posts, puff pieces. Be ruthless.
6. **Research gets its own section** — arXiv/HuggingFace papers go in Research Radar.
7. Use the actual source URLs in every link.
8. **Paywalled sources** — if flagged [PAYWALL]: append ` [PAYWALL]` to ### headline, write longer summary (4-5 sentences + bullets).

TONE:
- Sharp, slightly contrarian, builder-focused
- No corporate language, no hype
- Write like a smart engineer talking to other engineers
- Be direct and opinionated

FORMAT:

---

# The Bash — {nice_date}

*{n_sources} sources · ranked by impact · signal over noise*

---

## stdout // top stories

[5-7 entries. Each story MUST include a DEV TAKE — a one-sentence opinionated takeaway a smart engineer would say. Use this exact structure:]

### Headline That Creates Urgency or Curiosity
*[classification]* — 2-3 sentence summary of what actually happened and why it matters for builders. Concrete specifics: numbers, capabilities, constraints. For [PAYWALL] stories write 4-5 sentences plus **Key details:** bullets.

- Bullet 1: key fact
- Bullet 2: key fact
- Bullet 3: what a dev/operator can DO differently now

**🔧 Dev Take:** "One sentence, slightly opinionated takeaway that a smart engineer would say."

**Source:** [Publication](URL) · Score signal if notable
[Read more →](URL)

---

## stderr // quick hits

[10-15 bullets. Format: **Topic** *[classification]* — one sentence of what changed + why it matters. [Source](URL)]

---

## man bash-research // research radar

[3-6 papers from arXiv or HuggingFace. Format:
**Paper title** — one sentence on what's novel and why builders should care. [arXiv/HF](URL)
**🔧 Dev Take:** "What this means in practice."]

---

## pkg ls // tools & repos

[3-5 new tools, libraries, or trending repos. Format:
**Tool/Repo name** — what it does in one sentence. [GitHub/Link](URL) · ⭐ stars if available]

---

## crontab -l // trend watch

[2-3 paragraphs of synthesis. What's the signal vs noise? What patterns are emerging? What should builders actually pay attention to? Be direct, opinionated, slightly contrarian. End with a bold prediction or hot take.]

---

*The Bash · {nice_date} · {n_sources} outlets monitored · built for builders*

---

ARTICLES (ranked by score — use this order as primary signal):

{articles_text}"""

    print("Generating digest with Claude…")
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Multi-format output ───────────────────────────────────────────────────────

def generate_twitter_thread(articles, target_date, client):
    """Generate a Twitter/X thread from top stories."""
    top = articles[:7]
    articles_text = "\n".join(
        f"- [{a['source']}] {a['title']}: {a['desc'][:150]}" for a in top
    )
    prompt = f"""You are writing a Twitter/X thread for "The Bash" — an AI news account for developers.

Date: {target_date}
Top stories:
{articles_text}

Write a 5-tweet thread. Rules:
- Tweet 1: Hook headline. Bold claim or question. Use "🧵" at end.
- Tweet 2: "Here's what's actually happening:" + top story summary
- Tweets 3-4: One story each, concrete and punchy
- Tweet 5: Hot take / prediction / "what to watch"

TONE: sharp, builder-focused, no corporate language. Max 280 chars per tweet.
FORMAT: Number each tweet (1/, 2/, etc). Separate tweets with ---."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def generate_newsletter_block(articles, target_date, client):
    """Generate a newsletter-format block from top stories."""
    top = articles[:10]
    articles_text = "\n".join(
        f"- [{a['source']}] {a['title']}: {a['desc'][:200]}" for a in top
    )
    prompt = f"""You are writing the newsletter edition of "The Bash" for {target_date}.

Stories:
{articles_text}

Write a newsletter block for email. Format:

# The Bash — [date]

[2-sentence intro: what's the big theme today?]

## Headlines

[For each of the top 5-7 stories:]
### [Headline]
[2-sentence summary]
- [bullet 1]
- [bullet 2]
- [bullet 3]
**🔧 Dev Take:** "[opinionated one-liner]"

## Quick Hits
[5-7 one-line bullets for smaller stories]

---
*The Bash — built for builders*

TONE: sharp, direct, no hype. Builder-focused."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def generate_weekly_recap(digests, week_start, week_end, client=None):
    """Generate a weekly recap from saved daily digest markdown."""
    week_label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
    if not client:
        return fallback_weekly_recap(digests, week_label)

    digest_text = []
    for digest in digests:
        context = digest["context"]
        digest_text.append(
            "\n".join([
                f"DATE: {digest['nice_date']}",
                f"DIGEST URL: https://thebash.dev/{digest['date']}",
                "HEADLINES:",
                *(f"- {h}" for h in context["headlines"]),
                "QUICK HITS:",
                *(context["quick_hits"] or ["- none captured"]),
                "TREND WATCH:",
                *(context["trend_watch"] or ["- none captured"]),
            ])
        )

    prompt = f"""You are writing The Bash Weekly, the end-of-week version of The Bash for builders.

Date range: {week_label}
Daily digest count: {len(digests)}

Write a weekly recap in markdown. Be direct, technical, and useful for builders.

FORMAT:

---

# The Bash Weekly - {week_label}

*{len(digests)} daily digests - one weekly signal pass*

---

## Week in One Screen

[2 short paragraphs on what actually changed this week]

## Biggest Shifts

[3-5 items. Each item should be:]
### Headline
2-3 sentences on why it mattered this week.
- One concrete takeaway
- One thing builders should watch next
**Source trail:** [Mon digest](https://thebash.dev/2026-03-23) and similar links to the relevant daily digests

## Builder Board

[5-7 bullets covering tools, repos, releases, or tactics worth attention next week]

## What to Watch Next Week

[1 paragraph with a clear prediction or operator take]

---

*The Bash Weekly - built for builders*

---

DAILY DIGEST INPUTS:

{chr(10).join(digest_text)}
"""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def save_weekly_recap(content, target, source_dates):
    """Write weekly recap markdown and update weekly-index.json."""
    os.makedirs(NEWS_DIR, exist_ok=True)
    start, end = week_window(target)
    ident = week_id(target)
    path = os.path.join(NEWS_DIR, f"{ident}-weekly.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}")

    index = {"weeks": [], "lastUpdated": None}
    if os.path.exists(WEEKLY_INDEX_PATH):
        with open(WEEKLY_INDEX_PATH, encoding="utf-8") as f:
            index = json.load(f)

    entry = {
        "id": ident,
        "label": f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "sourceDates": source_dates,
        "path": f"news/{ident}-weekly.md",
    }

    weeks = [w for w in index.get("weeks", []) if w.get("id") != ident]
    weeks.insert(0, entry)
    weeks.sort(key=lambda item: item.get("endDate", ""), reverse=True)
    index["weeks"] = weeks[:26]
    index["lastUpdated"] = datetime.now(timezone.utc).isoformat()

    with open(WEEKLY_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print("Updated weekly index")
    return path


def build_weekly_recap_for_date(target_date, client=None):
    """Build a weekly recap from the current ISO week's saved daily digests."""
    start, end = week_window(target_date)
    digests = []

    current = start
    while current <= end:
        markdown = read_digest_markdown(current)
        if markdown:
            digests.append({
                "date": current.isoformat(),
                "nice_date": current.strftime("%A, %b %d"),
                "markdown": markdown,
                "context": extract_weekly_digest_context(markdown),
            })
        current += timedelta(days=1)

    if len(digests) < 2:
        print("Not enough daily digests available yet for a weekly recap.")
        return None

    print(f"Generating weekly recap from {len(digests)} daily digests...")
    content = generate_weekly_recap(digests, start, end, client)
    save_weekly_recap(content, target_date, [d["date"] for d in digests])
    return week_id(target_date)


# ── Save & Push ────────────────────────────────────────────────────────────────

def save_news(content, target_date, twitter_thread=None, newsletter=None):
    os.makedirs(NEWS_DIR, exist_ok=True)
    filepath = os.path.join(NEWS_DIR, f"{target_date}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filepath}")

    # Save Twitter thread
    if twitter_thread:
        twitter_path = os.path.join(NEWS_DIR, f"{target_date}-twitter.md")
        with open(twitter_path, "w", encoding="utf-8") as f:
            f.write(twitter_thread)
        print(f"Saved: {twitter_path}")

    # Save Newsletter block
    if newsletter:
        newsletter_path = os.path.join(NEWS_DIR, f"{target_date}-newsletter.md")
        with open(newsletter_path, "w", encoding="utf-8") as f:
            f.write(newsletter)
        print(f"Saved: {newsletter_path}")

    index_path = os.path.join(NEWS_DIR, "index.json")
    index = {"dates": [], "lastUpdated": None}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    if target_date not in index["dates"]:
        index["dates"].insert(0, target_date)
        index["dates"] = index["dates"][:90]
    index["lastUpdated"] = datetime.now(timezone.utc).isoformat()
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
    run(["git", "add", "news/", "feed.xml", "sitemap.xml", "robots.txt"])
    r = run(["git", "commit", "-m", f"bash: digest for {target_date}"])
    if "nothing to commit" in r.stdout + r.stderr:
        print("  Nothing new to commit.")
        return
    remote = f"https://{GITHUB_TOKEN}@github.com/danhedrick1/ai-news.git"
    run(["git", "push", remote, "main"])
    print("  Pushed.")


# ── RSS / Sitemap / Robots ─────────────────────────────────────────────────────

def generate_rss_feed():
    """Generate an RSS 2.0 feed from the most recent 20 digests."""
    index_path = os.path.join(NEWS_DIR, "index.json")
    if not os.path.exists(index_path):
        print("No index.json found — skipping RSS feed.")
        return
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    dates = index.get("dates", [])[:20]
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]

    items_xml = []
    for d in dates:
        md_path = os.path.join(NEWS_DIR, f"{d}.md")
        if not os.path.exists(md_path):
            continue
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        y, m, day = d.split("-")
        nice_date = f"{months[int(m)-1]} {int(day)}, {y}"
        desc = content[:500].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # RFC 822 date for RSS
        dt = datetime(int(y), int(m), int(day), 12, 0, 0, tzinfo=timezone.utc)
        pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        items_xml.append(
            f"    <item>\n"
            f"      <title>The Bash — {nice_date}</title>\n"
            f"      <link>https://thebash.dev/{d}</link>\n"
            f"      <description>{desc}</description>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"      <guid>https://thebash.dev/{d}</guid>\n"
            f"    </item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        '    <title>The Bash</title>\n'
        '    <link>https://thebash.dev</link>\n'
        '    <description>High-signal AI &amp; tech news for developers</description>\n'
        + "\n".join(items_xml) + "\n"
        '  </channel>\n'
        '</rss>\n'
    )

    feed_path = os.path.join(REPO_PATH, "feed.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"Generated RSS feed: {feed_path} ({len(items_xml)} items)")


def generate_sitemap():
    """Generate a sitemap.xml from all available digest dates."""
    index_path = os.path.join(NEWS_DIR, "index.json")
    if not os.path.exists(index_path):
        print("No index.json found — skipping sitemap.")
        return
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    dates = index.get("dates", [])
    urls = ['  <url>\n    <loc>https://thebash.dev</loc>\n  </url>']
    for d in dates:
        urls.append(f'  <url>\n    <loc>https://thebash.dev/{d}</loc>\n  </url>')

    if os.path.exists(WEEKLY_INDEX_PATH):
        with open(WEEKLY_INDEX_PATH, encoding="utf-8") as f:
            weekly_index = json.load(f)
        for week in weekly_index.get("weeks", []):
            ident = week.get("id")
            if ident:
                urls.append(f'  <url>\n    <loc>https://thebash.dev/week/{ident}</loc>\n  </url>')

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n"
        '</urlset>\n'
    )

    sitemap_path = os.path.join(REPO_PATH, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"Generated sitemap: {sitemap_path} ({len(urls)} URLs)")


def generate_robots_txt():
    """Generate a robots.txt pointing to the sitemap."""
    robots = "User-agent: *\nAllow: /\nSitemap: https://thebash.dev/sitemap.xml\n"
    robots_path = os.path.join(REPO_PATH, "robots.txt")
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(robots)
    print(f"Generated robots.txt: {robots_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def parse_args(argv):
    """Parse simple CLI args without external dependencies."""
    target_date = None
    weekly_mode = False

    for arg in argv[1:]:
        if arg == "--weekly":
            weekly_mode = True
        elif arg.startswith("--"):
            print(f"ERROR: unknown option '{arg}'")
            sys.exit(1)
        elif target_date is None:
            target_date = arg
        else:
            print("ERROR: only one date argument is supported")
            sys.exit(1)

    return target_date or date.today().isoformat(), weekly_mode


def main():
    target_date, weekly_mode = parse_args(sys.argv)
    try:
        parsed_target = date.fromisoformat(target_date)
    except ValueError:
        print(f"ERROR: bad date '{target_date}', use YYYY-MM-DD")
        sys.exit(1)

    client = None
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            print(f"  [warn] Anthropic client unavailable: {e}")

    if weekly_mode:
        print(f"\n{'='*55}")
        print(f"  The Bash Weekly - {target_date}")
        print(f"{'='*55}\n")

        ident = build_weekly_recap_for_date(parsed_target, client)
        if not ident:
            return

        print("\nRefreshing sitemap and robots.txt...")
        generate_sitemap()
        generate_robots_txt()

        if GITHUB_TOKEN:
            git_push(ident)
        else:
            print("\nNote: GITHUB_TOKEN not set — skipping push.")

        print(f"\nDone. Weekly recap available at: https://thebash.dev/week/{ident}\n")
        return

    print(f"\n{'='*55}")
    print(f"  The Bash — {target_date}")
    print(f"{'='*55}\n")

    print("Fetching RSS sources…")
    articles = fetch_rss_sources()

    print("\nFetching Hacker News…")
    hn_stories = fetch_hacker_news()

    print("\nFetching GitHub Trending…")
    gh_repos = fetch_github_trending()

    print("\nFetching HuggingFace Papers…")
    hf_papers = fetch_huggingface_papers()

    print("\nChecking previously covered stories…")
    articles = mark_previously_covered(articles)

    print("\nScoring and ranking…")
    articles = score_articles(articles, hn_stories, gh_repos, hf_papers)
    print(f"Total scored: {len(articles)} articles")

    content = generate_summary(articles, target_date)

    twitter_thread = None
    newsletter = None
    try:
        if client:
            print("\nGenerating Twitter thread…")
            twitter_thread = generate_twitter_thread(articles, target_date, client)
            print("Generating newsletter block…")
            newsletter = generate_newsletter_block(articles, target_date, client)
        else:
            print("  [warn] Extra formats skipped: ANTHROPIC_API_KEY not available")
    except Exception as e:
        print(f"  [warn] Extra formats failed: {e}")

    save_news(content, target_date, twitter_thread, newsletter)

    print("\nGenerating RSS feed, sitemap, and robots.txt…")
    generate_rss_feed()
    generate_sitemap()
    generate_robots_txt()

    print("\nUpdating covered-stories fingerprints…")
    save_covered(articles, target_date)

    if GITHUB_TOKEN:
        git_push(target_date)
    else:
        print("\nNote: GITHUB_TOKEN not set — skipping push.")

    print(f"\nDone. View at: https://thebash.dev\n")


if __name__ == "__main__":
    main()

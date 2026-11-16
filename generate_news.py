#!/usr/bin/env python3
"""
theba.sh — Daily Digest Generator
Multi-tier source coverage with impact-based ranking.

Stories are filtered to 24h freshness (tier-adjusted), scored by source tier +
HN engagement + cross-source signal, and deduplicated against previous issues.
The digest and weekly recap are composed from those sources. Summaries come
from each feed's own description. No model API is called.

Usage:
  python generate_news.py              # today
  python generate_news.py 2026-03-24   # specific date
  python generate_news.py --weekly     # weekly recap for current ET date

Optional env vars:
  GITHUB_TOKEN   local auto-push, and a higher GitHub API rate limit
"""

import html
import os
import sys
import json
import re
import subprocess
import urllib.request
from datetime import date, datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Config ─────────────────────────────────────────────────────────────────────

SITE_URL          = "https://theba.sh"
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
REPO_PATH         = os.environ.get("REPO_PATH", os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR          = os.path.join(REPO_PATH, "news")
COVERED_PATH      = os.path.join(NEWS_DIR, "covered.json")
WEEKLY_INDEX_PATH = os.path.join(NEWS_DIR, "weekly-index.json")
MIN_PUBLISH_STORIES = 5

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
        # Research from multiple sources — not just arXiv
        "weight": 5,
        "max_age_hours": 72,
        "feeds": [
            ("arXiv cs.AI",             "http://rss.arxiv.org/rss/cs.AI"),
            ("arXiv cs.LG",             "http://rss.arxiv.org/rss/cs.LG"),
            ("arXiv cs.CL",             "http://rss.arxiv.org/rss/cs.CL"),
            ("Google Research Blog",    "https://blog.research.google/feeds/posts/default?alt=rss"),
            ("Microsoft Research Blog", "https://www.microsoft.com/en-us/research/feed/"),
            ("Allen AI Blog",           "https://blog.allenai.org/feed"),
            ("BAIR Blog",              "https://bair.berkeley.edu/blog/feed.xml"),
        ],
    },
    "industry": {
        # Broad news coverage — higher volume, kept or dropped by score
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
        return True   # no date = keep it and let scoring decide
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    return pub_date >= cutoff


# ── Fetching ───────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=12):
    # Reddit blocks bots; use a browser UA for .rss endpoints
    ua = ("Mozilla/5.0 (compatible; theba-sh-bot/1.0; +https://theba.sh)"
          if "reddit.com" not in url else
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


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


def _fetch_single_source(tier, source_name, url, weight, max_age, limit, now, seen_links):
    """Helper: fetch and process a single RSS source. Returns (articles, stats, message)."""
    articles = []
    added = stale = 0
    fetched = 0

    try:
        data  = fetch_url(url)
        items = parse_rss(data)[:limit]

        for title, link, desc, pub_str in items:
            fetched += 1
            if link in seen_links:
                continue
            pub_dt = parse_pub_date(pub_str)
            if not is_fresh(pub_dt, max_age):
                stale += 1
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

        label = f"{added} added" + (f", {stale} stale" if stale else "")
        message = f"  [{tier:8}] {source_name}: {label}"
        return articles, {"fetched": fetched, "stale": stale, "added": added}, message
    except Exception as e:
        message = f"  [{tier:8}] {source_name}: SKIP ({type(e).__name__}: {e})"
        return [], {"fetched": 0, "stale": 0, "added": 0}, message


def fetch_rss_sources():
    """Fetch all sources in parallel, apply freshness filter, return scored article dicts."""
    articles  = []
    seen_links = set()
    now        = datetime.now(timezone.utc)
    totals     = {"fetched": 0, "stale": 0, "added": 0}

    # Collect all feed tasks
    feed_tasks = []
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
            feed_tasks.append((tier, source_name, url, weight, max_age, limit))

    # Fetch feeds in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(_fetch_single_source, tier, source_name, url, weight, max_age, limit, now, seen_links): (tier, source_name)
            for tier, source_name, url, weight, max_age, limit in feed_tasks
        }

        for future in as_completed(futures):
            source_articles, stats, message = future.result()
            articles.extend(source_articles)
            totals["fetched"] += stats["fetched"]
            totals["stale"] += stats["stale"]
            totals["added"] += stats["added"]
            print(message)

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


def titles_overlap(a, b, threshold=0.60):
    """True when two headlines share a real phrase, not one common word."""
    ka, kb = key_words(a), key_words(b)
    if not ka or not kb:
        return False
    shared = len(ka & kb)
    if shared < 2:
        return False
    return shared / min(len(ka), len(kb)) >= threshold


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
            if not aw or not cw:
                continue
            shared = len(aw & cw)
            if shared >= 2 and shared / min(len(aw), len(cw)) >= 0.60:
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
        "headlines": headlines[:30],
        "quick_hits": quick_hits[:30],
        "trend_watch": trend_lines[:3],
    }


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

    # Cross-source boost and same-run deduplication
    # First, detect overlapping titles and boost both
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
        noise_penalty = -20 if re.search(
            r"daily discussion|self-promotion|open thread", a["title"], re.I
        ) else 0
        a["score"]   = a["weight"] + hn_boost + cross_boost + kw_boost + prev_penalty + noise_penalty

    articles.sort(key=lambda x: x["score"], reverse=True)

    # Merge duplicates: keep highest-scored article, absorb alt sources
    merged = []
    absorbed = set()
    for i, a in enumerate(articles):
        if i in absorbed:
            continue
        alt_sources = []
        for j, b in enumerate(articles):
            if j <= i or j in absorbed:
                continue
            if titles_overlap(a["title"], b["title"]):
                alt_sources.append(f"[{b['source']}]({b['link']})")
                absorbed.add(j)
        if alt_sources:
            a["alt_sources"] = alt_sources
        merged.append(a)
    if absorbed:
        print(f"  Merged {len(absorbed)} duplicate article(s)")
    articles = merged

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


# ── Digest formatting ──────────────────────────────────────────────────────────

def format_nice_date(target_date):
    y, m, d = target_date.split("-")
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    return f"{months[int(m)-1]} {int(d)}, {y}"


def mentions(text, tokens):
    """Match whole words so 'bill' does not fire inside 'billion'."""
    return any(re.search(rf"\b{re.escape(token)}s?\b", text) for token in tokens)


def article_classification(article):
    text = f"{article['title']} {article['desc']}".lower()
    link = article["link"].lower()

    if article["tier"] == "research" or "arxiv" in link or "huggingface.co/papers" in link:
        return "research"
    if article["source"] == "GitHub Trending" or "github.com" in link:
        return "tool"
    if mentions(text, ["policy", "regulation", "bill", "court", "copyright", "antitrust"]):
        return "policy"
    if mentions(text, ["funding", "valuation", "acquire", "acquisition", "ipo"]) or re.search(
        r"\braise[sd]?\b.{0,30}(\$|million|billion)", text
    ):
        return "funding"
    if mentions(text, ["lawsuit", "backlash", "criticism", "controversy", "ban", "risk"]):
        return "controversy"
    if mentions(text, ["release", "launch", "api", "sdk", "model", "agent", "tool", "open source"]):
        return "tool"
    if article["tier"] == "primary":
        return "breakthrough"
    return "dev_insight"


def clean_summary(text, limit=420):
    """Return a feed description, trimmed, or an empty string when the feed had none."""
    compact = strip_html(text or "").strip(" -")
    if not compact:
        return ""
    if len(compact) <= limit:
        return compact
    cutoff = compact[:limit].rsplit(" ", 1)[0].strip()
    return f"{cutoff}…"


def source_signal(article):
    signals = []
    if article.get("hn_points", 0) > 0:
        signals.append(f"HN {article['hn_points']}pts/{article['hn_comments']}cmts")
    if article.get("cross_sources", 1) > 1:
        signals.append(f"{article['cross_sources']} outlets")
    if article.get("age_str"):
        signals.append(article["age_str"])
    if article.get("prev_covered"):
        signals.append("seen earlier this week")
    return " · ".join(signals)


# ── Compose digest and weekly recap ────────────────────────────────────────────

TOPIC_LABELS = {
    "breakthrough": "breakthroughs",
    "tool": "tools",
    "funding": "funding",
    "controversy": "controversy",
    "dev_insight": "builder notes",
    "research": "research",
    "policy": "policy",
}

TOPIC_ORDER = [
    "breakthrough",
    "tool",
    "research",
    "funding",
    "policy",
    "controversy",
    "dev_insight",
]

TOPIC_HEADINGS = {
    "breakthrough": "Launches and lab news",
    "tool": "Tools and open source",
    "research": "Research",
    "funding": "Funding and deals",
    "policy": "Policy",
    "controversy": "Controversy",
    "dev_insight": "Builder notes",
}


def story_headline(article):
    headline = (article.get("title") or "").strip()
    if article.get("paywalled") and "[PAYWALL]" not in headline:
        headline += " [PAYWALL]"
    return headline


def render_story(article):
    """One ranked story: headline, feed summary, and the source link."""
    meta_bits = [article["source"]]
    signal = source_signal(article)
    if signal:
        meta_bits.append(signal)
    lines = [
        f"### {story_headline(article)}",
        "",
        f"*[{article_classification(article)}]* {' · '.join(meta_bits)}",
        "",
    ]
    blurb = clean_summary(article.get("desc", ""))
    if blurb:
        lines.extend([blurb, ""])
    alt = article.get("alt_sources") or []
    if alt:
        lines.extend(["Also covered by: " + " · ".join(alt), ""])
    lines.extend([
        f"**Source:** [{article['source']}]({article['link']})",
        f"[Read more →]({article['link']})",
        "",
    ])
    return lines


def render_linked_item(article):
    blurb = clean_summary(article.get("desc", ""), limit=180)
    title = re.sub(r"\s*\[PAYWALL\]\s*", " ", article.get("title") or "")
    title = re.sub(r"\s+", " ", title).strip()
    line = f"- **[{title}]({article['link']})**"
    if blurb:
        line += f" — {blurb}"
    if article.get("paywalled"):
        line += " [PAYWALL]"
    return line


def compose_daily_digest(articles, target_date):
    """Publishable daily digest built only from ranked source items."""
    nice_date = format_nice_date(target_date)
    unique_sources = len({a["source"] for a in articles})
    used_links = set()

    def pick(stories, limit, predicate=None):
        chosen = []
        for article in stories:
            link = article.get("link")
            if not link or link in used_links:
                continue
            if predicate and not predicate(article):
                continue
            chosen.append(article)
            used_links.add(link)
            if len(chosen) >= limit:
                break
        return chosen

    lead_pool = [
        article for article in articles
        if article["source"] not in {"GitHub Trending", "HuggingFace Papers"}
        and article["tier"] != "research"
    ]
    top_stories = pick(lead_pool, 8)
    if len(top_stories) < 5:
        top_stories.extend(pick(articles, 5 - len(top_stories)))

    research_entries = pick(
        articles,
        6,
        lambda article: article["tier"] == "research" or article_classification(article) == "research",
    )
    repo_entries = pick(
        articles,
        6,
        lambda article: (
            article["source"] == "GitHub Trending" or "github.com" in article["link"].lower()
        ),
    )
    policy_entries = pick(
        articles,
        6,
        lambda article: article["tier"] == "policy" or article_classification(article) == "policy",
    )
    funding_entries = pick(
        articles,
        6,
        lambda article: article_classification(article) == "funding",
    )
    quick_hits = pick(articles, 40)

    lines = [
        "---",
        "",
        f"# theba.sh — {nice_date}",
        "",
        (
            f"*{unique_sources} sources · {len(articles)} stories · ranked by impact · "
            "headlines and source summaries*"
        ),
        "",
        "---",
        "",
    ]

    if top_stories:
        lines.extend(["## stdout // the big story", ""])
        lines.extend(render_story(top_stories[0]))
        if len(top_stories) > 1:
            lines.extend(["---", "", "## stdout // top stories", ""])
            for article in top_stories[1:]:
                lines.extend(render_story(article))

    def section(heading, entries):
        if not entries:
            return
        lines.extend(["---", "", heading, ""])
        for article in entries:
            lines.append(render_linked_item(article))
        lines.append("")

    section("## man pages // deep cuts", research_entries)
    section("## pkg ls // repos & open source", repo_entries)
    section("## /etc/rules.d // compliance watch", policy_entries)
    section("## tail -f // cap table", funding_entries)

    if quick_hits:
        grouped = {}
        for article in quick_hits:
            grouped.setdefault(article["source"], []).append(article)
        order = sorted(
            grouped,
            key=lambda source: max(item["score"] for item in grouped[source]),
            reverse=True,
        )
        lines.extend(["---", "", "## stderr // quick hits", ""])
        for source in order:
            lines.extend([f"**{source}**", ""])
            for article in grouped[source]:
                lines.append(render_linked_item(article))
            lines.append("")

    topic_counts = {}
    source_counts = {}
    multi = 0
    seen_earlier = 0
    for article in articles:
        topic = TOPIC_LABELS.get(article_classification(article), "builder notes")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        source_counts[article["source"]] = source_counts.get(article["source"], 0) + 1
        if article.get("cross_sources", 1) > 1:
            multi += 1
        if article.get("prev_covered"):
            seen_earlier += 1

    topic_line = ", ".join(
        f"{name} {count}"
        for name, count in sorted(topic_counts.items(), key=lambda item: (-item[1], item[0]))
    )
    busiest = sorted(source_counts.items(), key=lambda item: (-item[1], item[0]))[:6]
    source_line = ", ".join(f"{name} ({count})" for name, count in busiest)
    notes = []
    if multi:
        noun = "story was" if multi == 1 else "stories were"
        notes.append(f"{multi} {noun} confirmed by more than one outlet")
    if seen_earlier:
        notes.append(f"{seen_earlier} overlap with something already covered in the last week")

    lines.extend([
        "---",
        "",
        "## crontab -l // trend watch",
        "",
        f"{len(articles)} stories from {len(source_counts)} outlets made the board after deduplication.",
        "",
        f"Topic mix: {topic_line}.",
        "",
        f"Busiest outlets: {source_line}.",
        "",
    ])
    if notes:
        lines.extend(["; ".join(notes) + ".", ""])
    lines.extend([
        "---",
        "",
        f"*theba.sh · {nice_date} · {unique_sources} outlets monitored · built for builders*",
        "",
        "---",
    ])
    return "\n".join(lines)


def clean_headline(title, limit=160):
    title = html.unescape(title or "")
    title = re.sub(r"\s*\[PAYWALL\]\s*", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    if len(title) <= limit:
        return title
    cutoff = title[:limit].rsplit(" ", 1)[0].strip(" :,-")
    return f"{cutoff}…"


def looks_like_repo(title):
    return bool(re.match(r"^[\w.\-]+/[\w.\-]+:", title or ""))


def quick_hit_title(line):
    match = re.search(r"\*\*(.+?)\*\*", line or "")
    return clean_headline(match.group(1) if match else "")


def classify_title(title):
    return article_classification({
        "title": title,
        "desc": "",
        "tier": "",
        "source": "",
        "link": "",
    })


def digest_link(digest, label=None):
    text = label or digest["nice_date"].split(",")[0]
    return f"[{text}]({SITE_URL}/{digest['date']})"


def cluster_weekly_items(digests):
    """Merge headlines that repeat across the week's daily issues."""
    clusters = []
    for digest in digests:
        weekday = digest["nice_date"].split(",")[0]
        context = digest["context"]
        candidates = [("headline", clean_headline(title)) for title in context["headlines"]]
        candidates += [("hit", quick_hit_title(line)) for line in context["quick_hits"]]
        for kind, title in candidates:
            if not title:
                continue
            match = None
            for cluster in clusters:
                if titles_overlap(cluster["title"], title, threshold=0.5):
                    match = cluster
                    break
            if match is None:
                clusters.append({
                    "title": title,
                    "kind": kind,
                    "dates": [digest["date"]],
                    "labels": [weekday],
                    "topic": classify_title(title),
                })
                continue
            if digest["date"] not in match["dates"]:
                match["dates"].append(digest["date"])
                match["labels"].append(weekday)
            if kind == "headline" and match["kind"] != "headline":
                match["title"] = title
                match["kind"] = "headline"
                match["topic"] = classify_title(title)
    return clusters


def compose_weekly_recap(digests, week_start, week_end):
    """Weekly index of the saved daily issues. No model call."""
    week_label = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
    by_date = {digest["date"]: digest for digest in digests}
    clusters = cluster_weekly_items(digests)
    raw_count = sum(
        len(digest["context"]["headlines"]) + len(digest["context"]["quick_hits"])
        for digest in digests
    )
    repeated = [cluster for cluster in clusters if len(cluster["dates"]) >= 2]
    repeated.sort(key=lambda cluster: (
        1 if looks_like_repo(cluster["title"]) else 0,
        0 if cluster["kind"] == "headline" else 1,
        -len(cluster["dates"]),
        cluster["title"].lower(),
    ))

    shifts = list(repeated[:6])
    if len(shifts) < 3:
        for cluster in clusters:
            if cluster in shifts or cluster["kind"] != "headline":
                continue
            shifts.append(cluster)
            if len(shifts) >= 5:
                break
    shift_ids = {id(cluster) for cluster in shifts}

    lines = [
        "---",
        "",
        f"# theba.sh weekly - {week_label}",
        "",
        f"*{len(digests)} daily digests · {len(clusters)} distinct stories after dedupe*",
        "",
        "---",
        "",
        "## Week in One Screen",
        "",
        (
            f"This recap indexes {week_start.strftime('%b %d')} through "
            f"{week_end.strftime('%b %d, %Y')}. {len(digests)} daily issues contributed "
            f"{raw_count} headlines and quick hits. After deduplication, {len(clusters)} "
            "distinct stories remain, grouped by topic below. The writeups live on the "
            "linked daily issues; this page is the map."
        ),
        "",
        "## Biggest Shifts",
        "",
    ]

    if shifts:
        for cluster in shifts:
            trail = ", ".join(
                digest_link(by_date[day], label)
                for day, label in zip(cluster["dates"], cluster["labels"])
                if day in by_date
            )
            day_count = len(cluster["dates"])
            span = "one daily issue" if day_count == 1 else f"{day_count} daily issues"
            lines.extend([
                f"### {cluster['title']}",
                "",
                f"Grouped from {span}.",
                "",
                f"**Source trail:** {trail}",
                "",
            ])
    else:
        lines.extend([
            "No headlines were available to promote. The daily log below still links every issue from this week.",
            "",
        ])

    lines.extend(["## By Topic", ""])
    any_topic = False
    for topic in TOPIC_ORDER:
        members = [
            cluster for cluster in clusters
            if cluster["topic"] == topic and id(cluster) not in shift_ids
        ]
        if not members:
            continue
        any_topic = True
        lines.extend([f"**{TOPIC_HEADINGS[topic]}**", ""])
        for cluster in members[:8]:
            digest = by_date.get(cluster["dates"][0])
            link = digest_link(digest, cluster["labels"][0]) if digest else cluster["labels"][0]
            extra = ""
            if len(cluster["dates"]) > 1:
                extra = f" · also {', '.join(cluster['labels'][1:])}"
            lines.append(f"- **{cluster['title']}** — {link}{extra}")
        lines.append("")
    if not any_topic:
        lines.extend(["Every distinct headline is already in Biggest Shifts.", ""])

    lines.extend(["## Daily Signal Log", ""])
    for digest in digests:
        lines.extend([f"### {digest['nice_date']}", ""])
        headlines = [clean_headline(title) for title in digest["context"]["headlines"][:5]]
        headlines = [title for title in headlines if title]
        if headlines:
            lines.extend(f"- {title}" for title in headlines)
        else:
            lines.append("- No section headlines were captured for this issue.")
        lines.extend([
            "",
            f"[Open the daily issue]({SITE_URL}/{digest['date']})",
            "",
        ])

    lines.extend(["## What carried through the week", ""])
    if repeated:
        lines.extend(["These stories showed up on more than one day:", ""])
        for cluster in repeated[:8]:
            lines.append(f"- **{cluster['title']}** — {', '.join(cluster['labels'])}")
        lines.append("")
    else:
        lines.extend([
            "No headline repeated closely enough to merge across days. Use the daily log as the full index.",
            "",
        ])

    lines.extend([
        "---",
        "",
        "*theba.sh weekly - built for builders*",
        "",
        "---",
    ])
    return "\n".join(lines)


def save_weekly_recap(content, target, source_dates):
    """Write weekly recap markdown and update weekly-index.json."""
    os.makedirs(NEWS_DIR, exist_ok=True)
    start, end = week_window(target)
    ident = week_id(target)
    path = os.path.join(NEWS_DIR, f"{ident}-weekly.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}")

    index = {"weeks": []}
    if os.path.exists(WEEKLY_INDEX_PATH):
        with open(WEEKLY_INDEX_PATH, encoding="utf-8") as f:
            index = json.load(f)
    index.pop("lastUpdated", None)

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

    with open(WEEKLY_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print("Updated weekly index")
    return path


def build_weekly_recap_for_date(target_date):
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

    print(f"Composing weekly recap from {len(digests)} daily digests...")
    content = compose_weekly_recap(digests, start, end)
    save_weekly_recap(content, target_date, [d["date"] for d in digests])
    return week_id(target_date)


def generate_og_image(content, target_date):
    """Generate a 1200x630px OG image for social sharing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  [og-image] Pillow not installed, skipping OG image generation")
        return None

    try:
        # Create image
        width, height = 1200, 630
        img = Image.new('RGB', (width, height), color='#0a0e14')
        draw = ImageDraw.Draw(img)

        # Colors from theba.sh theme
        accent_green = '#39d353'
        text_color = '#e6edf3'
        muted_color = '#7a8a9e'

        # Try to use a nice font, fall back to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            story_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            footer_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            title_font = ImageFont.load_default()
            story_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Draw border
        border_width = 4
        draw.rectangle(
            [(border_width//2, border_width//2), (width - border_width//2, height - border_width//2)],
            outline=accent_green,
            width=border_width
        )

        # Extract top 3 stories from markdown
        lines = content.split('\n')
        stories = []
        for i, line in enumerate(lines):
            if line.startswith('### ') and len(stories) < 3:
                story_title = line[4:].strip()
                # Remove [PAYWALL] tag if present
                story_title = story_title.replace('[PAYWALL]', '').strip()
                if len(story_title) > 60:
                    story_title = story_title[:57] + '...'
                stories.append(story_title)

        # Draw title (date)
        y = 40
        formatted_date = format_nice_date(target_date)
        draw.text((60, y), f"theba.sh — {formatted_date}", fill=accent_green, font=title_font)

        # Draw stories
        y = 140
        for story in stories:
            draw.text((60, y), f"• {story}", fill=text_color, font=story_font)
            y += 60

        # Draw footer
        draw.text((60, height - 60), "35 sources • ranked by impact", fill=muted_color, font=footer_font)

        # Save image
        og_images_dir = os.path.join(NEWS_DIR, 'og-images')
        os.makedirs(og_images_dir, exist_ok=True)
        image_path = os.path.join(og_images_dir, f"{target_date}.png")
        img.save(image_path)
        print(f"  [og-image] Generated: {image_path}")
        return image_path
    except Exception as e:
        print(f"  [og-image] Failed to generate: {e}")
        return None


# ── Save & Push ────────────────────────────────────────────────────────────────

def save_news(content, target_date, twitter_thread=None, newsletter=None):
    os.makedirs(NEWS_DIR, exist_ok=True)
    filepath = os.path.join(NEWS_DIR, f"{target_date}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filepath}")

    # Generate OG image for social sharing
    generate_og_image(content, target_date)

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
    index = {"dates": []}
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    index.pop("lastUpdated", None)
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
    run(["git", "add", "news/", "feed.xml", "sitemap.xml", "robots.txt"])
    r = run(["git", "commit", "-m", f"theba.sh: digest for {target_date}"])
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
            f"      <title>theba.sh — {nice_date}</title>\n"
            f"      <link>{SITE_URL}/{d}</link>\n"
            f"      <description>{desc}</description>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"      <guid>{SITE_URL}/{d}</guid>\n"
            f"    </item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        '    <title>theba.sh</title>\n'
        f'    <link>{SITE_URL}</link>\n'
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
    urls = [f'  <url>\n    <loc>{SITE_URL}</loc>\n  </url>']
    for d in dates:
        urls.append(f'  <url>\n    <loc>{SITE_URL}/{d}</loc>\n  </url>')

    if os.path.exists(WEEKLY_INDEX_PATH):
        with open(WEEKLY_INDEX_PATH, encoding="utf-8") as f:
            weekly_index = json.load(f)
        for week in weekly_index.get("weeks", []):
            ident = week.get("id")
            if ident:
                urls.append(f'  <url>\n    <loc>{SITE_URL}/week/{ident}</loc>\n  </url>')

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
    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
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

    if weekly_mode:
        print(f"\n{'='*55}")
        print(f"  theba.sh weekly - {target_date}")
        print(f"{'='*55}\n")

        ident = build_weekly_recap_for_date(parsed_target)
        if not ident:
            return

        print("\nRefreshing sitemap and robots.txt...")
        generate_sitemap()
        generate_robots_txt()

        if GITHUB_TOKEN:
            git_push(ident)
        else:
            print("\nNote: GITHUB_TOKEN not set — skipping push.")

        print(f"\nDone. Weekly recap available at: {SITE_URL}/week/{ident}\n")
        return

    print(f"\n{'='*55}")
    print(f"  theba.sh — {target_date}")
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

    if len(articles) < MIN_PUBLISH_STORIES:
        print(
            f"ERROR: only {len(articles)} stories after ranking. "
            "Refusing to overwrite the published digest."
        )
        sys.exit(1)

    print("\nComposing digest from source headlines…")
    content = compose_daily_digest(articles, target_date)
    save_news(content, target_date)

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

    print(f"\nDone. View at: {SITE_URL}\n")


if __name__ == "__main__":
    main()

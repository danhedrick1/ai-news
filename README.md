# The Bash

High-signal AI and developer news for builders. The site is a static Vercel deployment with a Python digest generator, lightweight Vercel Functions for newsletter capture, and scheduled GitHub Actions for daily and weekly publishing.

## What It Does

- Generates a daily digest from ranked RSS, HN, GitHub, and research sources
- Generates Twitter/X and newsletter-format variants when Anthropic is configured
- Publishes a weekly recap from the saved daily issues every Sunday in New York time
- Exposes an inline newsletter signup endpoint for Buttondown or a generic webhook

## Environment

Copy `.env.example` to `.env` and fill in what you need:

- `ANTHROPIC_API_KEY`: required for daily digest generation and AI-written variants
- `GITHUB_TOKEN`: optional for local auto-push behavior
- `BUTTONDOWN_API_KEY`: optional, used by `api/newsletter-subscribe.mjs`
- `NEWSLETTER_WEBHOOK_URL`: optional fallback if you are not using Buttondown

If both newsletter variables are empty, the signup form stays visible but returns a friendly configuration error.

## Local Usage

Daily digest for today:

```bash
python generate_news.py
```

Daily digest for a specific date:

```bash
python generate_news.py 2026-03-25
```

Weekly recap for the current week:

```bash
python generate_news.py --weekly
```

Weekly recap for a specific week-ending date:

```bash
python generate_news.py 2026-03-29 --weekly
```

## Deployment Notes

- `index.html` is the app shell and client-side router
- `api/newsletter-subscribe.mjs` handles signup posts on Vercel
- `news/weekly-index.json` powers the weekly recap surface in the UI
- `.github/workflows/daily-news.yml` now runs the daily digest and conditionally builds the weekly recap on Sundays in `America/New_York`

## Monetization Surfaces

The sponsor rail and job board are intentionally simple and editable in `index.html` via the `MARKET_CONFIG` object. Replace the placeholder `mailto:` links and sample job rows with real inventory when you are ready to sell the surfaces.

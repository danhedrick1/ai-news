# theba.sh — 2026-04-12

The AI money is getting serious and the tooling is maturing fast — $30B ARR at Anthropic, a $100/mo ChatGPT tier, and a model too dangerous to ship. Meanwhile, the open-source build stack keeps compounding.

---

## Headlines

### 💸 ChatGPT Launches $100/Month Pro Tier
OpenAI is moving upmarket with a premium tier aimed at power users willing to pay for priority access and expanded capabilities. This is a clear monetization play ahead of their IPO, signaling they believe there's a ceiling-less market for heavy AI users.
- Targets professionals, researchers, and enterprise power users
- Likely unlocks higher rate limits and advanced model access
- Competitive pressure on Anthropic's Claude Pro and similar offerings

**🔧 Dev Take:** "If your workflow depends on it, $100/mo is noise — but watch if the API pricing follows suit."

---

### 🦇 Anthropic Hits $30B ARR, Drops Project GlassWing and a Model Too Hot to Ship
Anthropic is aggressively flexing before OpenAI's IPO window: $30B ARR, a new initiative called Project GlassWing, and a Claude variant they've internally flagged as too dangerous to release — the first model in that category since GPT-2. This is a calculated narrative move as much as a technical milestone.
- $30B ARR puts Anthropic in serious revenue territory, not just valuation theater
- "Claude Mythos" preview signals a new capability frontier being gated deliberately
- Anthropic is positioning safety restraint as a competitive differentiator

**🔧 Dev Take:** "A model too dangerous to release is either genuinely alarming or the best marketing Anthropic has ever done — possibly both."

---

### 🤖 ClawBench: Can AI Agents Actually Handle Everyday Online Tasks?
A new benchmark paper tests AI agents on the kind of mundane browser-based tasks real users actually care about — booking, forms, inbox management, and routine web workflows. Results suggest agents are improving but still inconsistent on the long-tail of real-world friction.
- Tests multi-step tasks that require navigating real UI states, not toy environments
- Highlights the gap between demo performance and reliable daily-driver behavior
- Useful signal for teams building agentic products on top of LLMs

**🔧 Dev Take:** "Benchmarks on real tasks > benchmarks on benchmarks — ClawBench is the kind of eval that actually maps to production pain."

---

### 🧱 Haystack: Open-Source LLM Orchestration Worth a Second Look
deepset's Haystack continues trending with 24K+ stars as teams look for production-grade alternatives to LangChain with more explicit pipeline control. Its modular, component-based architecture is a good fit for teams who want observability and reproducibility baked in.
- Pipelines are declarative and composable — easier to debug than magic abstractions
- Native support for RAG, agents, and custom component integration
- Strong fit for teams already operating in Python-heavy ML infrastructure

**🔧 Dev Take:** "If LangChain feels like magic you can't control, Haystack is the boring-in-a-good-way alternative."

---

### 📊 MLflow Doubles Down on Agents and LLM Evaluation
MLflow (25K+ stars) is expanding beyond experiment tracking into a full AI engineering platform covering agents, LLM evaluation, and production monitoring. For teams already using MLflow for traditional ML, this is a low-friction path into structured LLM ops.
- Evaluation and monitoring hooks for LLM outputs are now first-class features
- Integrates with major model registries and deployment targets
- Lowers the barrier to bringing MLOps discipline to LLM workflows

**🔧 Dev Take:** "MLflow eating into the LLMOps space makes sense — don't rebuild observability infrastructure if you already have it."

---

### 💀 Reddit Declares "The Era of Human Coding Is Over"
The r/singularity crowd is doing what they do, but the underlying signal — that AI coding tools are now genuinely displacing significant chunks of human-written code in production workflows — is worth separating from the hype. The debate is real even if the framing is dramatic.
- Cursor, Copilot, and agent-based coding workflows are compressing junior dev output
- The real question is scope: automation of tasks vs. replacement of engineering judgment
- Productivity multiplier framing is more accurate than "replacement" for most senior devs

**🔧 Dev Take:** "The era of writing boilerplate by hand might be over. The era of needing engineers who can reason about systems is not."

---

## Quick Hits

- **f/prompts.chat** (159K ⭐) — the community prompt library keeps growing; self-hostable for org privacy if you need it
- **rasbt/LLMs-from-scratch** (90K ⭐) — still the best resource if you want to actually understand what you're building on top of
- **OpenBB** (65K ⭐) — financial data platform with native AI agent support; worth a look if you're building in fintech
- **netdata/netdata** (78K ⭐) — AI-assisted full-stack observability in C; lean teams take note if you're not already on it
- **Anthropic IPO watch** — OpenAI's IPO timeline makes every Anthropic announcement land with extra weight right now; read accordingly

---

*theba.sh — built for builders*
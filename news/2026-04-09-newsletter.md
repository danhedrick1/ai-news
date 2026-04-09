# theba.sh — 2026-04-09

The open model ecosystem keeps shipping while OpenAI's internal culture starts showing cracks. If you're building, the tooling and model landscape just got meaningfully better this week.

---

## Headlines

### EXAONE-4.5-33B Drops from LG AI Research
LG's AI division quietly released a 33B parameter model that's turning heads on r/LocalLLaMA. At this size, it's squarely in the "run it on a single high-end GPU" tier — worth benchmarking against your current local stack.
- 33B parameter open model from LG AI Research (EXAONE series)
- Active community testing and evals already underway on r/LocalLLaMA
- Adds meaningful competition in the 30B+ local model bracket
**🔧 Dev Take:** "Pull it, run it, form your own opinion — don't wait for the benchmark consensus."

---

### Gemma 4: Google's Best Small Multimodal Open Model Yet
Google pushed a significant update to the Gemma line, and the Latent Space team is calling it dramatically better than Gemma 3 across the board — including multimodal capabilities. For devs who need a capable, deployable open model without the weight of a 70B+, this is the one to watch right now.
- Multimodal support is the headline upgrade over Gemma 3
- "Best small open multimodal model" is a strong claim, but early reports back it up
- Production-ready small models matter more than frontier benchmarks for most builders
**🔧 Dev Take:** "If you've been sleeping on Gemma, Gemma 4 is the reason to wake up."

---

### The Vibes Are Off at OpenAI
The Verge is reporting on a noticeable cultural and internal tension at OpenAI — even as the company just closed $122B in funding at an $852B valuation. Money is not the problem; clarity of mission and organizational coherence apparently are.
- $122B raise, $852B post-money valuation — the numbers are staggering
- Internal culture described as increasingly strained and misaligned
- Rapid product pivots and leadership pressure are likely contributors
**🔧 Dev Take:** "The richest lab in history having a vibe problem is a signal, not a footnote."

---

### Google Research: Social Learning with LLMs
Google's research blog published work on collaborative, multi-agent learning frameworks where LLMs learn socially — essentially by interacting with each other. This is foundational work for anyone building multi-agent pipelines who wants more than just tool-calling chains.
- Explores how LLMs can learn collaboratively rather than in isolation
- Relevant to agent framework design and multi-model pipeline architecture
- Points toward more adaptive, emergent behavior in production agent systems
**🔧 Dev Take:** "The shift from 'single model doing tasks' to 'models learning from each other' is where agentic systems get actually interesting."

---

### Haystack Hits 24.7K Stars — Production LLM Pipelines Getting Serious
deepset's Haystack continues trending on GitHub, signaling that the "context-engineered, production-ready LLM application" framing is resonating with builders. Modular pipelines with explicit control are winning over magic black-box frameworks.
- Open-source orchestration framework for production LLM apps
- 24,772 GitHub stars and trending — adoption is real, not just hype
- Explicit pipeline control and modularity are the design philosophy
**🔧 Dev Take:** "If your LLM app is held together with string and LangChain callbacks, Haystack is worth an honest look."

---

## Quick Hits

- **MLflow (25.2K ⭐)** — Also trending; the AI engineering platform for agents and LLMs is becoming the de facto eval/monitor layer for production ML teams.
- **Claude Opus vs. Mythos (r/singularity)** — Community benchmark thread comparing Anthropic's Opus to Mythos; worth skimming if you're choosing a frontier model for complex reasoning tasks.
- **"Too Dangerous to Release" (The Neuron)** — Another capability apparently being held back from public release; the pattern of selective disclosure continues.
- **Project Glasswing called out as cartel behavior (r/artificial)** — Community flagging coordinated AI industry behavior; details murky but the thread is heated and worth watching.
- **Peacock promo codes (Wired)** — 40% off streaming. Not a dev tool. Skip it.

---

*theba.sh — built for builders*
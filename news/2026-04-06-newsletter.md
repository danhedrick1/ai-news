# theba.sh — 2026-04-06

The world woke up this weekend to missile strikes taking down AWS infrastructure in the Gulf and OpenAI's executive team crumbling ahead of its IPO — AI is no longer just a software problem. If you built on top of any of this stuff, you felt it.

---

## Headlines

### Iran Strikes U.S.-Linked "Stargate" AI Data Centers
Iran followed through on threats and targeted U.S.-linked data centers, with AWS infrastructure in the Gulf region reportedly going dark. This is the first time geopolitical conflict has directly taken out major AI cloud capacity at scale.
- AWS Gulf region outages confirmed following strikes
- Stargate-linked infrastructure explicitly named as a target
- Raises immediate questions about geographic redundancy for AI workloads

**🔧 Dev Take:** "If your production AI stack has a single-region Gulf dependency and no failover, this weekend was your architecture review."

---

### OpenAI's Executive Bench Collapses Ahead of IPO
Multiple senior leaders departed OpenAI in a compressed window, right as the company is navigating its IPO process. The timing is brutal — investor confidence in leadership continuity is not a nice-to-have at this stage.
- Executive departures clustered in a single weekend
- IPO timeline now under heightened scrutiny
- Adds to an already chaotic week that included the Claude Code source leak

**🔧 Dev Take:** "Companies ship products; executives ship org charts — watch what the engineers do next, not the press releases."

---

### The Claude Code Source Leak
Anthropic's Claude Code was accidentally "open sourced" — enough internals surfaced to give the community a detailed look under the hood. The leaks reveal meaningful architectural and prompting decisions that weren't public before.
- Accidental exposure, not a breach — Anthropic has not confirmed full scope
- Community already dissecting the system prompt and tool-use scaffolding
- Anthropic's agentic coding approach now considerably less opaque

**🔧 Dev Take:** "Reading a competitor's leaked system prompt is the 2026 equivalent of reading their engineering blog — do it."

---

### An AI Agent Hacked FreeBSD in Four Hours
An autonomous AI agent successfully exploited FreeBSD in under four hours over the weekend. This is a concrete, documented case — not a benchmark, not a CTF toy environment — and it matters.
- Full compromise achieved without human intervention mid-run
- Timeline of four hours puts it well within automated attack thresholds
- Security teams need to update their threat models *now* if agents are in scope

**🔧 Dev Take:** "Four hours is faster than your on-call response time. Assume agents are part of your threat surface."

---

### Gemma 4 Drops: Google's Best Small Multimodal Models Yet
Google released Gemma 4, a significant step up from Gemma 3 across the board, with multimodal capabilities that punch well above its weight class. For teams running open models locally or on constrained infrastructure, this changes the calculus.
- Dramatically improved multimodal performance vs. Gemma 3
- Small footprint means realistic local and edge deployment
- Positions Google's open model line as a serious alternative to proprietary APIs

**🔧 Dev Take:** "If you wrote off open small models for multimodal tasks six months ago, re-run your evals today."

---

### DeepSeek V4 to Run on Huawei Chips
DeepSeek V4 is targeting Huawei Ascend hardware — a deliberate architectural choice that sidesteps U.S. export controls entirely. The geopolitical and technical implications are both significant.
- Signals maturation of the non-NVIDIA AI hardware ecosystem in China
- DeepSeek continues to ship capable models outside the Western chip stack
- Export control strategy is actively being routed around at the model layer

**🔧 Dev Take:** "The chip war's effectiveness is increasingly a question of months, not years."

---

### Do Audio-Visual LLMs Actually See and Hear? (New Research)
A new mechanistic interpretability paper takes the first deep look at whether AVLLMs are genuinely integrating audio and visual signals or just pattern-matching on unimodal shortcuts. Early findings suggest more shallow fusion than the benchmarks imply.
- First mechanistic interpretability study specifically targeting AVLLMs
- Gap between benchmark performance and actual multimodal reasoning appears significant
- Has direct implications for anyone deploying AV models in production pipelines

**🔧 Dev Take:** "Before you ship an audio-visual pipeline, read this paper — benchmark numbers are hiding something."

---

## Quick Hits

- **haystack (24.7k ⭐)** — deepset's LLM orchestration framework keeps climbing; worth a look if LangChain is feeling heavy for your use case
- **mlflow (25.1k ⭐)** — open source AI engineering platform for agents and LLMs; experiment tracking for production workloads, not just notebooks
- **prompts.chat (157k ⭐)** — still the largest community prompt library; now self-hostable for orgs that need privacy
- **Mark Zuckerberg & Garry Tan coding with AI** — C-suite is picking up editors again; the signal is that AI has genuinely lowered the floor back to zero
- **Claude Code had a bad week** — source leak plus Pragmatic Engineer coverage of GitHub stumbles; two black eyes in 48 hours
- **Using Discord on Plan 9** — someone got it working; the Lobste.rs thread is the most niche-joy thing you'll read today
- **Anthropic acquired a company this weekend** — details sparse, but it dropped during the same news cycle as the Claude Code leak

---

*theba.sh — built for builders*
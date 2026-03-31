# theba.sh — 2026-03-31

The CLI is eating the world, and autonomous agents are eating the codebase. Today's feed is a coherent signal: the interface layer is collapsing toward the terminal, and the human-in-the-loop is getting pushed further and further out.

---

## Headlines

### Computer Use Lands in Claude Code
Anthropic has shipped computer use directly into Claude Code, meaning the model can now observe and interact with your actual desktop environment — not just your codebase. This closes the loop between code generation and execution in a way that makes "agentic" feel less like a buzzword.
- Claude Code can now click, scroll, and interact with UI elements mid-session
- Reduces the need for human handoffs between "write code" and "verify it works"
- Raises the floor for what "autonomous coding agent" actually means in practice

**🔧 Dev Take:** "Your QA pipeline just got a new intern that doesn't sleep."

---

### Everything is CLI: The Quiet Consolidation of Agent Interfaces
Latent Space's AINews flags a pattern that's been hiding in plain sight: nearly every serious agent framework, LLM toolchain, and dev product released in the last 90 days ships a CLI first. GUIs are an afterthought, if they exist at all.
- Agents need scriptable, composable interfaces — GUIs don't fit that contract
- CLI-first design aligns with how pipelines, cron jobs, and CI systems actually work
- The "chat UI" era may be giving way to the "pipe operator" era

**🔧 Dev Take:** "The terminal won. Again. It always wins."

---

### "The Era of Human Coding Is Over"
The r/singularity crowd is amplifying a narrative that's getting harder to dismiss: AI isn't augmenting developers anymore, it's replacing the core loop. The debate is less about *if* and more about *how fast* and *for whom*.
- Junior and mid-level coding tasks are the most immediately exposed
- The remaining human value is shifting toward architecture, judgment, and taste
- "Vibe coding" discourse is maturing into a real skills conversation

**🔧 Dev Take:** "Knowing what to build still matters — knowing how to type it, less so."

---

### Google Research: LLMs Can Teach Each Other (Social Learning)
Google Research published work on "social learning" — a framework where LLMs learn from each other's outputs without direct access to raw training data. It's a meaningful step toward distributed, privacy-preserving model improvement.
- Models share learned behaviors via natural language rather than gradient updates
- Has practical implications for fine-tuning in regulated or siloed environments
- Could reduce the data-moat advantage of large centralized labs over time

**🔧 Dev Take:** "If models can teach each other, your fine-tuning strategy needs a rethink."

---

### Jack Dorsey Wants AI to Replace Middle Management at Block
Dorsey is making the case internally and publicly that AI can absorb the coordination and oversight functions traditionally held by middle managers, weeks after Block announced layoffs. This is a live experiment in org design, not just rhetoric.
- Dorsey frames it as flatter orgs enabled by AI-driven visibility and decision-making
- Follows a broader Silicon Valley pattern of using AI as cover for structural cuts
- The real question is whether AI tooling can actually absorb accountability, not just meetings

**🔧 Dev Take:** "Replacing managers with AI only works if you've actually built the AI — most haven't."

---

### Granite 4.0 3B Vision: IBM's Multimodal Bet for the Enterprise Edge
IBM's Hugging Face drop of Granite 4.0 3B Vision is a compact multimodal model targeting enterprise document workflows. 3B parameters with vision capability is a meaningful point on the efficiency curve.
- Handles document understanding, tables, charts, and forms at low compute cost
- Open weights, enterprise-licensed, aimed at on-prem and regulated deployments
- Signals that the "vision on everything" trend is reaching the edge inference tier

**🔧 Dev Take:** "If you're still OCR-pipelining enterprise docs in 2026, this is your wake-up call."

---

## Quick Hits

- **Haystack hits 24.6k stars** — deepset's orchestration framework keeps climbing; context engineering is the new prompt engineering
- **MLflow at 25k stars** — agent observability is no longer optional; if you're not tracking, you're guessing
- **Gizmodo warns against app attachment** — compute constraints mean your favorite AI product can vanish overnight; build on APIs with exit strategies
- **AI music roundup from The Verge** — sample sourcing to playlist curation, the legal and ethical fights are just getting started; don't ignore the IP exposure if you're building in this space
- **r/singularity coding discourse heating up** — useful signal for where developer anxiety is concentrating, even if the takes need calibration

---

*theba.sh — built for builders*
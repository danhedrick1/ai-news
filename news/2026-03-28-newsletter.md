# theba.sh — 2026-03-28

The command line is back at the center of the AI stack, and the tools being built around it are starting to look less like toys and more like infrastructure. Today's digest is heavy on frameworks, workflows, and one uncomfortable question about where all this autonomy is heading.

---

## Headlines

### Everything is CLI: Agents Are Finding Their Natural Habitat
The Latent Space / AINews crew noticed something on a quiet news day: the dominant interface pattern for AI agents isn't chat, it's the terminal. CLIs give agents the composability, scriptability, and lack of UI overhead that GUIs simply can't match.
- Agent frameworks are converging on stdin/stdout as the default communication layer
- Claude Code, shell-native tooling, and headless pipelines are driving the trend
- The GUI wrapper is becoming the exception, not the rule

**🔧 Dev Take:** "If your agent needs a UI to be useful, you've probably built a product — not a tool."

---

### The Neuron's AI Skill Digest: 10 Practical Skills Worth Stealing
Ten skills across prompt engineering, multi-agent workflows, and thinking modes — distilled from two weeks of The Neuron's daily newsletter. Less theory, more copy-paste-and-ship.
- Company research prompts and self-improving prompt loops are the standouts
- Multi-agent workflow design gets concrete treatment, not just buzzword coverage
- Claude Code gets its own dedicated skill breakdown

**🔧 Dev Take:** "Skills digests like this are worth more than most $500 courses — just actually implement one."

---

### Anthropic, the Pentagon, and the Future of Autonomous Weapons
Bloomberg digs into Anthropic's relationship with the Department of Defense and what it means for the trajectory of AI in warfare. This is the conversation the AI safety crowd and the defense sector are both avoiding having in public.
- Autonomous weapons development is accelerating faster than governance frameworks
- AI labs with safety mandates are now active players in military procurement
- The gap between "safe AI" messaging and defense contracts is getting hard to ignore

**🔧 Dev Take:** "The most important AI alignment problem in 2026 might not be in a research paper — it might be in a DoD contract."

---

### Haystack & MLflow Both Trending: Production AI Pipelines Are the New Battleground
Two serious open-source frameworks are climbing GitHub trending simultaneously — Haystack (context-engineered LLM pipelines) and MLflow (AI engineering platform for agents and models). The market is clearly hungry for production-grade scaffolding.
- Haystack at 24.6k stars focuses on modular, explicit pipeline control for LLM apps
- MLflow at 25k stars covers the full lifecycle: debug, evaluate, monitor, optimize
- Both signal that "vibe-coding an agent" isn't cutting it in production anymore

**🔧 Dev Take:** "Pick one, go deep. Switching costs between orchestration frameworks are higher than they look."

---

### OpenAI Kills Sora — While VCs Keep Writing Checks
TechCrunch asks the obvious question: if investors are pouring billions into AI's next wave, why is OpenAI quietly shutting down one of its most publicly hyped products? The answer probably involves unit economics and focus, but the optics aren't great.
- Sora was OpenAI's flagship bet on generative video — now it's being wound down
- VC enthusiasm for AI hasn't cooled, but the gap between demos and durable products is widening
- Meanwhile, an 82-year-old Kentucky woman turned down $26M for a data center site — respect

**🔧 Dev Take:** "Hype cycles kill products that demos built — ship revenue, not impressions."

---

## Quick Hits

- **f/prompts.chat** crossed 154k GitHub stars — the prompt-sharing community isn't slowing down; self-hosting option now available for orgs with privacy requirements
- **OpenBB** (63.7k stars) keeps climbing — if you're building anything in fintech + AI agents, this is the data layer worth evaluating
- **PyTorch Lightning** at 31k stars — still the go-to for scaling model training from 1 GPU to 10,000 without refactoring your training loop
- **Garmin watch guide from Wired** — off-topic, but if you're training for anything outdoors this spring, the Fenix line still dominates for serious use cases
- **Multi-agent workflows** show up in three separate stories today — if you're not designing for agent composition yet, you're already behind the curve

---

*theba.sh — built for builders*
# theba.sh — 2026-03-28

The terminal is eating the world, and agents are the ones doing the typing. Today's signal: the shift from GUIs to CLIs isn't a regression—it's infrastructure for the agentic layer being built on top of everything.

---

## Headlines

### Everything is CLI: The Agentic Interface Convergence
Latent Space and AINews are calling out what builders have quietly noticed—CLIs are becoming the default interface layer for AI agents, not a niche developer preference. When your primary "user" is another piece of software, a clean CLI beats a polished GUI every time.
- Agents need deterministic, composable interfaces—CLIs deliver exactly that
- The explosion of agent frameworks is accelerating CLI-first design patterns
- This is infrastructure thinking, not nostalgia for the command line

**🔧 Dev Take:** "If your tool doesn't have a CLI in 2026, your tool doesn't have an agent story."

---

### Anthropic, the Pentagon, and Autonomous Weapons
Bloomberg is reporting on Anthropic's deepening relationship with the U.S. Department of Defense and what it means for AI-driven autonomous weapons systems. This isn't hypothetical anymore—the decisions being made now about AI autonomy in warfare will be locked in for decades.
- Constitutional AI meets the laws of war: a collision course with no clean answers
- Anthropic's "safety-focused" brand identity is under real pressure here
- Every major AI lab will face this moment; Anthropic is just first in the spotlight

**🔧 Dev Take:** "The most consequential alignment problem right now isn't a benchmark—it's a contract."

---

### The Era of Human Coding Is Over (r/singularity Weighs In)
Reddit's singularity community is declaring the end of human-authored code as the primary mode of software production. Hyperbole aside, the underlying trend is real—AI-generated code is no longer a curiosity, it's the majority output in many professional workflows.
- The debate isn't whether AI writes code, it's whether humans understand what's being written
- Code review skills are now more valuable than code-writing skills
- "Over" is too strong, but "dominant" is probably accurate within 18 months

**🔧 Dev Take:** "The job title is shifting from 'software engineer' to 'software editor'—get comfortable with that."

---

### How to Install Skills in Claude Code: A Practical Guide
dev.to drops a concrete walkthrough on extending Claude Code with packaged skill sets—think of it as plugins for your AI coding agent. This is the kind of applied, unglamorous tooling content that actually moves the needle for working developers.
- Skills encapsulate repeatable task logic: commit messages, code review patterns, deploy checklists
- Three distinct install methods give flexibility depending on your workflow and team setup
- This is the missing manual that Anthropic's docs haven't fully covered yet

**🔧 Dev Take:** "Customizing your AI coding agent is now a legitimate part of your dev environment setup—treat it like dotfiles."

---

### Haystack Hits 24K Stars: Context Engineering Is the New RAG
deepset-ai/haystack is trending on GitHub as the framing shifts from "RAG pipelines" to "context engineering"—a more deliberate, architectural approach to what goes into an LLM's context window. The star count reflects a maturing ecosystem looking for production-grade primitives.
- Modular pipeline design means you own the data flow, not the framework
- "Context-engineered" is doing a lot of work in the AI tooling space right now—worth watching
- Haystack is positioning itself as the serious alternative to LangChain for teams that want explicit control

**🔧 Dev Take:** "Context engineering is just prompt engineering with better version control and less magical thinking."

---

### MLflow Expands to Full AI Engineering Platform
MLflow is no longer just experiment tracking—it's making a credible play for the entire AI engineering lifecycle, from agent debugging to production monitoring. At nearly 25K stars and Python-native, it's the incumbent with the broadest adoption base in the space.
- Covers agents, LLMs, and classical ML in one platform—rare breadth
- Production monitoring for agents is the genuinely hard, underserved problem MLflow is targeting
- Teams already using MLflow for ML will find the LLM tooling a natural extension

**🔧 Dev Take:** "MLflow is the unsexy choice that keeps winning because it works in the stack you already have."

---

## Quick Hits

- **9to5Mac | RIP Mac Pro:** Apple quietly sunsets the Mac Pro, closing a chapter on modular pro desktop hardware—pour one out for the cheese grater.
- **GitHub Trending | f/prompts.chat (154K ⭐):** The prompt-sharing community isn't slowing down—still the biggest repo of its kind, now with self-hosting for orgs.
- **GitHub Trending | OpenBB (63K ⭐):** OpenBB is becoming the Bloomberg Terminal alternative for teams that want AI agents running on financial data pipelines.
- **GitHub Trending | PyTorch Lightning (31K ⭐):** Zero-code-change scaling from 1 to 10,000 GPUs is trending again—fine-tuning season is apparently not over.
- **Meta signal:** Three of today's top GitHub repos are orchestration or tooling layers—the model wars are cooling, the infrastructure wars are heating up.

---

*theba.sh — built for builders*
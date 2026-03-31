# theba.sh — 2026-03-31

The story today is Claude Code eating everything — computer use, hidden power features, and a creator who just showed his hand. Meanwhile, the CLI-as-agent-interface pattern is quietly becoming the default architecture nobody planned for.

---

## Headlines

### Everything is CLI: Agents Are Converging on the Terminal
A slow news day produced a sharp observation from Latent Space/AINews: CLIs aren't a throwback — they're becoming the canonical interface for agents operating in production environments. Structured, composable, scriptable. It makes sense when you think about it.
- Text in, text out maps cleanly to LLM I/O with no UI overhead
- CLIs compose naturally into pipelines agents can reason about and invoke
- The terminal is effectively the universal API for agentic workflows
**🔧 Dev Take:** "The GUI was always a human affordance — agents don't need it."

---

### Computer Use Lands in Claude Code
Claude Code now ships with computer use capabilities, meaning agents can navigate GUIs, click buttons, and operate software that has no API. This closes a significant gap for automation tasks that were previously off-limits.
- Handles legacy software and web UIs that lack programmatic interfaces
- Expands the surface area of what Claude Code can autonomously complete
- Raises the floor on what "agentic coding assistant" actually means in practice
**🔧 Dev Take:** "If your workflow still requires a human to click things, that excuse just got smaller."

---

### Boris Cherny Reveals 15 Claude Code Power Features
The creator of Claude Code dropped a list of 15 features he uses daily — most of which users haven't discovered on their own. This is the kind of inside knowledge that separates 2x users from 10x users.
- Custom slash commands, memory files, and project-level context are all under-leveraged
- Features like `--continue` and session management reshape how you structure long tasks
- Knowing the tool's own creator's workflow is as close to a cheat sheet as you'll get
**🔧 Dev Take:** "Read the creator's list once, then delete the habits you built from guessing."

---

### Google Research: Social Learning with LLMs
Google's research blog published work on collaborative learning between LLMs — models that learn from each other's outputs rather than purely from static training data. This is early but directionally important infrastructure thinking.
- Models can share "experiences" as natural language, no weight transfer required
- Opens a path toward networks of specialized agents that improve collectively
- Distinct from federated learning — this operates at the prompt/context layer
**🔧 Dev Take:** "Agents teaching agents is either the most elegant scaling path or the fastest way to launder model errors — probably both."

---

### Haystack Hits 24K Stars — Context Engineering Is the New Prompt Engineering
deepset's Haystack framework is trending hard, and the framing shift in their own description is worth noting: "context-engineered" applications, not just "prompt-engineered" ones. The vocabulary is moving.
- Modular pipeline architecture gives explicit control over what context reaches the model
- Production-ready positioning means it's built for teams shipping real systems, not demos
- Growing alongside the broader move away from monolithic LLM calls toward structured flows
**🔧 Dev Take:** "If you're still thinking in prompts and not pipelines, you're one abstraction behind."

---

### "The Era of Human Coding Is Over" — r/singularity Is Loud Again
The Reddit discourse is running hot following the Claude Code computer use announcement. The claim is big; the evidence is mounting.
- Agentic coding tools are now handling full tasks, not just autocomplete
- The debate is less about *if* and more about *what humans do next* in the stack
- Worth filtering signal from hype, but the direction of travel is not seriously in dispute
**🔧 Dev Take:** "The era of human coding being the *only* option — yeah, that one's over."

---

## Quick Hits

- **MLflow at 25K stars** — The AI engineering platform keeps growing; evaluation and monitoring are becoming non-negotiable for production agents. [GitHub Trending]
- **OpenBB hits 64K stars** — Financial data platform explicitly positioning for AI agents now, not just human analysts. Quants, take note. [GitHub Trending]
- **prompts.chat at 155K stars** — Still the top prompt repo; rebranded from Awesome ChatGPT Prompts, now community-driven and self-hostable. [GitHub Trending]
- **AI and music: everywhere and messy** — The Verge covers AI across the full music stack; legal and ethical frameworks are still way behind the tooling. [The Verge]
- **Computer use in Claude Code also means more attack surface** — Worth reading the security implications before you let an agent start clicking around in production environments. [Builder reminder]

---

*theba.sh — built for builders*
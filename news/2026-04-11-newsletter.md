# theba.sh — 2026-04-11

The machines are writing the code, and someone's throwing molotovs at the guy building them. It's a normal week in AI.

---

## Headlines

### The Era of Human Coding Is Over (According to Reddit, At Least)
The r/singularity crowd is declaring victory for AI coding tools, and the anecdotal evidence is stacking up fast. Whether it's "over" or just "fundamentally changed" depends on what you're shipping.
- Vibe coding is moving from side projects to production systems
- Junior dev hiring freezes are becoming a real pattern at AI-native shops
- The debate is no longer *if* but *how much* human oversight is still needed
**🔧 Dev Take:** "The era of human *typing* code may be over — the era of human *judgment* in code is just getting started."

---

### Claude Code + n8n: Agents That Actually Do Stuff
Builders are pairing Anthropic's Claude Code with n8n's workflow automation and getting genuinely useful autonomous pipelines. This combo is quietly becoming one of the more practical agentic stacks in the wild.
- n8n handles the workflow orchestration and integrations; Claude Code handles the reasoning and code execution
- Low-code entry point means non-engineers can wire up surprisingly capable agents
- Still early, but the Reddit thread is full of working demos, not just promises
**🔧 Dev Take:** "If you haven't spun up an n8n + Claude pipeline yet, you're leaving real automation hours on the table."

---

### OpenAI Launches $100/Month ChatGPT Tier
OpenAI is moving upmarket with a premium tier aimed at power users who've been hitting limits on the $20 plan. More compute, higher rate limits, and access to frontier models first.
- Positions OpenAI to capture prosumer and solo-dev budgets before enterprise contracts kick in
- Pressure mounts on Anthropic and Google to match or differentiate on value
- The gap between free-tier and paid-tier AI capability is widening fast
**🔧 Dev Take:** "At $100/month, this needs to save you at least two hours a week to justify itself — for most heavy users, it probably does."

---

### Sam Altman's House Targeted With Molotov Cocktail
A 20-year-old suspect allegedly threw a molotov cocktail at Altman's home and has reportedly made similar threats toward OpenAI's SF HQ. The suspect was arrested; no injuries reported.
- A stark reminder that AI's cultural footprint now comes with real-world threat surfaces
- OpenAI's physical security posture will almost certainly be reviewed industry-wide after this
- The incident reflects growing public hostility toward AI leadership figures, not just the technology
**🔧 Dev Take:** "This is what happens when the discourse around AI stays abstract and the frustration becomes very concrete."

---

### OpenAI Has a Model "Too Dangerous to Release"
Reports indicate OpenAI has internally shelved a model deemed too risky to put in front of the public. No confirmed details on what it does or why — which is part of the story.
- Raises legitimate questions about what the evaluation criteria actually are
- Skeptics will ask whether "too dangerous" is safety or liability talking
- If true, it's one of the first high-profile cases of frontier labs actually pulling back
**🔧 Dev Take:** "A model too dangerous to ship is either a genuine safety win or the best marketing they've never run — hard to know which without transparency."

---

### ClawBench: Can Agents Handle Real Everyday Online Tasks?
A new benchmark tests whether AI agents can complete realistic, routine web tasks — think managing forms, navigating portals, handling multi-step online workflows. Results are humbling.
- Current agents handle clean, well-structured tasks reasonably well; messy real-world UIs wreck them
- Highlights the gap between demo-quality agents and production-ready automation
- A useful reality check for anyone building browser-based agent products
**🔧 Dev Take:** "Benchmark your agent against ClawBench before you pitch it to a client — you'll thank yourself later."

---

### Haystack & MLflow Both Trending: The OSS AI Stack Is Maturing
Deepset's Haystack (24.8k ⭐) and MLflow (25.3k ⭐) are both climbing GitHub trending — a signal that teams are standardizing on open-source tooling for production AI pipelines.
- Haystack focuses on context-engineered LLM pipelines and agent workflows with modular design
- MLflow covers the full lifecycle: debugging, evaluation, monitoring, and optimization
- Together they represent a viable open-source answer to the managed AI platform stack
**🔧 Dev Take:** "If you're paying for a managed AI ops platform and haven't audited what Haystack + MLflow can replace, do that audit."

---

## Quick Hits

- **Large-Scale OCR [r/MachineLearning]:** The discussion thread is surfacing solid practical approaches — vision models are making classical OCR pipelines look dated fast.
- **Apple iPhone Ultra (Foldable):** The foldable iPhone is reportedly being branded "Ultra" — expect a premium price point that makes the $100 ChatGPT tier look reasonable.
- **n8n adoption** is accelerating specifically among AI builders; the self-hosted option is worth a look if you're building agent workflows with data you can't send to the cloud.
- **MLflow 25k stars** — if your team isn't tracking experiments and model versions in prod, this is the week to fix that.
- **ClawBench is open** — worth running your agent stack against it before your competitors do.

---

*theba.sh — built for builders*
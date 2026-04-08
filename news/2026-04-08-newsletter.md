# theba.sh — 2026-04-08

The AI arms race is entering a new phase: models too dangerous to ship, open-source frameworks maturing fast, and the question of who actually controls the stack is getting louder. Meanwhile, the rest of tech is busy renaming itself to avoid accountability.

## Headlines

### Anthropic @ $30B ARR — and a Model They Won't Release
Anthropic is reportedly hitting $30B ARR while teasing Project GlassWing, a Claude-lineage model they've deemed too dangerous to release publicly — the first such decision since OpenAI sat on GPT-2 back in 2019. The timing, right as OpenAI navigates IPO turbulence, is not subtle.
- GlassWing reportedly exceeds internal safety thresholds Anthropic set for public deployment
- $30B ARR positions Anthropic as a credible rival heading into OpenAI's messy public market debut
- "Claude Mythos" previews suggest a bifurcated release strategy: constrained public models, more capable private/API tiers

**🔧 Dev Take:** "The most interesting model is the one you can't access — plan your architecture around that reality."

---

### Gemma 4: Google's Open Multimodal Story Gets Serious
Google dropped Gemma 4 and it's a meaningful leap — dramatically better than Gemma 3 across multimodal benchmarks, and the best small open model in its class by most measures. For teams running on-prem or building cost-sensitive pipelines, this changes the calculus.
- Multimodal performance closes the gap significantly on proprietary alternatives
- "Small" doesn't mean neutered anymore — Gemma 4 is genuinely capable at production tasks
- Reinforces Google's strategy of using open weights to stay relevant in the developer layer

**🔧 Dev Take:** "If you benchmarked Gemma 3 and moved on, run the evals again — this isn't incremental."

---

### Haystack & MLflow Both Trending: The Orchestration Layer is Consolidating
deepset's Haystack (24.7k stars) and MLflow (25.2k stars) are both surging on GitHub Trending, signaling that builders are moving past "which LLM" and into "how do I run this reliably in production." Two different philosophies — pipeline-first vs. experiment-and-deploy — both gaining ground simultaneously.
- Haystack emphasizes explicit pipeline control and context engineering for production LLM apps
- MLflow covers the full lifecycle: debugging, eval, monitoring, and optimization for agents and LLMs
- The fact that both are trending suggests teams are hedging and exploring rather than converging on one tool

**🔧 Dev Take:** "Pick the one that matches how your team thinks about the problem — Haystack if you design pipelines, MLflow if you instrument experiments."

---

### Google Research: Social Learning with LLMs
Google Research published work on collaborative learning frameworks where LLMs learn from peer interactions rather than purely from human feedback or static datasets. It's early, but the implications for agent architectures and multi-model systems are worth tracking.
- Agents improving via structured peer critique loops could reduce reliance on expensive human annotation
- Opens questions about emergent behavior and alignment drift in multi-agent training setups
- Directly relevant to anyone building agent workflows where models need to self-correct

**🔧 Dev Take:** "Interesting research direction, but don't deploy multi-agent self-improvement loops in prod until you understand the failure modes cold."

---

### Space Data Centers: Four Hard Problems
MIT Technology Review breaks down what it would actually take to operate data centers in orbit — and the answer is: a lot of unsolved engineering. Beyond the Musk-adjacent hype, there are four concrete blockers that make this a 2030s problem at best.
- Power generation, thermal dissipation, latency, and maintenance are all harder in orbit than on the ground
- The pitch is lower land/cooling costs and proximity to satellites — the reality is far higher operational complexity
- Worth understanding as context for where hyperscaler capex conversations are heading

**🔧 Dev Take:** "Cool concept, irrelevant to your infrastructure decisions for at least a decade — stay focused on optimizing what's available now."

---

### Social Media Is Rebranding. Again.
Meta and YouTube are reportedly pushing to shed the "social media" label amid mounting criticism and regulatory pressure. This is less a product strategy and more a narrative defense — but the framing shift will matter for how platforms get regulated.
- "Social media" carries legal and political baggage; new terminology could complicate liability arguments
- YouTube is leaning into "video platform," Meta toward "connection infrastructure" or similar abstraction
- Regulators and legislators tend to ignore rebrandings — but enterprise buyers and advertisers may not

**🔧 Dev Take:** "If your product roadmap depends on how Meta describes itself this quarter, that's the real problem."

---

## Quick Hits

- 🕊️ **U.S.-Iran two-week ceasefire agreed**, brokered by Pakistan — geopolitical risk window temporarily reduced, watch energy and supply chain implications
- 📉 **Reddit r/singularity declares "the era of human coding is over"** — the comments section remains, fittingly, written by humans
- 📱 **iPhone scores a D– on repairability** — up from previous years, still embarrassing; Samsung gets a D, so the bar is low
- 🔬 **Gemma 4 open weights are out** — pull them, run your evals, update your benchmarks before making model decisions this quarter
- 🧵 **MLflow hitting 25k+ stars** — if you're not using structured experiment tracking for LLM evals yet, now is a good time to start

---
*theba.sh — built for builders*
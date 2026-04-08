# theba.sh — 2026-04-08

The AI power rankings are getting reshuffled in real time: Anthropic is playing offense, OpenAI's internal vibes are fraying, and Google is quietly shipping. Pick your horse.

---

## Headlines

### OpenAI's Cracks Are Starting to Show
$852B valuation, $122B raised — and yet something feels structurally off inside OpenAI right now. The Verge is reporting on mounting internal tension as the company navigates a looming IPO and an increasingly competitive landscape.
- Funding numbers are historically absurd, but burn rate and organizational chaos are real concerns
- Anthropic is explicitly timing its moves around OpenAI's IPO vulnerability
- "Vibes" is a soft word for what sounds like a harder problem

**🔧 Dev Take:** "A $852B valuation is a promise, not a product — watch what ships, not what's raised."

---

### Anthropic Hits $30B ARR and Drops a Model Too Dangerous to Release
Anthropic crossed $30B ARR and previewed Claude Mythos — reportedly the first model deemed too dangerous to release since OpenAI sat on GPT-2. Project GlassWing is also in the mix, details still thin.
- $30B ARR puts Anthropic in a credible position to pressure OpenAI's IPO narrative
- Claude Mythos being withheld is either genuinely alarming or the best marketing move of 2026
- GlassWing remains opaque — watch this space closely

**🔧 Dev Take:** "Withholding a model is a statement — either they've built something serious or they've learned that restraint is its own PR strategy."

---

### Gemma 4: Google's Small Model Story Just Got a Lot Better
Google dropped Gemma 4, calling it dramatically better than Gemma 3 across the board, with strong multimodal performance at small model sizes. A quiet but meaningful win for on-device and cost-sensitive deployments.
- Multimodal capability at small scale is the real unlock for edge and embedded use cases
- "Dramatically better" is a high bar — benchmarks will tell the real story fast
- Open weights continue to be Google's most credible developer trust play

**🔧 Dev Take:** "If the benchmarks hold, Gemma 4 just became the default starting point for any constrained-environment multimodal build."

---

### Meta Drops Muse Spark, a New Reasoning Model
Meta quietly released Muse Spark, a new reasoning-focused model, surfacing first on r/LocalLLaMA. Early community impressions are being stress-tested in real time.
- The LocalLLaMA community is already running evals — trust those over the press release
- Reasoning model competition is now a four-way race: OpenAI, Anthropic, Google, Meta
- Meta's open release cadence remains its biggest differentiator

**🔧 Dev Take:** "Meta keeps shipping into the open — whatever Muse Spark's ceiling is, you'll know its floor by end of week."

---

### Google Research: Can LLMs Learn Socially?
Google Research published work on "social learning" — using collaborative frameworks to let LLMs share and build on learned knowledge across agents. This is foundational infrastructure thinking, not a product announcement.
- Multi-agent knowledge propagation is an unsolved problem with significant production implications
- If agents can learn from each other's context without full retraining, evaluation pipelines need to adapt
- Still research-stage, but the direction points directly at where agentic systems are heading

**🔧 Dev Take:** "The moment agents can teach each other reliably is the moment your eval suite becomes your most important engineering investment."

---

## Quick Hits

- **Haystack (24.7k ⭐)** is worth a look if you're building context-engineered pipelines and tired of rolling your own orchestration layer
- **MLflow (25.2k ⭐)** added agent and LLM support — if you're already using it for ML, the upgrade path is low-friction
- **prompts.chat (158k ⭐)** keeps climbing — useful for teams that want a self-hostable, private prompt library without the SaaS overhead
- **OpenBB (65.6k ⭐)** is the sleeper pick for anyone building financial AI agents that need clean, structured data access
- **PyTorch Lightning (31k ⭐)** remains the pragmatic choice for fine-tuning at scale without rewriting your training loop

---

*theba.sh — built for builders*